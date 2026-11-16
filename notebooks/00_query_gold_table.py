# Databricks notebook source
"""
Query Gold Table - Run in Databricks Workspace
This notebook queries the gold.story_records table directly from your workspace.
No special token scopes needed - just attach to a cluster and run!
"""

# COMMAND ----------

# Get configuration
CATALOG = spark.conf.get("trust.catalog", "main")
SCHEMA = spark.conf.get("trust.schema", "trust_dev")

print(f"Querying from: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# Query the gold table
gold_table = f"{CATALOG}.{SCHEMA}.story_records"

try:
    df = spark.read.table(gold_table)
    total_rows = df.count()

    print(f"\n✅ Gold table found: {gold_table}")
    print(f"📊 Total rows: {total_rows}\n")

    if total_rows > 0:
        print("=" * 80)
        print("GOLD TABLE DATA:")
        print("=" * 80)
        df.display()

        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS:")
        print("=" * 80)
        print(f"Total stories: {total_rows}")
        print(f"Stories per outlet:")
        df.select("story_id", "outlets_covering").display()

    else:
        print("⚠️  Gold table is empty. Pipeline may not have run yet.")
        print("Run: 06_pipeline_orchestrator.py")

except Exception as e:
    print(f"❌ Error querying gold table: {e}")
    print(f"\nTable: {gold_table}")
    print("\nTroubleshooting:")
    print("1. Verify catalog/schema exist")
    print("2. Run 06_pipeline_orchestrator.py to populate")
    print("3. Check table permissions")

# COMMAND ----------

# Query story_synthesis table (agent output)
print("\n\n" + "=" * 80)
print("SYNTHESIS TABLE (Agent Output):")
print("=" * 80)

synthesis_table = f"{CATALOG}.{SCHEMA}.story_synthesis"

try:
    df_synthesis = spark.read.table(synthesis_table)
    synthesis_rows = df_synthesis.count()

    print(f"✅ Synthesis table found: {synthesis_table}")
    print(f"📊 Total synthesized stories: {synthesis_rows}\n")

    if synthesis_rows > 0:
        df_synthesis.display()
    else:
        print("⚠️  No synthesized data yet. Run agent to populate:")
        print("   python -m trust_agent.cli --story-id unclustered")

except Exception as e:
    print(f"ℹ️  Synthesis table not yet created or empty: {e}")
    print("   This is normal before running the agent.")

# COMMAND ----------

# Show all Trust tables
print("\n\n" + "=" * 80)
print("ALL TRUST TABLES:")
print("=" * 80)

try:
    spark.sql(f"USE SCHEMA {CATALOG}.{SCHEMA}").show()
    df_tables = spark.sql("SHOW TABLES")
    print(f"\nTables in {CATALOG}.{SCHEMA}:")
    df_tables.display()
except Exception as e:
    print(f"Error listing tables: {e}")

# COMMAND ----------

print("\n✅ Query complete!")
