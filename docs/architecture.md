# AutoBoost Agent — Architecture

System architecture of the AutoBoost agent: the AI agent, its tools, and the
external systems it integrates with.

```mermaid
flowchart LR
    classDef live fill:#d4f7d4,stroke:#2e7d32,color:#1b1b1b;
    classDef stub fill:#fff3cd,stroke:#b8860b,color:#1b1b1b;
    classDef external fill:#e3e3e3,stroke:#666666,color:#1b1b1b;
    classDef core fill:#dbe9ff,stroke:#1c5dbf,color:#1b1b1b;

    Rallio["Rallio Platform<br/>post + engagement data"]:::external

    subgraph Entry["FastAPI + Uvicorn"]
        WebhookEP["/webhook/engagement<br/>/webhook/slack"]:::core
        Sched["APScheduler<br/>5-min poll fallback"]:::core
    end

    subgraph AgentCore["AutoBoost Agent — LangGraph ReAct"]
        LLM["LLM backbone<br/>Gemini 2.5 Flash (default)<br/>or Claude Haiku 4.5"]:::live
        SysPrompt["System prompt:<br/>Score → Filter → Route → Act"]:::core
    end

    subgraph ToolLayer["Agent Tools (LangChain @tool)"]
        T1["score_post<br/>composite engagement score"]:::live
        T2["run_negativity_filter<br/>reaction ratio + LLM sentiment"]:::live
        T3["send_slack_notification<br/>APPROVAL / NOTIFY_ONLY"]:::live
        T4["submit_meta_boost<br/>lookalike audience + campaign"]:::stub
    end

    subgraph Storage["Config & Data"]
        BrandCfg["Brand Config Registry<br/>boost_mode, thresholds, budgets"]:::core
        DataReg["Post / Baseline Registry<br/>(in-memory today — DB in prod)"]:::core
    end

    Slack["Slack<br/>Account Manager workspace"]:::live
    MetaAds["Meta Ads<br/>Campaign Manager"]:::stub
    LangSmithSvc["LangSmith<br/>tracing & observability"]:::live

    Rallio -- "engagement webhook" --> WebhookEP
    Sched -. "fallback poll" .-> Rallio
    WebhookEP --> AgentCore
    AgentCore -- "tool calls" --> ToolLayer
    T1 --> DataReg
    T2 --> LLM
    T4 --> DataReg
    ToolLayer --> BrandCfg
    T3 <--> Slack
    T4 --> MetaAds
    Slack -- "Approve / Suppress click" --> WebhookEP
    AgentCore -. "full trace per run" .-> LangSmithSvc
```

**Legend:** 🟩 live & working today · 🟦 core orchestration/config · 🟨 stubbed (mock data, ready to swap for real API) · ⬜ external system

## Tech stack

| Layer | Technology | Status |
|---|---|---|
| Agent orchestration | LangGraph (`create_react_agent`) + LangChain | Live |
| LLM backbone | Gemini 2.5 Flash (default, free tier) / Claude Haiku 4.5 | Live, swappable via `.env` |
| Web server | FastAPI + Uvicorn | Live |
| Scheduling | APScheduler (5-min polling fallback) | Live |
| Config & validation | Pydantic / pydantic-settings | Live |
| Observability | LangSmith (per-run traces of every LLM call & tool call) | Live |
| Notifications & approvals | Slack SDK (real bot token + channel) | Live |
| Ad platform | Meta Ads | Stubbed — mock campaign IDs, drop-in ready for Meta Ads MCP |
| Source platform | Rallio | Mocked client + sample data — drop-in ready for Rallio webhooks/API |
| Package management | uv | Live |

## Agent & tools

The system runs a **single LangGraph ReAct agent** ("AutoBoost") per post event. Given a `post_id` and `brand_id`, its system prompt drives a fixed decision sequence using four tools:

1. **`score_post`** — computes a composite engagement score (comments 30% · shares 25% · saves 20% · reach velocity 15% · likes 10%) against the location's 90-day baseline. If below the brand's threshold, the agent stops here.
2. **`run_negativity_filter`** — two-stage gate: a reaction-ratio check (angry/sad reactions > 20%) and an LLM-based sentiment check on comments (negative > 30%). If either fails, the agent stops and logs a suppression reason.
3. **`send_slack_notification`** — routes by the brand's `boost_mode`:
   - `APPROVAL` sends an interactive Slack card and awaits an Approve/Suppress click (with a configurable timeout).
   - `NOTIFY_ONLY` sends a fire-and-forget performance alert.
4. **`submit_meta_boost`** — builds a dynamic lookalike audience from the post's organic engagers and submits a paid boost campaign with the brand's configured budget.

Every brand is independently configured (`config/brand_config.py`) for `boost_mode`, `score_threshold`, `monthly_budget_cap`, `default_boost_budget`, and `approval_timeout_mins` — so different franchise brands can run fully autonomous, human-in-the-loop, or alert-only.
