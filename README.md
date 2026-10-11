# Crop Price Forecasting API for GreenField Farmers

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Data Pipeline](https://img.shields.io/badge/Pipeline-Validated-success.svg)](data/processed/crop_prices_cleaned.csv)
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
  - Downloaded and ingested multi-year raw wholesale market price records.
  - Built an automated data cleaning script (`src/data_pipeline.py`) handling missing values and standardizing dates.
  - Implemented an automated data validation suite (`src/data_validator.py`) verifying 5 key data quality rules.
  - Generated modeling-ready dataset committed at `data/processed/crop_prices_cleaned.csv`.
- [ ] **Task 2: Train and Evaluate Baseline Price Model**
  - Chronological train/test split.
  - Train baseline Linear Regression model.
  - Evaluate performance using RMSE and MAE.
  - Serialize baseline model artifact for comparison.
- [ ] **Task 3: Feature Engineering and Model Improvement**
  - Create lag features ($t-1, t-7$), rolling moving averages, and weather/supply indicators.
  - Retrain advanced regressors and evaluate error reduction.
  - Calculate and report feature importance rankings.
- [ ] **Task 4: Build and Test FastAPI Service**
  - Wrap top model into FastAPI with a `/predict` endpoint.
  - Automated unit test suite using `pytest` (valid and invalid inputs).
  - Return clean JSON prediction responses.
- [ ] **Task 5: Deploy API and Write Handover Docs**
  - Cloud deployment to a free host (Render / Railway).
  - Client handover documentation, Model Card, and demonstration video.

---

## 📊 Task 1: Data Preparation, Cleaning & Validation

### 1. Data Source & Collection
The dataset covers weekly wholesale market arrivals and prices from 2022 to 2024 for GreenField Farmers Co-op's top 3 staple crops:
* **Target Crops**: Wheat, Rice (Paddy), Potato
* **Wholesale Market**: GreenField Central Mandi
* **Features Included**:
  * `Date`: Reporting date of market transaction
  * `Crop`: Commodity identifier (Wheat, Rice, Potato)
  * `Market`: Reporting wholesale mandi
  * `Modal_Price_PKR`: Prevailing wholesale price per quintal (PKR) at which the highest volume was traded
  * `Min_Price_PKR` & `Max_Price_PKR`: Observed quality price range
  * `Market_Arrival_Tonnes`: Weekly supply arrival volume in metric tonnes
  * `Rainfall_mm`: Weekly cumulative precipitation
  * `Temperature_C`: Average ambient temperature in Celsius

### 2. Data Cleaning Steps Performed (`src/data_pipeline.py`)
Raw agricultural datasets often suffer from reporting discrepancies. The automated pipeline performed:
1. **Date Standardization**: Standardized varied calendar formats (`%d/%m/%Y`, `%m-%d-%Y`, `%Y-%m-%d`) into uniform ISO-8601 (`YYYY-MM-DD`) datetimes and verified chronological ordering.
2. **Missing Price Imputation**: Missing `Modal_Price_PKR` records were imputed via **linear time-series interpolation** per crop group to ensure trend continuity without introducing statistical bias.
3. **Supply Arrival Imputation**: Null arrival quantities were imputed with the rolling median of the corresponding crop.
4. **Price Boundary Alignment**: Verified and enforced the business constraint that `Min_Price_PKR <= Modal_Price_PKR <= Max_Price_PKR`.
5. **Weather Imputation**: Null rainfall figures were set to `0.0` mm and temperatures linearly interpolated.

### 3. Data Quality & Validation Results (`src/data_validator.py`)
All 5 automated validation checks passed successfully:

| Check Name | Target Requirement | Status | Result / Details |
| :--- | :--- | :---: | :--- |
| **Missing Values Check** | Strictly 0 null values across all columns | **PASSED** | 0 nulls remaining |
| **Date Range & Continuity** | Records span 2022-01-03 to 2024-12-30 monotonically | **PASSED** | Monotonic ordering verified |
| **Crop Coverage Check** | Presence of all top 3 crops | **PASSED** | Wheat (157), Rice (157), Potato (157) |
| **Price Sanity & Spread** | Prices > 0 and Min <= Modal <= Max | **PASSED** | Range: PKR 1,010.0 to 4,890.0 |
| **Feature Bounds Check** | Arrivals > 0, Rainfall >= 0, realistic temps | **PASSED** | All environmental limits verified |

---

## 📂 Project Structure

```plaintext
Crop-Price-Forecasting-API-for-GreenField-Farmers/
│
├── .gitignore               # Excludes virtual environments (crop/, venv/) and cache
├── README.md                # Project documentation and Task 1 validation report
├── requirements.txt         # Project dependencies
├── submission_note.txt      # Formatted task submission note for mentor portal
│
├── data/
│   ├── raw/                 # Raw market arrivals and price records
│   │   └── crop_prices_raw.csv
│   └── processed/           # Cleaned, standardized, and validated dataset
│       └── crop_prices_cleaned.csv
│
├── notebooks/
│   └── 01_data_cleaning_and_validation.ipynb  # Interactive EDA and validation notebook
│
├── src/
│   ├── __init__.py
│   ├── download_dataset.py  # Benchmark raw dataset generator/fetcher
│   ├── data_pipeline.py     # Automated data cleaning and date standardization
│   └── data_validator.py    # Automated data quality checks
│
├── models/                  # Serialized models (Task 2 & 3)
└── tests/                   # Automated API test suite (Task 4)
```

---

## ⚙️ Installation & How to Run

### 1. Setup Virtual Environment
```powershell
# Activate the existing crop virtual environment
crop\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Run Data Cleaning Pipeline
To process raw data and produce the cleaned CSV:
```bash
python -m src.data_pipeline
```

### 3. Run Data Quality Validation Suite
To execute all automated validation rules:
```bash
python -m src.data_validator
```

---

## 👨‍💻 Author & Acknowledgements

* **Author:** Mushtaq Ahmad
* **Program:** Machine Learning Internship Program, Ezitech Software House
* **Client Representative:** GreenField Farmers Co-op
