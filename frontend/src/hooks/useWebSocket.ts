import { useEffect, useRef, useCallback } from 'react'
import { useAuthStore } from '../store/authStore'

interface Notification {
  type: string
  notification_type: string
  title: string
  message: string
  data: Record<string, unknown>
  timestamp: string
}

interface UseWebSocketOptions {
  onNotification?: (notification: Notification) => void
  onConnect?: () => void
  onDisconnect?: () => void
  autoReconnect?: boolean
  reconnectInterval?: number
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    onNotification,
    onConnect,
    onDisconnect,
    autoReconnect = true,
    reconnectInterval = 5000,
  } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const { token, isAuthenticated } = useAuthStore()
  const isConnected = useRef(false)

  const connect = useCallback(() => {
    if (!isAuthenticated || !token) return

    const wsUrl = `${import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000/api'}/ws/notifications?token=${token}`
    
    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        isConnected.current = true
        console.log('WebSocket connected')
        onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const data: Notification = JSON.parse(event.data)
          
          if (data.type === 'notification') {
            onNotification?.(data)
          } else if (data.type === 'pong') {
            // Heartbeat response
          } else {
            console.log('WebSocket message:', data)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onclose = () => {
        isConnected.current = false
        console.log('WebSocket disconnected')
        onDisconnect?.()

        if (autoReconnect && isAuthenticated) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...')
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        ws.close()
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }, [token, isAuthenticated, onConnect, onDisconnect, onNotification, autoReconnect, reconnectInterval])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    isConnected.current = false
  }, [])

  const send = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  const joinRoom = useCallback((room: string) => {
    send({ action: 'join_room', room })
  }, [send])

  const leaveRoom = useCallback((room: string) => {
    send({ action: 'leave_room', room })
  }, [send])

  const ping = useCallback(() => {
    send({ action: 'ping' })
  }, [send])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    isConnected: isConnected.current,
    connect,
    disconnect,
    send,
    joinRoom,
    leaveRoom,
    ping,
  }
}
