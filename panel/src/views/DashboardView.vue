<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="service in services" :key="service.name">
        <el-card class="service-card">
          <template #header>
            <div class="card-header">
              <span>{{ service.name }}</span>
              <el-tag :type="service.status === 'running' ? 'success' : 'danger'">
                {{ service.status }}
              </el-tag>
            </div>
          </template>
          <div class="service-info">
            <p>运行时间: {{ formatUptime(service.uptime) }}</p>
            <p v-if="service.pid">PID: {{ service.pid }}</p>
          </div>
          <div class="service-actions">
            <el-button size="small" @click="toggleService(service)">
              {{ service.status === 'running' ? '停止' : '启动' }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>系统信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="版本">{{ version }}</el-descriptions-item>
            <el-descriptions-item label="运行模式">{{ mode }}</el-descriptions-item>
            <el-descriptions-item label="总运行时间">{{ totalUptime }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>快速操作</template>
          <el-space wrap>
            <el-button type="primary" @click="startAll">启动全部</el-button>
            <el-button type="danger" @click="stopAll">停止全部</el-button>
            <el-button @click="refreshStatus">刷新状态</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const version = ref('0.1.0')
const mode = ref('development')
const totalUptime = ref('0s')

const services = ref([
  { name: 'Core', status: 'running', uptime: 3600, pid: 1234 },
  { name: 'ASR', status: 'running', uptime: 3500, pid: 1235 },
  { name: 'VRChat', status: 'stopped', uptime: null, pid: null },
  { name: 'Keyboard', status: 'running', uptime: 3600, pid: 1236 },
  { name: 'Web', status: 'running', uptime: 3600, pid: 1237 },
])

const formatUptime = (seconds) => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

const toggleService = (service) => {
  service.status = service.status === 'running' ? 'stopped' : 'running'
  ElMessage.success(`${service.name} 已${service.status === 'running' ? '启动' : '停止'}`)
}

const startAll = () => {
  services.value.forEach(s => s.status = 'running')
  ElMessage.success('所有服务已启动')
}

const stopAll = () => {
  services.value.forEach(s => s.status = 'stopped')
  ElMessage.warning('所有服务已停止')
}

const refreshStatus = () => {
  ElMessage.info('状态已刷新')
}

onMounted(() => {
  refreshStatus()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.service-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-info {
  margin-bottom: 10px;
  color: #666;
}

.service-actions {
  text-align: right;
}
</style>
