import { ref, onMounted, onUnmounted } from 'vue'

export interface WebSocketStatus {
  connected: boolean
  reconnecting: boolean
}

export function useWebSocket(url: string) {
  const status = ref<WebSocketStatus>({
    connected: false,
    reconnecting: false,
  })

  const lastMessage = ref<unknown>(null)
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const connect = () => {
    if (ws) {
      ws.close()
    }

    ws = new WebSocket(url)

    ws.onopen = () => {
      status.value.connected = true
      status.value.reconnecting = false
    }

    ws.onclose = () => {
      status.value.connected = false
      scheduleReconnect()
    }

    ws.onerror = () => {
      status.value.connected = false
    }

    ws.onmessage = (event) => {
      try {
        lastMessage.value = JSON.parse(event.data)
      } catch {
        lastMessage.value = event.data
      }
    }
  }

  const scheduleReconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }
    status.value.reconnecting = true
    reconnectTimer = setTimeout(() => {
      connect()
    }, 3000)
  }

  const send = (data: unknown) => {
    if (ws && status.value.connected) {
      ws.send(JSON.stringify(data))
    }
  }

  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }
    if (ws) {
      ws.close()
      ws = null
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    status,
    lastMessage,
    send,
    connect,
    disconnect,
  }
}
