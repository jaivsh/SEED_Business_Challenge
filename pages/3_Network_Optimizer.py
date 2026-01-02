# pages/3_Network_Optimizer.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Network Optimizer")
st.title("The Network Optimizer: Eliminating Inefficiency")

@st.cache_data
def load_data():
    return pd.read_parquet("urbaneats_master_dataset.parquet")

df = load_data()

st.subheader("The Anatomy of a Late Delivery: Where is Time Lost?")
avg_dispatch_lag = df['dispatch_lag_min'].mean()
avg_pickup_lag = df['restaurant_wait_min'].mean()

fig_funnel = go.Figure(go.Funnel(y=["Order Placed", "Restaurant Confirmed", "Driver Assigned", "Order Picked Up", "Delivered On-Time"], x=[100, 100, 100, 100, df['is_on_time'].mean()*100], textinfo="value+percent initial", marker={"color": ["#636EFA", "#636EFA", "#EF553B", "#636EFA", "#00CC96"]}, connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}}))
fig_funnel.add_annotation(x=0.65, y=1.5, text=f"Avg Dispatch Lag:<br><b>{avg_dispatch_lag:.1f} min</b>", showarrow=False, font=dict(size=14, color="white"))
fig_funnel.add_annotation(x=0.65, y=2.5, text=f"Avg Restaurant Wait:<br><b>{avg_pickup_lag:.1f} min</b>", showarrow=False, font=dict(size=14, color="white"))
fig_funnel.update_layout(title="Delivery Lifecycle Funnel - Dispatch Lag is a Key Bottleneck", template="plotly_dark")
st.plotly_chart(fig_funnel, use_container_width=True)

st.subheader("Driver Idle Time Hotspots")
df['hour_of_day'] = df['order_placed_at'].dt.hour
df['day_of_week'] = df['order_placed_at'].dt.day_name()
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
idle_heatmap = df.pivot_table(values='dispatch_lag_min', index='day_of_week', columns='hour_of_day', aggfunc='mean').reindex(days_order)
fig_heatmap = go.Figure(data=go.Heatmap(z=idle_heatmap.values, x=idle_heatmap.columns, y=idle_heatmap.index, colorscale='Reds'))
fig_heatmap.update_layout(title="Average Dispatch Lag (Idle Time) by Hour and Day", xaxis_title="Hour of Day", template="plotly_dark")
st.plotly_chart(fig_heatmap, use_container_width=True)