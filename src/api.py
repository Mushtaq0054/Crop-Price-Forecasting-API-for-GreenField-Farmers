"""
FastAPI Service for Crop Price Forecasting
Client: GreenField Farmers Co-op
Project: Crop Price Forecasting API for GreenField Farmers
Task 4: Build RESTful prediction API with automated validation and error handling.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator

# Initialize FastAPI App
app = FastAPI(
    title="GreenField Farmers Co-op - Crop Price Forecasting API",
    description="Production-grade Machine Learning API forecasting next-week wholesale commodity prices (Wheat, Rice, Potato).",
    version="1.0.0"
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "improved_crop_model.joblib")
FALLBACK_MODEL_PATH = os.path.join(BASE_DIR, "models", "baseline_linear_regression.joblib")
FEATURED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "crop_prices_featured.csv")

SUPPORTED_CROPS = ["Wheat", "Rice", "Potato"]

# Global model and reference cache
MODEL = None
LATEST_CROP_STATE = {}


def load_model_and_reference_data():
    """Loads the trained model and caches the latest observed state per crop."""
    global MODEL, LATEST_CROP_STATE

    # 1. Load Model
    if os.path.exists(MODEL_PATH):
        MODEL = joblib.load(MODEL_PATH)
        print(f"[API] Successfully loaded primary model: {MODEL_PATH}")
    elif os.path.exists(FALLBACK_MODEL_PATH):
        MODEL = joblib.load(FALLBACK_MODEL_PATH)
        print(f"[API Warning] Loaded fallback baseline model: {FALLBACK_MODEL_PATH}")
    else:
        print("[API Warning] No pre-trained model found on disk yet.")

    # 2. Load latest crop state for feature imputation
    if os.path.exists(FEATURED_DATA_PATH):
        df_feat = pd.read_csv(FEATURED_DATA_PATH)
        df_feat["Date"] = pd.to_datetime(df_feat["Date"])
        for crop in SUPPORTED_CROPS:
            crop_df = df_feat[df_feat["Crop"].str.lower() == crop.lower()].sort_values("Date")
            if not crop_df.empty:
                LATEST_CROP_STATE[crop] = crop_df.iloc[-1].to_dict()
        print(f"[API] Cached reference features for crops: {list(LATEST_CROP_STATE.keys())}")


@app.on_event("startup")
def startup_event():
    """Trigger model loading on server startup."""
    load_model_and_reference_data()


# -------------------------------------------------------------
# PYDANTIC SCHEMAS
# -------------------------------------------------------------
class PredictionRequest(BaseModel):
    crop: str = Field(..., example="Wheat", description="Crop name (Wheat, Rice, or Potato)")
    date: str = Field(..., example="2026-10-25", description="Forecast target date (YYYY-MM-DD)")
    current_price_pkr: Optional[float] = Field(None, description="Optional current wholesale price per quintal")
    market_arrival_tonnes: Optional[float] = Field(None, description="Optional current weekly market arrival in tonnes")
    rainfall_mm: Optional[float] = Field(None, description="Optional weekly rainfall in mm")
    temperature_c: Optional[float] = Field(None, description="Optional ambient temperature in Celsius")

    @validator("crop")
    def validate_crop_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Crop name must be a non-empty string.")
        formatted = v.strip().capitalize()
        if formatted not in SUPPORTED_CROPS:
            raise ValueError(f"Unsupported crop '{v}'. Supported crops are: {', '.join(SUPPORTED_CROPS)}")
        return formatted

    @validator("date")
    def validate_date_format(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Date string must be provided in YYYY-MM-DD format.")
        try:
            parsed = datetime.strptime(v.strip(), "%Y-%m-%d")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format '{v}'. Expected format: YYYY-MM-DD")


class ConfidenceRange(BaseModel):
    lower_bound: float
    upper_bound: float


class PredictionResponse(BaseModel):
    status: str
    crop: str
    target_date: str
    predicted_next_week_price_pkr: float
    confidence_interval_pkr: ConfidenceRange
    currency: str
    model_version: str


# -------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    """Root endpoint welcoming the client and confirming API status."""
    return {
        "status": "online",
        "service": "GreenField Farmers Co-op Crop Price Forecasting API",
        "version": "1.0.0",
        "supported_crops": SUPPORTED_CROPS,
        "docs_url": "/docs"
    }


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint checking model availability."""
    return {
        "status": "healthy" if MODEL is not None else "degraded",
        "model_loaded": MODEL is not None,
        "supported_crops": SUPPORTED_CROPS
    }


@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK, tags=["Forecasting"])
def predict_crop_price(request: PredictionRequest):
    """
    Predicts next-week wholesale commodity price based on crop type and date.
    Accepts crop type and date as input, with optional real-time weather and market arrivals.
    """
    global MODEL
    if MODEL is None:
        load_model_and_reference_data()
        if MODEL is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Forecasting model is not loaded. Please ensure models are trained and saved."
            )

    crop = request.crop
    target_date = datetime.strptime(request.date, "%Y-%m-%d")
    month = target_date.month

    # Retrieve cached latest feature benchmarks for the selected crop
    ref = LATEST_CROP_STATE.get(crop, {})

    # Base price values
    modal_price = request.current_price_pkr or float(ref.get("Modal_Price_PKR", 3000.0))
    min_price = modal_price * 0.96
    max_price = modal_price * 1.04
    arrival = request.market_arrival_tonnes or float(ref.get("Market_Arrival_Tonnes", 400.0))
    rainfall = request.rainfall_mm or float(ref.get("Rainfall_mm", 0.0))
    temp = request.temperature_c or float(ref.get("Temperature_C", 22.0))

    # Lag features (imputed from reference history or realistic offsets)
    price_lag_1 = float(ref.get("Price_Lag_1", modal_price * 0.99))
    price_lag_2 = float(ref.get("Price_Lag_2", modal_price * 0.98))
    price_lag_4 = float(ref.get("Price_Lag_4", modal_price * 0.97))
    arrival_lag_1 = float(ref.get("Arrival_Lag_1", arrival))
    arrival_lag_2 = float(ref.get("Arrival_Lag_2", arrival))
    arrival_lag_4 = float(ref.get("Arrival_Lag_4", arrival))

    # Moving averages and momentum
    price_ma_3 = (modal_price + price_lag_1 + price_lag_2) / 3.0
    price_ma_6 = float(ref.get("Price_MA_6", modal_price))
    price_vol_4 = float(ref.get("Price_Volatility_4", 25.0))
    arrival_ma_3 = (arrival + arrival_lag_1 + arrival_lag_2) / 3.0
    price_momentum_1 = (modal_price - price_lag_1) / (price_lag_1 + 1e-5)
    supply_shock_idx = arrival / (arrival_ma_3 + 1e-5)
    rainfall_ma_2 = rainfall
    temp_anomaly = temp - 22.0

    # Cyclical trigonometric features for target date
    month_sin = float(np.sin(2 * np.pi * month / 12.0))
    month_cos = float(np.cos(2 * np.pi * month / 12.0))

    # Construct feature payload DataFrame for model pipeline
    feature_payload = pd.DataFrame([{
        "Crop": crop,
        "Modal_Price_PKR": modal_price,
        "Min_Price_PKR": min_price,
        "Max_Price_PKR": max_price,
        "Market_Arrival_Tonnes": arrival,
        "Rainfall_mm": rainfall,
        "Temperature_C": temp,
        "Price_Lag_1": price_lag_1,
        "Price_Lag_2": price_lag_2,
        "Price_Lag_4": price_lag_4,
        "Arrival_Lag_1": arrival_lag_1,
        "Arrival_Lag_2": arrival_lag_2,
        "Arrival_Lag_4": arrival_lag_4,
        "Price_MA_3": price_ma_3,
        "Price_MA_6": price_ma_6,
        "Price_Volatility_4": price_vol_4,
        "Arrival_MA_3": arrival_ma_3,
        "Price_Momentum_1": price_momentum_1,
        "Supply_Shock_Index": supply_shock_idx,
        "Rainfall_MA_2": rainfall_ma_2,
        "Temp_Anomaly": temp_anomaly,
        "Month_Sin": month_sin,
        "Month_Cos": month_cos
    }])

    try:
        prediction = float(MODEL.predict(feature_payload)[0])
    except Exception as e:
        # Fallback if model expects Task 2 7-feature schema
        try:
            base_cols = ["Crop", "Modal_Price_PKR", "Min_Price_PKR", "Max_Price_PKR", "Market_Arrival_Tonnes", "Rainfall_mm", "Temperature_C"]
            prediction = float(MODEL.predict(feature_payload[base_cols])[0])
        except Exception:
            raise HTTPException(status_code=500, detail=f"Model prediction inference failed: {str(e)}")

    # Model confidence interval bounds (+/- MAE = ~18.95 PKR)
    mae_margin = 18.95
    lower_bound = round(max(0.0, prediction - mae_margin), 2)
    upper_bound = round(prediction + mae_margin, 2)
    predicted_val = round(prediction, 2)

    return PredictionResponse(
        status="success",
        crop=crop,
        target_date=request.date,
        predicted_next_week_price_pkr=predicted_val,
        confidence_interval_pkr=ConfidenceRange(
            lower_bound=lower_bound,
            upper_bound=upper_bound
        ),
        currency="PKR per Quintal",
        model_version="GradientBoostingRegressor_v1.0"
    )
