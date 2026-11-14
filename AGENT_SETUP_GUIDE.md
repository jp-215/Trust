# Gemini Agent Setup Guide

This guide explains how to configure the external Gemini agent to query your Databricks gold table and synthesize truths.

---

## 📍 Prerequisites

Before running the agent, ensure:

1. ✅ Trust pipeline has run (bronze/silver/gold tables populated)
2. ✅ Gold table has story records: `SELECT COUNT(*) FROM {catalog}.{schema}.story_records`
3. ✅ You have a Google Gemini API key
4. ✅ Agent package is installed locally: `pip install -e ./agent`

---

## 🔑 Step 1: Get Databricks Credentials

The agent needs 3 pieces of information to connect to your Databricks workspace:

### A. Server Hostname

**Where to find it:**
1. Go to your Databricks workspace URL in browser
2. Copy the domain: `https://adb-123456789.azuredatabricks.net`
3. Extract the hostname: `adb-123456789.azuredatabricks.net`

Or via CLI:
```bash
databricks config
# Output shows: host = ...
```

**What it looks like:**
```
adb-123456789.azuredatabricks.net
or
abc-xyz.cloud.databricks.us
```

### B. SQL Warehouse HTTP Path

**Where to find it:**
1. In Databricks, go to **SQL** → **SQL Warehouses**
2. Click on your warehouse (e.g., `trust-warehouse`)
3. Click **Connection details** (or similar)
4. Copy the **HTTP Path**

**What it looks like:**
```
/sql/1.0/warehouses/0123456789abcdef
```

**Via CLI:**
```bash
databricks sql warehouses list
# Shows connection strings for each warehouse
```

### C. Personal Access Token (PAT)

**If you already have one:**
```bash
# Use your existing token
```

**If you need to create one:**
1. In Databricks, click your **User icon** (top right)
2. Click **Settings**
3. Go to **Personal access tokens**
4. Click **Generate new token**
5. Copy the token (you can only see it once!)

**What it looks like:**
```
dapi1234567890abcdefghijklmnopqrstuvwxyz
```

**Via CLI (if you already authenticated):**
```bash
# Your token is in ~/.databrickscfg
cat ~/.databrickscfg | grep token
```

---

## 🔐 Step 2: Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click **Get API key** (or **Create new API key**)
3. Select/create a project
4. Copy the API key

**What it looks like:**
```
AIzaSyABCDEfGHIjKLMnopQRSTuvwxyz1234567
```

---

## ⚙️ Step 3: Configure Environment

### Option A: Environment Variables (Recommended)

Create/edit your `.env` file in the agent folder:

```bash
cd agent
cp .env.example .env
```

Edit `agent/.env` and fill in:

```env
# Your Gemini API key
GEMINI_API_KEY=AIzaSyABCDEfGHIjKLMnopQRSTuvwxyz1234567

# Your Databricks workspace
DATABRICKS_SERVER_HOSTNAME=adb-123456789.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/0123456789abcdef
DATABRICKS_TOKEN=dapi1234567890abcdefghijklmnopqrstuvwxyz
```

### Option B: Shell Environment Variables

```bash
export GEMINI_API_KEY="AIzaSyABCDEfGHIjKLMnopQRSTuvwxyz1234567"
export DATABRICKS_SERVER_HOSTNAME="adb-123456789.azuredatabricks.net"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/0123456789abcdef"
export DATABRICKS_TOKEN="dapi1234567890abcdefghijklmnopqrstuvwxyz"
```

### Option C: Pass on Command Line

```bash
GEMINI_API_KEY="..." \
DATABRICKS_SERVER_HOSTNAME="..." \
DATABRICKS_HTTP_PATH="..." \
DATABRICKS_TOKEN="..." \
python -m trust_agent.cli --story-id unclustered
```

---

## ✅ Step 4: Verify Gold Table Access

Before running the agent, test that it can query your gold table:

```bash
cd agent
python3 << 'EOF'
from trust_agent.gold_client import GoldClient
import os

gold_client = GoldClient(
    server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
    http_path=os.environ["DATABRICKS_HTTP_PATH"],
    access_token=os.environ["DATABRICKS_TOKEN"],
)

# Test query
result = gold_client.query_gold_table("unclustered")
if result:
    print("✅ Gold table accessible!")
    print(f"Story ID: {result.get('story_id')}")
    print(f"Outlets: {result.get('outlets_covering')}")
else:
    print("❌ No story found with ID 'unclustered'")
    print("Run the pipeline first: 06_pipeline_orchestrator.py")
EOF
```

**Expected output if successful:**
```
✅ Gold table accessible!
Story ID: unclustered
Outlets: ['CNN', 'Fox News', 'ABC News', ...]
```

**If it fails:**
```
❌ No story found with ID 'unclustered'
```

This likely means the pipeline hasn't run yet. Go back and run:
1. `02_bronze_ingestion.py` (ingests articles)
2. `06_pipeline_orchestrator.py` (full pipeline) or manually run silver/gold

---

## 🤖 Step 5: Run the Agent

Once credentials are set and gold table is accessible:

```bash
cd agent
python -m trust_agent.cli --story-id unclustered
```

**What happens:**
1. Agent connects to Databricks
2. Queries the gold table for story `unclustered`
3. Calls Gemini to synthesize the story
4. Prints the synthesized truth

**Expected output:**
```
================================================================================
SYNTHESIZED TRUTH FOR STORY: unclustered
================================================================================

Based on aggregated coverage across CNN, Fox News, and ABC News:

The CEO of a major technology company announced their resignation following 
allegations of misconduct. While the outlets agree on the core fact of the 
departure, they differ in framing:

- CNN emphasizes the allegations and immediate board action
- Fox News describes it as a "strategic transition"
- ABC News questions the timing and independence of the decision

All three outlets expect an interim leadership appointment within the week.

================================================================================
```

---

## 🔄 Step 6: Write Synthesis Back (Optional)

To persist the agent's output back to Databricks:

1. Ensure `GoldClient.write_synthesis()` has your credentials
2. Uncomment this line in `agent/trust_agent/cli.py`:

```python
# TODO: Write synthesis back to gold.story_synthesis table
# gold_client.write_synthesis(args.story_id, synthesis, metadata={"model": "gemini-2.0-flash"})
```

Change to:

```python
# Write synthesis to gold.story_synthesis table
gold_client.write_synthesis(
    args.story_id, 
    synthesis, 
    metadata={
        "model": "gemini-2.0-flash",
        "timestamp": datetime.utcnow().isoformat(),
        "agent_version": "0.1.0"
    }
)
print(f"\n✅ Synthesis written to gold.story_synthesis")
```

Then run:

```bash
python -m trust_agent.cli --story-id unclustered
```

The agent will now:
1. Query gold table
2. Synthesize with Gemini
3. Write result to `gold.story_synthesis` table

Verify with:

```sql
SELECT story_id, synthesized_truth, synthesized_at 
FROM main.trust_dev.story_synthesis 
LIMIT 1;
```

---

## 🔍 Troubleshooting Agent Issues

### Issue: "Failed to query gold table"

**Causes & Solutions:**
```
1. Table doesn't exist
   → Run pipeline: 06_pipeline_orchestrator.py

2. Wrong catalog/schema
   → Check DATABRICKS_HTTP_PATH points to correct warehouse
   → Verify CATALOG and SCHEMA in notebooks

3. Credentials wrong
   → Verify credentials using test script above
   → Check token hasn't expired

4. Network issue
   → Ensure internet connectivity
   → Check firewall isn't blocking Databricks
```

### Issue: "GEMINI_API_KEY not set"

```bash
# Verify env var is set
echo $GEMINI_API_KEY

# If empty, set it:
export GEMINI_API_KEY="your-key-here"

# Or use .env file
cat agent/.env | grep GEMINI_API_KEY
```

### Issue: "Connection refused"

```
Cause: SQL warehouse not running
Solution: Start warehouse in Databricks UI
```

### Issue: "timeout waiting for Gemini"

```
Cause: Gemini API unreachable or slow
Solution: 
  - Check internet
  - Wait a moment
  - Try again
  - Check https://status.cloud.google.com for outages
```

### Issue: "Table not found" / "Access denied"

```
Cause: Your token doesn't have permission
Solution:
  - Verify token is valid: databricks config
  - Check token has SQL warehouse access
  - Create new token with appropriate permissions
```

---

## 📊 Example Usage Scenarios

### Scenario 1: Single Story Synthesis

```bash
python -m trust_agent.cli --story-id unclustered
```

### Scenario 2: Query Different Story ID

If pipeline created multiple stories:

```sql
-- Find story IDs
SELECT DISTINCT story_id FROM main.trust_dev.story_records;
```

Then run:

```bash
python -m trust_agent.cli --story-id "your-story-id-here"
```

### Scenario 3: Batch Synthesis (Loop)

```bash
# Run agent on all stories
for story_id in unclustered story-1 story-2; do
  echo "Processing $story_id..."
  python -m trust_agent.cli --story-id "$story_id"
  sleep 2
done
```

### Scenario 4: Integration with Web API

Once working, wrap the agent in a FastAPI/Flask endpoint:

```python
from fastapi import FastAPI
from trust_agent.agent import StorySynthesisAgent

app = FastAPI()

@app.get("/synthesize/{story_id}")
async def synthesize(story_id: str):
    agent = StorySynthesisAgent(api_key=os.environ["GEMINI_API_KEY"], gold_client=gold_client)
    synthesis = agent.run(story_id)
    return {"story_id": story_id, "synthesis": synthesis}
```

---

## ✨ Configuration Checklist

Copy and check off as you go:

```
☐ Databricks hostname found
☐ SQL warehouse HTTP path found  
☐ Personal access token created
☐ Gemini API key obtained
☐ agent/.env file filled in
☐ Tested gold table access (test script passed)
☐ Agent CLI runs: python -m trust_agent.cli --story-id unclustered
☐ Output shows synthesized narrative
☐ (Optional) Write-back enabled in cli.py
☐ Synthesis written to gold.story_synthesis table
```

---

## 📞 Support

If stuck:

1. Check the test script output above
2. Review error message carefully
3. Verify all env vars are set: `env | grep -i databricks`
4. Check Databricks UI that tables exist and have data
5. Review `agent/trust_agent/gold_client.py` to see exact query being run
6. Check `agent/trust_agent/agent.py` to see tool-calling logic

---

## 🎯 Next: Deploy as Service

Once working, you can:

1. **Run on schedule** (cron job, Airflow, etc.)
2. **Wrap as API** (FastAPI, Flask, etc.)
3. **Integrate with web UI** (query endpoint for story synthesis)
4. **Set up alerts** (email when synthesis completes)

See main `README.md` for phase 3+ roadmap.
