# Databricks notebook source
"""
Trust: Bronze Ingestion Notebook
Ingests articles from Apify, NewsAPI, and GDELT into the bronze.raw_articles table.
Run this notebook as a Databricks job on a schedule (hourly/daily).
"""

# COMMAND ----------

from datetime import datetime
from uuid import uuid4
import requests
import json

# COMMAND ----------

# Get configuration from setup notebook
CATALOG = spark.conf.get("trust.catalog", "main")
SCHEMA = spark.conf.get("trust.schema", "trust_dev")
BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.raw_articles"

print(f"Ingesting into: {BRONZE_TABLE}")

# COMMAND ----------

# Helper: Get secrets from Databricks secret scope
def get_secret(scope: str, key: str):
    try:
        return dbutils.secrets.get(scope, key)
    except Exception as e:
        print(f"⚠️  Could not retrieve secret {scope}/{key}: {e}")
        return None

# COMMAND ----------

# Normalization functions
def normalize_apify_item(item: dict, source_query: str, apify_run_id: str, ingest_job_run_id: str) -> dict:
    """Normalize Apify scraper output to bronze schema"""
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
    """Normalize NewsAPI output to bronze schema"""
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
    """Normalize GDELT output to bronze schema"""
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

print("✅ Normalization functions ready")

# COMMAND ----------

# Ingestion job run ID (unique for this run)
ingest_job_run_id = str(uuid4())
print(f"Ingest job run ID: {ingest_job_run_id}")

records = []

# COMMAND ----------

# NEWSAPI INGESTION
print("\n=== NewsAPI Ingestion ===")
try:
    newsapi_key = get_secret("trust-secrets", "newsapi-key")
    if newsapi_key:
        query = "technology news"
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "pageSize": 50,
            "page": 1,
            "apiKey": newsapi_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = data.get("articles", [])
        print(f"Fetched {len(articles)} articles from NewsAPI")

        for item in articles:
            normalized = normalize_newsapi_item(item, query, ingest_job_run_id)
            records.append(normalized)

        print(f"✅ NewsAPI: {len(articles)} records added")
    else:
        print("⚠️  NewsAPI key not found in secrets")
except Exception as e:
    print(f"❌ NewsAPI error: {e}")

# COMMAND ----------

# GDELT INGESTION
print("\n=== GDELT Ingestion ===")
try:
    gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": "technology",
        "mode": "json",
        "maxrecords": 100,
        "timespan": "7d",
    }
    response = requests.get(gdelt_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    articles = data.get("articles", [])
    print(f"Fetched {len(articles)} articles from GDELT")

    for item in articles:
        normalized = normalize_gdelt_item(item, "technology", ingest_job_run_id)
        records.append(normalized)

    print(f"✅ GDELT: {len(articles)} records added")
except Exception as e:
    print(f"❌ GDELT error: {e}")

# COMMAND ----------

# APIFY INGESTION (TODO: requires Apify client setup)
print("\n=== Apify Ingestion ===")
try:
    apify_token = get_secret("trust-secrets", "apify-token")
    if apify_token:
        print("⚠️  Apify integration requires apify-client library")
        print("TODO: Install apify-client and configure actor ID")
    else:
        print("⚠️  Apify token not found in secrets")
except Exception as e:
    print(f"❌ Apify error: {e}")

# COMMAND ----------

# WRITE TO BRONZE
print(f"\n=== Writing to Bronze ===")
print(f"Total records to write: {len(records)}")

if records:
    from pyspark.sql.types import *

    # Define schema (must match bronze schema)
    ENTITY_SCHEMA = StructType([
        StructField("name", StringType(), False),
        StructField("type", StringType(), False),
    ])

    BRONZE_SCHEMA = StructType([
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
    ])

    # Create DataFrame and write
    df = spark.createDataFrame(records, schema=BRONZE_SCHEMA)
    df.write.format("delta").mode("append").option("mergeSchema", True).saveAsTable(BRONZE_TABLE)

    print(f"✅ Wrote {len(records)} records to {BRONZE_TABLE}")

    # Show summary
    summary_df = spark.read.table(BRONZE_TABLE)
    print(f"\nBronze table now has {summary_df.count()} total rows")
    print("\nRecent articles by outlet:")
    summary_df.groupBy("outlet").count().show()
else:
    print("❌ No records to write")

# COMMAND ----------

print("\n=== Bronze Ingestion Complete ===")
print(f"Job run ID: {ingest_job_run_id}")
print(f"Timestamp: {datetime.utcnow().isoformat()}")
