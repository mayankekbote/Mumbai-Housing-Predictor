

# 🏠 Mumbai Housing Price Predictor (Hybrid ANN + Fuzzy Logic)

House price prediction uses machine learning to assist buyers, sellers, and real estate companies in making better decisions. This project builds a comprehensive, hybrid system to estimate prices using features like region, size, bedrooms, and property age. The final application integrates an **Artificial Neural Network (ANN)** for high-precision data-driven predictions and a **Fuzzy Logic Expert System** for transparent, rule-based reasoning. Regional classification is performed using unsupervised clustering to group areas with similar price dynamics.

🔗 **Live App:** [https://flatdekho.streamlit.app](https://flatdekho.streamlit.app)

---

# 🚀 How to Run This Project Locally

### **1️⃣ Clone the repository**

```bash
git clone <your-repo-link>
cd <repo-folder>
```

### **2️⃣ Create & activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### **3️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

### **4️⃣ Make sure the required files exist**

The project expects the following files in the root directory:

```
mumbai_model (6).pkl  
mumbai_cleaned.csv  
mumbai_region_coords (1).csv  
```

### **5️⃣ Run the Streamlit app**

```bash
streamlit run app.py
```

The app will open automatically in your browser at:

```
http://localhost:8501
```

---

Mumbai's real estate is one of India's most dynamic markets. This project provides a **hybrid intelligent system** to estimate housing prices based on:

* BHK
* Area (sqft)
* Property age
* Region (Grouped into buckets: Elite, High, Premium, Mid-Range, Budget, and Essential)
* Local market dynamics

The system features:
1. **ANN Prediction Engine**: High-accuracy deep learning backend.
2. **Fuzzy Logic Dashboard**: Transparent, rule-based expert system for human-like reasoning.
3. **Regional Analytics**: Automated classification of Mumbai regions into value-based tiers.

---

### ✔ **Model 1: Artificial Neural Network (ANN)**

* Architecture: Dense input layer, multiple hidden layers (ReLU), and a single linear output layer.
* Reason for using ANN:
  * Captures complex non-linear relationships between property features.
  * Scales well with large datasets (100+ region segments).
  * High predictive accuracy through backpropagation and Adam optimization.

### ✔ **Model 2: Fuzzy Logic Expert System**

* Methodology: Rule-based engine using membership functions for `Size`, `BHK`, `Age`, and `Region Category`.
* Features:
  * Transparent deduction logic (e.g., If Region is Elite and BHK is High, then Price is High).
  * Centroid defuzzification for crisp price estimation.
  * Interactive UI for viewing membership functions and active rule tables.

### ✔ **Feature Engineering**

* One-hot encoding for **100+ Mumbai regions**
* Numeric features:

  * BHK count
  * Built-up area (sqft)
  * Age category encoding (0/1/2)
* Cleaning column names
* Imputing & merging median price per sqft for mapping

### ✔ **Data Processing Skills Used**

* Pandas cleaning (strip, fill, merge, groupby)
* Normalized region data
* Cache optimization using `st.cache_resource` & `st.cache_data`
* Coordinate mapping and merging with price data

### ✔ **Model Serving Skills**

* Loading `.pkl` model safely
* Converting inputs to correct feature vector alignment
* Handling exceptions & invalid inputs

---

# 🎨 App Features (Streamlit)

### **1️⃣ Price Prediction**

* User inputs: region, BHK, sqft, age
* Beautiful UI with CSS styling
* Displays estimated price in Lakhs

### **2️⃣ Interactive Heatmap**

* Explore **median price per sqft**
* Choose map styles (OpenStreetMap, CartoDB)
* Region filtering
* Circle markers OR heatmap view

### **3️⃣ Neighbourhood Clustering**

* K-Means clustering (2–8 clusters)
* Automatically colors clusters
* View summaries (mean, min, max price)
* Interactive geospatial visualization

---

# 🏗️ DevOps & CI/CD Pipeline

This project implements a complete **DevOps pipeline** to automate the testing and deployment lifecycle:

- **Version Control**: Managed with **GitHub**.
- **Continuous Integration (CI)**: Powered by **Jenkins** (via `Jenkinsfile`).
- **Automated Testing**: UI tests built using **Selenium** with **Microsoft Edge (Headless)**.
- **Background Automation**: The pipeline automatically manages the Streamlit server lifecycle (Start -> Test -> Cleanup) using Windows PowerShell.
- **Portability**: All dependencies are managed in `requirements.txt` for easy replication.

---

# 📁 Project Structure

```
📂 project-root
│── app_ann.py                   # Main Streamlit application (Hybrid ANN + Fuzzy)
│── analyze_regions.py           # Script for regional classification & analysis
│── region_buckets.json          # Pre-calculated regional categorization data
│── tests/test_ui.py             # Automated Selenium UI tests (Edge)
│── Jenkinsfile                  # DevOps pipeline configuration (Windows)
│── mumbai_ann_model_fixed.keras # Trained ANN model
│── mumbai_cleaned.csv           # Cleaned housing dataset
│── mumbai_region_coords (1).csv # Mapping coordinates for geospatial features
│── scaler.pkl                   # Input data scaler for ANN features
│── requirements.txt             # Project dependencies
│── README.md                    # Project documentation
```

---

# 🛠 Tech Stack

### **Frontend/UI**

* Streamlit
* Streamlit Folium
* Custom CSS

### **Backend / ML Serving**

* Python
* NumPy
* Pandas
* Scikit-learn
* Pickle

### **Geospatial Visualization**

* Folium
* HeatMap plugin
* Branca colormap

---

# 📌 Future Improvements

* Add grid-search optimized Random Forest
* Save & log user predictions
* Deploy on AWS / GCP with CI/CD
* Add rent prediction model

---

# 🤝 Contributing

Pull requests and feature suggestions are welcome!

