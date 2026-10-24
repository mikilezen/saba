"""Load simple KEY=value settings from a local .env file without overriding the shell."""

import os
from pathlib import Path
import re


_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        if value.startswith("export "):
            value = value[7:].lstrip()
        name, separator, raw = value.partition("=")
        name = name.strip()
        if not separator or not _ENV_NAME.fullmatch(name) or name in os.environ:
            continue
        raw = raw.strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
            raw = raw[1:-1]
        else:
            raw = re.split(r"\s+#", raw, maxsplit=1)[0].rstrip()
        os.environ[name] = raw
