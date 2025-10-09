# Core libraries
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
# Folium and related plugins
import folium
from folium.plugins import HeatMap
import branca.colormap as cm

# Streamlit-Folium integration
from streamlit_folium import st_folium

@st.cache_data
def load_mumbai():
    return pd.read_csv("mumbai_cleaned.csv", encoding="latin1")

mumbai = load_mumbai()

# Load Mumbai region coordinates
@st.cache_data
def load_coords():
    return pd.read_csv("mumbai_region_coords.csv", encoding="latin1")

df = load_coords()

# Clean column names
mumbai.columns = mumbai.columns.str.strip().str.lower()
df.columns = df.columns.str.strip().str.lower()


# Load GeoJSON from .txt file
try:
    with open("maharashtra.geojson.txt", "r", encoding="utf-8") as f:
        maha_geojson = json.load(f)
except Exception as e:
    st.error(f"Failed to load GeoJSON: {e}")
    maha_geojson = None

# Create Folium map
m = folium.Map(location=[19.7515, 75.7139], zoom_start=6)

# Add Maharashtra outline if loaded
if maha_geojson:
    folium.GeoJson(maha_geojson, name="Maharashtra Outline").add_to(m)

# Display map in Streamlit
st_folium(m, width=700, height=500)

# -----------------------------
# Tab 2: Maharashtra Map
st.markdown("## 🗺️ Maharashtra Housing Heatmap")
st.caption("Explore median price per sqft across Maharashtra regions")

    # Prepare median prices
median_prices = mumbai.groupby("region")["price_per_sqft"].median().reset_index()
median_prices.rename(columns={"price_per_sqft": "median_price"}, inplace=True)
df_map = pd.merge(df, median_prices, on="region", how="left")

    # Columns for filters and map
col1, col2 = st.columns([1, 4])

    # -----------------------------
    # Left: Filters & Map options
    # -----------------------------
with col1:
        selected_regions = st.multiselect(
            "📍 Filter by Region",
            df_map["region"].unique().tolist(),
            default=[]
        )
        map_style = st.selectbox(
            "🗺️ Map Style",
            ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]
        )
        map_mode = st.radio("🌍 View Mode", ["Circle Markers", "Heatmap"])

    # -----------------------------
    # Right: Map
    # -----------------------------
with col2:
        # Maharashtra center and bounds
        maharashtra_center = [19.7515, 75.7139]
        sw = [15.6, 72.6]  # southwest corner of Maharashtra
        ne = [22.1, 80.9]  # northeast corner of Maharashtra

        m = folium.Map(
            location=maharashtra_center,
            zoom_start=6,
            tiles=map_style,
            control_scale=True
        )
        m.fit_bounds([sw, ne])  # restrict map to Maharashtra bounds

        # Optional: Maharashtra outline
        try:
            maha_geojson = "https://raw.githubusercontent.com/geohacker/india/master/states/Maharashtra.geojson"
            folium.GeoJson(maha_geojson, name="Maharashtra Outline").add_to(m)
        except:
            pass

        # Color map
        min_price = df_map['median_price'].min()
        max_price = df_map['median_price'].max()
        colormap = cm.LinearColormap(['green','yellow','red'], vmin=min_price, vmax=max_price)

        if map_mode == "Circle Markers":
            for _, row in df_map.iterrows():
                if not selected_regions or row['region'] in selected_regions:
                    color = colormap(row['median_price']) if row['median_price'] else 'gray'
                    popup_html = f"""
                        <div style='font-size:14px;'>
                        <b>{row['region'].title()}</b><br>
                        {'💰 Avg Price: ₹ {:,.2f}/sqft'.format(row['median_price']) if row['median_price'] else '💰 No price data'}
                        </div>
                    """
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=10,
                        popup=folium.Popup(popup_html, max_width=250),
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7
                    ).add_to(m)
            colormap.add_to(m)
        else:
            HeatMap(
                df_map[['latitude','longitude','median_price']].dropna().values.tolist(),
                radius=15, blur=10
            ).add_to(m)

        st_folium(m, width='100%', height=700, key="maharashtra_map")

        if selected_regions:
            avg_price = df_map[df_map['region'].isin(selected_regions)]['median_price'].mean()
            st.success(f"📊 Average Price per sqft : ₹ {avg_price:,.2f} /sqft")


