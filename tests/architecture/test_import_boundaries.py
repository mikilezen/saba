"""Regression coverage for the executable Python import boundaries."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_import_boundaries import Violation, find_violations


@pytest.mark.parametrize("module", [
    "saba.agent.loop", "saba.session.state", "saba.runtime_admission",
    "saba.data_access", "saba.installation_lock",
])
def test_runtime_owners_do_not_depend_on_update_policy(module: str) -> None:
    assert find_violations("from saba.update_service import UpdateService", module) == [
        Violation("update-policy-direction", "saba.update_service.UpdateService", 1),
    ]


def test_updater_uses_process_contracts_not_agent_or_client_implementations() -> None:
    assert find_violations("from saba.agent.loop import AgentLoop", "saba.update_stop") == [
        Violation("update-domain", "saba.agent.loop.AgentLoop", 1),
    ]
    assert find_violations(
        "from saba.gateway.runtime import GatewayRuntime", "saba.update_stop",
    ) == []
    assert find_violations(
        "from saba.update_stop import watch_gateway_stop", "saba.cli.gateway_runtime",
    ) == []
    assert find_violations(
        "from saba.cli.gateway_runtime import _run_gateway", "saba.update_restart",
    ) == []
    assert find_violations(
        "from saba.agent.loop import AgentLoop", "saba.update_restart",
    ) == [Violation("update-restart-adapter", "saba.agent.loop.AgentLoop", 1)]


@pytest.mark.parametrize(
    ("source", "target", "line"),
    [
        ("import saba.webui.metadata", "saba.webui.metadata", 1),
        ("from saba import webui", "saba.webui", 1),
        ("from saba.webui import metadata", "saba.webui.metadata", 1),
        ("from .. import webui", "saba.webui", 1),
        ("from ..webui import metadata", "saba.webui.metadata", 1),
        (
            "def load():\n    from saba.cli import gateway",
            "saba.cli.gateway", 2,
        ),
        (
            "import importlib\nimportlib.import_module('saba.webui.metadata')",
            "saba.webui.metadata", 2,
        ),
        (
            "import importlib as modules\n"
            "modules.import_module(name='saba.webui.metadata')",
            "saba.webui.metadata", 2,
        ),
        (
            "from importlib import import_module as load\n"
            "load('..webui.metadata', __package__)",
            "saba.webui.metadata", 2,
        ),
        (
            "from importlib import import_module\n"
            "import_module('..webui.metadata', package='saba.agent')",
            "saba.webui.metadata", 2,
        ),
        ("__import__('saba.webui.metadata')", "saba.webui.metadata", 1),
        (
            "import builtins as imports\nimports.__import__('saba.webui.metadata')",
            "saba.webui.metadata", 2,
        ),
    ],
)
def test_core_rejects_adapter_imports_in_supported_spellings(
    source: str, target: str, line: int,
) -> None:
    assert find_violations(source, "saba.agent.loop") == [
        Violation("core-execution", target, line),
    ]


@pytest.mark.parametrize(
    "source",
    [
        "from typing import TYPE_CHECKING as TC\n"
        "if TC:\n    from saba.webui import metadata",
        "import typing as t\n"
        "if t.TYPE_CHECKING:\n    from saba.webui import metadata",
    ],
)
def test_core_boundary_includes_type_dependencies(source: str) -> None:
    assert find_violations(source, "saba.agent.runner") == [
        Violation("core-execution", "saba.webui.metadata", 3),
    ]


@pytest.mark.parametrize(
    ("module", "rule"),
    [
        ("saba.session.manager", "session-storage"),
        ("saba.session.recovery", "session-storage"),
        ("saba.security.workspace_policy", "security-primitives"),
        ("saba.agent.turn_delivery", "core-execution"),
        ("saba.channels.notification_routes", "channel-routing-contracts"),
        ("saba.config.schema", "configuration-contracts"),
        ("saba.agent.tools.cli_apps_config", "tool-configuration-contracts"),
        ("saba.utils.file_io", "shared-primitives"),
    ],
)
def test_storage_and_security_do_not_depend_on_adapters(module: str, rule: str) -> None:
    assert find_violations("from saba.cli import gateway", module) == [
        Violation(rule, "saba.cli.gateway", 1),
    ]


def test_websocket_only_permits_progress_event_as_a_type_dependency() -> None:
    source = (
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from saba.bus.outbound_events import ProgressEvent\n"
        "    from saba.command import router\n"
        "else:\n"
        "    from saba.bus.outbound_events import ProgressEvent\n"
    )
    assert find_violations(source, "saba.channels.websocket.runtime") == [
        Violation("websocket-transport", "saba.command.router", 4),
        Violation("websocket-transport", "saba.bus.outbound_events.ProgressEvent", 6),
    ]


@pytest.mark.parametrize(
    "source",
    [
        "from saba.config.schema import Base",
        "from ...config.schema import Base as ConfigBase",
    ],
)
def test_tool_configs_import_the_shared_base_directly(source: str) -> None:
    assert find_violations(source, "saba.agent.tools.shell") == [
        Violation("tool-config-base", "saba.config.schema.Base", 1),
    ]
    assert find_violations(
        "from saba.config_base import Base", "saba.agent.tools.shell",
    ) == []


def test_configuration_imports_the_six_tool_owned_config_contracts() -> None:
    source = (
        "from saba.agent.tools.cli_apps_config import CliAppsToolConfig\n"
        "from saba.agent.tools.filesystem_config import FileToolsConfig\n"
        "from saba.agent.tools.image_generation_config import ImageGenerationToolConfig\n"
        "from saba.agent.tools.self_config import MyToolConfig\n"
        "from saba.agent.tools.shell_config import ExecToolConfig\n"
        "from saba.agent.tools.web_config import WebToolsConfig\n"
    )
    assert find_violations(source, "saba.config.schema") == []


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("saba.agent.loop", "from saba.session.recovery import RecoveryAdmission"),
        ("saba.session.manager", "from saba.providers.base import ProviderConversationState"),
        ("saba.session.webui_turns", "from saba.webui import transcript"),
        ("saba.cli.gateway_runtime", "from saba.agent.loop import AgentLoop"),
        ("saba.channels.websocket.runtime", "from saba.webui import inbound_commands"),
        ("saba.agent.tools.cli_apps_config", "from saba.config_base import Base"),
        (
            "saba.agent.turn_delivery",
            "from saba.channels.notification_routes import notification_metadata",
        ),
    ],
)
def test_existing_runtime_and_composition_dependencies_remain_allowed(
    module: str, source: str,
) -> None:
    assert find_violations(source, module) == []


@pytest.mark.parametrize(
    ("relative", "source", "rule", "target", "line"),
    [
        (
            "saba/agent/runner.py", "import saba.webui.metadata",
            "core-execution", "saba.webui.metadata", 1,
        ),
        (
            "saba/agent/loop.py",
            "import importlib\nif importlib.import_module('saba.webui.metadata'):\n    pass",
            "core-execution", "saba.webui.metadata", 2,
        ),
        (
            "saba/agent/loop.py", "if __import__('saba.webui.metadata'):\n    pass",
            "core-execution", "saba.webui.metadata", 1,
        ),
        (
            "saba/session/manager.py", "from saba.cli import gateway",
            "session-storage", "saba.cli.gateway", 1,
        ),
        (
            "saba/channels/notification_routes.py",
            "from saba.channels.slack.runtime import SlackChannel",
            "channel-routing-contracts", "saba.channels.slack.runtime.SlackChannel", 1,
        ),
        (
            "saba/channels/notification_routes.py",
            "from saba.agent.turn_delivery import TurnRoute",
            "channel-routing-contracts", "saba.agent.turn_delivery.TurnRoute", 1,
        ),
        (
            "saba/security/__init__.py", "from ..cli import gateway",
            "security-primitives", "saba.cli.gateway", 1,
        ),
        (
            "saba/channels/websocket/runtime.py",
            "import importlib as modules\nmodules.import_module('saba.command.router')",
            "websocket-transport", "saba.command.router", 2,
        ),
        (
            "saba/agent/tools/shell.py", "from ...config.schema import Base as ConfigBase",
            "tool-config-base", "saba.config.schema.Base", 1,
        ),
        (
            "saba/channels/telegram/runtime.py", "from saba.config.schema import Base",
            "tool-config-base", "saba.config.schema.Base", 1,
        ),
        (
            "saba/config/schema.py", "from saba.agent.tools.shell import ExecTool",
            "configuration-contracts", "saba.agent.tools.shell.ExecTool", 1,
        ),
        (
            "saba/agent/tools/cli_apps_config.py", "from .cli_apps import CliAppsTool",
            "tool-configuration-contracts", "saba.agent.tools.cli_apps.CliAppsTool", 1,
        ),
        (
            "saba/agent/tools/web_config.py", "from saba.config.schema import Config",
            "tool-configuration-contracts", "saba.config.schema.Config", 1,
        ),
        (
            "saba/providers/oauth_catalog_cache.py",
            "from saba.providers import openai_codex_provider",
            "oauth-catalog-cache", "saba.providers.openai_codex_provider", 1,
        ),
    ],
)
def test_cli_rejects_a_violation_and_reports_its_source_location(
    tmp_path: Path, relative: str, source: str, rule: str, target: str, line: int,
) -> None:
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text(source + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_import_boundaries", "--root", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert result.stderr.strip() == f"{relative}:{line}: [{rule}] must not import {target}"


def test_cli_accepts_a_tool_owned_config_import(tmp_path: Path) -> None:
    path = tmp_path / "saba/config/schema.py"
    path.parent.mkdir(parents=True)
    path.write_text(
        "from saba.agent.tools.cli_apps_config import CliAppsToolConfig\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_import_boundaries", "--root", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
