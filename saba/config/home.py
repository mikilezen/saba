"""Default instance paths selected by the global --home option."""

from pathlib import Path

_home_path: Path | None = None


def set_home_path(path: Path | None) -> None:
    """Select the instance root for the current CLI invocation."""
    global _home_path
    _home_path = path.expanduser().resolve() if path is not None else None


def get_selected_home_path() -> Path | None:
    """Return the explicit instance root, if one was selected."""
    return _home_path


def get_default_home_path(home: Path | None = None) -> Path:
    """Return Saba's default instance root, preserving an existing saba home."""
    home = home if home is not None else Path.home()
    saba_home = home / ".saba"
    legacy_home = home / ".saba"
    if not saba_home.exists() and legacy_home.exists():
        return legacy_home
    return saba_home


def get_home_path() -> Path:
    """Return the selected instance root, or Saba's default instance root."""
    return _home_path if _home_path is not None else get_default_home_path()


def get_default_workspace() -> str:
    """Keep the portable default unless an instance home was selected."""
    if _home_path is not None:
        return str(get_home_path() / "workspace")
    return f"~/{get_default_home_path().name}/workspace"
