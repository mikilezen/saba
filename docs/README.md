# saba Documentation

Use these docs to get a working agent first. After the first reply, describe your next goal to saba or choose a task guide to read yourself. Source-level design and extension details are kept in the contributor section.

Repository docs follow the current source tree. For the original saba release docs, visit [saba.wiki](https://saba.wiki/docs/latest/getting-started/saba-overview).

Use the graphical setup steps first when the WebUI exposes the setting. Expand **Manual configuration** for headless deployments or configuration managed as code. Settings without a graphical control keep their direct configuration instructions.

## Start Here

| Your situation | Read this | You are done when... |
|---|---|---|
| Terminals, Python, or API keys are new to you | [Beginner walkthrough](./start-without-technical-background.md) | The browser can send `Hello!` and receive a reply |
| You are comfortable running commands | [Install and Quick Start](./quick-start.md) | `saba status` is healthy and the WebUI or CLI can get one reply |
| saba will not start | [Troubleshooting: Installation Problems](./troubleshooting.md#installation-problems) | saba starts, or you know what to fix next |
| The browser or chat app opens, but saba does not reply | [Troubleshooting: Provider and Model Problems](./troubleshooting.md#provider-and-model-problems), [WebUI Problems](./troubleshooting.md#webui-problems), or [Chat App Problems](./troubleshooting.md#chat-app-problems) | You have a working reply or a specific next step |

The recommended first-run path is:

1. Install saba.
2. Let the installer open `saba webui` on a fresh local desktop.
3. Configure a provider and model in **Settings → Models**.
4. Send `Hello!` before configuring anything else.

Most people do not need to edit JSON for the first run. The WebUI handles the initial provider, model, and local browser settings. SSH, headless, existing-config, and older-release installs retain `saba onboard --wizard` as a terminal fallback. After the WebUI opens, use **Settings** for models and built-in capabilities, **Channels** for chat apps, and **Apps** for Agent Plugins, CLI Apps, and MCP integrations.

## After the First Reply

When the built-in `saba-document` skill is available and enabled, saba can consult the documentation bundled with your installation as you ask about features, configuration, or errors. Describe your current setup and one goal in the same chat; see [Continue with saba](./quick-start.md#continue-with-saba) for examples and explicit skill invocation. The skill links to the task and reference pages below as needed.

For independent reading, choose a task guide below. Use the reference section when you need an exact field, default, command, or protocol detail.

## Add One Capability

Pick the row that matches what you want to accomplish next:

| Goal | Guide |
|---|---|
| Learn the browser workbench | [WebUI](./webui.md) |
| Connect Telegram, Discord, Slack, Feishu, WeChat, Email, or another chat app | [Chat Apps](./chat-apps.md) |
| Choose a hosted, OAuth, company, or local model | [Provider Cookbook](./provider-cookbook.md) |
| Add model fallbacks | [Configure Model Fallback](./guides/configure-model-fallback.md) |
| Enable web search | [Configure Web Search](./guides/configure-web-search.md) |
| Manage Agent Plugins, CLI Apps, or MCP integrations | [WebUI Apps](./webui.md#apps) |
| Add an MCP tool server | [Configure MCP Tools](./guides/configure-mcp-tools.md) |
| Generate images | [Image Generation](./image-generation.md) |
| Schedule work or create a local trigger | [Automations](./automations.md) |
| Understand and manage long-term memory | [Memory](./memory.md) |
| Run saba continuously | [Deployment](./deployment.md) |
| Run separate bots or workspaces | [Multiple Instances](./multiple-instances.md) |
| Call saba from Python | [Python SDK](./python-sdk.md) |
| Expose an OpenAI-compatible endpoint | [OpenAI-Compatible API](./openai-api.md) |

For shorter, outcome-focused walkthroughs, browse the [task guide index](./guides/README.md).

## Operate saba

| Need | Read |
|---|---|
| Commands and flags | [CLI Reference](./cli-reference.md) |
| Update an installation or recover an interrupted update | [Updating saba](./updating.md) |
| In-chat slash commands | [In-Chat Commands](./chat-commands.md) |
| Config, workspace, gateway, sessions, tools, and memory in plain language | [Concepts](./concepts.md) |
| Provider/model matching and selection | [Providers and Models](./providers.md) |
| Setup and runtime diagnosis | [Troubleshooting](./troubleshooting.md) |
| Older development highlights | [Release Archive](./release-archive.md) |

## Reference

Use reference pages to look up an exact option after you know what you are trying to configure:

| Area | Reference |
|---|---|
| Every configuration field and default | [Configuration](./configuration.md) |
| Provider and model behavior | [Providers and Models](./providers.md) |
| Chat channel prerequisites and manual JSON | [Chat Apps](./chat-apps.md) |
| WebSocket authentication and wire protocol | [WebSocket](./websocket.md) |
| Python SDK classes, events, sessions, and hooks | [Python SDK](./python-sdk.md) |
| OpenAI-compatible HTTP routes and payloads | [OpenAI-Compatible API](./openai-api.md) |
| Runtime self-inspection and tuning | [My Tool](./my-tool.md) |

Configuration examples are usually snippets to merge into `~/.saba/config.json`, not complete replacement files. The docs use camelCase because saba writes config that way. Keep real API keys, bot tokens, and passwords out of issues and public logs.

## Extend or Contribute

These pages explain implementation and extension points. You do not need them to install or operate saba.

| Goal | Read |
|---|---|
| Understand source ownership and runtime flow | [Architecture](./architecture.md) |
| Set up a development environment | [Development](./development.md) and [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Add a channel package | [Channel Package Guide](./channel-package-guide.md) |
| Build the WebUI source | [WebUI Development](../webui/README.md) |
| Change update APIs, execution or recovery | [Update protocol](./update-protocol.md) |
| Prepare and publish a release | [Release checklist](./releasing.md) |

If a command or screen no longer matches these docs, please [open an issue](https://github.com/mikilezen/saba/issues) with your saba version, operating system, and the page that needs correction.
