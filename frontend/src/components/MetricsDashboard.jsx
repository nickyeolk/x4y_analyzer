export function MetricsDashboard({ result }) {
  if (!result || !result.metadata) {
    return null;
  }

  const { metadata, loop_count, skeptic_approved } = result;
  const viabilityScore = result.strategist_plan?.viability_score || 0;

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = (seconds % 60).toFixed(0);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatCost = (cost) => {
    return `$${cost.toFixed(4)}`;
  };

  const formatTokens = (tokens) => {
    if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(2)}M`;
    if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}K`;
    return tokens.toString();
  };

  // Calculate total tokens from per-agent token usage
  const calculateTotalTokens = () => {
    if (!metadata.token_usage) return null;

    let totalPrompt = 0;
    let totalCompletion = 0;

    Object.values(metadata.token_usage).forEach(agentUsage => {
      totalPrompt += agentUsage.prompt_tokens || 0;
      totalCompletion += agentUsage.completion_tokens || 0;
    });

    return {
      totalPrompt,
      totalCompletion,
      total: totalPrompt + totalCompletion
    };
  };

  const tokenTotals = calculateTotalTokens();

  return (
    <>
      {/* Idea Quality Assessment */}
      <div className="card">
        <div className="card-header">
          <h2>💡 Idea Quality Assessment</h2>
        </div>

        <div className="viability-score">
          <div style={{ textAlign: 'center' }}>
            <div className="score-circle">
              {Math.round(viabilityScore)}%
            </div>
            <p style={{ marginTop: '1rem', fontSize: '1.125rem', fontWeight: 600, color: 'var(--gray-900)' }}>
              Viability Score
            </p>
            <p style={{ fontSize: '0.875rem', color: 'var(--gray-700)' }}>
              {viabilityScore >= 80 ? '🚀 Highly Viable' : viabilityScore >= 60 ? '✅ Viable' : viabilityScore >= 40 ? '⚠️ Moderate' : '❌ Low Viability'}
            </p>
          </div>
        </div>

        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <span className={`badge ${skeptic_approved ? 'badge-success' : 'badge-warning'}`}>
            {skeptic_approved ? '✓ Skeptic Approved' : '⚠️ Needs Review'}
          </span>
          {loop_count > 0 && (
            <span className="badge badge-info">
              🔄 {loop_count} Quality Loop{loop_count > 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Technical Metrics */}
      <details className="card" style={{ cursor: 'pointer' }}>
        <summary style={{ listStyle: 'none', padding: '1rem', borderBottom: '1px solid var(--gray-200)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600, color: 'var(--gray-800)' }}>
              ⚙️ Technical Metrics
            </h3>
            <span style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
              Click to expand
            </span>
          </div>
        </summary>

        <div style={{ padding: '1rem' }}>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">{formatDuration(metadata.total_duration_seconds)}</div>
              <div className="metric-label">Duration</div>
            </div>

            <div className="metric-card">
              <div className="metric-value">{formatCost(metadata.cost_usd)}</div>
              <div className="metric-label">Cost (USD)</div>
            </div>

            <div className="metric-card">
              <div className="metric-value">{loop_count}</div>
              <div className="metric-label">Iterations</div>
            </div>

            {tokenTotals && (
              <div className="metric-card">
                <div className="metric-value">{formatTokens(tokenTotals.total)}</div>
                <div className="metric-label">Tokens</div>
              </div>
            )}
          </div>

          {tokenTotals && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--border-radius)' }}>
              <h4 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--gray-700)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Token Breakdown
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem', fontSize: '0.875rem' }}>
                <div>
                  <span style={{ color: 'var(--gray-600)' }}>Input: </span>
                  <strong style={{ color: 'var(--gray-900)' }}>{formatTokens(tokenTotals.totalPrompt)}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--gray-600)' }}>Output: </span>
                  <strong style={{ color: 'var(--gray-900)' }}>{formatTokens(tokenTotals.totalCompletion)}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--gray-600)' }}>Total: </span>
                  <strong style={{ color: 'var(--gray-900)' }}>{formatTokens(tokenTotals.total)}</strong>
                </div>
              </div>
            </div>
          )}
        </div>
      </details>
    </>
  );
}
