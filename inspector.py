# inspector.py
import pandas as pd
from pathlib import Path

# --- Configuration ---
# This should point to the folder where your Excel files are.
# It assumes you run this script from the 'seed business' directory.
data_directory = Path.cwd() / "data"

# List of ALL 7 files we need to inspect
files_to_inspect = [
    "UrbanEats_Operations_Telemetry.xlsx",
    "UrbanEats_Customer_Intelligence.xlsx",
    "UrbanEats_Driver_Analytics.xlsx",
    "UrbanEats_Restaurant_Partners.xlsx",
    "UrbanEats_Financial_Data.xlsx",
    "UrbanEats_City_Performance.xlsx",
    "UrbanEats_Technology_Systems.xlsx"
]

print("--- UrbanEats Column Inspector (All 7 Files) ---")
print("Reading each file to extract column names...\n")

# Loop through each file, read it, and print its columns
for filename in files_to_inspect:
    try:
        file_path = data_directory / filename
        # Use read_excel since the files are .xlsx
        df = pd.read_excel(file_path)
        
        print(f"--- File: {filename} ---")
        print(df.columns.tolist())
        print("\n" + "="*50 + "\n") # Separator for clarity
        
    except FileNotFoundError:
        print(f"--- File: {filename} ---")
        print("!!! ERROR: FILE NOT FOUND. Please check the file name and location. !!!")
        print("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"--- File: {filename} ---")
        print(f"!!! An error occurred: {e} !!!")
        print("\n" + "="*50 + "\n")

print("--- Inspection Complete ---")