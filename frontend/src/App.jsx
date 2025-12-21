import { useState } from 'react';
import { AnalysisForm } from './components/AnalysisForm';
import { ProgressDisplay } from './components/ProgressDisplay';
import { MetricsDashboard } from './components/MetricsDashboard';
import { ResultsDisplay } from './components/ResultsDisplay';
import { useSSE } from './hooks/useSSE';
import './styles/index.css';

function App() {
  const [analysisRequest, setAnalysisRequest] = useState(null);
  const [shouldAnalyze, setShouldAnalyze] = useState(false);

  const { events, isConnected, error, result } = useSSE(
    '/api/analyze/stream',
    analysisRequest,
    shouldAnalyze
  );

  const handleSubmit = (request) => {
    setAnalysisRequest(request);
    setShouldAnalyze(true);
  };

  const handleReset = () => {
    setAnalysisRequest(null);
    setShouldAnalyze(false);
  };

  const hasResults = result !== null;
  const isAnalyzing = isConnected || (shouldAnalyze && !hasResults && !error);

  return (
    <div className="container">
      <div className="header">
        <h1>🚀 Startup Analyzer</h1>
        <p>AI-Powered "X for Y" Business Idea Analysis</p>
      </div>

      {!isAnalyzing && !hasResults && (
        <AnalysisForm onSubmit={handleSubmit} isLoading={false} />
      )}

      {error && (
        <div className="card">
          <div className="error-message">
            <strong>Error:</strong> {error.error || 'An error occurred during analysis'}
            {error.error_type && (
              <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                Type: {error.error_type}
              </div>
            )}
          </div>
          <button
            onClick={handleReset}
            className="btn btn-primary"
            style={{ marginTop: '1rem' }}
          >
            Try Again
          </button>
        </div>
      )}

      {(isAnalyzing || hasResults) && (
        <>
          {analysisRequest && (
            <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <h2 style={{ marginBottom: '0.5rem', fontSize: '1.5rem' }}>
                Analyzing: {analysisRequest.x_brand} for {analysisRequest.y_market}
              </h2>
              {analysisRequest.description && (
                <p style={{ opacity: 0.9 }}>{analysisRequest.description}</p>
              )}
            </div>
          )}

          <ProgressDisplay events={events} isConnected={isConnected} />

          {hasResults && (
            <>
              <MetricsDashboard result={result} />
              <ResultsDisplay result={result} />

              <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                  onClick={handleReset}
                  className="btn btn-primary btn-lg"
                >
                  Analyze Another Idea
                </button>
              </div>
            </>
          )}

          {isAnalyzing && !hasResults && (
            <div className="card">
              <div className="loading">
                <div style={{ textAlign: 'center' }}>
                  <div className="spinner"></div>
                  <p style={{ marginTop: '1rem', color: 'var(--gray-600)' }}>
                    Multi-agent analysis in progress...
                  </p>
                  <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--gray-500)' }}>
                    This may take 30-60 seconds
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {!isAnalyzing && !hasResults && !error && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">💡</div>
            <div className="empty-state-text">
              Enter your "X for Y" idea above to get started with AI-powered analysis
            </div>
            <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--gray-500)' }}>
              Our multi-agent system will analyze your idea through brand analysis,
              market research, critical evaluation, and strategic planning.
            </p>
          </div>
        </div>
      )}

      <footer style={{ textAlign: 'center', marginTop: '3rem', paddingBottom: '2rem', color: 'white', opacity: 0.8 }}>
        <p>Powered by GPT-4o via OpenRouter | Real-time SSE Streaming</p>
      </footer>
    </div>
  );
}

export default App;
