# Crop Price Forecasting API for GreenField Farmers

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-12%20Passed-brightgreen.svg)](tests/test_api.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Project Overview

| Project Information | Details |
| :--- | :--- |
| **Project Title** | Crop Price Forecasting API for GreenField Farmers |
| **Client** | GreenField Farmers Co-op |
| **Intern** | Mushtaq Ahmad |
| **Technology** | Machine Learning, Feature Engineering, FastAPI, Pytest |
| **Level** | Intermediate |
| **Repository** | [GitHub Repo](https://github.com/Mushtaq0054/Crop-Price-Forecasting-API-for-GreenField-Farmers.git) |

---

## 🌾 Business Problem Statement

**GreenField Farmers Co-op** sells staple agricultural produce to local and regional wholesale markets (mandis). Due to volatile weather disruptions (untimely rain, temperature shifts) and sudden market supply changes, the cooperative struggles to determine fair, profitable selling prices.

Without forward-looking price visibility, farmers risk selling their harvest during sudden price crashes, leading to heavy financial losses.

### Objective:
Build and deploy a machine learning-backed API that forecasts **next-week crop prices** for the cooperative's top three staple crops:
1. **Wheat**
2. **Rice (Paddy)**
3. **Potato**

With accurate one-week price forecasts, farmers can schedule harvest sales strategically, minimize holding costs, and maximize collective profits.

---

## 🗺️ Project Roadmap & Milestones

- [x] **Task 1: Prepare and Validate Crop Price Dataset**
  - Ingested multi-year raw wholesale market price records.
  - Built an automated data cleaning script (`src/data_pipeline.py`) handling missing values and standardizing dates.
  - Implemented an automated data validation suite (`src/data_validator.py`) verifying 5 key data quality rules.
  - Cleaned dataset committed at `data/processed/crop_prices_cleaned.csv`.
- [x] **Task 2: Train and Evaluate Baseline Price Model**
  - Created temporal next-week price target (`Target_Next_Week_Price`).
  - Performed chronological 80/20 train/test split to prevent data leakage.
  - Fitted a Scikit-Learn Linear Regression pipeline with one-hot encoding for crops.
  - Benchmarked against a Naive Persistence Baseline ($\hat{y}_{t+1} = y_t$).
  - Serialized the baseline model to `models/baseline_linear_regression.joblib`.
- [x] **Task 3: Feature Engineering and Model Improvement**
  - Engineered domain-specific features: price lags ($t-1, t-2, t-4$), rolling moving averages (3-week & 6-week), price volatility, supply shock index, and cyclical harvest seasonality.
  - Benchmarked improved models: Gradient Boosting Regressor reduced RMSE by 43.65% over the baseline.
  - Serialized winning model to `models/improved_crop_model.joblib`.
- [x] **Task 4: Build and Test FastAPI Service**
  - Wrapped the trained Gradient Boosting model into a high-performance RESTful FastAPI service (`src/api.py`, `app.py`).
  - Implemented `/predict` endpoint taking `crop` and `date` with strict Pydantic input validation.
  - Authored a comprehensive automated test suite (`tests/test_api.py`) with 12 unit tests verifying valid predictions and error handling.
- [ ] **Task 5: Deploy API and Write Handover Docs**
  - Cloud deployment to a free host (Render / Railway).
  - Client handover documentation, Model Card, and demonstration video.

---

## ⚡ Task 4: FastAPI Service & Automated Test Suite

### 1. API Endpoints

| Method | Endpoint | Description | Sample Request | Expected Response |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/` | API status, metadata & documentation link | None | `{"status": "online", "service": "..."}` |
| `GET` | `/health` | Health check verifying model availability | None | `{"status": "healthy", "model_loaded": true}` |
| `POST` | `/predict` | Predicts next-week crop price in PKR per quintal | `{"crop": "Wheat", "date": "2026-10-25"}` | `{"status": "success", "predicted_next_week_price_pkr": 3845.2, ...}` |
| `GET` | `/docs` | Interactive Swagger UI documentation | Open in browser | Interactive API Explorer |

---

### 2. Request & Response Payload Examples

#### Sample POST `/predict` Request:
```json
{
  "crop": "Wheat",
  "date": "2026-10-25",
  "current_price_pkr": 3820.0,
  "market_arrival_tonnes": 420.0,
  "rainfall_mm": 12.5,
  "temperature_c": 26.0
}
```
*(Note: `current_price_pkr`, `market_arrival_tonnes`, `rainfall_mm`, and `temperature_c` are optional. If omitted, the service automatically populates features using latest cached market state).*

#### Sample Response (HTTP 200 OK):
```json
{
  "status": "success",
  "crop": "Wheat",
  "target_date": "2026-10-25",
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

### 3. Automated Validation & Error Handling (Pytest)

The automated test suite in `tests/test_api.py` includes **12 automated test cases**:
1. **Root Endpoint**: Verifies `GET /` returns HTTP 200 and correct service metadata.
2. **Health Check**: Verifies `GET /health` confirms active model loading.
3. **Valid Crop Predictions**: Confirms correct inference for all 3 staple crops (**Wheat**, **Rice**, **Potato**).
4. **Case-Insensitive Input**: Confirms lowercase inputs (e.g., `"wheat"`, `"rice"`) are properly parsed.
5. **Real-Time Context**: Validates prediction when client supplies dynamic weather and market arrivals.
6. **Invalid Crop Handling**: Confirms submitting unsupported commodities (e.g., `"Mango"`) returns HTTP 422 with a descriptive error message.
7. **Malformed Dates**: Confirms malformed date strings (e.g., `"25-10-2026"` or `"tomorrow"`) trigger HTTP 422 validation errors.
8. **Missing Fields**: Confirms requests missing required fields (`crop` or `date`) are cleanly rejected without server crashes.

---

## 📂 Project Structure

```plaintext
Crop-Price-Forecasting-API-for-GreenField-Farmers/
│
├── .gitignore               # Excludes virtual environments (crop/, venv/) and cache
├── README.md                # Project documentation and Task reports
├── requirements.txt         # Project dependencies (includes fastapi, uvicorn, pytest, httpx)
├── submission_note.txt      # Formatted task submission note for mentor portal
├── app.py                   # Root Uvicorn server entrypoint
│
├── data/
│   ├── raw/                 # Raw market arrivals and price records
│   │   └── crop_prices_raw.csv
│   └── processed/           # Cleaned and feature-engineered datasets
│       ├── crop_prices_cleaned.csv
│       └── crop_prices_featured.csv
│
├── models/                  # Serialized models and evaluation reports
│   ├── baseline_linear_regression.joblib  # Task 2 baseline model
│   ├── baseline_metrics.json              # Task 2 metrics
│   ├── improved_crop_model.joblib         # Task 3 winning Gradient Boosting model
│   ├── improved_model_metrics.json        # Task 3 model comparison report
│   └── feature_importance.json            # Task 3 feature importance report
│
├── notebooks/
│   ├── 01_data_cleaning_and_validation.ipynb  # Task 1 EDA and validation notebook
│   ├── 02_baseline_model_training.ipynb       # Task 2 baseline training & plots
│   └── 03_feature_engineering_and_model_improvement.ipynb # Task 3 feature analysis
│
├── src/
│   ├── __init__.py
│   ├── download_dataset.py      # Benchmark raw dataset generator/fetcher
│   ├── data_pipeline.py         # Automated data cleaning and date standardization
│   ├── data_validator.py        # Automated data quality checks
│   ├── train_baseline.py        # Task 2 baseline model training and evaluation script
│   ├── feature_engineering.py   # Task 3 lag and rolling feature engineering pipeline
│   ├── train_improved_model.py  # Task 3 model training, comparison, and importance
│   └── api.py                   # Task 4 production FastAPI service implementation
│
└── tests/
    └── test_api.py              # Task 4 automated unit test suite (12 tests)
```

---

## ⚙️ How to Run

### 1. Run the FastAPI Server
To start the live local API server:
```powershell
uvicorn app:app --reload
```
*(Or run `python app.py`).*  
Interactive Swagger API documentation will be available at: **http://127.0.0.1:8000/docs**

### 2. Run Automated Test Suite
To execute all 12 automated unit and integration tests:
```powershell
pytest tests/test_api.py -v
```

---

## 👨‍💻 Author & Acknowledgements

* **Author:** Mushtaq Ahmad
* **Program:** Machine Learning Internship Program, Ezitech Software House
* **Client Representative:** GreenField Farmers Co-op
