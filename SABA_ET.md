# Saba ET

Telegram-first app for helping people navigate Ethiopian government services. This separately deployable Saba ET app lives beside the Saba agent framework in the saba_et package.

## Current slice

- Telegram long polling locally and a signed-webhook ASGI entry point for Render, with an interactive language picker for Amharic, Afaan Oromoo, Tigrinya, and English.
- A LangGraph workflow with a deterministic risk node, read-only catalog/provider lookup nodes, configurable Google Search, Gemini structured answers, and an official-source gate.
- By default Gemini performs grounded Google Search. Optionally enable SearchAPI Google results with `SEARCHAPI_ENABLED=true` and a rotated `SEARCHAPI_API_KEY`; results are restricted to official Ethiopian domains and passed to Gemini as untrusted evidence. SearchAPI is disabled by default and uses credits only when enabled.
- A curated `/providers` directory covers the agencies and public needs in `data/providers.json`. Verified official portal links are labeled separately from candidate links; no service API or transaction integration is claimed unless independently documented.
- Agent requests show changing Telegram status messages for catalog lookup, Gemini Search, answer drafting, and source checks. These are operational progress labels, not private model reasoning.
- Saba's internal output is validated as `answer`, `next_step`, `risk_level`, `risk_reason`, `requires_approval`, `tools_used`, `sources`, and `process_summary`. Risk and executed-tool metadata come from Python/LangGraph, not Gemini claims.
- With `GEMINI_MODEL=gemini-3.8-flash`, Gemini's Interactions API enforces an `answer`/`next_step` JSON schema together with Google Search in one request. The default `gemini-2.5-flash` preserves the lower-cost/free-tier search path: Gemini is prompted for JSON and Saba validates its application result, but the model's raw output schema is not enforced. A schema does not prove factual accuracy; Saba still withholds answers that lack approved official sources.
- Fayda connect or manual-entry choices. Fayda is marked unavailable until an approved official integration exists.
- Language preference and consented name, age, birth year, and location are stored in Supabase Postgres when `SUPABASE_DB_URL` is configured; local development falls back to SQLite. Profile fields are never sent to Gemini. `/forget` clears personal fields while keeping the language preference.
- On startup, the bot sets its Telegram display name to **Saba ET**. Conversation step and completed profile answers are persisted to the configured database, so a restart does not send an in-progress user back to the language picker or repeat completed questions.
- `/back` returns to the prior onboarding question so people can change an answer without restarting or using `/forget`. Each prompt replaces the previous reply keyboard; invalid age/year replies keep the Back button available.
- Explicit consent before manual personal details. Never ask for Fayda numbers, national ID numbers, passwords, or payment details.
- The LangGraph agent can request one narrowly scoped public-office call when official search cannot verify an answer. Saba supplies the phone only from the human-maintained `data/voice_contacts.json` allowlist; the model cannot invent a destination. Calls are disabled by default and require `VAPI_AUTO_CALL_ENABLED=true`, configured Vapi keys, a non-high-risk request, an enabled contact whose terms match the request, and an available daily quota. A secured Vapi webhook sends a short call summary to the initiating Telegram user; transcripts and recordings are not stored by Saba.
- High-risk requests such as calls, payments, account authentication, or submitting a form are marked for approval. High-risk calls are blocked. A low-risk outbound call is an explicit global opt-in: enabling `VAPI_AUTO_CALL_ENABLED=true` permits the agent to call only allowlisted office numbers under the stated limits.
- Render receives Telegram updates at `/telegram/webhook`, verifies Telegram's secret-token header, accepts Vapi call reports at `/vapi/webhook`, accepts signed Telnyx Voice API events at `/telnyx/webhook`, and exposes `/healthz` for health checks. The Telnyx endpoint answers inbound calls with a short setup notice; conversational voice support is not yet implemented. The local polling command removes an active Telegram webhook before polling.
- Goal state is stored in Supabase Postgres when configured. Telegram supports `/task create <goal>`, `/tasks`, `/task <id>`, `/task pause <id>`, and `/task resume <id>`; these commands manage task records only and do not submit applications or perform browser actions.
- Public website snapshots and JavaScript API hints are stored separately for human review; scraped text never becomes trusted facts automatically.

For Supabase provisioning and deployment setup, see [Supabase setup](docs/SUPABASE.md). For Render and voice-call setup, see the [Render deployment guide](docs/RENDER_DEPLOYMENT.md), [Amharic calling options](docs/AMHARIC_CALLING.md), and [copy-ready Vapi agent prompt](docs/VAPI_AGENT_PROMPT.md).

The fact catalog remains deliberately empty. `/providers` is the separate starting directory for official portals and requested service areas; entries without confirmed official links are labeled. Add procedural facts only after reviewing official sources. The eServices portal can render without returning service records to a plain page fetch, so dynamic data needs an official API or browser-rendered review before it is treated as fact.

In Telegram, send `/providers` to browse the directory or `/providers tax` (replace `tax` with `visa`, `fayda`, `power`, `education`, `police`, or another keyword) to filter it. `/services` opens the same directory while in the service-help flow.

To search and explore the live eServices portal in a local browser, install the optional browser dependency and Chromium, then run:

```powershell
python -m pip install -r requirements-browser.txt
python -m playwright install chromium
python scripts/eservices_agent.py "Trade License"
```

The helper checks the portal's `robots.txt`, searches the public service listing, displays rendered page text and visible same-site links, and moves the mouse to click a selected link. It stays open until you choose `q`; you can search again, refresh, go back, or inspect another result. With `GEMINI_API_KEY`, Gemini returns a validated JSON plan containing `page_summary`, `observed_facts`, `suggested_next_steps`, `needs_user_input`, and `user_input_reason`. With `TYPESAFE_API_KEY`, Jev (`jev-latest`) returns a typed next-action choice over only allowlisted public links and read-only actions; automatic navigation requires confidence of at least 0.75 and pauses for your input after ten steps. Without the TypeSafe key, choose the next action yourself. The helper can optionally fill non-sensitive text fields in that temporary browser session. It does not save browser state, handle identity/payment fields, upload files, or submit forms. Treat page text and AI suggestions as unverified until you confirm them on the official portal.

When an eServices login, signup, or account screen appears, the browser remains open in manual-only mode until you choose `q`; no page text is sent to Gemini or TypeSafe. CAPTCHA and verification prompts pause for you to complete them directly in the visible browser; type `resume` in the terminal afterward. Passwords, one-time codes, and CAPTCHA answers belong in the browser only, never in the terminal or AI prompts.

## Run

Requires Python 3.11+, a Telegram bot token from BotFather, and a Gemini API key for autonomous AI search. Google AI Studio lists Ethiopia as a supported Gemini API region. Grounded search depends on the key's tier.

Create `.env` from `.env.example` in the project root, then enter freshly rotated keys locally. Startup loads `.env` automatically; values already set in PowerShell take precedence.

```powershell
Copy-Item .env.example .env
notepad .env
```

Keep `.env` out of Git and chat. If a key was pasted into chat or committed, revoke it and create a replacement. `GEMINI_MODEL` is optional; it defaults to `gemini-2.5-flash`. Local long polling needs no public webhook; Render uses the HTTPS webhook service described in the deployment guide.

PowerShell (environment variables instead of `.env`):

```powershell
$secureToken = Read-Host "Paste the freshly rotated BotFather token" -AsSecureString
$tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
try {
  $env:TELEGRAM_BOT_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)
  python -m saba_et
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
  Remove-Item Env:TELEGRAM_BOT_TOKEN -ErrorAction SilentlyContinue
}
```

Install the SDK first:

```powershell
python -m pip install -r requirements.txt
```

The PowerShell example prompts for the Telegram token without echoing it. Set `GEMINI_API_KEY` in `.env` or in the process environment to enable autonomous search. `GEMINI_MODEL` defaults to `gemini-2.5-flash`. Set it to `gemini-3.8-flash` for model-enforced JSON with Google Search in one request; Google currently lists no free-tier API Search grounding for Gemini 3, so check billing before switching. Gemini requests time out after 25 seconds; key, quota, timeout, schema, and network errors have separate user-facing messages. To use SearchAPI instead of Gemini's native Google Search, revoke the previously exposed SearchAPI key, create a replacement, and set `SEARCHAPI_API_KEY` plus `SEARCHAPI_ENABLED=true` in `.env` or Render. Keep it disabled until you are ready to spend SearchAPI credits.

Saba's visible process summary reports checks performed (local catalog, selected web search, official-domain gate). It does not reveal private chain-of-thought.

As of October 2, 2026, Google's pricing page lists Gemini 2.5 Flash text input/output as free on the free tier and Google Search grounding up to 500 requests per day, subject to account quota and availability. One Gemini request can trigger more than one Google Search query, so a paid account could incur grounding charges; keep billing disabled if you want the bot to stop at free quota. Google says free-tier content may be used to improve its products, so do not send personal or sensitive data in search questions. [Gemini API pricing and data-use terms](https://ai.google.dev/gemini-api/docs/pricing).

Example internal `AgentResult` (risk and tool fields are constructed by Saba, not invented by Gemini):

```json
{
  "answer": "The official page describes the application route.",
  "next_step": "Open the verified service portal.",
  "risk_level": "low",
  "risk_reason": "Read-only local lookup and public-source search.",
  "requires_approval": false,
  "tools_used": ["service_catalog", "provider_directory", "gemini_google_search"],
  "sources": [{"title": "Official portal", "url": "https://example.gov.et/service"}],
  "process_summary": "Verified sources: ..."
}
```

## Public service-source snapshots

The scraper stays on configured public sites, checks each site's `robots.txt`, skips account and payment pages, and writes untrusted review snapshots to `data/source_snapshots.json`. It does not submit forms or access pages behind login.

```powershell
python scripts/scrape_public_sources.py
```

Configured starting pages:

- <https://www.eservices.gov.et/en/services>
- <https://www.eservices.gov.et/en/providers>
- <https://services.eaes.et/> (corrected from the duplicated URL in the message)
- <https://www.ebc.et/>

Review every snapshot and source date before adding facts to `data/services.json`.

## Optional form preparation

There is no Playwright MCP server connected to this coding session. For local form preparation, install `requirements-browser.txt` and Chromium, then run `python scripts/prepare_public_form.py <public-form-url>`. It opens only allowlisted public pages, asks before opening, skips identity/passport/password/payment fields, keeps entered values in a temporary browser, and never clicks Submit. The person reviews the open page and decides whether to submit. The official eVisa site is allowlisted, but an applicant must choose the visa category and personally complete sensitive fields and submission.

## Structure

```text
saba/
  __main__.py              executable entry point
  application.py           message routing and conversation behavior
  agent.py                 LangGraph workflow and Gemini grounded search
  audit.py                 Postgres or SQLite action log (metadata only, no message text)
  config.py                environment-backed configuration
  env.py                   local .env loader (shell variables take precedence)
  profile_store.py         consent-gated local language/profile storage
  task_store.py            actor-scoped persistent goal lifecycle storage
  domain.py                typed service, source, and consent models
  knowledge.py             verified local catalog reader
  provider_directory.py    read-only government-provider portal directory
  permissions.py           read-only auto policy and sensitive-action gates
  plugins.py               plugin contract and safe unavailable stubs
  web.py                   FastAPI Telegram webhook and health-check endpoints
  vapi.py                  opt-in Vapi call client, verified-contact loader, and call ledger
  telegram/
    api.py                 Telegram Bot API client and long polling
    transport.py           channel adapter into the application
data/services.json         verified service catalog (empty starter)
data/providers.json        curated provider portal and API-readiness directory
data/voice_contacts.json   explicitly enabled, official-source public office numbers
scripts/scrape_public_sources.py  public-page snapshotter
requirements.txt           LangGraph, Gemini, FastAPI, and ASGI server
```

## Safety boundary

Saba never calls a private number supplied by Gemini, collects identity numbers for calls, charges users, submits forms, or claims that unverified services are available. When outbound calls are globally enabled, Saba may call a manually allowlisted public office without a per-call confirmation; this is an intentional autonomous action. Keep the global flag off until each contact number, assistant prompt, Vapi phone route, calling policy, and cost limit have been reviewed. Payments, authentication, and form submission remain unavailable. Consented profile fields live in Supabase Postgres when configured, otherwise in local SQLite; `/forget` clears them. Keep official sources and their check dates with service facts.

WhatsApp and a future website should be added as separate channel adapters that call the same application layer. They should not duplicate service rules or safety checks.
