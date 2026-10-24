# Amharic phone-agent options for Ethiopia

## Recommended prototype

Use **Gemini 3.8 Live** for Amharic speech-to-speech and a PSTN/SIP provider for the telephone leg. Google lists Amharic among Live API languages and recommends Gemini 3.8 Live for low-latency voice agents. The current API pricing page lists a free tier (where submitted data may be used to improve Google products) and paid audio rates of about **$0.005/min input + $0.018/min output**. Live API costs depend on turn/context usage, so treat that as a starting estimate rather than a fixed per-call bill. Do not send passwords, Fayda numbers, or payment information through the agent.

For a quick PSTN pilot, Twilio's published Ethiopia rates are about **$0.499/min to local numbers** and **$0.4903/min to mobile numbers**, plus **$0.0044/min for Media Streams**. A five-minute mobile call is roughly **$2.45 telephony + $0.022 Media Streams**, or **$2.47 before Gemini audio usage, taxes, and any number charges**. Telephony is the main expense; a GPU will not reduce it.

The initial design suggested this approval flow. The current Saba prototype instead supports a global opt-in for autonomous, allowlisted public-office calls; don't enable it until you accept that behavior and have reviewed costs. It does not use Gemini Live directly. The Vapi adapter sends one approved question to its configured assistant and uses a result webhook.

The current data path is:

```text
Telegram user asks a public-service question
  -> LangGraph runs Gemini grounded search and official-source checks
  -> Gemini may request one public-office call if its search cannot answer
  -> Saba verifies the contact is in the source-backed allowlist and enforces a daily cap
  -> Vapi dials the allowlisted +251 number only if global auto-call is enabled
  -> authenticated Vapi callback sends the summary to the originating Telegram chat
```

Gemini does not select phone numbers or override the deterministic risk gate, contact allowlist, or global Vapi opt-in. Because enabling the feature permits autonomous calls without an individual prompt, set a low daily cap, use an approved public contact, check applicable consent/calling policies, and disclose the bot is an AI agent. Recipients can decline; the Vapi prompt directs the assistant to stop when asked.

## Vapi versus direct Gemini Live

Vapi may be a convenient call orchestration layer, but its free number is US-only and cannot place outbound calls. Ethiopia calls need an imported PSTN number/provider or a SIP trunk. Its usage-only plan currently includes $5 trial credit, then charges a $0.05/min platform fee plus model, voice, transcription, and telephony costs. The sample endpoint should be `/call` (not `/call/phone`), and Vapi's function tools use a server webhook configuration rather than a nested `server` property in the function schema.

Vapi lists Amharic for ElevenLabs speech-to-text. However, Amharic is not listed in Vapi's published ElevenLabs text-to-speech language matrix. I cannot confirm the pasted `amharic_voice_id` works. Test the *spoken output* before relying on that voice stack. Gemini Live's native Amharic support is the better documented Amharic prototype path.

## Lowest-cost route to ask about

Ask Ethio Telecom Enterprise whether they can provision an authorized outbound SIP trunk that can connect to an AI voice service, and request the per-minute off-net/mobile tariff, setup fees, and technical integration details in writing. Ethio Telecom publishes Hosted IP Telephony from 200 ETB per extension per month (minimum five extensions for standard/advanced packages), with prevailing voice tariffs; that page does not promise an API-compatible SIP trunk or publish the voice tariff. Treat local SIM gateways or unusually low per-minute estimates as unverified until Ethio Telecom confirms terms and permits the use.

## What is and is not active in Saba

Saba's Vapi call client and authenticated result webhook are wired into the LangGraph agent. No call can actually start until you supply Vapi credentials, an outbound-capable imported phone route that can reach +251, and manually verified contacts in `data/voice_contacts.json`; global calls remain off by default. Test Amharic spoken output with the selected Vapi transcriber and voice. The public prices and provider requirements were checked on October 2, 2026; rates and capabilities can change.

> Keep this guidance aligned with the current implementation.
