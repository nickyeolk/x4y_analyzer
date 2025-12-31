# LangSmith Integration - Complete Setup

## ✅ What Was Implemented

Your LLM client has been refactored to use **LangChain's ChatOpenAI**, which provides automatic LangSmith tracing.

### Changes Made:
- ✅ Replaced custom `httpx` HTTP client with LangChain's `ChatOpenAI`
- ✅ Added `SystemMessage` and `HumanMessage` formatting
- ✅ Automatic prompt/response tracing to LangSmith
- ✅ Kept same `generate()` interface (no agent changes needed)
- ✅ Maintained all observability (logging, metrics, OpenTelemetry)

---

## 🔧 Railway Configuration

### Required Environment Variables

In your Railway backend service, ensure these are set:

```bash
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=startup-analyzer
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# Your existing variables
OPENROUTER_API_KEY=xxxxx
TAVILY_API_KEY=xxxxx
```

**How to set them:**
1. Go to Railway Dashboard → Your Project
2. Click on your backend service
3. Click "Variables" tab
4. Add each variable above
5. Redeploy (automatic after adding variables)

---

## 📊 Using LangSmith

### 1. Access LangSmith Dashboard

Go to: https://smith.langchain.com/

### 2. Find Your Project

- Click "Projects" in sidebar
- Select "startup-analyzer" (or whatever you named it)

### 3. View Traces

Click "Traces" to see all analysis runs:

```
Each trace shows:
├── workflow.execute (overall analysis)
    ├── node.analyst
    │   ├── agent.analyst
    │   │   ├── tool.tavily_search
    │   │   └── llm.generate ← YOU CAN NOW SEE THIS!
    ├── node.researcher
    │   ├── agent.researcher
    │   │   ├── tool.tavily_search (market)
    │   │   ├── tool.tavily_search (competitors)
    │   │   └── llm.generate ← FULL PROMPT VISIBLE!
    ├── node.skeptic
    │   ├── agent.skeptic
    │   │   ├── tool.marketing_rag
    │   │   └── llm.generate ← INCLUDES RAG CONTEXT!
    └── node.strategist
        └── agent.strategist
            └── llm.generate ← FINAL SYNTHESIS PROMPT!
```

### 4. View Individual LLM Calls

Click on any `llm.generate` step to see:

**Input (Prompt):**
```
System: You are The Analyst, an expert at deconstructing brands...

User: Analyze the brand: Uber

Business Idea Context: Uber for Dog Walkers

Web Search Results:
**Uber's Success Story**
[Full search results here...]

⚠️ PREVIOUS ITERATION FEEDBACK - CRITICAL TO ADDRESS:
[Skeptic's feedback if loop-back]

Provide a comprehensive brand DNA analysis.
```

**Output (Response):**
```json
{
  "brand_name": "Uber",
  "core_strengths": [...],
  "business_model": "...",
  ...
}
```

**Metadata:**
- Model: `openai/gpt-4o`
- Prompt tokens: 1,234
- Completion tokens: 567
- Total tokens: 1,801
- Latency: 2.3s
- Cost estimate: $0.023

---

## 🔍 What You Can Now See

### Before (Custom httpx client):
- ❌ No LLM traces in LangSmith
- ❌ Can't see prompts sent to agents
- ❌ Can't see LLM responses
- ❌ Can't debug why agent produced certain output

### After (LangChain ChatOpenAI):
- ✅ **Full prompt visibility** - See exactly what each agent asks
- ✅ **Response visibility** - See raw LLM output
- ✅ **Skeptic feedback** - See loop-back instructions in prompts
- ✅ **RAG context** - See marketing frameworks retrieved
- ✅ **Token usage** - Track costs per agent
- ✅ **Latency breakdown** - Find slow agents
- ✅ **Error traces** - Debug failed calls

---

## 🧪 Testing LangSmith Integration

### 1. Deploy to Railway
```bash
git push
```

### 2. Run an Analysis

Use your frontend or curl:
```bash
curl -X POST https://your-backend.railway.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"x_brand": "Uber", "y_market": "Dog Walkers"}'
```

### 3. Check LangSmith

Within 10 seconds, you should see:
1. New trace appears in LangSmith dashboard
2. Click on it to expand the tree
3. Click any `llm.generate` node
4. See full prompt and response!

---

## 📝 Example: Debugging with LangSmith

### Scenario: Skeptic keeps rejecting

**Before:** 🤷 "Why does skeptic keep rejecting?"

**After with LangSmith:**
1. Open trace for the analysis
2. Click on skeptic's `llm.generate`
3. View prompt - see the RAG context retrieved:
   ```
   MARKETING FRAMEWORKS & PITFALLS:
   **Marketing Framework 1** (relevance: 0.85)
   "Dog walking marketplace saturation: Studies show..."
   ```
4. View response - see skeptic's reasoning:
   ```json
   {
     "approved": false,
     "concerns": ["Competitive analysis missing Rover details"],
     "loop_back_reason": "Need deeper competitive analysis"
   }
   ```
5. Check next iteration's analyst prompt:
   ```
   ⚠️ PREVIOUS ITERATION FEEDBACK:
   Rejection Reason: Need deeper competitive analysis
   Concerns:
   - Competitive analysis missing Rover details
   ```
6. See that analyst searched specifically for "Uber Rover competitive analysis"

---

## 🎯 Common Use Cases

### 1. Improve Prompts
- See which prompts produce best results
- A/B test different system prompts
- Refine instructions based on actual outputs

### 2. Debug Loops
- See why skeptic rejects
- Verify feedback reaches analyst/researcher
- Confirm improvements in iteration 2

### 3. Cost Optimization
- Identify which agent uses most tokens
- Find opportunities to reduce prompt size
- Track cost per analysis

### 4. Quality Assurance
- Review LLM outputs for quality
- Identify hallucinations or errors
- Validate structured JSON parsing

---

## 🚨 Troubleshooting

### "I don't see traces in LangSmith"

**Check:**
1. ✅ Environment variables set correctly in Railway
2. ✅ `LANGCHAIN_TRACING_V2=true` (must be string "true")
3. ✅ Railway redeployed after adding variables
4. ✅ Actually ran an analysis (traces only appear on LLM calls)
5. ✅ Selected correct project in LangSmith dashboard

### "Traces appear but no LLM calls"

This shouldn't happen now! The refactored client uses LangChain.

If you still don't see them:
1. Check Railway logs for `openrouter_client_initialized` - should show `langsmith_enabled=True`
2. Check for any LLM errors in logs
3. Verify `langchain-openai` package installed (in requirements.txt)

---

## 📈 Next Steps

1. **Push changes:** `git push`
2. **Wait for Railway deploy:** ~2 minutes
3. **Run test analysis:** Use frontend or API
4. **Open LangSmith:** https://smith.langchain.com/
5. **Explore traces:** Click through the tree
6. **View prompts:** Click any `llm.generate` node

Enjoy full visibility into your agent system! 🎉
