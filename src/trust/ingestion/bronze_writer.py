from datetime import datetime
from uuid import uuid4
from pyspark.sql import SparkSession
from trust.schemas.tables import BRONZE_SCHEMA


def normalize_apify_item(item: dict, source_query: str, apify_run_id: str, ingest_job_run_id: str) -> dict:
    return {
        "article_id": str(uuid4()),
        "source_type": "apify_scrape",
        "outlet": item.get("outlet", "Unknown"),
        "url": item.get("url", ""),
        "published_at": item.get("published_at") or datetime.utcnow().isoformat(),
        "scraped_at": datetime.utcnow().isoformat(),
        "title": item.get("title", ""),
        "raw_text": item.get("raw_text", ""),
        "author": item.get("author"),
        "language": item.get("language"),
        "apify_run_id": apify_run_id,
        "source_query": source_query,
        "ingest_job_run_id": ingest_job_run_id,
        "raw_metadata": item.get("raw_metadata", {}),
    }


def normalize_newsapi_item(item: dict, source_query: str, ingest_job_run_id: str) -> dict:
    return {
        "article_id": str(uuid4()),
        "source_type": "newsapi",
        "outlet": item.get("source", {}).get("name", "Unknown"),
        "url": item.get("url", ""),
        "published_at": item.get("publishedAt") or datetime.utcnow().isoformat(),
        "scraped_at": datetime.utcnow().isoformat(),
        "title": item.get("title", ""),
        "raw_text": item.get("content", "") or item.get("description", ""),
        "author": item.get("author"),
        "language": item.get("language"),
        "apify_run_id": None,
        "source_query": source_query,
        "ingest_job_run_id": ingest_job_run_id,
        "raw_metadata": {"source_id": item.get("source", {}).get("id", "")},
    }


def normalize_gdelt_item(item: dict, source_query: str, ingest_job_run_id: str) -> dict:
    return {
        "article_id": str(uuid4()),
        "source_type": "gdelt",
        "outlet": item.get("source", "Unknown"),
        "url": item.get("url", ""),
        "published_at": item.get("published_at") or datetime.utcnow().isoformat(),
        "scraped_at": datetime.utcnow().isoformat(),
        "title": item.get("title", ""),
        "raw_text": item.get("content", ""),
        "author": item.get("author"),
        "language": item.get("language"),
        "apify_run_id": None,
        "source_query": source_query,
        "ingest_job_run_id": ingest_job_run_id,
        "raw_metadata": item.get("raw_metadata", {}),
    }


def write_bronze(spark: SparkSession, records: list[dict], table_name: str = "bronze.raw_articles") -> None:
    if not records:
        return

    df = spark.createDataFrame(records, schema=BRONZE_SCHEMA)
    df.write.format("delta").mode("append").option("mergeSchema", True).saveAsTable(table_name)
