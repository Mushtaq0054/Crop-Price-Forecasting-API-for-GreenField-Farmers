"""
Data Cleaning and Preprocessing Pipeline
Client: GreenField Farmers Co-op
Project: Crop Price Forecasting API for GreenField Farmers
Task 1 (Part 1): Clean missing values, standardize dates, and save processed CSV.
"""

import os
import pandas as pd
import numpy as np


class CropDataPipeline:
    """
    Pipeline responsible for loading raw agricultural price records,
    standardizing heterogeneous date formats, handling missing entries,
    and outputting modeling-ready datasets.
    """

    def __init__(self, raw_data_path: str = None, processed_data_path: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.raw_data_path = raw_data_path or os.path.join(base_dir, "data", "raw", "crop_prices_raw.csv")
        self.processed_data_path = processed_data_path or os.path.join(base_dir, "data", "processed", "crop_prices_cleaned.csv")

    def load_raw_data(self) -> pd.DataFrame:
        """Loads raw data from disk."""
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Raw data file not found at: {self.raw_data_path}")
        df = pd.read_csv(self.raw_data_path)
        print(f"[Pipeline] Successfully loaded raw dataset with {len(df)} records.")
        return df

    def standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes diverse date strings (%Y-%m-%d, %d/%m/%Y, %m-%d-%Y)
        into uniform ISO datetime objects (YYYY-MM-DD).
        """
        print("[Pipeline] Standardizing date formats...")
        df = df.copy()
        
        # Use pandas to_datetime with flexible parsing
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=False)
        
        # Verify no failed date conversions
        invalid_dates = df["Date"].isna().sum()
        if invalid_dates > 0:
            print(f"[Pipeline Warning] Found {invalid_dates} unparseable dates. Dropping invalid rows.")
            df = df.dropna(subset=["Date"])

        # Format as standard YYYY-MM-DD
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        df["Date"] = pd.to_datetime(df["Date"])
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans missing values using domain-appropriate time-series interpolation:
        - Missing Modal_Price: Forward-fill / linear time interpolation per crop
        - Missing Market_Arrival_Tonnes: Crop-specific rolling median imputation
        - Min / Max price boundary alignment
        """
        print("[Pipeline] Handling missing values and null entries...")
        df = df.copy()

        # Sort chronologically by Crop and Date
        df = df.sort_values(by=["Crop", "Date"]).reset_index(drop=True)

        cleaned_dfs = []
        for crop, group in df.groupby("Crop"):
            group = group.copy()

            # Time-series interpolation for Modal Price
            group["Modal_Price_PKR"] = group["Modal_Price_PKR"].interpolate(method="linear").bfill().ffill()

            # Impute missing arrival volumes with crop median
            arrival_median = group["Market_Arrival_Tonnes"].median()
            group["Market_Arrival_Tonnes"] = group["Market_Arrival_Tonnes"].fillna(arrival_median)

            # Ensure logical consistency: Min_Price <= Modal_Price <= Max_Price
            group["Min_Price_PKR"] = group["Min_Price_PKR"].fillna(group["Modal_Price_PKR"] * 0.95)
            group["Max_Price_PKR"] = group["Max_Price_PKR"].fillna(group["Modal_Price_PKR"] * 1.05)

            group["Min_Price_PKR"] = np.minimum(group["Min_Price_PKR"], group["Modal_Price_PKR"])
            group["Max_Price_PKR"] = np.maximum(group["Max_Price_PKR"], group["Modal_Price_PKR"])

            # Weather features zero-fill if null
            group["Rainfall_mm"] = group["Rainfall_mm"].fillna(0.0)
            group["Temperature_C"] = group["Temperature_C"].interpolate(method="linear").bfill()

            cleaned_dfs.append(group)

        cleaned_df = pd.concat(cleaned_dfs, ignore_index=True)
        # Sort chronologically across the entire dataset
        cleaned_df = cleaned_df.sort_values(by=["Date", "Crop"]).reset_index(drop=True)
        return cleaned_df

    def run_pipeline(self) -> pd.DataFrame:
        """Executes full cleaning workflow and exports processed CSV."""
        df_raw = self.load_raw_data()
        df_dated = self.standardize_dates(df_raw)
        df_cleaned = self.handle_missing_values(df_dated)

        # Ensure processed directory exists
        os.makedirs(os.path.dirname(self.processed_data_path), exist_ok=True)
        df_cleaned.to_csv(self.processed_data_path, index=False)
        print(f"[Pipeline] Cleaned dataset saved to: {self.processed_data_path}")
        print(f"[Pipeline] Final shape: {df_cleaned.shape}")
        print(f"[Pipeline] Remaining missing values: {df_cleaned.isna().sum().sum()}")
        return df_cleaned


if __name__ == "__main__":
    pipeline = CropDataPipeline()
    pipeline.run_pipeline()
