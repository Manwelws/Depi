# main.py
"""
Main script to run the preprocessing pipeline for the Titanic dataset.
"""

from preprocessing import Read_data_file, Drop_unnecessary_features, Check_data_type
from config.config import data_path, cols_to_drop

def main():
    # Step 1: Read the dataset
    print("Step 1: Reading the dataset...")
    df = Read_data_file(data_path)
    if df is None:
        print("Failed to read dataset. Exiting.")
        return
    
    print(f"Successfully loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.\n")
    
    # Step 2: Inspect the dataset
    print("Step 2: Inspecting dataset structure...")
    info_df = Check_data_type(df)
    print(info_df)
    print("\n" + "="*80 + "\n")
    
    # Step 3: Drop unnecessary features
    print("Step 3: Dropping unnecessary features...")
    print(f"Columns to drop: {cols_to_drop}")
    df_clean = Drop_unnecessary_features(df, cols_to_drop)
    
    if df_clean is not None:
        print(f"Successfully dropped columns. New shape: {df_clean.shape}")
        
        # Step 4: Inspect the cleaned dataset
        print("\nStep 4: Inspecting cleaned dataset structure...")
        info_df_clean = Check_data_type(df_clean)
        print(info_df_clean)
    else:
        print("Failed to drop columns.")

if __name__ == "__main__":
    main()