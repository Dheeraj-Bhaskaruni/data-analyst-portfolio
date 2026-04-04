import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime

st.set_page_config(page_title="Dheeraj Bhaskaruni | Data Analyst Portfolio", layout="wide", page_icon="📊")

# --- sidebar nav ---
st.sidebar.title("Portfolio")
page = st.sidebar.radio("", [
    "Home",
    "E-Commerce Dashboard",
    "A/B Test Analysis",
    "AI Ecosystem",
    "Global CO2 Emissions",
    "Crypto Market",
])

# ============================================================
# HOME
# ============================================================
if page == "Home":
    st.title("Dheeraj Bhaskaruni")
    st.subheader("Data Analyst")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Projects", "5")
    col2.metric("Datasets Analyzed", "50K+ rows")
    col3.metric("Skills", "Python · SQL · Statistics")

    st.markdown("""
    ### About
    Data analyst with hands-on experience in business intelligence, experimentation,
    and data storytelling. This portfolio contains end-to-end projects using real-world
    data — from executive dashboards to A/B test analysis.

    ### Projects

    **E-Commerce Executive Dashboard** — KPI tracking, RFM segmentation, cohort retention, SQL queries
    **A/B Test Checkout Optimization** — Hypothesis testing, power analysis, funnel analysis, ship recommendation
    **AI Ecosystem Analysis** — GitHub + HuggingFace data, framework trends, model landscape
    **Global CO2 Emissions** — OWID data, per-capita trends, regional comparisons
    **Crypto Market Analysis** — CoinGecko data, market dominance, volatility tiers

    ### Tools & Stack
    Python · Pandas · NumPy · SQL · Plotly · Matplotlib · Seaborn · Scipy · Scikit-learn · Jupyter · Streamlit
    """)

# ============================================================
# E-COMMERCE EXECUTIVE DASHBOARD
# ============================================================
elif page == "E-Commerce Dashboard":
    st.title("E-Commerce Executive Dashboard")
    st.caption("KPI tracking, segmentation, and cohort analysis on 6,800+ orders")

    orders = pd.read_csv("04_ecommerce_executive_dashboard/data/orders.csv", parse_dates=["order_date"])
    customers = pd.read_csv("04_ecommerce_executive_dashboard/data/customers.csv")

    orders["revenue"] = orders["quantity"] * orders["unit_price"] * (1 - orders["discount_pct"] / 100)
    active = orders[orders["order_status"] != "Cancelled"].copy()

    # --- KPI row ---
    total_rev = active["revenue"].sum()
    total_orders = active["order_id"].nunique()
    aov = total_rev / total_orders
    unique_customers = active["customer_id"].nunique()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Revenue", f"${total_rev:,.0f}")
    k2.metric("Orders", f"{total_orders:,}")
    k3.metric("Avg Order Value", f"${aov:,.2f}")
    k4.metric("Unique Customers", f"{unique_customers:,}")

    st.markdown("---")

    # --- Revenue over time ---
    monthly = active.set_index("order_date").resample("M")["revenue"].sum().reset_index()
    monthly.columns = ["month", "revenue"]

    fig_rev = px.area(monthly, x="month", y="revenue",
                      title="Monthly Revenue Trend",
                      labels={"revenue": "Revenue ($)", "month": ""},
                      color_discrete_sequence=["#2C3E50"])
    fig_rev.update_layout(hovermode="x unified")
    st.plotly_chart(fig_rev, use_container_width=True)

    # --- Two columns: category + payment ---
    c1, c2 = st.columns(2)

    with c1:
        cat_rev = active.groupby("category")["revenue"].sum().sort_values(ascending=True)
        fig_cat = px.bar(x=cat_rev.values, y=cat_rev.index, orientation="h",
                         title="Revenue by Category",
                         labels={"x": "Revenue ($)", "y": ""},
                         color_discrete_sequence=["#2980B9"])
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        pay = active.groupby("payment_method")["order_id"].nunique().sort_values(ascending=False)
        fig_pay = px.pie(values=pay.values, names=pay.index,
                         title="Payment Methods",
                         color_discrete_sequence=px.colors.qualitative.Set2)
        fig_pay.update_traces(textinfo="label+percent")
        st.plotly_chart(fig_pay, use_container_width=True)

    # --- RFM Segmentation ---
    st.subheader("RFM Customer Segmentation")
    ref_date = active["order_date"].max() + pd.Timedelta(days=1)
    rfm = active.groupby("customer_id").agg(
        recency=("order_date", lambda x: (ref_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()

    rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    def segment(row):
        if row["rfm_score"] >= 10:
            return "Champions"
        elif row["rfm_score"] >= 8:
            return "Loyal"
        elif row["rfm_score"] >= 6:
            return "Potential"
        elif row["rfm_score"] >= 4:
            return "At Risk"
        else:
            return "Lost"

    rfm["segment"] = rfm.apply(segment, axis=1)
    seg_counts = rfm["segment"].value_counts()

    fig_rfm = px.bar(x=seg_counts.index, y=seg_counts.values,
                     title="Customer Segments",
                     labels={"x": "Segment", "y": "Customers"},
                     color=seg_counts.index,
                     color_discrete_sequence=["#27AE60", "#2980B9", "#F39C12", "#E74C3C", "#95A5A6"])
    st.plotly_chart(fig_rfm, use_container_width=True)

    # --- Cohort retention ---
    st.subheader("Cohort Retention")
    active["order_month"] = active["order_date"].dt.to_period("M")
    first_purchase = active.groupby("customer_id")["order_month"].min().rename("cohort")
    cohort_data = active.merge(first_purchase, on="customer_id")
    cohort_data["period"] = (cohort_data["order_month"] - cohort_data["cohort"]).apply(lambda x: x.n)

    cohort_table = cohort_data.groupby(["cohort", "period"])["customer_id"].nunique().reset_index()
    cohort_table = cohort_table.pivot(index="cohort", columns="period", values="customer_id")
    cohort_sizes = cohort_table[0]
    retention = cohort_table.div(cohort_sizes, axis=0) * 100

    retention.index = retention.index.astype(str)
    fig_heat = px.imshow(retention.values[:8, :6],
                         x=[f"Month {i}" for i in range(min(6, retention.shape[1]))],
                         y=retention.index[:8].tolist(),
                         color_continuous_scale="YlOrRd_r",
                         title="Cohort Retention (%)",
                         aspect="auto",
                         text_auto=".0f")
    st.plotly_chart(fig_heat, use_container_width=True)

    # --- Geographic ---
    geo = active.groupby("country")["revenue"].sum().sort_values(ascending=False).head(10)
    fig_geo = px.bar(x=geo.index, y=geo.values,
                     title="Revenue by Country (Top 10)",
                     labels={"x": "Country", "y": "Revenue ($)"},
                     color_discrete_sequence=["#2C3E50"])
    st.plotly_chart(fig_geo, use_container_width=True)

    # --- SQL section ---
    with st.expander("SQL Queries Used"):
        try:
            sql_text = open("04_ecommerce_executive_dashboard/queries/business_queries.sql").read()
            st.code(sql_text, language="sql")
        except FileNotFoundError:
            st.info("SQL file not found")


# ============================================================
# A/B TEST ANALYSIS
# ============================================================
elif page == "A/B Test Analysis":
    st.title("A/B Test: Checkout Flow Optimization")
    st.caption("Statistical analysis of a checkout redesign experiment (15K users)")

    df = pd.read_csv("05_ab_test_checkout_optimization/data/ab_test_checkout.csv")
    df = df[df["session_duration_sec"] >= 5]  # exclude bots

    control = df[df["variant"] == "control"]
    treatment = df[df["variant"] == "treatment"]

    # --- Sample sizes ---
    st.subheader("Experiment Overview")
    e1, e2, e3 = st.columns(3)
    e1.metric("Control Users", f"{len(control):,}")
    e2.metric("Treatment Users", f"{len(treatment):,}")
    e3.metric("Total Users", f"{len(df):,}")

    # --- SRM check ---
    st.subheader("Sample Ratio Mismatch (SRM) Check")
    expected = len(df) / 2
    chi2_stat, srm_p = stats.chisquare([len(control), len(treatment)], [expected, expected])
    srm_pass = srm_p > 0.01

    if srm_pass:
        st.success(f"SRM check passed (p={srm_p:.4f}). Traffic split is balanced.")
    else:
        st.error(f"SRM detected (p={srm_p:.4f}). Traffic split is imbalanced.")

    # --- Funnel comparison ---
    st.subheader("Conversion Funnel")

    funnel_stages = ["added_to_cart", "started_checkout", "completed_purchase"]
    funnel_data = []
    for stage in funnel_stages:
        for variant in ["control", "treatment"]:
            subset = df[df["variant"] == variant]
            rate = subset[stage].mean() * 100
            funnel_data.append({"stage": stage.replace("_", " ").title(), "variant": variant, "rate": rate})

    funnel_df = pd.DataFrame(funnel_data)
    fig_funnel = px.bar(funnel_df, x="stage", y="rate", color="variant",
                        barmode="group", title="Funnel Conversion Rates (%)",
                        labels={"rate": "Conversion Rate (%)", "stage": ""},
                        color_discrete_map={"control": "#95A5A6", "treatment": "#2980B9"})
    st.plotly_chart(fig_funnel, use_container_width=True)

    # --- Primary metric: purchase rate ---
    st.subheader("Primary Metric: Purchase Conversion Rate")

    ctrl_purchases = control["completed_purchase"].sum()
    treat_purchases = treatment["completed_purchase"].sum()
    ctrl_rate = ctrl_purchases / len(control)
    treat_rate = treat_purchases / len(treatment)

    pooled_rate = (ctrl_purchases + treat_purchases) / len(df)
    se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1/len(control) + 1/len(treatment)))
    z_stat = (treat_rate - ctrl_rate) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    lift = (treat_rate - ctrl_rate) / ctrl_rate * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Control Rate", f"{ctrl_rate:.2%}")
    m2.metric("Treatment Rate", f"{treat_rate:.2%}")
    m3.metric("Lift", f"{lift:+.1f}%")
    m4.metric("P-value", f"{p_value:.4f}")

    if p_value < 0.05:
        st.success(f"Statistically significant at α=0.05 (z={z_stat:.3f}, p={p_value:.4f})")
    else:
        st.warning(f"Not statistically significant at α=0.05 (z={z_stat:.3f}, p={p_value:.4f})")

    # --- Confidence interval ---
    ci_low = (treat_rate - ctrl_rate) - 1.96 * se
    ci_high = (treat_rate - ctrl_rate) + 1.96 * se
    st.info(f"95% CI for difference: [{ci_low:.4f}, {ci_high:.4f}]")

    # --- Segment analysis ---
    st.subheader("Results by Device Type")
    segments = []
    for device in df["device_type"].unique():
        for variant in ["control", "treatment"]:
            sub = df[(df["device_type"] == device) & (df["variant"] == variant)]
            segments.append({
                "device": device,
                "variant": variant,
                "conversion_rate": sub["completed_purchase"].mean() * 100,
                "n": len(sub)
            })

    seg_df = pd.DataFrame(segments)
    fig_seg = px.bar(seg_df, x="device", y="conversion_rate", color="variant",
                     barmode="group", title="Conversion Rate by Device",
                     labels={"conversion_rate": "Conversion Rate (%)", "device": ""},
                     color_discrete_map={"control": "#95A5A6", "treatment": "#2980B9"})
    st.plotly_chart(fig_seg, use_container_width=True)

    # --- Revenue impact ---
    st.subheader("Revenue Impact Estimate")
    purchasers_ctrl = control[control["completed_purchase"] == 1]
    purchasers_treat = treatment[treatment["completed_purchase"] == 1]
    avg_order_ctrl = purchasers_ctrl["order_value"].mean() if len(purchasers_ctrl) > 0 else 0
    avg_order_treat = purchasers_treat["order_value"].mean() if len(purchasers_treat) > 0 else 0

    monthly_traffic = 100000  # assumed
    extra_conversions = monthly_traffic * (treat_rate - ctrl_rate)
    monthly_impact = extra_conversions * avg_order_treat

    r1, r2 = st.columns(2)
    r1.metric("Avg Order Value (Control)", f"${avg_order_ctrl:.2f}")
    r2.metric("Avg Order Value (Treatment)", f"${avg_order_treat:.2f}")

    st.metric("Estimated Monthly Revenue Impact (at 100K users/mo)", f"${monthly_impact:,.0f}")

    # --- Recommendation ---
    st.subheader("Recommendation")
    if p_value < 0.05 and lift > 0:
        st.markdown(f"""
        **Ship it.** The new checkout flow shows a **{lift:.1f}%** lift in conversion
        with statistical significance (p={p_value:.4f}). Estimated monthly revenue
        impact: **${monthly_impact:,.0f}** at 100K monthly users.

        Suggested rollout: 10% → 25% → 50% → 100% over 2 weeks, monitoring for regressions.
        """)
    else:
        st.markdown("**Hold.** Results are not statistically significant. Consider extending the experiment or testing a different variant.")


# ============================================================
# AI ECOSYSTEM
# ============================================================
elif page == "AI Ecosystem":
    st.title("AI & ML Ecosystem Analysis")
    st.caption("Trends across 467 GitHub repos and 200 HuggingFace models")

    repos = pd.read_csv("01_ai_ecosystem_analysis/data/github_ai_repos.csv")
    models = pd.read_csv("01_ai_ecosystem_analysis/data/huggingface_models.csv")

    k1, k2, k3 = st.columns(3)
    k1.metric("GitHub Repos", f"{len(repos):,}")
    k2.metric("HuggingFace Models", f"{len(models):,}")
    k3.metric("Total Stars", f"{repos['stars'].sum():,.0f}")

    # --- Top repos by stars ---
    top = repos.nlargest(15, "stars")
    fig_stars = px.bar(top, x="stars", y="repo_name", orientation="h",
                       title="Top 15 Repos by Stars",
                       labels={"stars": "Stars", "repo_name": ""},
                       color_discrete_sequence=["#2C3E50"])
    fig_stars.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_stars, use_container_width=True)

    # --- Language distribution ---
    c1, c2 = st.columns(2)
    with c1:
        lang = repos["language"].value_counts().head(10)
        fig_lang = px.pie(values=lang.values, names=lang.index,
                          title="Top Languages",
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig_lang.update_traces(textinfo="label+percent")
        st.plotly_chart(fig_lang, use_container_width=True)

    with c2:
        pipeline = models["pipeline_tag"].value_counts().head(10)
        fig_pipe = px.bar(x=pipeline.values, y=pipeline.index, orientation="h",
                          title="Top Model Tasks (HuggingFace)",
                          labels={"x": "Count", "y": ""},
                          color_discrete_sequence=["#8E44AD"])
        st.plotly_chart(fig_pipe, use_container_width=True)

    # --- Stars vs Forks scatter ---
    fig_scatter = px.scatter(repos, x="stars", y="forks", hover_name="repo_name",
                             color="language", size="open_issues",
                             title="Stars vs Forks (sized by open issues)",
                             labels={"stars": "Stars", "forks": "Forks"},
                             log_x=True, log_y=True)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- HuggingFace downloads ---
    top_models = models.nlargest(15, "downloads")
    fig_dl = px.bar(top_models, x="downloads", y="model_id", orientation="h",
                    title="Top 15 Models by Downloads",
                    labels={"downloads": "Downloads", "model_id": ""},
                    color_discrete_sequence=["#E67E22"])
    fig_dl.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_dl, use_container_width=True)


# ============================================================
# CO2 EMISSIONS
# ============================================================
elif page == "Global CO2 Emissions":
    st.title("Global CO2 Emissions Analysis")
    st.caption("Historical trends from Our World in Data")

    co2 = pd.read_csv("02_global_co2_analysis/data/owid_co2_data.csv")
    co2 = co2[co2["iso_code"].notna() & (co2["iso_code"] != "")]

    k1, k2, k3 = st.columns(3)
    k1.metric("Countries", f"{co2['country'].nunique()}")
    k2.metric("Year Range", f"{co2['year'].min()} - {co2['year'].max()}")
    k3.metric("Data Points", f"{len(co2):,}")

    # --- Top emitters ---
    latest = co2[co2["year"] == co2["year"].max()]
    top_emitters = latest.nlargest(10, "co2")

    fig_top = px.bar(top_emitters, x="country", y="co2",
                     title=f"Top 10 CO2 Emitters ({co2['year'].max()})",
                     labels={"co2": "CO2 (Mt)", "country": ""},
                     color_discrete_sequence=["#E74C3C"])
    st.plotly_chart(fig_top, use_container_width=True)

    # --- Per capita comparison ---
    st.subheader("Per Capita Emissions")
    countries_select = st.multiselect("Select countries to compare",
                                       co2["country"].unique().tolist(),
                                       default=["United States", "China", "India", "Germany", "Brazil"])

    if countries_select:
        filtered = co2[co2["country"].isin(countries_select)]
        fig_pc = px.line(filtered, x="year", y="co2_per_capita", color="country",
                         title="CO2 Per Capita Over Time",
                         labels={"co2_per_capita": "CO2 per capita (t)", "year": ""})
        st.plotly_chart(fig_pc, use_container_width=True)

    # --- Emission sources ---
    c1, c2 = st.columns(2)
    with c1:
        source_cols = ["coal_co2", "oil_co2", "gas_co2", "cement_co2"]
        available = [c for c in source_cols if c in latest.columns]
        if available:
            global_sources = latest[available].sum()
            fig_src = px.pie(values=global_sources.values,
                             names=[s.replace("_co2", "").title() for s in global_sources.index],
                             title="Emissions by Source (Latest Year)",
                             color_discrete_sequence=px.colors.qualitative.Set1)
            fig_src.update_traces(textinfo="label+percent")
            st.plotly_chart(fig_src, use_container_width=True)

    with c2:
        top_pc = latest.nlargest(10, "co2_per_capita")
        fig_tpc = px.bar(top_pc, x="country", y="co2_per_capita",
                         title="Highest Per Capita Emissions",
                         labels={"co2_per_capita": "CO2 per capita (t)", "country": ""},
                         color_discrete_sequence=["#F39C12"])
        st.plotly_chart(fig_tpc, use_container_width=True)


# ============================================================
# CRYPTO MARKET
# ============================================================
elif page == "Crypto Market":
    st.title("Cryptocurrency Market Analysis")
    st.caption("Market data for 250 cryptocurrencies from CoinGecko")

    crypto = pd.read_csv("03_crypto_market_analysis/data/crypto_market.csv")

    total_mcap = crypto["market_cap"].sum()
    k1, k2, k3 = st.columns(3)
    k1.metric("Coins Tracked", f"{len(crypto):,}")
    k2.metric("Total Market Cap", f"${total_mcap/1e12:.2f}T")
    k3.metric("24h Volume", f"${crypto['total_volume'].sum()/1e9:.1f}B")

    # --- Market dominance ---
    top10 = crypto.nlargest(10, "market_cap")
    fig_dom = px.pie(top10, values="market_cap", names="name",
                     title="Market Cap Dominance (Top 10)",
                     color_discrete_sequence=px.colors.qualitative.Bold)
    fig_dom.update_traces(textinfo="label+percent")
    st.plotly_chart(fig_dom, use_container_width=True)

    # --- Price vs Market Cap ---
    fig_scatter = px.scatter(crypto[crypto["market_cap"] > 1e8],
                             x="market_cap", y="current_price",
                             hover_name="name", size="total_volume",
                             title="Price vs Market Cap (coins > $100M mcap)",
                             labels={"market_cap": "Market Cap ($)", "current_price": "Price ($)"},
                             log_x=True, log_y=True,
                             color_discrete_sequence=["#F39C12"])
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- 24h price changes ---
    c1, c2 = st.columns(2)
    with c1:
        gainers = crypto.nlargest(10, "price_change_pct_24h")
        fig_gain = px.bar(gainers, x="price_change_pct_24h", y="name", orientation="h",
                          title="Top 10 Gainers (24h)",
                          labels={"price_change_pct_24h": "Change (%)", "name": ""},
                          color_discrete_sequence=["#27AE60"])
        fig_gain.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_gain, use_container_width=True)

    with c2:
        losers = crypto.nsmallest(10, "price_change_pct_24h")
        fig_lose = px.bar(losers, x="price_change_pct_24h", y="name", orientation="h",
                          title="Top 10 Losers (24h)",
                          labels={"price_change_pct_24h": "Change (%)", "name": ""},
                          color_discrete_sequence=["#E74C3C"])
        fig_lose.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_lose, use_container_width=True)

    # --- ATH distance ---
    crypto["ath_distance"] = crypto["ath_change_pct"]
    ath_data = crypto.nlargest(15, "market_cap")[["name", "current_price", "ath", "ath_distance"]]
    fig_ath = px.bar(ath_data, x="name", y="ath_distance",
                     title="Distance from All-Time High (Top 15 by Market Cap)",
                     labels={"ath_distance": "% from ATH", "name": ""},
                     color_discrete_sequence=["#8E44AD"])
    st.plotly_chart(fig_ath, use_container_width=True)


# --- footer ---
st.markdown("---")
st.markdown("Built by Dheeraj Bhaskaruni · [GitHub](https://github.com/dheeraj-bhaskaruni)")
