---
name: saas-data-analysis
description: Analyze SaaS monthly metrics datasets including MRR, churn,
ARPU, NPS, subscribers, marketing spend, and support tickets. Generates
EDA summaries, dashboards, visualizations, and executive presentations.
---

# SaaS Data Analysis Skill

## When to Use

Trigger when the user asks to analyze SaaS/subscription business metrics
including any of: MRR, ARR, churn, ARPU, NPS, subscriber counts,
revenue retention, marketing spend, or support tickets.

## Required Libraries

- pandas, openpyxl (data loading)
- matplotlib, seaborn (static charts)
- plotly, kaleido (interactive charts and HTML dashboards)
- scipy (statistical tests)
- python-pptx (PowerPoint generation)

## Analysis Framework

1. LOAD: Read Excel/CSV, convert dates, check nulls
2. DESCRIBE: Compute mean, median, std, Q1, Q3 for all numeric cols
3. DETECT OUTLIERS: IQR method (Q1-1.5*IQR to Q3+1.5*IQR)
4. SEGMENT: Group by region, plan tier, time period
5. CORRELATE: Correlation matrix, highlight top relationships
6. VISUALIZE: 10 chart types covering trends, distributions, comparisons
7. DASHBOARD: Single-page HTML with Plotly subplots and KPI cards
8. PRESENT: 10-slide PPTX with findings and recommendations

## Key Metrics to Always Include

- MRR growth rate (month-over-month)
- Net subscriber growth (new - churned)
- Churn rate = churned / (active + churned)
- Net revenue retention (>1 = expansion, <1 = contraction)
- ARPU by segment
- NPS trends and distribution

## Output Files- eda_summary.csv (descriptive statistics)

- outlier_report.csv (outlier details)
- saas_dashboard.html (interactive dashboard)
- viz_01 through viz_10.png (10 visualizations)
- executive_presentation.pptx (10-slide deck)
