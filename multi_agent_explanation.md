# Creative Advertising Multi-Agent System — Explanation (v2)

## Overview

This system implements a **sequential multi-agent pipeline** for generating professional advertising campaigns using the **OpenAI Agents SDK**, upgraded with **CrewAI best practices**. Four specialized AI agents collaborate in a defined order, each building on the previous agent's structured output.

**Pipeline flow:**
```
User Prompt
    ↓
Creative Director  →  CreativeBrief (Pydantic)
    ↓
Strategist         →  CampaignStrategy (Pydantic)
    ↓
Copywriter         →  AdCopy (Pydantic)
    ↓
Media Planner      →  MediaPlan (Pydantic)
```

---

## Role of Each Agent

Each agent is defined using the **Role / Goal / Backstory** instruction pattern from CrewAI:
- **Role** — what the agent *is*
- **Goal** — what it must *achieve*
- **Backstory** — context that shapes its *judgment*

### 1. Creative Director
**Role:** Senior Creative Director at a top-tier global advertising agency.
**Goal:** Receive a raw campaign request and produce a sharp, inspiring creative brief that sets the vision for the entire campaign team.
**Backstory:** Has led campaigns for Nike, Patagonia, and emerging DTC brands. Makes clear creative bets rather than trying to please everyone; considers local culture, emotional resonance, and brand differentiation.
**Output (`CreativeBrief`):** Campaign name, tagline concept, core brand message, visual direction, and campaign objectives.
**Why first?** The creative brief is the vision document that all subsequent work must align with. No strategy or copy is written before it is locked.

### 2. Strategist
**Role:** Brand Strategist specialising in digital and experiential marketing.
**Goal:** Transform a creative brief into an actionable strategic plan — audience profile, messaging pillars, channel mix, and campaign hooks — that the Copywriter can execute immediately.
**Backstory:** Has led go-to-market strategies for lifestyle, wellness, and sustainability brands across South-East Asia. Combines cultural intelligence with data-driven channel selection.
**Output (`CampaignStrategy`):** Target audience profile, three messaging pillars, recommended channels, and campaign hooks.
**Why second?** Strategy translates creative vision into audience-specific direction. The Copywriter needs to know *who* they're talking to before writing a word.

### 3. Copywriter
**Role:** Award-winning Copywriter known for culturally resonant, conversion-driven ad copy.
**Goal:** Produce a complete suite of copy assets — taglines, social captions, video scripts, email copy, and print — tightly aligned with the brief and strategy received.
**Backstory:** Has written campaigns for global consumer brands; won Cannes Lions. Matches tone to platform (punchy on Instagram, narrative on email, sensory for print).
**Output (`AdCopy`):** Hero tagline, Instagram caption with hashtags, 15-second video script, email subject line, email preview text, print headline, and 50-word print body.
**Why third?** Copy is the final execution layer. It can only be written effectively once the creative direction and audience strategy are fully defined.

### 4. Media Planner
**Role:** Senior Media Planner at a full-service advertising agency.
**Goal:** Translate a finished creative campaign into a concrete, budget-allocated media plan with measurable KPIs and a realistic launch timeline.
**Backstory:** Has placed campaigns across Instagram, TikTok, YouTube, OOH, and influencer networks. Thinks in CPM, ROAS, and reach curves; balances awareness spend against conversion spend based on brand maturity stage.
**Output (`MediaPlan`):** Total budget, channel-by-channel budget percentages, campaign timeline (weeks), KPIs, and week-by-week launch milestones.
**Why last?** Media planning requires knowing the full creative vision, target audience, and copy assets before committing budget and channel choices.

---

## Tools & Technologies Used

| Component | Technology |
|-----------|-----------|
| Agent framework | `openai-agents` SDK (`agents.Agent`, `agents.Runner`, `agents.handoff`) |
| Language model | `gpt-4o-mini` (per agent) |
| Notebook environment | Jupyter Notebook (`.ipynb`) |
| Agent instruction pattern | Role / Goal / Backstory (CrewAI best practice) |
| Handoff wiring | `handoff(next_agent)` declared on each agent; chain: CD → Strategist → Copywriter → Media Planner |
| Structured outputs | Pydantic models via `output_type`: `CreativeBrief`, `CampaignStrategy`, `AdCopy`, `ChannelAllocation`, `MediaPlan` (from `ad_models.py`) |
| Context passing | Accumulated JSON context injected into each agent's input prompt |
| Input guardrails | Length validation (10–500 chars) + banned keyword list (`spam`, `mislead`, `fake`, `scam`, `illegal`) |
| Retry logic | Exponential backoff — up to 3 attempts; waits 1 s, 2 s, 4 s between retries |
| Token tracking | Per-agent extraction from `result.raw_responses`; cost estimated at $0.00015/1K input + $0.00060/1K output |
| Output persistence | `sample_output_v2.json` (structured JSON with all four agents' outputs + token log) |

---

## Why Multi-Agent vs. Single-Agent?

| Dimension | Single Agent | Multi-Agent (This System) |
|-----------|-------------|--------------------------|
| **Focus** | One prompt tries to do everything | Each agent has one clear, expert role |
| **Output quality** | Shallow across all areas | Deep expertise per stage |
| **Error isolation** | Hard to identify which part failed | Failures are scoped to one agent |
| **Scalability** | Adding tasks bloats the single prompt | New agents can be inserted into the chain |
| **Reusability** | Not reusable | Each agent can be reused across campaigns |

In a single-agent setup, the model is asked to simultaneously think like a Creative Director, Strategist, Copywriter, and Media Planner — leading to generic, unfocused output. The multi-agent pipeline mimics the real-world agency workflow: specialized roles hand off to each other, with each stage deepening the quality of the final deliverable.

---

## What Changed from v1

| Feature | v1 | v2 |
|---------|----|----|
| Output format | Raw text strings | Pydantic models (`output_type`) |
| Agent instructions | Bullet-list prompts | Role / Goal / Backstory pattern |
| Agent count | 3 | **4** (+ Media Planner) |
| `handoff` usage | Imported, unused | Wired on every agent |
| Error handling | None | Retry with exponential backoff (3 attempts) |
| Input validation | None | Guardrail (length + banned keywords) |
| Token tracking | None | Per-agent + total cost estimate |
| Output file | Plain `.txt` | Structured `.json` |

---

## Test Run

**Prompt used:** `"Launch a campaign for a new eco-friendly water bottle in Bali"`

The full pipeline output (all four agents) is saved in `sample_output_v2.json`. Key results:

| Agent | Key Output |
|-------|-----------|
| Creative Director | Campaign: *Bali's Pure Flow* — "Refresh Sustainably, Live Consciously" |
| Strategist | Eco-conscious tourists & locals aged 25–45; channels: Instagram, Local Partnerships, Facebook |
| Copywriter | Hero tagline, Instagram caption, 15-sec video script, email subject, print headline & body |
| Media Planner | $50,000 budget; Instagram 40%, Local Partnerships 30%, Facebook 20%, Influencer Networks 10%; 8-week roadmap |

**Token usage:**

| Agent | Input tokens | Output tokens | Est. cost (USD) |
|-------|-------------|--------------|----------------|
| Creative Director | 358 | 130 | $0.000132 |
| Strategist | 503 | 284 | $0.000246 |
| Copywriter | 838 | 170 | $0.000228 |
| Media Planner | 1,039 | 252 | $0.000307 |
| **Total** | **2,738** | **836** | **$0.000913** |

---

## How to Extend Further

- Add a **Brand Guardian** agent to validate all copy against brand guidelines before the Media Planner runs
- Attach **tools** (web search, social trend APIs) via `tools=[...]` on any agent
- Enable **memory** between runs by persisting `results` and injecting prior campaigns as context
- Switch to **hierarchical orchestration** by promoting the Creative Director to an orchestrator that spawns and delegates to the other agents
