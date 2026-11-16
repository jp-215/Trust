# Databricks Configuration Checklist

This document outlines **everything you need to configure** in your Databricks workspace for the Trust pipeline to run.

---

## ✅ Pre-Flight (Do First)

### 1. Workspace Access
- [ ] You have a Databricks workspace (AWS/Azure/GCP)
- [ ] You have Admin or can create clusters, jobs, pipelines
- [ ] You can access the workspace via web UI or CLI

### 2. Databricks CLI
- [ ] Databricks CLI installed: `pip install databricks-cli`
- [ ] Authenticated: `databricks configure --token`
- [ ] Test: `databricks workspace list-jobs` (should return results or empty)

---

## 🏗️ Infrastructure Setup

### 3. Create Catalog (if not using `main`)
```sql
-- In Databricks SQL editor
CREATE CATALOG IF NOT EXISTS trust_catalog;
USE CATALOG trust_catalog;
```

### 4. Create Schema
```sql
CREATE SCHEMA IF NOT EXISTS trust_dev;
-- OR use existing: trust_prod, trust_staging, etc.
```

### 5. Create Compute (Cluster or SQL Warehouse)

**Option A: All-Purpose Cluster** (recommended for notebooks)
```
Name: trust-cluster
Spark version: 14.3 LTS or newer
Node type: i3.xlarge (or similar)
Min workers: 2
Max workers: 4
Auto-terminate: 30 minutes
```

**Option B: SQL Warehouse** (recommended for queries)
```
Name: trust-warehouse
Cluster size: Pro or Classic (2-4 cores)
Auto-stop: 15 minutes
```

**Option C: Job cluster** (created automatically by jobs)
- Defined in notebook as part of job config

- [ ] Cluster created and running
- [ ] You can execute a simple query: `SELECT 1;`

---

## 🔐 Secrets Setup

### 6. Create Secret Scope
```bash
databricks secrets create-scope --scope trust-secrets
```

Verify:
```bash
databricks secrets list-scopes
# Should show: trust-secrets
```

### 7. Add API Keys to Secrets

**If using NewsAPI:**
```bash
databricks secrets put --scope trust-secrets --key newsapi-key
# Paste your NewsAPI key when prompted
```

**If using Apify:**
```bash
databricks secrets put --scope trust-secrets --key apify-token
# Paste your Apify token when prompted
```

**Verify:**
```bash
databricks secrets list --scope trust-secrets
# Should show: newsapi-key, apify-token (without values)
```

- [ ] Secret scope `trust-secrets` created
- [ ] API keys added (or marked as "optional, will use stubs")

---

## 📓 Upload Notebooks

### 8. Create Workspace Folder
```bash
databricks workspace mkdirs /Workspace/Trust/
```

Or in UI:
- Click **Workspace** → Create → Folder → Name: `Trust`

### 9. Upload Notebook Files
```bash
# From repo root
databricks workspace import notebooks/01_setup.py /Workspace/Trust/01_setup.py --language PYTHON
databricks workspace import notebooks/02_bronze_ingestion.py /Workspace/Trust/02_bronze_ingestion.py --language PYTHON
databricks workspace import notebooks/03_silver_extraction.py /Workspace/Trust/03_silver_extraction.py --language PYTHON
databricks workspace import notebooks/04_gold_aggregation.py /Workspace/Trust/04_gold_aggregation.py --language PYTHON
databricks workspace import notebooks/05_gold_synthesis.py /Workspace/Trust/05_gold_synthesis.py --language PYTHON
databricks workspace import notebooks/06_pipeline_orchestrator.py /Workspace/Trust/06_pipeline_orchestrator.py --language PYTHON
```

Or manually:
1. In Databricks UI, go to `/Workspace/Trust/`
2. Click **Create** → **Notebook**
3. Copy-paste code from each `.py` file

- [ ] All 6 notebooks uploaded to `/Workspace/Trust/`
- [ ] You can see them in the UI

---

## 🔧 Configure Notebooks

### 10. Edit Catalog/Schema in Notebooks

Open each notebook and verify/update:

```python
# At the top of each notebook, check:
CATALOG = "main"        # ← Change if needed
SCHEMA = "trust_dev"    # ← Change if needed
```

**Options:**
- Use `main` catalog (default in most workspaces)
- Use a custom catalog you created in step 3

- [ ] Notebooks point to correct catalog/schema
- [ ] Schema exists (create if needed)

---

## ⚡ Run Orchestrator

### 11. Test Bronze Ingestion Notebook
```
1. Open: /Workspace/Trust/02_bronze_ingestion.py
2. Attach to cluster (from step 5)
3. Click "Run All"
```

**Expected output:**
```
=== NewsAPI Ingestion ===
Fetched 50 articles from NewsAPI
✅ NewsAPI: 50 records added

=== GDELT Ingestion ===
Fetched 100 articles from GDELT
✅ GDELT: 100 records added

✅ Wrote 150 records to {CATALOG}.{SCHEMA}.raw_articles
```

- [ ] Bronze ingestion runs without errors
- [ ] Articles table populated (check with `SELECT COUNT(*) FROM {catalog}.{schema}.raw_articles`)

### 12. Run Full Pipeline
```
1. Open: /Workspace/Trust/06_pipeline_orchestrator.py
2. Attach to cluster
3. Click "Run All"
```

**Expected output:**
```
[1/5] SETUP ✅
[2/5] BRONZE: 150 rows ✅
[3/5] DLT: Claims extracted ✅
[4/5] GOLD: Stories aggregated ✅
[5/5] VERIFICATION ✅

📊 Pipeline Summary:
  Bronze: 150 rows
  Silver: 450 rows
  Gold: 5 rows
```

- [ ] Orchestrator completes successfully
- [ ] All tables created (check in Data Explorer)

---

## 📊 Verify Tables Exist

Run in Databricks SQL editor:

```sql
-- List your tables
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'trust_dev'
ORDER BY table_name;
```

Expected result:
```
claims              MANAGED
raw_articles       MANAGED
story_records      MANAGED
story_synthesis    MANAGED
claims_summary     VIEW
story_coverage_summary  VIEW
outlet_activity    VIEW
```

- [ ] All tables created
- [ ] Schemas match expectations

---

## 🤖 Set Up DLT Pipeline (Optional, Phase 2)

When ready for production scheduling:

### 13. Create Delta Live Tables Pipeline

In Databricks UI:
1. Go to **Workflows** → **Delta Live Tables**
2. Click **Create pipeline**
3. Configure:
   ```
   Name: trust-dlt-pipeline
   Notebook libraries:
     - /Workspace/Trust/03_silver_extraction.py
     - /Workspace/Trust/04_gold_aggregation.py
   Target: main.trust_dev
   Storage: (auto or specify)
   ```
4. Save

- [ ] DLT pipeline created
- [ ] Can run manually and see DAG

---

## ⏰ Set Up Jobs/Workflows (Optional, Phase 2)

### 14. Create Scheduled Ingestion Job

In Databricks UI:
1. Go to **Workflows** → **Jobs**
2. Click **Create job**
3. Configure:
   ```
   Job name: trust-bronze-ingestion
   Task name: ingest
   Type: Notebook
   Notebook: /Workspace/Trust/02_bronze_ingestion.py
   Cluster: trust-cluster (or new job cluster)
   Schedule: Hourly or Daily
   ```
4. Save and enable

- [ ] Ingestion job created
- [ ] Scheduled to run (hourly/daily)

### 15. Create Orchestration Workflow (Optional)

For multi-step workflows:
```
Task 1: 01_setup → Task 2: 02_bronze_ingestion 
       → Task 3: DLT pipeline → Task 4: (external agent call)
```

See **Databricks Workflows** documentation for details.

- [ ] Workflow created (optional for phase 1)

---

## 🔗 Integration Points

### 16. Gemini Agent Configuration

For the external agent to query your gold table:

```bash
# Set environment variables on your local machine
export GEMINI_API_KEY=<your-gemini-key>
export DATABRICKS_SERVER_HOSTNAME=<workspace-url>  # e.g., adb-123456.azuredatabricks.net
export DATABRICKS_HTTP_PATH=<warehouse-http-path>  # e.g., /sql/1.0/warehouses/abc123
export DATABRICKS_TOKEN=<pat-token>
```

To get `DATABRICKS_SERVER_HOSTNAME` and `HTTP_PATH`:
```bash
# From Databricks CLI
databricks config
# Shows current host and token

# For SQL warehouse HTTP_PATH:
# 1. Go to SQL Warehouses in UI
# 2. Select your warehouse
# 3. Click "Connection details"
# 4. Copy HTTP_PATH
```

- [ ] Gemini API key obtained
- [ ] Databricks workspace hostname noted
- [ ] SQL warehouse HTTP path noted
- [ ] Personal access token created (if needed)

---

## 🔐 AI Gateway Setup (Phase 2)

### 17. Configure AI Gateway (Optional)

When ready for real claim extraction:

1. Go to **Admin Console** → **Governance** → **AI Gateway**
2. Create new route:
   ```
   Route name: trust-claim-extractor
   Model: databricks-meta-llama-3-70b-instruct
   Rate limit: 100 req/min
   Usage tags: team=trust, stage=silver
   ```
3. Note the route name for notebooks

Update `03_silver_extraction.py`:
```python
ai_gateway_route = "trust-claim-extractor"  # ← Update this
```

- [ ] AI Gateway route created (optional for phase 1, required for phase 2)

---

## 📋 Final Verification

### 18. Run End-to-End Test

```python
# In Databricks notebook
CATALOG = "main"
SCHEMA = "trust_dev"

# Check all tables
bronze = spark.read.table(f"{CATALOG}.{SCHEMA}.raw_articles").count()
silver = spark.read.table(f"{CATALOG}.{SCHEMA}.claims").count()
gold = spark.read.table(f"{CATALOG}.{SCHEMA}.story_records").count()

print(f"✅ Bronze: {bronze} articles")
print(f"✅ Silver: {silver} claims")
print(f"✅ Gold: {gold} stories")
```

- [ ] All tables accessible and populated
- [ ] Row counts make sense

### 19. Query Gold Table (for agent integration)

```sql
SELECT 
  story_id,
  outlets_covering,
  size(source_article_ids) as num_articles
FROM main.trust_dev.story_records
LIMIT 5;
```

- [ ] Gold table queryable
- [ ] Data structure matches expectations

---

## 🎯 Configuration Summary Template

Copy this and fill in with your values:

```
=== DATABRICKS CONFIGURATION ===
Workspace URL: _______________
Catalog: _______________
Schema: _______________
Cluster: _______________
SQL Warehouse: _______________

=== API KEYS ===
NewsAPI: ✓ ☐ Added to secrets
Apify: ✓ ☐ Added to secrets
Gemini: ✓ ☐ Available locally

=== CREDENTIALS FOR AGENT ===
Server hostname: _______________
HTTP path: _______________
PAT token: ✓ ☐ Created

=== STATUS ===
Notebooks uploaded: ✓ ☐
Tables created: ✓ ☐
Pipeline runs: ✓ ☐
Gold table accessible: ✓ ☐
Agent can query: ✓ ☐
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---|---|
| "Secret not found" | Run: `databricks secrets create-scope --scope trust-secrets` |
| "Table not found" | Run notebook `01_setup.py` first |
| "Cluster not running" | Start cluster or create new one |
| "Workspace import failed" | Check path: `/Workspace/Trust/` must exist |
| "Permission denied" | Check IAM permissions in Databricks |
| "API rate limit" | Wait or reduce page_size in `02_bronze_ingestion.py` |

---

## ✅ Ready When You Have:

- [ ] Databricks workspace access
- [ ] Cluster or warehouse running
- [ ] All 6 notebooks uploaded
- [ ] Secrets configured (or ready to skip)
- [ ] Tables created (by running setup notebook)
- [ ] Bronze ingestion works
- [ ] Full orchestrator completes

**Then you're ready to deploy and run the pipeline!**
