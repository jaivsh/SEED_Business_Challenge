import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Margin Engine")
st.title("The Margin Engine: Deconstructing Unit Economics")

@st.cache_data
def load_data():
    return pd.read_parquet("urbaneats_master_dataset.parquet")

df = load_data()

st.subheader("The Anatomy of a -$1.80 Delivery")
st.markdown("Use the filters to see how unit economics change across different segments.")

col1, col2 = st.columns([1, 3])
with col1:
    city_filter = st.selectbox("Filter by City", ["All"] + sorted(df['city_name'].unique()))
    segment_filter = st.selectbox("Filter by Customer Segment", ["All"] + sorted(df['customer_segment'].unique()))

filtered_df = df.copy()
if city_filter != "All": filtered_df = filtered_df[filtered_df['city_name'] == city_filter]
if segment_filter != "All": filtered_df = filtered_df[filtered_df['customer_segment'] == segment_filter]

avg_revenue = filtered_df['platform_revenue'].mean()
avg_driver_pay = filtered_df['driver_total_pay'].mean()
avg_processing_fee = filtered_df['payment_processing_fee'].mean()
avg_discounts = filtered_df['discount_amount'].mean()
avg_margin = filtered_df['gross_margin'].mean()

fig_waterfall = go.Figure(go.Waterfall(name="P&L", orientation="v", measure=["relative", "relative", "relative", "relative", "total"], x=["Platform Revenue", "Driver Pay", "Processing Fees", "Discounts", "Final Gross Margin"], text=[f"${v:.2f}" for v in [avg_revenue, -avg_driver_pay, -avg_processing_fee, -avg_discounts, avg_margin]], y=[avg_revenue, -avg_driver_pay, -avg_processing_fee, -avg_discounts, avg_margin], connector={"line":{"color":"rgb(63, 63, 63)"}}, increasing={"marker":{"color":"rgba(50, 171, 96, 0.7)"}}, decreasing={"marker":{"color":"rgba(214, 39, 40, 0.7)"}}, totals={"marker":{"color":"rgba(99, 110, 250, 0.7)"}}))
fig_waterfall.update_layout(title=f"Average Delivery P&L (Avg. Margin: ${avg_margin:.2f})", template="plotly_dark")
with col2:
    st.plotly_chart(fig_waterfall, use_container_width=True)

st.subheader("Profitability Drill-Down Explorer")
dimension = st.selectbox("Analyze Margin by:", ('customer_segment', 'city_name', 'cuisine_type', 'traffic_level', 'weather_condition'))
margin_by_dim = filtered_df.groupby(dimension)['gross_margin'].mean().sort_values().reset_index()
fig_drilldown = go.Figure(go.Bar(x=margin_by_dim['gross_margin'], y=margin_by_dim[dimension], orientation='h', marker_color=margin_by_dim['gross_margin'].apply(lambda x: 'rgba(214, 39, 40, 0.7)' if x < 0 else 'rgba(50, 171, 96, 0.7)')))
fig_drilldown.update_layout(title=f"Average Gross Margin by {dimension.replace('_', ' ').title()}", xaxis_title="Average Gross Margin ($)", yaxis_title="", template="plotly_dark")
st.plotly_chart(fig_drilldown, use_container_width=True)