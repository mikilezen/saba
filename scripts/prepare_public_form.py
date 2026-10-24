"""Prepare a public application form for human review; this script never submits it."""

from __future__ import annotations

import asyncio
import re
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser


ALLOWED_HOSTS = {
    "www.eservices.gov.et",
    "services.eaes.et",
    "www.ebc.et",
    "evisa.gov.et",
    "www.evisa.gov.et",
}
SENSITIVE_FIELD = re.compile(r"(^|[^a-z])(fayda|national.?id|identity|passport|travel.?document|password|passcode|pin|card|payment)([^a-z]|$)", re.I)
BLOCKED_PATH = re.compile(r"/(login|account|workspace|payment|checkout)(/|$)", re.I)


def validate_url(url: str) -> None:
    parts = urlsplit(url)
    if parts.scheme != "https" or (parts.hostname or "").lower() not in ALLOWED_HOSTS:
        raise ValueError("Only configured official public-service sites over HTTPS are allowed.")
    if BLOCKED_PATH.search(parts.path):
        raise ValueError("Login, account, and payment pages are not supported.")


def check_robots(url: str) -> None:
    parts = urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = RobotFileParser(robots_url)
    try:
        with urlopen(Request(robots_url, headers={"User-Agent": "SabaFormPrep/0.1"}), timeout=8) as response:
            parser.parse(response.read(256_000).decode("utf-8", errors="replace").splitlines())
    except HTTPError as exc:
        if exc.code == 404:
            parser.parse([])
        else:
            raise PermissionError("Could not confirm the site's robots policy; form preparation stopped.") from None
    except (URLError, TimeoutError):
        raise PermissionError("Could not confirm the site's robots policy; form preparation stopped.") from None
    if not parser.can_fetch("SabaFormPrep/0.1", url):
        raise PermissionError("The site's robots policy disallows this page.")


async def prepare(url: str) -> None:
    validate_url(url)
    check_robots(url)
    print("This opens a temporary browser session. It does not save field values or submit the form.")
    if input("Continue? Type yes: ").strip().casefold() != "yes":
        print("Stopped without opening the page.")
        return

    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise SystemExit("Install optional browser support: python -m pip install -r requirements-browser.txt; python -m playwright install chromium") from exc

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=20_000)
            if response and response.status >= 400:
                raise RuntimeError(f"The site returned HTTP {response.status}.")
            if BLOCKED_PATH.search(urlsplit(page.url).path):
                raise RuntimeError("The page redirected to a login or account flow; it was not filled.")

            fields = page.locator(
                "input:not([type=hidden]):not([type=submit]):not([type=button]), textarea"
            )
            count = await fields.count()
            print(f"Opened: {await page.title()} — {page.url}")
            print("Enter values only for fields you understand. Skip Fayda/ID, password, card, and payment fields.")
            for index in range(count):
                field = fields.nth(index)
                descriptor = await field.evaluate(
                    """el => {
                        const labels = el.labels ? Array.from(el.labels).map(x => x.innerText.trim()).filter(Boolean) : [];
                        return {
                            type: (el.getAttribute('type') || el.tagName).toLowerCase(),
                            label: labels[0] || el.getAttribute('aria-label') || el.getAttribute('placeholder') || el.name || el.id || 'form field',
                            name: el.name || ''
                        };
                    }"""
                )
                label = str(descriptor.get("label", f"field {index + 1}"))
                field_name = str(descriptor.get("name", ""))
                field_type = str(descriptor.get("type", ""))
                if field_type in {"password", "file", "checkbox", "radio", "submit", "button"} or SENSITIVE_FIELD.search(label) or SENSITIVE_FIELD.search(field_name):
                    print(f"Skipped protected or non-text field: {label}")
                    continue
                value = input(f"{label} (Enter to skip): ")
                if value:
                    await field.fill(value)
                    print("Filled in this temporary browser only.")

            print("\nReview the open browser page. Saba will not click Submit. You decide whether to submit it yourself.")
            await asyncio.to_thread(input, "Press Enter here to close the temporary browser: ")
        finally:
            await browser.close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="A public form URL on an allowlisted government/service site")
    args = parser.parse_args()
    try:
        asyncio.run(prepare(args.url))
    except Exception as exc:
        raise SystemExit(f"Form preparation stopped ({type(exc).__name__}). No form was submitted.") from None


if __name__ == "__main__":
    main()
