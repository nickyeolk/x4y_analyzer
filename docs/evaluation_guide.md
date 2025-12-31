# Evaluation Guide

Complete guide to AgentLand's evaluation framework and how to validate agent performance.

## Table of Contents

- [Overview](#overview)
- [Evaluation Framework](#evaluation-framework)
- [Test Datasets](#test-datasets)
- [Custom Metrics](#custom-metrics)
- [Running Evaluations](#running-evaluations)
- [Interpreting Results](#interpreting-results)
- [Adding Test Cases](#adding-test-cases)
- [Continuous Evaluation](#continuous-evaluation)

## Overview

AgentLand includes a comprehensive evaluation framework to validate:
- **Routing Accuracy**: Does triage route to the correct specialist?
- **Tool Usage**: Do agents call the right tools?
- **Performance**: Are latency and cost within targets?
- **Response Quality**: Are agent responses helpful and accurate?

### Why Evaluation Matters

- **Confidence**: Know your changes improve the system
- **Regressions**: Catch issues before production
- **Optimization**: Identify improvement opportunities
- **Compliance**: Demonstrate system reliability

## Evaluation Framework

### Architecture

```
Test Datasets (JSON)
  ↓
Test Runner (Python)
  ↓
Workflow Execution (Real agents)
  ↓
Metric Calculation (Custom metrics)
  ↓
Results & Reports (JSON + Console)
```

### Design Principles

1. **Real Execution**: Tests run through actual workflow
2. **Comprehensive**: 40+ test cases covering all scenarios
3. **Automated**: Full test suite runs in ~2 minutes
4. **Actionable**: Clear pass/fail with detailed diagnostics
5. **Extensible**: Easy to add new tests and metrics

## Test Datasets

### Dataset Files

Located in `tests/evaluation/datasets/`:

#### billing_cases.json (10 tests)
Billing scenarios:
- Double charges and refund requests
- Payment method updates
- Declined payments
- Subscription changes
- Invoice requests
- Auto-renewal issues
- Discount code problems

**Example**:
```json
{
  "test_id": "billing_001",
  "input": "I was charged twice for my subscription...",
  "customer_id": "cust_001",
  "subject": "Double charge on my account",
  "expected_routing": {
    "assigned_agent": "billing_agent",
    "urgency": "medium"
  },
  "expected_tools": ["database_query", "payment_gateway", "email_sender"],
  "expected_outcome": "resolved",
  "context": "Customer has active Pro subscription..."
}
```

#### technical_cases.json (10 tests)
Technical issues:
- API errors (500, 401, etc.)
- SSL certificate problems
- App crashes
- Webhook failures
- Dashboard loading issues
- Export feature bugs
- Performance problems
- SDK integration errors

#### account_cases.json (10 tests)
Account management:
- Password resets
- Email updates
- Security breaches
- Team member management
- Account deletion
- Notification settings
- 2FA setup
- Account suspension
- Profile updates
- Account merging

#### edge_cases.json (10 tests)
Complex and ambiguous scenarios:
- GDPR data deletion requests
- Multi-issue tickets
- Vague inquiries
- Legal matters
- Security concerns
- Audit requests
- Abuse reports
- Positive feedback
- Data recovery

### Dataset Format

Each test case includes:

| Field | Description |
|-------|-------------|
| `test_id` | Unique identifier |
| `input` | Ticket body text |
| `customer_id` | Customer identifier |
| `subject` | Ticket subject |
| `expected_routing.assigned_agent` | Expected agent |
| `expected_routing.urgency` | Expected urgency level |
| `expected_tools` | Tools that should be called |
| `expected_outcome` | Expected resolution status |
| `context` | Background information |
| `requires_human` (optional) | Should escalate to human |

## Custom Metrics

### 1. RoutingAccuracyMetric

**Purpose**: Validate triage agent routing decisions

**Threshold**: 90% accuracy

**Calculation**:
```python
accuracy = correct_routings / total_tests

# Per-agent metrics:
precision = true_positives / (true_positives + false_positives)
recall = true_positives / (true_positives + false_negatives)
f1_score = 2 * (precision * recall) / (precision + recall)
```

**Output**:
```
Routing Accuracy
════════════════════════════════════════════════════════════

Overall Accuracy: 95.0% (38/40)
Threshold: 90.0%
Status: ✅ PASSED

Per-Agent Metrics:

  billing_agent:
    Precision: 100.0%
    Recall: 90.0%
    F1 Score: 0.947
    TP: 9, FP: 0, FN: 1

  technical_agent:
    Precision: 90.0%
    Recall: 100.0%
    F1 Score: 0.947
    TP: 10, FP: 1, FN: 0

Routing Failures (2):
  - billing_004: Expected billing_agent, got account_agent (conf: 0.85)
  - technical_005: Expected technical_agent, got billing_agent (conf: 0.72)
```

### 2. ToolUsageMetric

**Purpose**: Validate agents call correct tools

**Threshold**: 80% correctness (F1 >= 0.8)

**Calculation**:
```python
# For each test case:
expected_tools = set(test['expected_tools'])
actual_tools = set(tools_called_by_agents)

precision = len(expected ∩ actual) / len(actual)
recall = len(expected ∩ actual) / len(expected)
f1_score = 2 * (precision * recall) / (precision + recall)

# Pass if F1 >= 0.8
correctness = count(f1 >= 0.8) / total_tests
```

**Output**:
```
Tool Usage Correctness
════════════════════════════════════════════════════════════

Overall Correctness: 83.3% (25/30)
Threshold: 80.0%
Status: ✅ PASSED

Average Metrics:
  Precision: 91.2%
  Recall: 88.5%
  F1 Score: 0.897

Tool Usage Issues (5):
  billing_006:
    Expected: ['database_query', 'email_sender']
    Actual: ['database_query', 'payment_gateway', 'email_sender']
    Missing: []
    Unexpected: ['payment_gateway']
    F1 Score: 0.667
```

### 3. Performance Benchmarks

**Purpose**: Validate latency and cost targets

**Thresholds**:
- P95 latency < 3 seconds
- Average cost < $0.01 per ticket

**Metrics Collected**:
- End-to-end latency (P50, P95, P99)
- Per-agent latency
- Token usage (prompt + completion)
- Estimated cost

**Output**:
```
PERFORMANCE BENCHMARK SUMMARY
════════════════════════════════════════════════════════════

BILLING (10 tickets):
  Latency:
    Mean:   225ms
    Median: 220ms
    P95:    280ms
    P99:    310ms
  Token Usage:
    Avg Prompt:     672
    Avg Completion: 36
  Cost:
    Total:       $0.0249
    Per Ticket:  $0.0025

OVERALL (30 tickets):
  Latency:
    Mean:   235ms
    Median: 228ms
    P95:    395ms
    P99:    520ms
  Total Cost: $0.0741
  Avg Cost Per Ticket: $0.0025

  Performance Targets:
    P95 < 3000ms: ✅ PASSED (actual: 395ms)
    Avg Cost < $0.01: ✅ PASSED (actual: $0.0025)
```

## Running Evaluations

### Quick Start

```bash
# Run all evaluations
python scripts/run_evaluation.py

# Or use make
make evaluate
```

### Individual Test Suites

```bash
# Routing accuracy only
python tests/evaluation/test_routing_eval.py

# Tool usage only
python tests/evaluation/test_tool_usage_eval.py

# Performance benchmarks only
python tests/evaluation/test_benchmark.py
```

### Filtering Tests

Run specific categories:

```bash
# Just billing tests
python -c "
from tests.evaluation.test_routing_eval import test_billing_routing
import asyncio
asyncio.run(test_billing_routing())
"
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Evaluation Suite
  run: |
    python scripts/run_evaluation.py
    if [ $? -ne 0 ]; then
      echo "Evaluation failed"
      exit 1
    fi
```

## Interpreting Results

### Success Criteria

**All Tests Pass**:
```
✅ ALL EVALUATIONS PASSED!

Routing Accuracy: ✅
Tool Usage: ✅
Performance: ✅
```

System is ready for deployment!

### Partial Failures

**Routing Failed**:
```
❌ SOME EVALUATIONS FAILED

Routing Accuracy:
  Billing: 90.0% (9/10) ✅ PASSED
  Technical: 80.0% (8/10) ❌ FAILED (threshold: 90%)
```

**Action**: Review failed test cases, check triage prompts

**Tool Usage Failed**:
```
Tool Usage Correctness:
  Billing: 70.0% (7/10) ❌ FAILED
```

**Action**: Verify tool registry, check agent logic

**Performance Failed**:
```
Performance:
  P95: 4500ms ❌ (target: <3000ms)
```

**Action**: Profile slow operations, optimize LLM calls

### Analyzing Failures

#### Routing Failure

```
Routing Failures (3):
  - technical_002: Expected technical_agent, got billing_agent (conf: 0.72)
```

**Investigation**:
1. Read test case: `technical_002`
2. Check input text for ambiguity
3. Review triage agent logs for reasoning
4. Consider adding keywords or examples

#### Tool Usage Failure

```
billing_003:
  Expected: ['database_query', 'payment_gateway', 'email_sender']
  Actual: ['database_query', 'email_sender']
  Missing: ['payment_gateway']
```

**Investigation**:
1. Ticket mentioned "refund" - should call payment_gateway
2. Check billing agent logic - does it detect refund keyword?
3. Review agent logs to see why tool wasn't called
4. May need prompt adjustment

## Adding Test Cases

### 1. Create Test Case

Add to appropriate dataset file:

```json
{
  "test_id": "billing_011",
  "input": "Your description of the issue...",
  "customer_id": "cust_001",
  "subject": "Test case subject",
  "expected_routing": {
    "assigned_agent": "billing_agent",
    "urgency": "high"
  },
  "expected_tools": ["database_query", "payment_gateway"],
  "expected_outcome": "resolved",
  "context": "Background information for this test"
}
```

### 2. Run Tests

```bash
python tests/evaluation/test_routing_eval.py
```

### 3. Verify Results

Check if new test passes. If it fails:
- Is it a real bug? Fix the agent
- Is the expectation wrong? Update test case
- Is it edge case? Lower threshold or mark as known issue

### Best Practices

**Good Test Cases**:
- ✅ Realistic customer language
- ✅ Clear expected behavior
- ✅ Representative of production
- ✅ Edge cases and ambiguous scenarios

**Bad Test Cases**:
- ❌ Overly simple or obvious
- ❌ Unrealistic language
- ❌ Duplicate scenarios
- ❌ Vague expectations

## Continuous Evaluation

### Regression Testing

Run evaluations before every deployment:

```bash
# Pre-deploy check
make evaluate
if [ $? -eq 0 ]; then
  echo "✅ Safe to deploy"
else
  echo "❌ Regressions detected"
  exit 1
fi
```

### Performance Tracking

Track metrics over time:

```bash
# Save results
python scripts/run_evaluation.py > eval_$(date +%Y%m%d).json

# Compare with baseline
diff eval_baseline.json eval_$(date +%Y%m%d).json
```

### A/B Testing

Compare two versions:

```bash
# Baseline
git checkout main
python scripts/run_evaluation.py > results_main.json

# New feature
git checkout feature-branch
python scripts/run_evaluation.py > results_feature.json

# Compare
python -c "
import json

main = json.load(open('results_main.json'))
feature = json.load(open('results_feature.json'))

print(f\"Routing accuracy: {main['routing']['accuracy']:.1%} → {feature['routing']['accuracy']:.1%}\")
print(f\"P95 latency: {main['performance']['p95']}ms → {feature['performance']['p95']}ms\")
"
```

### Monitoring Production

Run evaluations against production:

```bash
# Point to production endpoint
export API_URL=https://api.production.example.com

# Run smoke tests
python tests/evaluation/test_routing_eval.py \
  --endpoint $API_URL \
  --sample 10%  # Only 10% of tests
```

## Advanced Topics

### Custom Metrics

Create your own metric:

```python
# tests/evaluation/metrics/custom_metric.py

class CustomMetric:
    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold
        self.name = "Custom Metric"

    def evaluate(
        self,
        test_cases: List[Dict],
        actual_results: List[Dict]
    ) -> Dict[str, Any]:
        # Your evaluation logic here
        score = calculate_score(test_cases, actual_results)

        return {
            "metric_name": self.name,
            "score": score,
            "passed": score >= self.threshold,
            "details": {...}
        }
```

### Dataset Generation

Generate synthetic test cases:

```python
# scripts/generate_test_cases.py

def generate_billing_cases(n: int) -> List[Dict]:
    """Generate n billing test cases."""
    templates = [
        "I was charged {amount} but expected {expected}",
        "My subscription renewed but I cancelled it",
        # ...
    ]

    cases = []
    for i in range(n):
        template = random.choice(templates)
        case = {
            "test_id": f"billing_gen_{i}",
            "input": template.format(...),
            # ...
        }
        cases.append(case)

    return cases
```

### Human Evaluation

Add human-in-the-loop evaluation:

```python
# tests/evaluation/human_eval.py

def human_eval(test_case: Dict, result: Dict):
    """Show result to human for rating."""
    print(f"Ticket: {test_case['input']}")
    print(f"Response: {result['resolution']['response']}")

    rating = input("Rate 1-5: ")
    feedback = input("Feedback: ")

    return {
        "test_id": test_case["test_id"],
        "rating": int(rating),
        "feedback": feedback
    }
```

## Conclusion

AgentLand's evaluation framework provides:
- ✅ Comprehensive test coverage (40+ cases)
- ✅ Automated evaluation (<2 minutes)
- ✅ Clear pass/fail criteria
- ✅ Detailed diagnostics
- ✅ Easy to extend

### Quick Reference

```bash
# Run all evaluations
make evaluate

# Individual suites
python tests/evaluation/test_routing_eval.py
python tests/evaluation/test_tool_usage_eval.py
python tests/evaluation/test_benchmark.py

# Add test case
# 1. Edit tests/evaluation/datasets/*.json
# 2. Run evaluation
# 3. Verify results

# CI/CD integration
# Add `make evaluate` to your pipeline
```

With proper evaluation, you can:
- Deploy with confidence
- Catch regressions early
- Optimize systematically
- Demonstrate reliability
- Track improvements over time
