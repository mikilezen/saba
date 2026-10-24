# Saba AI: Minimal Setup

Saba is a self-hosted AI assistant with a browser WebUI, terminal interface, channels, tools, and skills.

This setup is intended for a clean local installation on Windows, macOS, or Linux.

## Requirements

- Python 3.11 or newer
- Git
- An API key or account for a supported AI model provider
- Node.js and Bun only when developing the WebUI
- Docker Desktop only when using Docker

## Install and run

From the directory that contains `pyproject.toml`:

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

The last command starts the gateway and opens the WebUI at `http://127.0.0.1:8765`.

1. Open **Settings → Models**.
2. Create a model preset and enter the provider credentials.
3. Start a new topic and send `Hello!`.

Keep API keys and the browser sign-in link private.

## Run again later

```powershell
# Windows
.\.venv\Scripts\saba.exe webui
```

```bash
# macOS or Linux
./.venv/bin/saba webui
```

Check the installation if the gateway does not start:

```powershell
# Windows
.\.venv\Scripts\saba.exe --version
.\.venv\Scripts\saba.exe status
```

```bash
# macOS or Linux
./.venv/bin/saba --version
./.venv/bin/saba status
```

## WebUI development

The packaged application already includes the built WebUI. Use this section only when changing frontend code.

```bash
cd webui
bun install
bun run dev
```

For the supported gateway-aware development mode, run this from the project root:

```bash
saba webui --dev
```

Useful checks:

```bash
cd webui
bun run lint
bun run typecheck
bun run test
bun run build
```

## Docker Compose

With Docker Desktop running:

```bash
docker compose up --build
```

The gateway is available at `http://127.0.0.1:8765`. Stop it with:

```bash
docker compose down
```

## Project credits

- **Project adaptation and setup:** Mikiyas Zenebe
- **Original Saba project and maintainers:** [mikilezen/saba](https://github.com/mikilezen/saba)
- **Nanobot inspiration and open-source community:** [HKUDS/nanobot](https://github.com/HKUDS/nanobot)
- **OpenClaw inspiration and open-source community:** [openclaw/openclaw](https://github.com/openclaw/openclaw)

Saba is released under the MIT License. See [LICENSE](./LICENSE) for the complete license text. Please preserve upstream copyright and license notices when redistributing changes.
