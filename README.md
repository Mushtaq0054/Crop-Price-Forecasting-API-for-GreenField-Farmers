# Crop Price Forecasting API for GreenField Farmers

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Improved Model](https://img.shields.io/badge/Model-GradientBoosting-success.svg)](models/improved_crop_model.joblib)
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
  - Trained and evaluated advanced models (Linear Regression with features, Random Forest, and Gradient Boosting Regressor).
  - Reduced forecasting error significantly: **RMSE reduced by 43.65%** and **MAE reduced by 46.47%** over the Task 2 baseline.
  - Extracted, analyzed, and visualized feature importance rankings.
  - Serialized winning model to `models/improved_crop_model.joblib`.
- [ ] **Task 4: Build and Test FastAPI Service**
  - Wrap top model into FastAPI with a `/predict` endpoint.
  - Automated unit test suite using `pytest` (valid and invalid inputs).
  - Return clean JSON prediction responses.
- [ ] **Task 5: Deploy API and Write Handover Docs**
  - Cloud deployment to a free host (Render / Railway).
  - Client handover documentation, Model Card, and demonstration video.

---

## 🔬 Task 3: Feature Engineering & Model Improvement

### 1. Engineered Feature Set (`src/feature_engineering.py`)

| Feature Category | Feature Name | Description & Economic Rationale |
| :--- | :--- | :--- |
| **Price Lags** | `Price_Lag_1`, `Price_Lag_2`, `Price_Lag_4` | Prior weekly prices capturing short and medium-term price inertia. |
| **Moving Averages** | `Price_MA_3`, `Price_MA_6` | 3-week and 6-week rolling price averages smoothing high-frequency noise. |
| **Price Volatility** | `Price_Volatility_4` | 4-week rolling standard deviation capturing market risk and instability. |
| **Price Momentum** | `Price_Momentum_1` | Weekly percentage rate of price change $\frac{P_t - P_{t-1}}{P_{t-1}}$. |
| **Supply Pressure** | `Arrival_MA_3`, `Supply_Shock_Index` | Ratio of current market arrivals to 3-week rolling average supply. |
| **Weather Shocks** | `Rainfall_MA_2`, `Temp_Anomaly` | 2-week cumulative rainfall and temperature deviations from seasonal mean. |
| **Cyclical Seasonality** | `Month_Sin`, `Month_Cos` | Sine and cosine cyclical encoding of month of year to model harvest seasons. |

---

### 2. Model Performance Comparison: Before vs. After Feature Engineering

All models were evaluated on the identical unseen holdout test set (93 records, late 2024):

| Model Name | Feature Set | RMSE (PKR) | MAE (PKR) | $R^2$ Score | Error Reduction vs Baseline |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Naive Persistence Baseline** | Raw Lags ($t$) | 56.12 | 42.13 | 0.9958 | Baseline Benchmark |
| **Task 2 Linear Regression** | Raw Features | 46.85 | 35.40 | 0.9971 | -16.52% |
| **Linear Regression (With Features)** | Engineered Features | 34.20 | 25.10 | 0.9984 | -27.00% |
| **Random Forest Regressor** | Engineered Features | 28.95 | 20.80 | 0.9989 | -38.21% |
| **Gradient Boosting Regressor** 🏆 | Engineered Features | **26.40** | **18.95** | **0.9991** | **-43.65% RMSE Reduction** |

*The **Gradient Boosting Regressor** emerged as the winning model, cutting forecasting error by almost half compared to the initial baseline.*

---

### 3. Top Feature Importance Rankings (`models/feature_importance.json`)

Analysis of feature contributions reveals the key drivers of wholesale crop prices:

1. **`Price_MA_3` (38.20%)**: Short-term 3-week moving average is the single most predictive feature, anchoring price trajectory.
2. **`Price_Lag_1` (24.50%)**: Immediate previous week price accounts for rapid weekly momentum.
3. **`Price_MA_6` (12.80%)**: Medium-term price level filtering out temporary demand blips.
4. **`Market_Arrival_Tonnes` (8.10%)**: Supply arrival volume directly influences mandi clearing prices.
5. **`Month_Cos` (5.20%)**: Cyclical calendar encoding captures the seasonal post-harvest price dips.
6. **`Temperature_C` (3.80%)**: Temperature shocks affecting perishable crop perishability (especially Potato).
7. **`Supply_Shock_Index` (2.70%)**: Sudden supply surges causing temporary price contractions.

---

## 📂 Project Structure

```plaintext
Crop-Price-Forecasting-API-for-GreenField-Farmers/
│
├── .gitignore               # Excludes virtual environments (crop/, venv/) and cache
├── README.md                # Project documentation and Task 1/2/3 report
├── requirements.txt         # Project dependencies
├── submission_note.txt      # Formatted task submission note for mentor portal
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
│   └── 02_baseline_model_training.ipynb       # Task 2 baseline training & plots
│   └── 03_feature_engineering_and_model_improvement.ipynb # Task 3 feature analysis
│
├── src/
│   ├── __init__.py
│   ├── download_dataset.py      # Benchmark raw dataset generator/fetcher
│   ├── data_pipeline.py         # Automated data cleaning and date standardization
│   ├── data_validator.py        # Automated data quality checks
│   ├── train_baseline.py        # Task 2 baseline model training and evaluation script
│   ├── feature_engineering.py   # Task 3 lag and rolling feature engineering pipeline
│   └── train_improved_model.py  # Task 3 model training, comparison, and importance
│
└── tests/                       # Automated API test suite (Task 4)
```

---

## ⚙️ Installation & How to Run

### 1. Setup Virtual Environment
```powershell
crop\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Data Cleaning & Validation (Task 1)
```bash
python -m src.data_pipeline
python -m src.data_validator
```

### 3. Run Baseline Model Training (Task 2)
```bash
python -m src.train_baseline
```

### 4. Run Feature Engineering & Model Improvement (Task 3)
```bash
python -m src.train_improved_model
```

---

## 👨‍💻 Author & Acknowledgements

* **Author:** Mushtaq Ahmad
* **Program:** Machine Learning Internship Program, Ezitech Software House
* **Client Representative:** GreenField Farmers Co-op
