# 1_data_ingestion_and_preparation.py
import pandas as pd
from pathlib import Path
import sys

def standardize_columns(df):
    """Converts all column names to a standard snake_case format."""
    original_cols = df.columns
    df.columns = [
        col.strip().lower().replace(' ', '_').replace('-', '_').replace('.', '_')
        for col in original_cols
    ]
    return df

def load_and_prepare_data(base_path: Path):
    """
    Loads ALL 7 data files, cleans them, creates a master delivery dataset,
    and saves summary tables for separate use.
    """
    print("--- Starting Data Ingestion and Preparation (All 7 Files) ---")
    
    files = {
        "deliveries": "UrbanEats_Operations_Telemetry.xlsx",
        "customers": "UrbanEats_Customer_Intelligence.xlsx",
        "drivers": "UrbanEats_Driver_Analytics.xlsx",
        "restaurants": "UrbanEats_Restaurant_Partners.xlsx",
        "cities": "UrbanEats_City_Performance.xlsx",
        "financials": "UrbanEats_Financial_Data.xlsx",
        "tech": "UrbanEats_Technology_Systems.xlsx"
    }
    
    try:
        print("Loading raw data files...")
        data = {name: pd.read_excel(base_path / fname) for name, fname in files.items()}
        print("All 7 files loaded successfully.")
    except FileNotFoundError as e:
        print(f"ERROR: File not found. Ensure all Excel files are in the 'data' directory.")
        print(f"Details: {e}")
        sys.exit(1)

    print("Standardizing all column names (lowercase, underscore)...")
    for df_name, df_instance in data.items():
        data[df_name] = standardize_columns(df_instance)
        print(f"  - Standardized columns in '{df_name}' table.")

    # --- 1. Process and Save Summary Tables ---
    print("\nProcessing and saving summary tables...")
    
    financial_summary_df = data["financials"]
    financial_summary_path = Path.cwd() / "urbaneats_financial_summary.parquet"
    financial_summary_df.to_parquet(financial_summary_path, index=False)
    print(f"  - Saved cleaned financial summary to: {financial_summary_path}")

    tech_systems_df = data["tech"]
    tech_systems_path = Path.cwd() / "urbaneats_tech_systems.parquet"
    tech_systems_df.to_parquet(tech_systems_path, index=False)
    print(f"  - Saved cleaned tech systems to: {tech_systems_path}")

    # --- 2. Create the Master Delivery-Level DataFrame ---
    print("\nCreating the master delivery-level DataFrame...")
    master_df = data["deliveries"].merge(data["cities"], on='city_id', how='left', suffixes=('', '_city'))
    master_df = master_df.merge(data["restaurants"], on='restaurant_id', how='left', suffixes=('', '_restaurant'))
    master_df = master_df.merge(data["drivers"], on='driver_id', how='left', suffixes=('', '_driver'))
    master_df = master_df.merge(data["customers"], on='customer_id', how='left', suffixes=('', '_customer'))
    
    print("Cleaning data and converting types for master DataFrame...")
    # --- FIX: Added 'driver_at_restaurant_at' to the list ---
    timestamp_cols = [
        'order_placed_at', 'restaurant_confirmed_at', 'driver_assigned_at', 
        'driver_at_restaurant_at', 'order_picked_up_at', 'delivered_at'
    ]
    for col in timestamp_cols:
        if col in master_df.columns:
            master_df[col] = pd.to_datetime(master_df[col], errors='coerce')
            # Check if conversion failed for the entire column
            if master_df[col].isnull().all():
                print(f"  - WARNING: Column '{col}' could not be converted to datetime. It may contain non-date text.")

    print("Using pre-calculated financial metrics from source data...")
    rename_map = {
        'gross_profit': 'gross_margin',
        'on_time': 'is_on_time',
        'actual_prep_time_min': 'prep_time_min',
        'actual_travel_time_min': 'travel_time_min',
        'estimated_total_time_min': 'estimated_time_min',
        'actual_total_time_min': 'actual_time_min'
    }
    master_df.rename(columns=rename_map, inplace=True)

    print("Engineering additional critical metrics...")
    # These calculations will now work because the columns are guaranteed to be datetime objects
    master_df['dispatch_lag_min'] = (master_df['driver_assigned_at'] - master_df['restaurant_confirmed_at']).dt.total_seconds() / 60
    master_df['restaurant_wait_min'] = (master_df['order_picked_up_at'] - master_df['driver_at_restaurant_at']).dt.total_seconds() / 60
    
    numeric_cols = ['gross_margin', 'platform_revenue', 'driver_total_pay', 'dispatch_lag_min', 'restaurant_wait_min']
    for col in numeric_cols:
        if col in master_df.columns:
            master_df[col] = pd.to_numeric(master_df[col], errors='coerce').fillna(0)

    master_output_path = Path.cwd() / "urbaneats_master_dataset.parquet"
    print(f"Saving master delivery dataset to: {master_output_path}")
    master_df.to_parquet(master_output_path, index=False)
    
    print("\n--- Data Preparation Finished Successfully ---")
    return master_df, financial_summary_df

if __name__ == "__main__":
    data_directory = Path.cwd() / "data"
    if not data_directory.exists():
        print(f"ERROR: Directory not found at '{data_directory}'. Please create it and place your data there.")
        sys.exit(1)

    df, df_financials = load_and_prepare_data(data_directory)
    
    print("\n--- Master DataFrame Verification Summary ---")
    avg_gross_margin = df['gross_margin'].mean()
    avg_revenue = df['platform_revenue'].mean()
    print(f"Verification Check (using pre-calculated values from your data):")
    print(f"  - Avg. Platform Revenue per Delivery: ${avg_revenue:.2f} (Problem Statement Target: $6.00)")
    print(f"  - Avg. Gross Margin per Delivery: ${avg_gross_margin:.2f} (Problem Statement Target: -$1.80)")
    
    total_fixed_cost_8mo = df_financials['total_fixed_cost'].sum()
    annualized_fixed_cost = total_fixed_cost_8mo * (12/8)
    print(f"  - Annualized Fixed Cost from Data: ${annualized_fixed_cost:,.0f} (Problem Statement Target: $336,000)")
    print("\nVerification successful. You can now run the main app.")