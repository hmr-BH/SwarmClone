<template>
  <div class="logs-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统日志</span>
          <el-space>
            <el-select v-model="logLevel" placeholder="日志级别" style="width: 120px;">
              <el-option label="全部" value="" />
              <el-option label="DEBUG" value="DEBUG" />
              <el-option label="INFO" value="INFO" />
              <el-option label="WARNING" value="WARNING" />
              <el-option label="ERROR" value="ERROR" />
            </el-select>
            <el-button @click="clearLogs">清空</el-button>
            <el-button @click="exportLogs">导出</el-button>
          </el-space>
        </div>
      </template>
      
      <div class="log-container" ref="logContainer">
        <div
          v-for="(log, index) in filteredLogs"
          :key="index"
          :class="['log-item', log.level.toLowerCase()]"
        >
          <span class="log-time">{{ log.time }}</span>
          <span :class="['log-level', log.level.toLowerCase()]">{{ log.level }}</span>
          <span class="log-source">{{ log.source }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const logLevel = ref('')
const logContainer = ref(null)

const logs = ref([
  { time: '2024-03-27 00:00:00', level: 'INFO', source: 'Core', message: '核心引擎已启动' },
  { time: '2024-03-27 00:00:01', level: 'INFO', source: 'ASR', message: 'ASR服务已连接' },
  { time: '2024-03-27 00:00:02', level: 'DEBUG', source: 'Core', message: '加载动作映射: 5个' },
  { time: '2024-03-27 00:01:00', level: 'WARNING', source: 'VRChat', message: 'VRChat未连接' },
  { time: '2024-03-27 00:02:00', level: 'INFO', source: 'Keyboard', message: '快捷键监听已启动' },
  { time: '2024-03-27 00:05:00', level: 'ERROR', source: 'ASR', message: '音频设备错误' },
])

const filteredLogs = computed(() => {
  if (!logLevel.value) return logs.value
  return logs.value.filter(log => log.level === logLevel.value)
})

const clearLogs = () => {
  logs.value = []
  ElMessage.success('日志已清空')
}

const exportLogs = () => {
  const content = logs.value.map(log => 
    `${log.time} [${log.level}] ${log.source}: ${log.message}`
  ).join('\n')
  
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `swarmclone-logs-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('日志已导出')
}
</script>

<style scoped>
.logs-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-container {
  height: 500px;
  overflow-y: auto;
  background: #1e1e1e;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
}

.log-item {
  padding: 4px 0;
  color: #d4d4d4;
}

.log-time {
  color: #6a9955;
  margin-right: 10px;
}

.log-level {
  padding: 2px 6px;
  border-radius: 3px;
  margin-right: 10px;
  font-weight: bold;
}

.log-level.debug { color: #608b4e; }
.log-level.info { color: #4ec9b0; }
.log-level.warning { color: #dcdcaa; }
.log-level.error { color: #f14c4c; }

.log-source {
  color: #569cd6;
  margin-right: 10px;
}

.log-message {
  color: #ce9178;
}
</style>
