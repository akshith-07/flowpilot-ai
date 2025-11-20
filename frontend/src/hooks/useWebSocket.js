import { useState, useEffect, useRef, useCallback } from 'react';
import { getAccessToken } from '@/utils/storage';

/**
 * Custom hook for WebSocket connections
 * @param {string} url - WebSocket URL
 * @param {Object} options - Configuration options
 * @returns {Object} WebSocket state and controls
 */
export const useWebSocket = (url, options = {}) => {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectInterval = 3000,
    reconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);

  const wsRef = useRef(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    try {
      // Add token to WebSocket URL
      const token = getAccessToken();
      const wsUrl = token ? `${url}?token=${token}` : url;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = (event) => {
        setIsConnected(true);
        setError(null);
        reconnectCountRef.current = 0;
        if (onOpen) onOpen(event);
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        if (onMessage) onMessage(data);
      };

      wsRef.current.onerror = (event) => {
        const errorMessage = 'WebSocket error occurred';
        setError(errorMessage);
        if (onError) onError(errorMessage);
      };

      wsRef.current.onclose = (event) => {
        setIsConnected(false);
        if (onClose) onClose(event);

        // Attempt reconnection
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else {
          setError('Failed to connect after multiple attempts');
        }
      };
    } catch (err) {
      setError(err.message);
      if (onError) onError(err.message);
    }
  }, [url, onMessage, onOpen, onClose, onError, reconnectInterval, reconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
};
