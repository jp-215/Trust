#!/usr/bin/env python
"""
Seed bronze table with sample articles for local development/testing.
Bypasses Apify entirely, loads fixtures directly.

Usage:
  python scripts/seed_dev_data.py
"""

import json
import sys
from pathlib import Path

from pyspark.sql import SparkSession
from trust.ingestion.bronze_writer import write_bronze

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"


def main():
    spark = SparkSession.builder.appName("trust-seed-dev").getOrCreate()

    fixtures_file = FIXTURES_DIR / "sample_articles.json"
    if not fixtures_file.exists():
        print(f"Fixtures file not found: {fixtures_file}")
        sys.exit(1)

    with open(fixtures_file) as f:
        records = json.load(f)

    print(f"Loaded {len(records)} sample articles from {fixtures_file}")

    write_bronze(spark, records, table_name="bronze.raw_articles")
    print(f"Wrote {len(records)} records to bronze.raw_articles")

    # Verify the write
    df = spark.read.table("bronze.raw_articles")
    print(f"Bronze table now has {df.count()} rows")
    df.show(truncate=False)


if __name__ == "__main__":
    main()
