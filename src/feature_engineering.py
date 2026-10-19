"""
Feature Engineering Pipeline for Crop Price Forecasting
Client: GreenField Farmers Co-op
Project: Crop Price Forecasting API for GreenField Farmers
Task 3: Create lag features, moving averages, supply pressure indices, and cyclical seasonality.
"""

import os
import pandas as pd
import numpy as np


class CropFeatureEngineer:
    """
    Transforms cleaned agricultural time-series data into feature-rich datasets
    incorporating price lags, rolling moving averages, supply volume momentum,
    weather indicators, and cyclical seasonal encodings.
    """

    def __init__(self, cleaned_data_path: str = None, engineered_data_path: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cleaned_data_path = cleaned_data_path or os.path.join(base_dir, "data", "processed", "crop_prices_cleaned.csv")
        self.engineered_data_path = engineered_data_path or os.path.join(base_dir, "data", "processed", "crop_prices_featured.csv")

    def load_data(self) -> pd.DataFrame:
        """Loads cleaned dataset."""
        if not os.path.exists(self.cleaned_data_path):
            raise FileNotFoundError(f"Cleaned data not found at: {self.cleaned_data_path}")
        df = pd.read_csv(self.cleaned_data_path)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by=["Crop", "Date"]).reset_index(drop=True)
        return df

    def create_lagged_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Creates price and market arrival lag features (t-1, t-2, t-4 weeks)."""
        df = df.copy()

        # Group-wise lags per crop
        for lag in [1, 2, 4]:
            df[f"Price_Lag_{lag}"] = df.groupby("Crop")["Modal_Price_PKR"].shift(lag)
            df[f"Arrival_Lag_{lag}"] = df.groupby("Crop")["Market_Arrival_Tonnes"].shift(lag)

        return df

    def create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Creates short-term and medium-term rolling moving averages and volatility."""
        df = df.copy()

        # Rolling Moving Averages (3-week and 6-week)
        df["Price_MA_3"] = df.groupby("Crop")["Modal_Price_PKR"].transform(lambda x: x.rolling(window=3, min_periods=1).mean())
        df["Price_MA_6"] = df.groupby("Crop")["Modal_Price_PKR"].transform(lambda x: x.rolling(window=6, min_periods=1).mean())

        # Rolling Volatility (4-week rolling standard deviation)
        df["Price_Volatility_4"] = df.groupby("Crop")["Modal_Price_PKR"].transform(lambda x: x.rolling(window=4, min_periods=1).std()).fillna(0.0)

        # Rolling Arrival Moving Average
        df["Arrival_MA_3"] = df.groupby("Crop")["Market_Arrival_Tonnes"].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

        return df

    def create_momentum_and_shock_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Creates price momentum (rate of change) and supply shock indicators."""
        df = df.copy()

        # 1-week Price Momentum: (P_t - P_{t-1}) / P_{t-1}
        df["Price_Momentum_1"] = ((df["Modal_Price_PKR"] - df["Price_Lag_1"]) / df["Price_Lag_1"]).fillna(0.0)

        # Supply Shock Index: Ratio of current arrival volume to 3-week average
        df["Supply_Shock_Index"] = (df["Market_Arrival_Tonnes"] / (df["Arrival_MA_3"] + 1e-5)).fillna(1.0)

        # Weather Indicators: 2-week rolling rainfall average & temperature anomaly
        df["Rainfall_MA_2"] = df.groupby("Crop")["Rainfall_mm"].transform(lambda x: x.rolling(window=2, min_periods=1).mean())
        temp_mean = df.groupby("Crop")["Temperature_C"].transform("mean")
        df["Temp_Anomaly"] = df["Temperature_C"] - temp_mean

        return df

    def create_cyclical_calendar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Encodes month of year using sine and cosine transformations to preserve
        cyclical harvest calendars without discontinuities between December and January.
        """
        df = df.copy()
        month = df["Date"].dt.month
        df["Month_Sin"] = np.sin(2 * np.pi * month / 12.0)
        df["Month_Cos"] = np.cos(2 * np.pi * month / 12.0)
        return df

    def build_featured_dataset(self) -> pd.DataFrame:
        """Executes full feature engineering pipeline and attaches next-week target."""
        df = self.load_data()
        df = self.create_lagged_features(df)
        df = self.create_rolling_features(df)
        df = self.create_momentum_and_shock_features(df)
        df = self.create_cyclical_calendar_features(df)

        # Target variable: next-week modal price (t+1)
        df["Target_Next_Week_Price"] = df.groupby("Crop")["Modal_Price_PKR"].shift(-1)

        # Drop initial rows with NaN due to 4-week lag and the final row per crop (unknown target)
        df_featured = df.dropna(subset=["Price_Lag_4", "Target_Next_Week_Price"]).copy()

        # Chronologically sort across dataset
        df_featured = df_featured.sort_values(by=["Date", "Crop"]).reset_index(drop=True)

        # Save featured CSV
        os.makedirs(os.path.dirname(self.engineered_data_path), exist_ok=True)
        df_featured.to_csv(self.engineered_data_path, index=False)

        print("[Feature Engineering] Successfully constructed domain features:")
        print(f"  * Total records: {len(df_featured)}")
        print(f"  * Total columns: {len(df_featured.columns)}")
        print(f"  * Output saved to: {self.engineered_data_path}")
        return df_featured


if __name__ == "__main__":
    engineer = CropFeatureEngineer()
    engineer.build_featured_dataset()
