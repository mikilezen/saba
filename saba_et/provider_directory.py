"""Curated public-service provider links and integration-readiness notes."""

import json
from pathlib import Path
from typing import Any


class ProviderDirectory:
    def __init__(self, path: Path) -> None:
        self._path = path

    def all(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        rows = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError("Provider directory must be a JSON array.")
        return [row for row in rows if isinstance(row, dict)]

    def find(self, query: str = "") -> list[dict[str, Any]]:
        providers = self.all()
        needle = query.casefold().strip()
        if not needle:
            return providers
        terms = [term for term in needle.split() if term]
        matches: list[tuple[int, dict[str, Any]]] = []
        for provider in providers:
            haystack = " ".join(
                [
                    str(provider.get("id", "")),
                    str(provider.get("name", "")),
                    str(provider.get("category", "")),
                    " ".join(str(term) for term in provider.get("search_terms", [])),
                ]
            ).casefold()
            score = sum(1 for term in terms if term in haystack)
            if score:
                matches.append((score, provider))
        matches.sort(key=lambda item: item[0], reverse=True)
        return [provider for _, provider in matches]

    def render(self, query: str, language: str) -> str:
        labels = {
            "am": ("የአገልግሎት አቅራቢዎች", "የፖርታል አገናኝ፤ ከስር ያለው የAPI ሁኔታ አልተረጋገጠም።", "ኦፊሴላዊ ፖርታል", "አገናኙ ከመጠቀምዎ በፊት ያረጋግጡ", "ኦፊሴላዊ አገናኝ ገና አልተረጋገጠም"),
            "om": ("Tajaajiloota mootummaa", "Kunuunsa fuulaa qofa; API mirkanaa'aa hin jiru.", "Poortaala mootummaa", "Liinkii mirkaneeffadhu", "Liinkiin mootummaa hin mirkanoofne"),
            "ti": ("ኣቕረብቲ ኣገልግሎት", "መራኸቢ ፖርታል ጥራይ፤ API ኣይተረጋገጸን።", "ወግዓዊ ፖርታል", "እቲ መራኸቢ ኣረጋግጹ", "ወግዓዊ መራኸቢ ኣይተረጋገጸን"),
            "en": ("Public-service providers", "Directory links only; no automated API integration is confirmed.", "Official portal", "Candidate link; verify before use", "Official link not verified yet"),
        }.get(language, ("Public-service providers", "Directory links only; no automated API integration is confirmed.", "Official portal", "Candidate link; verify before use", "Official link not verified yet"))
        title, note, official, candidate, missing = labels
        providers = self.find(query)
        if not providers:
            return f"{title}: no matches. Try /providers visa, tax, fayda, power, or education."

        lines = [title, note]
        for provider in providers[:24]:
            lines.append(f"• {provider['name']} — {provider['category']}")
            url = provider.get("url")
            status = provider.get("portal_status")
            if url:
                link_label = official if status == "verified" else candidate
                lines.append(f"  {link_label}: {url}")
            else:
                lines.append(f"  {missing}")
        return "\n".join(lines)
