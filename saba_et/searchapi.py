"""Optional SearchAPI.io Google Search client for official-source research."""

from __future__ import annotations

import os
from typing import Any

import httpx


class SearchAPIError(RuntimeError):
    """Sanitized SearchAPI failure; never contains request data or credentials."""

    def __init__(self, reason: str, status: int | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.status = status


class SearchAPIClient:
    endpoint = "https://www.searchapi.io/api/v1/search"

    def __init__(self, api_key: str, engine: str = "google") -> None:
        self._api_key = api_key.strip()
        self._engine = engine.strip().lower() or "google"

    @classmethod
    def from_env(cls) -> SearchAPIClient | None:
        enabled = os.environ.get("SEARCHAPI_ENABLED", "false").strip().lower() in {
            "1", "true", "yes", "on"
        }
        api_key = os.environ.get("SEARCHAPI_API_KEY", "").strip()
        if not enabled:
            return None
        if not api_key:
            raise ValueError("SEARCHAPI_ENABLED is true but SEARCHAPI_API_KEY is missing.")
        engine = os.environ.get("SEARCHAPI_ENGINE", "google").strip()
        if engine.lower() != "google":
            raise ValueError("SEARCHAPI_ENGINE must be google for Saba's official-source search.")
        return cls(api_key, engine)

    async def search(self, question: str) -> list[dict[str, str]]:
        query = f"{question[:500]} (site:gov.et OR site:eaes.et OR site:ebc.et)"
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(connect=4, read=10, write=5, pool=2)
            ) as client:
                response = await client.get(
                    self.endpoint,
                    params={"engine": self._engine, "q": query, "gl": "et", "hl": "en"},
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                response.raise_for_status()
                payload: Any = response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status in (401, 403):
                reason = "credentials"
            elif status in (402, 429):
                reason = "quota"
            elif status in (408, 504):
                reason = "timeout"
            else:
                reason = "unavailable"
            raise SearchAPIError(reason, status) from None
        except httpx.TimeoutException:
            raise SearchAPIError("timeout") from None
        except httpx.HTTPError:
            raise SearchAPIError("network") from None
        except ValueError:
            raise SearchAPIError("invalid_response") from None

        if not isinstance(payload, dict):
            raise SearchAPIError("invalid_response")
        if payload.get("error"):
            raise SearchAPIError("unavailable")

        results: list[dict[str, str]] = []
        organic = payload.get("organic_results", [])
        if not isinstance(organic, list):
            return results
        for item in organic:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()[:200]
            url = str(item.get("link", "")).strip()[:1000]
            snippet = str(item.get("snippet", "")).strip()[:800]
            if title and url and snippet:
                results.append({"title": title, "url": url, "snippet": snippet})
            if len(results) >= 8:
                break
        return results
