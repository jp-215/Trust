# Trust Frontend + Backend Integration Guide

Complete implementation guide for building and deploying the Trust fact-checker web application.

---

## 📁 Project Structure

```
Trust/
├── frontend/                          # Next.js React app
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── FactMatrix.tsx        # Fact detection matrix
│   │   │   ├── ChatPanel.tsx         # Gemini chat interface
│   │   │   ├── StoryCard.tsx         # Story display
│   │   │   └── Layout.tsx            # Main dashboard layout
│   │   ├── pages/
│   │   │   ├── index.tsx             # Home page
│   │   │   ├── story/[id].tsx        # Story detail page
│   │   │   └── api/                  # Next.js API routes (optional)
│   │   ├── hooks/
│   │   │   └── useStory.ts           # Story data hook
│   │   └── store/
│   │       └── storyStore.ts         # Zustand store
│   ├── public/                        # Static assets
│   └── tailwind.config.js
│
├── backend/                           # FastAPI Python app
│   ├── main.py                       # Main application
│   ├── requirements.txt
│   ├── .env.example
│   ├── models.py                     # Pydantic models
│   ├── db.py                         # Database utilities
│   ├── gemini_agent.py               # Gemini integration
│   └── config.py                     # Configuration
│
└── docker-compose.yml                # Local development
```

---

## 🚀 Setup Instructions

### Prerequisites

- Node.js 18+ (frontend)
- Python 3.10+ (backend)
- Docker (optional, for local Databricks)
- Databricks workspace access
- Google Gemini API key

### Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials:
# DATABRICKS_SERVER_HOSTNAME=dbc-913b22e4-dda6.cloud.databricks.com
# DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/33eaa1878956b7ed
# DATABRICKS_TOKEN=<REDACTED>
# GEMINI_API_KEY=AIzaSyABC...

# Run server
python main.py
# Server runs on http://localhost:8000
```

### Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Run development server
npm run dev
# App runs on http://localhost:3000
```

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Get Story
```bash
GET /story/{story_id}

Response:
{
  "story_id": "unclustered",
  "outlets_covering": ["CNN", "Fox News", "ABC News"],
  "num_articles": 46,
  "claim_matrix": [
    {
      "claim_text": "CEO resigned",
      "outlets_reporting": ["CNN", "ABC"],
      "outlets_silent": ["Fox"],
      "agreement_status": "STRONG"
    }
  ],
  "synthesized_truth": "The CEO announced resignation...",
  "confidence": 0.87
}
```

### Chat with Gemini
```bash
POST /chat

Request:
{
  "story_id": "unclustered",
  "question": "What is the consensus?"
}

Response:
{
  "answer": "Based on coverage from CNN, Fox News, and ABC News...",
  "citations": ["CNN", "Fox News", "ABC News"],
  "confidence": 0.87
}
```

### List Stories
```bash
GET /stories?limit=10
```

### Get Outlets
```bash
GET /outlets
```

### Search
```bash
POST /search
{
  "query": "CEO",
  "limit": 10
}
```

---

## 🎨 Frontend Components

### FactMatrix Component
Shows claim-outlet agreement matrix with color coding

```typescript
<FactMatrix 
  claims={claimsData}
  outlets={outletsList}
/>
```

### ChatPanel Component
Interactive chat interface with Gemini agent

```typescript
<ChatPanel 
  storyId="unclustered"
  apiBaseUrl="http://localhost:8000"
/>
```

### StoryCard Component
Display story with synthesis and metadata

```typescript
<StoryCard
  storyId="unclustered"
  outletsCovering={["CNN", "Fox", "ABC"]}
  numArticles={46}
  synthesizedTruth="The CEO announced resignation..."
  confidence={0.87}
/>
```

---

## 🔗 Data Flow

### Story Page Load
```
1. User visits: /story/unclustered
2. Frontend calls: GET /story/unclustered
3. Backend queries: workspace.trust_dev.story_records
4. Returns: Story data + synthesis (if exists)
5. Frontend renders: StoryCard + FactMatrix + ChatPanel
```

### Chat Interaction
```
1. User types: "What is the consensus?"
2. Frontend calls: POST /chat
3. Backend:
   - Queries: workspace.trust_dev.story_records
   - Extracts: outlets, claims, contradictions
   - Calls: Gemini with context
   - Returns: Synthesized answer + citations
4. Frontend displays: Message in ChatPanel with citations
```

---

## 🗄️ Database Schema (Unity Catalog)

### story_records Table
```sql
SELECT
  story_id,
  outlets_covering,      -- Array<String>
  claim_matrix,          -- Array<Struct>
  contradiction_pairs,   -- Array<Struct>
  source_article_ids,    -- Array<String>
  created_at,
  updated_at
FROM workspace.trust_dev.story_records
```

### story_synthesis Table
```sql
SELECT
  story_id,
  synthesized_truth,     -- String
  synthesis_metadata,    -- Map<String, String>
  synthesized_at
FROM workspace.trust_dev.story_synthesis
```

### raw_articles Table
```sql
SELECT
  article_id,
  outlet,
  title,
  raw_text,
  published_at,
  scraped_at,
  url
FROM workspace.trust_dev.raw_articles
```

---

## 🤖 Gemini Agent Integration

### Tool: query_gold_table
```python
def query_gold_table(story_id: str) -> dict:
    """
    Query Unity Catalog for story data
    Returns: claim_matrix, outlets, contradictions
    """
```

### Agent Flow
```
1. Receive user question
2. Query gold table via tool
3. Extract: claims, outlets, contradictions
4. Reason: Compare outlets, find consensus
5. Generate: Synthesized answer
6. Return: Answer + citations + confidence
```

### Custom Prompt
```
You are a fact-checking assistant analyzing news from multiple outlets.

Data available:
- claim_matrix: Which outlets reported which claims
- outlets_covering: [CNN, Fox News, ABC News, ...]
- contradictions: Where outlets disagree

User question: {question}

Provide clear answer:
1. State the consensus (if any)
2. List disagreements
3. Identify information gaps
4. Cite supporting outlets

Be neutral and evidence-based.
```

---

## 🔐 Authentication

### Option 1: No Auth (Development)
```
# .env
DATABRICKS_TOKEN=<your-pat-token>
GEMINI_API_KEY=<your-gemini-key>
```

### Option 2: OAuth2 (Production)
```python
# backend/auth.py
from fastapi.security import HTTPBearer, HTTPAuthCredential

security = HTTPBearer()

@app.get("/protected")
async def protected_route(credentials: HTTPAuthCredential = Depends(security)):
    # Verify token
    pass
```

### Option 3: API Key
```python
# backend/main.py
@app.get("/protected")
async def protected_route(api_key: str = Header(...)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
    pass
```

---

## 📊 Deployment

### Local Development
```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Visit: http://localhost:3000
```

### Docker Compose (Production-like)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
```

```bash
docker-compose up
```

### Cloud Deployment

**Backend (Google Cloud Run)**
```bash
gcloud run deploy trust-backend \
  --source backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DATABRICKS_TOKEN=..."
```

**Frontend (Vercel)**
```bash
npm install -g vercel
vercel --prod
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install pytest pytest-asyncio

pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

---

## 📈 Performance Optimization

### Database
- Index on `story_id` in `story_records`
- Cache Gemini responses
- Pagination for large result sets

### Frontend
- Lazy load components
- Cache API responses (SWR/React Query)
- Optimize bundle size (next/dynamic)

### Gemini Agent
- Reuse connection
- Batch queries when possible
- Cache similar queries

---

## 🐛 Troubleshooting

### Issue: "Table not found"
```
Solution: Verify workspace.trust_dev.story_records exists
Run pipeline first: 06_pipeline_orchestrator.py
```

### Issue: Gemini API errors
```
Solution: Check GEMINI_API_KEY in .env
Verify token has required scopes
```

### Issue: CORS errors
```
Solution: Backend CORS is enabled for all origins
In production, restrict to your frontend domain:
allow_origins=["https://yourdomain.com"]
```

### Issue: Databricks connection fails
```
Solution: Verify credentials:
- DATABRICKS_SERVER_HOSTNAME: dbc-...cloud.databricks.com
- DATABRICKS_HTTP_PATH: /sql/1.0/warehouses/...
- DATABRICKS_TOKEN: dapi...
```

---

## 📝 Environment Variables

### Backend (.env)
```
DATABRICKS_SERVER_HOSTNAME=<your-workspace>.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/<warehouse-id>
DATABRICKS_TOKEN=<your-pat-token>
GEMINI_API_KEY=<your-gemini-api-key>
ENVIRONMENT=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎯 Next Steps

1. **Backend Setup**: `cd backend && python main.py`
2. **Frontend Setup**: `cd frontend && npm run dev`
3. **Test API**: Visit `http://localhost:8000/docs` (Swagger UI)
4. **View App**: Visit `http://localhost:3000`
5. **Ask Questions**: Open a story and chat with Gemini

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review backend logs: `python main.py` output
3. Check frontend console: Browser DevTools
4. Verify credentials in .env files
5. Test Databricks connection: `databricks configure --token`

