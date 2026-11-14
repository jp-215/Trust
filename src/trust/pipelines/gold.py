import dlt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, collect_set, collect_list, coalesce, current_timestamp, lit
from trust.schemas.tables import GOLD_SCHEMA


@dlt.table(
    name="story_records",
    comment="Aggregated per-story claim/outlet coverage matrix.",
    schema=GOLD_SCHEMA,
)
def story_records():
    spark = SparkSession.getActiveSession()
    claims = spark.read.table("silver.claims")

    # TODO: Real clustering logic here.
    # Currently stubbed: treat each distinct story_cluster_id as a story.
    # Phase 2: implement entity-based / semantic similarity clustering
    # to group claims from different articles about the same real-world event.

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
            "array() as claim_matrix",
            "array() as contradiction_pairs",
            "source_article_ids",
        )
    )
    return story_records
