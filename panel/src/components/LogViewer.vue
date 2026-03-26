<script setup lang="ts">
import { ref } from 'vue'
import { ElCard, ElButton, ElInput } from 'element-plus'

const logs = ref<string[]>([])
const newLog = ref('')

const addLog = () => {
  if (newLog.value.trim()) {
    logs.value.push(`[${new Date().toLocaleTimeString()}] ${newLog.value}`)
    newLog.value = ''
  }
}

const clearLogs = () => {
  logs.value = []
}
</script>

<template>
  <div class="log-viewer">
    <ElCard>
      <template #header>
        <div class="card-header">
          <span>日志查看器</span>
          <ElButton size="small" @click="clearLogs">清空</ElButton>
        </div>
      </template>
      <div class="log-content">
        <div v-for="(log, index) in logs" :key="index" class="log-item">
          {{ log }}
        </div>
        <div v-if="logs.length === 0" class="log-empty">暂无日志</div>
      </div>
      <div class="log-input">
        <ElInput
          v-model="newLog"
          placeholder="输入测试日志..."
          @keyup.enter="addLog"
        >
          <template #append>
            <ElButton @click="addLog">添加</ElButton>
          </template>
        </ElInput>
      </div>
    </ElCard>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-content {
  height: 200px;
  overflow-y: auto;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 16px;
}

.log-item {
  font-family: monospace;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid #ebeef5;
}

.log-empty {
  color: #909399;
  text-align: center;
  padding: 16px;
}
</style>
