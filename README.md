# 🚀 Startup Analyzer - "X for Y" AI Multi-Agent System

**An intelligent multi-agent system that analyzes "X for Y" business ideas with comprehensive observability.**

Powered by GPT-4o via OpenRouter, this system uses 4 specialized AI agents orchestrated through LangGraph to provide deep, coordinated analysis of startup ideas like "Uber for Dog Walkers" or "Airbnb for Office Spaces."

**Live Demo**: [https://x4y.wildnode.io](https://x4y.wildnode.io)

---

## 🎯 What It Does

Input a business idea in the format "**X for Y**" (e.g., "Uber for Dog Walkers") and get:

- **Brand DNA Analysis** - What makes the X brand successful?
- **Market Research** - How saturated is the Y market?
- **Risk Assessment** - What could go wrong?
- **GTM Strategy** - How should you launch this?
- **Viability Score** - Is this idea worth pursuing? (0-100%)

All with **real-time observability** showing exactly how agents think, coordinate, and make decisions.

---

## ✨ Key Features

### 🤖 Multi-Agent Intelligence
- **4 Specialized Agents** working in parallel with dynamic coordination
- **Intelligent research loops** - agents request follow-up research when gaps are identified
- **Context-aware analysis** - each agent adapts based on business model type

### ⚡ Performance Optimized
- **Parallel execution** - 3 agents run concurrently (saves 15-20s)
- **Fast classification** - GPT-4o-mini for simple tasks (saves 2-3s)
- **Dynamic coordination** - only loop when necessary

### 📊 Production-Grade Observability
- **LangSmith tracing** - Visual exploration of every LLM call
- **Structured logging** - JSON logs with correlation IDs
- **Token & cost tracking** - Per-agent usage and aggregated costs
- **Real-time SSE streaming** - Live updates in the frontend
- **Debug panel** - On-screen console for tablet/mobile debugging

### 🎨 Modern Frontend
- **React + Vite** - Fast, responsive UI
- **Real-time progress** - SSE streaming with agent status updates
- **Rich results display** - Expandable sections with severity badges
- **Error boundaries** - Graceful error handling
- **Mobile-friendly** - Debug panel accessible on tablets

---

## 🤖 The Multi-Agent System

### Architecture Overview

```
User Input: "Uber for Dog Walkers"
         ↓
┌─────────────────────────────────────────┐
│    PHASE 1: Parallel Analysis (⚡15s)   │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌────────┐ │
│  │ Analyst │  │Researcher│  │  Risk  │ │
│  │         │  │          │  │Analyst │ │
│  └─────────┘  └──────────┘  └────────┘ │
│      ↓             ↓             ↓      │
└──────┬─────────────┬─────────────┬──────┘
       └─────────────┴─────────────┘
                     ↓
┌─────────────────────────────────────────┐
│   PHASE 2: Strategist Coordination      │
├─────────────────────────────────────────┤
│  • Reviews all agent outputs            │
│  • Identifies knowledge gaps            │
│  • Requests targeted follow-up research │
│    OR proceeds to final synthesis       │
└─────────────────────────────────────────┘
         ↓ (loop if needed)     ↓ (ready)
         ←───────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│      PHASE 3: Final Synthesis           │
├─────────────────────────────────────────┤
│  Strategist creates comprehensive       │
│  GTM plan with viability score          │
└─────────────────────────────────────────┘
```

---

### 1. 🔍 Analyst Agent (Brand DNA Specialist)

**Role**: Deconstructs the "X" brand to extract core strengths

**Capabilities**:
- Extracts brand DNA: core strengths, business model, differentiators
- Identifies success factors and competitive advantages
- Adapts research focus based on coordination feedback
- Provides confidence score for analysis

**Tools**:
- **Tavily Search** - AI-optimized web search
  - Basic mode: 5 results
  - Focused mode: 7 results with advanced depth

**Example Output**:
```json
{
  "core_strengths": [
    "On-demand marketplace platform",
    "Real-time GPS tracking",
    "Dynamic pricing algorithm",
    "Trust & safety systems"
  ],
  "business_model": "Two-sided marketplace connecting riders with drivers...",
  "key_differentiators": [
    "First-mover advantage in ridesharing",
    "Network effects and scale",
    "Superior user experience"
  ],
  "confidence": 0.87
}
```

---

### 2. 📊 Researcher Agent (Market Intelligence)

**Role**: Investigates the "Y" market for competition and opportunity

**Capabilities**:
- Assesses market saturation (low/medium/high)
- Identifies competitors and counts them
- Discovers market opportunities and barriers
- **Parallel search optimization** - runs 2 searches concurrently

**Tools**:
- **Tavily Search** (2 parallel queries)
  - Market search: size, trends, landscape
  - Competitor search: companies, apps, services

**Example Output**:
```json
{
  "market_name": "Dog Walking Services",
  "market_size": "$1.2B annually in US",
  "saturation_level": "high",
  "competitors": ["Rover", "Wag", "PetBacker", "Care.com"],
  "competitor_count": 15,
  "opportunities": [
    "Premium certified trainer segment underserved",
    "Corporate dog walking programs"
  ],
  "barriers": [
    "Trust and insurance requirements",
    "Local regulations and licensing",
    "Established incumbents with network effects"
  ]
}
```

---

### 3. ⚠️ Risk Analyst Agent (Critical Thinker)

**Role**: Identifies threats, risks, and potential failure modes

**Capabilities**:
- **Business model classification** - Categorizes idea (marketplace, SaaS, ecommerce, etc.)
- **Context-aware RAG lookup** - Queries relevant risk frameworks
- Analyzes competitive threats, market risks, execution challenges
- Identifies financial risks and fatal flaws
- Provides realistic overall risk assessment

**Tools**:
- **GPT-4o-mini classifier** - Fast business model categorization (saves 2-3s)
- **Marketing RAG** - Semantic search over frameworks
  - FAISS vector store with curated knowledge base
  - Context-aware queries per model type
  - Examples: "marketplace cold start", "SaaS churn risks"

**Example Output**:
```json
{
  "competitive_threats": [
    {
      "threat": "Rover controls 70% market share with 2M users",
      "severity": "high",
      "mitigation": "Target premium segment Rover underserves"
    }
  ],
  "market_risks": [
    {
      "risk": "Highly saturated market with low switching costs",
      "probability": "high",
      "impact": "Difficult customer acquisition and retention"
    }
  ],
  "execution_challenges": [
    {
      "challenge": "Building walker supply in new cities",
      "difficulty": "high"
    }
  ],
  "financial_risks": [
    {
      "risk": "High customer acquisition costs ($50-100)",
      "concern_level": "high"
    }
  ],
  "fatal_flaws": [
    "No clear differentiation from incumbents"
  ],
  "overall_risk_level": "high",
  "summary": "Market highly saturated with strong incumbents...",
  "confidence": 0.82
}
```

---

### 4. 🎯 Strategist Agent (GTM Expert)

**Role**: Synthesizes all insights into actionable go-to-market strategy

**Capabilities**:
- **Coordination mode** - Reviews research, identifies gaps, requests follow-up
- **Synthesis mode** - Creates comprehensive GTM plan
- Assigns viability score (0-100%)
- Provides realistic, risk-aware strategy

**Coordination Loop Logic**:
```python
if knowledge_gaps_exist:
    request_targeted_research()  # Loop back (max 3 iterations)
else:
    create_final_gtm_plan()
```

**Example Output**:
```json
{
  "target_audience": "Affluent urban professionals with high-value dogs",
  "value_proposition": "Certified trainers, not just walkers",
  "pricing_strategy": "Premium tier at $50/walk vs $25 industry average",
  "distribution_channels": [
    "Instagram influencer partnerships",
    "Veterinary clinic referrals",
    "Premium pet boutique partnerships"
  ],
  "marketing_hooks": [
    "Your dog deserves a trainer, not just a walker",
    "Rover gets you a walk. We get you better behavior.",
    "Premium dogs deserve premium care"
  ],
  "competitive_advantages": [
    "Walker certification program",
    "Behavioral training focus",
    "Premium service positioning"
  ],
  "key_risks": [
    "Higher CAC due to premium positioning",
    "Limited addressable market"
  ],
  "success_metrics": [
    "Customer LTV > $2000",
    "Net Promoter Score > 70",
    "Walker retention > 80%"
  ],
  "timeline": "6-month pilot in SF, 12-month expansion to 5 cities",
  "viability_score": 68
}
```

**Viability Score Guidelines**:
- **80-100%**: Highly viable (low competition, clear differentiation)
- **60-79%**: Viable (moderate competition, good fit)
- **40-59%**: Moderate (high competition OR uncertain demand)
- **0-39%**: Low viability (fatal flaws, saturated market)

---

## 🛠️ Tools & Integrations

### Tavily Search
- **AI-optimized web search** designed for LLM consumption
- Returns high-quality, relevant content snippets
- Supports basic/advanced search depth
- Used by: Analyst, Researcher
- **Optimization**: Parallel searches save 5-8s

### Marketing RAG (Retrieval Augmented Generation)
- **Semantic search** over curated marketing knowledge base
- FAISS vector store with OpenAI embeddings
- Context-aware queries based on business model
- Contains: startup failure patterns, pitfalls, frameworks
- Used by: Risk Analyst

### LLM Providers
- **Primary**: GPT-4o via OpenRouter (all agents)
- **Classification**: GPT-4o-mini for fast categorization
- Automatic LangSmith tracing
- Temperature: 0.7 (balanced creativity/consistency)

---

## 📊 Comprehensive Observability

### 1. LangSmith Tracing

**Visual trace exploration** of every LLM call:

- **Hierarchical traces** - See parent workflow → agent calls → tool executions
- **Token tracking** - Input/output tokens per call
- **Latency metrics** - Duration of each operation
- **Error tracking** - Failed calls with stack traces
- **Prompt inspection** - View exact prompts and responses

**Access**: Set `LANGSMITH_API_KEY` and view traces at [smith.langchain.com](https://smith.langchain.com)

### 2. Structured Logging

**JSON logs with rich context**:

```json
{
  "timestamp": "2024-01-02T10:30:45.123Z",
  "level": "INFO",
  "event": "analyst_completed",
  "correlation_id": "CID-abc123",
  "analysis_id": "AID-xyz789",
  "brand": "Uber",
  "confidence": 0.87,
  "iteration": 0,
  "duration_ms": 3456
}
```

**Log Events Tracked**:
- `workflow_started` / `workflow_completed`
- `agent_started` / `agent_completed`
- `tool_called` / `tool_completed`
- `llm_request_started` / `llm_request_completed`
- `coordination_decision` / `synthesis_started`
- `error_occurred`

**Query logs**:
```bash
# Filter by agent
grep "analyst_completed" logs/app.log

# Filter by correlation ID
grep "CID-abc123" logs/app.log

# Track a specific analysis
grep "AID-xyz789" logs/app.log
```

### 3. Token & Cost Tracking

**Per-agent token usage**:

```python
{
  "metadata": {
    "token_usage": {
      "analyst": {
        "prompt_tokens": 1234,
        "completion_tokens": 567,
        "total_tokens": 1801
      },
      "researcher": {
        "prompt_tokens": 1456,
        "completion_tokens": 678,
        "total_tokens": 2134
      },
      "risk_analyst": {
        "classification_prompt_tokens": 45,
        "classification_completion_tokens": 12,
        "analysis_prompt_tokens": 1567,
        "analysis_completion_tokens": 789,
        "total_tokens": 2413
      },
      "strategist": {
        "prompt_tokens": 2345,
        "completion_tokens": 1234,
        "total_tokens": 3579
      }
    },
    "cost_usd": 0.0494
  }
}
```

**Cost Calculation**:
- Input: `total_prompt_tokens / 1_000_000 * $2.50`
- Output: `total_completion_tokens / 1_000_000 * $10.00`
- **GPT-4o pricing**: $2.50/MTok input, $10.00/MTok output

**Typical Analysis Cost**: $0.04 - $0.08

### 4. Real-Time SSE Streaming

**Server-Sent Events** provide live updates to the frontend:

```
event: agent_started
data: {"agent": "analyst", "status": "running"}

event: tool_called
data: {"tool": "tavily_search", "query": "Uber business model"}

event: agent_progress
data: {"agent": "analyst", "message": "Analyzing brand DNA..."}

event: agent_completed
data: {"agent": "analyst", "confidence": 0.87}

event: coordination_decision
data: {"action": "request_followup", "reason": "Need pricing data"}

event: analysis_completed
data: {"viability_score": 68, "total_duration": 48.3}
```

### 5. Frontend Debug Panel

**On-screen debugging** for tablets and mobile:

- **Console interceptor** - Captures all console.log/error/warn
- **Result inspector** - View raw JSON responses
- **SSE event log** - Track all server events
- **Connection status** - Monitor SSE connection
- **Error boundary** - Catch and display React crashes

**Access**: Click "🐛 Debug Panel" button (bottom-right)

### 6. Metrics Dashboard

**Key metrics tracked**:

- `analysis_duration_seconds` - Total analysis time
- `coordination_iterations` - Number of research loops
- `tool_call_count` - Tavily and RAG usage
- `llm_tokens_total` - Token consumption
- `llm_cost_usd` - Estimated API costs
- `viability_score_distribution` - Score histogram
- `agent_completion_rate` - Success rate per agent

**Frontend displays**:
- Duration with breakdown (minutes/seconds)
- Cost in USD with 4 decimal precision
- Token usage with K/M suffixes
- Token breakdown (input/output/total)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- OpenRouter API key
- Tavily API key
- (Optional) LangSmith API key

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/startup-analyzer.git
cd startup-analyzer

# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configure Environment

Create `.env` file:

```bash
# Required: LLM Provider
OPENROUTER_API_KEY=your_openrouter_key
LLM_MODEL=openai/gpt-4o

# Required: Search
TAVILY_API_KEY=your_tavily_key

# Optional: Observability
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=startup-analyzer
LANGCHAIN_TRACING_V2=true

# Settings
LOG_LEVEL=INFO
APP_ENV=development
```

### 3. Build RAG Knowledge Base

```bash
# Create directories
mkdir -p data/knowledge_base data/vector_store

# Add your marketing documents (.txt files) to data/knowledge_base/

# Build vector store
python scripts/build_vector_store.py
```

**Expected output**:
```
✅ Vector store built successfully!
   - Documents: 4
   - Chunks: 48
   - Location: data/vector_store
```

### 4. Start Backend

```bash
# Development
python -m src.api.main

# Production
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**API available at**: http://localhost:8000

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

**Frontend available at**: http://localhost:5173

### 6. Analyze Your First Idea

**Via UI**: Open http://localhost:5173 and enter:
- X Brand: `Uber`
- Y Market: `Dog Walkers`

**Via API**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "x_brand": "Uber",
    "y_market": "Dog Walkers",
    "description": "On-demand certified dog trainers"
  }'
```

---

## 📁 Project Structure

```
startup-analyzer/
├── frontend/                 # React + Vite UI
│   ├── src/
│   │   ├── components/      # UI components
│   │   │   ├── AnalysisForm.jsx
│   │   │   ├── ProgressDisplay.jsx
│   │   │   ├── MetricsDashboard.jsx
│   │   │   ├── ResultsDisplay.jsx
│   │   │   ├── DebugPanel.jsx
│   │   │   └── ErrorBoundary.jsx
│   │   ├── hooks/
│   │   │   └── useSSE.js    # SSE streaming hook
│   │   └── styles/
│   └── package.json
│
├── src/
│   ├── agents/              # Multi-agent system
│   │   ├── analyst.py       # Brand DNA analysis
│   │   ├── researcher.py    # Market research
│   │   ├── risk_analyst.py  # Risk assessment
│   │   ├── strategist.py    # GTM strategy
│   │   ├── base.py          # Base agent class
│   │   └── prompts/         # System prompts
│   │
│   ├── orchestration/       # LangGraph workflow
│   │   ├── graph.py         # Workflow definition
│   │   ├── nodes.py         # Node implementations
│   │   ├── edges.py         # Routing logic
│   │   └── state.py         # State management
│   │
│   ├── tools/               # External integrations
│   │   ├── tavily.py        # Web search tool
│   │   ├── marketing_rag.py # RAG knowledge base
│   │   ├── base.py          # Base tool class
│   │   └── registry.py      # Tool registry
│   │
│   ├── llm/                 # LLM client
│   │   ├── openrouter_client.py
│   │   └── token_counter.py
│   │
│   ├── observability/       # Full observability stack
│   │   ├── logger.py        # Structured JSON logging
│   │   ├── tracer.py        # OpenTelemetry tracing
│   │   ├── metrics.py       # Prometheus metrics
│   │   └── decorators.py    # @trace_agent, @trace_tool
│   │
│   ├── api/                 # FastAPI backend
│   │   ├── main.py          # Application entry
│   │   ├── routes/          # API endpoints
│   │   │   └── analysis.py  # /analyze, /analyze/stream
│   │   └── models/          # Pydantic models
│   │
│   └── utils/               # Utilities
│       └── errors.py        # Custom exceptions
│
├── data/
│   ├── knowledge_base/      # 📄 Marketing documents (.txt)
│   └── vector_store/        # FAISS index (auto-generated)
│
├── config/
│   └── settings.py          # Environment configuration
│
├── scripts/
│   └── build_vector_store.py
│
├── tests/
│   ├── agents/
│   ├── tools/
│   └── evaluation/
│
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🔧 API Reference

### POST /api/analyze

**Synchronous analysis** (waits for completion):

```json
POST /api/analyze
Content-Type: application/json

{
  "x_brand": "Uber",
  "y_market": "Dog Walkers",
  "description": "Optional context"
}
```

**Response**:
```json
{
  "analysis_id": "AID-abc123",
  "business_idea": {
    "full_idea": "Uber for Dog Walkers",
    "x_brand": "Uber",
    "y_market": "Dog Walkers"
  },
  "analyst_insights": { ... },
  "researcher_findings": { ... },
  "risk_analysis": { ... },
  "strategist_plan": {
    "viability_score": 68,
    ...
  },
  "metadata": {
    "total_duration_seconds": 48.3,
    "cost_usd": 0.0494,
    "token_usage": { ... }
  },
  "langsmith_trace_url": "https://smith.langchain.com/..."
}
```

### GET /api/analyze/stream

**Real-time SSE streaming** (recommended):

```
GET /api/analyze/stream?x_brand=Uber&y_market=Dog%20Walkers
Accept: text/event-stream
```

**SSE Events**:
```
event: agent_started
data: {"agent": "analyst"}

event: agent_completed
data: {"agent": "analyst", "result": {...}}

event: coordination_decision
data: {"action": "proceed_to_synthesis"}

event: complete
data: {"viability_score": 68, "metadata": {...}}
```

### GET /health

Health check endpoint:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "langsmith_enabled": true
}
```

---

## 🧪 Testing & Evaluation

### Run Tests

```bash
# All tests
pytest

# Specific module
pytest tests/agents/test_analyst.py

# With coverage
pytest --cov=src tests/
```

### Evaluation Datasets

Located in `tests/evaluation/datasets/`:

- `test_ideas.json` - Curated test cases
- `edge_cases.json` - Challenging scenarios
- `expected_outputs.json` - Ground truth

### Run Evaluation

```bash
python -m pytest tests/evaluation/ -v
```

---

## 🚢 Deployment

### Railway (Recommended)

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
```

2. **Login & Deploy**:
```bash
railway login
railway init
railway up
```

3. **Set Environment Variables** in Railway dashboard:
   - `OPENROUTER_API_KEY`
   - `TAVILY_API_KEY`
   - `LANGSMITH_API_KEY` (optional)

4. **Frontend Deployment**:
   - Build: `cd frontend && npm run build`
   - Deploy `dist/` to Vercel/Netlify
   - Set `VITE_API_URL` to Railway backend URL

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for details.

---

## 🐛 Troubleshooting

### "Vector store not initialized"
```bash
# Build vector store
python scripts/build_vector_store.py

# Verify documents exist
ls data/knowledge_base/
```

### "OPENROUTER_API_KEY not set"
```bash
# Add to .env
echo "OPENROUTER_API_KEY=your_key" >> .env

# Restart app
```

### Frontend shows blank page
- Check browser console for errors
- Open Debug Panel (🐛 button bottom-right)
- Check ErrorBoundary for React crashes
- Verify backend is running

### SSE connection fails
- Ensure backend CORS is configured
- Check network tab for streaming response
- Verify `/api/analyze/stream` endpoint accessible

### Cost is higher than expected
- Check token usage in response metadata
- Verify you're using GPT-4o (not GPT-4)
- Consider reducing max_tokens in agent prompts

---

## 📚 Documentation

- **[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)** - Deployment guide
- **[CLAUDE.md](./CLAUDE.md)** - Project instructions for development
- **Frontend README**: `frontend/README.md`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests: `pytest tests/`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details

---

## 🙏 Acknowledgments

**Built with**:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [OpenRouter](https://openrouter.ai/) - LLM API gateway
- [Tavily](https://tavily.com/) - AI-optimized search
- [LangSmith](https://smith.langchain.com/) - LLM observability
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) + [Vite](https://vitejs.dev/) - Frontend
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/startup-analyzer/issues)
- **Documentation**: This README + inline code docs
- **Examples**: `tests/evaluation/datasets/`

---

**⭐ Star this repo if you find it useful!**

**Built to showcase production-grade multi-agent systems with comprehensive observability.**
