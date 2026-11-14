# Trust — Fact-Checker: Ingestion + Comparison Engine

A system to aggregate news coverage of the same real-world event across multiple outlets and press releases, extract discrete claims, compare them, and synthesize a "source of truth" story record.

## Architecture Overview

This project follows a **medallion architecture** on Databricks:

- **Bronze**: Raw articles ingested from Apify, NewsAPI, GDELT, and press releases.
- **Silver**: Discrete claims extracted from articles using Databricks AI Gateway (stubbed in phase 1).
- **Gold**: Aggregated story records with outlet coverage matrices, contradictions, and claimed facts.
- **Synthesis**: A Gemini-based agent that queries the gold table and produces synthesized narratives.

## Project Structure

```
Trust/
├── src/                          # Databricks Asset Bundle (DAB) project
│   ├── trust/
│   │   ├── ingestion/           # Data ingestion: Apify, NewsAPI, GDELT sources
│   │   ├── pipelines/           # DLT pipeline definitions (silver, gold)
│   │   └── schemas/             # Shared PySpark StructType definitions
│   └── jobs/
│       └── run_ingestion.py     # Workflow job entrypoint
├── agent/                        # Standalone Gemini agent package
│   ├── trust_agent/
│   │   ├── agent.py             # Real tool-calling loop for Gemini
│   │   ├── gold_client.py       # Databricks SQL queries
│   │   ├── cli.py               # CLI entrypoint
│   │   └── tools.py             # Tool schema + dispatch
│   └── tests/
│       └── test_agent_mocked.py # Mocked agent tests (no credentials needed)
├── resources/                    # Databricks workflow/pipeline YAML
├── scripts/                      # Helper scripts
│   └── seed_dev_data.py         # Load fixtures into bronze
├── tests/                        # Pipeline unit tests
└── databricks.yml               # DAB root config
```

## Setup

### Prerequisites

- Python 3.10+
- Databricks workspace (for phase 2 deployment)
- Apify account (optional, for real scraping)
- Google Gemini API key (for agent phase)
- NewsAPI key (optional)

### Local Development

1. Clone the repo and install dependencies:

```bash
cd Trust
pip install -e .
```

2. Copy environment templates:

```bash
cp .env.example .env
cp agent/.env.example agent/.env
```

3. Install the agent package separately:

```bash
cd agent
pip install -e .
```

## Verification (Phase 1 — No Credentials Required)

### Step 1: Test Bronze Writer

```bash
python -m pytest tests/test_bronze_writer.py -v
```

This tests the data normalization layer (Apify, NewsAPI, GDELT) that ingests raw articles into the bronze schema.

### Step 2: Seed Dev Data

```bash
python scripts/seed_dev_data.py
```

This loads the sample articles from `tests/fixtures/sample_articles.json` directly into a local Delta table (simulating bronze layer), bypassing any real API calls.

### Step 3: Test DLT Pipeline (Silver)

```bash
python -m pytest tests/test_silver_claims_stub.py -v
```

This tests the stubbed claim extraction: verifying that articles are read and placeholder claims are generated.

### Step 4: Test Agent (Mocked)

```bash
cd agent
python -m pytest tests/test_agent_mocked.py -v
```

This runs the Gemini agent's tool-calling loop against a fake gold client (no network, no Gemini API key needed). Confirms the function-call → dispatch → function-response → final-text loop works.

## Next Steps (Phase 2+)

### Real Apify Integration

Uncomment the Apify actor calls in `src/jobs/run_ingestion.py` and provide a real `APIFY_API_TOKEN`.

### AI Gateway Integration

1. In your Databricks workspace, go to **Admin > Governance > AI Gateway**.
2. Create a new route:
   - Name: `trust-claim-extractor`
   - Model: Any Databricks foundation model (e.g., Llama 3 70B Instruct)
3. Replace the stub in `src/trust/pipelines/ai_gateway_client.py` with a real API call.

### Real Gemini Synthesis

1. Provide a `GEMINI_API_KEY`.
2. Configure Databricks SQL connection details in `agent/.env`.
3. Run `python -m trust_agent.cli --story-id <story-id>` against a populated gold table.

## Configuration

### Databricks AI Gateway

Edit `resources/ai_gateway.yml` to configure the extraction model route. This is currently documented but not auto-created via DAB (AI Gateway routes are a manual/Terraform step).

### Secrets

On Databricks:
- Create a secret scope: `databricks secrets create-scope --scope trust-secrets`
- Add secrets:
  ```bash
  databricks secrets put --scope trust-secrets --key apify-token --string-value <token>
  databricks secrets put --scope trust-secrets --key newsapi-key --string-value <key>
  ```

### Local Testing

Copy `.env.example` to `.env` and fill in your keys (only needed if you want to test real APIs locally).

## Running the Pipeline

### Databricks Deployment (Phase 2)

```bash
databricks bundle deploy -t dev
databricks bundle run ingestion_job
```

This runs the ingestion job (which writes to bronze) and triggers the DLT pipeline (silver/gold).

### Local Testing

Use the seed script and unit tests for now. Real Databricks deployment requires a configured workspace.

## Architecture Decisions

1. **Ingestion job writes bronze directly** (not DLT Autoloader) for simplicity in phase 1.
2. **Gold table is DLT-managed, read-only** for this phase; the agent writes to a separate `gold.story_synthesis` table to keep write paths isolated.
3. **Extraction and clustering logic are stubbed** with clear TODOs so the pipeline runs end-to-end immediately, with real ML logic plugged in later.
4. **Agent is a standalone package** with its own dependencies (Gemini SDK, Databricks SQL connector) — deliberately separate from the Spark runtime to allow independent deployment and iteration.

## Known Limitations (Phase 1)

- Claim extraction is a stub (first 120 chars of article text as placeholder).
- Story clustering is naive (treats each article as its own story).
- Contradiction detection is not implemented (empty contradiction_pairs).
- No real API calls to Apify, NewsAPI, GDELT, or Gemini are made during verification.

These are intentionally stubbed and marked with TODO comments so phase 2 can fill them in without architectural rework.
