from pyspark.sql import DataFrame
from pyspark.sql.functions import pandas_udf, col
from trust.schemas.tables import SILVER_SCHEMA
import pandas as pd


def extract_claims_batch(articles_df: DataFrame, ai_gateway_route: str = None) -> DataFrame:
    """
    Extract discrete claims from articles. Stub implementation returns first 120 chars
    of raw_text as placeholder claim. Real implementation will call AI Gateway route.

    TODO: Replace with real AI Gateway call:
    - POST to configured gateway route with claim-extraction prompt
    - Parse JSON claims from model response
    - Return structured claims per article
    """

    @pandas_udf("array<string>")
    def stub_extract_claims(text_series: pd.Series) -> pd.Series:
        return text_series.apply(lambda t: [t[:120]] if t else [])

    df_with_claims = articles_df.withColumn(
        "claim_text_arr",
        stub_extract_claims(col("raw_text"))
    )

    from pyspark.sql.functions import explode, uuid, current_timestamp

    return (
        df_with_claims
        .selectExpr(
            "uuid() as claim_id",
            "article_id",
            "outlet",
            "explode(claim_text_arr) as claim_text",
            "cast(null as string) as claim_type",
            "array() as entities",
            "cast(null as string) as story_cluster_id",
            f"'{ai_gateway_route or 'stub-v0'}' as extraction_model",
            "current_timestamp() as extracted_at",
            "cast(null as double) as confidence"
        )
    )
