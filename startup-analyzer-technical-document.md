# Startup Analyzer - Technical Architecture Document

## Executive Summary

This document provides a comprehensive technical overview of the Startup Analyzer multi-agent system, focusing on architecture decisions, implementation details, and observability infrastructure.

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐     ┌─────────────┐     ┌───────────────┐ │
│  │   API      │────▶│  LangGraph  │────▶│ Observability │ │
│  │ Endpoints  │     │  Workflow   │     │    Stack      │ │
│  └────────────┘     └─────────────┘     └───────────────┘ │
│        │                   │                     │          │
│        │                   │                     │          │
│        ▼                   ▼                     ▼          │
│  ┌────────────┐     ┌─────────────┐     ┌───────────────┐ │
│  │    SSE     │     │   4 Agents  │     │   LangSmith   │ │
│  │ Streaming  │     │  (parallel) │     │    Tracing    │ │
│  └────────────┘     └─────────────┘     └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐│
│  │ OpenRouter │  │   Tavily    │  │  FAISS Vector Store  ││
│  │  (GPT-4o)  │  │   Search    │  │  (Marketing RAG)     ││
│  └────────────┘  └─────────────┘  └──────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent System Design

### Agent Architecture

All agents inherit from `BaseAgent`:

```python
class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(__name__)

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic and return updated state."""
        pass

    def log_decision(self, decision: str, reasoning: str, confidence: float):
        """Log agent decision with context."""
        self.logger.info(
            f"{self.name}_decision",
            decision=decision,
            reasoning=reasoning,
            confidence=confidence
        )
```

### Agent Implementation Details

#### 1. Analyst Agent

**File**: `src/agents/analyst.py`

**Responsibilities**:
- Brand DNA extraction
- Core strengths identification
- Business model analysis

**Implementation**:
```python
@trace_agent("analyst")
async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Extract business idea from state
    business_idea = state.get("business_idea") or {}
    x_brand = business_idea.get("x_brand")

    # 2. Search for brand information
    search_result = await self.tavily_tool.execute(
        ToolInput(
            tool_name="tavily_search",
            parameters={"query": f"{x_brand} business model", "max_results": 5}
        )
    )

    # 3. LLM analysis with structured output
    llm_response = await self.llm_client.generate(
        system=ANALYST_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=2000
    )

    # 4. Parse and store results
    brand_dna = json.loads(llm_response.content)
    state["analyst_insights"] = brand_dna

    # 5. Track token usage
    state["metadata"]["token_usage"]["analyst"] = {
        "prompt_tokens": llm_response.prompt_tokens,
        "completion_tokens": llm_response.completion_tokens
    }

    return state
```

**Token Usage**: ~1,200 input, ~600 output

#### 2. Researcher Agent

**File**: `src/agents/researcher.py`

**Responsibilities**:
- Market saturation assessment
- Competitor identification
- Opportunity discovery

**Key Optimization**: Parallel searches

```python
# Execute market and competitor searches concurrently
market_search, competitor_search = await asyncio.gather(
    self.tavily_tool.execute(ToolInput(..., query=market_query)),
    self.tavily_tool.execute(ToolInput(..., query=competitor_query))
)
```

**Performance Impact**: Saves 5-8 seconds vs sequential execution

**Token Usage**: ~1,400 input, ~700 output

#### 3. Risk Analyst Agent

**File**: `src/agents/risk_analyst.py`

**Responsibilities**:
- Business model classification
- Risk framework retrieval (RAG)
- Threat identification
- Fatal flaw detection

**Key Optimization**: Two-tier LLM strategy

```python
# Step 1: Fast classification with GPT-4o-mini (saves 2-3s, reduces cost)
classification_response = await self.classification_client.generate(
    system="Classify business model type",
    messages=[{"role": "user", "content": f"Classify: {business_idea}"}],
    max_tokens=50,
    temperature=0.3
)

# Step 2: Context-aware RAG lookup
business_model_type = classification_response.content.strip()
rag_query = rag_query_map[business_model_type]
rag_result = await self.rag_tool.execute(ToolInput(..., query=rag_query))

# Step 3: Full risk analysis with GPT-4o
llm_response = await self.llm_client.generate(
    system=RISK_ANALYST_SYSTEM_PROMPT,
    messages=[{"role": "user", "content": f"Analyze risks...\n{rag_context}"}]
)
```

**Token Usage**:
- Classification: ~45 input, ~12 output (GPT-4o-mini)
- Analysis: ~1,500 input, ~800 output (GPT-4o)

#### 4. Strategist Agent

**File**: `src/agents/strategist.py`

**Responsibilities**:
- Research coordination (identifies gaps)
- GTM plan synthesis
- Viability scoring

**Dual-Mode Operation**:

1. **Coordination Mode** (`strategist_coordination_node`):
```python
async def strategist_coordination_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Review all research
    research_summary = create_summary(state)

    # Ask: "Do we have enough information?"
    coordination_prompt = f"""
    Review the research and decide:
    - PROCEED if research is sufficient for GTM plan
    - REQUEST_FOLLOWUP if critical gaps exist

    Research: {research_summary}
    """

    decision = await llm_client.generate(system=..., messages=[...])

    if decision == "REQUEST_FOLLOWUP":
        state["ready_for_synthesis"] = False
        state["follow_up_requests"] = extract_requests(decision)
    else:
        state["ready_for_synthesis"] = True

    return state
```

2. **Synthesis Mode** (`strategist_synthesis_node`):
```python
async def strategist_synthesis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Create final GTM plan from all research
    gtm_plan = await create_gtm_strategy(state)
    state["strategist_plan"] = gtm_plan

    # Calculate total cost
    state["metadata"]["cost_usd"] = calculate_total_cost(state)

    return state
```

**Token Usage**: ~2,300 input, ~1,200 output

---

## LangGraph Workflow

### Workflow Definition

**File**: `src/orchestration/graph.py`

```python
def create_analysis_graph():
    workflow = StateGraph(dict)

    # Nodes
    workflow.add_node("parallel_analysis", parallel_analysis_node)
    workflow.add_node("strategist_coordination", strategist_coordination_node)
    workflow.add_node("strategist_synthesis", strategist_synthesis_node)

    # Edges
    workflow.set_entry_point("parallel_analysis")
    workflow.add_edge("parallel_analysis", "strategist_coordination")

    # Conditional routing (enables loops)
    workflow.add_conditional_edges(
        "strategist_coordination",
        route_after_coordination,
        {
            "coordination": "strategist_coordination",  # Loop back
            "synthesis": "strategist_synthesis",        # Proceed
        }
    )

    workflow.add_edge("strategist_synthesis", END)

    return workflow.compile()
```

### Parallel Execution Node

**File**: `src/orchestration/nodes.py`

```python
async def parallel_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Analyst, Researcher, and Risk Analyst concurrently."""

    analyst = get_analyst()
    researcher = get_researcher()
    risk_analyst = get_risk_analyst()

    # Run all three agents in parallel
    analyst_state, researcher_state, risk_state = await asyncio.gather(
        analyst.execute(copy.deepcopy(state)),
        researcher.execute(copy.deepcopy(state)),
        risk_analyst.execute(copy.deepcopy(state)),
        return_exceptions=False
    )

    # Merge results
    state["analyst_insights"] = analyst_state.get("analyst_insights")
    state["researcher_findings"] = researcher_state.get("researcher_findings")
    state["risk_analysis"] = risk_state.get("risk_analysis")

    # Merge token usage
    merge_token_usage(state, analyst_state, researcher_state, risk_state)

    return state
```

**Performance**: 15-20s for all three vs 40-50s sequential

### Routing Logic

**File**: `src/orchestration/edges.py`

```python
def route_after_coordination(state: Dict[str, Any]) -> Literal["coordination", "synthesis"]:
    """Route after strategist coordination."""

    ready_for_synthesis = state.get("ready_for_synthesis", False)
    coordination_iteration = state.get("coordination_iteration", 0)
    max_iterations = state.get("max_coordination_iterations", 3)

    if ready_for_synthesis:
        return "synthesis"  # Proceed to final plan
    elif coordination_iteration >= max_iterations:
        return "synthesis"  # Force synthesis at max iterations
    else:
        return "coordination"  # Loop back for more research
```

---

## Observability Infrastructure

### 1. LangSmith Tracing

**Implementation**: Automatic via LangChain ChatOpenAI

```python
# OpenRouter client with LangSmith integration
self.llm = ChatOpenAI(
    model="openai/gpt-4o",
    openai_api_key=settings.openrouter_api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    # LangSmith automatically enabled via LANGCHAIN_TRACING_V2
)
```

**Trace Hierarchy**:
```
workflow.execute
├── parallel_analysis_node
│   ├── analyst.execute
│   │   ├── tavily_search (tool)
│   │   └── llm.generate (GPT-4o)
│   ├── researcher.execute
│   │   ├── tavily_search (market)
│   │   ├── tavily_search (competitors)
│   │   └── llm.generate (GPT-4o)
│   └── risk_analyst.execute
│       ├── llm.generate (GPT-4o-mini, classification)
│       ├── marketing_rag (tool)
│       └── llm.generate (GPT-4o, analysis)
├── strategist_coordination_node
│   └── llm.generate (GPT-4o)
└── strategist_synthesis_node
    └── llm.generate (GPT-4o)
```

### 2. Structured Logging

**Implementation**: Custom JSON logger

**File**: `src/observability/logger.py`

```python
class StructuredLogger:
    def info(self, event: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "event": event,
            "correlation_id": get_correlation_id(),
            **kwargs
        }
        print(json.dumps(log_entry))
```

**Key Events**:
- `workflow_started` / `workflow_completed`
- `agent_started` / `agent_completed`
- `tool_called` / `tool_completed`
- `llm_request_started` / `llm_request_completed`
- `coordination_decision`
- `error_occurred`

### 3. Token Tracking

**Per-Agent Storage**:

```python
state["metadata"]["token_usage"] = {
    "analyst": {
        "prompt_tokens": 1234,
        "completion_tokens": 567,
        "total_tokens": 1801
    },
    "researcher": {...},
    "risk_analyst": {
        "classification_prompt_tokens": 45,
        "classification_completion_tokens": 12,
        "analysis_prompt_tokens": 1567,
        "analysis_completion_tokens": 789,
        "total_tokens": 2413
    },
    "strategist": {...}
}
```

**Cost Calculation** (in Strategist):

```python
total_prompt_tokens = sum(
    usage.get("prompt_tokens", 0)
    for usage in state["metadata"]["token_usage"].values()
)
total_completion_tokens = sum(
    usage.get("completion_tokens", 0)
    for usage in state["metadata"]["token_usage"].values()
)

# GPT-4o pricing
cost_usd = (total_prompt_tokens / 1_000_000 * 2.5) + \
           (total_completion_tokens / 1_000_000 * 10.0)
```

**Known Issue**: Risk Analyst's multi-call tokens don't aggregate properly in backend calculation (frontend handles it correctly).

### 4. Real-Time SSE Streaming

**Implementation**: FastAPI SSE endpoint

**File**: `src/api/routes/analysis.py`

```python
@router.get("/analyze/stream")
async def analyze_stream(x_brand: str, y_market: str):
    async def event_generator():
        # Initial event
        yield f"event: started\ndata: {json.dumps({...})}\n\n"

        # Execute workflow
        result = await workflow.execute(...)

        # Stream progress events
        for event in result.events:
            yield f"event: {event.type}\ndata: {json.dumps(event.data)}\n\n"

        # Final event
        yield f"event: complete\ndata: {json.dumps(result)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Event Types**:
- `agent_started` / `agent_completed`
- `tool_called`
- `coordination_decision`
- `complete` / `error`

---

## Tool Integration

### Tavily Search Tool

**File**: `src/tools/tavily.py`

**Features**:
- AI-optimized search
- Configurable depth (basic/advanced)
- Domain filtering
- Async HTTP client

**Usage Example**:
```python
tool = TavilySearchTool()
result = await tool.execute(ToolInput(
    tool_name="tavily_search",
    parameters={
        "query": "Uber business model",
        "max_results": 5,
        "search_depth": "advanced"
    }
))
```

**Rate Limits**: 1000 queries/month (free tier)

### Marketing RAG Tool

**File**: `src/tools/marketing_rag.py`

**Architecture**:
```
Marketing Docs (.txt)
        ↓
  Text Splitter
        ↓
OpenAI Embeddings (via OpenRouter)
        ↓
   FAISS Index
        ↓
Semantic Search (k=3)
```

**Implementation**:
```python
class MarketingRAGTool(BaseTool):
    def _load_vectorstore(self):
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings

        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )

        if vector_store_exists:
            self.vectorstore = FAISS.load_local(path, self.embeddings)
        else:
            # Build from documents
            docs = load_documents("data/knowledge_base/")
            chunks = split_text(docs)
            self.vectorstore = FAISS.from_texts(chunks, self.embeddings)
            self.vectorstore.save_local(path)
```

**Query Strategy** (in Risk Analyst):
```python
rag_query_map = {
    "marketplace": "marketplace cold start chicken-egg network effects",
    "subscription": "subscription churn retention pricing SaaS failures",
    "saas": "B2B SaaS enterprise sales switching costs",
    # ...
}
query = rag_query_map[business_model_type]
```

---

## Frontend Architecture

### React + Vite Stack

**Key Components**:

1. **AnalysisForm.jsx** - Input form
2. **useSSE.js** - Custom hook for SSE streaming
3. **ProgressDisplay.jsx** - Real-time agent status
4. **MetricsDashboard.jsx** - Token/cost display
5. **ResultsDisplay.jsx** - Analysis results
6. **DebugPanel.jsx** - Console interceptor
7. **ErrorBoundary.jsx** - React error handling

### SSE Streaming Hook

**File**: `frontend/src/hooks/useSSE.js`

```javascript
export function useSSE(endpoint, request, shouldConnect) {
  const [events, setEvents] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!shouldConnect) return;

    const eventSource = new EventSource(
      `${API_URL}${endpoint}?x_brand=${request.x_brand}&y_market=${request.y_market}`
    );

    eventSource.addEventListener('agent_completed', (e) => {
      const data = JSON.parse(e.data);
      setEvents(prev => [...prev, data]);
    });

    eventSource.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data);
      setResult(data);
      eventSource.close();
    });

    return () => eventSource.close();
  }, [shouldConnect]);

  return { events, result, error };
}
```

### Debug Panel

**Purpose**: On-screen debugging for tablets/mobile

**Features**:
- Console log interception
- JSON result inspection
- SSE event log
- Connection status

**Implementation**: Overrides `console.log/error/warn` and stores in React state.

---

## Performance Optimizations

### 1. Parallel Agent Execution

**Impact**: Saves 15-20 seconds
- Sequential: 40-50s (Analyst 12s → Researcher 15s → Risk 13s)
- Parallel: 20-25s (all three concurrently, takes longest duration)

### 2. Fast Business Model Classification

**Impact**: Saves 2-3 seconds, reduces cost
- GPT-4o: ~3s, $0.005
- GPT-4o-mini: ~0.5s, $0.0003 (17x cheaper)

### 3. Researcher Parallel Searches

**Impact**: Saves 5-8 seconds
- Sequential: 2 × 4s = 8s
- Parallel: max(4s, 4s) = 4s

### 4. Dynamic Coordination

**Impact**: Only loops when necessary
- Avoids fixed iteration counts
- Strategist decides when research is sufficient
- Typically 0-1 loops (95% of cases)

---

## Cost Analysis

### Typical Analysis Breakdown

| Component | Tokens (in/out) | Cost |
|-----------|----------------|------|
| Analyst | 1,234 / 567 | $0.0088 |
| Researcher | 1,456 / 678 | $0.0104 |
| Risk Analyst (classification) | 45 / 12 | $0.0002 |
| Risk Analyst (analysis) | 1,567 / 789 | $0.0118 |
| Strategist | 2,345 / 1,234 | $0.0182 |
| **Total** | **6,647 / 3,280** | **$0.0494** |

**Pricing** (GPT-4o via OpenRouter):
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens

---

## Error Handling

### Backend Error Handling

1. **Agent-level**: Try-catch with fallback values
2. **Workflow-level**: State recovery and error state
3. **API-level**: HTTP error responses with details

### Frontend Error Handling

1. **ErrorBoundary**: Catches React rendering crashes
2. **SSE error events**: Backend errors streamed to UI
3. **Network errors**: Retry logic and user feedback

---

## Testing Strategy

### Unit Tests

- Agent logic (`tests/agents/`)
- Tool functionality (`tests/tools/`)
- LLM client (`tests/llm/`)

### Integration Tests

- Workflow execution (`tests/orchestration/`)
- API endpoints (`tests/api/`)

### Evaluation

- Response quality (`tests/evaluation/`)
- Cost analysis
- Performance benchmarks

---

## Deployment Architecture

### Production Setup

```
┌──────────────────────────────────────────────────┐
│              Railway (Backend)                   │
│  - Python 3.11 runtime                          │
│  - Gunicorn + Uvicorn workers                   │
│  - Environment variables in dashboard           │
└──────────────────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌──────────────────────────────────────────────────┐
│           Vercel/Netlify (Frontend)              │
│  - Static site deployment (dist/)                │
│  - VITE_API_URL → Railway backend                │
└──────────────────────────────────────────────────┘
```

### Environment Configuration

**Backend (.env)**:
```bash
OPENROUTER_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LANGSMITH_API_KEY=ls__...
LLM_MODEL=openai/gpt-4o
LOG_LEVEL=INFO
```

**Frontend (.env)**:
```bash
VITE_API_URL=https://your-backend.railway.app
```

---

## Future Enhancements

### Planned Features

1. **Caching Layer** - Redis for repeated analyses
2. **User Authentication** - JWT-based auth
3. **Analysis History** - PostgreSQL storage
4. **Batch Analysis** - Process multiple ideas
5. **Custom Agents** - User-defined agent logic
6. **RAG Improvements** - Better chunking, hybrid search
7. **Cost Optimization** - Prompt compression, caching

### Scalability Considerations

- **Rate limiting** - Per-user API limits
- **Queue system** - Celery for background processing
- **Database** - Move from in-memory to PostgreSQL
- **Load balancing** - Multiple backend instances

---

## Appendix

### Key Configuration Files

- `config/settings.py` - Environment settings
- `requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `.env` - Environment variables (not in git)

### External Service Dependencies

1. **OpenRouter** - LLM API gateway
2. **Tavily** - AI-optimized search
3. **LangSmith** - Observability platform
4. **Railway** - Backend hosting
5. **Vercel/Netlify** - Frontend hosting

### Monitoring Checklist

- [ ] LangSmith traces enabled
- [ ] Structured logs captured
- [ ] SSE events streaming correctly
- [ ] Token usage tracked
- [ ] Cost calculation accurate
- [ ] Error boundaries active
- [ ] Debug panel accessible

---

**Document Version**: 1.0
**Last Updated**: 2026-01-02
**Maintained By**: Development Team
