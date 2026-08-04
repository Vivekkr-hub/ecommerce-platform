# End-to-End E-Commerce Data Platform

A production-grade data analytics platform built on the Brazilian E-Commerce (Olist) dataset, covering 100K+ orders and R$13.2M in revenue. The project spans the full data lifecycle from raw ingestion to machine learning and business intelligence.

---

## Architecture

```
Raw Data (Olist CSV)
        |
ETL Pipeline (Python)
        |
PostgreSQL Data Warehouse
        |
Analytics Layer (SQL)
        |
ML Models (Churn Prediction + Sales Forecasting)
        |
Power BI Dashboard + Streamlit Web App
```

---

## Business Summary

| Metric | Value |
|---|---|
| Total Revenue | R$13.2M |
| Total Orders | 96,478 |
| Average Order Value | R$137 |
| Average Review Score | 4.09 / 5.0 |
| Late Delivery Rate | 6.8% |
| Customer Churn Rate | 71.4% |
| Revenue at Risk | R$9.3M |
| 30-Day Revenue Forecast | R$720,707 |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Storage | PostgreSQL 18 |
| ETL | Python, Pandas, SQLAlchemy |
| Analytics | SQL - CTEs, Window Functions, Cohort Analysis |
| Machine Learning | Scikit-learn, XGBoost, SHAP |
| Visualization | Power BI, Matplotlib, Seaborn |
| Web App | Streamlit |

---

## Project Structure

```
ecommerce-platform/
├── data/
│   └── raw/                     # Raw CSV files (not tracked)
├── etl/
│   └── pipeline.py              # ETL pipeline script
├── sql/
│   ├── analytics.sql            # Core analytics queries
│   └── advanced_analytics.sql  # Advanced SQL queries
├── notebooks/
│   ├── 00_sanity_check.ipynb
│   └── 01_eda.ipynb
├── ml/
│   ├── churn_prediction.ipynb
│   └── sales_forecasting.ipynb
├── dashboard/
│   └── ecommerce_dashboard.pbix
├── app/
│   └── main.py
├── requirements.txt
└── README.md
```

---

## How to Run

### 1. Clone and Setup

```bash
git clone https://github.com/Vivekkr-hub/ecommerce-platform.git
cd ecommerce-platform
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Download Dataset

Download the Brazilian E-Commerce dataset from Kaggle:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Place all CSV files inside data/raw/

### 3. Configure Database

Create a PostgreSQL database named ecommerce_db and update your credentials in etl/pipeline.py

### 4. Run ETL Pipeline

```bash
python etl/pipeline.py
```

### 5. Launch Streamlit App

```bash
streamlit run app/main.py
```

---

## Machine Learning

### Churn Prediction

- Algorithm: XGBoost
- ROC-AUC: 0.609
- Features: order frequency, total spend, average order value, review score, payment installments
- Notable: Initial model had data leakage giving AUC of 1.0. Identified and fixed by removing the leaky feature, resulting in an honest 0.609 AUC
- Business Impact: 71,097 high-risk customers identified with R$9.3M revenue at stake

### Sales Forecasting

- Algorithm: Gradient Boosting Regressor
- Features: day index, day of week, month, quarter
- Output: 30-day forward revenue forecast
- Projected Revenue: R$720,707

---

## SQL Analytics

| Analysis | SQL Concepts Used |
|---|---|
| Monthly Revenue Trend | GROUP BY, DATE_TRUNC |
| Top Product Categories | JOINs, ORDER BY |
| Cohort Retention Analysis | CTEs, Window Functions |
| RFM Customer Segmentation | NTILE, CASE WHEN |
| Funnel Analysis | CTEs, COUNT DISTINCT |
| Customer Lifetime Value | NTILE, Aggregations |
| A/B Test Simulation | CASE WHEN, STDDEV |
| Month-over-Month Growth | LAG, Window Functions |

---

## Power BI Dashboard

Three-page interactive dashboard connected live to PostgreSQL.

Page 1 - Executive Overview: revenue KPIs, monthly trend, top categories, state-wise revenue map, order status breakdown.

Page 2 - Customer Analytics: customers by state, payment method distribution, monthly new customers, review score distribution.

Page 3 - Operations and Sellers: top sellers by revenue, average delivery days by state, revenue by payment type, delivery status.

---

## Resume Bullets

- Designed and automated an ETL pipeline processing 100K+ records from 9 CSV sources into a PostgreSQL data warehouse using Python and SQLAlchemy
- Wrote 14 advanced SQL queries covering cohort analysis, RFM segmentation, funnel analysis, CLV, and A/B testing on 96K orders
- Built a churn prediction model using XGBoost (ROC-AUC 0.609), identified and resolved data leakage, and used SHAP to explain feature impact on R$9.3M at-risk revenue
- Developed a 30-day sales forecasting model using Gradient Boosting projecting R$720K in future revenue
- Designed a 3-page Power BI dashboard with live PostgreSQL connection tracking revenue, customer segments, and operational KPIs

---

## Author

Vivek Kumar
B.Tech Electronics and Communication Engineering
Manipal Institute of Technology, Manipal
GitHub: https://github.com/Vivekkr-hub