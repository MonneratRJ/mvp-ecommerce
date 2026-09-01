-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Gold — modelo estrela

-- COMMAND ----------

CREATE WIDGET TEXT catalog DEFAULT "workspace";

CREATE SCHEMA IF NOT EXISTS ${catalog}.olist_gold;

CREATE OR REPLACE TABLE ${catalog}.olist_gold.dim_clientes AS
SELECT customer_id, customer_city, customer_state
FROM ${catalog}.olist_silver.customers;

CREATE OR REPLACE TABLE ${catalog}.olist_gold.dim_produtos AS
SELECT product_id, product_category_name
FROM ${catalog}.olist_silver.products;

CREATE OR REPLACE TABLE ${catalog}.olist_gold.dim_avaliacoes AS
SELECT review_score, CONCAT('nota_', CAST(review_score AS STRING)) AS review_label
FROM (SELECT EXPLODE(SEQUENCE(1, 5)) AS review_score);

CREATE OR REPLACE TABLE ${catalog}.olist_gold.dim_tempo AS
SELECT DISTINCT
  CAST(order_purchase_timestamp AS DATE) AS purchase_date,
  YEAR(order_purchase_timestamp) AS year,
  MONTH(order_purchase_timestamp) AS month,
  DAY(order_purchase_timestamp) AS day,
  DATE_FORMAT(order_purchase_timestamp, 'yyyy-MM') AS year_month
FROM ${catalog}.olist_silver.orders
WHERE order_purchase_timestamp IS NOT NULL;

-- COMMAND ----------

CREATE OR REPLACE TABLE ${catalog}.olist_gold.fato_vendas AS
WITH primary_payment AS (
  SELECT order_id, payment_type
  FROM (
    SELECT
      order_id,
      payment_type,
      ROW_NUMBER() OVER (
        PARTITION BY order_id
        ORDER BY payment_sequential, payment_type
      ) AS row_number
    FROM ${catalog}.olist_silver.payments
  ) ranked_payments
  WHERE row_number = 1
)
SELECT
  o.order_id,
  i.order_item_id,
  o.customer_id,
  i.product_id,
  r.review_score,
  CAST(o.order_purchase_timestamp AS DATE) AS purchase_date,
  p.payment_type,
  i.price,
  i.freight_value,
  DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp) AS delivery_days,
  DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) AS delivery_delay_days,
  CASE
    WHEN o.order_delivered_customer_date IS NULL THEN 'nao_entregue'
    WHEN DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) <= 0 THEN 'adiantado_ou_no_prazo'
    WHEN DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) <= 7 THEN 'atraso_1_7_dias'
    ELSE 'atraso_mais_de_7_dias'
  END AS delivery_status
FROM ${catalog}.olist_silver.orders o
JOIN ${catalog}.olist_silver.order_items i ON i.order_id = o.order_id
LEFT JOIN ${catalog}.olist_silver.reviews r ON r.order_id = o.order_id
LEFT JOIN primary_payment p ON p.order_id = o.order_id
WHERE o.order_purchase_timestamp IS NOT NULL
  AND (
    o.order_delivered_customer_date IS NULL OR
    o.order_delivered_customer_date >= o.order_purchase_timestamp
  );
