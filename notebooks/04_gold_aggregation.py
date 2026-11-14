# Databricks notebook source
"""
Trust: Gold Layer - Story Aggregation & Synthesis Prep
DLT notebook for aggregating claims into story records.
Used in Databricks Delta Live Tables pipeline.
"""

# COMMAND ----------

import dlt
from pyspark.sql.functions import col, collect_set, collect_list, coalesce, current_timestamp, lit

# COMMAND ----------

# Get configuration
CATALOG = spark.conf.get("trust.catalog", "main")
SCHEMA = spark.conf.get("trust.schema", "trust_dev")

CLAIMS_TABLE = f"{CATALOG}.{SCHEMA}.claims"
STORY_RECORDS_TABLE = f"{CATALOG}.{SCHEMA}.story_records"

print(f"Reading from: {CLAIMS_TABLE}")
print(f"Writing to: {STORY_RECORDS_TABLE}")

# COMMAND ----------

# DLT TABLE: Story Records (Gold Layer)
@dlt.table(
    name="story_records",
    comment="Aggregated per-story claim/outlet coverage matrix",
)
def story_records():
    """
    Aggregate claims into story records.

    STUBBED: Current implementation groups by story_cluster_id (all null).
    All claims land under 'unclustered' story.

    TODO: Phase 2 - Implement real clustering:
    - Entity-based semantic similarity grouping
    - Cross-article story identification
    - Real agreement/contradiction detection
    """
    claims = dlt.read("claims")

    # Group by story_cluster_id (stub: all null -> all in "unclustered")
    story_records = (
        claims
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
            "array() as claim_matrix",  # TODO: Phase 2 - populate with real claims per outlet
            "array() as contradiction_pairs",  # TODO: Phase 2 - detect contradictions
            "source_article_ids",
        )
    )

    return story_records

# COMMAND ----------

# DLT VIEW: Story Coverage Summary
@dlt.view(name="story_coverage_summary")
def story_coverage_summary():
    """Summary view: outlets per story"""
    stories = dlt.read("story_records")
    return (
        stories
        .selectExpr(
            "story_id",
            "size(outlets_covering) as num_outlets",
            "outlets_covering",
            "size(source_article_ids) as num_articles"
        )
        .orderBy(col("num_articles").desc())
    )

# COMMAND ----------

# DLT VIEW: Outlet Activity
@dlt.view(name="outlet_activity")
def outlet_activity():
    """Summary view: which outlets are reporting on which stories"""
    stories = dlt.read("story_records")
    return (
        stories
        .selectExpr(
            "story_id",
            "explode(outlets_covering) as outlet",
            "size(outlets_covering) as total_outlets_on_story"
        )
        .groupBy("outlet")
        .agg(
            {"outlet": "count"}
        )
        .withColumnRenamed("count(outlet)", "stories_reported")
        .orderBy(col("stories_reported").desc())
    )

# COMMAND ----------

print("✅ Gold layer (story aggregation) DLT tables defined")
