# 🤖 HanuAI Insight Engine

AI-powered analytics platform for **Customer Voice** and **Field Failure Intelligence**.

## 🚀 Live Demo

**Streamlit Application:**  
https://YOUR-STREAMLIT-APP-URL.streamlit.app

**GitHub Repository:**  
https://github.com/PN200203/hanuai-insight-engine

---

## 📌 Project Overview

HanuAI Insight Engine is a data analytics platform designed to analyze:

- Customer reviews and feedback
- Customer sentiment
- Product aspects and customer opinions
- Field failure records
- Failure categories
- Affected components
- Potential root causes
- Failure trends
- Downtime and repair costs

The project combines data scraping, sentiment analysis, text mining, exploratory data analysis, and an interactive Streamlit dashboard.

---

## 🎯 Key Features

### 📊 Voice of Customer

The Voice of Customer module analyzes customer reviews and provides:

- Customer review analysis
- Sentiment analysis
- Aspect-level sentiment
- Customer insights
- Review trends
- Product feedback analysis

The project includes a Selenium-based scraper for collecting Best Buy product reviews.

### 🔧 Field Failure Intelligence

The Field Failure Intelligence module analyzes field failure records to identify:

- Failure categories
- Problematic components
- Issue patterns
- Root-cause candidates
- Failure trends
- Downtime analysis
- Repair-cost analysis
- Component/model relationships

---

## 🛠️ Tech Stack

### Programming

- Python

### Data Analysis

- Pandas
- NumPy
- Scikit-learn

### Web Scraping

- Selenium
- BeautifulSoup
- WebDriver Manager
- Requests

### Visualization

- Matplotlib
- Seaborn

### Dashboard

- Streamlit

### Data Formats

- CSV
- Excel
- Markdown

### Development Tools

- Jupyter Notebook
- Git
- GitHub
- VS Code

---

## 📂 Project Structure

```text
hanuai-insight-engine/
│
├── app.py
├── README.md
├── requirements.txt
│
├── docs/
│
├── task1_voice_of_customer/
│   │
│   ├── data/
│   │   ├── processed/
│   │   │   ├── reviews_sentiment_DEMO.csv
│   │   │   └── reviews_sentiment_DEMO.xlsx
│   │   │
│   │   └── raw/
│   │       ├── bestbuy_roku_reviews.csv
│   │       └── reviews_raw_DEMO.csv
│   │
│   ├── notebooks/
│   │   └── 01_scrape_and_sentiment.ipynb
│   │
│   ├── reports/
│   │   ├── aspect_net_sentiment_DEMO.png
│   │   ├── insights_DEMO.md
│   │   └── Task1_Report.md
│   │
│   └── src/
│       ├── config.py
│       ├── report_builder.py
│       ├── resilience.py
│       ├── run_pipeline.py
│       ├── sample_data.py
│       ├── scraper.py
│       └── sentiment.py
│
├── task2_field_failure_intelligence/
│   │
│   ├── data/
│   │   ├── processed/
│   │   │   ├── mined_tags_SYNTHETIC_DEMO.xlsx
│   │   │   └── notebook_tags_SYNTHETIC_DEMO.xlsx
│   │   │
│   │   └── raw/
│   │       └── failures_SYNTHETIC_DEMO.csv
│   │
│   ├── notebooks/
│   │   └── 02_eda_text_mining.ipynb
│   │
│   ├── reports/
│   │   ├── auto_insights_SYNTHETIC_DEMO.md
│   │   ├── Task2_Report.md
│   │   └── figures/
│   │
│   └── src/
│       ├── eda.py
│       ├── run_pipeline.py
│       ├── sample_data.py
│       ├── textmining.py
│       └── topics.py
│
└── tools/
    └── build_notebooks.py
```

---

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/PN200203/hanuai-insight-engine.git
cd hanuai-insight-engine
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the Streamlit application

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

---

## 📊 Application Modules

### Overview

The Overview page provides a high-level summary of the complete analytics platform, including customer reviews, failure records, failure clusters, and data sources.

### Voice of Customer

This module uses customer review data to understand:

- Overall customer sentiment
- Positive and negative feedback
- Product strengths
- Product weaknesses
- Customer concerns
- Important product aspects

### Field Failure Intelligence

This module processes field failure data to identify:

- Frequently occurring failures
- Important components
- Issue categories
- Failure trends
- Potential root causes
- Downtime patterns
- Repair-cost patterns

---

## 🔄 Data Pipeline

The project follows a data-processing pipeline:

```text
Raw Data
   ↓
Data Collection / Loading
   ↓
Data Cleaning
   ↓
Text Processing
   ↓
Sentiment Analysis / Text Mining
   ↓
Aspect & Failure Analysis
   ↓
Insight Generation
   ↓
Reports & Visualizations
   ↓
Streamlit Dashboard
```

---

## 🧪 Voice of Customer Pipeline

```text
Best Buy Reviews
       ↓
Selenium Scraper
       ↓
Raw Review CSV
       ↓
Text Cleaning
       ↓
Sentiment Analysis
       ↓
Aspect Analysis
       ↓
Customer Insights
       ↓
Streamlit Dashboard
```

---

## 🔧 Field Failure Pipeline

```text
Field Failure Data
       ↓
Data Cleaning
       ↓
Exploratory Data Analysis
       ↓
Text Mining
       ↓
Issue Categorization
       ↓
Component Analysis
       ↓
Root-Cause Candidates
       ↓
Trend & Cost Analysis
       ↓
Streamlit Dashboard
```

---

## 📈 Sample Insights

The dashboard provides insights such as:

- Customer sentiment distribution
- Frequently discussed product aspects
- Positive and negative customer feedback
- Failure category distribution
- Top problematic components
- Monthly failure trends
- Component/model relationships
- Downtime patterns
- Repair-cost analysis

---

## 🌐 Deployment

The Streamlit dashboard is deployed using **Streamlit Community Cloud**.

### Deployment configuration

```text
Repository: PN200203/hanuai-insight-engine
Branch: main
Main file: app.py
```

### Live Application

👉 **[Open HanuAI Insight Engine](https://YOUR-STREAMLIT-APP-URL.streamlit.app)**

---

## 📁 Data

The repository contains demo and synthetic datasets used for analysis and demonstration.

### Voice of Customer

- Best Buy Roku TV review data
- Processed sentiment data
- Generated reports
- Sentiment visualization

### Field Failure Intelligence

- Synthetic field failure dataset
- Processed mining results
- Generated insights
- EDA visualizations

---

## ⚠️ Notes

The project contains demo/synthetic datasets for demonstration purposes.

The Selenium scraper is intended for controlled data collection and may require updates if the target website changes its page structure.

The deployed Streamlit application primarily uses the processed data and reports stored in the repository.

---

## 👨‍💻 Author

**Praveen Neelamsetti
