# Crop Price Forecasting API for GreenField Farmers

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Baseline Model](https://img.shields.io/badge/Model-Trained-brightgreen.svg)](models/baseline_linear_regression.joblib)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Project Overview

| Project Information | Details |
| :--- | :--- |
| **Project Title** | Crop Price Forecasting API for GreenField Farmers |
| **Client** | GreenField Farmers Co-op |
| **Intern** | Mushtaq Ahmad |
| **Technology** | Machine Learning, Time Series, FastAPI, Pytest |
| **Level** | Intermediate |
| **Repository** | [GitHub Repo](https://github.com/Mushtaq0054/Crop-Price-Forecasting-API-for-GreenField-Farmers.git) |

---

## 🌾 Business Problem Statement

**GreenField Farmers Co-op** sells staple agricultural commodities to local and regional wholesale markets (mandis). Due to volatile weather disruptions (untimely rain, temperature shifts) and sudden market supply changes, the cooperative struggles to determine fair, profitable selling prices.

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
  - Built and fitted a Scikit-Learn Linear Regression pipeline with one-hot encoding for crops.
  - Benchmarked against a Naive Persistence Baseline ($\hat{y}_{t+1} = y_t$).
  - Evaluated performance using RMSE, MAE, $R^2$, and MAPE.
  - Serialized the trained model artifact to `models/baseline_linear_regression.joblib`.
- [ ] **Task 3: Feature Engineering and Model Improvement**
  - Create lag features ($t-1, t-7$), rolling moving averages, and weather/supply indicators.
  - Retrain advanced regressors and evaluate error reduction over baseline.
  - Calculate and report feature importance rankings.
- [ ] **Task 4: Build and Test FastAPI Service**
  - Wrap top model into FastAPI with a `/predict` endpoint.
  - Automated unit test suite using `pytest` (valid and invalid inputs).
  - Return clean JSON prediction responses.
- [ ] **Task 5: Deploy API and Write Handover Docs**
  - Cloud deployment to a free host (Render / Railway).
  - Client handover documentation, Model Card, and demonstration video.

---

## 📈 Task 2: Baseline Model Training & Evaluation

### 1. Chronological Split Strategy
In agricultural time-series forecasting, random cross-validation splits introduce severe future lookahead bias. To preserve real-world forecasting conditions:
* **Train Set (80%)**: 375 records (2022-01-03 to 2024-05-20)
* **Test Set (20%)**: 93 records (2024-05-27 to 2024-12-23)
* **Target Variable**: $y = \text{Modal\_Price}_{t+1\text{ week}}$

### 2. Baseline Model Architecture
* **Naive Persistence Baseline**: Predicts that next week's price equals the current week's price ($\hat{y}_{t+1} = y_t$).
* **Linear Regression Pipeline**:
  * Categorical Encoding: `OneHotEncoder(drop='first')` for crop types (`Wheat`, `Rice`, `Potato`).
  * Numerical Scaling: `StandardScaler` for `Modal_Price_PKR`, `Min_Price_PKR`, `Max_Price_PKR`, `Market_Arrival_Tonnes`, `Rainfall_mm`, `Temperature_C`.
  * Estimator: `LinearRegression()`.

### 3. Baseline Performance Comparison

| Metric | Naive Persistence Baseline | Linear Regression Model | Improvement (%) |
| :--- | :---: | :---: | :---: |
| **RMSE (PKR)** | **56.12** | **46.85** | **16.52% Reduction** |
| **MAE (PKR)** | **42.13** | **35.40** | **15.97% Reduction** |
| **$R^2$ Score** | 0.9958 | **0.9971** | **+0.0013** |
| **MAPE (%)** | 1.48% | **1.22%** | **17.57% Relative Improvement** |

### 4. Per-Crop Error Breakdown (Linear Regression)
* **Wheat**: $\text{RMSE} = 35.21\text{ PKR}$, $\text{MAE} = 27.65\text{ PKR}$, $R^2 = 0.9892$
* **Rice**: $\text{RMSE} = 44.18\text{ PKR}$, $\text{MAE} = 34.20\text{ PKR}$, $R^2 = 0.9854$
* **Potato**: $\text{RMSE} = 57.82\text{ PKR}$, $\text{MAE} = 44.35\text{ PKR}$, $R^2 = 0.9821$

*The higher RMSE on Potato reflects its known market volatility during harvest dips, highlighting the need for advanced feature engineering (moving averages, lagged features) in Task 3.*

---

## 📂 Project Structure

```plaintext
Crop-Price-Forecasting-API-for-GreenField-Farmers/
│
├── .gitignore               # Excludes virtual environments (crop/, venv/) and cache
├── README.md                # Project documentation and Task 1/2 report
├── requirements.txt         # Project dependencies
├── submission_note.txt      # Formatted task submission note for mentor portal
│
├── data/
│   ├── raw/                 # Raw market arrivals and price records
│   │   └── crop_prices_raw.csv
│   └── processed/           # Cleaned, standardized, and validated dataset
│       └── crop_prices_cleaned.csv
│
├── models/                  # Serialized models and evaluation reports
│   ├── baseline_linear_regression.joblib  # Serialized Task 2 model
│   └── baseline_metrics.json              # Evaluated metrics JSON
│
├── notebooks/
│   ├── 01_data_cleaning_and_validation.ipynb  # Task 1 EDA and validation notebook
│   └── 02_baseline_model_training.ipynb       # Task 2 baseline training & plots
│
├── src/
│   ├── __init__.py
│   ├── download_dataset.py  # Benchmark raw dataset generator/fetcher
│   ├── data_pipeline.py     # Automated data cleaning and date standardization
│   ├── data_validator.py    # Automated data quality checks
│   └── train_baseline.py    # Task 2 baseline model training and evaluation script
│
└── tests/                   # Automated API test suite (Task 4)
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

### 3. Run Baseline Model Training & Evaluation (Task 2)
```bash
python -m src.train_baseline
```

---

## 👨‍💻 Author & Acknowledgements

* **Author:** Mushtaq Ahmad
* **Program:** Machine Learning Internship Program, Ezitech Software House
* **Client Representative:** GreenField Farmers Co-op
