from __future__ import annotations

import sys
from pathlib import Path

import pytest

from saba.apps.cli.service import CliAppManager


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        (
            "install",
            ["winget", "install", "--exact", "--id", "AgileBits.1Password.CLI"],
        ),
        (
            "update",
            ["winget", "upgrade", "--exact", "--id", "AgileBits.1Password.CLI"],
        ),
        (
            "uninstall",
            ["winget", "uninstall", "--exact", "--id", "AgileBits.1Password.CLI"],
        ),
    ],
)
def test_1password_cli_uses_winget_on_windows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    action: str,
    expected: list[str],
) -> None:
    manager = CliAppManager(workspace=tmp_path)
    app = {
        "name": "1password-cli",
        "package_manager": "brew",
        "install_cmd": "brew install --cask 1password-cli",
        "update_cmd": "brew upgrade --cask 1password-cli",
        "uninstall_cmd": "brew uninstall --cask 1password-cli",
    }

    monkeypatch.setattr(sys, "platform", "win32")

    assert manager._argv_for_action(app, action) == expected


def test_other_brew_apps_keep_catalog_commands_on_windows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = CliAppManager(workspace=tmp_path)
    app = {
        "name": "example",
        "package_manager": "brew",
        "install_cmd": "brew install example",
    }

    monkeypatch.setattr(sys, "platform", "win32")

    assert manager._argv_for_action(app, "install") == ["brew", "install", "example"]
