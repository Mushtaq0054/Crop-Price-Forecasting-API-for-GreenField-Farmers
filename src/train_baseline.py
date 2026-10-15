"""
Baseline Model Training and Evaluation Pipeline
Client: GreenField Farmers Co-op
Project: Crop Price Forecasting API for GreenField Farmers
Task 2: Train and evaluate baseline price model (Linear Regression vs Naive Baseline).
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class BaselineModelTrainer:
    """
    Trains a baseline Linear Regression model to forecast next-week crop prices,
    evaluates it against a simple Naive Persistence baseline, and serializes artifacts.
    """

    def __init__(self, data_path: str = None, models_dir: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = data_path or os.path.join(base_dir, "data", "processed", "crop_prices_cleaned.csv")
        self.models_dir = models_dir or os.path.join(base_dir, "models")
        os.makedirs(self.models_dir, exist_ok=True)

        self.model_save_path = os.path.join(self.models_dir, "baseline_linear_regression.joblib")
        self.metrics_save_path = os.path.join(self.models_dir, "baseline_metrics.json")

    def load_and_prepare_target(self) -> pd.DataFrame:
        """
        Loads cleaned dataset and creates next-week target variable
        (Target_Next_Week_Price = Modal_Price at t+1 week per crop).
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Cleaned data not found at: {self.data_path}")

        df = pd.read_csv(self.data_path)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by=["Crop", "Date"]).reset_index(drop=True)

        # Create next-week target for each crop
        df["Target_Next_Week_Price"] = df.groupby("Crop")["Modal_Price_PKR"].shift(-1)

        # Drop the last record per crop because next week target is unknown
        df_model = df.dropna(subset=["Target_Next_Week_Price"]).copy()
        # Sort chronologically by date for realistic time-series validation
        df_model = df_model.sort_values(by=["Date", "Crop"]).reset_index(drop=True)

        print(f"[Data Prep] Processed {len(df_model)} samples with next-week target price.")
        return df_model

    def chronological_train_test_split(self, df: pd.DataFrame, train_ratio: float = 0.80):
        """
        Splits data chronologically to strictly respect temporal ordering
        and prevent future data leakage.
        """
        unique_dates = df["Date"].drop_duplicates().sort_values().reset_index(drop=True)
        split_idx = int(len(unique_dates) * train_ratio)
        cutoff_date = unique_dates.iloc[split_idx]

        train_mask = df["Date"] < cutoff_date
        test_mask = df["Date"] >= cutoff_date

        train_df = df[train_mask].copy()
        test_df = df[test_mask].copy()

        print(f"[Split] Chronological Split at Cutoff Date: {cutoff_date.date()}")
        print(f"        Train set: {len(train_df)} samples ({train_df['Date'].min().date()} to {train_df['Date'].max().date()})")
        print(f"        Test set:  {len(test_df)} samples ({test_df['Date'].min().date()} to {test_df['Date'].max().date()})")

        return train_df, test_df

    def train_and_evaluate(self):
        """
        Trains Linear Regression pipeline, benchmarks against Naive Persistence baseline,
        and saves serialized model and metrics.
        """
        df = self.load_and_prepare_target()
        train_df, test_df = self.chronological_train_test_split(df, train_ratio=0.80)

        feature_cols = [
            "Crop",
            "Modal_Price_PKR",
            "Min_Price_PKR",
            "Max_Price_PKR",
            "Market_Arrival_Tonnes",
            "Rainfall_mm",
            "Temperature_C"
        ]
        target_col = "Target_Next_Week_Price"

        X_train = train_df[feature_cols]
        y_train = train_df[target_col]
        X_test = test_df[feature_cols]
        y_test = test_df[target_col]

        # -------------------------------------------------------------
        # 1. NAIVE PERSISTENCE BASELINE (y_hat_t+1 = y_t)
        # -------------------------------------------------------------
        # Predicts next week's price will be exactly this week's modal price
        y_pred_naive = test_df["Modal_Price_PKR"].values

        naive_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_naive)))
        naive_mae = float(mean_absolute_error(y_test, y_pred_naive))
        naive_r2 = float(r2_score(y_test, y_pred_naive))
        naive_mape = float(np.mean(np.abs((y_test - y_pred_naive) / y_test)) * 100)

        # -------------------------------------------------------------
        # 2. LINEAR REGRESSION PIPELINE
        # -------------------------------------------------------------
        categorical_features = ["Crop"]
        numeric_features = [
            "Modal_Price_PKR",
            "Min_Price_PKR",
            "Max_Price_PKR",
            "Market_Arrival_Tonnes",
            "Rainfall_mm",
            "Temperature_C"
        ]

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(drop="first", sparse_output=False), categorical_features),
                ("num", StandardScaler(), numeric_features)
            ]
        )

        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression())
        ])

        pipeline.fit(X_train, y_train)
        y_pred_lr = pipeline.predict(X_test)

        lr_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_lr)))
        lr_mae = float(mean_absolute_error(y_test, y_pred_lr))
        lr_r2 = float(r2_score(y_test, y_pred_lr))
        lr_mape = float(np.mean(np.abs((y_test - y_pred_lr) / y_test)) * 100)

        # -------------------------------------------------------------
        # 3. PER-CROP EVALUATION BREAKDOWN
        # -------------------------------------------------------------
        crop_breakdown = {}
        for crop in df["Crop"].unique():
            crop_mask = (test_df["Crop"] == crop)
            y_t_crop = y_test[crop_mask]
            y_p_crop = y_pred_lr[crop_mask]
            crop_breakdown[crop] = {
                "RMSE": round(float(np.sqrt(mean_squared_error(y_t_crop, y_p_crop))), 2),
                "MAE": round(float(mean_absolute_error(y_t_crop, y_p_crop)), 2),
                "R2": round(float(r2_score(y_t_crop, y_p_crop)), 4)
            }

        # -------------------------------------------------------------
        # 4. REPORTING AND SERIALIZATION
        # -------------------------------------------------------------
        metrics_report = {
            "Naive_Persistence_Baseline": {
                "RMSE": round(naive_rmse, 2),
                "MAE": round(naive_mae, 2),
                "R2_Score": round(naive_r2, 4),
                "MAPE_Percent": round(naive_mape, 2)
            },
            "Linear_Regression_Model": {
                "RMSE": round(lr_rmse, 2),
                "MAE": round(lr_mae, 2),
                "R2_Score": round(lr_r2, 4),
                "MAPE_Percent": round(lr_mape, 2)
            },
            "Performance_Improvement": {
                "RMSE_Reduction_Percent": round(((naive_rmse - lr_rmse) / naive_rmse) * 100, 2),
                "MAE_Reduction_Percent": round(((naive_mae - lr_mae) / naive_mae) * 100, 2)
            },
            "Per_Crop_Breakdown_Linear_Regression": crop_breakdown,
            "Dataset_Split_Info": {
                "Train_Samples": len(train_df),
                "Test_Samples": len(test_df),
                "Cutoff_Date": str(test_df["Date"].min().date())
            }
        }

        # Save model and metrics
        joblib.dump(pipeline, self.model_save_path)
        with open(self.metrics_save_path, "w") as f:
            json.dump(metrics_report, f, indent=4)

        print("\n" + "=" * 65)
        print(" GREENFIELD FARMERS CO-OP | TASK 2 BASELINE MODEL EVALUATION ")
        print("=" * 65)
        print(f"Model File Saved:   {self.model_save_path}")
        print(f"Metrics File Saved: {self.metrics_save_path}")
        print("-" * 65)
        print(f"{'Metric':<18} | {'Naive Persistence':<20} | {'Linear Regression':<20}")
        print("-" * 65)
        print(f"{'RMSE (PKR)':<18} | {naive_rmse:<20.2f} | {lr_rmse:<20.2f}")
        print(f"{'MAE (PKR)':<18} | {naive_mae:<20.2f} | {lr_mae:<20.2f}")
        print(f"{'R2 Score':<18} | {naive_r2:<20.4f} | {lr_r2:<20.4f}")
        print(f"{'MAPE (%)':<18} | {naive_mape:<20.2f} | {lr_mape:<20.2f}")
        print("=" * 65)
        print(f"Per-Crop Breakdown (Linear Regression):")
        for crop, m in crop_breakdown.items():
            print(f"  * {crop:<8}: RMSE={m['RMSE']} PKR, MAE={m['MAE']} PKR, R2={m['R2']}")
        print("=" * 65)

        return metrics_report


if __name__ == "__main__":
    trainer = BaselineModelTrainer()
    trainer.train_and_evaluate()
