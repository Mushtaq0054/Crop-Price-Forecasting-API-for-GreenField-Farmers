"""
Script to download and save the raw crop price dataset for GreenField Farmers Co-op.
This script fetches or compiles historical market arrival and price records for the
top 3 crops: Wheat, Rice, and Potato.
"""

import os
import urllib.request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
RAW_DATA_PATH = os.path.join(DATA_DIR, "crop_prices_raw.csv")

def generate_benchmark_raw_dataset():
    """
    Creates a realistic multi-year raw dataset representing public wholesale market records
    with real-world artifacts (missing values, inconsistent date formats) for Task 1 cleaning.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    np.random.seed(42)

    start_date = datetime(2021, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    crops = ["Wheat", "Rice", "Potato"]
    
    # Baseline commodity economic profiles
    profiles = {
        "Wheat": {"base_price": 2800.0, "seasonal_amplitude": 350.0, "peak_month": 3, "base_arrival": 450.0},
        "Rice":  {"base_price": 3600.0, "seasonal_amplitude": 420.0, "peak_month": 10, "base_arrival": 520.0},
        "Potato": {"base_price": 1400.0, "seasonal_amplitude": 500.0, "peak_month": 1, "base_arrival": 680.0}
    }

    records = []

    for current_date in date_range:
        day_of_year = current_date.timetuple().tm_yday
        month = current_date.month
        year = current_date.year

        # Weather factors
        rainfall = max(0.0, float(np.random.exponential(scale=3.5 if month in [7, 8, 9] else 0.8)))
        temp = 22.0 + 12.0 * np.sin(2 * np.pi * (day_of_year - 100) / 365) + np.random.normal(0, 2.0)

        for crop in crops:
            p = profiles[crop]
            # Inflation & trend
            trend_factor = 1.0 + (year - 2021) * 0.06
            # Seasonal price variation (prices dip at harvest, rise during off-season)
            harvest_phase = 2 * np.pi * (month - p["peak_month"]) / 12.0
            seasonal_price_effect = -p["seasonal_amplitude"] * np.cos(harvest_phase)
            
            # Weather disruption impact
            weather_shock = 15.0 * (rainfall if rainfall > 15.0 else 0.0)
            noise = np.random.normal(0, 45.0)

            modal_price = round(float((p["base_price"] + seasonal_price_effect + weather_shock + noise) * trend_factor), 2)
            spread = max(30.0, round(float(modal_price * 0.04 + np.random.uniform(10, 30)), 2))
            min_price = round(modal_price - spread, 2)
            max_price = round(modal_price + spread, 2)

            # Market arrival (tonnes) - rises during harvest
            seasonal_arrival_effect = (p["base_arrival"] * 0.6) * np.cos(harvest_phase)
            arrival = max(50.0, round(float(p["base_arrival"] + seasonal_arrival_effect + np.random.normal(0, 40)), 2))

            # Simulate real-world raw data artifacts:
            # 1. Inconsistent date formats (YYYY-MM-DD vs DD/MM/YYYY vs MM-DD-YYYY)
            date_fmt_choice = np.random.choice([0, 1, 2], p=[0.75, 0.15, 0.10])
            if date_fmt_choice == 0:
                raw_date_str = current_date.strftime("%Y-%m-%d")
            elif date_fmt_choice == 1:
                raw_date_str = current_date.strftime("%d/%m/%Y")
            else:
                raw_date_str = current_date.strftime("%m-%d-%Y")

            # 2. Simulated missing values (~2% missing prices/arrivals)
            if np.random.rand() < 0.02:
                modal_price = np.nan
            if np.random.rand() < 0.015:
                arrival = np.nan

            records.append({
                "Date": raw_date_str,
                "Crop": crop,
                "Market": "GreenField Central Mandi",
                "Modal_Price_PKR": modal_price,
                "Min_Price_PKR": min_price,
                "Max_Price_PKR": max_price,
                "Market_Arrival_Tonnes": arrival,
                "Rainfall_mm": round(rainfall, 2),
                "Temperature_C": round(temp, 1)
            })

    df = pd.DataFrame(records)
    # Shuffle slightly to simulate out-of-order raw market receipts
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Raw dataset successfully saved to: {RAW_DATA_PATH}")
    print(f"Total raw records: {len(df)}")
    print(f"Crops covered: {df['Crop'].unique().tolist()}")
    return RAW_DATA_PATH

if __name__ == "__main__":
    generate_benchmark_raw_dataset()
