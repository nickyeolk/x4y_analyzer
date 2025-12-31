# Feedback Loop Implementation

## Problem Identified

The Skeptic agent could reject analysis and trigger a loop back to Analyst/Researcher, but those agents **did not receive or use the Skeptic's feedback**. They would simply re-run with the same context, producing similar results.

## Solution Implemented

Both Analyst and Researcher agents now:
1. **Detect loop-back scenarios** - Check if `skeptic_critique` exists in state
2. **Read the Skeptic's feedback** - Extract concerns, suggestions, fatal flaws
3. **Adjust their behavior** - Search more deeply and specifically
4. **Include feedback in LLM prompts** - Explicitly tell the LLM what to address

---

## Changes to Analyst Agent

### Detection Logic
```python
skeptic_critique = state.get("skeptic_critique")
is_loop_back = skeptic_critique is not None and iteration > 0
```

### Enhanced Search on Loop-Back
- **First run:** Generic query like `"Uber company business model key features"`
- **Loop-back:** Focused query incorporating skeptic's concerns
  ```python
  concerns = skeptic_critique.get("concerns", [])
  suggestions = skeptic_critique.get("suggestions", [])
  focus_areas = " ".join(concerns[:2] + suggestions[:2])
  search_query = f"{x_brand} {focus_areas} business model competitive advantages"
  ```
- **More results:** 7 results instead of 5
- **More context:** Uses 5 results instead of 3 for analysis

### Enhanced Prompt
The LLM prompt now includes:
```
⚠️ PREVIOUS ITERATION FEEDBACK - CRITICAL TO ADDRESS:

The Skeptic rejected the previous analysis for the following reasons:
Rejection Reason: {loop_back_reason}

Specific Concerns Identified:
- {concern 1}
- {concern 2}
...

Fatal Flaws Found:
- {flaw 1}
...

Suggestions for Improvement:
- {suggestion 1}
...

Iteration: 2 of 3

INSTRUCTION: Address ALL of the above concerns. Be MORE specific, MORE detailed,
and MORE thorough than the previous iteration.
```

---

## Changes to Researcher Agent

### Detection Logic
Same as Analyst - detects loop-back scenarios

### Enhanced Search on Loop-Back
**Market Search:**
- Adjusts query to focus on skeptic's concerns
- Increases results from 5 to 7
- Always uses "advanced" search depth

**Competitor Search:**
- Increases results from 5 to 7
- **Upgrades search depth** from "basic" to "advanced" on loop-back
- Uses 5 results instead of 3 for analysis

### Enhanced Prompt
Similar feedback structure as Analyst, with specific instructions:
```
INSTRUCTION: Address ALL concerns. Be MORE specific about competitive threats,
MORE detailed about market saturation, and MORE thorough about barriers to entry.
```

---

## How the Loop Now Works

### Iteration 1 (Initial Run)
```
Analyst → Searches broadly for "Uber business model"
        → Produces initial brand DNA analysis

Researcher → Searches broadly for "Dog Walking market"
           → Produces initial market research

Skeptic → Reviews both analyses
        → Finds issues: "Competitive analysis too shallow"
        → REJECTS with specific concerns
        → Sets loop_back_reason = "Competitive threats underestimated"
```

### Iteration 2 (Loop Back - NOW IMPROVED!)
```
Analyst → Detects loop_back = True
        → Searches specifically: "Uber competitive threats underestimated business model"
        → Gets 7 results, uses 5 for context
        → LLM sees skeptic's feedback in prompt
        → Produces DEEPER analysis addressing specific concerns

Researcher → Detects loop_back = True
           → Searches with "advanced" depth
           → Focuses on "competitive threats barriers saturation"
           → Gets 7 results, uses 5 for context
           → LLM sees skeptic's feedback in prompt
           → Produces MORE THOROUGH market analysis

Skeptic → Reviews IMPROVED analyses
        → Hopefully approves this time
        → If still not good enough, can loop again (up to max_loops)
```

---

## Benefits

✅ **Agents actually improve** - Each iteration is genuinely different and better
✅ **Skeptic's feedback drives refinement** - Concerns directly influence next analysis
✅ **More targeted search** - Queries focus on identified gaps
✅ **Deeper research** - More results and advanced search on loop-back
✅ **Explicit instructions** - LLM knows exactly what to fix
✅ **Observable** - Logs show `is_loop_back` and focused queries
✅ **Safety preserved** - Max loops still prevents infinite cycles

---

## Before vs After

### Before
```
Loop 1: Generic analysis
  ↓
Skeptic rejects: "Too shallow"
  ↓
Loop 2: Same generic analysis (likely same result)
  ↓
Skeptic rejects again
  ↓
Loop 3: Force approve (wasted loops)
```

### After
```
Loop 1: Generic analysis
  ↓
Skeptic rejects: "Too shallow - need more on competitors X, Y"
  ↓
Loop 2: Focused search on X, Y
        Deeper analysis
        Addresses specific concerns
  ↓
Skeptic: Much better! Approved.
  ↓
Strategist creates high-quality GTM plan
```

---

## Testing Recommendations

1. **Test a "good" idea** - Should pass on first iteration (no loop)
2. **Test a "weak" idea** - Should trigger loop-back with specific feedback
3. **Check LangSmith traces** - Verify feedback appears in prompts on loop 2
4. **Check Railway logs** - Look for `is_loop_back=True` and focused queries
5. **Compare outputs** - Iteration 2 should be noticeably more detailed

---

## Future Enhancements (Optional)

- [ ] Pass previous iteration's full output to avoid repeating research
- [ ] Let Skeptic specify WHICH agent to improve (Analyst only vs Researcher only)
- [ ] Dynamically adjust `max_tokens` on loop-back (allow longer responses)
- [ ] Track improvement metrics (how much better is iteration 2 vs 1?)
- [ ] Add "confidence delta" - skip loop if improvement is marginal
