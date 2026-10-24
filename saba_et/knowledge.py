"""Read verified service information from the local JSON catalog."""

import json
from datetime import date
from pathlib import Path

from saba_et.domain import Service, Source


class ServiceCatalog:
    def __init__(self, path: Path) -> None:
        self._path = path

    def all(self) -> list[Service]:
        if not self._path.exists():
            return []
        rows = json.loads(self._path.read_text(encoding="utf-8"))
        services: list[Service] = []
        for row in rows:
            source = row["source"]
            services.append(
                Service(
                    service_id=row["id"],
                    name_am=row["name_am"],
                    summary_am=row["summary_am"],
                    documents_am=tuple(row.get("documents_am", [])),
                    fee_etb=row.get("fee_etb"),
                    source=Source(
                        title=source["title"],
                        url=source["url"],
                        last_checked=date.fromisoformat(source["last_checked"]),
                    ),
                )
            )
        return services

    def find(self, query: str) -> list[Service]:
        needle = query.casefold().strip()
        if not needle:
            return []
        return [
            service
            for service in self.all()
            if needle in service.name_am.casefold()
            or needle in service.summary_am.casefold()
            or needle in service.service_id.casefold()
        ]
