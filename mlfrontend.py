# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from folium.plugins import HeatMap
import pickle
from streamlit_folium import st_folium
import folium
import branca.colormap as cm

# ==================================================
# Load model (cached globally)
# ==================================================
@st.cache_resource
def load_model():
    with open("mumbai_model (6).pkl", "rb") as f:
        return pickle.load(f)
model = load_model()

# ==================================================
# Load data (cached globally)
# ==================================================
@st.cache_data
def load_coords():
    return pd.read_csv("mumbai_region_coords (1).csv", encoding="latin1")

@st.cache_data
def load_mumbai():
    return pd.read_csv("mumbai_cleaned.csv", encoding="latin1")

df = load_coords()
mumbai = load_mumbai()

# Clean column names once
df.columns = df.columns.str.strip().str.lower()
mumbai.columns = mumbai.columns.str.strip().str.lower()
# df_clusters['latitude'] = pd.to_numeric(df_clusters['latitude'], errors='coerce')
# df_clusters['longitude'] = pd.to_numeric(df_clusters['longitude'], errors='coerce')

# # Drop rows with invalid coordinates
# df_clusters = df_clusters.dropna(subset=['latitude', 'longitude', 'median_price'])
# ==================================================
# Features
# ==================================================
regions = [
 'agripada','airoli','ambarnath','ambernath east','ambernath west','andheri east',
 'andheri west','anjurdive','badlapur east','badlapur west','bandra east',
 'bandra kurla complex','bandra west','belapur','bhandup east','bhandup west',
 'bhayandar east','bhayandar west','bhiwandi','boisar','borivali east',
 'borivali west','byculla','chembur','colaba','dadar east','dadar west',
 'dahisar','deonar','diva','dombivali','dombivali east','dronagiri',
 'ghansoli','ghatkopar east','ghatkopar west','girgaon','goregaon east',
 'goregaon west','jogeshwari east','jogeshwari west','juhu','juinagar',
 'kalamboli','kalyan east','kalyan west','kamothe','kandivali east',
 'kandivali west','kanjurmarg','karanjade','karjat','khar','kharghar',
 'khopoli','koper khairane','kurla','lower parel','mahalaxmi','mahim',
 'malad east','malad west','marine lines','matunga','mazagaon','mira road east',
 'mulund east','mulund west','nahur east','naigaon east','nala sopara','neral',
 'nerul','nilje gaon','palghar','panvel','parel','powai','prabhadevi',
 'rasayani','sanpada','santacruz east','santacruz west','seawoods','sewri',
 'shil phata','sion','taloja','tardeo','thane east','thane west','titwala',
 'ulhasnagar','ulwe','umroli','vasai','vashi','vikhroli','ville parle east',
 'ville parle west','virar','wadala','worli'
]
ages = ["New", "Resale", "Unknown"]

# ==================================================
# Streamlit Page Config & CSS
# ==================================================
st.set_page_config(page_title="Mumbai Housing Price Predictor", page_icon="🏠", layout="wide")
st.markdown("""
<meta name="google-site-verification" content="ZVe3DzHw-s_FVXPPXlSvWPgR0hoxBoP72sETwBwfd2U">
""", unsafe_allow_html=True)

st.markdown("""
<style>
h1 { text-align:center; color:#000000; }
.stButton>button {
    background-color:#FFB400;
    color:#000000;
    font-weight:bold;
}
.prediction-card {
    padding:20px; 
    background: rgba(0,0,0,0.7); 
    border-radius:15px; 
    text-align:center;
    color: #FFD700;
    font-size: 1.5rem;
    font-weight: bold;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.title("🏠 Mumbai Housing Price Predictor")
st.subheader("🔮 AI-powered estimate of your dream home price in Mumbai")

# ==================================================
# Tabs
# ==================================================
tab1, tab2 ,tab3= st.tabs(["⚡ Predict Price", "🗺️ Explore Map","Neighbourhood Clusters"])

# -----------------------------
# Tab 1: Prediction
# -----------------------------
with tab1:
    with st.expander("📌 Enter Property Details", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            bhk = st.slider("🛏️ Number of BHK", min_value=1, max_value=3, value=1, step=1)
            area = st.number_input("📐 Area (sqft)", min_value=100, max_value=3000, value=1000, step=50)

        with col2:
            age = st.selectbox("🏗️ Property Age", ages)
            region = st.selectbox("📍 Select Region", ["Any / Not Sure"] + sorted(regions))

    feature_names = ['x`bhk','area','age'] + regions
    input_data = np.zeros(len(feature_names))
    input_data[feature_names.index('x`bhk')] = bhk
    input_data[feature_names.index('area')] = area

    if age == "New":
        input_data[feature_names.index('age')] = 1
    elif age == "Resale":
        input_data[feature_names.index('age')] = 2
    else:
        input_data[feature_names.index('age')] = 0

    if region in regions:
        input_data[feature_names.index(region)] = 1

    if st.button("🚀 Predict Price", use_container_width=True):
        try:
            prediction = model.predict([input_data])[0]
            st.markdown(
                f"<div class='prediction-card'>🏷️ Estimated Price: ₹ {prediction:,.2f} Lakhs</div>",
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Prediction failed: {e}")

# -----------------------------
# Tab 2: Map
# -----------------------------
with tab2:
    st.markdown("## 🗺️ Mumbai Housing Heatmap")
    st.caption("Explore median price per sqft across Mumbai regions")

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
            default=[],
            key="tab2_region_filter"
        )
        map_style = st.selectbox(
            "🗺️ Map Style",
            ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"],
            key="tab2map"
        )
        map_mode = st.radio("🌍 View Mode", ["Circle Markers", "Heatmap"])

    # -----------------------------
    # Right: Map
    # -----------------------------
    with col2:
        m = folium.Map(location=[19.0760, 72.8777], zoom_start=10, tiles=map_style, control_scale=True)

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

        st_folium(m, width='100%', height=700, key="mumbai_map")

    if selected_regions:
        avg_price = df_map[df_map['region'].isin(selected_regions)]['median_price'].mean()
        st.success(f"📊 Average Price per sqft : ₹ {avg_price:,.2f} /sqft")
with tab3:
    st.markdown("## 🏘️ Mumbai Housing Clusters")
    

    # Prepare data
    df_clusters = pd.merge(df, median_prices, on="region", how="left")
    df_clusters.rename(columns={"price_per_sqft": "median_price"}, inplace=True)


    # Layout
    col1, col2 = st.columns([1, 1])

    # ---------- LEFT COLUMN ----------
    with col1:
        k = st.slider("🔢 Select number of clusters", min_value=2, max_value=8, value=3, step=1)

        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=k, random_state=42)
        df_clusters['cluster'] = kmeans.fit_predict(df_clusters[['latitude','longitude','median_price']])

        # Cluster summary
        cluster_summary = df_clusters.groupby('cluster')['median_price'].agg(['count','mean','min','max']).reset_index()
        cluster_summary = cluster_summary.sort_values(by='mean', ascending=False).reset_index(drop=True)

        # Assign colors for sorted clusters
        import matplotlib.cm as mpl_cm
        import matplotlib.colors as mpl_colors
        palette = mpl_cm.get_cmap('Set1', k)
        cluster_colors = [mpl_colors.rgb2hex(palette(i)) for i in range(k)]

        # Map original KMeans label → color according to sorted mean
        # This ensures dataframe and map colors match
        label_to_color = {row['cluster']: cluster_colors[i] for i, row in cluster_summary.iterrows()}

        # Highlight cluster column in dataframe
        def highlight_cluster(row):
            return [f'background-color: {label_to_color[row.cluster]}' if col=='cluster' else '' for col in row.index]

        st.dataframe(cluster_summary.style.apply(highlight_cluster, axis=1))

    # ---------- RIGHT COLUMN ----------
    with col2:
        import folium
        from streamlit_folium import st_folium

        m = folium.Map(location=[19.0760, 72.8777], zoom_start=10)

        for _, row in df_clusters.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=10,
                color=label_to_color[row['cluster']],       # <- use mapping here
                fill=True,
                fill_color=label_to_color[row['cluster']],  # <- use mapping here
                fill_opacity=0.7,
                popup=f"{row['region'].title()}<br>Median Price: ₹ {row['median_price']:,.2f}/sqft<br>Cluster: {row['cluster']}"
            ).add_to(m)

        st_folium(m, width='100%', height=700)





    # median_prices = mumbai.groupby("region")["price_per_sqft"].median().reset_index()
    # df_dend = pd.merge(df, median_prices, on="region", how="left")
    # df_dend.rename(columns={"price_per_sqft": "median_price"}, inplace=True)
    # df_dend = df_dend.dropna(subset=['latitude','longitude','median_price'])

    # from scipy.cluster.hierarchy import linkage, dendrogram
    # import matplotlib.pyplot as plt

    # # Features for clustering: lat, lon, median_price
    # X = df_dend[['latitude','longitude','median_price']].values

    # # Perform hierarchical clustering
    # Z = linkage(X, method='ward')

    # # Plot dendrogram
    # fig, ax = plt.subplots(figsize=(12, 6))
    # dendrogram(Z, labels=df_dend['region'].values, leaf_rotation=90)
    # plt.title("Hierarchical Clustering Dendrogram (Ward)")
    # plt.xlabel("Region")
    # plt.ylabel("Distance")
    # st.pyplot(fig)
