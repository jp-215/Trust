# Databricks notebook source
"""
Trust: Setup & Configuration Notebook
Initializes catalogs, schemas, and shared configurations for the pipeline.
Run this FIRST before any other notebooks.
"""

# COMMAND ----------

from pyspark.sql.types import *
import json

# COMMAND ----------

# Configuration - EDIT THESE FOR YOUR ENVIRONMENT
CATALOG = "main"
SCHEMA = "trust_dev"
BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.raw_articles"
SILVER_TABLE = f"{CATALOG}.{SCHEMA}.claims"
GOLD_TABLE = f"{CATALOG}.{SCHEMA}.story_records"
GOLD_SYNTHESIS_TABLE = f"{CATALOG}.{SCHEMA}.story_synthesis"

print(f"Using catalog: {CATALOG}")
print(f"Using schema: {SCHEMA}")

# COMMAND ----------

# Create schema if it doesn't exist
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"Schema {CATALOG}.{SCHEMA} ready")

# COMMAND ----------

# Define schemas (single source of truth)
ENTITY_SCHEMA = StructType([
    StructField("name", StringType(), False),
    StructField("type", StringType(), False),
])

BRONZE_SCHEMA = StructType([
    StructField("article_id", StringType(), False),
    StructField("source_type", StringType(), False),
    StructField("outlet", StringType(), False),
    StructField("url", StringType(), False),
    StructField("published_at", TimestampType(), False),
    StructField("scraped_at", TimestampType(), False),
    StructField("title", StringType(), False),
    StructField("raw_text", StringType(), False),
    StructField("author", StringType(), True),
    StructField("language", StringType(), True),
    StructField("apify_run_id", StringType(), True),
    StructField("source_query", StringType(), True),
    StructField("ingest_job_run_id", StringType(), False),
    StructField("raw_metadata", MapType(StringType(), StringType()), True),
])

SILVER_SCHEMA = StructType([
    StructField("claim_id", StringType(), False),
    StructField("article_id", StringType(), False),
    StructField("outlet", StringType(), False),
    StructField("claim_text", StringType(), False),
    StructField("claim_type", StringType(), True),
    StructField("entities", ArrayType(ENTITY_SCHEMA), False),
    StructField("story_cluster_id", StringType(), True),
    StructField("extraction_model", StringType(), False),
    StructField("extracted_at", TimestampType(), False),
    StructField("confidence", DoubleType(), True),
])

CLAIM_MATRIX_ITEM_SCHEMA = StructType([
    StructField("claim_text", StringType(), False),
    StructField("canonical_claim_id", StringType(), False),
    StructField("outlets_reporting", ArrayType(StringType()), False),
    StructField("outlets_silent", ArrayType(StringType()), False),
    StructField("agreement_status", StringType(), False),
])

CONTRADICTION_PAIR_SCHEMA = StructType([
    StructField("outlet_a", StringType(), False),
    StructField("outlet_b", StringType(), False),
    StructField("claim_a", StringType(), False),
    StructField("claim_b", StringType(), False),
])

GOLD_SCHEMA = StructType([
    StructField("story_id", StringType(), False),
    StructField("story_title", StringType(), True),
    StructField("created_at", TimestampType(), False),
    StructField("updated_at", TimestampType(), False),
    StructField("outlets_covering", ArrayType(StringType()), False),
    StructField("claim_matrix", ArrayType(CLAIM_MATRIX_ITEM_SCHEMA), False),
    StructField("contradiction_pairs", ArrayType(CONTRADICTION_PAIR_SCHEMA), False),
    StructField("source_article_ids", ArrayType(StringType()), False),
])

GOLD_SYNTHESIS_SCHEMA = StructType([
    StructField("story_id", StringType(), False),
    StructField("synthesized_truth", StringType(), False),
    StructField("synthesis_metadata", MapType(StringType(), StringType()), True),
    StructField("synthesized_at", TimestampType(), False),
])

print("✅ Schemas defined")

# COMMAND ----------

# Save schemas to a global dict for other notebooks to reference
spark.conf.set("trust.catalog", CATALOG)
spark.conf.set("trust.schema", SCHEMA)
spark.conf.set("trust.bronze_table", BRONZE_TABLE)
spark.conf.set("trust.silver_table", SILVER_TABLE)
spark.conf.set("trust.gold_table", GOLD_TABLE)
spark.conf.set("trust.gold_synthesis_table", GOLD_SYNTHESIS_TABLE)

# Create a shared variables widget for easy config updates
dbutils.widgets.text("catalog", CATALOG)
dbutils.widgets.text("schema", SCHEMA)

print("✅ Configuration complete. Shared settings saved.")
print(f"Bronze table: {BRONZE_TABLE}")
print(f"Silver table: {SILVER_TABLE}")
print(f"Gold table: {GOLD_TABLE}")
print(f"Gold synthesis table: {GOLD_SYNTHESIS_TABLE}")
