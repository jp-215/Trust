import os
import sys
from datetime import datetime
from uuid import uuid4

from pyspark.sql import SparkSession
from trust.ingestion.apify_source import ApifySource
from trust.ingestion.newsapi_source import NewsAPISource
from trust.ingestion.gdelt_source import GDELTSource
from trust.ingestion.bronze_writer import (
    normalize_apify_item,
    normalize_newsapi_item,
    normalize_gdelt_item,
    write_bronze,
)


def get_databricks_secret(scope: str, key: str) -> str:
    try:
        dbutils = globals().get("dbutils")
        if dbutils:
            return dbutils.secrets.get(scope, key)
    except Exception:
        pass
    return os.environ.get(key, "")


def main():
    spark = SparkSession.getActiveSession()
    if spark is None:
        spark = SparkSession.builder.appName("trust-ingestion").getOrCreate()

    # Get job run id (fallback to timestamp if not in Databricks context)
    try:
        job_run_id = spark.conf.get("spark.databricks.job.run.id")
    except Exception:
        job_run_id = f"local-{int(datetime.utcnow().timestamp())}"

    ingest_job_run_id = str(uuid4())
    records = []

    # Apify ingestion
    apify_token = get_databricks_secret("trust-secrets", "apify-token") or os.environ.get("APIFY_API_TOKEN", "")
    if apify_token:
        try:
            apify = ApifySource(apify_token, actor_id="apify/web-scraper")
            apify_items = apify.run_and_fetch(
                {
                    "startUrls": [
                        {"url": "https://news.ycombinator.com"},
                        {"url": "https://news.google.com"},
                    ],
                    "useChrome": False,
                }
            )
            for item in apify_items:
                normalized = normalize_apify_item(
                    item,
                    source_query="default-scrape",
                    apify_run_id="stub-run-id",
                    ingest_job_run_id=ingest_job_run_id,
                )
                records.append(normalized)
        except Exception as e:
            print(f"Apify ingestion failed: {e}")

    # NewsAPI ingestion
    newsapi_key = get_databricks_secret("trust-secrets", "newsapi-key") or os.environ.get("NEWSAPI_KEY", "")
    if newsapi_key:
        try:
            newsapi = NewsAPISource(newsapi_key)
            newsapi_items = newsapi.search(query="technology news", page_size=50)
            for item in newsapi_items:
                normalized = normalize_newsapi_item(
                    item,
                    source_query="technology news",
                    ingest_job_run_id=ingest_job_run_id,
                )
                records.append(normalized)
        except Exception as e:
            print(f"NewsAPI ingestion failed: {e}")

    # GDELT ingestion
    try:
        gdelt = GDELTSource()
        gdelt_items = gdelt.search(keywords="technology", max_records=100, time_span="7d")
        for item in gdelt_items:
            normalized = normalize_gdelt_item(
                item,
                source_query="technology",
                ingest_job_run_id=ingest_job_run_id,
            )
            records.append(normalized)
    except Exception as e:
        print(f"GDELT ingestion failed: {e}")

    if records:
        write_bronze(spark, records)
        print(f"Wrote {len(records)} records to bronze.raw_articles")
    else:
        print("No records ingested")


if __name__ == "__main__":
    main()
