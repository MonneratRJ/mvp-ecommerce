-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Análises de negócio

-- COMMAND ----------

CREATE WIDGET TEXT catalog DEFAULT "workspace";

-- Pergunta 1: associação entre atraso e satisfação.
SELECT
  delivery_status,
  COUNT(DISTINCT order_id) AS total_pedidos,
  ROUND(AVG(review_score), 2) AS nota_media,
  ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN review_score IN (1, 2) THEN order_id END) /
    NULLIF(COUNT(DISTINCT CASE WHEN review_score IS NOT NULL THEN order_id END), 0),
    2
  ) AS percentual_notas_1_2
FROM ${catalog}.olist_gold.fato_vendas
GROUP BY delivery_status
ORDER BY total_pedidos DESC;

-- COMMAND ----------

-- Pergunta 2: estados líderes em receita e sua forma de pagamento predominante.
WITH state_sales AS (
  SELECT
    c.customer_state,
    COUNT(DISTINCT f.order_id) AS total_pedidos,
    ROUND(SUM(f.price + f.freight_value), 2) AS receita_brl
  FROM ${catalog}.olist_gold.fato_vendas f
  JOIN ${catalog}.olist_gold.dim_clientes c USING (customer_id)
  GROUP BY c.customer_state
),
state_payment AS (
  SELECT
    customer_state,
    payment_type,
    COUNT(DISTINCT order_id) AS pedidos_com_pagamento,
    ROW_NUMBER() OVER (
      PARTITION BY customer_state
      ORDER BY COUNT(DISTINCT order_id) DESC, payment_type
    ) AS row_number
  FROM (
    SELECT DISTINCT c.customer_state, f.order_id, f.payment_type
    FROM ${catalog}.olist_gold.fato_vendas f
    JOIN ${catalog}.olist_gold.dim_clientes c USING (customer_id)
    WHERE f.payment_type IS NOT NULL
  ) orders_with_payment
  GROUP BY customer_state, payment_type
)
SELECT
  s.customer_state,
  s.total_pedidos,
  s.receita_brl,
  p.payment_type AS pagamento_predominante,
  p.pedidos_com_pagamento
FROM state_sales s
LEFT JOIN state_payment p
  ON p.customer_state = s.customer_state AND p.row_number = 1
ORDER BY s.receita_brl DESC;
