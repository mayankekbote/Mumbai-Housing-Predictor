

# 🏠 Mumbai Housing Price Predictor

House price prediction uses machine learning to assist buyers, sellers, and real estate companies in making better decisions. This project builds a machine learning model to estimate prices using features like region, size, bedrooms, and property age. Regression models such as Linear Regression, Decision Tree, and Random Forest were tested to identify the most accurate predictor, with the final application powered by an **Artificial Neural Network (ANN)**. Geospatial aggregation is used to identify areas with high price per sqft.

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

# 🌟 Project Overview

Mumbai's real estate is one of India's most dynamic markets. This project provides a **machine learning–powered system** to estimate housing prices based on:

* BHK
* Area (sqft)
* Property age
* Region
* Local market dynamics

It uses an **Artificial Neural Network (ANN)** with multiple hidden layers and Adam optimization to deliver high-precision predictions.

---

# 🧠 Machine Learning Details

### ✔ **Model Used: Artificial Neural Network (ANN)**

* Architecture: Dense input layer, multiple hidden layers (ReLU), and a single linear output layer.
* Reason for using ANN:
  * Captures complex non-linear relationships between property features.
  * Scales well with large datasets (100+ region segments).
  * High predictive accuracy through backpropagation and Adam optimization.

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

# 📁 Project Structure

```
📂 project-root
│── app_ann.py                   # Main Streamlit application
│── mumbai_ann_model_fixed.keras # ANN model
│── mumbai_cleaned.csv           # Cleaned housing dataset
│── mumbai_region_coords (1).csv # Mapping coordinates
│── scaler.pkl                   # Input data scaler
│── requirements.txt
│── README.md
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

