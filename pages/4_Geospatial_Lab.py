# pages/4_Geospatial_Lab.py
import streamlit as st
import pandas as pd
import h3
import plotly.express as px
import json

st.set_page_config(layout="wide", page_title="Geospatial Lab")
st.title("The Geospatial Lab: The Hex-Grid Scalpel")
st.markdown("Using a 2D Choropleth map for a stable and clear view of hyper-local profitability.")

@st.cache_data
def load_data():
    df = pd.read_parquet("urbaneats_master_dataset.parquet")
    df['h3_index'] = df.apply(
        lambda row: h3.latlng_to_cell(row['customer_latitude'], row['customer_longitude'], 8) 
        if pd.notna(row['customer_latitude']) and pd.notna(row['customer_longitude']) else None, 
        axis=1
    )
    df.dropna(subset=['h3_index'], inplace=True)
    return df

df = load_data()

col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("Controls & Insights")
    selected_city = st.selectbox("Focus on a City", ["All"] + sorted(df['city_name'].unique()))
    city_df = df if selected_city == "All" else df[df['city_name'] == selected_city]
    
    st.markdown("---")
    st.subheader("Actionable Insights")
    
    hex_summary = city_df.groupby('h3_index').agg(
        gross_margin=('gross_margin', 'sum'),
        num_orders=('delivery_id', 'count')
    ).reset_index()

    st.info("The map shows total gross margin per hexagonal area. Bright green areas are profitable 'golden hexes'; bright red areas are unprofitable 'zombie hexes'.")
    worst_hexes = hex_summary.sort_values('gross_margin').head(10)
    st.write("**Top 10 Worst Performing Hexes (by Margin):**")
    st.dataframe(worst_hexes.style.format({'gross_margin': '${:,.2f}'}))

with col2:
    st.subheader("Hyper-Local Profitability Map")
    
    hex_data_for_map = hex_summary.copy()
    
    def h3_to_geojson(h3_index):
        boundary_lat_lon = h3.cell_to_boundary(h3_index)
        boundary_lon_lat = [[lon, lat] for lat, lon in boundary_lat_lon]
        return {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [boundary_lon_lat]},
            "id": h3_index
        }

    geojson_features = [h3_to_geojson(h) for h in hex_data_for_map['h3_index']]
    geojson_data = {"type": "FeatureCollection", "features": geojson_features}

    map_center = {
        "lat": city_df['customer_latitude'].mean(),
        "lon": city_df['customer_longitude'].mean()
    }
    zoom_level = 10 if selected_city != "All" else 3.5

    if not hex_data_for_map.empty:
        # --- FIX: Create a dynamic and symmetrical color range ---
        # 1. Find the maximum absolute value to center the color scale around zero.
        max_abs_val = hex_data_for_map['gross_margin'].abs().max()
        
        # 2. Create the symmetrical range. Add a small epsilon to prevent a zero range.
        color_range = [-max_abs_val - 1e-9, max_abs_val + 1e-9]

        fig = px.choropleth_mapbox(
            hex_data_for_map,
            geojson=geojson_data,
            locations='h3_index',
            color='gross_margin',
            color_continuous_scale="RdYlGn",
            # 3. Use the dynamic range instead of a hard-coded one.
            range_color=color_range,
            mapbox_style="carto-darkmatter",
            zoom=zoom_level,
            center=map_center,
            opacity=0.6,
            labels={'gross_margin': 'Gross Margin ($)'},
            hover_data={'num_orders': True}
        )
        
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            title_text="Profitability by Neighborhood",
            title_x=0.5
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data to display on the map for the selected city.")