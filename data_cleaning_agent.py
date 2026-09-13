import pandas as pd
import numpy as np

class DataCleaningAgent:
    """
    An automated agent that identifies and cleans dirty data.
    It tracks changes and prints them to the console to maintain transparency.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        # Read the raw data
        self.df = pd.read_csv(filepath)
        self.original_shape = self.df.shape
        print(f"[*] Data loaded successfully. Initial shape: {self.original_shape}")

    def clean_column_names(self):
        """Standardizes column names (lowercase, no trailing spaces, spaces replaced by underscores)."""
        old_cols = list(self.df.columns)
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
        print(f"\n[+] Column names cleaned.\n    Old: {old_cols}\n    New: {list(self.df.columns)}")

    def remove_duplicates(self):
        """Identifies and removes duplicate rows."""
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        dropped = initial_rows - len(self.df)
        print(f"\n[+] Duplicates checked: {dropped} duplicate row(s) identified and removed.")

    def handle_missing_values(self):
        """Fills missing numeric values with the median and categorical/text values with the mode."""
        print("\n[+] Missing values handled:")
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                if self.df[col].dtype in ['int64', 'float64']:
                    # Use median for numeric to avoid outlier skew
                    median_val = self.df[col].median()
                    self.df[col] = self.df[col].fillna(median_val)
                    print(f"    - '{col}': {missing_count} missing value(s) replaced with median ({median_val}).")
                else:
                    # Use mode for text/categorical
                    mode_vals = self.df[col].mode()
                    if not mode_vals.empty:
                        mode_val = mode_vals[0]
                        self.df[col] = self.df[col].fillna(mode_val)
                        print(f"    - '{col}': {missing_count} missing value(s) replaced with mode ('{mode_val}').")

    def standardize_text(self):
        """Removes whitespace padding and formats text columns properly."""
        print("\n[+] Text standardization:")
        count = 0
        for col in self.df.select_dtypes(include=['object']).columns:
            self.df[col] = self.df[col].astype(str).str.strip().str.title()
            count += 1
        print(f"    - Cleaned casing and whitespaces across {count} text columns.")

    def handle_outliers(self, column, threshold=1.5):
        """Caps extreme outliers using the Interquartile Range (IQR) method."""
        if column not in self.df.columns:
            return

        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        # Identify outliers
        outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)]
        outlier_count = len(outliers)
        
        # Cap the outliers to the upper/lower bounds
        self.df.loc[self.df[column] < lower_bound, column] = lower_bound
        self.df.loc[self.df[column] > upper_bound, column] = upper_bound
        
        if outlier_count > 0:
            print(f"\n[+] Outliers handled in '{column}': {outlier_count} extreme value(s) capped using IQR.")

    def run_pipeline(self, output_filepath):
        """Executes the full cleaning pipeline."""
        print("\n" + "="*40)
        print("  STARTING DATA CLEANING PIPELINE")
        print("="*40)
        
        self.clean_column_names()
        self.remove_duplicates()
        self.handle_missing_values()
        self.standardize_text()
        
        # Apply outlier detection specifically on the salary column
        if 'salary' in self.df.columns:
            self.handle_outliers('salary')
            
        print("\n" + "="*40)
        print("  PIPELINE COMPLETE")
        print("="*40)
        print(f"[*] Final dataset shape: {self.df.shape}")
        
        self.df.to_csv(output_filepath, index=False)
        print(f"[*] Cleaned data saved successfully to: {output_filepath}")
        return self.df

if __name__ == "__main__":
    # Initialize the agent with the raw dataset
    agent = DataCleaningAgent("messy_data.csv")
    # Run the pipeline and output the clean dataset
    cleaned_df = agent.run_pipeline("cleaned_data.csv")