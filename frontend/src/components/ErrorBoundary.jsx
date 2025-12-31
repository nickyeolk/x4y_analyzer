import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to state so we can display it
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    console.error('Error type:', typeof error);
    console.error('Error keys:', error ? Object.keys(error) : 'null');
    console.error('Error string:', String(error));

    // Use setState instead of direct mutation
    this.setState({
      hasError: true,
      error: error,
      errorInfo: errorInfo,
    });
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI when there's an error
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          background: '#f3f4f6',
        }}>
          <div style={{
            maxWidth: '800px',
            width: '100%',
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
            padding: '32px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              marginBottom: '24px',
            }}>
              <div style={{
                fontSize: '48px',
              }}>
                💥
              </div>
              <div>
                <h1 style={{
                  fontSize: '24px',
                  fontWeight: 700,
                  color: '#dc2626',
                  margin: 0,
                }}>
                  Something Went Wrong
                </h1>
                <p style={{
                  fontSize: '14px',
                  color: '#6b7280',
                  margin: '4px 0 0 0',
                }}>
                  The application encountered an error and needs to reload
                </p>
              </div>
            </div>

            {/* Error Details */}
            <div style={{
              background: '#fee2e2',
              border: '2px solid #ef4444',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px',
            }}>
              <h3 style={{
                fontSize: '14px',
                fontWeight: 600,
                color: '#991b1b',
                margin: '0 0 8px 0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                Error Message:
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#7f1d1d',
                margin: 0,
                fontFamily: 'monospace',
                wordBreak: 'break-word',
              }}>
                {this.state.error?.message || this.state.error?.toString() || String(this.state.error) || 'Unknown error - check console logs in debug panel'}
              </p>
            </div>

            {/* Stack Trace */}
            {this.state.errorInfo && (
              <details style={{
                background: '#1e1e1e',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '24px',
                cursor: 'pointer',
              }}>
                <summary style={{
                  color: '#d4d4d4',
                  fontSize: '14px',
                  fontWeight: 600,
                  marginBottom: '8px',
                }}>
                  📋 Component Stack Trace
                </summary>
                <pre style={{
                  color: '#d4d4d4',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                  overflow: 'auto',
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}>
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            {/* Full Error Object */}
            <details style={{
              background: '#1e1e1e',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px',
              cursor: 'pointer',
            }}>
              <summary style={{
                color: '#d4d4d4',
                fontSize: '14px',
                fontWeight: 600,
                marginBottom: '8px',
              }}>
                🐛 Full Error Details (for debugging)
              </summary>
              <pre style={{
                color: '#d4d4d4',
                fontSize: '11px',
                fontFamily: 'monospace',
                overflow: 'auto',
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}>
                {JSON.stringify({
                  error: {
                    message: this.state.error?.message,
                    stack: this.state.error?.stack,
                    name: this.state.error?.name,
                  },
                  errorInfo: this.state.errorInfo,
                }, null, 2)}
              </pre>
            </details>

            {/* Action Buttons */}
            <div style={{
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap',
            }}>
              <button
                onClick={() => window.location.reload()}
                style={{
                  padding: '12px 24px',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(59, 130, 246, 0.3)',
                }}
              >
                🔄 Reload Page
              </button>
              <button
                onClick={() => {
                  const errorText = JSON.stringify({
                    error: this.state.error?.toString(),
                    stack: this.state.error?.stack,
                    componentStack: this.state.errorInfo?.componentStack,
                  }, null, 2);
                  navigator.clipboard?.writeText(errorText).then(() => {
                    alert('Error details copied to clipboard!');
                  });
                }}
                style={{
                  padding: '12px 24px',
                  background: '#6b7280',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                📋 Copy Error
              </button>
            </div>

            <p style={{
              marginTop: '24px',
              fontSize: '13px',
              color: '#6b7280',
              lineHeight: 1.6,
            }}>
              <strong>What to do:</strong><br/>
              1. Take a screenshot of this error<br/>
              2. Click "Copy Error" to copy error details<br/>
              3. Click "Reload Page" to try again<br/>
              4. Share the error details with the developer
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
