export function ResultsDisplay({ result }) {
  if (!result) {
    return null;
  }

  // Debug log the result structure
  console.log('[ResultsDisplay] Rendering with result:', result);

  const {
    analyst_insights,
    researcher_findings,
    risk_analysis,
    strategist_plan,
    skeptic_critique, // Legacy support
  } = result;

  // Check if we have any content to display
  const hasContent = analyst_insights || researcher_findings || risk_analysis || strategist_plan || skeptic_critique;

  if (!hasContent) {
    console.warn('[ResultsDisplay] Result object exists but has no displayable content');
    return (
      <div className="card">
        <div className="card-header">
          <h2>⚠️ No Results Available</h2>
        </div>
        <div style={{ padding: '1rem' }}>
          <p>The analysis completed but no results were generated. Please try again.</p>
          <details style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--gray-600)' }}>
            <summary>Debug Information</summary>
            <pre style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'var(--gray-100)', borderRadius: '4px', overflow: 'auto' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Analyst Insights */}
      {analyst_insights && (
        <div className="card">
          <div className="card-header">
            <h2>🔍 Brand Analysis</h2>
          </div>

          <div className="result-section">
            <h3>Core Strengths</h3>
            <ul className="result-list">
              {analyst_insights.core_strengths.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))}
            </ul>
          </div>

          <div className="result-section">
            <h3>Business Model</h3>
            <p style={{ color: 'var(--gray-900)', lineHeight: 1.6 }}>{analyst_insights.business_model}</p>
          </div>

          {analyst_insights.key_differentiators.length > 0 && (
            <div className="result-section">
              <h3>Key Differentiators</h3>
              <ul className="result-list">
                {analyst_insights.key_differentiators.map((diff, index) => (
                  <li key={index}>{diff}</li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ marginTop: '1rem' }}>
            <span className="badge badge-info">
              Confidence: {(analyst_insights.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      )}

      {/* Market Research */}
      {researcher_findings && (
        <div className="card">
          <div className="card-header">
            <h2>📊 Market Research</h2>
          </div>

          <div className="result-section">
            <h3>Market Overview</h3>
            <p style={{ color: 'var(--gray-900)', lineHeight: 1.6, marginBottom: '1rem' }}>
              <strong>Market:</strong> {researcher_findings.market_name}
            </p>
            {researcher_findings.market_size && (
              <p style={{ color: 'var(--gray-900)', lineHeight: 1.6, marginBottom: '1rem' }}>
                <strong>Size:</strong> {researcher_findings.market_size}
              </p>
            )}
            <p style={{ color: 'var(--gray-900)', lineHeight: 1.6 }}>
              <strong>Saturation:</strong>{' '}
              <span
                className={`badge ${
                  researcher_findings.saturation_level === 'low'
                    ? 'badge-success'
                    : researcher_findings.saturation_level === 'medium'
                    ? 'badge-warning'
                    : 'badge-error'
                }`}
              >
                {researcher_findings.saturation_level.toUpperCase()}
              </span>
            </p>
          </div>

          {researcher_findings.competitors.length > 0 && (
            <div className="result-section">
              <h3>Competitors ({researcher_findings.competitor_count})</h3>
              <ul className="result-list">
                {researcher_findings.competitors.map((competitor, index) => (
                  <li key={index}>{competitor}</li>
                ))}
              </ul>
            </div>
          )}

          {researcher_findings.opportunities.length > 0 && (
            <div className="result-section">
              <h3>Opportunities</h3>
              <ul className="result-list">
                {researcher_findings.opportunities.map((opp, index) => (
                  <li key={index}>{opp}</li>
                ))}
              </ul>
            </div>
          )}

          {researcher_findings.barriers.length > 0 && (
            <div className="result-section">
              <h3>Market Barriers</h3>
              <ul className="result-list">
                {researcher_findings.barriers.map((barrier, index) => (
                  <li key={index}>{barrier}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Risk Analysis */}
      {risk_analysis && (
        <div className="card">
          <div className="card-header">
            <h2>⚠️ Risk Analysis</h2>
          </div>

          {risk_analysis.summary && (
            <div className="result-section">
              <p style={{ color: 'var(--gray-900)', lineHeight: 1.6, marginBottom: '1rem' }}>
                {risk_analysis.summary}
              </p>
              <div style={{ marginBottom: '1rem' }}>
                <span
                  className={`badge ${
                    risk_analysis.overall_risk_level === 'low'
                      ? 'badge-success'
                      : risk_analysis.overall_risk_level === 'medium'
                      ? 'badge-warning'
                      : 'badge-error'
                  }`}
                >
                  Risk Level: {risk_analysis.overall_risk_level.toUpperCase()}
                </span>
                <span className="badge badge-info" style={{ marginLeft: '0.5rem' }}>
                  Confidence: {(risk_analysis.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          )}

          {risk_analysis.competitive_threats && risk_analysis.competitive_threats.length > 0 && (
            <div className="result-section">
              <h3>🎯 Competitive Threats</h3>
              <ul className="result-list">
                {risk_analysis.competitive_threats.map((threat, index) => (
                  <li key={index}>
                    {typeof threat === 'string' ? threat : (
                      <>
                        <strong>{threat.threat || threat.description || 'Unknown threat'}</strong>
                        {threat.severity && (
                          <span className={`badge ${threat.severity === 'high' ? 'badge-error' : threat.severity === 'medium' ? 'badge-warning' : 'badge-info'}`} style={{ marginLeft: '0.5rem', fontSize: '0.75rem' }}>
                            {threat.severity.toUpperCase()}
                          </span>
                        )}
                        {threat.mitigation && <div style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: 'var(--gray-600)' }}>Mitigation: {threat.mitigation}</div>}
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {risk_analysis.market_risks && risk_analysis.market_risks.length > 0 && (
            <div className="result-section">
              <h3>📉 Market Risks</h3>
              <ul className="result-list">
                {risk_analysis.market_risks.map((risk, index) => (
                  <li key={index}>
                    {typeof risk === 'string' ? risk : (
                      <>
                        <strong>{risk.risk || risk.description || 'Unknown risk'}</strong>
                        {risk.probability && (
                          <span className={`badge ${risk.probability === 'high' ? 'badge-error' : risk.probability === 'medium' ? 'badge-warning' : 'badge-info'}`} style={{ marginLeft: '0.5rem', fontSize: '0.75rem' }}>
                            {risk.probability.toUpperCase()} probability
                          </span>
                        )}
                        {risk.impact && <div style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: 'var(--gray-600)' }}>Impact: {risk.impact}</div>}
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {risk_analysis.execution_challenges && risk_analysis.execution_challenges.length > 0 && (
            <div className="result-section">
              <h3>⚙️ Execution Challenges</h3>
              <ul className="result-list">
                {risk_analysis.execution_challenges.map((challenge, index) => (
                  <li key={index}>
                    {typeof challenge === 'string' ? challenge : (
                      <>
                        <strong>{challenge.challenge || challenge.description || 'Unknown challenge'}</strong>
                        {challenge.difficulty && (
                          <span className={`badge ${challenge.difficulty === 'high' ? 'badge-error' : challenge.difficulty === 'medium' ? 'badge-warning' : 'badge-info'}`} style={{ marginLeft: '0.5rem', fontSize: '0.75rem' }}>
                            {challenge.difficulty.toUpperCase()} difficulty
                          </span>
                        )}
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {risk_analysis.financial_risks && risk_analysis.financial_risks.length > 0 && (
            <div className="result-section">
              <h3>💰 Financial Risks</h3>
              <ul className="result-list">
                {risk_analysis.financial_risks.map((risk, index) => (
                  <li key={index}>
                    {typeof risk === 'string' ? risk : (
                      <>
                        <strong>{risk.risk || risk.description || 'Unknown risk'}</strong>
                        {risk.concern_level && (
                          <span className={`badge ${risk.concern_level === 'high' ? 'badge-error' : risk.concern_level === 'medium' ? 'badge-warning' : 'badge-info'}`} style={{ marginLeft: '0.5rem', fontSize: '0.75rem' }}>
                            {risk.concern_level.toUpperCase()} concern
                          </span>
                        )}
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {risk_analysis.fatal_flaws && risk_analysis.fatal_flaws.length > 0 && (
            <div className="result-section">
              <h3>🚫 Fatal Flaws</h3>
              <div
                style={{
                  padding: '1rem',
                  background: '#fee2e2',
                  borderRadius: 'var(--border-radius)',
                  marginTop: '0.5rem',
                }}
              >
                <ul className="result-list">
                  {risk_analysis.fatal_flaws.map((flaw, index) => (
                    <li key={index} style={{ color: 'var(--error-color)' }}>
                      {flaw}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Skeptic Critique (Legacy) */}
      {!risk_analysis && skeptic_critique && (
        <div className="card">
          <div className="card-header">
            <h2>🤔 Critical Analysis (Legacy)</h2>
          </div>

          {skeptic_critique.concerns && skeptic_critique.concerns.length > 0 && (
            <div className="result-section">
              <h3>Concerns</h3>
              <ul className="result-list">
                {skeptic_critique.concerns.map((concern, index) => (
                  <li key={index}>{concern}</li>
                ))}
              </ul>
            </div>
          )}

          {skeptic_critique.fatal_flaws && skeptic_critique.fatal_flaws.length > 0 && (
            <div className="result-section">
              <h3>Critical Issues</h3>
              <div
                style={{
                  padding: '1rem',
                  background: '#fee2e2',
                  borderRadius: 'var(--border-radius)',
                  marginTop: '0.5rem',
                }}
              >
                <ul className="result-list">
                  {skeptic_critique.fatal_flaws.map((flaw, index) => (
                    <li key={index} style={{ color: 'var(--error-color)' }}>
                      {flaw}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {skeptic_critique.suggestions && skeptic_critique.suggestions.length > 0 && (
            <div className="result-section">
              <h3>Recommendations</h3>
              <ul className="result-list">
                {skeptic_critique.suggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ marginTop: '1rem' }}>
            <span
              className={`badge ${skeptic_critique.approved ? 'badge-success' : 'badge-warning'}`}
            >
              {skeptic_critique.approved ? '✓ Approved' : '⚠️ Needs Improvement'}
            </span>
          </div>
        </div>
      )}

      {/* GTM Strategy */}
      {strategist_plan && (
        <div className="card">
          <div className="card-header">
            <h2>🎯 Go-to-Market Strategy</h2>
          </div>

          <div className="result-section">
            <h3>Target Audience</h3>
            <p style={{ color: 'var(--gray-900)', lineHeight: 1.6 }}>{strategist_plan.target_audience}</p>
          </div>

          <div className="result-section">
            <h3>Value Proposition</h3>
            <p style={{ color: 'var(--gray-900)', lineHeight: 1.6 }}>{strategist_plan.value_proposition}</p>
          </div>

          {strategist_plan.pricing_strategy && (
            <div className="result-section">
              <h3>Pricing Strategy</h3>
              <p style={{ color: 'var(--gray-900)', lineHeight: 1.6 }}>{strategist_plan.pricing_strategy}</p>
            </div>
          )}

          {strategist_plan.distribution_channels.length > 0 && (
            <div className="result-section">
              <h3>Distribution Channels</h3>
              <ul className="result-list">
                {strategist_plan.distribution_channels.map((channel, index) => (
                  <li key={index}>{channel}</li>
                ))}
              </ul>
            </div>
          )}

          {strategist_plan.marketing_hooks.length > 0 && (
            <div className="result-section">
              <h3>Marketing Hooks</h3>
              <ul className="result-list">
                {strategist_plan.marketing_hooks.map((hook, index) => (
                  <li key={index}>{hook}</li>
                ))}
              </ul>
            </div>
          )}

          {strategist_plan.competitive_advantages.length > 0 && (
            <div className="result-section">
              <h3>Competitive Advantages</h3>
              <ul className="result-list">
                {strategist_plan.competitive_advantages.map((advantage, index) => (
                  <li key={index}>{advantage}</li>
                ))}
              </ul>
            </div>
          )}

          {strategist_plan.key_risks.length > 0 && (
            <div className="result-section">
              <h3>Key Risks</h3>
              <ul className="result-list">
                {strategist_plan.key_risks.map((risk, index) => (
                  <li key={index}>
                    {typeof risk === 'string' ? risk : (
                      typeof risk === 'object' && risk !== null ? JSON.stringify(risk) : String(risk)
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {strategist_plan.success_metrics.length > 0 && (
            <div className="result-section">
              <h3>Success Metrics</h3>
              <ul className="result-list">
                {strategist_plan.success_metrics.map((metric, index) => (
                  <li key={index}>{metric}</li>
                ))}
              </ul>
            </div>
          )}

          {strategist_plan.timeline && (
            <div className="result-section">
              <h3>Timeline</h3>
              <p style={{ color: 'var(--gray-900)', lineHeight: 1.6 }}>{strategist_plan.timeline}</p>
            </div>
          )}
        </div>
      )}

      {/* Summary Section */}
      {result.metadata && (
        <div className="card" style={{ background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.05))' }}>
          <div className="card-header">
            <h2>📋 Analysis Summary</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', padding: '1rem 0' }}>
            <div>
              <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Total Time
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--gray-900)' }}>
                {result.metadata.total_duration_seconds < 60
                  ? `${result.metadata.total_duration_seconds.toFixed(1)}s`
                  : `${Math.floor(result.metadata.total_duration_seconds / 60)}m ${(result.metadata.total_duration_seconds % 60).toFixed(0)}s`
                }
              </div>
            </div>

            {strategist_plan && (
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Viability Score
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>
                  <span className={`badge ${strategist_plan.viability_score >= 70 ? 'badge-success' : strategist_plan.viability_score >= 50 ? 'badge-warning' : 'badge-error'}`} style={{ fontSize: '1rem' }}>
                    {strategist_plan.viability_score}%
                  </span>
                </div>
              </div>
            )}

            {result.coordination_iteration > 0 && (
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Coordination Loops
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--gray-900)' }}>
                  {result.coordination_iteration} iteration{result.coordination_iteration > 1 ? 's' : ''}
                </div>
              </div>
            )}

            {result.loop_count > 0 && !result.coordination_iteration && (
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Quality Loops (Legacy)
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--gray-900)' }}>
                  {result.loop_count} iteration{result.loop_count > 1 ? 's' : ''}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
