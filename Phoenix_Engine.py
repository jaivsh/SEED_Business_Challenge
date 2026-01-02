# Phoenix_Engine.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Phoenix Engine - Command Center",
    layout="wide"
)

# --- SIDEBAR BRANDING ---
st.sidebar.title("Team Second Order")
st.sidebar.markdown("---")

@st.cache_data
def load_data():
    try:
        df_master = pd.read_parquet("urbaneats_master_dataset.parquet")
        df_financials = pd.read_parquet("urbaneats_financial_summary.parquet")
        return df_master, df_financials
    except FileNotFoundError:
        st.error("Master or financial dataset not found. Please run `1_data_ingestion_and_preparation.py` first.")
        return None, None

df, df_financials = load_data()

if df is None:
    st.stop()

st.title("The Phoenix Engine: UrbanEats Command Center")
st.markdown("A real-time, interactive digital twin for diagnosing the crisis and engineering the turnaround.")

st.subheader("Crisis & Turnaround Scorecard")
annual_revenue_est = df['platform_revenue'].sum() * (12/8)
annual_fixed_cost = df_financials['total_fixed_cost'].sum() * (12/8)
annual_loss_est = df['gross_margin'].sum() * (12/8) - annual_fixed_cost

col1, col2, col3, col4 = st.columns(4)
col1.metric("Annual Revenue", f"${annual_revenue_est/1_000_000:.2f}M", "60% YoY")
col2.metric("Annual Operating Loss", f"${abs(annual_loss_est)/1_000_000:.2f}M", f"${df['gross_margin'].mean():.2f} per delivery", delta_color="inverse")
col3.metric("On-Time Rate", f"{df['is_on_time'].mean():.1%}", f"Target: 95%", delta_color="inverse")
col4.metric("Failure Rate", f"{(df['delivery_status'] == 'failed').mean():.1%}", "Target: <3%", delta_color="inverse")

st.subheader("The Bleeding: Cumulative Margin Over 8 Months")
df['month'] = df['order_placed_at'].dt.to_period('M').astype(str)
monthly_margin = df.groupby('month')['gross_margin'].sum().reset_index()
monthly_margin['cumulative_margin'] = monthly_margin['gross_margin'].cumsum()

fig_cum_margin = go.Figure()
fig_cum_margin.add_trace(go.Bar(x=monthly_margin['month'], y=monthly_margin['gross_margin'], name='Monthly Gross Margin', marker_color='rgba(214, 39, 40, 0.6)'))
fig_cum_margin.add_trace(go.Scatter(x=monthly_margin['month'], y=monthly_margin['cumulative_margin'], name='Cumulative Gross Margin', mode='lines+markers', line=dict(color='white', width=3), yaxis='y2'))
fig_cum_margin.update_layout(title="Monthly margin shows consistent losses, cumulative debt deepens", template="plotly_dark", yaxis=dict(title='Monthly Gross Margin ($)'), yaxis2=dict(title='Cumulative Gross Margin ($)', overlaying='y', side='right'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_cum_margin, use_container_width=True)

st.subheader("National Profitability Footprint")
city_perf = df.groupby('city_name').agg(
    total_margin=('gross_margin', 'sum'),
    lat=('customer_latitude', 'mean'),
    lon=('customer_longitude', 'mean'),
    num_deliveries=('delivery_id', 'count')
).reset_index()

city_perf['color'] = city_perf['total_margin'].apply(lambda x: 'green' if x > 0 else 'red')
city_perf['size'] = abs(city_perf['total_margin']) / 100

fig_map = px.scatter_mapbox(
    city_perf,
    lat="lat",
    lon="lon",
    size="size",
    color="color",
    hover_name="city_name",
    hover_data={"total_margin": ":,.0f", "num_deliveries": True, "size": False, "color": False},
    mapbox_style="carto-darkmatter",
    zoom=3.5,
    title="Red markets represent financial drain; Green markets are the blueprint for success"
)
fig_map.update_layout(showlegend=False)
st.plotly_chart(fig_map, use_container_width=True)

st.sidebar.success("Phoenix Engine is online. Select a module to begin the turnaround.")