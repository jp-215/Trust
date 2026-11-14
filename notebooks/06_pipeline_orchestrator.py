# Databricks notebook source
"""
Trust: Pipeline Orchestrator
Master notebook to run the complete ingestion → silver → gold pipeline.
Execute this as your main Databricks job.
"""

# COMMAND ----------

from datetime import datetime
import time

# COMMAND ----------

print("=" * 80)
print("Trust: Complete Pipeline Orchestration")
print("=" * 80)
print(f"Start time: {datetime.utcnow().isoformat()}")

# COMMAND ----------

# STEP 1: Setup (initialize schemas and configs)
print("\n[1/5] SETUP: Initializing schemas and configuration...")
try:
    %run ./01_setup
    print("✅ Setup complete")
except Exception as e:
    print(f"❌ Setup failed: {e}")
    raise

# COMMAND ----------

# STEP 2: Bronze Ingestion
print("\n[2/5] BRONZE: Ingesting articles from APIs...")
try:
    %run ./02_bronze_ingestion
    print("✅ Bronze ingestion complete")
except Exception as e:
    print(f"❌ Bronze ingestion failed: {e}")
    raise

# COMMAND ----------

# STEP 3: Create DLT Pipeline (or refresh if exists)
print("\n[3/5] DLT: Triggering Delta Live Tables pipeline...")

# Get DLT pipeline ID (you'll need to create the pipeline first in Databricks)
# For now, we'll run the transformations directly as a workaround

CATALOG = spark.conf.get("trust.catalog", "main")
SCHEMA = spark.conf.get("trust.schema", "trust_dev")
BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.raw_articles"
SILVER_TABLE = f"{CATALOG}.{SCHEMA}.claims"
GOLD_TABLE = f"{CATALOG}.{SCHEMA}.story_records"

# For demo: run transformations inline (in production, use DLT pipeline)
try:
    print(f"  Reading from bronze: {BRONZE_TABLE}")

    # SILVER: Extract claims
    print("  → Extracting claims (silver layer)...")
    articles = spark.read.table(BRONZE_TABLE)

    from pyspark.sql.functions import col, pandas_udf, explode, uuid, current_timestamp
    import pandas as pd

    @pandas_udf("array<string>")
    def stub_extract_claims(text_series):
        return text_series.apply(lambda t: [t[:120]] if t else [])

    df_with_claims = articles.withColumn(
        "claim_text_arr",
        stub_extract_claims(col("raw_text"))
    )

    claims_df = (
        df_with_claims
        .filter(col("raw_text").isNotNull())
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

    claims_df.write.format("delta").mode("overwrite").option("mergeSchema", True).saveAsTable(SILVER_TABLE)
    print(f"  ✅ Claims extracted: {claims_df.count()} records → {SILVER_TABLE}")

    # GOLD: Aggregate stories
    print("  → Aggregating stories (gold layer)...")
    from pyspark.sql.functions import collect_set, collect_list, coalesce, lit

    story_records = (
        claims_df
        .groupBy(coalesce(col("story_cluster_id"), lit("unclustered")).alias("story_id"))
        .agg(
            collect_set("outlet").alias("outlets_covering"),
            collect_list(col("article_id")).alias("source_article_ids"),
        )
        .selectExpr(
            "story_id",
            "cast(null as string) as story_title",
            "current_timestamp() as created_at",
            "current_timestamp() as updated_at",
            "outlets_covering",
            "array() as claim_matrix",
            "array() as contradiction_pairs",
            "source_article_ids",
        )
    )

    story_records.write.format("delta").mode("overwrite").option("mergeSchema", True).saveAsTable(GOLD_TABLE)
    print(f"  ✅ Stories aggregated: {story_records.count()} records → {GOLD_TABLE}")

    print("✅ DLT pipeline (inline execution) complete")

except Exception as e:
    print(f"❌ DLT pipeline failed: {e}")
    raise

# COMMAND ----------

# STEP 4: Create gold.story_synthesis table
print("\n[4/5] GOLD SYNTHESIS: Setting up agent output table...")
try:
    %run ./05_gold_synthesis
    print("✅ Gold synthesis table ready")
except Exception as e:
    print(f"❌ Gold synthesis setup failed: {e}")
    raise

# COMMAND ----------

# STEP 5: Verification & Summary
print("\n[5/5] VERIFICATION: Pipeline results...")

try:
    bronze_count = spark.read.table(f"{CATALOG}.{SCHEMA}.raw_articles").count()
    silver_count = spark.read.table(f"{CATALOG}.{SCHEMA}.claims").count()
    gold_count = spark.read.table(f"{CATALOG}.{SCHEMA}.story_records").count()

    print(f"\n📊 Pipeline Summary:")
    print(f"  Bronze (raw articles): {bronze_count} rows")
    print(f"  Silver (claims):       {silver_count} rows")
    print(f"  Gold (stories):        {gold_count} rows")

    if bronze_count > 0:
        print(f"\n  Outlets represented in this run:")
        spark.read.table(f"{CATALOG}.{SCHEMA}.raw_articles").select("outlet").distinct().show(truncate=False)

    if gold_count > 0:
        print(f"\n  Stories aggregated:")
        spark.read.table(f"{CATALOG}.{SCHEMA}.story_records").select("story_id", "outlets_covering").show(truncate=False)

    print("\n✅ Pipeline execution complete!")

except Exception as e:
    print(f"❌ Verification failed: {e}")
    raise

# COMMAND ----------

print("\n" + "=" * 80)
print("🎉 All pipeline stages complete!")
print(f"End time: {datetime.utcnow().isoformat()}")
print("=" * 80)
print("\nNext steps:")
print("  1. Deploy the Gemini agent to synthesize truths from the gold table")
print("  2. Configure DLT pipeline in Databricks for production scheduling")
print("  3. Set up Databricks Workflows for orchestrated runs")
print("  4. Integrate AI Gateway for real claim extraction (phase 2)")
