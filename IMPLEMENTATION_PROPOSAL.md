# Startup Analyzer Implementation Proposal

## Executive Summary

This proposal outlines how to transform the existing AgentLand observability infrastructure into a "X for Y" Agentic Marketing Stress Tester while preserving all observability capabilities. The implementation will maintain the proven three-pillar observability approach (Traces, Logs, Metrics) while adapting it to the new business domain.

---

## Current State Analysis

### Existing Observability Components

The current AgentLand codebase provides production-ready observability:

#### 1. **Tracing Layer** (`src/observability/tracer.py`)
- OpenTelemetry distributed tracing
- Span hierarchy with automatic correlation
- Trace context propagation
- Support for console, Jaeger, and OTLP exporters

#### 2. **Logging Layer** (`src/observability/logger.py`)
- Structlog with JSON output
- Automatic correlation ID binding
- Rich context in every log entry
- Development-friendly console format

#### 3. **Metrics Layer** (`src/observability/metrics.py`)
- Prometheus format metrics
- Agent performance tracking
- Tool usage monitoring
- LLM cost tracking
- Business metrics

#### 4. **Orchestration Layer** (`src/orchestration/`)
- Custom state machine (LangGraph-compatible)
- State management with dataclasses
- Node-based workflow execution
- Conditional routing logic

#### 5. **Agent Architecture** (`src/agents/`)
- BaseAgent abstract class
- Specialized agents with focused responsibilities
- Automatic tracing with decorators
- Prompt management

#### 6. **Tool System** (`src/tools/`)
- BaseTool with consistent interface
- Automatic tracing and metrics
- Mock implementations for development
- Tool registry for agent-tool mapping

---

## Target State: Startup Analyzer

### Business Requirements

Transform the system to analyze "X for Y" business ideas through:

1. **The Analyst**: Deconstructs brand DNA of the "X" company
2. **The Researcher**: Investigates market saturation for "Y" segment
3. **The Skeptic**: Critiques ideas and triggers feedback loops
4. **The Strategist**: Synthesizes final GTM strategy

### Technical Requirements

1. **LangGraph DCG**: Support cyclic workflows for "thinking" loops
2. **Real-time Streaming**: SSE to React frontend
3. **Triple-Layer Observability**:
   - Real-time UX status updates
   - Embedded trace viewer (LangSmith)
   - Live metrics dashboard
4. **Tools**: Tavily API, RAG with marketing frameworks
5. **LLM**: GPT-4o-mini or Claude 3.5 Sonnet

---

## Implementation Strategy

### Phase 1: Core Architecture Migration

#### 1.1 Update State Schema

**Current**: Ticket-based state (AgentState for support tickets)
**Target**: Analysis-based state

```python
# src/startup_analyzer/state.py
@dataclass
class AnalysisState:
    # Identity
    analysis_id: str
    correlation_id: str
    timestamp: datetime

    # Input
    business_idea: BusinessIdea  # "X for Y" structure

    # Agent Results
    analyst_insights: Optional[BrandDNA]
    researcher_findings: Optional[MarketResearch]
    skeptic_critique: Optional[Critique]
    strategist_plan: Optional[GTMPlan]

    # Workflow Control
    loop_count: int = 0
    max_loops: int = 3
    skeptic_approved: bool = False

    # Observability
    agent_interactions: List[AgentInteraction]
    metadata: AnalysisMetadata
```

**Observability Impact**:
- All existing tracing/logging remains functional
- New state fields automatically tracked
- Correlation ID flows through entire analysis

#### 1.2 Implement LangGraph DCG

**Current**: Linear workflow (triage → specialist → done)
**Target**: Cyclic workflow with loops

```python
# src/startup_analyzer/graph.py
from langgraph.graph import StateGraph, END

def create_analysis_graph():
    workflow = StateGraph(AnalysisState)

    # Add nodes
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("skeptic", skeptic_node)
    workflow.add_node("strategist", strategist_node)

    # Linear flow
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "researcher")
    workflow.add_edge("researcher", "skeptic")

    # Conditional routing (LOOP CAPABILITY)
    workflow.add_conditional_edges(
        "skeptic",
        route_after_skeptic,  # Returns "analyst" or "strategist"
        {
            "loop_back": "analyst",  # Skeptic not satisfied
            "continue": "strategist",  # Skeptic approved
        }
    )

    workflow.add_edge("strategist", END)

    return workflow.compile()
```

**Observability Enhancement**:
- Each loop iteration creates a new span group
- Loop count tracked in metrics: `analysis_loop_count{reason="weak_logic"}`
- Logs show: `event: "skeptic_triggered_loop", iteration: 2, reason: "..."`

#### 1.3 Migrate Agents to New Domain

**Mapping**:
- TriageAgent → **AnalystAgent** (brand DNA deconstruction)
- BillingAgent → **ResearcherAgent** (market research)
- TechnicalAgent → **SkepticAgent** (critique & validation)
- AccountAgent → **StrategistAgent** (GTM synthesis)
- EscalationAgent → *(remove or repurpose as "human review" for edge cases)*

**Implementation Pattern** (example for Analyst):

```python
# src/startup_analyzer/agents/analyst.py
from src.agents.base import BaseAgent
from src.observability.decorators import trace_agent

class AnalystAgent(BaseAgent):
    """Deconstructs the 'X' brand's DNA."""

    @trace_agent
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        business_idea = state["business_idea"]

        # Tool: Tavily search for "X" brand
        brand_info = await self.search_brand(business_idea.x_brand)

        # LLM: Analyze brand DNA
        brand_dna = await self.llm_client.generate(
            system_prompt=ANALYST_PROMPT,
            user_message=f"Analyze: {business_idea.x_brand}",
            context=brand_info
        )

        # Update state
        state["analyst_insights"] = brand_dna

        # Observability (automatic via @trace_agent)
        self.log_decision(
            decision="brand_analyzed",
            reasoning=brand_dna.summary,
            confidence=brand_dna.confidence
        )

        return state
```

**Observability Continuity**:
- Same `@trace_agent` decorator
- Same logging patterns
- Same metrics recording
- Zero observability code changes needed

### Phase 2: Real-Time Streaming (Triple-Layer Observability)

#### 2.1 Layer 1: Real-Time Status Stream (UX)

**Add SSE endpoint** to FastAPI:

```python
# src/api/routes/analysis.py
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

@router.post("/analyze")
async def analyze_startup(request: AnalysisRequest):
    """Start analysis and return stream."""

    async def event_generator():
        analysis_id = generate_id()

        # Stream updates as workflow progresses
        async for event in run_analysis_with_streaming(request.business_idea):
            yield {
                "event": event.type,  # "agent_started", "agent_thinking", "tool_called"
                "data": json.dumps({
                    "analysis_id": analysis_id,
                    "agent": event.agent,
                    "status": event.status,
                    "message": event.message,
                    "timestamp": event.timestamp.isoformat()
                })
            }

    return EventSourceResponse(event_generator())
```

**Streaming Integration with Observability**:

```python
# src/startup_analyzer/streaming.py
async def run_analysis_with_streaming(business_idea):
    """Run analysis and yield events for SSE."""

    # Create callback handler for LangGraph
    class StreamingHandler:
        async def on_agent_start(self, agent_name):
            # Emit SSE event
            yield StreamEvent(
                type="agent_started",
                agent=agent_name,
                status="running",
                message=f"{agent_name} is analyzing..."
            )

            # Still create trace span (observability unchanged)
            # Logging still happens
            # Metrics still recorded

    # Execute workflow with handler
    graph = get_analysis_graph()
    async for event in graph.astream_events(initial_state, callbacks=[StreamingHandler()]):
        yield event
```

**React Frontend** (brief example):

```javascript
// frontend/src/hooks/useAnalysisStream.ts
export function useAnalysisStream(businessIdea) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const eventSource = new EventSource('/api/analyze');

    eventSource.addEventListener('agent_started', (e) => {
      const data = JSON.parse(e.data);
      setEvents(prev => [...prev, {
        type: 'status',
        message: `${data.agent} is working...`,
        timestamp: data.timestamp
      }]);
    });

    // ... more event listeners
  }, [businessIdea]);

  return events;
}
```

**Observability Benefits**:
- User sees real-time progress
- Backend still traces everything normally
- SSE events are ADDITIONAL, not replacing existing observability

#### 2.2 Layer 2: Embedded Trace Viewer (LangSmith)

**LangSmith Integration**:

```python
# config/settings.py
class Settings:
    # ... existing settings
    langsmith_api_key: str = Field(default="", env="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="startup-analyzer", env="LANGSMITH_PROJECT")
    langchain_tracing_v2: bool = Field(default=True, env="LANGCHAIN_TRACING_V2")
```

```python
# src/observability/langsmith.py
from langsmith import Client

def get_langsmith_client():
    return Client(api_key=settings.langsmith_api_key)

def get_trace_url(run_id: str) -> str:
    """Get LangSmith trace URL for embedding."""
    return f"https://smith.langchain.com/public/{settings.langsmith_project}/r/{run_id}"
```

**Frontend Integration**:

```javascript
// After analysis completes, embed trace viewer
<iframe
  src={`https://smith.langchain.com/public/${projectId}/r/${runId}?embed=true`}
  className="trace-viewer"
  title="Execution Trace"
/>
```

**Dual Tracing**:
- OpenTelemetry traces (existing) → for development/debugging
- LangSmith traces → for user-facing visualization
- Both run concurrently, no conflicts

#### 2.3 Layer 3: Live Metrics Dashboard

**New Metrics for Startup Analyzer**:

```python
# src/observability/metrics.py

# Analysis-specific metrics
analysis_duration = Histogram(
    "analysis_duration_seconds",
    "Total time to complete analysis",
    ["has_loops"],
    buckets=[5.0, 10.0, 30.0, 60.0, 120.0],
    registry=registry,
)

skeptic_rejection_rate = Gauge(
    "skeptic_rejection_rate",
    "Rate of ideas rejected by skeptic",
    ["rejection_reason"],
    registry=registry,
)

tavily_search_count = Counter(
    "tavily_search_count",
    "Number of Tavily API calls",
    ["agent", "status"],
    registry=registry,
)

gtm_confidence_score = Histogram(
    "gtm_confidence_score",
    "Confidence scores for GTM plans",
    buckets=[0.3, 0.5, 0.7, 0.8, 0.9, 0.95],
    registry=registry,
)

# Reuse existing LLM metrics (no changes needed)
# llm_tokens_used, llm_api_cost, etc.
```

**Frontend Metrics Display**:

```javascript
// Real-time metrics footer
<MetricsDashboard>
  <MetricCard label="Cost" value="$0.012" />
  <MetricCard label="Duration" value="18.3s" />
  <MetricCard label="Confidence" value="0.87" />
  <MetricCard label="Tokens Used" value="3,421" />
  <MetricCard label="Loops" value="2" />
</MetricsDashboard>
```

### Phase 3: Tool Integration

#### 3.1 Tavily Search Tool

```python
# src/tools/tavily.py
from src.tools.base import BaseTool, ToolInput, ToolOutput
from src.observability.decorators import trace_tool
import httpx

class TavilySearchTool(BaseTool):
    """Tavily AI-optimized search tool."""

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.client = httpx.AsyncClient()

    @trace_tool
    async def execute(self, input: ToolInput) -> ToolOutput:
        query = input.parameters.get("query")
        max_results = input.parameters.get("max_results", 5)

        # Call Tavily API
        response = await self.client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced"
            }
        )

        results = response.json()

        return ToolOutput(
            success=True,
            result=results,
            metadata={"query": query, "count": len(results.get("results", []))}
        )
```

**Observability**: Same `@trace_tool` decorator provides automatic tracing, logging, and metrics.

#### 3.2 RAG Knowledge Base Tool

```python
# src/tools/marketing_rag.py
from src.tools.base import BaseTool
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

class MarketingRAGTool(BaseTool):
    """RAG tool for marketing frameworks."""

    def __init__(self, knowledge_base_path: str):
        super().__init__()
        # Load FAISS vector store
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.load_local(knowledge_base_path, self.embeddings)

    @trace_tool
    async def execute(self, input: ToolInput) -> ToolOutput:
        query = input.parameters.get("query")

        # Semantic search
        docs = await self.vectorstore.asimilarity_search(query, k=3)

        return ToolOutput(
            success=True,
            result={
                "articles": [doc.page_content for doc in docs],
                "sources": [doc.metadata for doc in docs]
            },
            metadata={"query": query, "results_count": len(docs)}
        )
```

**Observability**: Automatic RAG metrics:
- `tool_call_count{tool="marketing_rag"}`
- `tool_call_duration_seconds{tool="marketing_rag"}`
- Traces show which documents were retrieved

### Phase 4: Evaluation Framework

#### 4.1 Reuse Existing DeepEval Structure

**Current**: `tests/evaluation/` with routing accuracy, tool usage metrics
**Target**: Startup analysis quality metrics

```python
# tests/evaluation/metrics/gtm_quality.py
from deepeval.metrics import BaseMetric

class GTMQualityMetric(BaseMetric):
    """Evaluate GTM plan quality."""

    def __init__(self):
        self.name = "GTM Quality"
        self.threshold = 0.7

    async def measure(self, test_case):
        # LLM-as-judge to score GTM plan
        score = await self.llm_judge(
            plan=test_case.actual_output,
            criteria=[
                "Is the target market clearly defined?",
                "Are competitive advantages identified?",
                "Is the pricing strategy realistic?",
                "Are distribution channels specified?"
            ]
        )
        return score
```

```python
# tests/evaluation/test_analysis_quality.py
@pytest.mark.evaluation
async def test_gtm_quality():
    """Test GTM plan quality across test cases."""

    test_cases = load_test_cases("tests/evaluation/datasets/startup_ideas.json")

    for case in test_cases:
        result = await analyze_startup(case.business_idea)

        # Evaluate with DeepEval
        metric = GTMQualityMetric()
        score = await metric.measure(result)

        assert score > 0.7, f"GTM quality too low: {score}"
```

**Observability Integration**:
- Evaluation runs are traced
- Metrics exported: `evaluation_score{metric="gtm_quality", case="uber_for_dogs"}`
- Results logged for analysis

---

## Project Structure

```
startup_analyzer/
├── config/
│   ├── observability.py          # [KEEP] OpenTelemetry setup
│   ├── logging_config.py          # [KEEP] Structlog config
│   └── settings.py                # [UPDATE] Add Tavily, LangSmith keys
│
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analysis.py        # [NEW] Analysis endpoints with SSE
│   │   │   ├── health.py          # [KEEP]
│   │   │   └── metrics.py         # [KEEP]
│   │   └── middleware/            # [KEEP] All middleware
│   │
│   ├── startup_analyzer/          # [NEW] Business logic
│   │   ├── agents/
│   │   │   ├── analyst.py
│   │   │   ├── researcher.py
│   │   │   ├── skeptic.py
│   │   │   └── strategist.py
│   │   ├── prompts/               # Agent prompts
│   │   ├── state.py               # AnalysisState dataclass
│   │   ├── graph.py               # LangGraph DCG
│   │   └── streaming.py           # SSE event generation
│   │
│   ├── tools/
│   │   ├── base.py                # [KEEP]
│   │   ├── tavily.py              # [NEW] Tavily search
│   │   ├── marketing_rag.py       # [NEW] RAG for marketing frameworks
│   │   └── registry.py            # [UPDATE] Register new tools
│   │
│   ├── observability/             # [KEEP ALL - NO CHANGES]
│   │   ├── tracer.py
│   │   ├── logger.py
│   │   ├── metrics.py             # [ADD] New metrics for startup analysis
│   │   ├── decorators.py
│   │   ├── context.py
│   │   └── langsmith.py           # [NEW] LangSmith integration
│   │
│   └── llm/
│       ├── client.py              # [UPDATE] Use real Claude/GPT client
│       ├── token_counter.py       # [KEEP]
│       └── retry.py               # [KEEP]
│
├── tests/
│   ├── evaluation/
│   │   ├── datasets/
│   │   │   └── startup_ideas.json # [NEW] Test cases
│   │   ├── metrics/
│   │   │   ├── gtm_quality.py     # [NEW]
│   │   │   └── skeptic_accuracy.py # [NEW]
│   │   └── test_analysis_eval.py  # [NEW]
│   │
│   └── integration/
│       └── test_analysis_workflow.py  # [NEW]
│
├── frontend/                       # [NEW] React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnalysisStream.tsx
│   │   │   ├── TraceViewer.tsx
│   │   │   └── MetricsDashboard.tsx
│   │   └── hooks/
│   │       └── useAnalysisStream.ts
│   └── vite.config.ts
│
├── docs/
│   ├── observability_guide.md     # [UPDATE] Add startup-specific examples
│   ├── architecture.md            # [UPDATE] New architecture diagram
│   └── deployment_guide.md        # [NEW] Railway deployment
│
└── IMPLEMENTATION_PROPOSAL.md     # [THIS FILE]
```

---

## Observability Mapping

### What STAYS (No Changes)

| Component | Current Use Case | New Use Case | Status |
|-----------|-----------------|--------------|--------|
| **Tracer** | Traces ticket workflow | Traces analysis workflow | ✅ Same code |
| **Logger** | Logs agent decisions | Logs agent decisions | ✅ Same code |
| **Metrics** | Agent performance | Agent performance | ✅ Same patterns |
| **Decorators** | `@trace_agent`, `@trace_tool` | `@trace_agent`, `@trace_tool` | ✅ Same decorators |
| **Context Mgmt** | Correlation IDs | Correlation IDs | ✅ Same system |
| **Prometheus** | `/metrics` endpoint | `/metrics` endpoint | ✅ Same export |

### What CHANGES (Extensions)

| Component | Change Type | Reason |
|-----------|------------|--------|
| **Metrics** | Add new metrics | Track loops, Tavily calls, GTM confidence |
| **Streaming** | Add SSE events | Real-time UX updates |
| **LangSmith** | Add integration | User-facing trace viewer |
| **State Schema** | New dataclasses | Different business domain |

### Observability Flow Comparison

#### Before (AgentLand):
```
User Request → Middleware (CID) → Triage → Specialist → Response
                    ↓
     [Trace] [Log] [Metric] at every step
```

#### After (Startup Analyzer):
```
User Request → Middleware (CID) → Analyst → Researcher → Skeptic ⟲ → Strategist → Response
                    ↓                                        ↑      ↓
     [Trace] [Log] [Metric] + [SSE Stream] + [LangSmith]    Loop
```

**Key Insight**: Observability foundation is identical. We're just adding streaming layers on top.

---

## Implementation Phases & Timeline

### Phase 1: Foundation (Week 1)
- [ ] Update state schema for analysis domain
- [ ] Implement LangGraph DCG with loop support
- [ ] Create 4 new agents (Analyst, Researcher, Skeptic, Strategist)
- [ ] Write agent prompts
- **Observability**: Works immediately (reuse existing decorators)

### Phase 2: Tools & LLM (Week 1-2)
- [ ] Integrate Tavily API tool
- [ ] Build RAG tool with FAISS
- [ ] Load marketing frameworks into vector store
- [ ] Switch to real LLM client (Claude/GPT)
- **Observability**: Automatic via `@trace_tool`

### Phase 3: Real-Time Streaming (Week 2)
- [ ] Implement SSE endpoint
- [ ] Create streaming callback handler
- [ ] Build React frontend with real-time status
- [ ] Add metrics dashboard component
- **Observability**: Add SSE layer, keep existing traces

### Phase 4: LangSmith & Evaluation (Week 3)
- [ ] Integrate LangSmith tracing
- [ ] Embed trace viewer in frontend
- [ ] Create evaluation datasets
- [ ] Implement GTM quality metrics with DeepEval
- **Observability**: Dual tracing (OTEL + LangSmith)

### Phase 5: Deployment (Week 3-4)
- [ ] Dockerize application
- [ ] Set up Railway deployment
- [ ] Configure environment variables
- [ ] Deploy frontend and backend
- [ ] Set up Prometheus + Grafana monitoring
- **Observability**: Production monitoring stack

---

## Cost Optimization

### Infrastructure Costs
- **Railway**: ~$5/month (Hobby tier, 500 hours)
- **Supabase**: Free tier (if needed for session storage)
- **LangSmith**: Free tier (5K traces/month)

### API Costs
- **LLM**: GPT-4o-mini (~$0.15/MTok input, $0.60/MTok output)
  - Estimate: ~4K tokens/analysis = $0.003/run
  - $10 → 3,333 analyses
- **Tavily**: $0.01/search
  - Estimate: 5 searches/analysis = $0.05/run
  - $10 → 200 analyses
- **Total per analysis**: ~$0.053

### Cost Tracking
All costs tracked via existing metrics:
- `llm_api_cost_dollars{agent="analyst"}`
- `tavily_search_count{agent="researcher"}`
- Real-time dashboard shows cumulative costs

---

## Migration Strategy

### Option A: In-Place Migration (Recommended)
1. Keep existing AgentLand code in `src/agents/` (rename to `src/agentland/`)
2. Add new Startup Analyzer code in `src/startup_analyzer/`
3. Share observability layer (`src/observability/`)
4. Run both systems side-by-side initially
5. Deprecate AgentLand code once comfortable

**Benefits**:
- Low risk (existing code untouched)
- Can compare implementations
- Reuse all observability infrastructure

### Option B: Clean Slate
1. Archive AgentLand code to separate branch
2. Delete old agents/orchestration
3. Build Startup Analyzer from scratch
4. Reuse only observability layer

**Benefits**:
- Cleaner codebase
- No legacy code

**Recommendation**: Option A for safety and learning.

---

## Success Metrics

### Technical Metrics
- ✅ All traces have correlation IDs
- ✅ Zero observability-related errors
- ✅ 100% of agents/tools traced
- ✅ <100ms latency for SSE events
- ✅ LangSmith traces visible in <5 seconds

### Business Metrics
- ✅ Average analysis time <30 seconds
- ✅ Skeptic rejection rate 20-40%
- ✅ GTM confidence scores >0.7
- ✅ Cost per analysis <$0.10
- ✅ Loop iterations average <2

### User Experience Metrics
- ✅ Real-time status updates visible
- ✅ Trace viewer loads successfully
- ✅ Metrics dashboard updates live
- ✅ Frontend responsive on mobile

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LangGraph loops infinite | High | Max loop counter in state |
| Tavily API rate limits | Medium | Implement caching, retry logic |
| LLM API costs spike | High | Budget alerts via Prometheus |
| SSE connection drops | Medium | Automatic reconnection logic |
| Trace viewer doesn't load | Low | Fallback to raw JSON trace |

---

## Questions for Clarification

Before proceeding, please confirm:

1. **LLM Choice**: Claude 3.5 Sonnet or GPT-4o-mini? (Impacts cost/quality tradeoff)
2. **Frontend**: Should I implement the React frontend, or backend API only?
3. **Deployment**: Railway preferred, or other platform (Vercel, Fly.io)?
4. **RAG Data**: Do you have marketing framework documents, or should I create sample ones?
5. **Evaluation**: Should I build the evaluation framework immediately, or after basic implementation?
6. **Migration**: Option A (side-by-side) or Option B (clean slate)?

---

## Conclusion

This proposal demonstrates how the existing AgentLand observability infrastructure can be directly reused for the Startup Analyzer with minimal changes. The three-pillar observability approach (Traces, Logs, Metrics) remains intact, with enhancements for real-time streaming and user-facing visualizations.

**Key Takeaway**: We're not rebuilding observability—we're extending it. The proven patterns (decorators, correlation IDs, automatic tracing) transfer seamlessly to the new domain.

**Next Steps**: Upon approval, I'll begin Phase 1 implementation starting with state schema and LangGraph DCG setup.
