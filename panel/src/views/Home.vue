<script setup lang="ts">
import { useWebSocket } from '@/composables/useWebSocket'
import { useServicesStore } from '@/stores/services'
import { ElCard, ElButton, ElProgress } from 'element-plus'
import LogViewer from '@/components/LogViewer.vue'

const { status, send } = useWebSocket('ws://127.0.0.1:8765')
const store = useServicesStore()

const testMessage = () => {
  send({
    type: 'status',
    source: 'panel',
    data: { test: true },
  })
}
</script>

<template>
  <div class="home">
    <ElCard class="status-card">
      <template #header>
        <span>系统状态</span>
      </template>
      <div class="status-content">
        <div class="status-item">
          <span>WebSocket 连接:</span>
          <span :class="status.connected ? 'connected' : 'disconnected'">
            {{ status.connected ? '已连接' : '未连接' }}
          </span>
        </div>
        <div class="status-item">
          <span>运行中服务:</span>
          <span>{{ store.runningCount }} / {{ store.services.length }}</span>
        </div>
      </div>
      <div class="status-actions">
        <ElButton
          type="primary"
          :disabled="!status.connected"
          @click="testMessage"
        >
          发送测试消息
        </ElButton>
      </div>
    </ElCard>

    <LogViewer />
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.status-card {
  margin-bottom: 16px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.connected {
  color: #67c23a;
  font-weight: 500;
}

.disconnected {
  color: #f56c6c;
  font-weight: 500;
}

.status-actions {
  display: flex;
  gap: 12px;
}
</style>
