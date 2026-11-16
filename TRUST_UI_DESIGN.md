# Trust Fact-Checker UI/UX Design

## Overview
A modern, interactive web application that visualizes aggregated news coverage from the gold table, displays fact detection with outlet references, and provides a chat interface powered by Google Gemini for asking questions about stories.

---

## 1. Main Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRUST - FACT CHECKER                             │
│  Aggregated News Intelligence | Source of Truth Detection                   │
├──────────┬────────────────────────────────────────┬─────────────────────────┤
│          │                                        │                         │
│ SIDEBAR  │         MAIN CONTENT AREA              │   CHAT PANEL            │
│          │                                        │                         │
│ • Home   │  ┌─ STORY CARD ──────────────────┐   │  ┌─ GEMINI CHAT ─────┐  │
│          │  │                               │   │  │                   │  │
│ • Search │  │ Story: Nvidia CEO Steps Down │   │  │ Q: What happened? │  │
│          │  │ Date: 2026-11-14             │   │  │                   │  │
│ • Trends │  │ Status: ⚠️ CONFLICTING INFO  │   │  │ A: The CEO of...  │  │
│          │  │                               │   │  │                   │  │
│ • Recent │  │ FACT MATRIX:                  │   │  │ ─────────────────│  │
│          │  │ ┌─────────────────────────┐   │   │  │                   │  │
│ • Saved  │  │ │ CLAIM               │OUT│   │   │  │ [Type message...] │  │
│          │  │ │─────────────────────│───│   │   │  │                   │  │
│          │  │ │CEO resigned         │✓✓✓│   │   │  └───────────────────┘  │
│          │  │ │Allegations involved │✓✗✗│   │   │                         │
│          │  │ │Board action rapid   │✓✓✗│   │   │                         │
│          │  │ └─────────────────────┘   │   │   │                         │
│          │  │                               │   │                         │
│          │  │ OUTLET COVERAGE:              │   │                         │
│          │  │ • CNN (12 articles)  [═══════ │   │                         │
│          │  │ • Fox News (8)       [═════   │   │                         │
│          │  │ • ABC News (10)      [════════ │   │                         │
│          │  │                               │   │                         │
│          │  │ SOURCE OF TRUTH:              │   │                         │
│          │  │ "The CEO announced resignation│   │                         │
│          │  │  following allegations. Board │   │                         │
│          │  │  acted within days. Reports   │   │                         │
│          │  │  diverge on investigation..."│   │                         │
│          │  │ [Citations: CNN, Fox, ABC]    │   │                         │
│          │  │                               │   │                         │
│          │  │ 🔗 View Full References       │   │                         │
│          │  └─────────────────────────────┘   │                         │
│          │                                        │                         │
│          └────────────────────────────────────────┘                         │
│                                                                             │
└──────────┴────────────────────────────────────────┴─────────────────────────┘
```

---

## 2. Story Card Component (Expanded View)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🎯 STORY: Nvidia CEO Steps Down Following Allegations                       │
│ 📅 2026-11-14 | ⚠️ CONFLICTING INFORMATION DETECTED                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ FACT DETECTION MATRIX                                                       │
│ ─────────────────────────────────────────────────────────────────────────   │
│                                                                              │
│ Claim                          | CNN | Fox | ABC | AP | Reuters | Consensus│
│ ─────────────────────────────────────────────────────────────────────────  │
│ CEO announced resignation      │ ✓   │ ✓   │ ✓   │ ✓  │   ✓    │ STRONG  │
│ Allegations of misconduct      │ ✓   │ ✗   │ ✓   │ ✓  │   ✓    │ WEAK    │
│ Board action was immediate     │ ✓   │ ✓   │ ~   │ ✓  │   ✓    │ MEDIUM  │
│ Investigation ongoing          │ ✓   │ ✗   │ ✗   │ ✓  │   ~    │ WEAK    │
│ Interim CEO already named      │ ✗   │ ✗   │ ✗   │ ✗  │   ✗    │ FALSE   │
│                                                                              │
│ Legend: ✓ Reported | ✗ Contradicted | ~ Unclear/Pending | STRONG/WEAK/...  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTLET COVERAGE BREAKDOWN                                                   │
│                                                                              │
│ 📰 CNN News                    | 12 articles | Focus: Allegations & Timeline│
│    ├─ Article 1: "CEO Steps Down..." (Nov 14, 10:00 AM)                   │
│    ├─ Article 2: "Board meets urgently..." (Nov 14, 2:30 PM)              │
│    └─ Article 3: "What we know..." (Nov 14, 8:45 PM)                      │
│                                                                              │
│ 📰 Fox News                    | 8 articles  | Focus: Strategic Transition │
│    ├─ Article 1: "Leadership Change..." (Nov 14, 11:15 AM)                │
│    └─ Article 2: "Market reacts to news..." (Nov 14, 3:20 PM)             │
│                                                                              │
│ 📰 ABC News                    | 10 articles | Focus: Allegations & Impact  │
│    ├─ Article 1: "Nvidia CEO resigns..." (Nov 14, 10:30 AM)               │
│    └─ Article 2: "Shares tumble as..." (Nov 14, 1:45 PM)                  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ SOURCE OF TRUTH SYNTHESIS (Powered by Google Gemini)                        │
│                                                                              │
│ The CEO of Nvidia announced their resignation on November 14, 2026.        │
│ This decision follows allegations of misconduct, with multiple news outlets │
│ confirming the resignation but diverging on specific details:               │
│                                                                              │
│ AGREEMENTS ACROSS OUTLETS:                                                  │
│ • CEO resignation confirmed by all major outlets                           │
│ • Board took swift action                                                   │
│ • Market impact was immediate (stock decline)                              │
│                                                                              │
│ CONFLICTING REPORTS:                                                        │
│ • Nature of allegations: CNN/ABC emphasize misconduct; Fox downplays       │
│ • Investigation status: Some outlets report ongoing, others suggest closed  │
│ • Interim leadership: Only CNN confirms successor named; others unclear     │
│                                                                              │
│ OMISSIONS BY OUTLETS:                                                       │
│ • Fox News notably absent from reporting allegations details                │
│ • No outlet provides full timeline of investigation                        │
│ • Details on board deliberations largely unreported                        │
│                                                                              │
│ [Generated by Gemini @ 2026-11-15 00:15 UTC | Confidence: 87%]            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ QUICK ACTIONS                                                               │
│ [View Full Articles] [Compare Outlet Angles] [Export Report] [Share]       │
│ [Ask Follow-up Q] [Flag Inconsistency] [Save Story] [Add to Briefing]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Chat Interface Component

```
┌──────────────────────────────┐
│   TRUST GEMINI ASSISTANT     │
│   Ask about this story       │
├──────────────────────────────┤
│                              │
│ Q: Why did the CEO leave?    │
│ → CNN says allegations        │
│   Fox says strategic choice   │
│                              │
│ A: Based on aggregated news  │
│ data, the CEO's resignation  │
│ follows allegations of       │
│ misconduct (reported by CNN, │
│ ABC). However, Fox News      │
│ frames it as a "strategic    │
│ transition." This suggests   │
│ outlet bias or incomplete    │
│ information sharing.         │
│                              │
│ The most likely truth: CEO   │
│ resigned due to allegations, │
│ though full scope remains    │
│ unclear.                     │
│                              │
│ [Sources: CNN(3) Fox(1)      │
│  ABC(2) Reuters(1)]          │
│                              │
├──────────────────────────────┤
│                              │
│ Q: What do we not know?      │
│                              │
│ A: Several key gaps exist:   │
│ • Formal investigation       │
│   status/timeline            │
│ • Board meeting minutes      │
│ • Succession plan details    │
│ • Employee impact            │
│ • Shareholder response       │
│                              │
│ These gaps are notable       │
│ absences from mainstream     │
│ coverage.                    │
│                              │
├──────────────────────────────┤
│ [Type your question...]      │
│ [Send] [Clear] [Options]     │
└──────────────────────────────┘
```

---

## 4. Technical Architecture

### Frontend Stack
- **Framework**: React/Next.js
- **Styling**: Tailwind CSS + custom components
- **Real-time**: WebSocket for live updates
- **Charts**: Recharts/D3 for visualization
- **State**: Redux/Zustand for data management

### Backend Stack
- **API**: FastAPI/Flask
- **Database**: Unity Catalog (Databricks)
- **Query Engine**: Custom SQL builder for dynamic queries
- **Agent Integration**: Google Gemini SDK with custom tool definitions
- **Authentication**: OAuth2 with Databricks

### Data Flow

```
┌─────────────────────────┐
│  Frontend (React UI)    │
│  - Display gold data    │
│  - Show fact matrix     │
│  - Chat interface       │
└────────────┬────────────┘
             │ API calls
             ▼
┌─────────────────────────┐
│   Backend (FastAPI)     │
│  - Route handlers       │
│  - SQL query builder    │
│  - Gemini orchestrator  │
└────────────┬────────────┘
             │ SQL queries
             ▼
┌─────────────────────────┐
│ Unity Catalog Tables    │
│ - workspace.trust_dev.* │
│   • story_records       │
│   • raw_articles        │
│   • claims              │
│   • story_synthesis     │
└────────────┬────────────┘
             │ Response
             ▼
┌─────────────────────────┐
│  Gemini Agent           │
│  - Query tool (SQL)     │
│  - Reasoning loop       │
│  - Synthesis output     │
└─────────────────────────┘
```

---

## 5. Key UI Components

### Fact Matrix Component
```python
interface FactMatrix {
  claims: Claim[]
  outlets: Outlet[]
  agreementStatus: 'STRONG' | 'MEDIUM' | 'WEAK' | 'CONFLICTING'
  heatmap: boolean // Color-coded confidence
}

// Color coding:
// ✓ Green  - Outlet reports this claim
// ✗ Red    - Outlet contradicts this claim
// ~ Yellow - Outlet unclear/pending
// ○ Gray   - Outlet silent on this claim
```

### Story Card Component
```python
interface StoryCard {
  storyId: string
  title: string
  outlets: Outlet[]
  claimMatrix: FactMatrix
  synthesizedTruth: string
  synthesisMeta: SynthesisMeta
  sourceArticles: Article[]
  createdAt: datetime
}
```

### Chat Message Component
```python
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  confidence?: number
  geminiMetadata?: {
    model: string
    toolsCalled: string[]
    reasoning: string
  }
}
```

---

## 6. Workflow: User Asks a Question

```
1. User types: "What is the consensus?"
   │
   ├─→ Frontend sends to backend: { question, storyId }
   │
2. Backend receives request
   │
   ├─→ Build SQL query from question context
   │   (e.g., "SELECT * FROM story_records WHERE story_id = ?")
   │
3. Query Unity Catalog
   │
   ├─→ Retrieve: claims, outlets_covering, claim_matrix, contradiction_pairs
   │
4. Pass to Gemini Agent
   │
   ├─→ Tool: query_gold_table() [already called, now we have data]
   │
   ├─→ Prompt: "User asks: {question}. Here's the gold data: {data}"
   │
   ├─→ Gemini reasons over:
   │   • Outlet agreements
   │   • Contradiction patterns
   │   • Information gaps
   │   • Source reliability
   │
5. Gemini generates response
   │
   ├─→ "Based on {N} outlets reporting on {claim}..."
   │   "[Citations: CNN(3x), Fox(1x), ABC(2x)]"
   │
6. Backend enriches response
   │
   ├─→ Add visualization data
   │   Add source links
   │   Add follow-up suggestions
   │
7. Frontend displays
   │
   └─→ Render in chat with citations, links, and matrix highlighting
```

---

## 7. Feature Breakdown

### Core Features
- **Fact Matrix Visualization** - Color-coded claim/outlet agreements
- **Outlet Coverage Breakdown** - See which outlets reported what
- **Source of Truth Synthesis** - Gemini-generated consensus narrative
- **Chat Interface** - Ask follow-up questions about any story
- **Citation System** - Every claim links back to source articles
- **Conflict Detection** - Automatic flagging of contradictions

### Advanced Features
- **Bias Detection** - Highlight outlet editorial patterns
- **Information Gaps** - Show what's NOT being reported
- **Timeline View** - See how story evolved across outlets
- **Comparison Mode** - Compare how different outlets covered the same event
- **Custom Reports** - Generate briefings for specific aspects
- **Trending Analysis** - See which stories have the most conflicting info

### Integration with Gemini Agent
- **Custom Tools**: `query_gold_table()`, `get_article_details()`, `analyze_outlet_bias()`
- **Reasoning**: Multi-step reasoning over fact matrix before answering
- **Follow-ups**: Agent suggests clarifying questions based on detected gaps
- **Confidence**: Agent reports confidence level and uncertainty

---

## 8. SQL Query Tool (Gemini Integration)

```python
# Gemini can call this tool to query Unity Catalog

def query_gold_table(story_id: str, query_type: str) -> dict:
    """
    Available query_types:
    - 'claims': Get all claims for this story
    - 'outlet_coverage': Get outlet breakdown
    - 'contradictions': Get conflicting reports
    - 'synthesis': Get agent's synthesized truth
    """
    
    queries = {
        'claims': f"""
            SELECT claim_text, outlets_reporting, outlets_silent, agreement_status
            FROM workspace.trust_dev.story_records
            WHERE story_id = '{story_id}'
        """,
        
        'outlet_coverage': f"""
            SELECT outlet, COUNT(*) as articles, 
                   COLLECT_LIST(article_id) as article_ids
            FROM workspace.trust_dev.raw_articles
            WHERE story_id = '{story_id}'
            GROUP BY outlet
        """,
        
        'synthesis': f"""
            SELECT synthesized_truth, synthesis_metadata
            FROM workspace.trust_dev.story_synthesis
            WHERE story_id = '{story_id}'
        """
    }
    
    return execute_query(queries[query_type])
```

---

## 9. Implementation Roadmap

### Phase 1 (MVP)
- [ ] Story display with fact matrix
- [ ] Basic Gemini chat
- [ ] SQL query integration
- [ ] Mobile responsive design

### Phase 2
- [ ] Advanced filtering & search
- [ ] Timeline view
- [ ] Bias detection
- [ ] Custom reports

### Phase 3
- [ ] Real-time updates
- [ ] User annotations
- [ ] AI-powered summarization
- [ ] API for third-party integrations

---

## 10. Sample Interactions

### Interaction 1: Fact-Checking
```
User: "Is the CEO definitely resigning?"

Agent: "Strong consensus (5/5 outlets confirm):
- CNN: ✓ "CEO steps down"
- Fox: ✓ "Leadership transition"  
- ABC: ✓ "CEO resigns"
- Reuters: ✓ "Departure announced"
- AP: ✓ "CEO leaves post"

Confidence: 98% - This is a solid fact."
```

### Interaction 2: Detecting Bias
```
User: "What's the difference in how outlets framed this?"

Agent: "Notable framing divergence:

ALLEGATIONS-FOCUSED (CNN, ABC):
- Emphasis on misconduct allegations
- Investigation narrative

NEUTRAL/STRATEGIC (Fox News, Reuters):
- Frame as 'strategic transition'
- Market focus

This suggests Fox News downplayed severity
compared to CNN/ABC coverage."
```

### Interaction 3: Finding Gaps
```
User: "What don't we know?"

Agent: "Key information gaps:

NOT REPORTED BY ANY OUTLET:
- Board meeting details/timeline
- Investigation scope definition
- Successor name/plans
- Employee communications
- Shareholder votes

This suggests mainstream news hasn't
obtained full details or chooses not to report."
```

---

## 11. Color Scheme

```
Primary Actions: Blue (#0066CC)
Success/Agreement: Green (#22C55E)
Conflict/Warning: Red (#EF4444)
Uncertain/Pending: Yellow (#EAB308)
Silent/Omission: Gray (#9CA3AF)
Background: Light (#F9FAFB) / Dark (#111827)
Text: Dark (#1F2937) / Light (#F3F4F6)
```

---

## 12. Responsive Design

- **Desktop** (1200px+): 3-column (sidebar + content + chat)
- **Tablet** (768px-1199px): 2-column (sidebar toggles, chat slides)
- **Mobile** (< 768px): 1-column (vertical stack, chat as modal)

