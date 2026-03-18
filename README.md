# SaaS Metrics Dashboard & Multi-Agent Advertising Pipeline

This project contains two components built as part of an AI Agentic Bootcamp:

1. **SaaS Monthly Metrics Dashboard** — an interactive Streamlit app for visualising SaaS KPIs
2. **Multi-Agent Advertising Pipeline** — a sequential AI agent system for generating advertising campaigns

---

## Environment Variables

The multi-agent pipeline requires an OpenAI API key. Copy `.env_example` to `.env` and fill in your key:

```bash
cp .env_example .env
```

`.env`:
```
OPENAI_API_KEY=your-openai-api-key-here
```

The `.env` file is listed in `.gitignore` and will never be committed.

---

## Installation

Install all dependencies at once using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Project Structure

```
.
├── requirements.txt                # Python dependencies
├── .env_example                    # Environment variable template (copy to .env)
├── .gitignore                      # Git ignore rules
├── saas_dashboard.py               # Streamlit dashboard app
├── saas_monthly_metrics.csv        # Source data (month × region × plan)
├── multi_agent_advertising_v2.ipynb  # Multi-agent pipeline (v2, recommended)
├── multi_agent_advertising.ipynb   # Multi-agent pipeline (v1)
├── ad_models.py                    # Pydantic output schemas for the pipeline
├── multi_agent_explanation.md      # Detailed explanation of the pipeline design
├── sample_output_v2.json           # Example pipeline output (structured JSON)
├── sample_output.txt               # Example pipeline output (v1, plain text)
├── eda_summary.csv                 # Exploratory data analysis summary
├── outlier_report.csv              # Outlier detection report
├── saas_executive_presentation.pptx  # Executive slide deck
└── viz_*.png                       # Pre-exported chart images
```

---

## Part 1 — SaaS Monthly Metrics Dashboard

An interactive dashboard built with **Streamlit** and **Plotly** that tracks SaaS business health across regions and plan tiers.

### Metrics covered

| Category | Metrics |
|---|---|
| Revenue | MRR, ARR, MRR MoM Growth |
| Growth | Net Subscriber Growth, New vs Churned |
| Unit Economics | ARPU (MRR ÷ Active Subs), CAC, LTV, LTV:CAC |
| Retention | Net Revenue Retention (NRR), Churn Rate by Plan |
| Satisfaction | NPS Score Trend by Plan |
| Operations | Support Tickets vs Churned Subscribers |

### Dashboard layout

- **Row A — Revenue KPIs:** MRR, ARR, MoM Growth, Net Sub Growth (4 metric cards)
- **Row B — Operational KPIs:** Active Subscribers, Churn Rate, ARPU, CAC, LTV:CAC (5 metric cards)
- **Revenue Trends:** MRR by region, MoM growth bar chart, ARPU by plan
- **Subscriber Health:** Subscriber flow (new/churned/net), NRR heatmap, net growth by region
- **Satisfaction & Churn:** NPS trend, churn rate by plan, CAC by region
- **Operations & Unit Economics:** Support tickets vs churn, LTV:CAC by region, ARPU vs NRR scatter

### Sidebar filters

- Date range slider
- Region multiselect
- Plan tier multiselect (Basic / Pro / Business / Enterprise)
- Dark/light mode toggle

### How to run

```bash
pip install -r requirements.txt
streamlit run saas_dashboard.py
```

The app opens at `http://localhost:8501` in your browser. The CSV file `saas_monthly_metrics.csv` must be in the same directory.

---

## Part 2 — Multi-Agent Advertising Pipeline

A sequential AI pipeline that generates a full advertising campaign from a single text prompt. Four specialised agents collaborate in order, each building on the previous agent's output.

### Pipeline flow

```
User Prompt
    ↓
Creative Director  →  CreativeBrief
    ↓
Strategist         →  CampaignStrategy
    ↓
Copywriter         →  AdCopy
    ↓
Media Planner      →  MediaPlan (JSON output)
```

### Agents

| Agent | Role | Output |
|---|---|---|
| Creative Director | Sets the campaign vision | Campaign name, tagline, brand message, visual direction, objectives |
| Strategist | Defines audience & channels | Target audience, messaging pillars, channel mix, campaign hooks |
| Copywriter | Writes all copy assets | Instagram caption, video script, email copy, print headline & body |
| Media Planner | Allocates budget & timeline | Channel budget split, KPIs, 8-week launch milestones |

### Features (v2)

- Structured Pydantic outputs via `output_type` (schemas in `ad_models.py`)
- Agent instructions follow the **Role / Goal / Backstory** pattern
- Input guardrails: length validation (10–500 chars) + banned keyword check
- Retry logic: exponential backoff up to 3 attempts (1 s, 2 s, 4 s)
- Per-agent token tracking with estimated cost
- Output saved as structured JSON (`sample_output_v2.json`)

### How to run

```bash
pip install -r requirements.txt
```

Set your API key by copying `.env_example` to `.env` (see Environment Variables above), then open the notebook and run all cells:

```bash
jupyter notebook multi_agent_advertising_v2.ipynb
```

Edit the `user_prompt` variable in the notebook to change the campaign brief. The pipeline uses `gpt-4o-mini` for all agents.

For a detailed explanation of the pipeline design, agent roles, and design decisions, see [`multi_agent_explanation.md`](multi_agent_explanation.md).

---

## Data — `saas_monthly_metrics.csv`

The dashboard reads from this CSV which contains monthly SaaS metrics segmented by region and plan tier.

| Column | Description |
|---|---|
| `month` | Month label (e.g. `Jan-23`) |
| `region` | Geographic region (e.g. North America, Europe) |
| `plan` | Subscription tier (Basic / Pro / Business / Enterprise) |
| `new_subscribers` | New subs acquired that month |
| `churned_subscribers` | Subs lost that month |
| `active_subscribers` | Total active subs at end of month |
| `mrr_usd` | Monthly Recurring Revenue (USD) |
| `net_revenue_retention` | NRR ratio (>1.0 = expansion revenue) |
| `marketing_spend_usd` | Marketing spend for the month |
| `support_tickets` | Support tickets raised |
| `nps_score` | Net Promoter Score |
