# Trust — Quick Start Guide

## 1-Minute Setup

```bash
# Clone and enter the repo
cd Trust

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -e .
cd agent && pip install -e .
cd ..

# Copy env templates (optional, not needed for verification)
cp .env.example .env
cp agent/.env.example agent/.env
```

## Verify Everything Works (5 minutes, no credentials needed)

```bash
# Run bronze writer tests
python3 -m pytest tests/test_bronze_writer.py -v

# Run agent tests (mocked, no Gemini/Databricks needed)
cd agent
python3 -m pytest tests/test_agent_mocked.py -v
cd ..

# Both should pass ✅
```

## Understand the Architecture (2 minutes)

Read the first 200 lines of `README.md` — it explains the medallion architecture (bronze → silver → gold) and where stubs are.

## Load Sample Data (optional, 1 minute)

```bash
python3 scripts/seed_dev_data.py
```

This loads 3 fake articles about the same event into a local Delta table, showing what bronze ingestion looks like.

## Next: Real API Integration

When you're ready to ingest from real sources:

1. **Apify**: Set `APIFY_API_TOKEN` in `.env`, update actor ID in `run_ingestion.py`.
2. **NewsAPI**: Set `NEWSAPI_KEY` in `.env`.
3. **Gemini**: Set `GEMINI_API_KEY` in `agent/.env`.
4. **Databricks**: Set workspace credentials in `agent/.env` to query the gold table.

## Deploy to Databricks

Once you have a Databricks workspace:

```bash
# Set up workspace host and token
export DATABRICKS_HOST=<your-workspace-url>
export DATABRICKS_TOKEN=<your-pat>

# Deploy the DAB
databricks bundle deploy -t dev

# Run the ingestion job
databricks bundle run ingestion_job
```

## Files to Know

| File | Purpose |
|---|---|
| `src/trust/schemas/tables.py` | Single source of truth for data shapes |
| `src/trust/pipelines/silver.py`, `gold.py` | DLT pipeline definitions |
| `scripts/seed_dev_data.py` | Load test data without real APIs |
| `agent/trust_agent/agent.py` | Gemini tool-calling loop |
| `tests/`, `agent/tests/` | Run verification (zero creds needed) |

## Common Tasks

### Run a single test
```bash
python3 -m pytest tests/test_bronze_writer.py::TestBronzeWriter::test_normalize_apify_item -v
```

### Test the agent alone (mocked)
```bash
cd agent && python3 -m pytest tests/test_agent_mocked.py::TestStorySynthesisAgent::test_agent_tool_calling_loop -v
```

### Check which files are stubbed
```bash
grep -r "TODO:" src/ agent/ --include="*.py"
```

### Verify repo structure
```bash
find . -type f -name "*.py" | head -20  # See all Python files
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'trust'"**
```bash
pip install -e .  # from the repo root
```

**"No module named pytest"**
```bash
pip install pytest
```

**"pyspark.sql not found"**
- PySpark is a heavy dependency; tests that require it will fail on a non-Spark environment.
- For phase 1, the bronze writer tests (which don't use PySpark) should pass.
- Full pipeline tests require a Databricks workspace or local Spark cluster.

## What's Next?

See `PHASE_1_SUMMARY.md` for what's stubbed and phase 2 roadmap, or jump to the `README.md` "Next Steps" section.
