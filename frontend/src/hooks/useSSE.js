import { useState, useEffect, useRef } from 'react';

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

  useEffect(() => {
    if (!shouldConnect || !url || !body) {
      return;
    }

    const connect = async () => {
      try {
        setIsConnected(true);
        setError(null);
        setEvents([]);
        setResult(null);

        // Make the POST request to initiate SSE
        const response = await fetch(url, {
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

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          let currentEvent = null;

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEvent = line.substring(6).trim();
            } else if (line.startsWith('data:')) {
              const data = line.substring(5).trim();

              if (data && currentEvent) {
                try {
                  const parsedData = JSON.parse(data);
                  const event = {
                    event: currentEvent,
                    data: parsedData,
                    timestamp: new Date().toISOString(),
                  };

                  setEvents(prev => [...prev, event]);

                  // Store the final result
                  if (currentEvent === 'result') {
                    setResult(parsedData);
                  }

                  // Handle errors
                  if (currentEvent === 'error') {
                    setError(parsedData);
                  }
                } catch (e) {
                  console.error('Error parsing SSE data:', e);
                }
              }

              currentEvent = null;
            }
          }
        }

        setIsConnected(false);
      } catch (err) {
        console.error('SSE connection error:', err);
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
