# CLI Reference

Use this page when you know what you want to run and need the command shape. For a guided first run, start with [`quick-start.md`](./quick-start.md).

## Choose a Command

| Goal | Command | Notes |
|---|---|---|
| Check the install | `saba --version` | If this fails, try `python -m saba --version` |
| Update an ordinary Python venv | `saba update` | Latest stable PyPI release; use the [installation-specific route](./updating.md#installation-owners) for other methods |
| Create or refresh config | `saba onboard` | Creates `~/.saba/config.json` and `~/.saba/workspace/` |
| Refresh config non-interactively | `saba onboard --refresh` | Preserves existing values and adds missing default fields without prompting |
| Use guided setup | `saba onboard --wizard` | Best when you prefer prompts over hand-editing JSON |
| Open the browser workbench | `saba webui` | Prepares local WebUI settings, starts the gateway, and opens the browser |
| Check readiness without calling a model | `saba status` | Summarizes config/workspace and validates the active provider/model configuration |
| Send one test message | `saba -m "Hello!"` | First proof that install, config, provider, model, and workspace all work |
| Chat in the terminal | `saba` | Interactive local chat; `saba agent` remains an explicit alias |
| Run the gateway directly | `saba gateway` | Service/ops command for WebUI, chat apps, cron, and heartbeat |
| Deliver a local trigger | `saba trigger <id> "message"` | Created first with `/trigger <name>` in the target chat/session |
| Serve an OpenAI-compatible API | `saba serve` | Starts `/v1/chat/completions`, `/v1/models`, and `/health` |
| Check chat channel setup | `saba channels status` | Useful before starting `saba gateway` |
| Manage optional features | `saba plugins list` | Shows channels and optional capabilities you can turn on |
| Log in to QR/OAuth-style channels | `saba channels login <channel>` | Used by channels such as WhatsApp and WeChat |
| Log in to OAuth model providers | `saba provider login <provider>` | Used by OpenAI Codex, xAI subscription, and GitHub Copilot providers |

## Global

```bash
saba --help
saba --version
saba --home ~/.saba-work onboard
python -m saba --help
python -m saba --version
```

`python -m saba ...` is useful when the package is installed but the `saba` script is not on `PATH`.

`--home <directory>` is a global option; place it before the subcommand. It selects `<directory>/config.json` and the default `<directory>/workspace/`. Explicit `--config` and workspace settings still apply. See [Multiple Instances](./multiple-instances.md) for runtime data locations and port selection. `-h` and `--help` display help.

### Coexisting with Saba Desktop

The Python package and Saba Desktop keep separate runtimes, configuration, workspaces, and state. When a running Desktop release publishes its private terminal-access descriptor, an interactive bare `saba` or `saba webui` asks which installation to use after authenticating a ready Desktop target. Use `Up`/`Down` to highlight an installation and `Enter` to confirm. `Ctrl+C` cancels with exit code 130 without attaching to Desktop or starting a Python backend. If Desktop is absent, busy, unavailable, or cannot be authenticated, the command reports the current Python executable and continues normally. A virtual environment's executable is shown without resolving it to its base interpreter.

Choosing Desktop for `saba webui` opens its already-running browser workbench and exits; closing the browser never stops the Desktop gateway. Choosing Desktop for bare `saba` opens the terminal UI against that same running backend when the Desktop host, gateway and terminal client support terminal protocol 1. Older versions fail explicitly with update guidance. Use explicit `saba agent` for the original Python terminal UI. After Desktop is selected, a disconnect or incompatible reply ends that invocation with an error; it never silently switches to Python or launches a replacement. On macOS, browser URLs are delivered through native Launch Services rather than command-line arguments. A failed native handoff does not fall back to `open` or a `BROWSER` command, keeping bootstrap credentials out of launcher arguments.

On Windows, the shared browser launcher uses a private HTML redirect rather than passing a credential-bearing URL to a browser command. A short-lived, windowless Python helper receives the URL over an anonymous pipe, opens the redirect through the system's HTTP association, and attempts file cleanup after two minutes. The calling CLI can exit immediately after the launch acknowledgement; this helper does not start, stop, or keep a gateway alive. It does not honor `BROWSER` overrides. Redirects are stored in the current user's Windows Local AppData known folder, under `SabaBrowserHandoff-v1`, with an explicit current-user-only protected ACL. An ACL-enforcing local filesystem and a non-reparse storage path are required; unsafe existing storage or failed browser handoff fails without raw-URL fallback. Abnormal termination can leave a private redirect behind. Later invocations retry cleanup of verified redirect files older than ten minutes, excluding active files; cleanup is not a guarantee of physical erasure or secrecy from same-user programs or administrators. No Python/Desktop settings, credentials, or history are imported between installations.

Any explicit subcommand or option—including `saba agent`, `saba webui --no-open`, config/workspace selectors, help, version, completion, and gateway lifecycle commands—keeps its existing Python meaning and never opens the Desktop picker. Target choices are not remembered, and Desktop settings are not copied into the Python installation.

Desktop terminal credentials are short-lived WebSocket/API tokens obtained through the authenticated current-user rendezvous. The TUI receives them through a bounded anonymous pipe, not command arguments, environment variables or temporary files. Its environment contains only a trusted resolver command and public instance IDs. The resolver verifies the selected Desktop and gateway again for every credential refresh. The gateway identity is also checked before any WebSocket mutation. This mode does not acquire a gateway lifecycle lease: client exit leaves Desktop running, and disconnect never automatically reconnects or replays an uncertain task.

Desktop-only distributions use the narrow `saba-desktop-tui` entrypoint inside their existing private runtime; it is not a replacement for the full Python CLI. They must ship this engine entrypoint and a matching terminal client together. The client cache can be kept inside Desktop's data root without reading or writing the separate Python installation's config. No additional system Python is needed.

## Common Patterns

### Updating

```bash
saba update --check       # Check the latest stable PyPI release; do not install
saba update               # Install it in an ordinary Python venv
saba update --dev         # Update source and prepare its matching interfaces
saba update --plan        # Save an exact review; do not install or restart
```

The first two commands target stable PyPI releases, not the saved Preview subscription. `--dev` (`--update-dev`) selects source, not Preview. `--plan --channel stable` or `--plan --channel preview` inspects that channel without changing the subscription; `--channel` requires `--plan`. Saved plans are not executed by `saba update`.

Before an in-place update, back up configuration, workspace files and chat history, then stop all processes sharing that Python environment. New versions may migrate stored data. Use the original [installation-specific route](./updating.md#installation-owners) for uv, pipx, containers, system packages and Desktop; do not overwrite a manager-owned environment with pip. Already-satisfying dependencies remain installed.

Source updates require Git. Existing editable checkouts fast-forward their current branch to its upstream; resolve local changes, detached HEADs and divergence manually. Updating a package with `--dev` creates an editable checkout under `~/.saba/src/` on the official `main` branch. saba downloads its pinned Bun when needed; Node is not required. To return to a release, install it in a separate environment and launch outside the checkout; in-place source-to-release switching is refused.

After installation, restart saba and verify the **running** gateway's version and behavior. The CLI checks the installation, not the live process. Downgrading requires `--allow-downgrade` and compatible data; back up before using it.

In-place CLI updates have no automatic rollback. A failed or interrupted installation leaves an incomplete-update marker under `~/.saba/run/`. Stop saba and retry the same update from that environment. On Windows, stop processes holding installation files and retry with that environment's `python -m saba update` (add `--dev` for source).

The WebUI's **Settings → About** uses a separate reviewed update-and-restart flow for supported installations and shows owner-specific instructions for others. See [Updating saba](./updating.md) for Preview selection, recovery and permission limits. Source updates remain CLI-only. To inspect a saved WebUI job, use `saba update --job <plan-id>`; [explicit handoff retry](./updating.md#explicit-recovery-before-package-mutation) requires additional consent and an intact installation, not a post-install repair.

Most day-to-day commands use the default config and workspace. Advanced or multi-instance runs usually pass both paths explicitly:

```bash
saba agent --config ./bot-a/config.json --workspace ./bot-a/workspace -m "Hello"
saba gateway --config ./bot-a/config.json --workspace ./bot-a/workspace
saba serve --config ./bot-a/config.json --workspace ./bot-a/workspace
```

Use `--verbose` on long-running processes when you need startup or runtime logs:

```bash
saba gateway --verbose
saba serve --verbose
```

Long-running commands keep working until you stop them. Press `Ctrl+C` in that terminal to stop foreground `saba gateway` or `saba serve`. If you started the gateway with `--background`, use `saba gateway stop`.

## Setup

| Command | Description |
|---|---|
| `saba onboard` | Initialize or refresh the default config and workspace |
| `saba onboard --refresh` | Refresh an existing config without prompting, preserving existing values |
| `saba onboard --wizard` | Use the interactive setup wizard |
| `saba onboard --config <path> --workspace <path>` | Initialize or refresh a specific instance |

Default paths:

| Path | Default |
|---|---|
| Config | `~/.saba/config.json` |
| Workspace | `~/.saba/workspace/` |

## Status

| Command | Description |
|---|---|
| `saba status` | Summarize the default config/workspace and check Agent provider/model readiness |
| `saba status --config <path>` | Check a specific config file |
| `saba status --workspace <path>` | Show status with a workspace override |

Status does not send a model request. On success, run the printed `saba agent -m "Hello!"` command to verify network access and credentials. On failure, follow the printed WebUI **Settings → Models** or `saba onboard --wizard` route.

## Agent CLI

| Command | Description |
|---|---|
| `saba -m "Hello!"` | Send one message and exit |
| `saba` | Start interactive terminal chat |
| `saba --session <id>` | Use a WebSocket session key; add `--classic` for another channel |
| `saba --workspace <path>` | Override workspace |
| `saba --config <path>` | Use a specific config file |
| `saba --classic` | Use the classic Python prompt instead of the native terminal UI |
| `saba --theme auto\|dark\|light` | Auto-detect the terminal appearance or force a TUI palette |
| `saba --no-markdown` | Use the classic prompt and print plain text instead of Markdown |
| `saba --logs` | Use the classic prompt and show runtime logs while chatting |

Inside the native TUI, `/sessions` switches saved conversations, `/new-chat` starts another saved conversation, and `/context` explains the compacted summary and raw session suffix available to the next agent turn. `/branch` forks a saved conversation from a completed reply, and `/diff` opens the latest turn's file changes as a full-screen unified diff. `PageUp` loads older transcript pages when you reach the top. By default, each launch starts a new session using the launch directory as its workspace. `--session` selects a specific existing session, and `--workspace` overrides the launch directory. When the TUI exits, it prints a ready-to-run `saba agent --session ...` command for the current session.

## Session Storage

Session state lives in `<config-dir>/sessions/<workspace-id>/sessions.sqlite3`, outside the agent-readable workspace. Existing JSONL conversations are imported on the first startup. JSONL migration is available from 0.3.6 through 0.4.x and is removed in **0.5.0**; installations with only JSONL data must upgrade through that window before using 0.5.0.

After a successful import, JSONL files and their checkpoints from `<workspace>/sessions/` move to `<config-dir>/sessions/<workspace-id>/jsonl-backup/`, preserving their contents outside the agent-readable workspace. JSONL files already in the private session directory remain there. An interrupted migration resumes on startup before saba serves conversations; failed imports leave their source files unchanged.

WebUI chat history is saved in the same session database. The gateway automatically imports old `<config-dir>/webui/*.jsonl` files and numbered JSONL files inside `<config-dir>/webui/*.segments/` directories. If old history is damaged or cannot be matched to one conversation, startup stops with an error; resolve the reported problem before restarting.

The old WebUI history files remain unchanged as backups. Imported chats deleted after the upgrade stay deleted on restart. Keep the `webui` directory: it still contains sidebar preferences and other saved WebUI state.

Before changing versions, stop all saba instances using the same config directory and back up that entire directory and the workspace together. Copying only `sessions.sqlite3` while saba is running can miss recent messages. To downgrade, restore a complete pre-upgrade backup compatible with the older release. Older releases cannot read newly saved WebUI history; do not combine the current session database with old WebUI history files.

Interactive mode uses saba's native TypeScript terminal UI. It talks to the same local gateway as the WebUI, so streaming, tool progress, and WebSocket sessions share one protocol instead of maintaining a second agent loop. If no gateway is running, either client starts it on demand. The TUI paints immediately while the local gateway starts, then obtains fresh bootstrap credentials and connects in the background. Exiting one TUI or WebUI launcher releases only that client; the last interactive launcher stops the on-demand gateway. A small gateway watchdog also reclaims an on-demand process if its last client crashes. `/detach` promotes the shared gateway to persistent background mode before closing the TUI, so active agent work continues without a connected client. An explicit `saba gateway --background` starts or promotes the gateway the same way before opening a client. `saba gateway restart` restarts a detached gateway without changing that lifetime; restart an attached foreground gateway in its owning terminal. `saba gateway stop` ends either mode.

The default `--theme auto` mode paints first with the terminal's default background, probes the real foreground and background colors asynchronously, and follows supported live appearance changes. Use `--theme light` or `--theme dark` when a terminal or multiplexer does not report its colors reliably. The model preset and workspace access labels above the composer can be clicked to open their selectors; arrow keys, `Enter`, and `Esc` provide the same controls without a mouse. Access changes still pass through the gateway's local-trust and active-turn policy checks.

`Enter` sends the current message. While saba is working, `Enter` sends immediately, `Tab` waits until the current response is finished, and `Option+Up` on macOS (`Alt+Up` on Windows/Linux) returns the latest waiting message to the composer. Press `Shift+Enter` to add a newline; `Ctrl+J` is the universal fallback when a terminal cannot distinguish modified Enter keys. `Alt+Enter` and `Ctrl+Enter` are also accepted when distinguishable. Use `Up`/`Down` at the composer edge to recall prompts from the current saved session. Large pastes appear as a compact placeholder in the composer but are sent unchanged. Type `/` to discover saba commands and terminal navigation in one palette, or type `@` to complete installed apps, configured MCP servers, and saved sessions. Use the arrow keys to choose an item and `Tab` to complete it. `/sessions` opens a searchable conversation picker, `/new-chat` preserves the current conversation and starts another one, and `/branch` forks from a completed reply. `/diff` opens a read-only unified diff for the newest turn; use `Left`/`Right` to switch edits and `Esc` to close it. The core `/new` command retains its cross-channel behavior and resets the current chat. `Ctrl+C` copies a selection, stops a running turn, clears a non-empty composer, or exits when idle. Use `PageUp`/`PageDown` to scroll, `Ctrl+Home`/`Ctrl+End` to jump to the transcript edges, and `Ctrl+O` to expand or collapse long tool traces. When you leave the bottom, the TUI shows a scrollbar and a `Ctrl+End` hint until you return. The footer reports provider token/cache usage when available. Selections copy through OSC 52 when the terminal supports it. The transcript reflows when the terminal is resized, and exiting restores the previous screen.

Platform wheels bundle the matching native terminal executable for macOS 13+ (Apple Silicon and Intel), glibc 2.17+ Linux (x64 and ARM64), and Windows x64. The x64 runtime requires SSE4.2. Its licenses, third-party notices, source offer, relinking instructions, and corresponding TUI source are installed alongside it in `saba/tui/bin/`. The launcher uses this bundled executable without downloading from GitHub or requiring Bun.

Source-distribution builds do not contain a native executable; where supported, their launcher can still fetch the version-matched GitHub release archive. `SABA_TUI_NO_DOWNLOAD=1` disables that fallback, not the bundled TUI. Use `--classic` to explicitly select the Python prompt. Windows ARM64 and musl-based Linux (such as Alpine) do not have a supported native TUI wheel; use the classic prompt or WebUI. In particular, Windows ARM64 cannot run OpenTUI because Bun disables the required FFI there. A local editable source install requires Bun and runs its own `tui/` source while the original checkout remains available; it never silently falls back to a release binary.

Non-interactive input/output, `--logs`, and `--no-markdown` automatically retain the classic prompt so existing scripts and diagnostic workflows do not acquire terminal control sequences or silently ignore their options.

Interactive mode exits with `exit`, `quit`, `/exit`, `/quit`, `:q`, or `Ctrl+D`. Use `/detach` instead to close the TUI without stopping the shared gateway or its active agent work. The restored terminal prints a copyable stop command with the same `--config` and explicit `--workspace` selectors.

## WebUI

| Command | Description |
|---|---|
| `saba webui` | Prepare local WebUI settings and open the browser; installer-managed environments launch persistently, other installations remain attached and follow gateway logs |
| `saba webui --detach` | Explicitly start or join a persistent gateway, open the browser and return control to the terminal |
| `saba webui --background` | Deprecated; prints the equivalent explicit `saba gateway --background` command and exits |
| `saba webui --dev` | Start the gateway and Vite together at `http://127.0.0.1:5173`, with live frontend updates |
| `saba webui --no-open` | Prepare and start the WebUI without opening a browser |
| `saba webui --no-dock` | Suppress the macOS Dock icon; detached mode remembers this choice until the next WebUI launch |
| `saba webui --port <port>` | Set the WebUI/WebSocket port |
| `saba webui --gateway-port <port>` | Override the gateway health port |
| `saba webui --yes` | Apply safe localhost WebUI defaults without confirmation; configure provider credentials in **Settings → Models** |

First-run WebUI setup binds to `127.0.0.1` by default. Use manual configuration and a WebUI password before exposing the WebSocket channel beyond localhost.

`--dev` is a foreground source-checkout workflow and cannot be combined with `--detach`. It installs frontend dependencies when `webui/node_modules` is missing, proxies to the configured WebSocket channel port, and stops Vite when the launcher exits. The shared on-demand gateway stops only when no other interactive client still holds it. Installer-managed normal WebUI launches and explicit `--detach` use the gateway's persistent lifecycle; manage that same instance with the `gateway` commands below. The old `webui --background` spelling remains deprecated and prints migration guidance.

## Gateway

`saba gateway` starts enabled chat channels, WebUI/WebSocket when configured, cron-backed system jobs, Dream, heartbeat, and the health endpoint. Most local browser users should start with `saba webui`; use `gateway` directly for service management, chat app operation, and advanced deployment. By default it runs in the foreground, which keeps existing scripts and terminal workflows unchanged. Use `--background` when you want a local macOS, Linux, or Windows process that you can manage from the CLI.

| Command | Description |
|---|---|
| `saba gateway` | Start the gateway in the foreground with config defaults |
| `saba gateway --verbose` | Show verbose runtime output |
| `saba gateway --port <port>` | Override `gateway.port` for the health endpoint |
| `saba gateway --workspace <path>` | Override workspace |
| `saba gateway --config <path>` | Use a specific config file |
| `saba gateway --background` | Start the gateway as a background process |
| `saba gateway status` | Show PID, foreground/background launch mode, explicit/on-demand lifetime, live client count, state, and logs |
| `saba gateway logs --no-follow` | Print recent background gateway logs and exit |
| `saba gateway logs` | Follow background gateway logs |
| `saba gateway restart` | Restart the recorded background gateway with the current config |
| `saba gateway stop` | Stop the recorded background gateway |
| `saba gateway install-service` | Install a systemd user service or macOS LaunchAgent |
| `saba gateway install-service --dry-run` | Preview the generated service file and system commands |
| `saba gateway uninstall-service` | Remove the installed system service |

On Windows, `gateway stop` waits up to `--timeout` seconds (default: 20) for the gateway to stop normally. If a forced stop is needed, the command displays a warning. Forced stops can interrupt active work.

For custom instances, pass the same selector flags after the management subcommand, as shown below. `--config` and `--workspace` before a management subcommand are rejected with a usage error; they are not inherited.

```bash
saba gateway --background --config ./bot-a/config.json --workspace ./bot-a/workspace
saba gateway status --config ./bot-a/config.json --workspace ./bot-a/workspace
saba gateway stop --config ./bot-a/config.json --workspace ./bot-a/workspace
saba gateway install-service --config ./bot-a/config.json --workspace ./bot-a/workspace --name bot-a
```

`--background` is a lightweight detached process. `install-service` is for login/startup integration: Linux uses a systemd user service; macOS uses a LaunchAgent plist. System services run the foreground gateway under the OS supervisor rather than nesting another background process.

Default health endpoint:

```text
http://127.0.0.1:18790/health
```

The bundled WebUI is served by the WebSocket channel, usually on port `8765`, not by the gateway health endpoint.

## Local Triggers

`saba trigger` delivers one local message to a trigger that was created from a chat/session with `/trigger <name>`.

```bash
saba trigger trg_8K4P2Q9X "Review PR #4502"
```

Keep `saba gateway` running so the message can be delivered to the linked chat/session. The message is recorded as an automation turn in that session, not as a normal chat message typed by the user.

The command writes to a workspace-local durable queue. If `saba gateway` is not running yet, the message waits in that workspace. If the target session is already running a turn, the trigger waits for that session to become idle. If the gateway exits after claiming a delivery but before the linked turn completes, the next gateway start requeues that delivery. The queue is at-least-once, not exactly-once, so the same message can be delivered again after an interrupted process. If the agent receives the delivery and the turn fails, the delivery is marked failed instead of retried indefinitely. Each delivery also writes an audit record under `<workspace>/triggers/runs`. Run one gateway consumer per workspace; this local queue is not a distributed multi-consumer queue.

Use stdin when another local process generates the message:

```bash
generate-report | saba trigger trg_8K4P2Q9X
```

Options:

| Command | Description |
|---|---|
| `saba trigger <id> "message"` | Deliver one message through a trigger |
| `saba trigger <id>` | Read the message from stdin |
| `saba trigger --config <path> <id> "message"` | Use the workspace from a specific config |
| `saba trigger --workspace <path> <id> "message"` | Use a specific workspace |

Triggers are managed in the WebUI Automations view instead of through separate `list`, `revoke`, or `delete` CLI subcommands. From there you can pause/resume, rename, delete, search, and copy the command for each trigger.

For webhooks or other external systems, run your own small service and have it call this CLI after it decides what message saba should receive.

See [Automations](./automations.md) for the broader automation model, WebUI management, and delivery behavior.

## OpenAI-Compatible API

| Command | Description |
|---|---|
| `saba serve` | Start `/v1/chat/completions`, `/v1/models`, and `/health` |
| `saba serve --host <host>` | Override API bind host |
| `saba serve --port <port>` | Override API port |
| `saba serve --timeout <seconds>` | Override per-request timeout |
| `saba serve --verbose` | Show runtime logs |
| `saba serve --workspace <path>` | Override workspace |
| `saba serve --config <path>` | Use a specific config file |

Default API endpoint:

```text
http://127.0.0.1:8900
```

Public binds (`0.0.0.0` or `::`) require `api.apiKey`; send it as a Bearer token on API routes.

See [`openai-api.md`](./openai-api.md) for request examples.

## Status

```bash
saba status
```

Shows the config path, workspace path, active model, and provider summary without calling a model.

| Command | Description |
|---|---|
| `saba status` | Inspect the default instance |
| `saba status --config <path>` | Inspect a specific config |
| `saba status --config <path> --workspace <path>` | Inspect a specific config with a workspace override |

## Channels

| Command | Description |
|---|---|
| `saba channels status` | Show configured channel status |
| `saba channels status --config <path>` | Show channel status for a specific config |
| `saba channels login <channel>` | Run interactive login for supported channels |
| `saba channels login <channel> --force` | Re-authenticate even if credentials already exist |
| `saba channels login <channel> --config <path>` | Use a specific config file |
| `saba plugins list --config <path>` | Show plugin/channel enabled state for a specific config |

Examples:

```bash
saba channels login whatsapp
saba channels login weixin
saba channels status
```

See [`chat-apps.md`](./chat-apps.md) for channel-specific setup.

## Optional Features

Use these commands when you want saba to add or remove a built-in capability without hand-editing JSON. Enabling may install the support package first. Disabling is for channels such as Telegram, Matrix, or Slack; it keeps your saved settings and turns the channel off.

The `plugins` command name is retained for compatibility, but these entries are saba runtime support packages, not the user-invokable tools shown in WebUI Apps. They cannot be attached to a chat turn with `@`.

| Feature name | What it enables |
|---|---|
| `api` | Dependencies required by the OpenAI-compatible `saba serve` process |
| `azure` | Azure identity support for Azure-hosted models |
| `bedrock` | AWS Bedrock model provider support |
| `langfuse` | Langfuse tracing support for OpenAI-compatible providers and the Codex OAuth provider |
| `olostep` | Olostep web search provider support |
| A channel name such as `telegram` or `slack` | The connector package and saved channel enablement |

| Command | Description |
|---|---|
| `saba plugins list` | Show available channels and optional capabilities |
| `saba plugins enable <name>` | Install missing support and enable the feature or channel |
| `saba plugins enable <name> --logs` | Show package install logs while enabling |
| `saba plugins disable <channel>` | Turn off a channel without deleting its saved settings |
| `saba plugins list --config <path>` | Read a specific config file |
| `saba plugins enable <name> --config <path>` | Update a specific config file |
| `saba plugins disable <channel> --config <path>` | Turn off a channel in a specific config file |

Document and PDF reading are included in the standard installation. The old `saba plugins enable documents` and `saba plugins enable pdf` commands remain accepted as no-op compatibility aliases.

## Provider OAuth

| Command | Description |
|---|---|
| `saba provider login openai-codex --set-main` | Authenticate Codex and select its current default model |
| `saba provider login xai-grok --set-main` | Authenticate an eligible X Premium / Grok subscription and select Grok 4.6; hosted X Search is enabled for models that advertise support |
| `saba provider login github-copilot --set-main` | Authenticate GitHub Copilot and select its current default model |
| `saba provider logout openai-codex` | Remove OpenAI Codex OAuth state |
| `saba provider logout xai-grok --config <path>` | Remove the selected saba instance's xAI OAuth state |
| `saba provider logout github-copilot` | Remove GitHub Copilot OAuth state |

See [`providers.md`](./providers.md#oauth-providers) for when OAuth providers need explicit provider/model selection.

## Useful First Checks

```bash
saba --version
saba status
saba agent -m "Hello!"
```

If these fail, use [`troubleshooting.md`](./troubleshooting.md) before debugging WebUI, chat apps, Docker, systemd, or SDK integrations.
