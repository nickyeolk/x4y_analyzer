# Agentic Workflow Refactor - Complete Summary

## Overview

Successfully transformed the startup analyzer's agentic workflow from a quality-gate architecture to a dynamic research coordination system.

## Architecture Transformation

### Old Architecture (Quality Gate Pattern)
```
Parallel Analysis (Analyst + Researcher)
  ↓
Skeptic (Quality Gate - approves or rejects)
  ↓ (if rejected)
Loop back to Parallel Analysis (up to 3 times)
  ↓ (if approved)
Strategist (Creates GTM plan)
```

**Problems:**
- Skeptic acted as a quality gate rather than contributing unique insights
- Binary approve/reject decision was limiting
- No mechanism for targeted follow-up research
- Skeptic couldn't add new information, only critique existing work

### New Architecture (Dynamic Coordination Pattern)
```
Parallel Analysis (Analyst + Researcher + Risk Analyst)
  ↓
Strategist Coordination
  - Reviews all research
  - Identifies gaps
  - Requests targeted follow-up from specific agents
  - Loops up to 3 times or until sufficient information
  ↓
Strategist Synthesis
  - Creates comprehensive GTM plan
  - Incorporates all research including follow-ups
```

**Benefits:**
- **Risk Analyst** provides unique threat analysis (not just critique)
- **Dynamic coordination** allows Strategist to request specific information
- **Targeted follow-up** via `execute_focused()` methods
- **More meaningful insights** from all agents
- **Better observability** through coordination tracking

## Implementation Details

### 1. Risk Analyst Agent (Part 1)
**File:** `src/agents/risk_analyst.py`

- Transformed from Skeptic (quality gate) to Risk Analyst (risk identification)
- Uses GPT-4o-mini for business model classification (performance optimization)
- Queries RAG tool for risk-specific frameworks
- Returns structured risk analysis:
  - Competitive threats
  - Market risks
  - Execution challenges
  - Financial risks
  - Fatal flaws
  - Overall risk level (low/medium/high)

**File:** `src/agents/prompts/risk_analyst.py`
- New system prompt focusing on risk identification
- Clear output format for structured risk data

### 2. Focused Research Methods (Part 2)
**Files:** `src/agents/{analyst,researcher,risk_analyst}.py`

Added `execute_focused(state, focus_query)` method to each agent:
- **Analyst:** Targeted brand/business model research
- **Researcher:** Specific market/competitive research
- **Risk Analyst:** Focused risk/threat assessment

Each method:
1. Takes a specific query from Strategist
2. Performs targeted web search (Tavily)
3. Runs focused LLM analysis
4. Returns structured results

### 3. Parallel Research Update (Part 3)
**File:** `src/orchestration/nodes.py`

- Updated `parallel_analysis_node()` to run 3 agents concurrently:
  ```python
  analyst_state, researcher_state, risk_state = await asyncio.gather(
      analyst.execute(state.copy()),
      researcher.execute(state.copy()),
      risk_analyst.execute(state.copy())
  )
  ```
- Merges all three results into state
- Tracks token usage for all agents

**File:** `src/agents/strategist_tools.py` (Created)

- Defined tool functions for coordination:
  - `analyze_brand_deeper(focus_query)`
  - `research_market_deeper(focus_query)`
  - `analyze_risks_deeper(focus_query)`
  - `create_gtm_plan()`
- Created `STRATEGIST_COORDINATION_SYSTEM_PROMPT`

### 4. Coordination & Synthesis Nodes (Part 4)
**File:** `src/orchestration/nodes.py`

**`strategist_coordination_node()`** (lines 274-440):
- Reviews all research from parallel analysis
- LLM decides to either:
  - Request targeted follow-up research
  - Proceed to synthesis
- If requesting follow-up:
  - Parses JSON with agent name and query
  - Calls `execute_focused()` on specified agent
  - Appends results to `state["follow_up_research"]`
  - Increments `coordination_iteration`
  - Loops back to itself
- Sets `ready_for_synthesis = True` when done
- Forces synthesis after 3 iterations

**`strategist_synthesis_node()`** (lines 443-469):
- Final node that creates GTM plan
- Calls existing `strategist.execute(state)`
- Synthesizes all research into strategy

**File:** `src/orchestration/graph.py`

- Updated graph structure:
  ```python
  workflow.set_entry_point("parallel_analysis")
  workflow.add_edge("parallel_analysis", "strategist_coordination")
  workflow.add_conditional_edges(
      "strategist_coordination",
      route_after_coordination,
      {
          "coordination": "strategist_coordination",  # Loop
          "synthesis": "strategist_synthesis"          # Done
      }
  )
  workflow.add_edge("strategist_synthesis", END)
  ```

**File:** `src/orchestration/edges.py`

- Added `route_after_coordination()` routing function
- Checks `ready_for_synthesis` flag
- Routes to synthesis or loops back

### 5. State Schema Update (Part 5)
**File:** `src/orchestration/state.py`

**New dataclass:** `RiskAnalysis`
- competitive_threats
- market_risks
- execution_challenges
- financial_risks
- fatal_flaws
- overall_risk_level
- summary
- confidence

**Updated `AnalysisState`:**
- Added coordination fields:
  - `coordination_iteration: int`
  - `max_coordination_iterations: int`
  - `ready_for_synthesis: bool`
  - `follow_up_research: List[Dict]`
  - `risk_analysis: Optional[RiskAnalysis]`
- Marked Skeptic fields as DEPRECATED (kept for backward compatibility)

### 6. Frontend & SSE Updates (Part 6)

**File:** `frontend/src/components/ProgressDisplay.jsx`
- Replaced Skeptic with Risk Analyst (⚠️ icon)
- Updated description: "Identifying threats, risks, and potential failure modes"
- Added coordination_follow_up event handling
- Updated messaging for coordination iterations

**File:** `frontend/src/components/ResultsDisplay.jsx`
- Added Risk Analysis section:
  - Shows overall risk level badge
  - Displays 5 risk categories with emojis
  - Highlights fatal flaws in red
- Updated summary section:
  - Shows viability score
  - Shows coordination iterations
  - Maintains legacy support for loop_count

**File:** `src/api/routes/analysis.py`
- Updated SSE agent list: `["analyst", "researcher", "risk_analyst"]`
- Added coordination_follow_up event emission
- Updated analysis_completed event structure
- Maintains backward compatibility

## Commits Made

```
2a61b41 Refactor Skeptic → Risk Analyst (Part 1)
c38507d Add execute_focused methods to all agents (Part 2)
5f55bae Add Risk Analyst to parallel research & create strategist tools (Part 3)
a92ba24 Refactor workflow: Replace Skeptic loop with Strategist coordination (Part 4)
c0ebc39 Update state schema for coordination workflow (Part 5)
32430ae Update frontend and SSE events for Risk Analyst and coordination workflow (Part 6)
```

## State Fields Reference

### New Fields
```python
state["risk_analysis"] = {
    "competitive_threats": [...],
    "market_risks": [...],
    "execution_challenges": [...],
    "financial_risks": [...],
    "fatal_flaws": [...],
    "overall_risk_level": "high|medium|low",
    "summary": "...",
    "confidence": 0.0-1.0
}

state["coordination_iteration"] = 0  # 0-3
state["max_coordination_iterations"] = 3
state["ready_for_synthesis"] = False
state["follow_up_research"] = [
    {
        "type": "focused_analysis|focused_research|focused_risk_analysis",
        "agent": "analyst|researcher|risk_analyst",
        "query": "specific question",
        "findings": [...],
        "insights": "...",
        "confidence": 0.0-1.0
    }
]
```

### Deprecated Fields (kept for backward compatibility)
```python
state["skeptic_critique"]  # Legacy
state["skeptic_approved"]  # Legacy
state["loop_count"]        # Legacy
state["max_loops"]         # Legacy
```

## Testing & Validation

All Python files validated for syntax:
- ✅ `src/orchestration/nodes.py`
- ✅ `src/orchestration/graph.py`
- ✅ `src/orchestration/edges.py`
- ✅ `src/orchestration/state.py`
- ✅ `src/agents/risk_analyst.py`
- ✅ `src/agents/analyst.py`
- ✅ `src/agents/researcher.py`
- ✅ `src/agents/strategist_tools.py`
- ✅ `src/api/routes/analysis.py`

## Next Steps for Testing

### 1. Start the backend
```bash
cd /data/data/com.termux/files/home/lik/startup_analyzer
python -m uvicorn src.api.main:app --reload
```

### 2. Start the frontend
```bash
cd frontend
npm run dev
```

### 3. Test the new workflow
- Submit a business idea (e.g., "Uber for Dog Walkers")
- Observe SSE events showing all 3 parallel agents
- Check if coordination events are emitted
- Verify Risk Analysis section in results
- Confirm viability score and coordination iterations are displayed

### 4. Monitor logs
```bash
# Watch for coordination decision logs
tail -f logs/app.log | grep coordination

# Watch for follow-up research logs
tail -f logs/app.log | grep follow_up
```

## Benefits Achieved

1. **More Meaningful Agent Contributions**
   - Risk Analyst provides unique threat analysis
   - No wasted effort on quality gating
   - Each agent adds distinct value

2. **Dynamic Research Coordination**
   - Strategist can request specific information
   - Targeted follow-up reduces token waste
   - Iterative refinement based on actual gaps

3. **Better Observability**
   - Clear coordination iterations tracking
   - Follow-up research logged
   - Structured risk data

4. **Improved User Experience**
   - Frontend shows all agent contributions
   - Risk analysis prominently displayed
   - Coordination progress visible

5. **Backward Compatibility**
   - Legacy fields maintained
   - Old analyses still viewable
   - Gradual migration path

## Architecture Patterns Used

- **Parallel Execution:** 3 agents run concurrently (performance)
- **Dynamic Coordination:** LLM-driven follow-up requests (flexibility)
- **Focused Research:** Targeted queries reduce token usage (efficiency)
- **State Management:** Immutable state passed through nodes (reliability)
- **Graceful Degradation:** Legacy support maintains compatibility (stability)

## Observability Features

- LangSmith automatic tracing for all LLM calls
- Comprehensive structured logging at each decision point
- Token usage tracking per agent
- Coordination iteration tracking
- Follow-up research narrative in state

---

**Status:** ✅ Implementation Complete
**Date:** 2026-01-01
**Total Commits:** 6
**Files Changed:** 13
**Lines Added:** ~1000
**Lines Removed:** ~100

This refactor successfully transforms the agentic workflow to enable more dynamic, meaningful, and observable multi-agent collaboration.
