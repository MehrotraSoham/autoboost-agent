# AutoBoost Agent

An AI agent that monitors franchise social media posts in real time and automatically boosts high-performing content.

## The Problem

Franchise locations post content daily, but no system watches for breakout posts in real time. When a post goes viral, the engagement signal sits idle until an account manager checks — once or twice a week. By then, the organic momentum is gone. The result: a 3–5 day gap between peak engagement and a live boosted ad.

## How It Works

```
Rallio post event
      ↓
Composite Engagement Score
(comments 30% · shares 25% · saves 20% · reach velocity 15% · likes 10%)
      ↓
Negativity Filter (reaction ratio + LLM sentiment analysis)
      ↓
       ├─ AUTONOMOUS → boost fires immediately
       ├─ APPROVAL   → Slack notification → account manager approves
       └─ NOTIFY_ONLY → Slack alert, no spend
      ↓
Meta Ads boost submitted
```

## Features

- **Real-time composite scoring** — weighted engagement score normalized against each location's 90-day baseline
- **Two-stage negativity filter** — reaction ratio check + LLM-powered comment sentiment analysis
- **Human-in-the-loop modes** — per-brand configuration: `AUTONOMOUS`, `APPROVAL`, or `NOTIFY_ONLY`
- **Dynamic lookalike audiences** — built from the post's real organic engagers, not a generic radius
- **Budget controls** — monthly cap enforced per location, no boost fires if cap is exhausted
- **Webhook-driven** — `/webhook/engagement` triggers the pipeline per post (polling fallback planned, not yet implemented)

## Architecture

```
autoboost-agent/
├── agent/
│   ├── tools/          # LangChain tools: score, filter, notify, boost
│   ├── engine.py       # Composite score calculation
│   ├── filter.py       # Negativity filter (reaction ratio + LLM sentiment)
│   └── agent.py        # LangGraph ReAct agent orchestration
├── integrations/
│   ├── rallio.py       # Rallio client (mock + real interface)
│   ├── slack.py        # Slack MCP wrapper
│   └── meta.py         # Meta Ads stub (swap for Meta Ads MCP)
├── config/
│   └── brand_config.py # Per-brand configuration model
├── data/
│   └── sample_posts.json  # Demo fixtures
├── server/
│   └── webhook.py      # FastAPI webhook server
├── docs/
│   ├── architecture.md            # System architecture diagram + tech stack
│   └── rallio-integration-flow.md # End-to-end decision flow diagram
└── main.py             # Entry point
```

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/MehrotraSoham/autoboost-agent.git
cd autoboost-agent

# 2. Install dependencies (uv creates the virtualenv automatically)
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run the agent
uv run python main.py
```

This starts the FastAPI server on `http://localhost:8000`, loads the sample
posts/baselines into the in-memory registry, and waits for events on
`/webhook/engagement` and `/webhook/slack`. See "Testing Locally" below to
actually fire the pipeline.

## Testing Locally

The agent ships with sample post data (`data/sample_posts.json`) covering
all three boost modes plus edge cases (below threshold, negative sentiment).

**Option A — run the pipeline directly** (no server needed):

```bash
# Single post
uv run python test_pipeline.py post-viral-001

# Full suite (processes posts sequentially with a short delay between them)
uv run python test_pipeline.py
```

> **Note:** the default `gemini-2.5-flash` free tier is limited to ~5
> requests/minute **and 20 requests/day**, while each post can take 3-4 LLM
> calls. If you hit a `429 RESOURCE_EXHAUSTED` error, check whether it's the
> per-minute limit (wait ~1 min and retry) or the per-day limit (wait until
> the next day, or switch to `LLM_PROVIDER=anthropic` with a paid key). Test
> one post at a time to conserve quota.

**Option B — via the webhook server.** With `uv run python main.py` running,
in another terminal:

```bash
curl -X POST http://localhost:8000/webhook/engagement \
  -H "Content-Type: application/json" \
  -d '{"post_id":"post-viral-001","location_id":"loc-001","brand_id":"demo-brand"}'
```

### Testing the Slack approval flow

For `APPROVAL`-mode brands (e.g. `demo-brand`), the agent sends a Slack
message with Approve/Suppress buttons and waits for a response. With the
server running and a post in-flight, simulate a button click — no public
endpoint required:

```bash
curl -X POST http://localhost:8000/webhook/slack \
  --data-urlencode 'payload={"actions":[{"action_id":"approve_boost","value":"post-viral-001"}]}'
```

Use `"action_id":"suppress_boost"` to simulate rejecting the boost instead.

### Real Slack button clicks (ngrok)

To have the actual Approve/Suppress buttons in Slack call back to your local
server, use [ngrok](https://ngrok.com):

```bash
# One-time setup: sign up at ngrok.com, then add your authtoken
ngrok config add-authtoken <your-authtoken>

ngrok http 8000
```

Then in your Slack app settings (api.slack.com/apps), enable **Interactivity
& Shortcuts** and set the Request URL to `<ngrok-url>/webhook/slack`.

## Configuration

Each franchise brand is configured independently in `config/brand_config.py`:

| Field | Description | Default |
|-------|-------------|---------|
| `boost_mode` | `AUTONOMOUS`, `APPROVAL`, or `NOTIFY_ONLY` | `APPROVAL` |
| `score_threshold` | Multiplier over location baseline to trigger | `1.5` |
| `monthly_budget_cap` | Max USD spend per location per month | `500` |
| `default_boost_budget` | Per-post boost budget in USD | `50` |
| `approval_timeout_mins` | Slack approval window before suppression | `60` |

## Integrations

| Integration | Status | Notes |
|-------------|--------|-------|
| Rallio | Mock | Swap `integrations/rallio.py` for real client when webhooks are confirmed |
| Slack | Real | Requires `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` |
| Meta Ads MCP | Stub | Meta Ads MCP announced April 2026 — drop-in ready |
| LLM (negativity filter + agent reasoning) | Real | Gemini 2.5 Flash by default (free tier); set `LLM_PROVIDER=anthropic` for Claude Haiku |

## Built With

- [LangChain](https://langchain.com) + [LangGraph](https://langchain-ai.github.io/langgraph/) — agent orchestration (ReAct agent)
- [Google Gemini](https://ai.google.dev) / [Claude (Anthropic)](https://anthropic.com) — LLM backbone, switchable via `.env`
- [FastAPI](https://fastapi.tiangolo.com) — webhook server
- [Slack SDK](https://slack.dev/python-slack-sdk/) — approval notifications
- [LangSmith](https://smith.langchain.com) — agent tracing and observability
- [uv](https://docs.astral.sh/uv/) — package management

---

Built by [Soham Mehrotra](https://github.com/MehrotraSoham) · Ignite Visibility × Rallio
