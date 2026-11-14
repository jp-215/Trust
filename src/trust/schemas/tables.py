from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
    ArrayType,
    MapType,
    DoubleType,
)

BRONZE_SCHEMA = StructType(
    [
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
    ]
)

ENTITY_SCHEMA = StructType(
    [
        StructField("name", StringType(), False),
        StructField("type", StringType(), False),
    ]
)

SILVER_SCHEMA = StructType(
    [
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
    ]
)

CLAIM_MATRIX_ITEM_SCHEMA = StructType(
    [
        StructField("claim_text", StringType(), False),
        StructField("canonical_claim_id", StringType(), False),
        StructField("outlets_reporting", ArrayType(StringType()), False),
        StructField("outlets_silent", ArrayType(StringType()), False),
        StructField("agreement_status", StringType(), False),
    ]
)

CONTRADICTION_PAIR_SCHEMA = StructType(
    [
        StructField("outlet_a", StringType(), False),
        StructField("outlet_b", StringType(), False),
        StructField("claim_a", StringType(), False),
        StructField("claim_b", StringType(), False),
    ]
)

GOLD_SCHEMA = StructType(
    [
        StructField("story_id", StringType(), False),
        StructField("story_title", StringType(), True),
        StructField("created_at", TimestampType(), False),
        StructField("updated_at", TimestampType(), False),
        StructField("outlets_covering", ArrayType(StringType()), False),
        StructField("claim_matrix", ArrayType(CLAIM_MATRIX_ITEM_SCHEMA), False),
        StructField("contradiction_pairs", ArrayType(CONTRADICTION_PAIR_SCHEMA), False),
        StructField("source_article_ids", ArrayType(StringType()), False),
    ]
)

GOLD_SYNTHESIS_SCHEMA = StructType(
    [
        StructField("story_id", StringType(), False),
        StructField("synthesized_truth", StringType(), False),
        StructField("synthesis_metadata", MapType(StringType(), StringType()), True),
        StructField("synthesized_at", TimestampType(), False),
    ]
)
