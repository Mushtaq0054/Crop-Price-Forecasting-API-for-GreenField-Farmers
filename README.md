# Crop Price Forecasting API for GreenField Farmers

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-13%20Passed-brightgreen.svg)](tests/test_api.py)
[![Deployment](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://render.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Project Overview

| Project Information | Details |
| :--- | :--- |
| **Project Title** | Crop Price Forecasting API for GreenField Farmers |
| **Client** | GreenField Farmers Co-op |
| **Intern** | Mushtaq Ahmad |
| **Technology Stack** | Python, Scikit-Learn, FastAPI, Pydantic v2, Pytest, Render |
| **Level** | Intermediate |
| **Repository** | [GitHub Repository](https://github.com/Mushtaq0054/Crop-Price-Forecasting-API-for-GreenField-Farmers.git) |
| **Live Deployed API** | [https://crop-price-forecasting-api.onrender.com](https://crop-price-forecasting-api.onrender.com) |
| **Interactive Dashboard** | [https://crop-price-forecasting-api.onrender.com/dashboard](https://crop-price-forecasting-api.onrender.com/dashboard) |
| **Interactive Docs** | [https://crop-price-forecasting-api.onrender.com/docs](https://crop-price-forecasting-api.onrender.com/docs) |

---

## 🌾 Business Problem Statement

**GreenField Farmers Co-op** sells staple agricultural produce (Wheat, Rice, and Potato) to wholesale agricultural markets (mandis). Due to volatile weather disruptions (unseasonal rain, temperature shifts) and sudden surges in market supply, the cooperative struggles to determine fair and profitable selling prices.

Selling produce blindly during sudden market gluts causes severe price depression and financial losses. Conversely, storing produce too long incurs warehousing expenses and spoilage risks.

### Objective:
Build and deploy a robust Machine Learning API that forecasts **next-week modal crop prices** (PKR per quintal) along with confidence intervals for the cooperative's top three staple crops:
1. **Wheat**
2. **Rice (Paddy)**
3. **Potato**

With these forward-looking predictions, the cooperative management can schedule sales strategically, negotiate fair pricing, and protect farmer livelihoods.

---

## 🗺️ Project Milestones & Completion Roadmap

- [x] **Task 1: Prepare and Validate Crop Price Dataset**
  - Ingested multi-year historical wholesale price records and weather observations.
  - Implemented automated data cleaning pipeline (`src/data_pipeline.py`) for missing value interpolation and ISO date standardization.
  - Built an automated data quality test suite (`src/data_validator.py`) verifying 5 fundamental integrity constraints.
  - Exported sanitized dataset to `data/processed/crop_prices_cleaned.csv`.
- [x] **Task 2: Train and Evaluate Baseline Price Model**
  - Formulated the next-week price target (`Target_Next_Week_Price`).
  - Implemented chronological 80/20 train/test split to prevent temporal data leakage.
  - Benchmarked against a Naive Persistence Baseline ($\hat{y}_{t+1} = y_t$).
  - Fitted a Scikit-Learn Linear Regression pipeline (Baseline RMSE: 46.85 PKR, MAE: 35.40 PKR).
  - Serialized model to `models/baseline_linear_regression.joblib`.
- [x] **Task 3: Feature Engineering and Model Improvement**
  - Engineered domain features: historical price lags ($t-1, t-2, t-4$), rolling moving averages (3-week and 6-week), 4-week price volatility, supply shock ratios, and cyclical harvest seasonality.
  - Evaluated multiple candidate algorithms: Linear Regression, Random Forest, and Gradient Boosting.
  - Selected **Gradient Boosting Regressor** as champion model (RMSE: 26.40 PKR, MAE: 18.95 PKR, $R^2$: 0.9991) — achieving a **43.65% RMSE reduction** over the baseline.
  - Serialized winning pipeline to `models/improved_crop_model.joblib`.
- [x] **Task 4: Build and Test FastAPI Service**
  - Encapsulated the production model inside a high-speed ASGI service (`src/api.py`, `app.py`).
  - Built the `/predict` endpoint with Pydantic schema validation, case-insensitive crop parsing, and fallback reference caches.
  - Created automated test suite (`tests/test_api.py`) with 13 comprehensive unit tests (all passing).
- [x] **Task 5: Deploy API and Write Handover Docs**
  - Configured cloud-native deployment manifests (`render.yaml`, `Procfile`).
  - Deployed live REST API service to Render free hosting.
  - Authored client handover documentation, API usage guides, and comprehensive Model Card.

---

## 🚀 Live API Endpoints

| Method | Endpoint | Description | Sample Request | Expected Output |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/` | API status, metadata & documentation URL | None | Service info & health link |
| `GET` | `/health` | Live probe checking model availability | None | `{"status": "healthy", "model_loaded": true}` |
| `POST` | `/predict` | Predicts next-week modal price in PKR/quintal | `{"crop": "Wheat", "date": "2026-10-25"}` | Predicted price & confidence interval |
| `GET` | `/docs` | Interactive Swagger UI API explorer | Open browser | Visual API testing interface |
| `GET` | `/redoc` | ReDoc OpenAPI documentation | Open browser | Clean API specifications |

---

## 💻 API Usage Examples

### 1. Interactive Swagger UI (Recommended for Demo)
Open **`https://crop-price-forecasting-api.onrender.com/docs`** (or `http://localhost:8000/docs` locally):
1. Click on `POST /predict`.
2. Click **"Try it out"**.
3. Enter the request payload and click **"Execute"**.

### 2. cURL Example
```bash
curl -X POST "https://crop-price-forecasting-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "Wheat",
    "date": "2026-10-28",
    "current_price_pkr": 3820.0,
    "market_arrival_tonnes": 420.0,
    "rainfall_mm": 10.0,
    "temperature_c": 25.5
  }'
```

*(Note: `current_price_pkr`, `market_arrival_tonnes`, `rainfall_mm`, and `temperature_c` are optional. If omitted, the API automatically infers reference values from historical crop trends).*

### 3. Python `requests` Example
```python
import requests

api_url = "https://crop-price-forecasting-api.onrender.com/predict"
payload = {
    "crop": "Rice",
    "date": "2026-11-05"
}

response = requests.post(api_url, json=payload)
data = response.json()

print(f"Crop: {data['crop']}")
print(f"Predicted Price: {data['predicted_next_week_price_pkr']} {data['currency']}")
print(f"Confidence Bounds: {data['confidence_interval_pkr']['lower_bound']} - {data['confidence_interval_pkr']['upper_bound']}")
```

### 4. Sample JSON Response (HTTP 200 OK)
```json
{
  "status": "success",
  "crop": "Wheat",
  "target_date": "2026-10-28",
  "predicted_next_week_price_pkr": 3845.2,
  "confidence_interval_pkr": {
    "lower_bound": 3826.25,
    "upper_bound": 3864.15
  },
  "currency": "PKR per Quintal",
  "model_version": "GradientBoostingRegressor_v1.0"
}
```

---

## 📋 Model Card

### 1. Model Details
* **Model Name:** GreenField Crop Price Forecaster
* **Model Architecture:** Gradient Boosting Regressor (`scikit-learn.ensemble.GradientBoostingRegressor`)
* **Pipeline Structure:** `ColumnTransformer` (One-Hot Encoding for categorical crop identifier + StandardScaler for numerical features) followed by an ensemble of 150 regression estimators.
* **Target Variable:** `Target_Next_Week_Price` (Wholesale Modal Price 7 days ahead in Pakistani Rupees [PKR] per quintal).
* **Release Date:** October 2026
* **Developer:** Mushtaq Ahmad (Machine Learning Intern, Ezitech Software House)

### 2. Intended Use
* **Primary Intended Use:** Provide weekly market price advisories and forecast intervals for cooperative leadership and smallholder member farmers to plan harvesting, storage, and wholesale market sales.
* **Intended Users:** GreenField Farmers Co-op market managers, pricing analysts, and agricultural extension field agents.
* **Out-of-Scope Uses:** Speculative financial commodity day-trading, non-agricultural commodities, or forecasting retail consumer prices.

### 3. Factors & Input Features
* **Commodity Types:** Wheat, Rice (Paddy), Potato.
* **Temporal Indicators:** Weekly calendar cycle, harvest month seasonality (sinusoidal and cosinusoidal transforms).
* **Price Momentum:** Lagged prices ($t-1, t-2, t-4$ weeks), 3-week and 6-week rolling moving averages, 4-week historical volatility.
* **Supply & Weather Drivers:** Weekly mandi market arrival tonnage, supply shock ratio (current arrival vs. 4-week average), cumulative rainfall (mm), and average ambient temperature (°C).

### 4. Benchmark Evaluation & Performance Metrics
Models were evaluated on unseen chronological test partitions (strictly forward in time to avoid data leakage):

| Model Architecture | RMSE (PKR/quintal) | MAE (PKR/quintal) | $R^2$ Score | Relative Error Reduction |
| :--- | :---: | :---: | :---: | :---: |
| Naive Persistence Baseline | 56.12 | 42.13 | 0.9950 | Reference Benchmark |
| Linear Regression Baseline (Task 2) | 46.85 | 35.40 | 0.9971 | 16.51% over persistence |
| Random Forest Regressor | 34.20 | 24.15 | 0.9984 | 26.99% over Task 2 |
| **Gradient Boosting Regressor (Champion)** | **26.40** | **18.95** | **0.9991** | **43.65% over Task 2 Baseline** |

### 5. Assumptions & Limitations
* **Continuity Assumption:** The model assumes typical continuous market dynamics without sudden nationwide export/import embargoes, drastic currency devaluation shocks, or unannounced statutory price caps.
* **Regional Calibration:** Models are calibrated on regional wholesale mandi dynamics; price variances may occur if produce is sold in distant metropolitan terminal markets without transport cost adjustment.
* **Extreme Weather Events:** Catastrophic floodings or severe droughts exceeding 100-year historical return periods may deviate actual spot prices beyond standard model confidence intervals.

### 6. Ethical Considerations & Safeguards
* **Farmer Protection:** Predictions provide a symmetric confidence interval (±1.0 MAE) to avoid false precision and prevent premature distress selling.
* **Explainability:** Feature importance analysis is publicly documented to ensure cooperative members understand why price movements are projected.

---

## 🛠️ Local Setup & Execution Instructions

### Prerequisites
* Python 3.10 to 3.12 installed.
* Git installed.

### 1. Clone the Repository
```bash
git clone https://github.com/Mushtaq0054/Crop-Price-Forecasting-API-for-GreenField-Farmers.git
cd Crop-Price-Forecasting-API-for-GreenField-Farmers
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv crop
.\crop\Scripts\activate

# macOS / Linux
python3 -m venv crop
source crop/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the API Locally
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Open **`http://127.0.0.1:8000/docs`** to access the interactive Swagger UI.

### 5. Run Automated Tests
```bash
pytest tests/test_api.py -v
```
All 13 unit tests will execute and confirm schema enforcement, calculation accuracy, and error handling.

---

## ☁️ Deployment Guide (Render / Railway)

This repository includes native cloud deployment blueprints (`render.yaml` and `Procfile`).

### Deploying to Render in 4 Simple Steps:
1. **Push to GitHub:** Ensure your latest commits are pushed to your GitHub repository.
2. **Log in to Render:** Go to [render.com](https://render.com) and click **"New" > "Web Service"**.
3. **Connect Repository:** Link your `Crop-Price-Forecasting-API-for-GreenField-Farmers` repository.
4. **Deploy with Blueprint or Manual Settings:**
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
5. Click **"Deploy Web Service"**. Once deployed, Render will provide your public URL (e.g., `https://crop-price-forecasting-api.onrender.com`).

---

## 📂 Project Repository Structure

```plaintext
Crop-Price-Forecasting-API-for-GreenField-Farmers/
│
├── .gitignore               # Ignores virtual environments (crop/, venv/) and cache files
├── README.md                # Comprehensive documentation, setup guide, and Model Card
├── requirements.txt         # Project runtime dependencies
├── Procfile                 # Cloud web dyno process declaration
├── render.yaml              # Render Infrastructure-as-Code deployment blueprint
├── submission_note.txt      # Formatted task submission notes for portal review
├── app.py                   # Root application entrypoint for Uvicorn
│
├── data/
│   ├── raw/                 # Raw multi-year crop price & arrival records
│   │   └── crop_prices_raw.csv
│   └── processed/           # Cleaned and feature-engineered datasets
│       ├── crop_prices_cleaned.csv
│       └── crop_prices_featured.csv
│
├── models/                  # Serialized ML models and metric reports
│   ├── baseline_linear_regression.joblib  # Task 2 baseline model
│   ├── baseline_metrics.json              # Task 2 baseline metrics
│   ├── improved_crop_model.joblib         # Task 3 champion Gradient Boosting pipeline
│   ├── improved_model_metrics.json        # Task 3 comparative benchmarks
│   └── feature_importance.json            # Task 3 feature importance ranking
│
├── notebooks/
│   ├── 01_data_cleaning_and_validation.ipynb  # Task 1 EDA and validation notebook
│   ├── 02_baseline_model_training.ipynb       # Task 2 baseline training & plots
│   └── 03_feature_engineering_and_model_improvement.ipynb # Task 3 feature engineering
│
├── src/
│   ├── __init__.py
│   ├── download_dataset.py      # Synthetic raw dataset generator/fetcher
│   ├── data_pipeline.py         # Automated cleaning and date standardization
│   ├── data_validator.py        # Automated quality validation checks
│   ├── train_baseline.py        # Task 2 baseline training pipeline
│   ├── feature_engineering.py   # Task 3 lag and rolling feature generator
│   ├── train_improved_model.py  # Task 3 model comparison and serialization
│   └── api.py                   # Production FastAPI service with robust schemas
│
└── tests/
    └── test_api.py              # Automated Pytest suite (13 test cases)
```

---

## 🎥 Client Handover Demo Video Guide

To demonstrate the working solution to GreenField Farmers Co-op:
1. Start your local or deployed API service.
2. Open the Swagger UI at `/docs`.
3. Demonstrate a successful prediction for **Wheat**, **Rice**, and **Potato**.
4. Show how the API responds with confidence bounds and handles invalid input (e.g., unsupported crop or malformed date).
5. Highlight how this provides actionable price visibility for the next selling week.

---

## 👨‍💻 Author & Acknowledgements

* **Author:** Mushtaq Ahmad
* **Program:** Machine Learning Internship Program, Ezitech Software House
* **Client Partner:** GreenField Farmers Co-op
* **License:** MIT License
