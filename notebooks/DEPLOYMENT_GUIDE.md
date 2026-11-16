# Trust Databricks Notebooks - Deployment Guide

## Overview

The Trust pipeline is now packaged as **standalone Databricks notebooks** for easy deployment to your Databricks workspace. Each notebook is self-contained and plug-and-play.

## Notebook Structure

| # | Notebook | Purpose | Type | Run as Job? |
|---|---|---|---|---|
| 01 | `01_setup.py` | Initialize schemas, define data models | Setup | ❌ No (dependency) |
| 02 | `02_bronze_ingestion.py` | Ingest from APIs into bronze | Ingestion | ✅ **Yes** |
| 03 | `03_silver_extraction.py` | Extract claims (DLT format) | DLT | ❌ DLT pipeline |
| 04 | `04_gold_aggregation.py` | Aggregate stories (DLT format) | DLT | ❌ DLT pipeline |
| 05 | `05_gold_synthesis.py` | Create agent output table | Setup | ❌ No (dependency) |
| 06 | `06_pipeline_orchestrator.py` | Master orchestration | Orchestrator | ✅ **Yes** |

## Quick Start (5 minutes)

### Step 1: Upload Notebooks to Databricks

1. In your Databricks workspace, create a folder: `/Workspace/Trust/`
2. Upload all `.py` files from the `notebooks/` directory
3. The structure should be:
   ```
   /Workspace/Trust/
   ├── 01_setup.py
   ├── 02_bronze_ingestion.py
   ├── 03_silver_extraction.py
   ├── 04_gold_aggregation.py
   ├── 05_gold_synthesis.py
   └── 06_pipeline_orchestrator.py
   ```

### Step 2: Configure Secrets (for real API access)

In Databricks, create a secret scope `trust-secrets`:

```bash
# Via Databricks CLI
databricks secrets create-scope --scope trust-secrets

# Add your API keys
databricks secrets put --scope trust-secrets --key newsapi-key --string-value <your-newsapi-key>
databricks secrets put --scope trust-secrets --key apify-token --string-value <your-apify-token>
```

Or in the Databricks UI:
- Go to **User Settings > Secrets**
- Create scope: `trust-secrets`
- Add secrets: `newsapi-key`, `apify-token`

### Step 3: Run the Orchestrator

Open the orchestrator notebook (`06_pipeline_orchestrator.py`) and click **Run All**.

It will:
1. ✅ Initialize schemas and configs
2. ✅ Ingest from APIs into bronze
3. ✅ Extract claims (silver)
4. ✅ Aggregate stories (gold)
5. ✅ Create synthesis table
6. ✅ Show summary

Expected output:
```
📊 Pipeline Summary:
  Bronze (raw articles): 150 rows
  Silver (claims):       450 rows
  Gold (stories):        5 rows
```

## Setup for Production (15 minutes)

### Option A: Single Orchestrator Job (Recommended for Phase 1)

1. Create a new Databricks Job:
   - **Task name**: `trust-pipeline`
   - **Notebook**: `06_pipeline_orchestrator`
   - **Cluster**: Create a new all-purpose cluster (or select existing)
   - **Schedule**: Hourly or Daily (your choice)

2. Run the job — it orchestrates the entire pipeline

### Option B: DLT Pipeline (Recommended for Phase 2+)

When ready for production with real claim extraction:

1. Create a **Delta Live Tables Pipeline**:
   - **Pipeline name**: `trust-dlt-pipeline`
   - **Notebook libraries**:
     - `03_silver_extraction`
     - `04_gold_aggregation`
   - **Target**: `main.trust_dev` (your catalog.schema)
   - **Storage location**: (auto-generated or specify)

2. Create a Databricks Job that:
   - **Task 1**: Runs `02_bronze_ingestion`
   - **Task 2** (downstream): Triggers the DLT pipeline
   - **Schedule**: Hourly

### Option C: Full Databricks Workflow (Production)

For maximum control and monitoring:

1. Create a **Databricks Workflow** with tasks:
   ```
   Task 1: 01_setup (notebook)
      ↓
   Task 2: 02_bronze_ingestion (notebook)
      ↓
   Task 3: 03_silver_extraction + 04_gold_aggregation (DLT pipeline)
      ↓
   Task 4: 05_gold_synthesis (notebook)
      ↓
   Task 5: Trigger Gemini agent (if separate job)
   ```

## Configuration

### Customize Catalog/Schema

Open any notebook and edit the top lines:

```python
CATALOG = "main"      # Change to your catalog
SCHEMA = "trust_dev"  # Change to your schema name
```

Or use Databricks widgets to parameterize:

```python
dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "trust_dev")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
```

### Enable/Disable API Sources

In `02_bronze_ingestion.py`, comment out sources you don't want:

```python
# NEWSAPI INGESTION
# try:
#     ... (entire section)
# except Exception as e:
#     ...

# GDELT INGESTION
try:
    ... (keep this)
except Exception as e:
    ...
```

## Monitoring & Troubleshooting

### Check Pipeline Status

Run this in any notebook:

```python
CATALOG = "main"
SCHEMA = "trust_dev"

bronze_count = spark.read.table(f"{CATALOG}.{SCHEMA}.raw_articles").count()
silver_count = spark.read.table(f"{CATALOG}.{SCHEMA}.claims").count()
gold_count = spark.read.table(f"{CATALOG}.{SCHEMA}.story_records").count()

print(f"Bronze: {bronze_count}, Silver: {silver_count}, Gold: {gold_count}")
```

### View Recent Data

```python
spark.read.table(f"{CATALOG}.{SCHEMA}.raw_articles") \
    .orderBy("scraped_at desc") \
    .select("outlet", "title", "scraped_at") \
    .limit(10) \
    .display()
```

### Common Issues

| Issue | Solution |
|---|---|
| "Secret not found" | Create scope `trust-secrets` in Databricks and add keys |
| "Table not found" | Run `01_setup.py` first, or create catalog/schema manually |
| "No data in bronze" | Check API keys, network connectivity, API rate limits |
| "Claims extraction slow" | Normal for stub implementation; phase 2 will optimize |

## Phase 2: AI Gateway Integration

When ready to use real claim extraction:

1. Configure Databricks AI Gateway (Admin panel)
2. Update `03_silver_extraction.py`:
   ```python
   # Replace stub_extract_claims with real gateway call
   # See comments marked "TODO: Phase 2"
   ```

3. Re-run pipeline

## Phase 3: Gemini Agent Integration

To run the external Gemini agent:

```bash
# On your local machine (or wherever the agent runs)
export GEMINI_API_KEY=<your-key>
export DATABRICKS_SERVER_HOSTNAME=<workspace-url>
export DATABRICKS_HTTP_PATH=<warehouse-path>
export DATABRICKS_TOKEN=<pat>

python -m trust_agent.cli --story-id unclustered
```

The agent will query the gold table and write synthesized results to `gold.story_synthesis`.

## Performance Tips

- **Increase ingestion frequency**: Change cron to hourly
- **Optimize DLT**: Use photon clusters for faster processing
- **Monitor costs**: Set resource limits in job clusters
- **Incremental updates**: Use MERGE instead of OVERWRITE in production

## Next Steps

1. ✅ Upload notebooks to Databricks
2. ✅ Configure secrets (API keys)
3. ✅ Create and run first job
4. ⏭️ Integrate AI Gateway (phase 2)
5. ⏭️ Deploy Gemini agent (phase 3)
6. ⏭️ Build web UI (phase 4)

## Support

For issues or questions:
- Check the README.md in the root directory
- Review notebook comments (marked with TODO)
- Verify all secrets are correctly configured
- Ensure cluster has internet access for API calls
