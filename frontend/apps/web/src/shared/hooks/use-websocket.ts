'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export type WebSocketMessage =
  | { type: 'connected'; sessionId: string; message: string }
  | { type: 'new_message'; message: any }
  | { type: 'session_updated'; session: any }
  | { type: 'pong' }
  | { type: 'error'; message: string };

interface UseWebSocketOptions {
  enabled?: boolean;
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export function useWebSocket(
  sessionId: string,
  onMessage: (msg: WebSocketMessage) => void,
  onError?: (error: string) => void,
  options: UseWebSocketOptions = {}
) {
  const {
    enabled = true,
    autoConnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 3000,
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    if (!enabled || !sessionId) return;

    try {
      // Construct WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const url = `${protocol}//${host}/api/v1/roundtable/ws/sessions/${sessionId}`;

      const ws = new WebSocket(url);

      ws.onopen = () => {
        reconnectCountRef.current = 0;
        setConnected(true);
        setError(null);
        console.log('[WebSocket] Connected to session:', sessionId);

        // Send ping every 30 seconds to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          onMessage(message);
        } catch (e) {
          console.error('[WebSocket] Failed to parse message:', e);
        }
      };

      ws.onerror = (event) => {
        const errorMsg = `WebSocket error: ${event.type}`;
        console.error('[WebSocket]', errorMsg);
        setError(errorMsg);
        onError?.(errorMsg);
      };

      ws.onclose = () => {
        setConnected(false);
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        // Attempt to reconnect if not explicitly closed
        if (enabled && reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current++;
          console.log(
            `[WebSocket] Reconnecting... (attempt ${reconnectCountRef.current}/${reconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay * reconnectCountRef.current); // Exponential backoff
        }
      };

      wsRef.current = ws;
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : 'Unknown error';
      console.error('[WebSocket] Connection failed:', errorMsg);
      setError(errorMsg);
      onError?.(errorMsg);
    }
  }, [
    sessionId,
    enabled,
    onMessage,
    onError,
    reconnectAttempts,
    reconnectDelay,
  ]);

  const disconnect = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, []);

  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send message, WebSocket not connected');
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    connected,
    error,
    send,
    disconnect,
    connect,
  };
}
