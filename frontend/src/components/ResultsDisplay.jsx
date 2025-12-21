export function ResultsDisplay({ result }) {
  if (!result) {
    return null;
  }

  const {
    analyst_insights,
    researcher_findings,
    skeptic_critique,
    strategist_plan,
  } = result;

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
            <p style={{ color: 'var(--gray-700)', lineHeight: 1.6 }}>{analyst_insights.business_model}</p>
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
            <p style={{ color: 'var(--gray-700)', lineHeight: 1.6, marginBottom: '1rem' }}>
              <strong>Market:</strong> {researcher_findings.market_name}
            </p>
            {researcher_findings.market_size && (
              <p style={{ color: 'var(--gray-700)', lineHeight: 1.6, marginBottom: '1rem' }}>
                <strong>Size:</strong> {researcher_findings.market_size}
              </p>
            )}
            <p style={{ color: 'var(--gray-700)', lineHeight: 1.6 }}>
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

      {/* Skeptic Critique */}
      {skeptic_critique && (
        <div className="card">
          <div className="card-header">
            <h2>🤔 Critical Analysis</h2>
          </div>

          {skeptic_critique.concerns.length > 0 && (
            <div className="result-section">
              <h3>Concerns</h3>
              <ul className="result-list">
                {skeptic_critique.concerns.map((concern, index) => (
                  <li key={index}>{concern}</li>
                ))}
              </ul>
            </div>
          )}

          {skeptic_critique.fatal_flaws.length > 0 && (
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

          {skeptic_critique.suggestions.length > 0 && (
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
            <p style={{ color: 'var(--gray-700)', lineHeight: 1.6 }}>{strategist_plan.target_audience}</p>
          </div>

          <div className="result-section">
            <h3>Value Proposition</h3>
            <p style={{ color: 'var(--gray-700)', lineHeight: 1.6 }}>{strategist_plan.value_proposition}</p>
          </div>

          {strategist_plan.pricing_strategy && (
            <div className="result-section">
              <h3>Pricing Strategy</h3>
              <p style={{ color: 'var(--gray-700)', lineHeight: 1.6 }}>{strategist_plan.pricing_strategy}</p>
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
                  <li key={index}>{risk}</li>
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
              <p style={{ color: 'var(--gray-700)', lineHeight: 1.6 }}>{strategist_plan.timeline}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
