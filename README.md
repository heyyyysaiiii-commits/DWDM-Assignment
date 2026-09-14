# AI Data Cleaning Agent

An automated, AI-assisted Python data cleaning agent that profiles raw CSV datasets, leverages OpenAI (or an internal heuristic fallback engine) to determine optimal cleaning strategies, executes a data cleaning pipeline using Pandas, and generates an audit log report alongside the sanitized CSV.

---

## Overview

Real-world datasets are frequently messy, inconsistent, and noisy. Before conducting analysis or training machine learning models, data must be standardly cleaned and profiled.

The **AI Data Cleaning Agent** automates this workflow by using an LLM to inspect dataset metadata, generate a JSON cleaning plan, and run an automated preprocessing pipeline with change tracking.

### Cleaning Pipeline Flow

```text
               Raw CSV Dataset
                      |
                      v
          Data Ingestion & Profiling
                      |
                      v
      AI Strategy Decision (OpenAI API / Heuristic Engine)
                      |
                      v
         ---------------------------
        |  Clean Column Names       |
        |  Remove Duplicates        |
        |  Standardize Text         |
        |  Impute Missing Values    |
        |  Detect & Cap Outliers    |
         ---------------------------
                      |
           +----------+----------+
           |                     |
           v                     v
   Export Cleaned CSV    Export Audit JSON
  (cleaned_data.csv)   (cleaning_report.json)

## Features

### 1. Dataset Profiling

Before altering any data, the agent constructs a detailed JSON metadata profile summarizing:

* Row and column counts
* Column data types
* Missing value counts per column
* Duplicate row count

### 2. AI-Driven Cleaning Strategy & Fallback Engine

The agent sends the dataset profile to an AI model (`gpt-4o-mini`) to generate a dynamic JSON cleaning plan.

> **Reliability Guarantee:** If an OpenAI API key is missing or out of API credits, the agent automatically catches the error and switches to an internal **Heuristic AI Planner** to ensure the pipeline executes without failing.

### 3. Column Name Standardization

* Strips leading and trailing whitespace
* Converts names to lowercase
* Replaces spaces with underscores (`" Full Name "` -> `"full_name"`)

### 4. Duplicate Record Removal

Identifies and drops 100% duplicate rows automatically while logging the number of removed entries.

### 5. Smart Missing Value Imputation

* **Numerical Columns:** Replaces missing values with the column **median** (reducing outlier skew).
* **Categorical / Text Columns:** Replaces missing values with the column **mode**.

### 6. Text Standardization

* Removes leading/trailing whitespace padding across string columns.
* Applies proper Title Casing (`" john doe "` -> `"John Doe"`).

### 7. Outlier Detection & Capping (IQR Method)

Detects extreme numerical anomalies using the Interquartile Range ($IQR = Q3 - Q1$). Values falling outside $[Q1 - 1.5 \times IQR, Q3 + 1.5 \times IQR]$ are capped to the upper or lower statistical boundary.

### 8. Audit Report Generation

Generates a `cleaning_report.json` file detailing the initial shape, final shape, AI decision parameters, and execution plan.

---

## Technologies Used

* **Python**
* **Pandas** – Data profiling, cleaning, and CSV transformations
* **OpenAI API** – LLM-driven decision planning (`gpt-4o-mini`)

---

## Project Structure

```text
data-cleaning-agent/
│
├── messy_data.csv           # Input raw dataset
├── cleaned_data.csv         # Processed CSV output
├── cleaning_report.json     # Generated JSON audit log
├── data_cleaning_agent.py   # Main Python agent code
└── README.md                # Documentation

```

---

## Requirements & Setup

### 1. Install Dependencies

Install the required Python packages:

```bash
pip install pandas openai

```

### 2. Configure OpenAI API Key (Optional)

Set your secret key as an environment variable in your terminal:

* **PowerShell (Windows):**
```powershell
$env:OPENAI_API_KEY="your-openai-api-key"

```


* **Linux / macOS / Bash:**
```bash
export OPENAI_API_KEY="your-openai-api-key"

```



*(Note: If no API key is set or your credit balance is zero, the script automatically uses the internal heuristic fallback).*

---

## Getting Started & Execution

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/data-cleaning-agent.git](https://github.com/your-username/data-cleaning-agent.git)
cd data-cleaning-agent

```

### 2. Add Your Input File

Ensure `messy_data.csv` is present in the project directory.

### 3. Run the Agent

```bash
python data_cleaning_agent.py

```

---

## Code Workflow & Methods

The core execution is encapsulated in the `DataCleaningAIAgent` class:

| Method | Purpose |
| --- | --- |
| `profile_dataset()` | Analyzes raw dataset structure and returns metadata. |
| `generate_cleaning_plan()` | Queries OpenAI API (or falls back to heuristics) for a JSON cleaning plan. |
| `clean_column_names()` | Normalizes column header naming conventions. |
| `remove_duplicates()` | Identifies and drops duplicate rows. |
| `standardize_text()` | Trims whitespaces and applies Title Case to text columns. |
| `handle_missing_values()` | Imputes numerical missing values with median and text with mode. |
| `handle_outliers()` | Clips numerical outliers using Interquartile Range ($1.5 \times IQR$). |
| `save_cleaned_data()` | Saves final sanitized DataFrame to `cleaned_data.csv`. |
| `save_report()` | Exports summary audit log to `cleaning_report.json`. |
| `run()` | Orchestrates the end-to-end execution pipeline. |

---

## Execution Outputs

### Console Output Example

```text
Data loaded successfully.
Original dataset shape: (7, 5)

======================================
       DATA CLEANING AI AGENT
======================================

Dataset Profile:
{
    "rows": 7,
    "columns": 5,
    "column_names": ["Employee ID", " Full Name", " Department ", " Salary", " Join Date"],
    "missing_values": {" Department ": 1, " Salary": 1},
    "duplicate_rows": 1
}

AI is analyzing the dataset...

AI Cleaning Plan:
{
    "column_name_standardization": true,
    "remove_duplicates": true,
    "text_standardization": true,
    "missing_value_strategy": "median_mode",
    "detect_outliers": true,
    "outlier_method": "IQR",
    "outlier_columns": ["salary"],
    "reasoning": "Standard numerical and text data cleaning strategy applied."
}

[AI ACTION] Column names standardized.
[AI ACTION] Duplicate rows removed: 1
[AI ACTION] Text standardized in 3 column(s).
[AI ACTION] department: missing categorical values replaced with mode = IT
[AI ACTION] salary: missing numerical values replaced with median = 75000.0
[AI ACTION] salary: 1 outlier(s) capped using IQR.
[AI ACTION] Cleaned dataset saved to: cleaned_data.csv
[AI ACTION] Cleaning report saved to: cleaning_report.json

======================================
       CLEANING COMPLETED
======================================
Final dataset shape: (5, 5)

```

### Sample `cleaning_report.json`

```json
{
    "input_file": "messy_data.csv",
    "original_shape": {
        "rows": 7,
        "columns": 5
    },
    "final_shape": {
        "rows": 5,
        "columns": 5
    },
    "ai_cleaning_plan": {
        "column_name_standardization": true,
        "remove_duplicates": true,
        "text_standardization": true,
        "missing_value_strategy": "median_mode",
        "detect_outliers": true,
        "outlier_method": "IQR",
        "outlier_columns": [
            "salary"
        ],
        "reasoning": "Standard numerical and text data cleaning strategy applied."
    }
}

```

---

## License

This project is available under the MIT License for educational and development purposes.

---

## Author

**Sai Charan Devisetty**

* GitHub: (https://github.com/heyyyysaiiii-commits)

```

```
