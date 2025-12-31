import { useState, useEffect, useRef } from 'react';
const API_BASE_URL = import.meta.env.VITE_API_URL || '';
/**
 * Custom hook for Server-Sent Events (SSE) streaming
 *
 * @param {string} url - The SSE endpoint URL
 * @param {object} body - The request body to send
 * @param {boolean} shouldConnect - Whether to establish the connection
 * @returns {object} - SSE state and control functions
 */
export function useSSE(url, body, shouldConnect = false) {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const eventSourceRef = useRef(null);

  // Reset state when shouldConnect becomes false (user clicked reset)
  useEffect(() => {
    if (!shouldConnect) {
      setEvents([]);
      setError(null);
      setResult(null);
      setIsConnected(false);
    }
  }, [shouldConnect]);

  useEffect(() => {
    if (!shouldConnect || !url || !body) {
      return;
    }

    const connect = async () => {
      try {
        console.log('[SSE] Starting connection...');
        setIsConnected(true);
        setError(null);
        setEvents([]);
        setResult(null);

        // Make the POST request to initiate SSE
        const response = await fetch(`${API_BASE_URL}${url}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(body),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = '';

        // Helper function to process lines
        const processLines = (lines) => {
          let currentEvent = null;

          console.log(`[SSE] processLines called with ${lines.length} lines`);

          for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            console.log(`[SSE] Line ${i}: "${line.substring(0, 50)}${line.length > 50 ? '...' : ''}"`);

            if (line.startsWith('event:')) {
              currentEvent = line.substring(6).trim();
              console.log(`[SSE] Found event: ${currentEvent}`);
            } else if (line.startsWith('data:')) {
              const data = line.substring(5).trim();
              console.log(`[SSE] Found data line, currentEvent: ${currentEvent}, data length: ${data.length}`);

              if (data && currentEvent) {
                try {
                  console.log(`[SSE] Parsing event: ${currentEvent}, data length: ${data.length}`);
                  const parsedData = JSON.parse(data);
                  const event = {
                    event: currentEvent,
                    data: parsedData,
                    timestamp: new Date().toISOString(),
                  };

                  setEvents(prev => [...prev, event]);

                  console.log(`[SSE] Received event: ${currentEvent}`, { timestamp: event.timestamp });

                  // Store the final result
                  if (currentEvent === 'result') {
                    console.log('[SSE] Final result received, setting result state');
                    console.log('[SSE] Result keys:', Object.keys(parsedData));
                    setResult(parsedData);
                    // Note: Stream should close after this, but connection may take a moment
                  }

                  // Handle errors
                  if (currentEvent === 'error') {
                    console.error('[SSE] Error event received:', parsedData);
                    setError(parsedData);
                  }
                } catch (e) {
                  console.error('[SSE] Error parsing SSE data:', e);
                  console.error('[SSE] Failed event:', currentEvent, 'data preview:', data.substring(0, 100));
                }
              } else {
                console.log(`[SSE] Skipping data line - data: ${!!data}, currentEvent: ${currentEvent}`);
              }

              currentEvent = null;
            } else if (line.trim() === '') {
              console.log(`[SSE] Empty line (event separator)`);
            } else {
              console.log(`[SSE] Unrecognized line format: "${line.substring(0, 30)}"`);
            }
          }
        };

        while (true) {
          const { done, value } = await reader.read();

          // IMPORTANT: Process the final chunk even when done=true
          if (value && value.length > 0) {
            buffer += decoder.decode(value, { stream: true });
          }

          if (done) {
            // IMPORTANT: Process any remaining buffered data before breaking
            console.log('[SSE] Stream done. Buffer length:', buffer.length);
            console.log('[SSE] Buffer contains "result":', buffer.includes('result'));
            if (buffer.trim()) {
              console.log('[SSE] Processing remaining buffer, first 200 chars:', buffer.substring(0, 200));
              const lines = buffer.split('\n');
              console.log('[SSE] Buffer split into', lines.length, 'lines');
              processLines(lines);
            }
            console.log('[SSE] Stream done, final buffer processed');
            break;
          }

          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          processLines(lines);
        }

        console.log('[SSE] Stream ended naturally, closing connection');
        setIsConnected(false);
      } catch (err) {
        console.error('[SSE] Connection error:', err);
        setError({
          error: err.message,
          error_type: 'ConnectionError',
        });
        setIsConnected(false);
      }
    };

    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [url, body, shouldConnect]);

  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      setIsConnected(false);
    }
  };

  return {
    events,
    isConnected,
    error,
    result,
    disconnect,
  };
}
