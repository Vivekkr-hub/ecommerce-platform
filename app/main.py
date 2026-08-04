import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Intelligence Platform",
    page_icon="📊",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_engine():
    return create_engine('postgresql://postgres:Abcd1234!@localhost:5432/ecommerce_db')

@st.cache_data
def load_data():
    engine = get_engine()
    orders   = pd.read_sql('SELECT * FROM orders', engine)
    items    = pd.read_sql('SELECT * FROM items', engine)
    customers = pd.read_sql('SELECT * FROM customers', engine)
    products = pd.read_sql('SELECT * FROM products', engine)
    payments = pd.read_sql('SELECT * FROM payments', engine)
    reviews  = pd.read_sql('SELECT * FROM reviews', engine)
    return orders, items, customers, products, payments, reviews

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
with st.spinner('Loading data from PostgreSQL...'):
    orders, items, customers, products, payments, reviews = load_data()

# Merge base dataframe
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
df = orders.merge(items, on='order_id')
df = df[df['order_status'] == 'delivered']

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.title("E-Commerce Platform")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Executive Overview", "Customer Analytics", "Churn Predictor"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset**")
st.sidebar.markdown(f"Orders: {len(orders):,}")
st.sidebar.markdown(f"Customers: {len(customers):,}")
st.sidebar.markdown(f"Products: {len(products):,}")

# ─────────────────────────────────────────
# PAGE 1 — EXECUTIVE OVERVIEW
# ─────────────────────────────────────────
if page == "Executive Overview":
    st.title("Executive Overview")
    st.markdown("Key business metrics across the e-commerce platform.")
    st.markdown("---")

    # KPI Cards
    total_revenue = df['price'].sum()
    total_orders  = df['order_id'].nunique()
    avg_order_val = total_revenue / total_orders
    avg_review    = reviews['review_score'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"R${total_revenue:,.0f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Avg Order Value", f"R${avg_order_val:,.2f}")
    col4.metric("Avg Review Score", f"{avg_review:.2f} / 5.0")

    st.markdown("---")

    # Monthly Revenue Trend
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Revenue Trend")
        monthly = df.groupby(
            df['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum().reset_index()
        monthly['order_purchase_timestamp'] = monthly['order_purchase_timestamp'].astype(str)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(monthly['order_purchase_timestamp'],
                monthly['price'], color='steelblue', linewidth=2, marker='o', markersize=3)
        ax.set_xlabel('Month')
        ax.set_ylabel('Revenue (BRL)')
        ax.tick_params(axis='x', rotation=90)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Top 10 Categories by Revenue")
        cat_rev = df.merge(products[['product_id','product_category_name']], on='product_id')
        top_cats = cat_rev.groupby('product_category_name')['price']\
                          .sum().sort_values(ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.barh(top_cats.index[::-1], top_cats.values[::-1], color='steelblue')
        ax.set_xlabel('Revenue (BRL)')
        plt.tight_layout()
        st.pyplot(fig)

    # Revenue by State
    st.subheader("Revenue by State")
    state_rev = df.merge(customers[['customer_id','customer_state']], on='customer_id')\
                  .groupby('customer_state')['price'].sum()\
                  .sort_values(ascending=False).reset_index()

    fig, ax = plt.subplots(figsize=(14, 4))
    bars = ax.bar(state_rev['customer_state'], state_rev['price'], color='steelblue')
    for i in range(3):
        bars[i].set_color('orange')
    ax.set_xlabel('State')
    ax.set_ylabel('Revenue (BRL)')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ─────────────────────────────────────────
# PAGE 2 — CUSTOMER ANALYTICS
# ─────────────────────────────────────────
elif page == "Customer Analytics":
    st.title("Customer Analytics")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Review Score Distribution")
        score_counts = reviews['review_score'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(score_counts.index, score_counts.values,
               color=['red','orange','yellow','lightgreen','green'])
        ax.set_xlabel('Review Score')
        ax.set_ylabel('Count')
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Payment Method Distribution")
        pay_counts = payments['payment_type'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4))

        def autopct_filter(pct):
            return f'{pct:.1f}%' if pct > 5 else ''

        wedges, texts, autotexts = ax.pie(
            pay_counts.values,
            labels=None,
            autopct=autopct_filter,
            startangle=90,
            pctdistance=0.75
        )
        ax.legend(
            wedges,
            pay_counts.index,
            title="Payment Type",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        plt.tight_layout()
        st.pyplot(fig)

    st.subheader("Monthly New Customers")
    monthly_customers = orders.groupby(
        orders['order_purchase_timestamp'].dt.to_period('M')
    )['customer_id'].nunique().reset_index()
    monthly_customers['order_purchase_timestamp'] = \
        monthly_customers['order_purchase_timestamp'].astype(str)

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(monthly_customers['order_purchase_timestamp'],
            monthly_customers['customer_id'],
            color='steelblue', linewidth=2, marker='o', markersize=3)
    ax.set_xlabel('Month')
    ax.set_ylabel('New Customers')
    ax.tick_params(axis='x', rotation=90)
    plt.tight_layout()
    st.pyplot(fig)

# ─────────────────────────────────────────
# PAGE 3 — CHURN PREDICTOR
# ─────────────────────────────────────────
elif page == "Churn Predictor":
    st.title("Customer Churn Predictor")
    st.markdown("Enter customer details to predict churn probability.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        order_frequency = st.slider("Order Frequency", 1, 20, 1)
        total_spend     = st.number_input("Total Spend (R$)", 0.0, 10000.0, 150.0)
        avg_order_value = st.number_input("Avg Order Value (R$)", 0.0, 5000.0, 150.0)

    with col2:
        avg_review_score  = st.slider("Avg Review Score", 1.0, 5.0, 4.0, 0.1)
        avg_installments  = st.slider("Avg Installments", 1, 12, 1)

    if st.button("Predict Churn Risk"):
        # Simple rule-based scoring (no saved model needed)
        score = 0
        if order_frequency == 1:
            score += 40
        if total_spend < 100:
            score += 20
        if avg_review_score < 3:
            score += 25
        if avg_installments > 6:
            score += 15

        score = min(score, 100)

        st.markdown("---")
        if score >= 60:
            st.error(f"High Churn Risk — {score}% probability")
            st.markdown("Recommended action: Send retention offer or discount coupon immediately.")
        elif score >= 30:
            st.warning(f"Medium Churn Risk — {score}% probability")
            st.markdown("Recommended action: Send re-engagement email within 7 days.")
        else:
            st.success(f"Low Churn Risk — {score}% probability")
            st.markdown("Customer appears healthy. Continue standard engagement.")