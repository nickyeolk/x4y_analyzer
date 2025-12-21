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

  return (
    <div className="card">
      <div className="card-header">
        <h2>Analysis Metrics</h2>
      </div>

      <div className="viability-score">
        <div style={{ textAlign: 'center' }}>
          <div className="score-circle">
            {viabilityScore.toFixed(1)}
          </div>
          <p style={{ marginTop: '1rem', fontSize: '1.125rem', fontWeight: 600, color: 'var(--gray-700)' }}>
            Viability Score
          </p>
          <p style={{ fontSize: '0.875rem', color: 'var(--gray-600)' }}>
            {viabilityScore >= 8 ? '🚀 Highly Viable' : viabilityScore >= 6 ? '✅ Viable' : viabilityScore >= 4 ? '⚠️ Moderate' : '❌ Low Viability'}
          </p>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{formatDuration(metadata.total_duration_seconds)}</div>
          <div className="metric-label">Duration</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{formatCost(metadata.cost_usd)}</div>
          <div className="metric-label">Cost</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{loop_count}</div>
          <div className="metric-label">Iterations</div>
        </div>

        {metadata.token_usage?.total_tokens && (
          <div className="metric-card">
            <div className="metric-value">{formatTokens(metadata.token_usage.total_tokens)}</div>
            <div className="metric-label">Tokens</div>
          </div>
        )}
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
  );
}
