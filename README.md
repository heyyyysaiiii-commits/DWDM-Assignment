# Data Cleaning Agent

An automated Python-based data cleaning agent that identifies and cleans common data-quality issues in CSV datasets.

The agent follows a structured cleaning pipeline to standardize column names, remove duplicate records, handle missing values, normalize text data, detect and cap numerical outliers, and export the cleaned dataset.

---

## Overview

Real-world datasets are often messy, inconsistent, incomplete, and noisy. Before performing analysis or building machine-learning models, the data must be cleaned and standardized.

This project provides an automated `DataCleaningAgent` that performs the most common data-preprocessing tasks through a reusable pipeline.

### Cleaning Pipeline

```text
Raw CSV Dataset
       |
       v
Load Data
       |
       v
Clean Column Names
       |
       v
Remove Duplicate Rows
       |
       v
Handle Missing Values
       |
       v
Standardize Text
       |
       v
Detect and Handle Outliers
       |
       v
Export Clean Dataset
```

---

## Features

### 1. Column Name Standardization

The agent standardizes column names by:

* Removing leading and trailing whitespace
* Converting names to lowercase
* Replacing spaces with underscores

Example:

```text
" Employee Name " -> "employee_name"
"Annual Salary"   -> "annual_salary"
```

---

### 2. Duplicate Removal

Duplicate rows are automatically detected and removed using:

```python
df.drop_duplicates()
```

The number of duplicate records removed is reported in the console.

---

### 3. Missing Value Handling

Missing values are handled according to the data type.

For numerical columns:

```text
Missing values -> Median
```

For text or categorical columns:

```text
Missing values -> Mode
```

Using the median for numerical data helps reduce the influence of extreme values compared with using the mean.

---

### 4. Text Standardization

Text columns are automatically:

* Trimmed for unnecessary whitespace
* Converted to title case

Example:

```text
"  john doe " -> "John Doe"
"MARY SMITH"  -> "Mary Smith"
```

---

### 5. Outlier Detection and Handling

The project uses the Interquartile Range (IQR) method to identify extreme values.

The calculation is:

```text
IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

Values outside these boundaries are identified as outliers and capped at the corresponding boundary rather than removed.

The pipeline automatically applies this process to the `salary` column when it exists.

---

### 6. Change Tracking

The agent provides console output throughout the cleaning process so that users can see what operations were performed.

Example:

```text
[*] Data loaded successfully. Initial shape: (100, 6)

[+] Column names cleaned.

[+] Duplicates checked: 4 duplicate row(s) identified and removed.

[+] Missing values handled:
    - 'age': 3 missing value(s) replaced with median (28.0).

[+] Text standardization:
    - Cleaned casing and whitespaces across 3 text columns.

[+] Outliers handled in 'salary': 5 extreme value(s) capped using IQR.
```

---

## Technologies Used

* Python
* Pandas – Data loading, manipulation, cleaning, and analysis
* NumPy – Numerical operations and data processing

---

## Project Structure

```text
data-cleaning-agent/
|
├── messy_data.csv
├── cleaned_data.csv
├── data_cleaning_agent.py
└── README.md
```

`cleaned_data.csv` is generated automatically when the program is executed.

---

## Requirements

Make sure Python is installed on your system.

Install the required libraries using:

```bash
pip install pandas numpy
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/data-cleaning-agent.git
cd data-cleaning-agent
```

### 2. Install Dependencies

```bash
pip install pandas numpy
```

### 3. Add Your Dataset

Place your raw CSV file in the project directory and name it:

```text
messy_data.csv
```

### 4. Run the Program

```bash
python data_cleaning_agent.py
```

The cleaned dataset will be saved as:

```text
cleaned_data.csv
```

---

## Usage

The main program initializes the cleaning agent with the raw CSV file:

```python
agent = DataCleaningAgent("messy_data.csv")
```

Then the complete cleaning pipeline is executed:

```python
cleaned_df = agent.run_pipeline("cleaned_data.csv")
```

The cleaned DataFrame is also returned so that it can be further processed in Python.

---

## How the Agent Works

The `DataCleaningAgent` is organized into separate methods, with each method responsible for a specific cleaning task.

| Method                    | Purpose                                 |
| ------------------------- | --------------------------------------- |
| `clean_column_names()`    | Standardizes column names               |
| `remove_duplicates()`     | Removes duplicate rows                  |
| `handle_missing_values()` | Fills missing values                    |
| `standardize_text()`      | Cleans and formats text                 |
| `handle_outliers()`       | Detects and caps outliers               |
| `run_pipeline()`          | Executes the complete cleaning workflow |

This modular design makes the project easier to understand, maintain, and extend.

---

## Example

Suppose the input dataset contains:

```csv
 Employee Name ,Age,Salary
 john doe ,25,40000
 JOHN DOE,25,40000
 Mary Smith,,50000
 Alex Brown,30,250000
```

The cleaning process can:

* Standardize `" Employee Name "` to `employee_name`
* Remove duplicate records
* Replace missing numerical values using the median
* Standardize names such as `" john doe "` to `"John Doe"`
* Detect extreme salary values using the IQR method
* Save the processed dataset as `cleaned_data.csv`

---

## Objectives

The project is designed to:

* Automate repetitive data-cleaning tasks
* Improve dataset consistency
* Reduce manual preprocessing effort
* Make cleaning operations transparent
* Produce a cleaner dataset suitable for further analysis

---

## Future Enhancements

Possible improvements include:

* Automatic data-type detection and conversion
* Configurable missing-value strategies
* Detection of invalid values and formatting errors
* Support for Excel and other file formats
* Automatic data-quality reports
* Before-and-after data-quality statistics
* Configurable outlier handling methods
* Logging changes to a separate audit file
* Interactive dashboard for data-quality analysis

---

## Important Considerations

This project uses general-purpose cleaning rules. These rules may not be appropriate for every dataset.

For example, capping outliers may be inappropriate when extreme values are genuine observations. Similarly, replacing missing categorical values with the mode may not always represent the intended meaning of the missing data.

Therefore, cleaning strategies should always be reviewed according to the specific dataset and business context.

---

## Contributing

Contributions, suggestions, and improvements are welcome.

To contribute:

```bash
git fork
git clone <your-fork-url>
git checkout -b feature/your-feature
```

Make your changes, commit them, and submit a pull request.

---

## License

This project is available for educational and development purposes.

You may add a specific license such as the MIT License depending on how you intend to distribute the project.

---

## Author

Sai Charan Devisetty

GitHub: `https://github.com/your-username`

---

If you find this project useful, consider giving the repository a star.
