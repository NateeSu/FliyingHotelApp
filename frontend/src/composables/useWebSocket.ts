/**
 * useWebSocket Composable (Phase 3)
 * Vue 3 composable for WebSocket connection management
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import type {
  WebSocketMessage,
  WebSocketConnectionState,
  WebSocketEventType
} from '@/types/websocket'

interface UseWebSocketOptions {
  url?: string
  autoConnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

type EventHandler<T = any> = (data: T) => void

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    url = `ws://${window.location.hostname}:8000/api/v1/ws/dashboard`,
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10
  } = options

  // WebSocket instance
  let ws: WebSocket | null = null
  let reconnectAttempts = 0
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let pingTimer: ReturnType<typeof setInterval> | null = null

  // State
  const connectionState = ref<WebSocketConnectionState>({
    connected: false,
    connecting: false,
    error: null,
    client_id: null
  })

  // Event handlers registry
  const eventHandlers = new Map<string, Set<EventHandler>>()

  // Computed
  const isConnected = computed(() => connectionState.value.connected)
  const isConnecting = computed(() => connectionState.value.connecting)
  const hasError = computed(() => connectionState.value.error !== null)
  const clientId = computed(() => connectionState.value.client_id)

  /**
   * Register event handler
   */
  function on<T = any>(event: WebSocketEventType | string, handler: EventHandler<T>) {
    if (!eventHandlers.has(event)) {
      eventHandlers.set(event, new Set())
    }
    eventHandlers.get(event)!.add(handler)
  }

  /**
   * Unregister event handler
   */
  function off<T = any>(event: WebSocketEventType | string, handler: EventHandler<T>) {
    const handlers = eventHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        eventHandlers.delete(event)
      }
    }
  }

  /**
   * Emit event to all registered handlers
   */
  function emit(event: string, data: any) {
    const handlers = eventHandlers.get(event)
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in WebSocket event handler for "${event}":`, error)
        }
      })
    }
  }

  /**
   * Start ping/pong mechanism to keep connection alive
   */
  function startPing() {
    if (pingTimer) {
      clearInterval(pingTimer)
    }
    pingTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        send({ type: 'ping' })
      }
    }, 30000) // Every 30 seconds
  }

  /**
   * Stop ping timer
   */
  function stopPing() {
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  function handleMessage(event: MessageEvent) {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)

      // Handle connected event
      if (message.event === 'connected') {
        connectionState.value.client_id = message.data.client_id
        console.log('WebSocket connected:', message.data.message)
      }

      // Handle pong response
      if (message.event === 'pong') {
        return
      }

      // Emit event to registered handlers
      emit(message.event, message.data)
      emit('*', message) // Wildcard handler for all events
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  /**
   * Connect to WebSocket server
   */
  function connect() {
    if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
      console.warn('WebSocket is already connected or connecting')
      return
    }

    connectionState.value.connecting = true
    connectionState.value.error = null

    try {
      // Add client_id to URL if available for reconnection
      const wsUrl =
        connectionState.value.client_id
          ? `${url}?client_id=${connectionState.value.client_id}`
          : url

      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket connection opened')
        connectionState.value.connected = true
        connectionState.value.connecting = false
        connectionState.value.error = null
        reconnectAttempts = 0

        // Start ping mechanism
        startPing()

        // Emit open event
        emit('open', null)
      }

      ws.onmessage = handleMessage

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        connectionState.value.error = 'เกิดข้อผิดพลาดในการเชื่อมต่อ'
        emit('error', error)
      }

      ws.onclose = (event) => {
        console.log('WebSocket connection closed', event)
        connectionState.value.connected = false
        connectionState.value.connecting = false

        // Stop ping timer
        stopPing()

        // Emit close event
        emit('close', event)

        // Attempt to reconnect if not closed intentionally
        if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
          attemptReconnect()
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          connectionState.value.error = `ไม่สามารถเชื่อมต่อใหม่ได้หลังจากพยายาม ${maxReconnectAttempts} ครั้ง`
        }
      }
    } catch (error) {
      console.error('Error creating WebSocket:', error)
      connectionState.value.connected = false
      connectionState.value.connecting = false
      connectionState.value.error = 'ไม่สามารถสร้างการเชื่อมต่อ WebSocket ได้'
    }
  }

  /**
   * Attempt to reconnect
   */
  function attemptReconnect() {
    if (reconnectTimer) {
      return
    }

    reconnectAttempts++
    console.log(
      `Attempting to reconnect... (${reconnectAttempts}/${maxReconnectAttempts})`
    )

    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connect()
    }, reconnectInterval)
  }

  /**
   * Disconnect from WebSocket server
   */
  function disconnect() {
    // Clear reconnect timer
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    // Stop ping timer
    stopPing()

    // Close WebSocket
    if (ws) {
      ws.close(1000, 'Client disconnecting')
      ws = null
    }

    connectionState.value.connected = false
    connectionState.value.connecting = false
    connectionState.value.error = null
  }

  /**
   * Send message to WebSocket server
   */
  function send(data: any) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify(data))
      } catch (error) {
        console.error('Error sending WebSocket message:', error)
      }
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  /**
   * Lifecycle hooks
   */
  onMounted(() => {
    if (autoConnect) {
      connect()
    }
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    // State
    connectionState,
    isConnected,
    isConnecting,
    hasError,
    clientId,

    // Methods
    connect,
    disconnect,
    send,
    on,
    off
  }
}
