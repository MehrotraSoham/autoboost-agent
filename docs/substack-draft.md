# Building AutoBoost: An AI Agent That Boosts Viral Posts Before the Moment Passes

*How I picked a problem at a marketing agency that works with franchise brands, scoped it down to something an AI agent could actually own, and built a working prototype in a weekend.*

---

## The problem: every franchise's best post dies of old age

Here's a workflow that plays out, every single day, across thousands of franchise locations:

A local plumber, dentist, or QSR franchise posts something on Instagram. It's nothing special — maybe a behind-the-scenes clip, a seasonal promo, a customer shoutout. But this time it catches. Comments roll in, people share it, saves spike. By any normal measure, it's a breakout post.

And then... nothing happens for three to five days.

The engagement signal just sits there in the social dashboard until an account manager happens to check — which, realistically, is once or twice a week. When they finally notice, they switch over to Meta Ads Manager, manually recreate the organic post as a paid ad, set a budget, and submit it for review. Meta can take up to 24 hours to approve it. By the time the boosted ad goes live, the organic momentum that made the post worth boosting in the first place is gone.

This matters more than it sounds like it should, because **timing is not a minor factor in paid amplification — it's close to the whole game**:

- Posts that accumulate engagement in their first hour are up to **4x more likely** to get algorithmic amplification than posts that take 12 hours to hit the same numbers (across 500+ campaigns analyzed).
- A Hootsuite experiment found that an early engagement push got posts in front of **~3x more people** than identical posts without one.
- Industry practitioners recommend boosting **2–6 hours** after posting to ride the algorithm's momentum — not 3–5 days later, once it's flat.

So across hundreds of franchise locations posting daily, high-performing content is quietly dying — not because the content was bad, but because nobody was watching the clock.

## The agency behind this project

I'm building this for a marketing agency that focuses on franchise and multi-location brands — the kind of company that runs paid media, social, content, and reputation management for hundreds of locations across dozens of brands. Like a lot of agencies, it's also expanding into platform/SaaS revenue: it operates a social media and reputation management platform built specifically for franchises, plus a performance-based lead-gen platform for home services and healthcare.

The agency sits in the middle of the market — bigger than boutique shops, smaller than holding-company giants — and it's betting that owning strategy, execution, technology, and lead generation under one contract is more defensible than being a pure SaaS platform (which still leaves a franchise client needing to hire an agency on top).

But there's real pressure behind that bet. The agency world is getting squeezed by AI in ways that show up in the numbers:

- **61%** organic CTR crash and **68%** paid CTR crash for queries that now show AI Overviews.
- **Zero-click searches** are up to **69%**, from 56% just twelve months earlier.
- **60%** of US senior marketing leaders say they spent less on agencies in 2025 *because of AI*, and **31%** of agencies are planning further headcount cuts in 2026.
- Like many agencies carrying acquisition debt, margin protection isn't just nice to have — it's a financial imperative.

Meanwhile, the most direct SaaS competitor in this space, **SOCi**, has already shipped "Genius Agents" — roughly 150,000 AI agents reportedly completing 10 million local marketing tasks. The agency's own platform doesn't have an equivalent yet. The internal brief I was working from put it bluntly: *the window to close that gap is open now, not later.*

## Why AutoBoost, specifically

The brief I read laid out two candidate AI products, scored with a RICE framework (Reach × Impact × Confidence ÷ Effort):

| Dimension | **Auto Boost** | Auto Remarketing |
|---|---|---|
| Reach | 4,000+ locations | 500-location pilot franchise |
| Impact | 2x — engagement & retention lift | 3x — direct revenue recovery / cost efficiency |
| Confidence | **80%** — Meta Ads API + the platform's data pipes already exist; trigger logic is straightforward | 65% — depends on CRM data access (ServiceTitan, HubSpot, etc.) |
| Effort | 8 person-weeks | 12 person-weeks |
| **RICE score** | **800 — Ship First** | 81 — Pilot in Parallel |

Auto Remarketing — an agent that detects customers who haven't returned within their expected repurchase window and automatically prepares a win-back ad for one-click approval — is genuinely the bigger long-term play. It's the kind of CRM-integration moat ("no client can easily walk away from a system that holds years of their customer history") that turns an agency into infrastructure.

But it depends on CRM integrations the agency doesn't have yet. **AutoBoost depends on data the platform and Meta already have.** That gap in confidence, combined with AutoBoost's much larger reach (every posting location vs. a 500-location pilot) and lower effort, made it the obvious place to start. It's the proof of concept that's actually *buildable* right now — not a six-month integration project.

There's also a sharper competitive argument. I went through the AI features of every adjacent player — SOCi, Birdeye, Yext, Hootsuite, Sprout Social, Vendasta — and mapped what each one can and can't do:

| Capability | This agency | SOCi | Birdeye | Yext | Hootsuite | Sprout |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| AI content generation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI review responses | ✅ | ✅ | ✅ | ✅ | partial | ❌ |
| AI assistant / chat | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Autonomous AI agents | ❌ | ✅ | ✅ | ✅ | ❌ | partial |
| **Performance-triggered amplification** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Cross-platform lifecycle loop** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

That last row is the interesting one. **Nobody** — not SOCi with its 150K agents, not Birdeye, not Hootsuite's OwlyGPT — has a system that watches organic performance in real time and *autonomously* converts a winning post into a paid campaign. SOCi's Genius Social Agent creates and publishes localized content, but it doesn't tie paid budget to real-time organic performance. AutoBoost would close that gap first, and it's the kind of capability that's only possible because this agency already sits on both the social platform *and* downstream customer data from its lead-gen platform.

## The solution — and what I actually built

The full vision from the product brief is a real product: composite engagement scoring across every post the platform manages, a two-stage negativity filter, dynamic Meta lookalike audiences built from a post's actual engagers (not a generic 5-mile radius — research shows lookalike seeding from real engagers gets up to 70% higher conversion vs. broad targeting), one-tap Slack approval, and a budget-capped autonomous boost pipeline. It's spec'd as an 8-person-week proof of concept with a clear trigger decision tree, suppression rules for every edge case, and configuration knobs per brand and per location.

I built a working slice of that as a single AI agent — here's the architecture:

```
Social post event
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

### Tech stack

- **LangGraph + LangChain** — a single ReAct agent ("AutoBoost") that owns the full decision sequence: score → filter → route → act, via four tools (`score_post`, `run_negativity_filter`, `send_slack_notification`, `submit_meta_boost`).
- **Gemini 2.5 Flash** as the default LLM (free tier), with Claude Haiku 4.5 as a drop-in swap via `.env`.
- **FastAPI + Uvicorn** for the webhook server (`/webhook/engagement`, `/webhook/slack`).
- **Slack SDK** — real bot token, real channel, both `NOTIFY_ONLY` alerts and interactive `APPROVAL` cards with Approve/Suppress buttons.
- **LangSmith** for full per-run tracing of every LLM call and tool call.
- **Pydantic** for per-brand configuration (`boost_mode`, `score_threshold`, `monthly_budget_cap`, `default_boost_budget`, `approval_timeout_mins`).
- **uv** for package management.

The composite score, negativity filter logic, and per-brand routing all run exactly per the spec. The platform's engagement webhook and Meta's boost submission are mocked — but with realistic interfaces designed as drop-in replacements once the real webhook and Meta's Ads MCP are confirmed.

### What actually worked (and what surprised me)

A few things I didn't expect going in:

1. **The agent loop is fragile to model choice.** I started with `gemini-2.5-flash-lite` and the agent would silently stop mid-sequence — it'd call `score_post`, get a result back, and then return an empty message instead of calling the negativity filter next. No error, just... done. Switching to `gemini-2.5-flash` fixed it completely. Lesson: for multi-step tool-calling agents, "lite" model tiers can quietly break your control flow in ways that look like logic bugs but aren't.

2. **LLM quotas are a real constraint on agent development**, not just production. Gemini's free tier caps `gemini-2.5-flash` at ~5 requests/minute *and* 20 requests/day — and each `process_post()` run burns 3-4 LLM calls. I burned through a day's quota just running tests one at a time. If you're prototyping an agent that makes several LLM calls per task, budget your quota like it's a scarce resource, because it is.

3. **The Slack approval loop worked end-to-end without needing a public endpoint.** Real Slack apps need a public URL (via ngrok) for button clicks to call back to your server. For a demo, I skipped that entirely by simulating Slack's callback with a single curl command hitting `/webhook/slack` directly — which exercises the *exact same* `resolve_approval` code path a real button click would. That simplification also surfaced a real bug: `python-multipart` wasn't installed, so the webhook couldn't parse Slack's form-encoded payload *at all* — a bug that would have silently broken real button clicks too, not just my test.

### Tradeoffs, on purpose

- **One agent, not a multi-agent system.** The decision sequence (score → filter → route → act) is linear and well-specified, so a single ReAct agent with four tools is simpler to reason about, trace, and debug than splitting it into a "scorer agent" + "filter agent" + "router agent." I'd revisit this if the negativity filter or audience-building logic grew complex enough to need its own retry/escalation behavior.
- **Mocked platform and Meta integrations, real Slack.** The riskiest, most novel part of this system — the human-in-the-loop approval UX — is the part I made real. The parts that are well-understood API integrations (the social platform's webhooks, Meta Ads API) are mocked with realistic interfaces, because the goal of the proof of concept is to validate the *decision logic and human trust model*, not to re-prove that REST APIs work.
- **In-memory registries, not a database.** Posts, baselines, and brand configs live in memory for the prototype. Fine for a demo against five sample posts; the first thing to change for anything beyond a single-brand pilot.
- **Biased toward suppression.** Per the trigger spec, every ambiguous case — a sentiment-analysis timeout, a Slack delivery failure, an audience-build API error — routes to a human review queue rather than either auto-approving or silently dropping the post. It's "always safer to miss a boost than to amplify negative content," and that bias is baked into the control flow, not bolted on as an afterthought.

## Measuring success

A prototype proves the loop *can* run. It doesn't prove the loop is *worth running*. If this went from prototype to pilot, here's how I'd know it was working — split into what we'd see in the first 30 days (is the system behaving as designed) and what we'd see in 90 days (is it actually moving the business).

**Leading indicators (30 days) — is the system doing what it's supposed to?**

| Metric | Target |
|---|---|
| Time from post peak to live boosted ad | < 30 minutes |
| Triggered posts correctly passing the negativity filter | > 95% |
| Account manager Slack approval rate | > 70% |
| Avg. time to approve in Slack | < 15 minutes |

**Lagging indicators (90 days) — is it moving the business?**

| Metric | Target |
|---|---|
| Boosted-post engagement rate vs. manual baseline | 2x improvement |
| Cost-per-engagement vs. manual boosts | 30% reduction |
| Account manager time saved per week, per brand | > 3 hours |
| Client retention on AutoBoost brands vs. control | Measurable positive delta |

The leading indicators matter most early on — they're the difference between "the agent works" and "the agent works *and people trust it enough to act on it*." A pipeline that correctly scores and filters posts but gets ignored or rejected 90% of the time in Slack hasn't actually closed the 3-5 day gap; it's just moved the bottleneck from "nobody checked the dashboard" to "nobody checked Slack." The lagging indicators are the actual point — but they only mean something once the leading indicators show the system is trusted enough to run.

## Conclusion

I started this project to work on my PM skills — to go through the full loop of finding a real problem, scoping it, and shipping something that could actually help a real agency, not just a toy idea. With some back-and-forth with people who actually work in this problem space, I was able to figure out what was genuinely worth solving. Unsurprisingly, that turned out to be the hard part — not the building, the *deciding what to build*.

Once I knew what I was building, building the agent from scratch turned out to be the fun part. Agentic tools like Claude Code made what could've been a slow, fiddly integration project feel easy and intuitive — I could move from "here's the spec" to "here's a working pipeline" in a weekend. Along the way I picked up LangChain and LangGraph as a new framework for building agents, and I'm excited to keep exploring how this kind of AI tooling can help me build projects that fit seamlessly into my day-to-day work — not just one-off prototypes.

## Sources

- Analysis of 500+ social campaigns on first-hour engagement and algorithmic amplification
- Hootsuite experiment on early engagement push vs. reach (Instagram)
- Meta internal data on lookalike audience conversion rates vs. broad targeting
- WordStream data on lookalike audience CPA vs. standard targeting
- Seer Interactive (Sep 2025) — organic/paid CTR impact of AI Overviews
- Industry surveys on marketing leader agency spend and agency headcount plans (2025–2026)
- SOCi "Genius Agents" — publicly reported deployment and task-completion figures
