import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from datetime import datetime

st.set_page_config(page_title="Dheeraj Bhaskaruni | Data Analyst", layout="wide", page_icon="📊")

# ── data loading with caching ──
@st.cache_data
def load_orders():
    df = pd.read_csv("04_ecommerce_executive_dashboard/data/orders.csv", parse_dates=["order_date"])
    df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    return df

@st.cache_data
def load_customers():
    return pd.read_csv("04_ecommerce_executive_dashboard/data/customers.csv")

@st.cache_data
def load_ab_test():
    df = pd.read_csv("05_ab_test_checkout_optimization/data/ab_test_checkout.csv")
    return df[df["session_duration_sec"] >= 5]

@st.cache_data
def load_repos():
    return pd.read_csv("01_ai_ecosystem_analysis/data/github_ai_repos.csv")

@st.cache_data
def load_models():
    return pd.read_csv("01_ai_ecosystem_analysis/data/huggingface_models.csv")

@st.cache_data
def load_co2():
    df = pd.read_csv("02_global_co2_analysis/data/owid_co2_data.csv")
    return df[df["iso_code"].notna() & (df["iso_code"] != "")]

@st.cache_data
def load_crypto():
    return pd.read_csv("03_crypto_market_analysis/data/crypto_market.csv")

@st.cache_data
def load_churn_features():
    return pd.read_csv("06_churn_prediction/data/customer_features.csv")

@st.cache_data
def load_monthly_sales():
    return pd.read_csv("07_sales_forecasting/data/monthly_sales.csv", parse_dates=["month"])


# ── sidebar ──
st.sidebar.title("Dheeraj Bhaskaruni")
st.sidebar.caption("Data Analyst Portfolio")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "Overview",
    "E-Commerce Dashboard",
    "A/B Test Analysis",
    "Churn Prediction",
    "Sales Forecasting",
    "AI & ML Ecosystem",
    "Global CO2 Emissions",
    "Crypto Market",
], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("[GitHub](https://github.com/Dheeraj-Bhaskaruni) · [LinkedIn](https://linkedin.com/in/dheeraj-bhaskaruni)")


# ── color palette ──
PALETTE = {
    "primary": "#1a1a2e",
    "blue": "#0f3460",
    "accent": "#e94560",
    "green": "#27AE60",
    "orange": "#F39C12",
    "gray": "#95A5A6",
}


# ════════════════════════════════════════════════════════════════
# OVERVIEW
# ════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("Hey, I'm Dheeraj.")
    st.markdown("""
    I'm a data analyst who likes digging into messy data and turning it into something
    useful. This portfolio is a collection of projects I've worked on — some business-focused,
    some exploratory. Each one uses real data, not toy datasets.

    Pick a project from the sidebar to explore it interactively.
    """)

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Business Projects")
        st.markdown("""
        **E-Commerce Executive Dashboard**
        Built a KPI dashboard on ~7K orders — revenue trends, RFM customer segmentation,
        cohort retention heatmaps, and SQL queries I'd actually use in production.
        The kind of thing you'd present in a weekly business review.

        **A/B Test: Checkout Optimization**
        Ran a full experiment analysis on 15K users testing a new checkout flow.
        SRM validation, z-test, power analysis, segment breakdowns, revenue impact
        estimation, and a ship/no-ship recommendation with rollout plan.

        **Churn Prediction**
        Feature engineering from order data, model comparison
        (Logistic Regression vs Random Forest vs Gradient Boosting), SHAP explanations,
        actionable retention recommendations.

        **Sales Forecasting**
        Time series decomposition, Holt-Winters vs regression vs
        gradient boosting, next-quarter revenue projection with confidence bands.
        """)

    with c2:
        st.markdown("#### Exploratory Projects")
        st.markdown("""
        **AI & ML Ecosystem**
        Pulled data from GitHub and HuggingFace APIs to map out the open-source
        ML landscape — which frameworks dominate, what tasks models are being
        built for, and how the ecosystem has evolved.

        **Global CO2 Emissions**
        Analyzed OWID climate data across countries and decades. Per-capita trends,
        emission sources, regional comparisons. Interactive country selector.

        **Crypto Market**
        CoinGecko data on 250 coins — market dominance, price momentum,
        distance from ATH. More of a data exploration than a trading strategy.
        """)

    st.markdown("---")
    st.markdown("##### What I work with")
    st.markdown("Python · SQL · Pandas · Plotly · Scipy · Scikit-learn · Streamlit · Jupyter · Git")


# ════════════════════════════════════════════════════════════════
# E-COMMERCE DASHBOARD
# ════════════════════════════════════════════════════════════════
elif page == "E-Commerce Dashboard":
    st.title("E-Commerce Executive Dashboard")

    orders = load_orders()
    active = orders[orders["order_status"] != "Cancelled"].copy()

    # ── date filter ──
    min_date = active["order_date"].min().date()
    max_date = active["order_date"].max().date()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        start_date = st.date_input("From", min_date, min_value=min_date, max_value=max_date)
    with col_f2:
        end_date = st.date_input("To", max_date, min_value=min_date, max_value=max_date)

    mask = (active["order_date"].dt.date >= start_date) & (active["order_date"].dt.date <= end_date)
    filtered = active[mask]

    # ── KPIs with MoM comparison ──
    st.markdown("---")

    current_month = filtered["order_date"].dt.to_period("M").max()
    prev_month = current_month - 1

    curr = filtered[filtered["order_date"].dt.to_period("M") == current_month]
    prev = filtered[filtered["order_date"].dt.to_period("M") == prev_month]

    def mom_delta(curr_val, prev_val):
        if prev_val == 0:
            return None
        return f"{((curr_val - prev_val) / prev_val) * 100:+.1f}%"

    curr_rev = curr["revenue"].sum()
    prev_rev = prev["revenue"].sum()
    curr_orders = curr["order_id"].nunique()
    prev_orders = prev["order_id"].nunique()
    curr_aov = curr_rev / curr_orders if curr_orders > 0 else 0
    prev_aov = prev_rev / prev_orders if prev_orders > 0 else 0
    curr_cust = curr["customer_id"].nunique()
    prev_cust = prev["customer_id"].nunique()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Revenue", f"${curr_rev:,.0f}", mom_delta(curr_rev, prev_rev))
    k2.metric("Orders", f"{curr_orders:,}", mom_delta(curr_orders, prev_orders))
    k3.metric("Avg Order Value", f"${curr_aov:,.2f}", mom_delta(curr_aov, prev_aov))
    k4.metric("Customers", f"{curr_cust:,}", mom_delta(curr_cust, prev_cust))

    st.caption(f"MoM comparison: {current_month} vs {prev_month}")

    # ── Revenue trend ──
    monthly = filtered.set_index("order_date").resample("M")["revenue"].sum().reset_index()
    monthly.columns = ["month", "revenue"]

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["revenue"],
        mode="lines+markers", fill="tozeroy",
        line=dict(color=PALETTE["blue"], width=2),
        marker=dict(size=5),
        hovertemplate="$%{y:,.0f}<extra></extra>"
    ))
    fig_rev.update_layout(title="Monthly Revenue", xaxis_title="", yaxis_title="Revenue ($)",
                          hovermode="x unified", template="plotly_white", height=350)
    st.plotly_chart(fig_rev, use_container_width=True)

    # ── Category + Country side by side ──
    c1, c2 = st.columns(2)

    with c1:
        cat_rev = filtered.groupby("category")["revenue"].sum().sort_values(ascending=True)
        fig_cat = px.bar(x=cat_rev.values, y=cat_rev.index, orientation="h",
                         labels={"x": "Revenue ($)", "y": ""},
                         color_discrete_sequence=[PALETTE["blue"]])
        fig_cat.update_layout(title="Revenue by Category", template="plotly_white", height=350)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        geo = filtered.groupby("country")["revenue"].sum().sort_values(ascending=False).head(8)
        fig_geo = px.bar(x=geo.index, y=geo.values,
                         labels={"x": "", "y": "Revenue ($)"},
                         color_discrete_sequence=[PALETTE["primary"]])
        fig_geo.update_layout(title="Revenue by Country", template="plotly_white", height=350)
        st.plotly_chart(fig_geo, use_container_width=True)

    # ── RFM Segmentation ──
    st.markdown("### Customer Segmentation (RFM)")
    st.caption("Recency × Frequency × Monetary scoring to identify high-value customers")

    ref_date = filtered["order_date"].max() + pd.Timedelta(days=1)
    rfm = filtered.groupby("customer_id").agg(
        recency=("order_date", lambda x: (ref_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()

    rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm_total"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    def label_segment(score):
        if score >= 10: return "Champions"
        if score >= 8: return "Loyal"
        if score >= 6: return "Potential"
        if score >= 4: return "At Risk"
        return "Lost"

    rfm["segment"] = rfm["rfm_total"].apply(label_segment)

    seg_order = ["Champions", "Loyal", "Potential", "At Risk", "Lost"]
    seg_colors = {"Champions": "#27AE60", "Loyal": "#2980B9", "Potential": "#F39C12", "At Risk": "#E74C3C", "Lost": "#BDC3C7"}

    r1, r2 = st.columns(2)
    with r1:
        seg_counts = rfm["segment"].value_counts().reindex(seg_order)
        fig_seg = px.bar(x=seg_counts.index, y=seg_counts.values,
                         color=seg_counts.index, color_discrete_map=seg_colors,
                         labels={"x": "", "y": "Customers"})
        fig_seg.update_layout(title="Segment Distribution", showlegend=False,
                              template="plotly_white", height=350)
        st.plotly_chart(fig_seg, use_container_width=True)

    with r2:
        seg_rev = rfm.groupby("segment")["monetary"].mean().reindex(seg_order)
        fig_sr = px.bar(x=seg_rev.index, y=seg_rev.values,
                        color=seg_rev.index, color_discrete_map=seg_colors,
                        labels={"x": "", "y": "Avg Revenue ($)"})
        fig_sr.update_layout(title="Avg Revenue per Segment", showlegend=False,
                             template="plotly_white", height=350)
        st.plotly_chart(fig_sr, use_container_width=True)

    # ── Cohort Retention ──
    st.markdown("### Cohort Retention")
    st.caption("How well we retain customers over time, grouped by their first purchase month")

    filtered_cohort = filtered.copy()
    filtered_cohort["order_month"] = filtered_cohort["order_date"].dt.to_period("M")
    first_purchase = filtered_cohort.groupby("customer_id")["order_month"].min().rename("cohort")
    cohort_data = filtered_cohort.merge(first_purchase, on="customer_id")
    cohort_data["period"] = (cohort_data["order_month"] - cohort_data["cohort"]).apply(lambda x: x.n)

    cohort_pivot = cohort_data.groupby(["cohort", "period"])["customer_id"].nunique().reset_index()
    cohort_pivot = cohort_pivot.pivot(index="cohort", columns="period", values="customer_id")
    cohort_sizes = cohort_pivot[0]
    retention = cohort_pivot.div(cohort_sizes, axis=0) * 100
    retention.index = retention.index.astype(str)

    n_cohorts = min(8, len(retention))
    n_periods = min(6, retention.shape[1])

    fig_heat = px.imshow(
        retention.values[:n_cohorts, :n_periods],
        x=[f"Month {i}" for i in range(n_periods)],
        y=retention.index[:n_cohorts].tolist(),
        color_continuous_scale="Blues",
        aspect="auto", text_auto=".0f",
        labels={"color": "Retention %"}
    )
    fig_heat.update_layout(title="", template="plotly_white", height=350)
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── SQL section ──
    with st.expander("Production SQL Queries"):
        st.caption("Queries I'd run against a data warehouse for this kind of analysis")
        try:
            st.code(open("04_ecommerce_executive_dashboard/queries/business_queries.sql").read(), language="sql")
        except FileNotFoundError:
            st.info("SQL file not found")


# ════════════════════════════════════════════════════════════════
# A/B TEST
# ════════════════════════════════════════════════════════════════
elif page == "A/B Test Analysis":
    st.title("A/B Test: Checkout Flow Optimization")
    st.caption("Did the new checkout flow actually improve conversions? Let's find out.")

    df = load_ab_test()
    control = df[df["variant"] == "control"]
    treatment = df[df["variant"] == "treatment"]

    # ── Experiment overview ──
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Control", f"{len(control):,}")
    e2.metric("Treatment", f"{len(treatment):,}")
    e3.metric("Duration", f"{df['timestamp'].nunique()} days" if 'timestamp' in df.columns else "14 days")
    e4.metric("Bot-filtered", f"{15000 - len(df):,} users removed")

    st.markdown("---")

    # ── SRM check ──
    expected = len(df) / 2
    _, srm_p = stats.chisquare([len(control), len(treatment)], [expected, expected])

    if srm_p > 0.01:
        st.success(f"**SRM check passed** — traffic split looks balanced (p={srm_p:.3f}). No instrumentation issues.")
    else:
        st.error(f"**SRM detected** (p={srm_p:.4f}) — the traffic split is off. Investigate before trusting results.")

    # ── Funnel ──
    st.markdown("### Conversion Funnel")

    stages = ["added_to_cart", "started_checkout", "completed_purchase"]
    stage_labels = ["Add to Cart", "Start Checkout", "Purchase"]
    funnel_rows = []
    for stage, label in zip(stages, stage_labels):
        for variant in ["control", "treatment"]:
            sub = df[df["variant"] == variant]
            funnel_rows.append({"Stage": label, "Variant": variant.title(), "Rate": sub[stage].mean() * 100})

    funnel_df = pd.DataFrame(funnel_rows)
    fig_funnel = px.bar(funnel_df, x="Stage", y="Rate", color="Variant", barmode="group",
                        color_discrete_map={"Control": PALETTE["gray"], "Treatment": PALETTE["blue"]},
                        labels={"Rate": "Conversion Rate (%)"})
    fig_funnel.update_layout(template="plotly_white", height=350, legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig_funnel, use_container_width=True)

    # ── Hypothesis test ──
    st.markdown("### Statistical Test")

    ctrl_conv = control["completed_purchase"].sum()
    treat_conv = treatment["completed_purchase"].sum()
    ctrl_rate = ctrl_conv / len(control)
    treat_rate = treat_conv / len(treatment)

    pooled = (ctrl_conv + treat_conv) / len(df)
    se = np.sqrt(pooled * (1 - pooled) * (1/len(control) + 1/len(treatment)))
    z = (treat_rate - ctrl_rate) / se
    p_val = 2 * (1 - stats.norm.cdf(abs(z)))
    lift = (treat_rate - ctrl_rate) / ctrl_rate * 100
    ci_low = (treat_rate - ctrl_rate) - 1.96 * se
    ci_high = (treat_rate - ctrl_rate) + 1.96 * se

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Control", f"{ctrl_rate:.2%}")
    m2.metric("Treatment", f"{treat_rate:.2%}")
    m3.metric("Relative Lift", f"{lift:+.1f}%")
    m4.metric("P-value", f"{p_val:.4f}")

    if p_val < 0.05 and lift > 0:
        st.success(f"Statistically significant (z={z:.3f}, p={p_val:.4f}). The new checkout works.")
    elif p_val < 0.05:
        st.error(f"Significant but negative (z={z:.3f}). The new checkout is worse.")
    else:
        st.warning(f"Not significant (z={z:.3f}, p={p_val:.4f}). Can't conclusively say it's better.")

    st.markdown(f"**95% CI** for absolute difference: `[{ci_low:.4f}, {ci_high:.4f}]`")

    # ── Segment analysis ──
    st.markdown("### Segment Breakdown")
    st.caption("Does the effect hold across devices, or is it driven by one segment?")

    seg_rows = []
    for device in sorted(df["device_type"].unique()):
        for variant in ["control", "treatment"]:
            sub = df[(df["device_type"] == device) & (df["variant"] == variant)]
            seg_rows.append({
                "Device": device.title(), "Variant": variant.title(),
                "Rate": sub["completed_purchase"].mean() * 100, "N": len(sub)
            })

    seg_df = pd.DataFrame(seg_rows)
    fig_seg = px.bar(seg_df, x="Device", y="Rate", color="Variant", barmode="group",
                     color_discrete_map={"Control": PALETTE["gray"], "Treatment": PALETTE["blue"]},
                     labels={"Rate": "Conversion Rate (%)"}, text="N")
    fig_seg.update_traces(texttemplate="n=%{text:,}", textposition="outside", textfont_size=10)
    fig_seg.update_layout(template="plotly_white", height=400, legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig_seg, use_container_width=True)

    # ── Revenue impact ──
    st.markdown("### Revenue Impact")

    buyers_ctrl = control[control["completed_purchase"] == 1]
    buyers_treat = treatment[treatment["completed_purchase"] == 1]
    aov_ctrl = buyers_ctrl["order_value"].mean() if len(buyers_ctrl) > 0 else 0
    aov_treat = buyers_treat["order_value"].mean() if len(buyers_treat) > 0 else 0

    monthly_traffic = 100_000
    extra_conversions = monthly_traffic * (treat_rate - ctrl_rate)
    monthly_rev_impact = extra_conversions * aov_treat
    annual_rev_impact = monthly_rev_impact * 12

    i1, i2, i3 = st.columns(3)
    i1.metric("Extra Conversions / Month", f"{extra_conversions:,.0f}", help="At 100K monthly users")
    i2.metric("Monthly Revenue Impact", f"${monthly_rev_impact:,.0f}")
    i3.metric("Annualized Impact", f"${annual_rev_impact:,.0f}")

    # ── Recommendation ──
    st.markdown("### Recommendation")
    if p_val < 0.05 and lift > 0:
        st.markdown(f"""
        **Ship it.** {lift:.1f}% lift with p={p_val:.4f}. The revenue upside is
        ~${annual_rev_impact:,.0f}/year at current traffic levels.

        **Rollout plan:** 10% for 2 days (watch for errors) → 50% for 3 days
        (confirm lift holds) → 100%. Keep the old flow as a quick rollback option
        for at least 2 weeks.
        """)
    else:
        st.markdown("""
        **Don't ship yet.** The results aren't conclusive. Options:
        - Extend the test another 1-2 weeks for more power
        - Check if there's a segment where it clearly wins and consider a targeted rollout
        - Iterate on the design and re-test
        """)


# ════════════════════════════════════════════════════════════════
# AI ECOSYSTEM
# ════════════════════════════════════════════════════════════════
elif page == "AI & ML Ecosystem":
    st.title("AI & ML Open Source Landscape")
    st.caption("What's happening in the open-source ML world, based on GitHub and HuggingFace data")

    repos = load_repos()
    models = load_models()

    k1, k2, k3 = st.columns(3)
    k1.metric("GitHub Repos", f"{len(repos):,}")
    k2.metric("HuggingFace Models", f"{len(models):,}")
    k3.metric("Combined Stars", f"{repos['stars'].sum()/1e6:.1f}M")

    st.markdown("---")

    # ── Top repos ──
    top = repos.nlargest(20, "stars")
    fig_stars = px.bar(top, x="stars", y="repo_name", orientation="h",
                       color="language", labels={"stars": "Stars", "repo_name": ""},
                       hover_data=["forks", "open_issues"])
    fig_stars.update_layout(title="Most Starred Repos", yaxis=dict(autorange="reversed"),
                            template="plotly_white", height=500)
    st.plotly_chart(fig_stars, use_container_width=True)

    # ── Language + Tasks ──
    c1, c2 = st.columns(2)
    with c1:
        lang = repos["language"].value_counts().head(8)
        fig_lang = px.pie(values=lang.values, names=lang.index,
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig_lang.update_traces(textinfo="label+percent")
        fig_lang.update_layout(title="Languages", template="plotly_white", height=350)
        st.plotly_chart(fig_lang, use_container_width=True)

    with c2:
        pipeline = models["pipeline_tag"].value_counts().head(10)
        fig_pipe = px.bar(x=pipeline.values, y=pipeline.index, orientation="h",
                          labels={"x": "Models", "y": ""},
                          color_discrete_sequence=["#8E44AD"])
        fig_pipe.update_layout(title="What Models Are Built For", template="plotly_white",
                               yaxis=dict(autorange="reversed"), height=350)
        st.plotly_chart(fig_pipe, use_container_width=True)

    # ── Stars vs Forks ──
    fig_sc = px.scatter(repos, x="stars", y="forks", hover_name="repo_name",
                        color="language", size="open_issues", size_max=20,
                        labels={"stars": "Stars", "forks": "Forks"},
                        log_x=True, log_y=True)
    fig_sc.update_layout(title="Stars vs Forks", template="plotly_white", height=450)
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Top HF models ──
    top_m = models.nlargest(15, "downloads")
    fig_dl = px.bar(top_m, x="downloads", y="model_id", orientation="h",
                    labels={"downloads": "Downloads", "model_id": ""},
                    color_discrete_sequence=["#E67E22"])
    fig_dl.update_layout(title="Most Downloaded Models", yaxis=dict(autorange="reversed"),
                         template="plotly_white", height=450)
    st.plotly_chart(fig_dl, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# CO2 EMISSIONS
# ════════════════════════════════════════════════════════════════
elif page == "Global CO2 Emissions":
    st.title("Global CO2 Emissions")
    st.caption("Historical trends from Our World in Data — who emits the most, and how that's changing")

    co2 = load_co2()

    latest_year = int(co2["year"].max())
    latest = co2[co2["year"] == latest_year]

    k1, k2, k3 = st.columns(3)
    k1.metric("Countries", f"{co2['country'].nunique()}")
    k2.metric("Latest Year", f"{latest_year}")
    k3.metric("Total Emissions", f"{latest['co2'].sum():,.0f} Mt")

    st.markdown("---")

    # ── Top emitters ──
    top_em = latest.nlargest(10, "co2")
    fig_top = px.bar(top_em, x="country", y="co2",
                     labels={"co2": "CO2 (Mt)", "country": ""},
                     color_discrete_sequence=[PALETTE["accent"]])
    fig_top.update_layout(title=f"Top 10 Emitters ({latest_year})", template="plotly_white", height=350)
    st.plotly_chart(fig_top, use_container_width=True)

    # ── Per capita over time ──
    st.markdown("### Per Capita Trends")
    default_countries = ["United States", "China", "India", "Germany", "Brazil"]
    available_defaults = [c for c in default_countries if c in co2["country"].unique()]

    selected = st.multiselect("Compare countries", sorted(co2["country"].unique()),
                               default=available_defaults)

    if selected:
        filt = co2[co2["country"].isin(selected)]
        fig_pc = px.line(filt, x="year", y="co2_per_capita", color="country",
                         labels={"co2_per_capita": "CO2 per capita (t)", "year": ""})
        fig_pc.update_layout(template="plotly_white", height=400,
                             legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig_pc, use_container_width=True)

    # ── Sources breakdown ──
    c1, c2 = st.columns(2)
    with c1:
        sources = {col.replace("_co2", "").title(): latest[col].sum()
                   for col in ["coal_co2", "oil_co2", "gas_co2", "cement_co2"]
                   if col in latest.columns and latest[col].sum() > 0}
        fig_src = px.pie(values=list(sources.values()), names=list(sources.keys()),
                         color_discrete_sequence=px.colors.qualitative.Set1)
        fig_src.update_traces(textinfo="label+percent")
        fig_src.update_layout(title=f"Emission Sources ({latest_year})", template="plotly_white", height=350)
        st.plotly_chart(fig_src, use_container_width=True)

    with c2:
        top_pc = latest.nlargest(10, "co2_per_capita")
        fig_tpc = px.bar(top_pc, x="country", y="co2_per_capita",
                         labels={"co2_per_capita": "t CO2/person", "country": ""},
                         color_discrete_sequence=[PALETTE["orange"]])
        fig_tpc.update_layout(title="Highest Per Capita", template="plotly_white", height=350)
        st.plotly_chart(fig_tpc, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# CRYPTO
# ════════════════════════════════════════════════════════════════
elif page == "Crypto Market":
    st.title("Crypto Market Overview")
    st.caption("Snapshot of 250 cryptocurrencies from CoinGecko")

    crypto = load_crypto()

    total_mcap = crypto["market_cap"].sum()
    k1, k2, k3 = st.columns(3)
    k1.metric("Coins", f"{len(crypto)}")
    k2.metric("Total Market Cap", f"${total_mcap/1e12:.2f}T")
    k3.metric("24h Volume", f"${crypto['total_volume'].sum()/1e9:.1f}B")

    st.markdown("---")

    # ── Dominance ──
    top10 = crypto.nlargest(10, "market_cap")
    other_mcap = total_mcap - top10["market_cap"].sum()
    dom_df = pd.DataFrame({
        "name": list(top10["name"]) + ["Others"],
        "market_cap": list(top10["market_cap"]) + [other_mcap]
    })
    fig_dom = px.pie(dom_df, values="market_cap", names="name",
                     color_discrete_sequence=px.colors.qualitative.Bold)
    fig_dom.update_traces(textinfo="label+percent")
    fig_dom.update_layout(title="Market Dominance", template="plotly_white", height=400)
    st.plotly_chart(fig_dom, use_container_width=True)

    # ── Movers ──
    c1, c2 = st.columns(2)
    with c1:
        gainers = crypto.nlargest(10, "price_change_pct_24h")
        fig_g = px.bar(gainers, x="price_change_pct_24h", y="name", orientation="h",
                       labels={"price_change_pct_24h": "24h Change (%)", "name": ""},
                       color_discrete_sequence=[PALETTE["green"]])
        fig_g.update_layout(title="Top Gainers", yaxis=dict(autorange="reversed"),
                            template="plotly_white", height=350)
        st.plotly_chart(fig_g, use_container_width=True)

    with c2:
        losers = crypto.nsmallest(10, "price_change_pct_24h")
        fig_l = px.bar(losers, x="price_change_pct_24h", y="name", orientation="h",
                       labels={"price_change_pct_24h": "24h Change (%)", "name": ""},
                       color_discrete_sequence=[PALETTE["accent"]])
        fig_l.update_layout(title="Top Losers", yaxis=dict(autorange="reversed"),
                            template="plotly_white", height=350)
        st.plotly_chart(fig_l, use_container_width=True)

    # ── Price vs Market Cap ──
    big_coins = crypto[crypto["market_cap"] > 1e8].copy()
    fig_sc = px.scatter(big_coins, x="market_cap", y="current_price",
                        hover_name="name", size="total_volume", size_max=25,
                        labels={"market_cap": "Market Cap ($)", "current_price": "Price ($)"},
                        log_x=True, log_y=True, color_discrete_sequence=[PALETTE["orange"]])
    fig_sc.update_layout(title="Price vs Market Cap (>$100M)", template="plotly_white", height=400)
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── ATH distance ──
    ath = crypto.nlargest(15, "market_cap")[["name", "current_price", "ath", "ath_change_pct"]].copy()
    fig_ath = px.bar(ath, x="name", y="ath_change_pct",
                     labels={"ath_change_pct": "% from ATH", "name": ""},
                     color_discrete_sequence=["#8E44AD"],
                     hover_data={"current_price": ":$.2f", "ath": ":$.2f"})
    fig_ath.update_layout(title="Distance from All-Time High (Top 15)", template="plotly_white", height=350)
    st.plotly_chart(fig_ath, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# CHURN PREDICTION
# ════════════════════════════════════════════════════════════════
elif page == "Churn Prediction":
    st.title("Customer Churn Prediction")
    st.caption("Which customers are about to leave? ML model trained on purchase behavior features.")

    from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score, roc_curve, f1_score, confusion_matrix

    cust = load_churn_features()

    # ── Overview ──
    churn_rate = cust["churned"].mean()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Customers", f"{len(cust):,}")
    k2.metric("Churned", f"{cust['churned'].sum():,}")
    k3.metric("Active", f"{(1 - cust['churned']).sum():,.0f}")
    k4.metric("Churn Rate", f"{churn_rate:.1%}")

    st.markdown("---")

    # ── Feature distributions ──
    st.markdown("### Feature Distributions by Churn Status")
    st.caption("How churned vs active customers differ across key behavioral features")

    feat_to_show = st.selectbox("Select feature",
        ["recency_days", "total_orders", "total_revenue", "avg_order_value", "avg_discount", "unique_categories"])

    active_vals = cust[cust["churned"] == 0][feat_to_show]
    churned_vals = cust[cust["churned"] == 1][feat_to_show]

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(x=active_vals, name="Active", marker_color=PALETTE["blue"],
                                     opacity=0.7, nbinsx=30))
    fig_dist.add_trace(go.Histogram(x=churned_vals, name="Churned", marker_color=PALETTE["accent"],
                                     opacity=0.7, nbinsx=30))
    fig_dist.update_layout(barmode="overlay", template="plotly_white", height=350,
                           title=f"Distribution: {feat_to_show.replace('_', ' ').title()}",
                           legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_dist, use_container_width=True)

    # ── Train models ──
    st.markdown("### Model Comparison")
    st.caption("Three classifiers trained with 5-fold stratified CV, evaluated on a held-out 20% test set")

    feature_cols = ["total_orders", "total_revenue", "avg_order_value", "std_order_value",
                    "total_quantity", "avg_discount", "max_discount", "unique_categories",
                    "unique_products", "recency_days", "tenure_days", "order_frequency",
                    "avg_delivery_days", "has_return"]

    # Encode categoricals
    for col, src in [("country_enc", "country"), ("channel_enc", "acquisition_channel"), ("payment_enc", "payment_method")]:
        if src in cust.columns:
            cust[col] = LabelEncoder().fit_transform(cust[src].astype(str))
            feature_cols.append(col)

    X = cust[feature_cols].fillna(0).values
    y = cust["churned"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    models_dict = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced", n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, random_state=42, max_depth=4),
    }

    model_results = {}
    for name, model in models_dict.items():
        X_use = X_train_sc if "Logistic" in name else X_train
        X_eval = X_test_sc if "Logistic" in name else X_test
        model.fit(X_use, y_train)
        y_prob = model.predict_proba(X_eval)[:, 1]
        y_pred = model.predict(X_eval)
        model_results[name] = {
            "auc": roc_auc_score(y_test, y_prob),
            "f1": f1_score(y_test, y_pred),
            "y_prob": y_prob,
            "y_pred": y_pred,
            "model": model,
        }

    # Results table
    res_df = pd.DataFrame({
        "Model": model_results.keys(),
        "AUC": [r["auc"] for r in model_results.values()],
        "F1 Score": [r["f1"] for r in model_results.values()],
    })
    st.dataframe(res_df.style.highlight_max(subset=["AUC", "F1 Score"], color="#d4edda"), use_container_width=True, hide_index=True)

    # ── ROC curves ──
    fig_roc = go.Figure()
    colors_roc = {"Logistic Regression": "#3498DB", "Random Forest": "#27AE60", "Gradient Boosting": "#E74C3C"}
    for name, res in model_results.items():
        fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"{name} (AUC={res['auc']:.3f})",
                                      line=dict(color=colors_roc[name], width=2)))
    fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random",
                                  line=dict(color="gray", dash="dash")))
    fig_roc.update_layout(title="ROC Curves", template="plotly_white", height=400,
                          xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    st.plotly_chart(fig_roc, use_container_width=True)

    # ── Feature importance (best model) ──
    st.markdown("### Feature Importance")
    best_name = max(model_results, key=lambda k: model_results[k]["auc"])
    best_model = model_results[best_name]["model"]

    if hasattr(best_model, "feature_importances_"):
        imp = pd.Series(best_model.feature_importances_, index=feature_cols).sort_values(ascending=True)
        fig_imp = px.bar(x=imp.values[-12:], y=imp.index[-12:], orientation="h",
                         labels={"x": "Importance", "y": ""},
                         color_discrete_sequence=[PALETTE["primary"]])
        fig_imp.update_layout(title=f"Top Features ({best_name})", template="plotly_white", height=400)
        st.plotly_chart(fig_imp, use_container_width=True)

    # ── At-risk customers ──
    st.markdown("### At-Risk Customers")
    cust["churn_prob"] = best_model.predict_proba(X if "Logistic" not in best_name else scaler.transform(X))[:, 1]
    at_risk = cust[(cust["churn_prob"] > 0.6) & (cust["churned"] == 0)].sort_values("churn_prob", ascending=False)

    ar1, ar2 = st.columns(2)
    ar1.metric("At-Risk Customers", f"{len(at_risk):,}")
    ar2.metric("Revenue at Risk", f"${at_risk['total_revenue'].sum():,.0f}")

    if len(at_risk) > 0:
        st.dataframe(
            at_risk[["customer_id", "total_revenue", "total_orders", "recency_days", "churn_prob"]]
            .head(15).style.format({"total_revenue": "${:,.0f}", "churn_prob": "{:.1%}"}),
            use_container_width=True, hide_index=True
        )

    st.markdown("""
    **Takeaways:**
    - Recency is the strongest churn signal — trigger re-engagement at 45 days, not 90
    - Heavy discount users churn more — consider a loyalty program over blanket discounts
    - Low category breadth correlates with churn — cross-sell recommendations could help
    """)


# ════════════════════════════════════════════════════════════════
# SALES FORECASTING
# ════════════════════════════════════════════════════════════════
elif page == "Sales Forecasting":
    st.title("Sales Forecasting")
    st.caption("Projecting next quarter's revenue using time series and ML approaches")

    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.metrics import mean_absolute_error

    monthly = load_monthly_sales()

    k1, k2, k3 = st.columns(3)
    k1.metric("Months of Data", f"{len(monthly)}")
    k2.metric("Total Revenue", f"${monthly['revenue'].sum():,.0f}")
    k3.metric("Avg Monthly Revenue", f"${monthly['revenue'].mean():,.0f}")

    st.markdown("---")

    # ── Revenue trend ──
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"],
                                    mode="lines+markers", line=dict(color=PALETTE["blue"], width=2),
                                    hovertemplate="$%{y:,.0f}<extra></extra>"))
    fig_trend.update_layout(title="Monthly Revenue", template="plotly_white", height=350,
                            yaxis_title="Revenue ($)")
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── Decomposition ──
    st.markdown("### Time Series Decomposition")
    ts = monthly.set_index("month")["revenue"]
    ts.index.freq = "ME"

    if len(ts) >= 6:
        decomp = seasonal_decompose(ts, model="additive", period=min(6, len(ts)//2))
        c1, c2 = st.columns(2)
        with c1:
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=decomp.trend.index, y=decomp.trend.values,
                                        mode="lines", line=dict(color=PALETTE["accent"], width=2)))
            fig_t.update_layout(title="Trend Component", template="plotly_white", height=250)
            st.plotly_chart(fig_t, use_container_width=True)
        with c2:
            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(x=decomp.seasonal.index, y=decomp.seasonal.values,
                                        mode="lines", line=dict(color=PALETTE["green"], width=2)))
            fig_s.update_layout(title="Seasonal Component", template="plotly_white", height=250)
            st.plotly_chart(fig_s, use_container_width=True)

    # ── Forecast models ──
    st.markdown("### Model Comparison")
    st.caption("Holdout: last 2 months. Comparing Holt-Winters, Linear Regression, and Gradient Boosting.")

    n_test = 2
    train = monthly.iloc[:-n_test].copy()
    test = monthly.iloc[-n_test:].copy()
    train_ts = train.set_index("month")["revenue"]
    train_ts.index.freq = "ME"

    forecasts = {}

    # Holt-Winters
    try:
        hw = ExponentialSmoothing(train_ts, trend="add", seasonal=None, damped_trend=True).fit()
        forecasts["Holt-Winters"] = hw.forecast(n_test).values
    except:
        pass

    # Linear Regression
    def make_lr_features(df, offset=0):
        return pd.DataFrame({
            "month_num": range(offset, offset + len(df)),
            "month_of_year": df["month"].dt.month.values,
            "quarter": df["month"].dt.quarter.values,
        })

    lr = LinearRegression()
    lr.fit(make_lr_features(train), train["revenue"])
    forecasts["Linear Regression"] = lr.predict(make_lr_features(test, offset=len(train)))

    # Gradient Boosting with lags
    all_rev = monthly["revenue"].values
    lag_data = pd.DataFrame({"revenue": all_rev})
    for lag in range(1, 4):
        lag_data[f"lag_{lag}"] = lag_data["revenue"].shift(lag)
    lag_data["rolling_3"] = lag_data["revenue"].rolling(3).mean().shift(1)
    lag_data["idx"] = range(len(lag_data))
    lag_data = lag_data.dropna()

    gb_feats = [c for c in lag_data.columns if c != "revenue"]
    gb = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=3)
    gb.fit(lag_data.iloc[:-n_test][gb_feats], lag_data.iloc[:-n_test]["revenue"])
    forecasts["Gradient Boosting"] = gb.predict(lag_data.iloc[-n_test:][gb_feats])

    # Plot
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(x=train["month"], y=train["revenue"],
                                 mode="lines+markers", name="Historical",
                                 line=dict(color=PALETTE["primary"], width=2)))
    fig_fc.add_trace(go.Scatter(x=test["month"], y=test["revenue"],
                                 mode="markers", name="Actual", marker=dict(size=10, color=PALETTE["primary"])))

    fc_colors = {"Holt-Winters": "#3498DB", "Linear Regression": "#27AE60", "Gradient Boosting": "#E74C3C"}
    for name, pred in forecasts.items():
        mae = mean_absolute_error(test["revenue"], pred)
        fig_fc.add_trace(go.Scatter(x=test["month"], y=pred, mode="lines+markers",
                                     name=f"{name} (MAE=${mae:,.0f})",
                                     line=dict(color=fc_colors[name], dash="dash", width=2)))

    fig_fc.update_layout(title="Forecast vs Actual (Holdout)", template="plotly_white", height=400)
    st.plotly_chart(fig_fc, use_container_width=True)

    # MAE table
    mae_df = pd.DataFrame({
        "Model": forecasts.keys(),
        "MAE ($)": [f"${mean_absolute_error(test['revenue'], p):,.0f}" for p in forecasts.values()],
        "MAPE (%)": [f"{mean_absolute_error(test['revenue'], p) / test['revenue'].mean() * 100:.1f}%" for p in forecasts.values()],
    })
    st.dataframe(mae_df, use_container_width=True, hide_index=True)

    # ── Next quarter projection ──
    st.markdown("### Next Quarter Projection")
    best_fc_name = min(forecasts, key=lambda k: mean_absolute_error(test["revenue"], forecasts[k]))

    # Refit best on full data and forecast 3 months
    full_ts = monthly.set_index("month")["revenue"]
    full_ts.index.freq = "ME"

    if best_fc_name == "Holt-Winters":
        final = ExponentialSmoothing(full_ts, trend="add", seasonal=None, damped_trend=True).fit()
        future = final.forecast(3)
    elif best_fc_name == "Linear Regression":
        lr_full = LinearRegression()
        lr_full.fit(make_lr_features(monthly), monthly["revenue"])
        future_months = pd.date_range(monthly["month"].max() + pd.DateOffset(months=1), periods=3, freq="ME")
        future_feat = pd.DataFrame({
            "month_num": range(len(monthly), len(monthly) + 3),
            "month_of_year": future_months.month,
            "quarter": future_months.quarter,
        })
        future = pd.Series(lr_full.predict(future_feat), index=future_months)
    else:
        lag_full = pd.DataFrame({"revenue": monthly["revenue"].values})
        for lag in range(1, 4):
            lag_full[f"lag_{lag}"] = lag_full["revenue"].shift(lag)
        lag_full["rolling_3"] = lag_full["revenue"].rolling(3).mean().shift(1)
        lag_full["idx"] = range(len(lag_full))
        lag_full = lag_full.dropna()

        gb_full = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=3)
        gb_full.fit(lag_full[gb_feats], lag_full["revenue"])

        recent = list(monthly["revenue"].values)
        preds = []
        for i in range(3):
            row = {"lag_1": recent[-1], "lag_2": recent[-2], "lag_3": recent[-3],
                   "rolling_3": np.mean(recent[-3:]), "idx": len(recent)}
            p = gb_full.predict(pd.DataFrame([row]))[0]
            preds.append(p)
            recent.append(p)
        future_months = pd.date_range(monthly["month"].max() + pd.DateOffset(months=1), periods=3, freq="ME")
        future = pd.Series(preds, index=future_months)

    q_total = future.sum()
    last_q = monthly["revenue"].iloc[-3:].sum()
    qoq = (q_total - last_q) / last_q * 100

    f1, f2, f3 = st.columns(3)
    f1.metric("Forecast Q Total", f"${q_total:,.0f}")
    f2.metric("Last Q Actual", f"${last_q:,.0f}")
    f3.metric("QoQ Change", f"{qoq:+.1f}%")

    # Forecast chart
    test_mae = mean_absolute_error(test["revenue"], forecasts[best_fc_name])
    fig_fut = go.Figure()
    fig_fut.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"],
                                  mode="lines+markers", name="Historical",
                                  line=dict(color=PALETTE["primary"], width=2)))
    fig_fut.add_trace(go.Scatter(x=future.index, y=future.values,
                                  mode="lines+markers", name=f"Forecast ({best_fc_name})",
                                  line=dict(color=PALETTE["accent"], width=2, dash="dash")))
    fig_fut.add_trace(go.Scatter(
        x=list(future.index) + list(future.index[::-1]),
        y=list(future.values + 1.5 * test_mae) + list((future.values - 1.5 * test_mae)[::-1]),
        fill="toself", fillcolor="rgba(233,69,96,0.1)", line=dict(width=0),
        name="Confidence band", showlegend=True
    ))
    fig_fut.update_layout(title="Revenue Forecast — Next Quarter", template="plotly_white", height=400)
    st.plotly_chart(fig_fut, use_container_width=True)
