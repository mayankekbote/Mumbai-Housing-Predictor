# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from folium.plugins import HeatMap
import pickle
from streamlit_folium import folium_static
import folium
import branca.colormap as cm

import json

st.set_page_config(page_title="Mumbai Housing Predictor", page_icon="🏠", layout="wide")

st.markdown(
    '<meta name="google-site-verification" content="ZVe3DzHw-s_FVXPPXlSvWPgR0hoxBoP72sETwBwfd2U" />',
    unsafe_allow_html=True
)

# ==================================================
# Load Fuzzy Buckets and Data
# ==================================================
@st.cache_data
def load_fuzzy_data():
    with open("region_buckets.json", "r") as f:
        buckets = json.load(f)
    coords = pd.read_csv("mumbai_region_coords (1).csv", encoding="latin1")
    mumbai_data = pd.read_csv("mumbai_cleaned.csv", encoding="latin1")
    # Clean column names
    coords.columns = coords.columns.str.strip().str.lower()
    mumbai_data.columns = mumbai_data.columns.str.strip().str.lower()
    return buckets, coords, mumbai_data

region_buckets, df, mumbai = load_fuzzy_data()

# ==================================================
# Features (must match training features exactly)
# ==================================================
_regions = [
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
_ages = ["New", "Resale", "Unknown"]
_feature_names = ['x`bhk', 'area', 'age'] + _regions

# ==================================================
# Load ANN model and scaler (moved to cache)
# ==================================================
@st.cache_resource
def load_ann_model():
    import keras
    # Keras 3 can directly load .keras zip files
    return keras.models.load_model("mumbai_ann_model_fixed.keras")

@st.cache_resource
def load_scaler():
    with open("scaler.pkl", "rb") as f:
        return pickle.load(f)

model = load_ann_model()
scaler = load_scaler()


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
.model-badge {
    background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    color: #444;
    padding: 8px 16px;
    border-radius: 20px;
    display: inline-block;
    margin: 10px 0;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🏠 Mumbai Housing Price Predictor")
st.subheader("🔮 Expert System powered by Fuzzy Logic")
st.markdown("<div class='model-badge'>⚖️ Using Rule-Based Fuzzy Inference System</div>", unsafe_allow_html=True)

# ==================================================
# Fuzzy Logic Core Functions
# ==================================================
def trimf(x, a, b, c):
    return max(0, min((x - a) / (b - a) if b > a else 1, (c - x) / (c - b) if c > b else 1))

def trapmf(x, a, b, c, d):
    return max(0, min((x - a) / (b - a) if b > a else 1, 1, (d - x) / (d - c) if d > c else 1))

def get_area_membership(area):
    return {
        "Small": trapmf(area, 0, 0, 500, 800),
        "Medium": trimf(area, 600, 1000, 1400),
        "Large": trimf(area, 1200, 1800, 2400),
        "X-Large": trapmf(area, 2200, 3000, 5000, 5000)
    }

def get_bhk_membership(bhk):
    return {
        "1 BHK": trimf(bhk, 0.5, 1, 1.5),
        "2 BHK": trimf(bhk, 1.5, 2, 2.5),
        "3 BHK": trimf(bhk, 2.5, 3, 3.5),
        "4+ BHK": trapmf(bhk, 3.5, 4, 6, 6)
    }

def get_region_membership(price):
    # Quantiles from our analysis: [6586, 10167, 19136, 23940, 36822]
    return {
        "Budget": trapmf(price, 0, 0, 5000, 8000),
        "Value": trimf(price, 6000, 10000, 14000),
        "Mid-Range": trimf(price, 12000, 18000, 24000),
        "Premium": trimf(price, 20000, 26000, 32000),
        "Luxury": trimf(price, 28000, 38000, 48000),
        "Ultra-Luxury": trapmf(price, 45000, 60000, 100000, 100000)
    }

# Programmatic Comprehensive Rule Base Generation
# We define base prices per sqft for each region category and then scale by BHK and Area
def generate_rules():
    reg_bases = {
        "Budget": 5000, 
        "Value": 9000, 
        "Mid-Range": 15000, 
        "Premium": 24000, 
        "Luxury": 38000, 
        "Ultra-Luxury": 65000
    }
    bhk_factors = {"1 BHK": 0.9, "2 BHK": 1.0, "3 BHK": 1.2, "4+ BHK": 1.5}
    area_factors = {"Small": 0.9, "Medium": 1.0, "Large": 1.2, "X-Large": 1.4}
    
    gen_rules = []
    for reg, base in reg_bases.items():
        for bhk, b_fact in bhk_factors.items():
            for area, a_fact in area_factors.items():
                price = int(base * b_fact * a_fact)
                gen_rules.append(((area, bhk, reg), price))
    return gen_rules

RULES = generate_rules()

# Inference with multiple overlapping rules
def fuzzy_inference(area, bhk, region_median_price):
    mu_area = get_area_membership(area)
    mu_bhk = get_bhk_membership(bhk)
    mu_region = get_region_membership(region_median_price)
    
    fired_rules = []
    numerator = 0
    denominator = 0
    
    for (r_area, r_bhk, r_reg), price_sqft in RULES:
        # Rule weight is the minimum of all inputs (Mamdani Min-Inference)
        a_deg = mu_area.get(r_area, 0)
        b_deg = mu_bhk.get(r_bhk, 0)
        r_deg = mu_region.get(r_reg, 0)
        
        weight = min(a_deg, b_deg, r_deg)
        if weight > 0:
            fired_rules.append({
                "rule": f"IF Area is {r_area} AND BHK is {r_bhk} AND Region is {r_reg}",
                "inputs": f"(Area: {a_deg:.2f}, BHK: {b_deg:.2f}, Region: {r_deg:.2f})",
                "weight": weight,
                "output": price_sqft
            })
            numerator += (weight * price_sqft)
            denominator += weight
            
    # Fallback to pure market average if extremely unusual input causes no rules to fire
    if denominator == 0:
        avg_price_sqft = region_median_price
    else:
        avg_price_sqft = numerator / denominator
        
    final_price_lakhs = (avg_price_sqft * area) / 100000
    return final_price_lakhs, avg_price_sqft, fired_rules, mu_area, mu_bhk, mu_region

# ==================================================
# Tabs Layout
# ==================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚡ Fuzzy Predictor", 
    "📊 Fuzzy Dashboard", 
    "🧠 ANN (Deep Learning)",
    "🗺️ Explore Map", 
    "🏘️ Clusters"
])

# -----------------------------
# Tab 1: Prediction
# -----------------------------
# -----------------------------
# Tab 1: Fuzzy Predictor
# -----------------------------
with tab1:
    with st.expander("📌 Enter Property Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            bhk_f = st.slider("🛏️ Number of BHK", min_value=1, max_value=5, value=2, step=1, key="f_bhk")
            area_f = st.number_input("📐 Area (sqft)", min_value=100, max_value=5000, value=1000, step=50, key="f_area")
        with col2:
            region_f = st.selectbox("📍 Select Region", sorted(_regions), key="f_reg")
            reg_class = region_buckets.get(region_f, "Mid-Range")
            st.info(f"🏷️ **Region Category:** {reg_class}")

    if st.button("🚀 Run Fuzzy Inference", use_container_width=True):
        # Get actual median price for the region from our data
        region_stats = mumbai.groupby("region")["price_per_sqft"].median()
        reg_median = region_stats.get(region_f, 15000)
        
        price, psf, rules, mu_area, mu_bhk, mu_reg = fuzzy_inference(area_f, bhk_f, reg_median)
        
        st.markdown(f"<div class='prediction-card'>✨ Predicted Price: ₹ {price:,.2f} Lakhs</div>", unsafe_allow_html=True)
        st.markdown(f"<center><b>Price per sqft: ₹ {psf:,.2f}</b></center>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            best_area = max(mu_area, key=mu_area.get)
           
        with c2:
            best_reg = max(mu_reg, key=mu_reg.get)
           
       
            
            
        with st.expander("🔍 Detailed Rule Inference Trace", expanded=True):
            st.markdown("### How the result was calculated:")
            for r in sorted(rules, key=lambda x: x['weight'], reverse=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"✅ **{r['rule']}**")
                    st.caption(f"Fuzzy Inputs: {r['inputs']}")
                with col_b:
                    st.write(f"**Weight: {r['weight']:.2f}**")
                    st.progress(r['weight'])
            st.info("The final price is the **Weighted Average** of the outputs from all rules firing above.")

# -----------------------------
# Tab 2: Fuzzy Dashboard
# -----------------------------
with tab2:
    st.header("🧮 Fuzzy membership & Rule Analysis")
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    d_col1, d_col2 = st.columns(2)
    
    with d_col1:
        st.subheader("📈 Membership Functions")
        
        # Plot Area MF
        x_area = np.linspace(0, 5000, 500)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(x_area, [trapmf(x, 0, 0, 500, 800) for x in x_area], label="Small")
        ax.plot(x_area, [trimf(x, 600, 1000, 1400) for x in x_area], label="Medium")
        ax.plot(x_area, [trimf(x, 1200, 1800, 2400) for x in x_area], label="Large")
        ax.plot(x_area, [trapmf(x, 2200, 3000, 5000, 5000) for x in x_area], label="X-Large")
        ax.set_title("Property Area (sqft)")
        ax.legend()
        st.pyplot(fig)
        
        # Plot BHK MF
        x_bhk = np.linspace(0, 6, 100)
        fig2, ax2 = plt.subplots(figsize=(8, 3))
        ax2.plot(x_bhk, [trimf(x, 0.5, 1, 1.5) for x in x_bhk], label="1 BHK", color="blue")
        ax2.plot(x_bhk, [trimf(x, 1.5, 2, 2.5) for x in x_bhk], label="2 BHK", color="orange")
        ax2.plot(x_bhk, [trimf(x, 2.5, 3, 3.5) for x in x_bhk], label="3 BHK", color="green")
        ax2.plot(x_bhk, [trapmf(x, 3.5, 4, 6, 6) for x in x_bhk], label="4+ BHK", color="red")
        ax2.set_title("BHK Levels")
        ax2.legend()
        st.pyplot(fig2)

        # Plot Region MF (Price PSF)
        st.write("**3. Region Affordability (Price per sqft)**")
        x_price = np.linspace(0, 80000, 500)
        fig3, ax3 = plt.subplots(figsize=(8, 3))
        ax3.plot(x_price, [trapmf(x, 0, 0, 5000, 8000) for x in x_price], label="Budget", color="gray")
        ax3.plot(x_price, [trimf(x, 6000, 10000, 14000) for x in x_price], label="Value", color="blue")
        ax3.plot(x_price, [trimf(x, 12000, 18000, 24000) for x in x_price], label="Mid-Range", color="cyan")
        ax3.plot(x_price, [trimf(x, 20000, 26000, 32000) for x in x_price], label="Premium", color="magenta")
        ax3.plot(x_price, [trimf(x, 28000, 40000, 52000) for x in x_price], label="Luxury", color="gold")
        ax3.plot(x_price, [trapmf(x, 45000, 60000, 80000, 80000) for x in x_price], label="Ultra-Luxury", color="black")
        ax3.set_title("Region Classification (6 Buckets)")
        ax3.legend()
        st.pyplot(fig3)

    with d_col2:
        st.subheader("🔥 Active Rules in Last Run")
        if 'f_area' in st.session_state:
            # Get actual median price for the region from our data
            region_stats = mumbai.groupby("region")["price_per_sqft"].median()
            reg_median = region_stats.get(st.session_state.f_reg, 15000)
            p, ps, fired, mu_a, mu_b, mu_r = fuzzy_inference(st.session_state.f_area, st.session_state.f_bhk, reg_median)
            if fired:
                for r in fired:
                    st.write(f"✅ **{r['rule']}**")
                    st.caption(f"Weight: {r['weight']:.2f} | Output PSF: ₹ {r['output']}")
                    st.progress(r['weight'])
            else:
                st.warning("No specific rules fired. Using baseline region averages.")
        
        st.subheader("📋 Static Rule Table")
        with st.expander("🔍 Click to view all Fuzzy Rules", expanded=False):
            rule_data = []
            for i, ((a, b, r), val) in enumerate(RULES):
                rule_data.append({"No": i+1, "Area": a, "BHK": b, "Region": r, "Result Price (PSF)": f"₹ {val:,}"})
            st.dataframe(rule_data, use_container_width=True)
            st.caption(f"Total active rules in the knowledge base: {len(RULES)}")
        st.subheader("⚖️ Defuzzification Formula")
        st.latex(r"Price = \frac{\sum (Weight_i \times Output_i)}{\sum Weight_i} \times Area")
        st.info("The system uses the **Weighted Average** method to convert fuzzy rule outputs into a crisp price per square foot.")

# -----------------------------
# Tab 3: ANN Predictor
# -----------------------------
with tab3:
    st.header("🧠 Artificial Neural Network Analysis")
    st.markdown("This tab uses the trained Deep Learning model to estimate prices based on the full feature set (One-Hot Encoded Regions).")
    
    with st.expander("📌 Enter Property Details (ANN)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            bhk_ann = st.slider("🛏️ Number of BHK", min_value=1, max_value=3, value=2, step=1, key="ann_bhk")
            area_ann = st.number_input("📐 Area (sqft)", min_value=100, max_value=3000, value=1000, step=50, key="ann_area")
        with col2:
            age_ann = st.selectbox("🏗️ Property Age", _ages, key="ann_age")
            region_ann = st.selectbox("📍 Select Region", ["Any / Not Sure"] + sorted(_regions), key="ann_reg")

    # ANN Prediction Logic
    if st.button("🚀 ANN Predict Price", use_container_width=True):
        input_data = np.zeros(len(_feature_names))
        input_data[_feature_names.index('x`bhk')] = bhk_ann
        input_data[_feature_names.index('area')] = area_ann
        if age_ann == "New": input_data[_feature_names.index('age')] = 1
        elif age_ann == "Resale": input_data[_feature_names.index('age')] = 2
        if region_ann != "Any / Not Sure" and region_ann in _regions:
            input_data[_feature_names.index(region_ann)] = 1
            
        try:
            input_scaled = scaler.transform([input_data])
            ann_prediction = model.predict(input_scaled, verbose=0)[0][0]
            st.success(f"### 🤖 ANN Predicted Price: ₹ {ann_prediction:,.2f} L")
        except Exception as e:
            st.error(f"Prediction error: {e}")

# -----------------------------
# Tab 4: Map
# -----------------------------
with tab4:
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
            # To fix MarshallComponentException, we use folium_static which renders HTML
            colormap.add_to(m) 
        else:
            HeatMap(
                df_map[['latitude','longitude','median_price']].dropna().values.tolist(),
                radius=15, blur=10
            ).add_to(m)

        folium_static(m, width=1000, height=700)

    if selected_regions:
        avg_price = df_map[df_map['region'].isin(selected_regions)]['median_price'].mean()
        st.success(f"📊 Average Price per sqft : ₹ {avg_price:,.2f} /sqft")

# -----------------------------
# Tab 5: Clusters
# -----------------------------
with tab5:
    st.markdown("## 🏘️ Mumbai Housing Clusters")
    
    # Prepare data
    df_clusters = pd.merge(df, median_prices, on="region", how="left")

    # Layout
    col1, col2 = st.columns([1, 1])

    # ---------- LEFT COLUMN ----------
    with col1:
        k = st.slider("🔢 Select number of clusters", min_value=2, max_value=8, value=3, step=1)

        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=k, random_state=42)
        df_clusters['cluster'] = kmeans.fit_predict(df_clusters[['latitude','longitude','median_price']])

        # Cluster summary
        st.markdown("### 📋 Cluster Summary")
        st.caption("Clusters sorted by average median price per sqft")
        cluster_summary = df_clusters.groupby('cluster')['median_price'].agg(['count','mean','min','max']).reset_index() 
        cluster_summary.rename(columns={'mean': 'median'}, inplace=True)   
        cluster_summary = cluster_summary.sort_values(by='median', ascending=False).reset_index(drop=True)

        # Assign colors for sorted clusters
        import matplotlib.cm as mpl_cm
        import matplotlib.colors as mpl_colors
        palette = mpl_cm.get_cmap('Set1', k)
        cluster_colors = [mpl_colors.rgb2hex(palette(i)) for i in range(k)]

        label_to_color = {row['cluster']: cluster_colors[i] for i, row in cluster_summary.iterrows()}

        # Highlight cluster column in dataframe
        def highlight_cluster(row):
            return [f'background-color: {label_to_color[row.cluster]}' if col=='cluster' else '' for col in row.index]

        st.dataframe(cluster_summary.style.apply(highlight_cluster, axis=1))

    # ---------- RIGHT COLUMN ----------
    with col2:
        m = folium.Map(location=[19.0760, 72.8777], zoom_start=10)

        for _, row in df_clusters.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=10,
                color=label_to_color[row['cluster']],
                fill=True,
                fill_color=label_to_color[row['cluster']],
                fill_opacity=0.7,
                popup=f"{row['region'].title()}<br>Median Price: ₹ {row['median_price']:,.2f}/sqft<br>Cluster: {row['cluster']}"
            ).add_to(m)

        # Use folium_static to avoid JSON serialization errors with complex objects
        folium_static(m, width=700, height=700)

# Note: Detailed Fuzzy Logic analysis moved to Dashboard tab for better flow.
    st.info("💡 **Project Goal:** This system uses Fuzzy Logic to simulate human reasoning (e.g., 'If a house is large and in a luxury area, the price is high'). The ANN tab remains available for high-precision machine learning comparisons.")
