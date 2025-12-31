# Observability Setup for Startup Analyzer

## LangSmith Tracing (Recommended)

### 1. Get LangSmith API Key
1. Go to https://smith.langchain.com/
2. Sign up or log in
3. Click on your profile → Settings
4. Create an API key
5. Copy the key

### 2. Add to Railway Environment Variables
In your Railway project:
1. Go to project settings
2. Click "Variables" tab
3. Add these environment variables:
   ```
   LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxxxxx
   LANGSMITH_PROJECT=startup-analyzer
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   ```
4. Click "Deploy" to restart with new variables

### 3. View Traces
1. Go to https://smith.langchain.com/
2. Select "startup-analyzer" project
3. Click "Traces" in sidebar
4. You'll see all analysis runs with:
   - Complete agent flow visualization
   - All prompts and responses
   - Token usage and costs
   - Latency breakdown
   - Error traces

## Railway Logs (Immediate Access)

### View Logs
1. Railway Dashboard → Your Project
2. Click backend service
3. Click "Deployments" tab
4. Select latest deployment
5. View "Deploy Logs"

### Key Log Events to Watch For:
- `workflow_started` - Analysis begins
- `agent_started` - Each agent execution starts
- `tool_started` / `tool_completed` - Tool calls
- `routing_decision` - Skeptic approval decision
- `analyst_loop_back` - Loop iterations
- `workflow_completed` - Final result

## Structured Log Events

Each log entry includes:
- `event` - Event name (e.g., "agent_started")
- `trace_id` - Links related operations
- `span_id` - Specific operation identifier
- `agent` / `node` - Which agent/node
- `iteration` - Loop count
- `duration_seconds` - How long it took

## Debugging Tips

### To see prompts sent to agents:
1. Check Railway logs for `agent_started` events
2. Or use LangSmith to see full prompt text

### To see routing decisions:
1. Look for `routing_decision` events
2. Check `approved` field and `loop_count`

### To see why skeptic rejected:
1. Find `skeptic_completed` event
2. Check `loop_back_reason` field
3. Or view in LangSmith trace

### To see tool results:
1. Look for `tool_completed` events
2. Or view in LangSmith with full search results

## Cost Tracking

LangSmith automatically tracks:
- Token usage per agent
- Estimated costs
- Model used

You can also see token usage in the API response:
```json
{
  "metadata": {
    "token_usage": {
      "analyst": {"total_tokens": 1234},
      "researcher": {"total_tokens": 567},
      ...
    }
  }
}
```
