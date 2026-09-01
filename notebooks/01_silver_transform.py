# Databricks notebook source
# MAGIC %md
# MAGIC # Silver — limpeza, padronização e métricas de qualidade

# COMMAND ----------

from pyspark.sql import Window, functions as F

CATALOG = "workspace"
BRONZE_SCHEMA = "olist_bronze"
SILVER_SCHEMA = "olist_silver"
RAW_PATH = f"/Volumes/{CATALOG}/{BRONZE_SCHEMA}/raw"
SILVER = f"{CATALOG}.{SILVER_SCHEMA}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SILVER}")


def read_csv(file_name):
    return spark.read.option("header", True).csv(f"{RAW_PATH}/{file_name}")


def first_by_key(dataframe, keys):
    return dataframe.withColumn(
        "_row_number", F.row_number().over(Window.partitionBy(*keys).orderBy(F.lit(1)))
    ).filter("_row_number = 1").drop("_row_number")


def save(dataframe, table_name):
    dataframe.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER}.{table_name}")


# COMMAND ----------

orders_raw = read_csv("olist_orders_dataset.csv")
orders_with_keys = orders_raw.filter("order_id IS NOT NULL AND customer_id IS NOT NULL")
orders = first_by_key(orders_with_keys, ["order_id"])
for column in [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]:
    orders = orders.withColumn(column, F.to_timestamp(column))
orders.cache()
save(orders, "orders")

customers_raw = read_csv("olist_customers_dataset.csv")
customers = first_by_key(customers_raw.filter("customer_id IS NOT NULL"), ["customer_id"])
save(customers, "customers")

items_raw = read_csv("olist_order_items_dataset.csv")
items = first_by_key(
    items_raw.filter("order_id IS NOT NULL AND product_id IS NOT NULL"),
    ["order_id", "order_item_id"],
).withColumn("order_item_id", F.col("order_item_id").cast("int")).withColumn(
    "price", F.col("price").cast("decimal(12,2)")
).withColumn("freight_value", F.col("freight_value").cast("decimal(12,2)"))
items.cache()
save(items, "order_items")

products_raw = read_csv("olist_products_dataset.csv")
products = first_by_key(products_raw.filter("product_id IS NOT NULL"), ["product_id"]).withColumn(
    "product_category_name", F.coalesce("product_category_name", F.lit("sem_categoria"))
)
save(products, "products")

# COMMAND ----------

reviews_raw = read_csv("olist_order_reviews_dataset.csv")
reviews = first_by_key(reviews_raw.filter("order_id IS NOT NULL"), ["order_id"]).withColumn(
    "review_score", F.col("review_score").cast("int")
).filter("review_score BETWEEN 1 AND 5")
save(reviews, "reviews")

payments_raw = read_csv("olist_order_payments_dataset.csv")
payments = payments_raw.filter("order_id IS NOT NULL").withColumn(
    "payment_sequential", F.col("payment_sequential").cast("int")
)
payments = first_by_key(payments, ["order_id", "payment_sequential"])
save(payments, "payments")

# COMMAND ----------

quality_metrics = [
    ("orders", "completude", "order_id_nulo", orders_raw.filter("order_id IS NULL").count()),
    ("orders", "unicidade", "order_id_duplicado", orders_with_keys.count() - orders.count()),
    ("orders", "acuracia", "entrega_acima_500_dias", orders.filter(
        F.datediff("order_delivered_customer_date", "order_purchase_timestamp") > 500
    ).count()),
    ("reviews", "completude", "review_score_nulo", reviews_raw.filter("review_score IS NULL").count()),
    ("items", "outliers", "frete_acima_p99", items.filter(
        F.col("freight_value") > items.approxQuantile("freight_value", [0.99], 0.01)[0]
    ).count()),
]
spark.createDataFrame(
    quality_metrics, "table_name string, dimension string, metric string, metric_value long"
).withColumn("measured_at", F.current_timestamp()).write.format("delta").mode(
    "overwrite"
).saveAsTable(f"{SILVER}.data_quality_metrics")
orders.unpersist()
items.unpersist()
