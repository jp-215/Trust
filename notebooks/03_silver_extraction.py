# Databricks notebook source
"""
Trust: Silver Layer - Claim Extraction
DLT notebook for extracting discrete claims from raw articles.
Used in Databricks Delta Live Tables pipeline.
"""

# COMMAND ----------

import dlt
from pyspark.sql.functions import col, pandas_udf, explode, uuid, current_timestamp
import pandas as pd

# COMMAND ----------

# Get configuration
CATALOG = spark.conf.get("trust.catalog", "main")
SCHEMA = spark.conf.get("trust.schema", "trust_dev")
BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.raw_articles"

print(f"Reading from: {BRONZE_TABLE}")

# COMMAND ----------

# Define claim extraction (STUBBED - replace with real AI Gateway call in phase 2)
@pandas_udf("array<string>")
def stub_extract_claims(text_series: pd.Series) -> pd.Series:
    """
    Stub claim extraction: returns first 120 chars of each article as placeholder.

    TODO: Phase 2 - Replace with real AI Gateway call:
    - POST to configured gateway route with claim-extraction prompt
    - Parse JSON claims from model response
    - Return structured claims per article
    """
    return text_series.apply(lambda t: [t[:120]] if t else [])

# COMMAND ----------

# DLT TABLE: Claims
@dlt.table(
    name="claims",
    comment="Discrete claims extracted from articles via AI Gateway",
)
@dlt.expect_or_drop("has_claim_text", "claim_text IS NOT NULL")
def claims():
    """
    Extract claims from bronze articles.

    Stub implementation returns first 120 chars as placeholder.
    Real implementation will use Databricks AI Gateway for extraction.
    """
    articles = spark.read.table(BRONZE_TABLE)

    # Extract claims using stub (one claim per article for now)
    df_with_claims = articles.withColumn(
        "claim_text_arr",
        stub_extract_claims(col("raw_text"))
    )

    # Explode to one row per claim
    claims_df = (
        df_with_claims
        .selectExpr(
            "uuid() as claim_id",
            "article_id",
            "outlet",
            "explode(claim_text_arr) as claim_text",
            "cast(null as string) as claim_type",
            "array() as entities",
            "cast(null as string) as story_cluster_id",
            "'stub-v0' as extraction_model",
            "current_timestamp() as extracted_at",
            "cast(null as double) as confidence"
        )
    )

    return claims_df

# COMMAND ----------

# DLT VIEW: Claims Summary (for monitoring)
@dlt.view(name="claims_summary")
def claims_summary():
    """Summary view: claims per outlet"""
    claims = dlt.read("claims")
    return claims.groupBy("outlet").count().alias("num_claims")

# COMMAND ----------

print("✅ Silver layer (claim extraction) DLT tables defined")
