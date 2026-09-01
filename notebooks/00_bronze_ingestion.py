# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze — inventário de arquivos brutos
# MAGIC Envie os CSVs originais ao Volume antes de executar este notebook.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "workspace"
BRONZE_SCHEMA = "olist_bronze"
VOLUME = "raw"
RAW_PATH = f"/Volumes/{CATALOG}/{BRONZE_SCHEMA}/{VOLUME}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{BRONZE_SCHEMA}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{BRONZE_SCHEMA}.{VOLUME}")

required_files = [
    "olist_orders_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
]
available = {file.name for file in dbutils.fs.ls(RAW_PATH)}
missing = sorted(set(required_files) - available)
if missing:
    raise ValueError(f"Envie os arquivos Bronze ausentes para {RAW_PATH}: {missing}")

inventory = spark.createDataFrame(
    [(file.name, file.path, file.size) for file in dbutils.fs.ls(RAW_PATH)],
    "file_name string, file_path string, file_size_bytes long",
).withColumn("inventoried_at", F.current_timestamp())

inventory.write.format("delta").mode("overwrite").saveAsTable(
    f"{CATALOG}.{BRONZE_SCHEMA}.bronze_file_inventory"
)
