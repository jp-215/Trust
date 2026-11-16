# Databricks notebook source
"""
Trust: Gold Synthesis Layer
Creates the table for agent-written synthesized truths.
This table is written to by the external Gemini agent, not by DLT.
"""

# COMMAND ----------

from pyspark.sql.types import *

# COMMAND ----------

# Get configuration
CATALOG = spark.conf.get("trust.catalog", "main")
SCHEMA = spark.conf.get("trust.schema", "trust_dev")
GOLD_SYNTHESIS_TABLE = f"{CATALOG}.{SCHEMA}.story_synthesis"

print(f"Creating synthesis table: {GOLD_SYNTHESIS_TABLE}")

# COMMAND ----------

# Create gold.story_synthesis table for agent output
# This is a regular table (not DLT-managed) that the agent writes to

GOLD_SYNTHESIS_SCHEMA = StructType([
    StructField("story_id", StringType(), False),
    StructField("synthesized_truth", StringType(), False),
    StructField("synthesis_metadata", MapType(StringType(), StringType()), True),
    StructField("synthesized_at", TimestampType(), False),
])

# Create or replace the table
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {GOLD_SYNTHESIS_TABLE} (
    story_id STRING NOT NULL,
    synthesized_truth STRING NOT NULL,
    synthesis_metadata MAP<STRING, STRING>,
    synthesized_at TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Agent-synthesized truth statements per story'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true'
)
""")

print(f"✅ Table created: {GOLD_SYNTHESIS_TABLE}")

# COMMAND ----------

# Verify table exists and show schema
result = spark.sql(f"DESCRIBE TABLE {GOLD_SYNTHESIS_TABLE}")
result.show()

print(f"\n✅ Gold synthesis table is ready for agent writes")
print(f"   Agent can INSERT or MERGE into this table")
print(f"   Example INSERT:")
print(f"   INSERT INTO {GOLD_SYNTHESIS_TABLE}")
print(f"   VALUES ('story-123', 'Synthesized narrative here...', map('model', 'gemini-2.0-flash'), current_timestamp())")
