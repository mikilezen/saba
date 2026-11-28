# Saba

**An independent, self-hosted AI assistant you can run, customize, and extend.**

Saba's Python gateway brings models, tools, memory, files, and messaging channels into one environment you control. Run it locally or on your own server, choose your model provider, and use Saba through the browser, a separate terminal app, or a connected chat platform.

[Features](#what-saba-does) · [Quick Start](#quick-install-with-frozen-dependencies) · [Screens](#webui-screens) · [Documentation](#documentation-and-support) · [GitHub Issues](https://github.com/mikilezen/saba/issues)

<p align="center">
  <img src="./images/logo.png" alt="Saba AI" width="380">
</p>
<!-- 
<p align="center">
  <img src="./images/saba_mascot.png" alt="Saba mascot" width="140">
</p> -->

<p align="center">
  <img src="./images/screens/webui-new-chat.png" alt="Saba WebUI chat workspace" width="900">
</p>

## What Saba does

- **Chat:** Start topics in the browser or terminal and continue them later.
- **Work with files:** Read and process documents such as PDF, Word, Excel, and PowerPoint files.
- **Use tools:** Run approved shell, web, MCP, document, and automation tools when enabled.
- **Remember context:** Keep session history and selected long-term preferences.
- **Connect channels:** Use the WebUI, Telegram, WhatsApp, and other supported channels.
- **Ethiopian service workflows:** The separate `saba_et` app supports language-aware public-service discovery over Telegram, with optional voice integrations. See [Ethiopian integrations](./saba_et/README.md).
- **Use different models:** Configure hosted providers, OpenAI-compatible endpoints, or local model servers.
- **Automate work:** Create scheduled tasks and longer-running goals.
- **Develop and extend:** Add skills, plugins, MCP servers, providers, and channel integrations.

## Saba's product work

This repository brings together several substantial parts of the product:

- **Python gateway:** Runs agent turns and owns provider calls, session state, memory, workspace scope, and tool permissions.
- **Two separate clients:** The React WebUI and TypeScript terminal UI use the same gateway and shared event contracts. See the [terminal UI guide](./tui/README.md).
- **Extension system:** Provider and channel adapters connect with built-in tools, MCP servers, plugins, and skills.
- **Ethiopian service assistant:** `saba_et` is a separate, language-aware public-service app with Telegram and optional voice integrations. See [its guide](./saba_et/README.md).

## What Saba does not do automatically

- It does **not** provide an AI model or API key. You must connect a provider or local model.
- It does **not** make every tool safe. Review permissions before enabling shell, browser, file, or external-service tools.
- It does **not** upload all local files by default. File access depends on the workspace and tools you approve.
- It does **not** guarantee that model responses are correct. Check important answers and generated changes.
- It does **not** expose your WebUI safely to the public internet by default. Use authentication and follow the deployment guidance before remote access.
- It does **not** require Node.js or Bun for normal users. They are needed only for WebUI development.

## How it works

1. You send a message from the WebUI, terminal, or a connected channel.
2. Saba sends the message and permitted context to your selected model.
3. The model may request an enabled tool, such as reading a file or searching the web.
4. Saba asks for permission when required, runs the tool, and returns the result to the model.
5. The model produces a response, which Saba shows in the same conversation.

The model provides language generation. Saba's Python gateway manages agent execution, conversations, permissions, tools, channels, and memory; the WebUI and terminal UI are separate clients of that same gateway.

```mermaid
flowchart LR
    User((People)) --> WebUI["WebUI<br/>React client"]
    User --> TUI["Terminal UI<br/>TypeScript client"]
    User --> ChatApps["Connected chat platforms"]

    WebUI -->|HTTP and WebSocket| API["Python gateway API"]
    TUI -->|WebSocket and REST| API
    ChatApps --> Adapters["Channel adapters"] --> Bus["Message bus"]

    subgraph Gateway["Saba Python gateway"]
        API --> Bus
        Bus --> Loop["Agent loop"] --> Runner["Agent and tool runner"]
        Loop <--> State["Sessions, context, and memory"]
        Runner --> Providers["Model provider adapters"]
        Runner <--> Tools["Tools and permissions"]
        Tools --> Extensions["MCP · skills · plugins"]
    end

    Providers --> Models["Hosted or local models"]
    WebUI -.-> Contracts["Shared client event contracts"]
    TUI -.-> Contracts

    subgraph Ethiopia["Saba ET · separate application"]
        User --> Telegram["Saba ET Telegram bot"] --> ETApp["Public-service assistant"]
        Voice["Optional voice integrations"] --> ETApp
        ETApp --> Directory["Provider directory and source lookup"]
        ETApp --> Queue["Durable webhook queue"]
        ETApp --> Stores["Profiles · tasks · audit"]
        Catalog["Curated catalog<br/>data/"] --> Directory
        ETApp --> Research["Gemini grounding<br/>optional SearchAPI"]
    end
    Directory --> Official["Public-service sources"]
    Research --> Official
    Queue --> Supabase["Supabase Postgres on Render"]
    Stores --> Persistence["SQLite locally or Supabase Postgres"]
```

The WebUI and terminal UI do not contain separate agent runtimes. Both use the Python gateway, which owns execution, session state, tool access, and provider calls. Saba ET is a separate Ethiopia-focused application in this repository.

## Screens and architecture

The WebUI includes a chat workspace, channel management, plugin and tool management, skills, and controlled workspace access.

## WebUI screens

### Manage channels

The Channels screen lets you see and enable connected interfaces such as the Saba WebUI, Telegram, WhatsApp, and email.

<p align="center">
  <img src="./images/screens/webui-channels.png" alt="Saba WebUI channels screen" width="900">
</p>

### Manage plugins and tools

The Plugins screen shows available applications and tools, including browser automation, local model integrations, diagrams, and other extensions.

<p align="center">
  <img src="./images/screens/webui-plugins.png" alt="Saba WebUI plugins and tools screen" width="900">
</p>

### Manage MCP tools

The MCP screen lets you search available MCP integrations, connect tools, and add custom or imported MCP configurations.

<p align="center">
  <img src="./images/screens/webui-mcp.png" alt="Saba WebUI MCP tools screen" width="900">
</p>

### Browse skills

The Skills screen lists available task skills with short descriptions and example prompts.

<p align="center">
  <img src="./images/screens/webui-skills.png" alt="Saba WebUI skills screen" width="900">
</p>

## Choose your setup

| Goal | Use |
| --- | --- |
| Run Saba locally | Frozen Python dependencies with `uv` |
| Install without uv | A Python virtual environment and `pip install -e .` |
| Develop the React/TypeScript WebUI | Bun and Vite |
| Run reproducible containers | Docker Compose |
| Test the browser UI | Bun, Playwright, and Chromium |

For most users, use **Quick install with frozen dependencies**. Use the other sections only when you need them.

## Requirements

- Python 3.11 or newer
- Git
- An API key or account for a supported AI model provider
- [uv](https://docs.astral.sh/uv/) for the exact locked Python environment
- Bun only when developing the WebUI
- Docker Desktop only when using Docker

## Quick install with frozen dependencies

Run the commands for your operating system from the directory containing `pyproject.toml`.

### Windows PowerShell

```powershell
uv sync
.\.venv\Scripts\saba.exe webui
```

### macOS or Linux

```bash
uv sync
./.venv/bin/saba webui
```

`uv sync` uses the committed [`uv.lock`](./uv.lock), so the complete Python dependency graph is reproducible. If `uv` is not installed, install it from the [official guide](https://docs.astral.sh/uv/getting-started/installation/).

The WebUI opens at:

```text
http://127.0.0.1:8765
```

On first launch:

1. Open **Settings > Models**.
2. Create or select a model preset.
3. Enter the provider credential or configure a local OpenAI-compatible server.
4. Start a new topic and send `Hello!`.

Keep API keys and browser sign-in links private.

## Install with Python and pip

If you do not use `uv`, create a virtual environment and install the project directly from `pyproject.toml`.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\saba.exe webui
```

### macOS or Linux

```bash
python3.11 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
./.venv/bin/saba webui
```

The committed [`uv.lock`](./uv.lock) is the dependency freeze. The root [`requirements.txt`](./requirements.txt) is a small compatibility list and is not a replacement for the lockfile.

## Run later

```powershell
# Windows
.\.venv\Scripts\saba.exe webui
```

```bash
# macOS or Linux
./.venv/bin/saba webui
```

Check the installation:

```text
saba --version
saba status
```

## WebUI development and browser tests

The packaged application already contains the built WebUI. Use these commands only when changing frontend code:

```bash
cd webui
bun install
bun run dev
```

For gateway-aware development, run this from the project root:

```bash
saba webui --dev
```

Install the Chromium browser used by Playwright tests:

```bash
cd webui
bun x playwright install chromium
```

Run frontend checks:

```bash
bun run lint
bun run typecheck
bun run test
bun run test:browser
bun run build
```

## Docker Compose

With Docker Desktop running:

```bash
docker compose up --build
```

Open `http://127.0.0.1:8765`. Stop the services with:

```bash
docker compose down
```

## Documentation and support

- [Quick start](./docs/quick-start.md) · [Configuration](./docs/configuration.md) · [Providers](./docs/providers.md)
- [WebUI guide](./docs/webui.md) · [Deployment](./docs/deployment.md) · [Troubleshooting](./docs/troubleshooting.md)
- [Python SDK](./docs/python-sdk.md) · [OpenAI-compatible API](./docs/openai-api.md) · [Development guide](./docs/development.md)
- [Report a bug](https://github.com/mikilezen/saba/issues/new?template=bug_report.yml)

Saba is released under the MIT License. See [`LICENSE`](./LICENSE) and preserve upstream copyright and license notices when redistributing changes.

## Project foundation

Saba is developed and maintained as an independent project. Its agent runtime builds on the MIT-licensed [HKUDS/Nanobot](https://github.com/HKUDS/nanobot) foundation; this repository adds Saba's Python gateway, browser and terminal clients, integrations, extension system, and separate Ethiopia-focused application. Saba is not an official project of the upstream maintainers.
