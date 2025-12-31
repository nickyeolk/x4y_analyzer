# Startup Analyzer - Quick Start Guide

## What's Been Built (50% Complete)

### ✅ Core Infrastructure
1. **Configuration System** - OpenRouter, Tavily, LangSmith, RAG settings
2. **State Management** - Complete AnalysisState with loop support
3. **OpenRouter LLM Client** - GPT-4o integration with full observability
4. **Tavily Search Tool** - AI-optimized web search
5. **Marketing RAG Tool** - FAISS-based semantic search
6. **All Agent Prompts** - 4 specialized system prompts
7. **Analyst Agent** - Complete implementation
8. **Observability Layer** - All tracing, logging, metrics preserved

### 📁 Project Structure

```
startup_analyzer/
├── config/settings.py [✅]
├── requirements.txt [✅]
├── src/
│   ├── agents/
│   │   ├── base.py [✅]
│   │   ├── analyst.py [✅]
│   │   ├── researcher.py [⏳]
│   │   ├── skeptic.py [⏳]
│   │   ├── strategist.py [⏳]
│   │   └── prompts/ [✅ ALL]
│   ├── orchestration/
│   │   ├── state.py [✅]
│   │   ├── nodes.py [⏳]
│   │   ├── edges.py [⏳]
│   │   └── graph.py [⏳]
│   ├── tools/
│   │   ├── tavily.py [✅]
│   │   └── marketing_rag.py [✅]
│   ├── llm/
│   │   └── openrouter_client.py [✅]
│   ├── api/
│   │   └── routes/analysis.py [⏳]
│   └── observability/ [✅ ALL]
├── scripts/
│   └── build_vector_store.py [✅]
└── frontend/ [⏳]
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file:

```bash
# LLM Provider
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_MODEL=openai/gpt-4o

# Tools
TAVILY_API_KEY=your_tavily_key_here

# LangSmith (optional)
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=startup-analyzer
LANGCHAIN_TRACING_V2=true

# Observability
OTEL_ENABLED=true
OTEL_EXPORTER=console

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

### 3. Set Up RAG Knowledge Base

#### Create Directory Structure:

```bash
mkdir -p data/knowledge_base
mkdir -p data/vector_store
```

#### Add Marketing Framework Documents

Place your `.txt` files in `data/knowledge_base/`. Example documents:

**`data/knowledge_base/marketing_pitfalls.txt`:**
```
Common Marketing Pitfalls for Startups

1. Targeting Too Broad an Audience
Many startups fail by trying to appeal to everyone...

2. Ignoring Market Saturation
Entering an oversaturated market without clear differentiation...

3. Underestimating Customer Acquisition Costs
...
```

**`data/knowledge_base/gtm_frameworks.txt`:**
```
Go-To-Market Strategy Frameworks

## The Lean Startup Approach
...

## Product-Led Growth
...

## Enterprise Sales Playbook
...
```

**`data/knowledge_base/competitive_analysis.txt`:**
```
Competitive Analysis Best Practices

1. Identify Direct and Indirect Competitors
...

2. SWOT Analysis Framework
...
```

#### Build Vector Store:

```bash
python scripts/build_vector_store.py
```

---

## What Still Needs Implementation

### Priority 1: Complete Backend (Critical Path)

#### A. Finish Agent Implementations

Create these files following the pattern in `analyst.py`:

**`src/agents/researcher.py`:**
- Use `RESEARCHER_SYSTEM_PROMPT`
- Call Tavily tool to research the "Y" market
- Parse JSON response into `MarketResearch` dataclass
- Update state with `researcher_findings`

**`src/agents/skeptic.py`:**
- Use `SKEPTIC_SYSTEM_PROMPT`
- Review `analyst_insights` and `researcher_findings`
- Use RAG tool to consult marketing frameworks
- Return `Critique` with `approved` boolean
- If not approved, set `loop_back_reason`

**`src/agents/strategist.py`:**
- Use `STRATEGIST_SYSTEM_PROMPT`
- Synthesize all insights into `GTMPlan`
- Calculate `viability_score`
- Generate marketing hooks for LinkedIn

#### B. Implement LangGraph Workflow

**`src/orchestration/graph.py`:**

```python
from langgraph.graph import StateGraph, END
from src.orchestration.state import AnalysisState

def create_analysis_graph():
    workflow = StateGraph(dict)  # Use dict for state

    # Add nodes
    from src.agents.analyst import AnalystAgent
    from src.agents.researcher import ResearcherAgent
    from src.agents.skeptic import SkepticAgent
    from src.agents.strategist import StrategistAgent

    analyst = AnalystAgent()
    researcher = ResearcherAgent()
    skeptic = SkepticAgent()
    strategist = StrategistAgent()

    workflow.add_node("analyst", analyst.execute)
    workflow.add_node("researcher", researcher.execute)
    workflow.add_node("skeptic", skeptic.execute)
    workflow.add_node("strategist", strategist.execute)

    # Define flow
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "researcher")
    workflow.add_edge("researcher", "skeptic")

    # Conditional routing after skeptic
    def route_after_skeptic(state):
        critique = state.get("skeptic_critique", {})
        loop_count = state.get("loop_count", 0)
        max_loops = state.get("max_loops", 3)

        # Check if approved or max loops reached
        if critique.get("approved") or loop_count >= max_loops:
            return "strategist"
        else:
            # Loop back
            state["loop_count"] = loop_count + 1
            return "analyst"

    workflow.add_conditional_edges(
        "skeptic",
        route_after_skeptic,
        {
            "analyst": "analyst",
            "strategist": "strategist",
        }
    )

    workflow.add_edge("strategist", END)

    return workflow.compile()
```

**`src/orchestration/nodes.py` and `edges.py`:**
- Simple wrappers if needed, or incorporate directly into graph.py

#### C. Create API Routes

**`src/api/routes/analysis.py`:**

```python
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from src.orchestration.graph import create_analysis_graph
from src.orchestration.state import create_initial_state

router = APIRouter()

@router.post("/analyze")
async def analyze_startup(x_brand: str, y_market: str):
    async def event_generator():
        analysis_id = f"A-{uuid.uuid4().hex[:8]}"
        correlation_id = f"CID-{uuid.uuid4().hex[:8]}"

        # Create initial state
        state = create_initial_state(
            analysis_id=analysis_id,
            correlation_id=correlation_id,
            x_brand=x_brand,
            y_market=y_market,
        )

        # Get workflow
        graph = create_analysis_graph()

        # Stream events
        async for event in graph.astream_events(state):
            yield {
                "event": "update",
                "data": json.dumps(event)
            }

    return EventSourceResponse(event_generator())
```

### Priority 2: Frontend

Create React app in `frontend/`:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install tailwindcss @shadcn/ui sse
```

**Key Components:**
- Input form for "X for Y" idea
- EventSource to consume SSE
- Real-time agent status display
- Metrics dashboard (cost, duration, loops)
- Final GTM plan display

### Priority 3: Evaluation & Documentation

- Create test datasets in `tests/evaluation/datasets/`
- Implement DeepEval metrics
- Update README.md with complete instructions
- Add deployment guide for Railway

---

## Testing the Implementation

### 1. Test Individual Components

```python
# Test Tavily tool
from src.tools.tavily import get_tavily_tool
from src.tools.base import ToolInput

tool = get_tavily_tool()
result = await tool.execute(ToolInput(
    tool_name="tavily",
    parameters={"query": "Uber business model"}
))
print(result.result)
```

### 2. Test Analyst Agent

```python
from src.agents.analyst import AnalystAgent
from src.orchestration.state import create_initial_state

analyst = AnalystAgent()
state = create_initial_state(
    analysis_id="test-1",
    correlation_id="test-cid",
    x_brand="Uber",
    y_market="Dog Walkers"
)

result = await analyst.execute(state)
print(result["analyst_insights"])
```

### 3. Test Full Workflow (once graph is complete)

```python
from src.orchestration.graph import create_analysis_graph

graph = create_analysis_graph()
state = create_initial_state(...)

final_state = await graph.ainvoke(state)
print(final_state["strategist_plan"])
```

---

## Observability in Action

### View Traces

All agents automatically create spans:

```bash
# Run with console exporter
OTEL_EXPORTER=console python -m src.api.main
```

You'll see:
```
{
  "name": "agent.analyst",
  "attributes": {
    "agent.name": "analyst",
    "agent.decision": "brand_analyzed",
    "agent.confidence": 0.85
  },
  "duration_ms": 1234
}
```

### View Metrics

```bash
curl http://localhost:8000/metrics | grep analysis
```

Output:
```
analysis_duration_seconds_bucket{has_loops="true",le="30.0"} 5
tool_call_count{tool="tavily_search",status="success"} 12
llm_tokens_used{model="openai/gpt-4o",type="prompt"} 15234
```

### View Logs

```bash
# Structured logs with correlation IDs
tail -f logs/app.log | jq 'select(.event == "analyst_completed")'
```

---

## Key Files Reference

### Agent Implementation Pattern

```python
from src.agents.base import BaseAgent
from src.observability.decorators import trace_agent

class YourAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="your_agent")
        self.llm_client = get_llm_client()
        self.tool = get_your_tool()

    @trace_agent
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Extract inputs from state
        # 2. Call tools if needed
        # 3. Call LLM with system prompt
        # 4. Parse JSON response
        # 5. Update state
        # 6. Log decision
        # 7. Return updated state
        pass
```

### State Update Pattern

```python
# Always update these fields
state["your_agent_result"] = {...}
state["agent_interactions"].append(interaction.__dict__)
state["metadata"]["token_usage"]["your_agent"] = {...}
```

### Tool Call Pattern

```python
from src.tools.base import ToolInput

result = await self.tool.execute(
    ToolInput(
        tool_name="tool_name",
        parameters={"param": "value"}
    )
)

if result.success:
    data = result.result
else:
    error = result.error
```

---

## Troubleshooting

### "OPENROUTER_API_KEY not set"
- Add to `.env` file
- Restart application

### "Vector store not found"
- Run `python scripts/build_vector_store.py`
- Ensure documents exist in `data/knowledge_base/`

### "Tavily API error"
- Check TAVILY_API_KEY in `.env`
- Verify API quota

### JSON parsing errors in agents
- Check LLM response format
- Add fallback parsing logic
- Log raw response for debugging

---

## Next Steps

1. **Complete remaining 3 agents** (Researcher, Skeptic, Strategist)
2. **Implement LangGraph workflow** with loop support
3. **Create API endpoint** with SSE streaming
4. **Build React frontend**
5. **Add LangSmith integration**
6. **Create evaluation framework**
7. **Deploy to Railway**

---

## Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **OpenRouter API**: https://openrouter.ai/docs
- **Tavily API**: https://tavily.com/docs
- **LangSmith**: https://smith.langchain.com/

---

**Current Status: ~50% Complete**
**Estimated Time to Complete: 4-6 hours of focused development**

All observability is already working. Focus on building the remaining agents and workflow logic.
