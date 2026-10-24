# Start Without Technical Background

This guide gets Saba running and answers one message. You do not need to edit a configuration file.

## Before You Start

- A Windows, macOS, or Linux computer with Python 3.11 or newer.
- Access to the Saba GitHub repository.
- Access to an AI provider or a model running on your computer.
- The provider’s sign-in or API key and the model name it supports.

An account on a chat website may not include API access. See the [Provider Cookbook](./provider-cookbook.md) if you need help choosing a service. Keep API keys and complete browser sign-in links private.

## 1. Install Python and Open a Terminal

If Python is not installed, download version 3.11 or newer from [python.org](https://www.python.org/downloads/). On Windows, enable **Add python.exe to PATH** if you see that option.

Open **PowerShell** on Windows, **Terminal** on macOS, or a terminal app on Linux. Check Python:

```bash
python --version
```

If the command is not found, close and reopen the terminal. On macOS or Linux, try `python3 --version`; on Windows, try `py --version`.

## 2. Download and Install Saba

Sign in to GitHub with an account that can access Saba, [download the source ZIP](https://github.com/mikilezen/saba/archive/refs/heads/main.zip), and extract it. If you already have the source folder, skip the download. Open the folder in File Explorer or Finder, then open a terminal in it. Confirm it contains `pyproject.toml` before running the commands below.

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

The last command opens Saba in your browser. Keep the terminal open while you use Saba. For other setup options, see [Install and Quick Start](./quick-start.md).

## 3. Connect Your Model

In the browser, open **Settings → Models**:

1. Choose **New preset**.
2. Select your provider, or choose **Add provider**. Sign in or enter its API key and connection details.
3. Choose a model available to your account and save the preset.

Keep your API key private. If you are unsure which provider or model to use, see the [Provider Cookbook](./provider-cookbook.md).

## 4. Send a Test Message

Start a new topic and send:

```text
Hello!
```

A normal reply means setup is complete. To open Saba later, rerun the matching WebUI command from step 2.

If it does not reply, run `./.venv/bin/saba status` on macOS or Linux, or `.\.venv\Scripts\saba.exe status` in PowerShell, then follow [Troubleshooting](./troubleshooting.md).

## Your First File Task

After Saba replies, you can try it with a copy of a text file:

1. Create a practice folder and put a copy of `notes.txt` inside it.
2. In a new WebUI topic, select that folder as the workspace and choose **Restricted** access.
3. Ask Saba to summarize `notes.txt` into `summary.md`, then open the new file to check it.

Use a copy of your file for this first task. For more about workspaces and file access, see [Workspace and Access](./webui.md#workspace-and-access).
