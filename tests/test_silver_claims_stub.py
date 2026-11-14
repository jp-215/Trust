import unittest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, ArrayType, MapType
from trust.schemas.tables import BRONZE_SCHEMA, SILVER_SCHEMA
from trust.pipelines.ai_gateway_client import extract_claims_batch
from datetime import datetime


class TestSilverClaimsStub(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("test-silver-claims").getOrCreate()
        cls.spark.conf.set("spark.sql.shuffle.partitions", "1")

    def test_extract_claims_stub_produces_claims(self):
        data = [
            {
                "article_id": "art-001",
                "source_type": "test",
                "outlet": "CNN",
                "url": "https://test.com",
                "published_at": datetime.utcnow(),
                "scraped_at": datetime.utcnow(),
                "title": "Test",
                "raw_text": "This is a test article with some important information.",
                "author": None,
                "language": "en",
                "apify_run_id": None,
                "source_query": "test",
                "ingest_job_run_id": "job-001",
                "raw_metadata": {},
            }
        ]

        df = self.spark.createDataFrame(data, schema=BRONZE_SCHEMA)
        claims_df = extract_claims_batch(df)

        assert claims_df.count() > 0
        assert "claim_id" in claims_df.columns
        assert "claim_text" in claims_df.columns
        assert "outlet" in claims_df.columns

    def test_extract_claims_stub_schema(self):
        data = [
            {
                "article_id": "art-002",
                "source_type": "test",
                "outlet": "ABC",
                "url": "https://test.com",
                "published_at": datetime.utcnow(),
                "scraped_at": datetime.utcnow(),
                "title": "Test",
                "raw_text": "Another test article content here.",
                "author": None,
                "language": "en",
                "apify_run_id": None,
                "source_query": "test",
                "ingest_job_run_id": "job-002",
                "raw_metadata": {},
            }
        ]

        df = self.spark.createDataFrame(data, schema=BRONZE_SCHEMA)
        claims_df = extract_claims_batch(df)

        columns = claims_df.columns
        assert "claim_id" in columns
        assert "article_id" in columns
        assert "outlet" in columns
        assert "claim_text" in columns
        assert "extraction_model" in columns


if __name__ == "__main__":
    unittest.main()
