"""Save public service-page snapshots for review; never writes them into the trusted catalog."""

from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "source_snapshots.json"
USER_AGENT = "SabaPublicServiceResearch/0.1 (public pages only)"
DEFAULT_SEEDS = (
    "https://www.eservices.gov.et/en/services",
    "https://www.eservices.gov.et/en/providers",
    "https://services.eaes.et/",
    "https://www.ebc.et/",
)
ALLOWED_HOSTS = {"www.eservices.gov.et", "services.eaes.et", "www.ebc.et"}
SKIP_PATH = re.compile(r"/(login|logout|register|account|workspace|profile|payment)(/|$)", re.I)
API_HINT = re.compile(
    r"[\"'`]([^\"'`]{0,180}(?:/api/|api/v\d+|graphql|/services/)[^\"'`]{0,180})[\"'`]",
    re.I,
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: list[str] = []
        self.text: list[str] = []
        self.links: list[str] = []
        self.scripts: list[str] = []
        self._in_title = False
        self._ignored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored += 1
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "noscript", "svg"} and self._ignored:
            self._ignored -= 1

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._in_title:
            self.title.append(cleaned)
        elif not self._ignored:
            self.text.append(cleaned)


def canonical_url(url: str) -> str | None:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or host not in ALLOWED_HOSTS:
        return None
    if SKIP_PATH.search(parts.path):
        return None
    path = parts.path or "/"
    return urlunsplit(("https", host, path, parts.query, ""))


def robots_for(url: str) -> RobotFileParser:
    parts = urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = RobotFileParser(robots_url)
    request = Request(robots_url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=10) as response:
            parser.parse(response.read(256_000).decode("utf-8", errors="replace").splitlines())
    except HTTPError as exc:
        if exc.code != 404:
            raise
        # A missing robots.txt file means there are no published crawl rules.
        parser.parse([])
    return parser


def fetch(url: str) -> tuple[str, str]:
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml", "Accept-Encoding": "identity"},
    )
    with urlopen(request, timeout=15) as response:
        content_type = response.headers.get_content_type()
        if content_type not in {"text/html", "application/xhtml+xml", "application/javascript", "text/javascript"}:
            raise ValueError(f"Skipping non-page content ({content_type}).")
        body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise ValueError("Page is larger than the 2 MB safety limit.")
        charset = response.headers.get_content_charset() or "utf-8"
    return body.decode(charset, errors="replace"), content_type


def crawl(seeds: list[str], max_pages_per_site: int) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    robots: dict[str, RobotFileParser] = {}
    for seed in seeds:
        start = canonical_url(seed)
        if not start:
            print(f"Skipping URL outside the public-site allowlist: {seed}")
            continue
        host = urlsplit(start).hostname or ""
        if host not in robots:
            try:
                robots[host] = robots_for(start)
            except (HTTPError, URLError, TimeoutError) as exc:
                print(f"Skipping {host}; robots.txt could not be checked ({type(exc).__name__}).")
                continue

        queue = deque([start])
        visited: set[str] = set()
        fetched_scripts: set[str] = set()
        while queue and len(visited) < max_pages_per_site:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)
            if not robots[host].can_fetch(USER_AGENT, url):
                print(f"Robots policy disallows: {url}")
                continue
            try:
                source, content_type = fetch(url)
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                print(f"Could not read {url} ({type(exc).__name__}).")
                continue

            if "html" not in content_type:
                candidates = sorted(set(API_HINT.findall(source)))
                if candidates:
                    snapshots.append({"url": url, "api_hints": candidates[:30]})
                continue

            parser = PageParser()
            parser.feed(source)
            api_hints: set[str] = set()
            script_assets: list[str] = []
            for src in parser.scripts[:8]:
                script_url = canonical_url(urljoin(url, src))
                if not script_url or urlsplit(script_url).hostname != host:
                    continue
                script_assets.append(script_url)
                if script_url in fetched_scripts or len(fetched_scripts) >= 12:
                    continue
                fetched_scripts.add(script_url)
                if not robots[host].can_fetch(USER_AGENT, script_url):
                    continue
                try:
                    script_text, script_type = fetch(script_url)
                except (HTTPError, URLError, TimeoutError, ValueError):
                    continue
                if "javascript" in script_type:
                    api_hints.update(API_HINT.findall(script_text))
            links: list[str] = []
            for href in parser.links:
                normalized = canonical_url(urljoin(url, href))
                if normalized and urlsplit(normalized).hostname == host and normalized not in visited:
                    links.append(normalized)
            for link in links:
                if len(queue) + len(visited) >= max_pages_per_site:
                    break
                queue.append(link)

            snapshots.append(
                {
                    "url": url,
                    "title": " ".join(parser.title)[:300],
                    "text": " ".join(parser.text)[:20_000],
                    "script_assets": script_assets,
                    "api_hints": sorted(api_hints)[:50],
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "needs_human_review": True,
                }
            )
    return snapshots


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-pages-per-site", type=int, default=12)
    args = parser.parse_args()
    results = crawl(list(DEFAULT_SEEDS), max(1, min(args.max_pages_per_site, 30)))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(results)} public-page snapshots to {OUTPUT}")
    print("Review every source and date before adding any fact to data/services.json.")


if __name__ == "__main__":
    main()
