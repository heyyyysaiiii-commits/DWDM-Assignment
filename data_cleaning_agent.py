import os
import json
import pandas as pd
from openai import OpenAI


class DataCleaningAIAgent:
    """
    AI-assisted data cleaning agent.

    The agent:
    1. Loads and profiles a messy dataset.
    2. Sends the profile to an AI model.
    3. Receives recommended cleaning actions.
    4. Applies those actions using Pandas.
    5. Generates a cleaned dataset and cleaning report.
    """

    def __init__(self, input_file):
        self.input_file = input_file
        self.df = pd.read_csv(input_file)

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        print("Data loaded successfully.")
        print(f"Original dataset shape: {self.df.shape}")

    # ---------------------------------------------------------
    # 1. PROFILE THE DATASET
    # ---------------------------------------------------------
    def profile_dataset(self):
        profile = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "data_types": {
                column: str(dtype)
                for column, dtype in self.df.dtypes.items()
            },
            "missing_values": {
                column: int(count)
                for column, count in self.df.isnull().sum().items()
                if count > 0
            },
            "duplicate_rows": int(self.df.duplicated().sum())
        }

        return profile

    # ---------------------------------------------------------
    # 2. ASK AI FOR CLEANING PLAN
    # ---------------------------------------------------------
    def generate_cleaning_plan(self, profile):

        prompt = f"""
You are a data quality analyst.

Analyze the following dataset profile and create a JSON cleaning plan.

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
    "outlier_columns": [],
    "reasoning": "Brief explanation of the selected cleaning strategy."
}}

Rules:
- Use median_mode for datasets containing numerical and categorical columns.
- Use IQR for numerical outlier detection.
- Add numerical columns that appear suitable for outlier analysis to outlier_columns.
- Do not invent column names.
- Keep the response as valid JSON only.
"""

        response = self.client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        return json.loads(response.output_text)

    # ---------------------------------------------------------
    # 3. STANDARDIZE COLUMN NAMES
    # ---------------------------------------------------------
    def clean_column_names(self):

        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
        )

        print("[AI ACTION] Column names standardized.")

    # ---------------------------------------------------------
    # 4. REMOVE DUPLICATES
    # ---------------------------------------------------------
    def remove_duplicates(self):

        before = len(self.df)

        self.df = self.df.drop_duplicates()

        removed = before - len(self.df)

        print(
            f"[AI ACTION] Duplicate rows removed: {removed}"
        )

    # ---------------------------------------------------------
    # 5. STANDARDIZE TEXT
    # ---------------------------------------------------------
    def standardize_text(self):

        text_columns = self.df.select_dtypes(
            include=["object"]
        ).columns

        for column in text_columns:
            self.df[column] = (
                self.df[column]
                .astype(str)
                .str.strip()
                .str.title()
            )

        print(
            f"[AI ACTION] Text standardized in "
            f"{len(text_columns)} column(s)."
        )

    # ---------------------------------------------------------
    # 6. HANDLE MISSING VALUES
    # ---------------------------------------------------------
    def handle_missing_values(self, strategy="median_mode"):

        for column in self.df.columns:

            if self.df[column].isnull().sum() == 0:
                continue

            # Numerical column
            if pd.api.types.is_numeric_dtype(self.df[column]):

                if strategy == "median_mode":
                    value = self.df[column].median()
                    self.df[column] = self.df[column].fillna(value)

                    print(
                        f"[AI ACTION] {column}: "
                        f"missing numerical values replaced "
                        f"with median = {value}"
                    )

            # Categorical/text column
            else:

                mode = self.df[column].mode()

                if not mode.empty:
                    value = mode.iloc[0]
                    self.df[column] = self.df[column].fillna(value)

                    print(
                        f"[AI ACTION] {column}: "
                        f"missing categorical values replaced "
                        f"with mode = {value}"
                    )

    # ---------------------------------------------------------
    # 7. HANDLE OUTLIERS USING IQR
    # ---------------------------------------------------------
    def handle_outliers(self, columns):

        for column in columns:

            if column not in self.df.columns:
                continue

            if not pd.api.types.is_numeric_dtype(
                self.df[column]
            ):
                continue

            q1 = self.df[column].quantile(0.25)
            q3 = self.df[column].quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_mask = (
                (self.df[column] < lower_bound) |
                (self.df[column] > upper_bound)
            )

            count = int(outlier_mask.sum())

            if count > 0:

                self.df[column] = self.df[column].clip(
                    lower=lower_bound,
                    upper=upper_bound
                )

                print(
                    f"[AI ACTION] {column}: "
                    f"{count} outlier(s) capped using IQR."
                )

    # ---------------------------------------------------------
    # 8. SAVE CLEANED DATA
    # ---------------------------------------------------------
    def save_cleaned_data(self, output_file):

        self.df.to_csv(output_file, index=False)

        print(
            f"[AI ACTION] Cleaned dataset saved to: "
            f"{output_file}"
        )

    # ---------------------------------------------------------
    # 9. SAVE AI CLEANING REPORT
    # ---------------------------------------------------------
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

        print(
            f"[AI ACTION] Cleaning report saved to: "
            f"{output_file}"
        )

    # ---------------------------------------------------------
    # 10. COMPLETE AI PIPELINE
    # ---------------------------------------------------------
    def run(self):

        print("\n======================================")
        print("       DATA CLEANING AI AGENT")
        print("======================================")

        # Profile raw dataset
        profile = self.profile_dataset()

        print("\nDataset Profile:")
        print(json.dumps(profile, indent=4))

        # Ask AI to decide cleaning strategy
        print("\nAI is analyzing the dataset...")

        cleaning_plan = self.generate_cleaning_plan(profile)

        print("\nAI Cleaning Plan:")
        print(json.dumps(cleaning_plan, indent=4))

        # Apply AI-recommended actions
        if cleaning_plan["column_name_standardization"]:
            self.clean_column_names()

        if cleaning_plan["remove_duplicates"]:
            self.remove_duplicates()

        if cleaning_plan["text_standardization"]:
            self.standardize_text()

        self.handle_missing_values(
            cleaning_plan["missing_value_strategy"]
        )

        if cleaning_plan["detect_outliers"]:
            self.handle_outliers(
                cleaning_plan["outlier_columns"]
            )

        # Save outputs
        self.save_cleaned_data(
            "cleaned_data.csv"
        )

        self.save_report(
            cleaning_plan,
            "cleaning_report.json"
        )

        print("\n======================================")
        print("       CLEANING COMPLETED")
        print("======================================")

        print(
            f"Final dataset shape: {self.df.shape}"
        )


# ---------------------------------------------------------
# PROGRAM ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":

    agent = DataCleaningAIAgent(
        "messy_data.csv"
    )

    agent.run()
