import { useState, useEffect } from 'react';

export function DebugPanel({ result, events, isConnected, error }) {
  const [isOpen, setIsOpen] = useState(false);
  const [logs, setLogs] = useState([]);

  // Intercept console.log and console.error
  useEffect(() => {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;

    console.log = (...args) => {
      originalLog(...args);
      setLogs(prev => [...prev, { type: 'log', message: args.join(' '), timestamp: new Date().toISOString() }]);
    };

    console.error = (...args) => {
      originalError(...args);
      setLogs(prev => [...prev, { type: 'error', message: args.join(' '), timestamp: new Date().toISOString() }]);
    };

    console.warn = (...args) => {
      originalWarn(...args);
      setLogs(prev => [...prev, { type: 'warn', message: args.join(' '), timestamp: new Date().toISOString() }]);
    };

    return () => {
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
    };
  }, []);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          padding: '12px 20px',
          background: 'var(--primary-color)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          fontSize: '14px',
          fontWeight: 600,
          zIndex: 9999,
        }}
      >
        🐛 Debug Panel
      </button>
    );
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '0',
        right: '0',
        width: '100%',
        maxWidth: '600px',
        maxHeight: '60vh',
        background: 'white',
        border: '2px solid var(--primary-color)',
        borderRadius: '8px 8px 0 0',
        boxShadow: '0 -4px 24px rgba(0,0,0,0.2)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 9999,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          background: 'var(--primary-color)',
          color: 'white',
          fontWeight: 600,
        }}
      >
        <span>🐛 Debug Panel</span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setLogs([])}
            style={{
              padding: '4px 12px',
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            Clear
          </button>
          <button
            onClick={() => setIsOpen(false)}
            style={{
              padding: '4px 12px',
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            Close
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ padding: '8px 16px', background: 'var(--gray-50)', borderBottom: '1px solid var(--gray-200)' }}>
        <div style={{ display: 'flex', gap: '12px', fontSize: '14px' }}>
          <button
            onClick={() => document.getElementById('debug-logs').scrollIntoView({ behavior: 'smooth' })}
            style={{ padding: '4px 8px', background: 'transparent', border: 'none', cursor: 'pointer', fontWeight: 600, color: 'var(--primary-color)' }}
          >
            Console ({logs.length})
          </button>
          <button
            onClick={() => document.getElementById('debug-result').scrollIntoView({ behavior: 'smooth' })}
            style={{ padding: '4px 8px', background: 'transparent', border: 'none', cursor: 'pointer', fontWeight: 600, color: 'var(--primary-color)' }}
          >
            Result
          </button>
          <button
            onClick={() => document.getElementById('debug-events').scrollIntoView({ behavior: 'smooth' })}
            style={{ padding: '4px 8px', background: 'transparent', border: 'none', cursor: 'pointer', fontWeight: 600, color: 'var(--primary-color)' }}
          >
            Events ({events?.length || 0})
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
        {/* Status */}
        <div style={{ marginBottom: '16px', padding: '12px', background: 'var(--gray-50)', borderRadius: '8px', fontSize: '14px' }}>
          <div><strong>Connected:</strong> {isConnected ? '✅ Yes' : '❌ No'}</div>
          <div><strong>Has Result:</strong> {result ? '✅ Yes' : '❌ No'}</div>
          <div><strong>Has Error:</strong> {error ? '⚠️ Yes' : '✅ No'}</div>
        </div>

        {/* Console Logs */}
        <div id="debug-logs" style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>Console Logs</h3>
          <div style={{ background: '#1e1e1e', color: '#d4d4d4', padding: '12px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px', maxHeight: '200px', overflow: 'auto' }}>
            {logs.length === 0 ? (
              <div style={{ color: '#888' }}>No logs yet...</div>
            ) : (
              logs.map((log, i) => (
                <div
                  key={i}
                  style={{
                    marginBottom: '4px',
                    color: log.type === 'error' ? '#f48771' : log.type === 'warn' ? '#dcdcaa' : '#d4d4d4',
                    wordBreak: 'break-word',
                  }}
                >
                  <span style={{ color: '#888' }}>[{new Date(log.timestamp).toLocaleTimeString()}]</span> {log.message}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Result */}
        <div id="debug-result" style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>Result Object</h3>
          <pre style={{ background: '#1e1e1e', color: '#d4d4d4', padding: '12px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '11px', overflow: 'auto', maxHeight: '300px' }}>
            {result ? JSON.stringify(result, null, 2) : 'No result yet'}
          </pre>
        </div>

        {/* Events */}
        <div id="debug-events" style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>SSE Events</h3>
          <pre style={{ background: '#1e1e1e', color: '#d4d4d4', padding: '12px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '11px', overflow: 'auto', maxHeight: '300px' }}>
            {events && events.length > 0 ? JSON.stringify(events, null, 2) : 'No events yet'}
          </pre>
        </div>

        {/* Error */}
        {error && (
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px', color: 'var(--error-color)' }}>Error</h3>
            <pre style={{ background: '#fee2e2', color: '#991b1b', padding: '12px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '11px', overflow: 'auto' }}>
              {JSON.stringify(error, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
