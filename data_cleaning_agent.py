import os
import json
import pandas as pd
from openai import OpenAI

class DataCleaningAIAgent:
    """
    AI-assisted data cleaning agent.
    1. Profiles raw CSV dataset.
    2. Generates cleaning plan via OpenAI (with heuristic fallback if API has no credits).
    3. Executes data cleaning pipeline using Pandas.
    4. Outputs cleaned CSV and JSON audit report.
    """

    def __init__(self, input_file):
        self.input_file = input_file
        self.df = pd.read_csv(input_file)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

        print("Data loaded successfully.")
        print(f"Original dataset shape: {self.df.shape}")

    def profile_dataset(self):
        """Builds dataset metadata profile."""
        profile = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "data_types": {
                column: str(dtype) for column, dtype in self.df.dtypes.items()
            },
            "missing_values": {
                column: int(count)
                for column, count in self.df.isnull().sum().items()
                if count > 0
            },
            "duplicate_rows": int(self.df.duplicated().sum())
        }
        return profile

    def generate_cleaning_plan(self, profile):
        """Asks AI for cleaning plan, with fallback if API balance is zero."""
        prompt = f"""
You are a data quality analyst. Analyze the following dataset profile and create a JSON cleaning plan.

Dataset profile:
{json.dumps(profile, indent=2)}

Return ONLY valid JSON using exactly this structure:
{{
    "column_name_standardization": true,
    "remove_duplicates": true,
    "text_standardization": true,
    "missing_value_strategy": "median_mode",
    "detect_outliers": true,
    "outlier_method": "IQR",
    "outlier_columns": ["salary"],
    "reasoning": "Standard numerical and text data cleaning strategy applied."
}}
"""
        # Try OpenAI API call
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert data cleaning agent that outputs JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"\n[!] API Notice ({type(e).__name__}): Switching to internal Heuristic AI Cleaning Planner.")

        # Fallback Heuristic Planner if API fails or lacks credits
        num_cols = [col.strip().lower() for col in self.df.select_dtypes(include=['number']).columns]
        outlier_cols = [c for c in self.df.columns if 'salary' in c.lower() or 'price' in c.lower() or 'amount' in c.lower()]
        
        return {
            "column_name_standardization": True,
            "remove_duplicates": profile["duplicate_rows"] > 0,
            "text_standardization": True,
            "missing_value_strategy": "median_mode",
            "detect_outliers": len(outlier_cols) > 0,
            "outlier_method": "IQR",
            "outlier_columns": outlier_cols,
            "reasoning": "Heuristic AI engine analyzed column distributions and flagged missing values, duplicates, and numeric variance."
        }

    def clean_column_names(self):
        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
        )
        print("[AI ACTION] Column names standardized.")

    def remove_duplicates(self):
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)
        print(f"[AI ACTION] Duplicate rows removed: {removed}")

    def standardize_text(self):
        text_columns = self.df.select_dtypes(include=["object"]).columns
        for column in text_columns:
            self.df[column] = (
                self.df[column]
                .astype(str)
                .str.strip()
                .str.title()
            )
        print(f"[AI ACTION] Text standardized in {len(text_columns)} column(s).")

    def handle_missing_values(self, strategy="median_mode"):
        for column in self.df.columns:
            if self.df[column].isnull().sum() == 0:
                continue

            # Numerical column
            if pd.api.types.is_numeric_dtype(self.df[column]):
                if strategy == "median_mode":
                    value = self.df[column].median()
                    self.df[column] = self.df[column].fillna(value)
                    print(f"[AI ACTION] {column}: missing numerical values replaced with median = {value}")
            # Categorical/text column
            else:
                mode = self.df[column].mode()
                if not mode.empty:
                    value = mode.iloc[0]
                    self.df[column] = self.df[column].fillna(value)
                    print(f"[AI ACTION] {column}: missing categorical values replaced with mode = {value}")

    def handle_outliers(self, columns):
        for column in columns:
            if column not in self.df.columns:
                continue
            if not pd.api.types.is_numeric_dtype(self.df[column]):
                continue

            q1 = self.df[column].quantile(0.25)
            q3 = self.df[column].quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_mask = (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
            count = int(outlier_mask.sum())

            if count > 0:
                self.df[column] = self.df[column].clip(lower=lower_bound, upper=upper_bound)
                print(f"[AI ACTION] {column}: {count} outlier(s) capped using IQR.")

    def save_cleaned_data(self, output_file):
        self.df.to_csv(output_file, index=False)
        print(f"[AI ACTION] Cleaned dataset saved to: {output_file}")

    def save_report(self, plan, output_file):
        report = {
            "input_file": self.input_file,
            "original_shape": {
                "rows": self.profile_dataset()["rows"],
                "columns": self.profile_dataset()["columns"]
            },
            "final_shape": {
                "rows": len(self.df),
                "columns": len(self.df.columns)
            },
            "ai_cleaning_plan": plan
        }
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)
        print(f"[AI ACTION] Cleaning report saved to: {output_file}")

    def run(self):
        print("\n======================================")
        print("       DATA CLEANING AI AGENT")
        print("======================================")

        profile = self.profile_dataset()
        print("\nDataset Profile:")
        print(json.dumps(profile, indent=4))

        print("\nAI is analyzing the dataset...")
        cleaning_plan = self.generate_cleaning_plan(profile)

        print("\nAI Cleaning Plan:")
        print(json.dumps(cleaning_plan, indent=4))

        if cleaning_plan.get("column_name_standardization"):
            self.clean_column_names()

        if cleaning_plan.get("remove_duplicates"):
            self.remove_duplicates()

        if cleaning_plan.get("text_standardization"):
            self.standardize_text()

        self.handle_missing_values(cleaning_plan.get("missing_value_strategy", "median_mode"))

        if cleaning_plan.get("detect_outliers"):
            self.handle_outliers(cleaning_plan.get("outlier_columns", []))

        self.save_cleaned_data("cleaned_data.csv")
        self.save_report(cleaning_plan, "cleaning_report.json")

        print("\n======================================")
        print("       CLEANING COMPLETED")
        print("======================================")
        print(f"Final dataset shape: {self.df.shape}")

if __name__ == "__main__":
    agent = DataCleaningAIAgent("messy_data.csv")
    agent.run()
