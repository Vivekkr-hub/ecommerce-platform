import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ecommerce_db',
    'username': 'postgres',
    'password': 'Abcd1234!'  # ← change this
}

DATA_PATH = r'C:\Users\nwdvi\Desktop\ecommerce-platform\data\raw'

engine = create_engine(
    f"postgresql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ─────────────────────────────────────────
# STEP 1 — LOAD RAW DATA
# ─────────────────────────────────────────
print("📂 Loading raw CSV files...")

orders      = pd.read_csv(f'{DATA_PATH}/olist_orders_dataset.csv')
items       = pd.read_csv(f'{DATA_PATH}/olist_order_items_dataset.csv')
customers   = pd.read_csv(f'{DATA_PATH}/olist_customers_dataset.csv')
products    = pd.read_csv(f'{DATA_PATH}/olist_products_dataset.csv')
sellers     = pd.read_csv(f'{DATA_PATH}/olist_sellers_dataset.csv')
payments    = pd.read_csv(f'{DATA_PATH}/olist_order_payments_dataset.csv')
reviews     = pd.read_csv(f'{DATA_PATH}/olist_order_reviews_dataset.csv')
translation = pd.read_csv(f'{DATA_PATH}/product_category_name_translation.csv')

print("✅ All files loaded\n")

# ─────────────────────────────────────────
# STEP 2 — CLEAN EACH TABLE
# ─────────────────────────────────────────
print("🧹 Cleaning data...")

# --- ORDERS ---
date_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')

orders['order_status'] = orders['order_status'].str.strip().str.lower()
orders = orders.drop_duplicates(subset='order_id')
print(f"  orders     → {len(orders):,} rows")

# --- ITEMS ---
items['shipping_limit_date'] = pd.to_datetime(items['shipping_limit_date'], errors='coerce')
items['price'] = pd.to_numeric(items['price'], errors='coerce')
items['freight_value'] = pd.to_numeric(items['freight_value'], errors='coerce')
items = items.dropna(subset=['order_id', 'product_id'])
print(f"  items      → {len(items):,} rows")

# --- CUSTOMERS ---
customers = customers.drop_duplicates(subset='customer_id')
customers['customer_state'] = customers['customer_state'].str.strip().str.upper()
customers['customer_city'] = customers['customer_city'].str.strip().str.title()
print(f"  customers  → {len(customers):,} rows")

# --- PRODUCTS ---
products = products.merge(translation, on='product_category_name', how='left')
products['product_category_name'] = products['product_category_name_english'].fillna(
    products['product_category_name']
)
products = products.drop(columns=['product_category_name_english'])
products['product_category_name'] = products['product_category_name'].fillna('unknown')

numeric_cols = ['product_weight_g', 'product_length_cm', 
                'product_height_cm', 'product_width_cm']
for col in numeric_cols:
    products[col] = pd.to_numeric(products[col], errors='coerce')
    products[col] = products[col].fillna(products[col].median())

products = products.drop_duplicates(subset='product_id')
print(f"  products   → {len(products):,} rows")

# --- SELLERS ---
sellers = sellers.drop_duplicates(subset='seller_id')
sellers['seller_state'] = sellers['seller_state'].str.strip().str.upper()
sellers['seller_city'] = sellers['seller_city'].str.strip().str.title()
print(f"  sellers    → {len(sellers):,} rows")

# --- PAYMENTS ---
payments['payment_value'] = pd.to_numeric(payments['payment_value'], errors='coerce')
payments['payment_installments'] = pd.to_numeric(payments['payment_installments'], errors='coerce')
payments = payments.dropna(subset=['order_id'])
print(f"  payments   → {len(payments):,} rows")

# --- REVIEWS ---
reviews = reviews.drop_duplicates(subset='review_id')
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'], errors='coerce')
reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'], errors='coerce')
reviews['review_score'] = pd.to_numeric(reviews['review_score'], errors='coerce')
# Drop free text columns (not needed for analytics)
reviews = reviews.drop(columns=['review_comment_title', 'review_comment_message'], errors='ignore')
print(f"  reviews    → {len(reviews):,} rows")

print("\n✅ Cleaning done\n")

# ─────────────────────────────────────────
# STEP 3 — LOAD TO POSTGRESQL
# ─────────────────────────────────────────
print("🚀 Loading to PostgreSQL...")

tables = {
    'orders':    orders,
    'items':     items,
    'customers': customers,
    'products':  products,
    'sellers':   sellers,
    'payments':  payments,
    'reviews':   reviews
}

for table_name, df in tables.items():
    df.to_sql(
        table_name,
        engine,
        if_exists='replace',   # drops and recreates table each run
        index=False,
        chunksize=1000
    )
    print(f"  ✅ {table_name:12} → {len(df):,} rows loaded")

print("\n🎉 ETL Complete! All tables in PostgreSQL.")

# ─────────────────────────────────────────
# STEP 4 — VERIFY
# ─────────────────────────────────────────
print("\n🔍 Verifying row counts in DB...\n")

with engine.connect() as conn:
    for table_name in tables.keys():
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        print(f"  {table_name:12} → {count:,} rows in DB")

print("\n✅ Verification complete!")