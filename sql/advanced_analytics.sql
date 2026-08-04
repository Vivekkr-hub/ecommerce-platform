-- ═══════════════════════════════════════
-- 1. FUNNEL ANALYSIS
-- How many orders make it through each stage?
-- ═══════════════════════════════════════
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN order_status != 'canceled' 
        THEN order_id END) AS approved_orders,
    COUNT(DISTINCT CASE WHEN order_delivered_carrier_date IS NOT NULL 
        THEN order_id END) AS shipped_orders,
    COUNT(DISTINCT CASE WHEN order_delivered_customer_date IS NOT NULL 
        THEN order_id END) AS delivered_orders,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN order_status != 'canceled' 
        THEN order_id END) / COUNT(DISTINCT order_id), 1) AS approval_rate,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN order_delivered_customer_date IS NOT NULL 
        THEN order_id END) / COUNT(DISTINCT order_id), 1) AS delivery_rate
FROM orders;


-- ═══════════════════════════════════════
-- 2. CUSTOMER LIFETIME VALUE (CLV)
-- ═══════════════════════════════════════
WITH customer_stats AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(i.price)::numeric, 2) AS total_spent,
        MIN(o.order_purchase_timestamp) AS first_order,
        MAX(o.order_purchase_timestamp) AS last_order,
        EXTRACT(DAY FROM (
            MAX(o.order_purchase_timestamp) - MIN(o.order_purchase_timestamp)
        )) AS customer_lifespan_days
    FROM orders o
    JOIN items i ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    total_orders,
    total_spent,
    customer_lifespan_days,
    ROUND(total_spent / NULLIF(total_orders, 0), 2) AS avg_order_value,
    NTILE(4) OVER (ORDER BY total_spent DESC) AS clv_quartile,
    CASE
        WHEN NTILE(4) OVER (ORDER BY total_spent DESC) = 1 THEN 'High Value'
        WHEN NTILE(4) OVER (ORDER BY total_spent DESC) = 2 THEN 'Mid Value'
        WHEN NTILE(4) OVER (ORDER BY total_spent DESC) = 3 THEN 'Low Value'
        ELSE 'Churned Risk'
    END AS clv_segment
FROM customer_stats
ORDER BY total_spent DESC;


-- ═══════════════════════════════════════
-- 3. A/B TEST SIMULATION
-- Do customers who pay in installments spend more?
-- ═══════════════════════════════════════
WITH payment_groups AS (
    SELECT
        o.order_id,
        o.customer_id,
        SUM(i.price) AS order_value,
        MAX(p.payment_installments) AS installments,
        CASE 
            WHEN MAX(p.payment_installments) > 1 THEN 'Installment'
            ELSE 'Single Payment'
        END AS payment_group
    FROM orders o
    JOIN items i ON o.order_id = i.order_id
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.order_id, o.customer_id
)
SELECT
    payment_group,
    COUNT(*) AS total_orders,
    ROUND(AVG(order_value)::numeric, 2) AS avg_order_value,
    ROUND(MIN(order_value)::numeric, 2) AS min_order_value,
    ROUND(MAX(order_value)::numeric, 2) AS max_order_value,
    ROUND(STDDEV(order_value)::numeric, 2) AS std_dev
FROM payment_groups
GROUP BY payment_group;


-- ═══════════════════════════════════════
-- 4. REPEAT vs ONE-TIME CUSTOMERS
-- ═══════════════════════════════════════
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY customer_id
)
SELECT
    CASE 
        WHEN order_count = 1 THEN 'One-Time'
        WHEN order_count BETWEEN 2 AND 3 THEN 'Occasional'
        ELSE 'Loyal'
    END AS customer_type,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM customer_orders
GROUP BY customer_type
ORDER BY customer_count DESC;


-- ═══════════════════════════════════════
-- 5. LATE DELIVERY IMPACT ON REVIEWS
-- Does late delivery hurt review scores?
-- ═══════════════════════════════════════
WITH delivery_status AS (
    SELECT
        o.order_id,
        CASE
            WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
            THEN 'On Time'
            ELSE 'Late'
        END AS delivery_type,
        r.review_score
    FROM orders o
    JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    delivery_type,
    COUNT(*) AS total_orders,
    ROUND(AVG(review_score)::numeric, 2) AS avg_review_score,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM delivery_status
GROUP BY delivery_type;


-- ═══════════════════════════════════════
-- 6. RUNNING TOTAL REVENUE (Cumulative)
-- ═══════════════════════════════════════
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        ROUND(SUM(i.price)::numeric, 2) AS monthly_revenue
    FROM orders o
    JOIN items i ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
)
SELECT
    month,
    monthly_revenue,
    ROUND(SUM(monthly_revenue) OVER (
        ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )::numeric, 2) AS cumulative_revenue
FROM monthly_revenue
ORDER BY month;