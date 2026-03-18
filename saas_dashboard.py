"""
SaaS Monthly Metrics Dashboard
Refactored to comply with SaaS Data Analysis Skill guidelines:
  - ARR, MRR MoM Growth, Net Sub Growth, CAC, LTV, LTV:CAC
  - NPS trend over time
  - Churn rate trend by plan
  - Sidebar filters (date, region, plan)
  - Correct metric formulas throughout
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaaS Monthly Metrics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEMPLATE  = "plotly_dark"   # overridden by toggle below
CHART_H   = 370
PLAN_ORDER = ["Basic", "Pro", "Business", "Enterprise"]
PLAN_COLORS = {
    "Basic":      "#3B82F6",
    "Pro":        "#10B981",
    "Business":   "#F59E0B",
    "Enterprise": "#8B5CF6",
}

# ── Load ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("saas_monthly_metrics.csv")
    df["month"] = pd.to_datetime(df["month"], format="%b-%y")
    df = df.sort_values("month").reset_index(drop=True)
    # ── Derived metrics (skill-mandated formulas) ─────────────────────────────
    # Correct ARPU: MRR / active_subscribers (not mean of pre-computed column)
    df["arpu_calc"] = df["mrr_usd"] / df["active_subscribers"].replace(0, np.nan)
    # Monthly churn rate per row
    df["churn_rate"] = (
        df["churned_subscribers"]
        / (df["active_subscribers"] + df["churned_subscribers"]).replace(0, np.nan)
    )
    # CAC: marketing spend per new subscriber
    df["cac"] = df["marketing_spend_usd"] / df["new_subscribers"].replace(0, np.nan)
    # LTV estimate: ARPU / monthly_churn_rate  (LTV = 1/churn_rate × ARPU)
    df["ltv"] = df["arpu_calc"] / df["churn_rate"].replace(0, np.nan)
    # Net subscriber growth
    df["net_sub_growth"] = df["new_subscribers"] - df["churned_subscribers"]
    return df

raw = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 Filters")
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    st.markdown("---")

    all_months  = sorted(raw["month"].unique())
    date_range  = st.select_slider(
        "Date Range",
        options=all_months,
        value=(all_months[0], all_months[-1]),
        format_func=lambda d: pd.Timestamp(d).strftime("%b %Y"),
    )

    all_regions = sorted(raw["region"].unique())
    sel_regions = st.multiselect("Region", all_regions, default=all_regions)

    all_plans   = PLAN_ORDER
    sel_plans   = st.multiselect("Plan Tier", all_plans, default=all_plans)

    st.markdown("---")
    st.caption("SaaS Metrics Dashboard\nv2.0 · Skill-compliant")

# ── Theme ─────────────────────────────────────────────────────────────────────
TEMPLATE = "plotly_dark" if dark_mode else "plotly_white"

if dark_mode:
    _bg       = "#0E1117"
    _surface  = "#1A1C24"
    _text     = "#FAFAFA"
    _subtext  = "#A0A0B0"
    _sidebar  = "#16181F"
    _border   = "#2E3040"
    _input_bg = "#1E2030"
else:
    _bg       = "#FFFFFF"
    _surface  = "#F4F6FA"
    _text     = "#1F2937"
    _subtext  = "#6B7280"
    _sidebar  = "#F0F2F6"
    _border   = "#D1D5DB"
    _input_bg = "#FFFFFF"

st.markdown(f"""
<style>
  /* ── Main app background ───────────────────────────────────────── */
  .stApp, .main .block-container {{
      background-color: {_bg} !important;
      color: {_text} !important;
  }}

  /* ── Top header bar ─────────────────────────────────────────────── */
  [data-testid="stHeader"],
  header.stAppHeader,
  .stAppToolbar {{
      background-color: {_bg} !important;
      border-bottom: 1px solid {_border} !important;
  }}
  [data-testid="stHeader"] * {{ color: {_text} !important; }}
  [data-testid="stToolbar"] button,
  [data-testid="stMainMenuButton"] {{
      color: {_text} !important;
  }}

  /* ── Sidebar ───────────────────────────────────────────────────── */
  [data-testid="stSidebar"],
  [data-testid="stSidebar"] > div:first-child {{
      background-color: {_sidebar} !important;
  }}
  [data-testid="stSidebar"] * {{ color: {_text} !important; }}

  /* ── Multiselect container (the input box itself) ──────────────── */
  [data-baseweb="select"] > div,
  [data-baseweb="select"] > div:focus-within {{
      background-color: {_input_bg} !important;
      border-color: {_border} !important;
      color: {_text} !important;
  }}

  /* ── Multiselect tags (the coloured chips) ─────────────────────── */
  [data-baseweb="tag"] {{
      background-color: {_surface} !important;
      border: 1px solid {_border} !important;
      color: {_text} !important;
      border-radius: 6px !important;
  }}
  [data-baseweb="tag"] span {{ color: {_text} !important; }}
  /* X button inside tag */
  [data-baseweb="tag"] [role="button"] {{ color: {_subtext} !important; }}

  /* ── Multiselect dropdown menu ─────────────────────────────────── */
  [data-baseweb="popover"],
  [data-baseweb="menu"],
  [role="listbox"] {{
      background-color: {_surface} !important;
      border: 1px solid {_border} !important;
  }}
  [role="option"] {{
      background-color: {_surface} !important;
      color: {_text} !important;
  }}
  [role="option"]:hover {{
      background-color: {_border} !important;
  }}

  /* ── Slider (range / select_slider) ───────────────────────────── */
  [data-testid="stSlider"] > div > div > div {{
      background-color: {_border} !important;       /* track background */
  }}
  [data-testid="stSlider"] [role="slider"] {{
      background-color: #4F8EF7 !important;          /* thumb colour */
      border: 2px solid #4F8EF7 !important;
  }}
  /* filled portion of track */
  [data-testid="stSlider"] > div > div > div > div {{
      background-color: #4F8EF7 !important;
  }}
  /* tick labels */
  [data-testid="stSlider"] p {{
      color: {_subtext} !important;
      font-size: 11px !important;
  }}

  /* ── Metric cards ──────────────────────────────────────────────── */
  [data-testid="stMetric"] {{
      background-color: {_surface} !important;
      border: 1px solid {_border} !important;
      border-radius: 10px !important;
      padding: 14px 18px !important;
  }}
  [data-testid="stMetricLabel"] {{ color: {_subtext} !important; font-size: 13px !important; }}
  [data-testid="stMetricValue"] {{ color: {_text}    !important; font-size: 22px !important; font-weight: 700 !important; }}
  [data-testid="stMetricDelta"]  {{ font-size: 12px !important; }}

  /* ── Plotly chart containers (remove white flash) ──────────────── */
  .stPlotlyChart, .stPlotlyChart > div, iframe {{
      background-color: transparent !important;
  }}
  .js-plotly-plot .plotly, .js-plotly-plot .plotly .bg {{
      background-color: transparent !important;
  }}

  /* ── Toggle widget ─────────────────────────────────────────────── */
  [data-testid="stToggle"] span {{ color: {_text} !important; }}

  /* ── Dividers & general text ───────────────────────────────────── */
  hr {{ border-color: {_border} !important; }}
  h1, h2, h3, h4, p, label {{ color: {_text} !important; }}
  .stCaption, [data-testid="stCaptionContainer"] * {{
      color: {_subtext} !important;
  }}

  /* ── Scrollbar (subtle) ────────────────────────────────────────── */
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: {_bg}; }}
  ::-webkit-scrollbar-thumb {{ background: {_border}; border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)

# ── Chart theme helper ────────────────────────────────────────────────────────
def th(fig):
    """Apply transparent background and consistent font colour to any figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font_color   =_text,
    )
    return fig

# ── Filter dataframe ──────────────────────────────────────────────────────────
df = raw[
    (raw["month"] >= pd.Timestamp(date_range[0]))
    & (raw["month"] <= pd.Timestamp(date_range[1]))
    & (raw["region"].isin(sel_regions if sel_regions else all_regions))
    & (raw["plan"].isin(sel_plans   if sel_plans   else all_plans))
].copy()

if df.empty:
    st.error("No data matches the current filters. Please broaden your selection.")
    st.stop()

# ── Monthly aggregates ────────────────────────────────────────────────────────
monthly = (
    df.groupby("month")
    .agg(
        mrr_usd              =("mrr_usd",               "sum"),
        active_subscribers   =("active_subscribers",    "sum"),
        churned_subscribers  =("churned_subscribers",   "sum"),
        new_subscribers      =("new_subscribers",       "sum"),
        nps_score            =("nps_score",             "mean"),
        marketing_spend_usd  =("marketing_spend_usd",  "sum"),
        support_tickets      =("support_tickets",       "sum"),
    )
    .reset_index()
    .sort_values("month")
)

# Skill-defined formulas on aggregated monthly data
monthly["arr"]          = monthly["mrr_usd"] * 12
monthly["mrr_growth"]   = monthly["mrr_usd"].pct_change() * 100          # MoM %
monthly["churn_rate"]   = (
    monthly["churned_subscribers"]
    / (monthly["active_subscribers"] + monthly["churned_subscribers"])
    * 100
)
monthly["net_sub_growth"] = monthly["new_subscribers"] - monthly["churned_subscribers"]
monthly["arpu"]          = monthly["mrr_usd"] / monthly["active_subscribers"].replace(0, np.nan)
monthly["cac"]           = monthly["marketing_spend_usd"] / monthly["new_subscribers"].replace(0, np.nan)
monthly["ltv"]           = monthly["arpu"] / (monthly["churn_rate"] / 100).replace(0, np.nan)
monthly["ltv_cac"]       = monthly["ltv"] / monthly["cac"].replace(0, np.nan)

latest   = monthly.iloc[-1]
previous = monthly.iloc[-2] if len(monthly) > 1 else monthly.iloc[-1]

def fmt_delta(val, fmt="{:+,.0f}"):
    return fmt.format(val)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("SaaS Monthly Metrics Dashboard")
st.caption(
    f"📅 {pd.Timestamp(date_range[0]).strftime('%b %Y')} → "
    f"{pd.Timestamp(date_range[1]).strftime('%b %Y')}  |  "
    f"Regions: {', '.join(sel_regions) if sel_regions else 'All'}  |  "
    f"Plans: {', '.join(sel_plans) if sel_plans else 'All'}  |  "
    f"{len(df):,} records"
)
st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# ROW A — Core Revenue KPIs  (4 cards)
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("Revenue KPIs")
a1, a2, a3, a4 = st.columns(4)

a1.metric(
    "💰 Total MRR",
    f"${latest['mrr_usd']:,.0f}",
    delta=f"${latest['mrr_usd'] - previous['mrr_usd']:+,.0f}",
)
a2.metric(
    "📈 ARR  (MRR × 12)",
    f"${latest['arr']:,.0f}",
    delta=f"${(latest['arr'] - previous['arr']):+,.0f}",
)
a3.metric(
    "📊 MRR MoM Growth",
    f"{latest['mrr_growth']:.1f}%" if pd.notna(latest['mrr_growth']) else "N/A",
    delta=f"{latest['mrr_growth'] - previous['mrr_growth']:+.1f} pp"
          if pd.notna(latest['mrr_growth']) and pd.notna(previous['mrr_growth']) else None,
)
a4.metric(
    "👥 Net Sub Growth",
    f"{int(latest['net_sub_growth']):+,}",
    delta=f"{int(latest['net_sub_growth'] - previous['net_sub_growth']):+,}",
)

# ═════════════════════════════════════════════════════════════════════════════
# ROW B — Operational KPIs  (5 cards)
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("Operational KPIs")
b1, b2, b3, b4, b5 = st.columns(5)

b1.metric(
    "🏢 Active Subscribers",
    f"{int(latest['active_subscribers']):,}",
    delta=f"{int(latest['active_subscribers'] - previous['active_subscribers']):+,}",
)
b2.metric(
    "📉 Churn Rate",
    f"{latest['churn_rate']:.2f}%",
    delta=f"{latest['churn_rate'] - previous['churn_rate']:+.2f} pp",
    delta_color="inverse",
)
b3.metric(
    "💵 ARPU",
    f"${latest['arpu']:.2f}",
    delta=f"${latest['arpu'] - previous['arpu']:+.2f}",
)
b4.metric(
    "🎯 CAC",
    f"${latest['cac']:.2f}" if pd.notna(latest['cac']) else "N/A",
    delta=f"${latest['cac'] - previous['cac']:+.2f}"
          if pd.notna(latest['cac']) and pd.notna(previous['cac']) else None,
    delta_color="inverse",
)
b5.metric(
    "⚖️ LTV : CAC",
    f"{latest['ltv_cac']:.1f}x" if pd.notna(latest['ltv_cac']) else "N/A",
    delta=f"{latest['ltv_cac'] - previous['ltv_cac']:+.2f}x"
          if pd.notna(latest['ltv_cac']) and pd.notna(previous['ltv_cac']) else None,
)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# ROW 2 — Revenue Charts
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("Revenue Trends")
c1, c2, c3 = st.columns(3)

# ── 2a  MRR Trend by Region ───────────────────────────────────────────────────
mrr_region = (
    df.groupby(["month", "region"])["mrr_usd"]
    .sum().reset_index().sort_values("month")
)
fig_mrr = px.line(
    mrr_region, x="month", y="mrr_usd", color="region",
    title="MRR Trend by Region",
    labels={"mrr_usd": "MRR (USD)", "month": "Month"},
    template=TEMPLATE, height=CHART_H,
)
fig_mrr.update_layout(
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    yaxis_tickprefix="$", yaxis_tickformat=",.0f",
    margin=dict(t=55, b=30),
)
c1.plotly_chart(th(fig_mrr), width="stretch")

# ── 2b  MRR MoM Growth Rate (bar) ────────────────────────────────────────────
growth_df = monthly.dropna(subset=["mrr_growth"]).copy()
growth_df["color"] = growth_df["mrr_growth"].apply(
    lambda v: "#10B981" if v >= 0 else "#EF4444"
)
fig_growth = go.Figure(go.Bar(
    x=growth_df["month"],
    y=growth_df["mrr_growth"],
    marker_color=growth_df["color"],
    text=growth_df["mrr_growth"].apply(lambda v: f"{v:+.1f}%"),
    textposition="outside",
))
fig_growth.add_hline(y=0, line_dash="dot", line_color="white", line_width=1)
fig_growth.update_layout(
    title="MRR Month-over-Month Growth Rate",
    xaxis_title="Month", yaxis_title="MoM Growth (%)",
    template=TEMPLATE, height=CHART_H,
    margin=dict(t=55, b=30),
    yaxis_ticksuffix="%",
)
c2.plotly_chart(th(fig_growth), width="stretch")

# ── 2c  ARPU by Plan (horizontal bar, skill formula: MRR/active) ─────────────
arpu_plan = (
    df.groupby("plan")
    .apply(lambda g: g["mrr_usd"].sum() / g["active_subscribers"].sum(), include_groups=False)
    .reset_index(name="arpu")
)
arpu_plan["plan"] = pd.Categorical(arpu_plan["plan"], categories=PLAN_ORDER, ordered=True)
arpu_plan = arpu_plan.sort_values("plan")

fig_arpu = px.bar(
    arpu_plan, x="arpu", y="plan", orientation="h",
    title="ARPU by Plan  (MRR ÷ Active Subscribers)",
    labels={"arpu": "ARPU (USD)", "plan": "Plan"},
    template=TEMPLATE, height=CHART_H,
    color="plan",
    color_discrete_map=PLAN_COLORS,
    text=arpu_plan["arpu"].apply(lambda v: f"${v:,.2f}"),
)
fig_arpu.update_traces(textposition="outside")
fig_arpu.update_layout(
    showlegend=False,
    xaxis_tickprefix="$", xaxis_tickformat=",.0f",
    xaxis_range=[0, arpu_plan["arpu"].max() * 1.2],
    margin=dict(t=55, b=30),
)
c3.plotly_chart(th(fig_arpu), width="stretch")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# ROW 3 — Subscriber & Retention
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("Subscriber Health & Retention")
d1, d2, d3 = st.columns(3)

# ── 3a  Subscriber Flow + net growth line ─────────────────────────────────────
sub_flow = monthly[["month", "new_subscribers", "churned_subscribers", "net_sub_growth"]].copy()

fig_flow = go.Figure()
fig_flow.add_bar(
    x=sub_flow["month"], y=sub_flow["new_subscribers"],
    name="New", marker_color="#10B981",
)
fig_flow.add_bar(
    x=sub_flow["month"], y=sub_flow["churned_subscribers"],
    name="Churned", marker_color="#EF4444",
)
fig_flow.add_scatter(
    x=sub_flow["month"], y=sub_flow["net_sub_growth"],
    name="Net Growth", mode="lines+markers",
    line=dict(color="#FBBF24", width=2.5, dash="dot"),
    marker=dict(size=5),
    yaxis="y",
)
fig_flow.update_layout(
    barmode="group",
    title="Subscriber Flow  (New / Churned / Net)",
    xaxis_title="Month", yaxis_title="Subscribers",
    template=TEMPLATE, height=CHART_H,
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    margin=dict(t=55, b=30),
)
d1.plotly_chart(th(fig_flow), width="stretch")

# ── 3b  NRR Heatmap ───────────────────────────────────────────────────────────
nrr_heat  = df.groupby(["month", "region"])["net_revenue_retention"].mean().reset_index()
nrr_pivot = nrr_heat.pivot(index="region", columns="month",
                            values="net_revenue_retention")
nrr_pivot.columns = [c.strftime("%b %y") for c in nrr_pivot.columns]

fig_heat = px.imshow(
    nrr_pivot,
    title="Net Revenue Retention  (Region × Month)",
    labels=dict(x="Month", y="Region", color="NRR"),
    color_continuous_scale="RdYlGn",
    aspect="auto", template=TEMPLATE, height=CHART_H,
    zmin=0.97, zmax=1.17,
)
fig_heat.update_layout(
    xaxis_tickangle=-45,
    coloraxis_colorbar=dict(title="NRR", tickformat=".2f"),
    margin=dict(t=55, b=60),
)
d2.plotly_chart(th(fig_heat), width="stretch")

# ── 3c  Net Subscriber Growth trend by region (stacked area) ─────────────────
net_region = (
    df.groupby(["month", "region"])
    .apply(
        lambda g: g["new_subscribers"].sum() - g["churned_subscribers"].sum(),
        include_groups=False
    )
    .reset_index(name="net_growth")
    .sort_values("month")
)
fig_net = px.area(
    net_region, x="month", y="net_growth", color="region",
    title="Net Subscriber Growth by Region",
    labels={"net_growth": "Net Growth", "month": "Month"},
    template=TEMPLATE, height=CHART_H,
)
fig_net.update_layout(
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    margin=dict(t=55, b=30),
)
d3.plotly_chart(th(fig_net), width="stretch")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# ROW 4 — Satisfaction & Churn Detail
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("Satisfaction & Churn")
e1, e2, e3 = st.columns(3)

# ── 4a  NPS Trend over time by Plan ──────────────────────────────────────────
nps_plan = (
    df.groupby(["month", "plan"])["nps_score"]
    .mean().reset_index().sort_values("month")
)
nps_plan["plan"] = pd.Categorical(nps_plan["plan"], categories=PLAN_ORDER, ordered=True)

fig_nps = px.line(
    nps_plan, x="month", y="nps_score", color="plan",
    title="NPS Score Trend by Plan Tier",
    labels={"nps_score": "NPS Score", "month": "Month", "plan": "Plan"},
    template=TEMPLATE, height=CHART_H,
    color_discrete_map=PLAN_COLORS,
    category_orders={"plan": PLAN_ORDER},
)
fig_nps.update_layout(
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    margin=dict(t=55, b=30),
)
e1.plotly_chart(th(fig_nps), width="stretch")

# ── 4b  Churn Rate trend by Plan ─────────────────────────────────────────────
churn_plan = (
    df.groupby(["month", "plan"])
    .apply(
        lambda g: g["churned_subscribers"].sum()
                  / (g["active_subscribers"].sum() + g["churned_subscribers"].sum()) * 100,
        include_groups=False
    )
    .reset_index(name="churn_rate")
    .sort_values("month")
)
churn_plan["plan"] = pd.Categorical(churn_plan["plan"], categories=PLAN_ORDER, ordered=True)

fig_churn = px.line(
    churn_plan, x="month", y="churn_rate", color="plan",
    title="Monthly Churn Rate by Plan Tier",
    labels={"churn_rate": "Churn Rate (%)", "month": "Month", "plan": "Plan"},
    template=TEMPLATE, height=CHART_H,
    color_discrete_map=PLAN_COLORS,
    category_orders={"plan": PLAN_ORDER},
)
fig_churn.update_layout(
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    yaxis_ticksuffix="%",
    margin=dict(t=55, b=30),
)
e2.plotly_chart(th(fig_churn), width="stretch")

# ── 4c  CAC by Region over time ──────────────────────────────────────────────
cac_region = (
    df.groupby(["month", "region"])
    .apply(
        lambda g: g["marketing_spend_usd"].sum() / g["new_subscribers"].sum()
                  if g["new_subscribers"].sum() > 0 else np.nan,
        include_groups=False
    )
    .reset_index(name="cac")
    .sort_values("month")
)
fig_cac = px.line(
    cac_region, x="month", y="cac", color="region",
    title="Customer Acquisition Cost (CAC) by Region",
    labels={"cac": "CAC (USD)", "month": "Month", "region": "Region"},
    template=TEMPLATE, height=CHART_H,
)
fig_cac.update_layout(
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    yaxis_tickprefix="$", yaxis_tickformat=",.0f",
    margin=dict(t=55, b=30),
)
e3.plotly_chart(th(fig_cac), width="stretch")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# ROW 5 — Operations & Unit Economics
# ═════════════════════════════════════════════════════════════════════════════
st.subheader("Operations & Unit Economics")
f1, f2, f3 = st.columns(3)

# ── 5a  Support Tickets vs Churned Subscribers (dual axis) ───────────────────
fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
fig_dual.add_trace(
    go.Scatter(x=monthly["month"], y=monthly["support_tickets"],
               name="Support Tickets", mode="lines+markers",
               line=dict(color="#EF4444", width=2), marker=dict(size=5)),
    secondary_y=False,
)
fig_dual.add_trace(
    go.Scatter(x=monthly["month"], y=monthly["churned_subscribers"],
               name="Churned Subscribers", mode="lines+markers",
               line=dict(color="#3B82F6", width=2, dash="dot"), marker=dict(size=5)),
    secondary_y=True,
)
fig_dual.update_layout(
    title="Support Tickets vs Churned Subscribers",
    template=TEMPLATE, height=CHART_H,
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    margin=dict(t=55, b=30),
)
fig_dual.update_yaxes(title_text="Support Tickets",    secondary_y=False)
fig_dual.update_yaxes(title_text="Churned Subscribers", secondary_y=True)
f1.plotly_chart(th(fig_dual), width="stretch")

# ── 5b  LTV : CAC Ratio by Region (latest month) ─────────────────────────────
latest_month = df["month"].max()
ltv_cac_region = (
    df[df["month"] == latest_month]
    .groupby("region")
    .apply(lambda g: (
        (g["mrr_usd"].sum() / g["active_subscribers"].sum())
        / (g["churn_rate"].mean())
    ) / (g["marketing_spend_usd"].sum() / g["new_subscribers"].sum())
    if g["new_subscribers"].sum() > 0 else np.nan, include_groups=False)
    .reset_index(name="ltv_cac")
    .sort_values("ltv_cac", ascending=True)
)

fig_ltvcac = px.bar(
    ltv_cac_region, x="ltv_cac", y="region", orientation="h",
    title=f"LTV : CAC Ratio by Region  ({latest_month.strftime('%b %Y')})",
    labels={"ltv_cac": "LTV : CAC", "region": "Region"},
    template=TEMPLATE, height=CHART_H,
    color="ltv_cac", color_continuous_scale="Blues",
    text=ltv_cac_region["ltv_cac"].apply(lambda v: f"{v:.1f}x" if pd.notna(v) else ""),
)
fig_ltvcac.add_vline(x=3, line_dash="dash", line_color="#FBBF24", line_width=1.5,
                     annotation_text="3x benchmark", annotation_position="top right",
                     annotation_font_color="#FBBF24")
fig_ltvcac.update_traces(textposition="outside")
fig_ltvcac.update_layout(
    coloraxis_showscale=False,
    margin=dict(t=55, b=30),
)
f2.plotly_chart(th(fig_ltvcac), width="stretch")

# ── 5c  ARPU vs NRR scatter (by plan, sized by active subs) ──────────────────
scatter_df = (
    df.groupby(["region", "plan"])
    .agg(
        arpu                 =("mrr_usd",                lambda x: x.sum() / df.loc[x.index, "active_subscribers"].sum()),
        nrr                  =("net_revenue_retention",  "mean"),
        active_subscribers   =("active_subscribers",     "mean"),
    )
    .reset_index()
)
scatter_df["plan"] = pd.Categorical(scatter_df["plan"], categories=PLAN_ORDER, ordered=True)

fig_scatter = px.scatter(
    scatter_df, x="arpu", y="nrr", color="plan", size="active_subscribers",
    facet_col=None, hover_data=["region"],
    title="ARPU vs Net Revenue Retention  (sized by active subs)",
    labels={"arpu": "ARPU (USD)", "nrr": "Net Revenue Retention", "plan": "Plan"},
    template=TEMPLATE, height=CHART_H,
    color_discrete_map=PLAN_COLORS,
    category_orders={"plan": PLAN_ORDER},
)
fig_scatter.add_hline(y=1.0, line_dash="dash", line_color="white", line_width=1,
                      annotation_text="NRR = 1.0", annotation_position="bottom right")
fig_scatter.update_layout(
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    xaxis_tickprefix="$",
    margin=dict(t=55, b=30),
)
f3.plotly_chart(th(fig_scatter), width="stretch")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "SaaS Monthly Metrics Dashboard · v2.0  |  "
    "Metrics: MRR · ARR · MoM Growth · Churn Rate · ARPU (MRR/Subs) · "
    "CAC (Spend/New Subs) · LTV (ARPU/Churn) · LTV:CAC · NRR  |  "
    "Built with Streamlit & Plotly"
)
