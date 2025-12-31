export function ProgressDisplay({ events, isConnected }) {
  const agentInfo = {
    analyst: {
      name: 'Brand Analyst',
      icon: '🔍',
      description: 'Deconstructing brand DNA and core strengths',
    },
    researcher: {
      name: 'Market Researcher',
      icon: '📊',
      description: 'Analyzing market saturation and competition',
    },
    risk_analyst: {
      name: 'Risk Analyst',
      icon: '⚠️',
      description: 'Identifying threats, risks, and potential failure modes',
    },
    strategist: {
      name: 'Strategist',
      icon: '🎯',
      description: 'Coordinating research and synthesizing GTM strategy',
    },
  };

  const getAgentStatus = (agentName) => {
    const agentStarted = events.find(
      (e) => e.event === 'agent_started' && e.data.agent === agentName
    );
    const agentCompleted = events.find(
      (e) => e.event === 'agent_completed' && e.data.agent === agentName
    );

    if (agentCompleted) return 'completed';
    if (agentStarted) return 'active';
    return 'pending';
  };

  const hasAnalysisStarted = events.some((e) => e.event === 'analysis_started');
  const hasAnalysisCompleted = events.some((e) => e.event === 'analysis_completed');
  const coordinationEvents = events.filter((e) => e.event === 'coordination_follow_up');
  const loopEvents = events.filter((e) => e.event === 'loop_triggered'); // Legacy support
  const keepaliveEvents = events.filter((e) => e.event === 'keepalive');
  const latestKeepalive = keepaliveEvents[keepaliveEvents.length - 1];

  if (!hasAnalysisStarted && !isConnected) {
    return null;
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Analysis Progress</h2>
        {isConnected && !hasAnalysisCompleted && (
          <span className="badge badge-info" style={{ marginLeft: '1rem' }}>
            🔴 Live
          </span>
        )}
        {hasAnalysisCompleted && (
          <span className="badge badge-success" style={{ marginLeft: '1rem' }}>
            ✓ Complete
          </span>
        )}
        {latestKeepalive && !hasAnalysisCompleted && (
          <span className="badge badge-info" style={{ marginLeft: '1rem' }}>
            ⏱️ {latestKeepalive.data.elapsed_seconds}s elapsed
          </span>
        )}
      </div>

      <div className="progress-container">
        {Object.entries(agentInfo).map(([key, info]) => {
          const status = getAgentStatus(key);
          return (
            <div
              key={key}
              className={`progress-step ${status}`}
            >
              <div className="progress-icon">{info.icon}</div>
              <div className="progress-content">
                <div className="progress-title">{info.name}</div>
                <div className="progress-description">{info.description}</div>
              </div>
              {status === 'completed' && <span style={{ fontSize: '1.5rem' }}>✓</span>}
              {status === 'active' && (
                <span className="spinner" style={{ width: '24px', height: '24px', borderWidth: '3px' }}></span>
              )}
            </div>
          );
        })}

        {coordinationEvents.length > 0 && (
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--info-color)', borderRadius: 'var(--border-radius)', color: 'white' }}>
            <strong>🔄 Strategist Coordination Active</strong>
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
              The Strategist is requesting targeted follow-up research. Coordination iteration {coordinationEvents.length} in progress...
            </p>
            {coordinationEvents[coordinationEvents.length - 1].data.query && (
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', fontStyle: 'italic' }}>
                Focus: {coordinationEvents[coordinationEvents.length - 1].data.query}
              </p>
            )}
          </div>
        )}

        {loopEvents.length > 0 && coordinationEvents.length === 0 && (
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--warning-color)', borderRadius: 'var(--border-radius)', color: 'white' }}>
            <strong>🔄 Quality Loop Triggered (Legacy)</strong>
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
              Deeper analysis requested. Iteration {loopEvents.length + 1} in progress...
            </p>
            {loopEvents[loopEvents.length - 1].data.reason && (
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', fontStyle: 'italic' }}>
                Reason: {loopEvents[loopEvents.length - 1].data.reason}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
