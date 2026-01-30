# etl/data_cleaner.py
import pandas as pd

def clean_data(df):
    """
    Cleans and preprocesses the dataset.
    - Fills missing text fields with 'Unknown'
    - Fills missing numerical fields with median
    - Creates derived metric ProfitINR
    """
    # Fill missing object type columns
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].fillna("Unknown")

    # Fill missing numerical type columns
    for col in df.select_dtypes(include="number"):
        df[col] = df[col].fillna(df[col].median())

    # Create ProfitINR if Revenue & OperatingCost exist
    if "RevenueINR" in df.columns and "OperatingCostINR" in df.columns:
        df["ProfitINR"] = df["RevenueINR"] - df["OperatingCostINR"]

    return df
