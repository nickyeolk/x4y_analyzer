# Startup Analyzer - "X for Y" Marketing Stress Tester

A multi-agent system with comprehensive observability that analyzes "X for Y" business ideas (e.g., "Uber for Dog Walkers") through intelligent orchestration and real-time transparency.

## Features

- 🤖 **Multi-Agent Analysis**: Analyst, Researcher, Skeptic, and Strategist agents work together
- 🔄 **Cyclic Workflows**: Skeptic can trigger feedback loops for deeper analysis
- 📊 **Real-Time Observability**: Live traces, structured logs, and metrics dashboard
- 🔍 **AI-Powered Research**: Tavily search + RAG over marketing frameworks
- 💡 **GTM Strategy Generation**: Actionable go-to-market plans with LinkedIn hooks
- 🎯 **LangSmith Integration**: Visual trace exploration for stakeholders

## Architecture

```
User Input ("Uber for Dog Walkers")
         ↓
    [Analyst] → Analyzes Uber's DNA
         ↓
   [Researcher] → Investigates dog walking market
         ↓
    [Skeptic] → Critiques idea
         ↓     ↖ (loops back if weak)
  [Strategist] → Final GTM plan
```

## Quick Start

### 1. Installation

```bash
# Clone and install
git clone <repo>
cd startup_analyzer
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
# Required: LLM Provider (OpenRouter)
OPENROUTER_API_KEY=your_key_here
LLM_MODEL=openai/gpt-4o

# Required: Search Tool
TAVILY_API_KEY=your_key_here

# Optional: LangSmith Tracing
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=startup-analyzer
LANGCHAIN_TRACING_V2=true

# Observability
OTEL_ENABLED=true
OTEL_EXPORTER=console
LOG_LEVEL=INFO
APP_ENV=development
```

### 3. RAG Knowledge Base Setup

**IMPORTANT: Where to Place Marketing Documents**

The RAG (Retrieval Augmented Generation) system needs marketing framework documents to provide intelligent insights.

#### Step 1: Create Directory Structure

```bash
mkdir -p data/knowledge_base
mkdir -p data/vector_store
```

#### Step 2: Add Your Documents

Place marketing framework documents (`.txt` files) in `data/knowledge_base/`. Examples:

**Recommended Documents:**

1. **`data/knowledge_base/marketing_pitfalls.txt`**
   - Common startup marketing mistakes
   - Red flags for saturated markets
   - Warning signs for bad business ideas

2. **`data/knowledge_base/gtm_frameworks.txt`**
   - Go-to-market strategy templates
   - Pricing strategy frameworks
   - Distribution channel playbooks

3. **`data/knowledge_base/competitive_analysis.txt`**
   - SWOT analysis frameworks
   - Competitive positioning strategies
   - Market entry tactics

4. **`data/knowledge_base/linkedin_marketing.txt`**
   - Viral post formulas
   - Hook writing techniques
   - B2B marketing strategies

**Example Document Format:**

```
File: data/knowledge_base/marketing_pitfalls.txt

Title: Common Marketing Pitfalls for Startups

1. TARGETING TOO BROAD
Many startups fail by trying to appeal to everyone. The "Uber for X" model
only works if X has specific pain points that generic solutions don't address.

Example: "Uber for grocery delivery" succeeded (Instacart) because grocery
shopping is time-consuming and people value convenience. But "Uber for mail
delivery" failed because USPS already offers cheap, reliable service.

2. IGNORING MARKET SATURATION
Entering an oversaturated market without clear differentiation is a death sentence.

Red flags:
- More than 5 well-funded competitors
- Market leader has >40% market share
- Low barriers to entry

3. UNDERESTIMATING CAC (Customer Acquisition Cost)
...

[Continue with more pitfalls]
```

#### Step 3: Build Vector Store

Once documents are in place, build the searchable index:

```bash
python scripts/build_vector_store.py
```

**Expected Output:**
```
Building vector store from marketing knowledge base...
Loading documents from: data/knowledge_base
Loaded 4 documents
Splitting documents into chunks...
Created 48 chunks
Creating FAISS vector store...
Saving vector store to: data/vector_store
✅ Vector store built successfully!
   - Documents: 4
   - Chunks: 48
   - Location: data/vector_store
```

**Troubleshooting:**
- If "No documents found", ensure `.txt` files are in `data/knowledge_base/`
- If embedding fails, check `OPENROUTER_API_KEY` is set correctly
- Vector store will be saved in `data/vector_store/` and loaded automatically

#### Step 4: Verify RAG Setup

Test the RAG tool:

```python
from src.tools.marketing_rag import get_rag_tool
from src.tools.base import ToolInput

rag = get_rag_tool()
result = await rag.execute(ToolInput(
    tool_name="rag",
    parameters={
        "query": "What are common pitfalls for marketplace startups?",
        "k": 3
    }
))

print(result.result["documents"])
```

### 4. Run the Application

```bash
# Start the API server
python -m src.api.main

# Or use uvicorn directly
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Analyze a Startup Idea

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "x_brand": "Uber",
    "y_market": "Dog Walkers"
  }'
```

## Project Structure

```
startup_analyzer/
├── config/                    # Configuration & settings
├── src/
│   ├── agents/               # 4 specialized agents
│   │   ├── analyst.py       # Brand DNA analysis
│   │   ├── researcher.py    # Market research
│   │   ├── skeptic.py       # Critical evaluation
│   │   ├── strategist.py    # GTM strategy
│   │   └── prompts/         # System prompts
│   ├── orchestration/        # LangGraph workflow
│   │   ├── state.py         # State management
│   │   └── graph.py         # DCG with loops
│   ├── tools/               # External integrations
│   │   ├── tavily.py        # Web search
│   │   └── marketing_rag.py # Knowledge base
│   ├── llm/                 # OpenRouter client
│   ├── observability/       # Tracing, logs, metrics
│   └── api/                 # FastAPI routes
├── data/
│   ├── knowledge_base/      # 📄 PUT YOUR .TXT FILES HERE
│   └── vector_store/        # Auto-generated FAISS index
├── scripts/
│   └── build_vector_store.py
└── frontend/                # React app (if building UI)
```

## Observability Dashboard

### View Real-Time Traces

```bash
# Console output
OTEL_EXPORTER=console python -m src.api.main

# Jaeger (requires Docker)
docker run -d -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one:latest
# Set OTEL_EXPORTER=jaeger in .env
# Visit http://localhost:16686
```

### View Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

**Key Metrics:**
- `analysis_duration_seconds` - Total analysis time
- `analysis_loop_count` - Number of skeptic loops
- `tool_call_count` - Tavily and RAG usage
- `llm_tokens_used` - Token consumption
- `llm_api_cost_dollars` - Estimated API costs

### View Structured Logs

```bash
# Filter by agent
tail -f logs/app.log | grep "analyst_completed"

# Filter by correlation ID
tail -f logs/app.log | grep "CID-abc123"
```

## Example Analysis Flow

```
Input: "Uber for Dog Walkers"

[Analyst] Searching: "Uber business model key features"
[Analyst] ✓ Brand DNA: On-demand marketplace, two-sided platform,
          dynamic pricing, real-time GPS, trust & safety systems
          Confidence: 0.87

[Researcher] Searching: "dog walking market size competitors"
[Researcher] ✓ Market: $1.2B, 15+ competitors (Rover, Wag, etc.),
             HIGH saturation, barriers: trust, insurance, local regulation

[Skeptic] 🔍 Reviewing analysis...
[Skeptic] ⚠️ CONCERNS: Market already saturated, Rover has 70% share,
          unit economics unclear, no clear differentiation
[Skeptic] ❌ REJECTED - Loop back reason: "Need deeper competitive analysis"

[Analyst] (Iteration 2) Deeper research on Rover and Wag...
[Analyst] ✓ Updated insights: Rover succeeded via trust (reviews + insurance)

[Researcher] (Iteration 2) Analyzing gaps in existing solutions...
[Researcher] ✓ OPPORTUNITY: Premium service tier (certified trainers)

[Skeptic] ✅ APPROVED - Proceed to strategy

[Strategist] 📋 GTM Plan:
- Target: Affluent urban professionals with high-value dogs
- Value Prop: "Certified dog trainers, not just walkers"
- Pricing: Premium ($50/walk vs $25 industry avg)
- Channels: Instagram, vet partnerships, pet boutiques
- Marketing Hooks:
  1. "Your dog deserves a trainer, not just a walker"
  2. "Rover gets you a walk. We get you better behavior."
  3. "Premium dogs deserve premium care"
- Viability: 0.68 (medium - requires strong execution)
```

## API Reference

### POST /analyze

Start a new analysis:

```json
{
  "x_brand": "Uber",
  "y_market": "Dog Walkers",
  "description": "Optional additional context"
}
```

**Response (SSE Stream):**
```
event: agent_started
data: {"agent": "analyst", "status": "running"}

event: tool_called
data: {"tool": "tavily_search", "query": "..."}

event: agent_completed
data: {"agent": "analyst", "result": {...}}

event: loop_triggered
data: {"reason": "weak analysis", "iteration": 2}

event: analysis_completed
data: {"final_plan": {...}, "trace_url": "..."}
```

## Evaluation & Testing

```bash
# Run evaluation suite
python -m pytest tests/evaluation/

# Run specific metric
python -m pytest tests/evaluation/test_gtm_quality.py
```

## Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Environment Variables:**
Set all `.env` variables in Railway dashboard.

## Troubleshooting

### "Vector store not initialized"
→ Run `python scripts/build_vector_store.py`
→ Ensure documents exist in `data/knowledge_base/`

### "OPENROUTER_API_KEY not set"
→ Add to `.env` file
→ Restart application

### "Tavily API rate limit exceeded"
→ Check your Tavily plan limits
→ Add caching to reduce API calls

### JSON parsing errors
→ Check LLM temperature (lower = more structured)
→ Review agent prompt format instructions

## Documentation

- [Implementation Proposal](./IMPLEMENTATION_PROPOSAL.md) - Detailed design doc
- [Implementation Status](./IMPLEMENTATION_STATUS.md) - Current progress
- [Quick Start Guide](./QUICKSTART.md) - Development guide
- [Observability Guide](./docs/observability_guide.md) - Traces, logs, metrics
- [Architecture Guide](./docs/architecture.md) - System design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Issues: GitHub Issues
- Documentation: `/docs` directory
- Examples: `/tests/evaluation/datasets`

---

**Built with**: FastAPI, LangGraph, OpenRouter, Tavily, FAISS, OpenTelemetry, React

**Observability**: Every request traced, logged, and metered for production debugging
