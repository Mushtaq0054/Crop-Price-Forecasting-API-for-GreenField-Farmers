# Crop Price Forecasting API for GreenField Farmers

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Project Overview

| Project Information | Details |
| :--- | :--- |
| **Project Title** | Crop Price Forecasting API for GreenField Farmers |
| **Client** | GreenField Farmers Co-op |
| **Intern** | Mushtaq Ahmad |
| **Technology** | Machine Learning, FastAPI, Time Series Forecasting |
| **Level** | Intermediate |
| **Repository** | [GitHub Repo](https://github.com/Mushtaq0054/Crop-Price-Forecasting-API-for-GreenField-Farmers.git) |

---

## 🌾 Business Problem Statement

**GreenField Farmers Co-op** sells agricultural commodities directly to regional wholesale markets (mandis). However, the cooperative routinely struggles to establish fair, competitive selling prices due to rapid supply fluctuations and volatile weather disruptions (such as untimely rainfall and temperature spikes).

Without reliable forward visibility, farmers are vulnerable to selling at market troughs, resulting in significant revenue losses. 

### Objective:
Develop and deploy a production-ready Machine Learning API that forecasts **next-week prices** for the cooperative's top three staple crops:
1. **Wheat**
2. **Rice (Paddy)**
3. **Potato**

By providing predictive price guidance one week in advance, farmers can make informed holding and harvesting decisions, time their market arrivals strategically, and maximize their earnings.

---

## 🗺️ Project Roadmap & Milestones

The project is structured into 5 incremental phases:

- [x] **Repository Initialization & Environment Setup**: Repository architecture, dependency mapping, and raw data ingestion.
- [ ] **Task 1: Prepare and Validate Crop Price Dataset**
  - Download and inspect raw agricultural market time-series.
  - Handle missing data points, impute values, and standardize varied date conventions.
  - Implement automated data validation checks (ranges, null checks, chronological order).
  - Produce clean, modeling-ready CSV.
- [ ] **Task 2: Train and Evaluate Baseline Price Model**
  - Partition historical records into chronological train/test splits.
  - Fit a linear regression baseline forecaster.
  - Benchmark performance using RMSE (Root Mean Squared Error) and MAE (Mean Absolute Error).
  - Serialize baseline model artifacts for persistent benchmarking.
- [ ] **Task 3: Feature Engineering and Model Optimization**
  - Engineer domain-specific features (lagged prices $t-1, t-7$, rolling averages, supply arrival volume, and weather indices).
  - Train advanced regressors and evaluate error reduction over baseline.
  - Extract and report feature importance rankings.
- [ ] **Task 4: Build and Test FastAPI Service**
  - Encapsulate the top-performing model in a RESTful FastAPI service.
  - Expose a `/predict` endpoint taking `crop_type` and target `date`.
  - Author robust automated unit test suites (`pytest`) handling valid and invalid inputs.
- [ ] **Task 5: Cloud Deployment & Handover Documentation**
  - Deploy the live FastAPI application to cloud hosting (e.g., Render / Railway).
  - Formulate a comprehensive Model Card documenting assumptions, performance bounds, and limitations.
  - Record a client demonstration video highlighting real-time forecasting.

---

## 📂 Project Structure

```plaintext
Crop-Price-Forecasting-API-for-GreenField-Farmers/
│
├── .gitignore               # Ignored environments (crop/, venv/) and cache files
├── README.md                # Comprehensive project documentation & architecture
├── requirements.txt         # Project dependencies
│
├── data/
│   ├── raw/                 # Ingested raw market arrival and price records
│   │   └── crop_prices_raw.csv
│   └── processed/           # Cleaned, standardized, and validated datasets (Task 1)
│
├── src/
│   ├── __init__.py
│   ├── download_dataset.py  # Script to ingest and prepare raw benchmark records
│   ├── data_pipeline.py     # Data cleaning, imputation, and date standardization
│   └── data_validator.py    # Automated dataset validation suite
│
├── models/                  # Serialized trained models and pipeline weights
├── notebooks/               # Exploratory Data Analysis (EDA) and experimentation
└── tests/                   # Automated API and model unit tests (pytest)
```

---

## ⚙️ Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Mushtaq0054/Crop-Price-Forecasting-API-for-GreenField-Farmers.git
cd Crop-Price-Forecasting-API-for-GreenField-Farmers
```

### 2. Activate the Virtual Environment
Using the designated `crop` virtual environment:

**Windows (PowerShell):**
```powershell
crop\Scripts\activate
```

**Windows (Command Prompt):**
```cmd
crop\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source crop/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 📊 Data Pipeline Preview

The initial raw dataset captures wholesale market price records across 2022–2024 for GreenField Farmers Co-op:
* **Target Commodities**: Wheat, Rice, Potato
* **Features Collected**: `Date`, `Crop`, `Market`, `Modal_Price_PKR`, `Min_Price_PKR`, `Max_Price_PKR`, `Market_Arrival_Tonnes`, `Rainfall_mm`, `Temperature_C`
* **Raw Artifacts**: Includes simulated real-world anomalies (heterogeneous date formats, missing prices, supply fluctuations) to be cleaned and validated in Task 1.

---

## 👨‍💻 Author & Acknowledgements

* **Author:** Mushtaq Ahmad
* **Program:** Machine Learning Internship Program, Ezitech Software House
* **Client Representative:** GreenField Farmers Co-op
