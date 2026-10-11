"""
Automated Data Validation and Quality Assurance Script
Client: GreenField Farmers Co-op
Project: Crop Price Forecasting API for GreenField Farmers
Task 1 (Part 2): Data validation checks for missing values, date ranges, and price consistency.
"""

import os
import sys
import pandas as pd
import numpy as np


class CropDataValidator:
    """
    Validates the cleaned agricultural dataset to guarantee zero missing values,
    consistent chronological date ranges, and domain price sanity before model training.
    """

    def __init__(self, processed_data_path: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = processed_data_path or os.path.join(base_dir, "data", "processed", "crop_prices_cleaned.csv")
        self.expected_crops = {"Wheat", "Rice", "Potato"}
        self.validation_results = {}

    def load_dataset(self) -> pd.DataFrame:
        """Loads processed dataset from disk."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Cleaned dataset not found at: {self.data_path}")
        df = pd.read_csv(self.data_path)
        df["Date"] = pd.to_datetime(df["Date"])
        return df

    def check_missing_values(self, df: pd.DataFrame) -> bool:
        """Rule 1: Verify strictly 0 null/NaN values across all columns."""
        total_nulls = int(df.isna().sum().sum())
        passed = (total_nulls == 0)
        self.validation_results["Missing Values Check"] = {
            "Status": "PASSED" if passed else "FAILED",
            "Total Nulls": total_nulls,
            "Details": df.isna().sum().to_dict()
        }
        return passed

    def check_date_ranges_and_continuity(self, df: pd.DataFrame) -> bool:
        """Rule 2: Verify date ranges, format integrity, and chronological ordering."""
        min_date = df["Date"].min()
        max_date = df["Date"].max()
        is_sorted = df.groupby("Crop")["Date"].apply(lambda s: s.is_monotonic_increasing).all()
        
        # Check date boundary sanity (2022 to 2024 records present)
        range_valid = (min_date.year == 2022 and max_date.year == 2024)
        passed = bool(is_sorted and range_valid)

        self.validation_results["Date Ranges & Continuity Check"] = {
            "Status": "PASSED" if passed else "FAILED",
            "Start Date": str(min_date.date()),
            "End Date": str(max_date.date()),
            "Chronological Order Maintained": bool(is_sorted)
        }
        return passed

    def check_crop_coverage(self, df: pd.DataFrame) -> bool:
        """Rule 3: Ensure all top 3 crops for GreenField Farmers Co-op exist."""
        present_crops = set(df["Crop"].unique())
        passed = self.expected_crops.issubset(present_crops)
        crop_counts = df["Crop"].value_counts().to_dict()

        self.validation_results["Crop Coverage Check"] = {
            "Status": "PASSED" if passed else "FAILED",
            "Expected Crops": list(self.expected_crops),
            "Present Crops": list(present_crops),
            "Record Counts per Crop": crop_counts
        }
        return passed

    def check_price_sanity(self, df: pd.DataFrame) -> bool:
        """
        Rule 4: Verify price positivity and domain sanity:
        Min_Price_PKR <= Modal_Price_PKR <= Max_Price_PKR
        """
        positive_prices = (df["Modal_Price_PKR"] > 0).all() and (df["Min_Price_PKR"] > 0).all() and (df["Max_Price_PKR"] > 0).all()
        valid_bounds = ((df["Min_Price_PKR"] <= df["Modal_Price_PKR"]) & (df["Modal_Price_PKR"] <= df["Max_Price_PKR"])).all()
        passed = bool(positive_prices and valid_bounds)

        self.validation_results["Price Sanity & Boundary Check"] = {
            "Status": "PASSED" if passed else "FAILED",
            "All Prices > 0": bool(positive_prices),
            "Min <= Modal <= Max Verified": bool(valid_bounds),
            "Overall Price Range (PKR)": f"{df['Modal_Price_PKR'].min()} to {df['Modal_Price_PKR'].max()}"
        }
        return passed

    def check_feature_bounds(self, df: pd.DataFrame) -> bool:
        """Rule 5: Validate supply arrival volumes and environmental feature bounds."""
        valid_arrivals = (df["Market_Arrival_Tonnes"] > 0).all()
        valid_rain = (df["Rainfall_mm"] >= 0).all()
        valid_temp = ((df["Temperature_C"] >= -5) & (df["Temperature_C"] <= 55)).all()
        passed = bool(valid_arrivals and valid_rain and valid_temp)

        self.validation_results["Feature Bounds Check"] = {
            "Status": "PASSED" if passed else "FAILED",
            "Arrivals > 0": bool(valid_arrivals),
            "Rainfall >= 0": bool(valid_rain),
            "Realistic Temperatures": bool(valid_temp)
        }
        return passed

    def run_all_checks(self) -> bool:
        """Runs the entire test suite and prints formatted summary."""
        print("=" * 65)
        print(" GREENFIELD FARMERS CO-OP | DATA QUALITY VALIDATION SUITE ")
        print("=" * 65)

        df = self.load_dataset()
        print(f"Loaded dataset: {self.data_path}")
        print(f"Total verified records: {len(df)}")
        print("-" * 65)

        c1 = self.check_missing_values(df)
        c2 = self.check_date_ranges_and_continuity(df)
        c3 = self.check_crop_coverage(df)
        c4 = self.check_price_sanity(df)
        c5 = self.check_feature_bounds(df)

        all_passed = c1 and c2 and c3 and c4 and c5

        for check_name, info in self.validation_results.items():
            status_indicator = "[✔ PASSED]" if info["Status"] == "PASSED" else "[✖ FAILED]"
            print(f"{status_indicator} {check_name}")
            for k, v in info.items():
                if k != "Status":
                    print(f"     * {k}: {v}")
            print()

        print("=" * 65)
        if all_passed:
            print(">>> ALL DATA VALIDATION CHECKS PASSED SUCCESSFULLY (READY FOR TASK 2) <<<")
            print("=" * 65)
            return True
        else:
            print(">>> VALIDATION WARNING: ONE OR MORE CHECKS FAILED <<<")
            print("=" * 65)
            return False


if __name__ == "__main__":
    validator = CropDataValidator()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)
