import dlt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from trust.pipelines.ai_gateway_client import extract_claims_batch
from trust.schemas.tables import SILVER_SCHEMA


@dlt.table(
    name="claims",
    comment="Discrete claims extracted from articles via AI Gateway.",
    schema=SILVER_SCHEMA,
)
@dlt.expect_or_drop("has_claim_text", "claim_text IS NOT NULL")
def claims():
    spark = SparkSession.getActiveSession()
    articles = spark.read.table("bronze.raw_articles")

    claims_df = extract_claims_batch(articles, ai_gateway_route="trust-claim-extractor")
    return claims_df
