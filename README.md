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
Negativity Filter (Claude sentiment analysis)
      ↓
       ├─ AUTONOMOUS → boost fires immediately
       ├─ APPROVAL   → Slack notification → account manager approves
       └─ NOTIFY_ONLY → Slack alert, no spend
      ↓
Meta Ads boost submitted
```

## Features

- **Real-time composite scoring** — weighted engagement score normalized against each location's 90-day baseline
- **Two-stage negativity filter** — reaction ratio check + Claude-powered comment sentiment analysis
- **Human-in-the-loop modes** — per-brand configuration: `AUTONOMOUS`, `APPROVAL`, or `NOTIFY_ONLY`
- **Dynamic lookalike audiences** — built from the post's real organic engagers, not a generic radius
- **Budget controls** — monthly cap enforced per location, no boost fires if cap is exhausted
- **Webhook-first, polling fallback** — event-driven when Rallio supports webhooks; APScheduler polling as safety net

## Architecture

```
autoboost-agent/
├── agent/
│   ├── tools/          # LangChain tools: score, filter, notify, boost
│   ├── engine.py       # Composite score calculation
│   ├── filter.py       # Negativity filter (Claude)
│   └── agent.py        # LangChain agent orchestration
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

## Testing Locally

The agent ships with a Rallio mock simulator. Run it to fire sample engagement events without needing real Rallio credentials:

```bash
python -m integrations.rallio --simulate
```

To test with real webhooks locally, use [ngrok](https://ngrok.com):

```bash
ngrok http 8000
# Point your webhook URL to the ngrok address
```

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
| Slack MCP | Real | Requires `SLACK_BOT_TOKEN` |
| Meta Ads MCP | Stub | Meta Ads MCP announced April 2026 — drop-in ready |
| Claude (Anthropic) | Real | Powers negativity filter sentiment analysis |

## Built With

- [LangChain](https://langchain.com) — agent orchestration
- [Claude (Anthropic)](https://anthropic.com) — sentiment analysis
- [FastAPI](https://fastapi.tiangolo.com) — webhook server
- [APScheduler](https://apscheduler.readthedocs.io) — polling scheduler
- [Slack SDK](https://slack.dev/python-slack-sdk/) — approval notifications
- [uv](https://docs.astral.sh/uv/) — package management

---

Built by [Soham Mehrotra](https://github.com/MehrotraSoham) · Ignite Visibility × Rallio
