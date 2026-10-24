# Deploy Saba ET as a Render Web Service

Saba uses Telegram's HTTPS webhook on Render, so it does not run long polling there. Render supplies the public HTTPS address; the service registers that address with Telegram when it starts.

## Cost and storage

The Blueprint selects Render's paid `0.5c-512mb` Web Service plan. Saba stores profiles and its durable webhook inbox in Supabase Postgres, so the Render service does not need a persistent disk. See [Render pricing](https://render.com/pricing).

Render Free Web Services can be used for a temporary demo, but they sleep after 15 minutes without inbound traffic and can take about a minute to wake. The webhook will wake the service, so replies can be delayed. See [Render free-instance limits](https://render.com/docs/free).

## Deploy from the repository

1. Push `main` to GitHub.
2. In Render, choose **New → Blueprint** and connect `mikilezen/saba` on `main`.
3. Apply `render.yaml`. Render creates a Web Service named `saba-et-web`.
4. Enter freshly rotated values for `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, and `GEMINI_API_KEY` when prompted. Keep all keys private. Add the Vapi variables below when ready; leave auto-calling false until a real outbound number and office contact have been checked.
5. Wait for the deploy. Check the logs for `Saba Telegram webhook configured` and confirm the health check passes at `/healthz`.
6. If you already deployed the old polling worker, stop it before enabling this service. Telegram allows only one update receiver (polling or webhook) at a time. Then send `/start` to the Telegram bot.

Generate a webhook secret on your computer with PowerShell:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Paste the generated value into Render's `TELEGRAM_WEBHOOK_SECRET` setting. It uses Telegram's supported characters and is not the bot token. Render provides `RENDER_EXTERNAL_URL`; the app registers `https://<service>/telegram/webhook` automatically. The webhook endpoint checks Telegram's `X-Telegram-Bot-Api-Secret-Token` header before queuing an update.

## Commands

Render Blueprint commands:

```text
Build:  pip install -r requirements.txt
Start:  uvicorn saba_et.web:app --host 0.0.0.0 --port $PORT
Health: /healthz
```

Local development still uses long polling:

```powershell
python -m pip install -r requirements.txt
python -m saba_et
```

The local command deletes a webhook before starting polling, because Telegram does not allow polling and webhooks to receive updates at the same time. Starting the bot locally while the Render service is online will therefore disconnect Render's webhook; restart the Render service to register it again.

## Environment values

- `TELEGRAM_BOT_TOKEN` — required BotFather token
- `TELEGRAM_WEBHOOK_SECRET` — required secret header value for the webhook
- `SUPABASE_DB_URL` — required server-only Postgres connection string; apply the [Supabase migration](SUPABASE.md) first
- `GEMINI_API_KEY` — optional; autonomous AI search is disabled if it is empty
- `GEMINI_MODEL=gemini-2.5-flash` — lower-cost default
- `SEARCHAPI_ENABLED=false` — optional SearchAPI Google search switch; keep false to avoid SearchAPI credit use
- `SEARCHAPI_API_KEY` — optional SearchAPI key; only used when SearchAPI is enabled
- `SEARCHAPI_ENGINE=google` — Google web results for SearchAPI
- `RENDER_EXTERNAL_URL` and `PORT` — supplied by Render
- `VAPI_AUTO_CALL_ENABLED=false` — leave false until call routing is configured and reviewed
- `VAPI_API_KEY`, `VAPI_ASSISTANT_ID`, `VAPI_PHONE_NUMBER_ID` — Vapi credentials and imported outbound-capable number ID
- `VAPI_WEBHOOK_SECRET` — shared secret for Vapi's result callback
- `VAPI_MAX_CALLS_PER_DAY=3` — daily cap (config clamps the value between 1 and 20)
- `TELNYX_API_KEY` — Telnyx API key used to answer incoming calls and issue call-control commands
- `TELNYX_PUBLIC_KEY` — base64 public key from Mission Control Portal → Account Settings → Keys & Credentials → Public Key; used to verify signed webhooks

For local use, put values in the ignored project-root `.env` file (`Copy-Item .env.example .env`) and run Saba. On Render, enter those values in **Dashboard → your service → Environment**. Do not commit `.env` or paste keys into chat. The Vapi callback settings are in the Vapi Assistant's Server URL: set `https://<render-service-host>/vapi/webhook`, add custom header `X-Saba-Vapi-Secret` with the same secret, and enable the `end-of-call-report` server message. Saba verifies that header and sends only Vapi's short analysis summary to the Telegram chat that initiated the call. It does not retain the transcript or recording.

For a Telnyx Voice API application, set its webhook URL to `https://<render-service-host>/telnyx/webhook` and configure the two Telnyx environment values above. Saba verifies the Ed25519 signature, answers incoming calls, plays a short English setup notice, and hangs up. This endpoint confirms the Telnyx call-control path; it does not yet provide a live conversational voice agent.

To use SearchAPI for Google results, first revoke the key previously pasted in chat, create a replacement, then set `SEARCHAPI_API_KEY` and `SEARCHAPI_ENABLED=true` in Render's Environment panel and redeploy. This makes one external SearchAPI request for each research question and can consume account credits. Keep it false to use Gemini's native Google Search grounding. Gemini still writes the structured answer and Saba filters sources to approved official domains.

To require Gemini schema-enforced JSON alongside Google Search, set `GEMINI_MODEL=gemini-3.8-flash`; check Gemini billing first. The default model validates Saba's app result, but does not enforce the model's raw output schema.

## Troubleshooting

- **Service exits during startup:** confirm the BotFather token and webhook secret are present and correctly formatted; inspect Render logs for a sanitized error category.
- **Health check fails:** verify the service is using the Blueprint start command and binds to `0.0.0.0:$PORT`.
- **Telegram bot does not reply:** check the Render deploy logs for `Saba Telegram webhook configured`; confirm the Render service is running and the secret was entered exactly. The webhook route never logs message bodies or secrets.
- **AI search reports an error:** check `GEMINI_API_KEY`, model access, quota, and the sanitized error category in Render logs.
- **Database connection fails:** check `SUPABASE_DB_URL`, network access, and that the versioned migration has been applied in Supabase.

## Vapi and Ethiopia outbound calls

Vapi's outbound endpoint is wired into Saba's LangGraph flow. Gemini can request a call after grounded search fails to verify an answer, but Saba only dials an enabled contact from `data/voice_contacts.json`. Add a number only after manually checking the official HTTPS source page. Add descriptive `search_terms` so the agent can match the right office/service. Empty starter file means no calls can be placed.

In Vapi, the dashboard's free US number cannot make outbound calls or international calls. Import an outbound-capable number or connect an outbound SIP trunk, then confirm the account/provider permits calls to Ethiopia and the exact destination number type. Vapi's official outbound docs require an imported provider number and `assistantId`, `phoneNumberId`, and customer destination. [Vapi outbound calls](https://docs.vapi.ai/calls/outbound-calling), [Vapi phone-number limitations](https://docs.vapi.ai/phone-calling).

Twilio currently lists Ethiopia calling at **$0.4990/minute local** and **$0.4903/minute mobile** for Programmable Voice; its SIP termination table lists **$0.4950/minute local** and **$0.4863/minute mobile**. These are carrier rates only; Vapi, assistant/model, speech, number, taxes, and routing may add cost. Verify your Vapi provider setup and destination rate before enabling calls. [Twilio Voice rates for Ethiopia](https://www.twilio.com/en-us/voice/pricing/et), [Twilio SIP trunk rates for Ethiopia](https://www.twilio.com/en-us/sip-trunking/pricing/et). Ethio Telecom public domestic bundles are not proof that an AI-compatible outbound SIP/API product is available; I did not find official, current public documentation confirming such access.

Before changing `VAPI_AUTO_CALL_ENABLED` to `true`, configure the assistant prompt in [VAPI_AGENT_PROMPT.md](VAPI_AGENT_PROMPT.md), add Vapi secrets to Render's Environment panel, configure the webhook, add a source-verified public office contact, and confirm your calling consent/policy requirements. Auto-calls are limited by the configured daily cap; there is no per-call approval prompt once globally enabled. High-risk requests are blocked. Saba doesn't request or store recordings; configure Vapi transcription/recording and an Amharic-capable transcriber/voice deliberately. If the dashboard still says English, switch that before Amharic calls.
