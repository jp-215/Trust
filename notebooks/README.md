# Trust Databricks Notebooks

Production-ready, plug-and-play notebooks for the Trust fact-checker pipeline on Databricks.

## What's Included

**6 self-contained notebooks:**

1. **01_setup.py** — Initialize schemas, define data models
2. **02_bronze_ingestion.py** — Ingest from Apify, NewsAPI, GDELT
3. **03_silver_extraction.py** — Extract claims (DLT format)
4. **04_gold_aggregation.py** — Aggregate stories (DLT format)
5. **05_gold_synthesis.py** — Create agent output table
6. **06_pipeline_orchestrator.py** — Master orchestration (run this one!)

## Quick Start

### Upload to Databricks

1. Create folder `/Workspace/Trust/`
2. Upload all 6 `.py` files
3. (Optional) Configure secrets:
   - Scope: `trust-secrets`
   - Keys: `newsapi-key`, `apify-token`

### Run the Pipeline

Open `06_pipeline_orchestrator.py` → Click **Run All**

Expected output:
```
📊 Pipeline Summary:
  Bronze (raw articles): 150 rows
  Silver (claims):       450 rows
  Gold (stories):        5 rows
```

**That's it!** Your pipeline runs end-to-end.

## For Production

See **DEPLOYMENT_GUIDE.md** for:
- Setting up scheduled jobs
- Configuring DLT pipelines
- Monitoring and troubleshooting
- Phase 2+ integration steps

## Features

✅ **Plug-and-play** — No code changes needed, just upload and run
✅ **Self-contained** — Each notebook is independent
✅ **Zero-credential verification** — Works without API keys (uses stubs)
✅ **Full real API support** — Swap stubs for real keys when ready
✅ **Modular phases** — Structured for incremental enhancement
✅ **Built-in monitoring** — Displays summaries and status

## Architecture

```
Ingestion (NewsAPI, GDELT, Apify)
    ↓
Bronze (raw_articles)
    ↓
Silver (claims) ← Extraction (stubbed, ready for AI Gateway)
    ↓
Gold (story_records) ← Aggregation (clustering stubbed)
    ↓
Gold Synthesis (agent output)
```

## Next: Gemini Agent

Once the pipeline populates the gold table, run the external agent:

```bash
cd ../agent
export GEMINI_API_KEY=your-key
export DATABRICKS_SERVER_HOSTNAME=workspace-url
export DATABRICKS_HTTP_PATH=warehouse-path
export DATABRICKS_TOKEN=token

python -m trust_agent.cli --story-id unclustered
```

## Troubleshooting

| Problem | Solution |
|---|---|
| Secret not found | Create scope `trust-secrets` in Databricks |
| No data ingested | Check API keys, network, rate limits |
| Slow extraction | Normal for stub; phase 2 optimizes with AI Gateway |
| Table errors | Run `01_setup.py` first, then others |

See **DEPLOYMENT_GUIDE.md** for more.

## Files

```
notebooks/
├── 01_setup.py                  # Setup
├── 02_bronze_ingestion.py       # Ingestion
├── 03_silver_extraction.py      # Claim extraction (DLT)
├── 04_gold_aggregation.py       # Story aggregation (DLT)
├── 05_gold_synthesis.py         # Synthesis table setup
├── 06_pipeline_orchestrator.py  # Master orchestrator ← RUN THIS
├── README.md                    # This file
└── DEPLOYMENT_GUIDE.md          # Production setup
```

## Support

- **Quick questions?** Check the comments in each notebook
- **Setup issues?** See DEPLOYMENT_GUIDE.md
- **Phase 2 planning?** See ../PHASE_1_SUMMARY.md
- **Architecture?** See ../README.md
