# Observability Guide

Complete guide to understanding and using AgentLand's observability features.

## Table of Contents

- [Overview](#overview)
- [Three Pillars](#three-pillars)
- [Traces](#traces)
- [Logs](#logs)
- [Metrics](#metrics)
- [Debugging Workflows](#debugging-workflows)
- [Production Monitoring](#production-monitoring)

## Overview

AgentLand implements comprehensive observability using the three pillars approach:

1. **Traces** (OpenTelemetry) - Distributed request tracing
2. **Logs** (Structlog) - Structured JSON logs with context
3. **Metrics** (Prometheus) - Time-series performance data

All three are automatically correlated via:
- **Correlation IDs**: Unique identifier for each request
- **Trace IDs**: OpenTelemetry distributed tracing ID
- **Span IDs**: Individual operation identifiers

## Three Pillars

### When to Use Each

**Traces**: "What happened during this specific request?"
- Visualize request flow
- Identify slow components
- Understand agent decisions

**Logs**: "What was the system doing at this time?"
- Debug specific errors
- Audit agent reasoning
- Track tool calls

**Metrics**: "How is the system performing overall?"
- Monitor performance trends
- Alert on anomalies
- Capacity planning

## Traces

### Architecture

OpenTelemetry provides distributed tracing across the entire request lifecycle.

### Span Hierarchy

```
workflow.execute (200ms)
├─ node.triage (110ms)
│  ├─ agent.triage (108ms)
│  │  ├─ tool.database_query (2ms)
│  │  └─ llm.request (105ms)
│  └─ ...
└─ node.billing (90ms)
   ├─ agent.billing (88ms)
   │  ├─ tool.database_query (1ms)
   │  ├─ llm.request (80ms)
   │  ├─ tool.payment_gateway (5ms)
   │  └─ tool.email_sender (2ms)
   └─ ...
```

### Span Attributes

Each span includes rich metadata:

```json
{
  "name": "agent.billing",
  "attributes": {
    "agent.name": "billing",
    "agent.decision": "Billing issue resolved",
    "agent.confidence": null,
    "agent.reasoning": "Investigated payment history and provided solution"
  },
  "duration": 88ms
}
```

### Using Traces

#### 1. Enable Tracing

```bash
# In .env
OTEL_ENABLED=true
OTEL_EXPORTER=console  # or jaeger, otlp
```

#### 2. View Traces in Console

Traces are printed as JSON to stdout when `OTEL_EXPORTER=console`:

```bash
make run | grep '"name":'
```

#### 3. Export to Jaeger

```bash
# In .env
OTEL_EXPORTER=jaeger
OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14268/api/traces

# Run Jaeger
docker run -d -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one:latest
```

Then visit http://localhost:16686 to view traces.

### Trace-Based Debugging

**Problem**: Request is slow

**Solution**:
1. Get correlation_id from response
2. Find trace by correlation_id
3. Visualize span waterfall
4. Identify slowest span
5. Drill down into that component

**Example**:
```
Trace ID: abc123
Total: 450ms
├─ triage: 120ms ✓ Normal
└─ technical: 330ms ⚠️ SLOW
   └─ llm.request: 320ms ⚠️ Root cause
```

## Logs

### Architecture

Structlog provides structured logging with automatic context binding.

### Log Structure

Every log entry is JSON:

```json
{
  "timestamp": "2025-12-11T10:30:45.123Z",
  "level": "info",
  "event": "agent_decision",
  "correlation_id": "CID-abc123",
  "trace_id": "7f8a9b3c...",
  "span_id": "4d2e1f0a...",
  "agent": "billing_agent",
  "decision": {
    "assigned_agent": "billing_agent",
    "urgency": "medium",
    "confidence": 0.92
  },
  "ticket_id": "T-001"
}
```

### Log Levels

- **DEBUG**: Detailed internal state
- **INFO**: Normal operations (agent decisions, tool calls)
- **WARNING**: Unusual but handled situations
- **ERROR**: Errors that need attention
- **CRITICAL**: System-level failures

### Log Events

Key events to watch:

#### Application Lifecycle
```
application_started
application_shutdown
```

#### Workflow Events
```
workflow_started
workflow_step
workflow_completed
workflow_failed
```

#### Agent Events
```
agent_started
agent_decision
agent_completed
agent_error
```

#### Tool Events
```
tool_started
tool_executing
tool_success
tool_failure
tool_completed
```

#### LLM Events
```
llm_request_started
llm_request_completed
llm_request_failed
mock_llm_generated
```

### Using Logs

#### 1. Configure Log Level

```bash
# In .env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
APP_ENV=development  # Console output
APP_ENV=production  # JSON output
```

#### 2. Follow Logs

```bash
# All logs
make run

# Filter by event
make run | grep agent_decision

# Filter by agent
make run | grep billing_agent

# Filter by ticket
make run | grep T-001
```

#### 3. Search Logs (Production)

If using centralized logging (ELK, Loki):

```
# Find all errors for a ticket
correlation_id:"CID-abc123" AND level:"error"

# Find slow LLM requests
event:"llm_request_completed" AND duration_seconds:>5

# Find failed tool calls
event:"tool_failure" AND tool:"payment_gateway"
```

### Log-Based Debugging

**Problem**: Agent made wrong decision

**Solution**:
1. Find correlation_id from response
2. Filter logs: `grep <correlation_id>`
3. Look for `agent_decision` events
4. Check `reasoning` field
5. Verify tool call results
6. Check LLM prompt/response

**Example**:
```json
{
  "event": "agent_decision",
  "agent": "triage",
  "decision": "Route to billing_agent",
  "reasoning": "Customer mentions billing-related terms",
  "confidence": 0.92
}
```

If wrong: Check if prompt needs adjustment or training data issue.

## Metrics

### Architecture

Prometheus metrics exposed at `/metrics` endpoint.

### Available Metrics

#### Agent Metrics

**agent_invocation_count** (Counter)
```
agent_invocation_count{agent="billing",status="success"} 142
agent_invocation_count{agent="billing",status="error"} 3
```

**agent_decision_latency_seconds** (Histogram)
```
agent_decision_latency_seconds_bucket{agent="billing",le="0.1"} 89
agent_decision_latency_seconds_bucket{agent="billing",le="0.5"} 142
agent_decision_latency_seconds_sum{agent="billing"} 18.45
agent_decision_latency_seconds_count{agent="billing"} 145
```

#### Tool Metrics

**tool_call_count** (Counter)
```
tool_call_count{tool="database_query",status="success"} 450
tool_call_count{tool="payment_gateway",status="failure"} 12
```

**tool_call_duration_seconds** (Histogram)
```
tool_call_duration_seconds_bucket{tool="payment_gateway",le="0.01"} 120
tool_call_duration_seconds_sum{tool="payment_gateway"} 12.45
```

#### LLM Metrics

**llm_tokens_used** (Counter)
```
llm_tokens_used{model="claude-sonnet-4-5",type="prompt"} 234567
llm_tokens_used{model="claude-sonnet-4-5",type="completion"} 45678
```

**llm_api_cost_dollars** (Counter)
```
llm_api_cost_dollars{agent="billing"} 1.23
llm_api_cost_dollars{agent="technical"} 2.34
```

#### Business Metrics

**tickets_processed_total** (Counter)
```
tickets_processed_total{category="billing",urgency="medium"} 67
tickets_processed_total{category="technical",urgency="high"} 23
```

**ticket_resolution_time_seconds** (Histogram)
```
ticket_resolution_time_seconds_bucket{le="1.0"} 120
ticket_resolution_time_seconds_sum 450.23
```

### Using Metrics

#### 1. View Metrics

```bash
curl http://localhost:8000/metrics
```

#### 2. Prometheus Setup

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'agentland'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

#### 3. Query Examples

**Average agent latency**:
```promql
rate(agent_decision_latency_seconds_sum[5m])
  /
rate(agent_decision_latency_seconds_count[5m])
```

**Error rate**:
```promql
rate(agent_invocation_count{status="error"}[5m])
  /
rate(agent_invocation_count[5m])
```

**P95 latency**:
```promql
histogram_quantile(0.95,
  rate(agent_decision_latency_seconds_bucket[5m])
)
```

**Hourly LLM cost**:
```promql
increase(llm_api_cost_dollars[1h])
```

#### 4. Grafana Dashboard

Create dashboard with panels:
- Request rate (tickets/sec)
- Latency (P50, P95, P99)
- Error rate (%)
- Agent distribution (pie chart)
- LLM cost (dollars/hour)
- Token usage (tokens/minute)

### Metric-Based Monitoring

**Setup Alerts**:

1. **High Error Rate**
```yaml
alert: HighErrorRate
expr: rate(agent_invocation_count{status="error"}[5m]) > 0.05
for: 5m
annotations:
  summary: "Error rate above 5%"
```

2. **Slow Response Time**
```yaml
alert: SlowResponseTime
expr: histogram_quantile(0.95, rate(ticket_resolution_time_seconds_bucket[5m])) > 5.0
for: 10m
annotations:
  summary: "P95 latency above 5 seconds"
```

3. **High LLM Costs**
```yaml
alert: HighLLMCost
expr: increase(llm_api_cost_dollars[1h]) > 10.0
for: 5m
annotations:
  summary: "LLM costs exceeding $10/hour"
```

## Debugging Workflows

### Common Debugging Scenarios

#### Scenario 1: Wrong Agent Routing

**Symptoms**: Ticket routed to incorrect agent

**Debug Steps**:
1. Get correlation_id from response
2. Filter logs: `grep <correlation_id> | grep agent_decision`
3. Check triage agent's reasoning
4. Verify customer tier was fetched
5. Check if keywords matched correctly

**Example Investigation**:
```bash
$ grep CID-abc123 logs.json | grep agent_decision

{
  "event": "agent_decision",
  "agent": "triage",
  "decision": "Route to technical_agent",  # Expected: billing_agent
  "reasoning": "Technical issue reported",  # Keywords triggered wrong match
  "confidence": 0.88
}
```

**Solution**: Adjust system prompt or add more specific keywords.

#### Scenario 2: Tool Call Failure

**Symptoms**: Agent couldn't complete resolution

**Debug Steps**:
1. Get correlation_id
2. Filter logs: `grep <correlation_id> | grep tool_failure`
3. Check error message
4. Verify tool input was valid
5. Check tool availability

**Example Investigation**:
```bash
$ grep CID-abc123 logs.json | grep tool_

{
  "event": "tool_executing",
  "tool": "payment_gateway",
  "input": "{'amount': 49.99, ...}"
}
{
  "event": "tool_failure",
  "tool": "payment_gateway",
  "error": "Connection timeout"
}
```

**Solution**: Check payment gateway connectivity, implement retry.

#### Scenario 3: Slow Response

**Symptoms**: Request takes >5 seconds

**Debug Steps**:
1. Get trace_id from logs
2. View trace waterfall
3. Identify slowest span
4. Check if it's LLM call, tool call, or other

**Example Investigation**:
```
Trace waterfall:
workflow.execute: 5200ms
├─ node.triage: 120ms ✓
└─ node.technical: 5080ms ⚠️
   ├─ tool.knowledge_base: 3000ms ⚠️ (Slow KB search)
   └─ llm.request: 2000ms ✓
```

**Solution**: Optimize knowledge base search, add caching.

#### Scenario 4: High Token Usage

**Symptoms**: LLM costs higher than expected

**Debug Steps**:
1. Check metrics: `llm_tokens_used`
2. Group by agent
3. Check which agent uses most tokens
4. Review prompts for that agent

**Example Investigation**:
```promql
sum(llm_tokens_used) by (agent)

billing: 450k tokens
technical: 890k tokens ⚠️ (2x expected)
account: 350k tokens
```

**Solution**: Shorten technical agent's system prompt, reduce KB context.

## Production Monitoring

### Recommended Setup

#### 1. Observability Stack

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and alerts
- **Jaeger/Tempo**: Distributed tracing
- **Loki/ELK**: Centralized logging

#### 2. Key Dashboards

**Overview Dashboard**:
- Request rate (1m, 5m, 1h)
- P95 latency
- Error rate %
- Active tickets
- Agent distribution

**Performance Dashboard**:
- Latency histograms per agent
- Tool call duration
- LLM response time
- Queue depth

**Cost Dashboard**:
- LLM tokens used (hourly, daily)
- LLM API cost (dollars)
- Cost per ticket
- Cost projection

**Business Dashboard**:
- Tickets by category
- Tickets by urgency
- Resolution time
- Escalation rate %
- Customer satisfaction (if available)

#### 3. Critical Alerts

**P1 Alerts** (Page immediately):
- API down (health check failed)
- Error rate > 10%
- P95 latency > 10 seconds

**P2 Alerts** (Notify team):
- Error rate > 5%
- P95 latency > 5 seconds
- LLM cost > $50/hour
- Escalation rate > 20%

**P3 Alerts** (Log for review):
- Error rate > 2%
- P95 latency > 3 seconds
- Unusual agent distribution

#### 4. Log Retention

- **Hot storage** (7 days): All logs, fast query
- **Warm storage** (30 days): Aggregated logs
- **Cold storage** (1 year): Archived logs, compliance

#### 5. Trace Sampling

Production sampling strategy:
- **All errors**: 100% sampled
- **Slow requests** (>3s): 100% sampled
- **Normal requests**: 1-10% sampled

### Performance Baselines

From evaluation benchmarks:

| Metric | Target | Baseline |
|--------|--------|----------|
| P50 latency | <500ms | 220ms |
| P95 latency | <3000ms | 500ms |
| P99 latency | <5000ms | 800ms |
| Error rate | <1% | 0.1% |
| Tokens/ticket | <2000 | 1500 |
| Cost/ticket | <$0.01 | $0.0025 |

### Capacity Planning

Use metrics to forecast scaling needs:

**Request Rate**:
```promql
# Current: 10 requests/sec
# Capacity: 100 requests/sec per instance
# Headroom: 90% capacity = 90 req/sec per instance
```

**Token Budget**:
```promql
# Current: 1M tokens/day = ~670 tickets/day
# Budget: $100/day = 40k tickets/day
# Headroom: 60x current usage
```

## Conclusion

AgentLand's observability provides:
- ✅ Full visibility into every request
- ✅ Automatic correlation across traces/logs/metrics
- ✅ Production-ready monitoring and alerting
- ✅ Debugging tools for common issues
- ✅ Cost tracking and optimization

With proper observability, you can:
- Debug issues quickly
- Optimize performance
- Control costs
- Scale confidently
- Ensure reliability
