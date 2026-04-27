# FarmAI Lite: Microclimate-Based Smart Farming Assistant

## Overview

FarmAI Lite is a data-driven smart farming system that analyzes microclimate variations within a farm to support better agricultural decision-making.

The system uses environmental parameters such as air temperature, humidity, soil moisture, soil temperature, rainfall, and light intensity to classify farms into distinct microclimate zones. Based on these zones, it provides intelligent insights including crop recommendations, irrigation planning, and zone health evaluation.

This project demonstrates how machine learning and rule-based systems can improve farming efficiency without relying on expensive IoT infrastructure.

---

## Key Features

* Microclimate zoning using K-Means clustering
* PCA-based visualization for cluster validation
* Rule-based crop recommendation system
* Irrigation advisory based on soil moisture thresholds
* Zone health scoring system (0–100 scale)
* What-if simulation for environmental changes
* Multi-page interactive dashboard built with Streamlit

---

## Microclimate Zones

The system identifies four major zones:

* Hot & Dry Zone
* Cool & Moist Zone
* Rain-Influenced Zone
* Sunny & Balanced Zone

Each zone is analyzed to provide tailored recommendations.

---

## Tech Stack

* Python
* Pandas, NumPy
* Scikit-learn
* Matplotlib, Seaborn
* Streamlit

---

## Project Structure

```
project-root/
│
├── data/
│   └── microclimate_clustered_final.csv
│
├── pages/
│   ├── Crop_Recommendation.py
│   ├── Irrigation_Advisor.py
│   ├── Zone_Explorer.py
│   └── Zone_Summary.py
│
├── app.py
├── utils.py
├── requirements.txt
└── README.md
```

---

## How It Works

1. Dataset is generated/simulated with environmental parameters
2. Data preprocessing and normalization is applied
3. K-Means clustering identifies microclimate zones
4. PCA is used for visualization and validation
5. Rule-based logic generates insights
6. Results are displayed through an interactive Streamlit dashboard

---

## Installation & Setup

### 1. Clone the repository

```
git clone https://github.com/YOUR_USERNAME/farmai-lite.git
cd farmai-lite
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the application

```
streamlit run app.py
```

---

## System Requirements

* Python 3.10 or above
* Minimum 8 GB RAM recommended
* Works on Windows, Linux, and macOS

---

## Limitations

* Uses synthetic dataset (no real sensor data)
* Rule-based system instead of predictive ML
* No real-time data integration
* Limited environmental parameters

---

## Future Scope

* Integration with IoT sensors
* Real-time weather API integration
* Predictive machine learning models
* Mobile application
* Automated irrigation systems
* Cloud deployment
