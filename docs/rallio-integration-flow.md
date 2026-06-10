# AutoBoost in Rallio — End-to-End Flow

How AutoBoost would sit inside the Rallio product experience: a post's
engagement is monitored in real time, scored, sentiment-checked, and routed
to the action appropriate for that brand — with Rallio as both the trigger
and the place results surface back to.

```mermaid
flowchart TD
    classDef rallio fill:#e8d5ff,stroke:#6a1b9a,color:#1b1b1b;
    classDef agent fill:#dbe9ff,stroke:#1c5dbf,color:#1b1b1b;
    classDef human fill:#fff3cd,stroke:#b8860b,color:#1b1b1b;
    classDef terminal fill:#d4f7d4,stroke:#2e7d32,color:#1b1b1b;
    classDef suppress fill:#fde0e0,stroke:#c62828,color:#1b1b1b;

    A["Rallio: post published,<br/>engagement tracked in real time"]:::rallio
    B{"Engagement spike<br/>detected on a post"}:::rallio
    C["AutoBoost: score_post —<br/>composite score vs<br/>90-day location baseline"]:::agent
    D{"Composite score ≥<br/>brand threshold?"}:::agent
    E["No action —<br/>resume monitoring"]:::terminal
    F["AutoBoost: run_negativity_filter —<br/>reaction ratio + LLM sentiment"]:::agent
    G{"Passes negativity<br/>gate?"}:::agent
    H["Suppress boost,<br/>log reason"]:::suppress
    I{"Brand's boost_mode<br/>(per-brand config)"}:::agent
    J["submit_meta_boost:<br/>build lookalike audience,<br/>submit campaign"]:::agent
    K["Slack: Approval card sent<br/>to Account Manager"]:::human
    L["Slack: Performance alert<br/>(no spend)"]:::human
    M{"AM responds within<br/>approval window?"}:::human
    N["Meta Ads: campaign live,<br/>budget capped per brand"]:::terminal
    O["Rallio dashboard: boosted-post<br/>badge + campaign link"]:::rallio
    P["AM can still boost<br/>manually from Rallio"]:::rallio

    A --> B -- "webhook event" --> C
    C --> D
    D -- "No" --> E
    D -- "Yes" --> F
    F --> G
    G -- "No, too negative" --> H
    G -- "Yes" --> I
    I -- "AUTONOMOUS" --> J
    I -- "APPROVAL" --> K
    I -- "NOTIFY_ONLY" --> L
    K --> M
    M -- "Approve" --> J
    M -- "Suppress / timeout" --> H
    J --> N --> O
    L --> P
```

**Legend:** 🟪 Rallio touchpoint (today or proposed) · 🟦 AutoBoost agent step · 🟨 Account Manager / Slack · 🟩 successful outcome · 🟥 suppressed outcome

## Why this matters for Rallio

- **Closes the 3–5 day gap** between a post going viral and an ad actually running — AutoBoost reacts within minutes of an engagement spike.
- **Per-brand control, not all-or-nothing**: a brand can run fully `AUTONOMOUS`, require human `APPROVAL` via Slack, or just get `NOTIFY_ONLY` alerts — Rallio decides the trust level per franchise.
- **Built-in guardrails**: nothing spends money until it passes both an engagement threshold *and* a negativity filter, and every brand has a hard monthly budget cap.
- **Rallio stays the system of record**: the proposed loop-back (🟪 boxes) shows boosted posts and campaign links surfaced directly in the Rallio dashboard, and account managers retain the ability to boost manually at any time.

## Today vs. proposed

| Step | Status |
|---|---|
| Engagement webhook trigger | Mocked (`integrations/rallio.py`) — ready for real Rallio webhook |
| Scoring, negativity filter, mode routing | **Working today**, demoed live |
| Slack notification (`NOTIFY_ONLY`) | **Working today** with real Slack workspace |
| Slack approval (`APPROVAL`) | Working today via simulated webhook callback; needs public endpoint (e.g. ngrok) for live Slack button clicks |
| Meta Ads boost submission | Stubbed with realistic mock IDs — ready for Meta Ads MCP |
| Rallio dashboard loop-back | Proposed — not yet built |
