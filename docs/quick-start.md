# Install and Quick Start

Install Saba from its GitHub source, connect one AI model, and send a test message. If you are new to terminals or API keys, use the [beginner walkthrough](./start-without-technical-background.md).

## What You Need

- Python 3.11 or newer.
- Access to the Saba GitHub repository.
- Access to an AI provider or a local model server.
- The sign-in details or API key and model name required by that provider. Check its pricing before use.

For help choosing a provider, see the [Provider Cookbook](./provider-cookbook.md).

## 1. Download and Install Saba

Sign in to GitHub with an account that can access Saba, [download the source ZIP](https://github.com/mikilezen/saba/archive/refs/heads/main.zip), and extract it. If you already have the source folder, skip the download. Open PowerShell or Terminal in the folder that contains `pyproject.toml`.

**macOS / Linux**

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -e .
./.venv/bin/saba webui
```

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\saba.exe webui
```

The last command opens Saba in your browser. To open it again later, rerun the matching command above from the source folder.

For SSH or a computer without a browser, run `./.venv/bin/saba onboard --wizard` on macOS or Linux, or `.\.venv\Scripts\saba.exe onboard --wizard` in PowerShell. You can also follow the [deployment guide](./deployment.md).

## 2. Configure Your Model

In the WebUI, open **Settings → Models**:

1. Choose **New preset**. If **Convert to presets** appears, choose it first.
2. Select a provider, or choose **Add provider**. Sign in or enter the provider’s API key and connection details.
3. Select a model available to your account and save the preset.

Keep API keys private.

## 3. Get Your First Reply

Start a new topic and send:

```text
Hello!
```

A normal reply means setup is complete. To open Saba again later, rerun the matching WebUI command from step 1.

## Continue with saba

Once the first reply works, ask saba for help with one next task or choose a guide from the [documentation index](./README.md). If the built-in `saba-document` skill is available and enabled, you can ask it to explain a feature or guide setup.

## If Something Goes Wrong

Run `./.venv/bin/saba --version` and `./.venv/bin/saba status` on macOS or Linux, or `.\.venv\Scripts\saba.exe --version` and `.\.venv\Scripts\saba.exe status` in PowerShell, then follow the [Troubleshooting guide](./troubleshooting.md). For an invalid-key error, confirm the key belongs to the provider selected in your model preset.

## Updating

Use the same method you installed with, or follow [Updating Saba](./updating.md).
