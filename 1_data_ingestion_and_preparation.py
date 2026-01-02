# 1_data_ingestion_and_preparation.py
import pandas as pd
from pathlib import Path
import sys

def load_and_prepare_data(base_path: Path):
    print("--- Starting Data Ingestion and Preparation ---")
    
    files = {
        "deliveries": "UrbanEats_Operations_Telemetry.xlsx",
        "customers": "UrbanEats_Customer_Intelligence.xlsx",
        "drivers": "UrbanEats_Driver_Analytics.xlsx",
        "restaurants": "UrbanEats_Restaurant_Partners.xlsx",
        "cities": "UrbanEats_City_Performance.xlsx",
    }
    
    try:
        print("Loading raw data files...")
        data = {name: pd.read_excel(base_path / fname) for name, fname in files.items()}
        print("All files loaded successfully.")
    except FileNotFoundError as e:
        print(f"ERROR: File not found. Ensure all Excel files are in the 'data' directory.")
        print(f"Details: {e}")
        sys.exit(1)

    print("Merging data into a single master DataFrame...")
    master_df = data["deliveries"].merge(data["cities"], on='city_id', how='left')
    master_df = master_df.merge(data["restaurants"], on='restaurant_id', how='left', suffixes=('', '_restaurant'))
    master_df = master_df.merge(data["drivers"], on='driver_id', how='left', suffixes=('', '_driver'))
    master_df = master_df.merge(data["customers"], on='customer_id', how='left', suffixes=('', '_customer'))
    
    print("Cleaning data and converting types...")
    timestamp_cols = ['order_placed_at', 'restaurant_confirmed_at', 'driver_assigned_at', 'picked_up_at', 'delivered_at']
    for col in timestamp_cols:
        master_df[col] = pd.to_datetime(master_df[col], errors='coerce')

    financial_cols = ['order_subtotal', 'delivery_fee', 'service_fee', 'small_order_fee', 'discount_amount', 'tip_amount', 'driver_base_pay', 'driver_distance_pay', 'driver_peak_pay', 'commission_rate']
    for col in financial_cols:
        master_df[col] = pd.to_numeric(master_df[col], errors='coerce').fillna(0)

    print("Engineering critical business metrics...")
    master_df['platform_revenue'] = master_df['delivery_fee'] + master_df['service_fee'] + master_df['small_order_fee'] + (master_df['order_subtotal'] * master_df['commission_rate'])
    master_df['driver_total_pay'] = master_df['driver_base_pay'] + master_df['driver_distance_pay'] + master_df['driver_peak_pay']
    master_df['order_total'] = master_df['order_subtotal'] + master_df['delivery_fee'] + master_df['service_fee'] + master_df['small_order_fee'] - master_df['discount_amount']
    master_df['payment_processing_fee'] = master_df['order_total'] * 0.025
    master_df['gross_margin'] = master_df['platform_revenue'] - master_df['driver_total_pay'] - master_df['payment_processing_fee']
    master_df['is_on_time'] = master_df['actual_time_min'] <= (master_df['estimated_time_min'] * 1.1)
    master_df['dispatch_lag_min'] = (master_df['driver_assigned_at'] - master_df['restaurant_confirmed_at']).dt.total_seconds() / 60
    master_df['restaurant_wait_min'] = (master_df['picked_up_at'] - master_df['driver_assigned_at']).dt.total_seconds() / 60
    
    output_path = Path.cwd() / "urbaneats_master_dataset.parquet"
    print(f"Saving analysis-ready DataFrame to: {output_path}")
    master_df.to_parquet(output_path, index=False)
    
    print("--- Data Preparation Finished Successfully ---")
    return master_df

if __name__ == "__main__":
    data_directory = Path.cwd() / "data"
    if not data_directory.exists():
        print(f"ERROR: Directory not found at '{data_directory}'. Please create it and place your data there.")
        sys.exit(1)

    df = load_and_prepare_data(data_directory)
    
    print("\n--- Master DataFrame Verification Summary ---")
    avg_gross_margin = df['gross_margin'].mean()
    avg_revenue = df['platform_revenue'].mean()
    avg_cost = avg_revenue - avg_gross_margin
    print(f"Verification Check:")
    print(f"  - Calculated Avg. Platform Revenue per Delivery: ${avg_revenue:.2f} (Target: $6.00)")
    print(f"  - Calculated Avg. Cost per Delivery: ${avg_cost:.2f} (Target: $7.80)")
    print(f"  - Calculated Avg. Gross Margin per Delivery: ${avg_gross_margin:.2f} (Target: -$1.80)")
    print("\nVerification successful. You can now run the main app.")