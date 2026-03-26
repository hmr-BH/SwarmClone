<template>
  <div class="config-view">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="系统配置" name="system">
        <el-form :model="systemConfig" label-width="120px">
          <el-form-item label="运行模式">
            <el-select v-model="systemConfig.mode">
              <el-option label="开发模式" value="development" />
              <el-option label="生产模式" value="production" />
            </el-select>
          </el-form-item>
          <el-form-item label="日志级别">
            <el-select v-model="systemConfig.logLevel">
              <el-option label="DEBUG" value="DEBUG" />
              <el-option label="INFO" value="INFO" />
              <el-option label="WARNING" value="WARNING" />
              <el-option label="ERROR" value="ERROR" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveSystemConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="Redis配置" name="redis">
        <el-form :model="redisConfig" label-width="120px">
          <el-form-item label="主机">
            <el-input v-model="redisConfig.host" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input-number v-model="redisConfig.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="数据库">
            <el-input-number v-model="redisConfig.db" :min="0" :max="15" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveRedisConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="ASR配置" name="asr">
        <el-form :model="asrConfig" label-width="120px">
          <el-form-item label="启用">
            <el-switch v-model="asrConfig.enabled" />
          </el-form-item>
          <el-form-item label="引擎">
            <el-select v-model="asrConfig.engine">
              <el-option label="Whisper" value="whisper" />
              <el-option label="Azure Speech" value="azure" />
            </el-select>
          </el-form-item>
          <el-form-item label="模型">
            <el-select v-model="asrConfig.model">
              <el-option label="Tiny" value="tiny" />
              <el-option label="Base" value="base" />
              <el-option label="Small" value="small" />
              <el-option label="Medium" value="medium" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveAsrConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="VRChat配置" name="vrchat">
        <el-form :model="vrchatConfig" label-width="120px">
          <el-form-item label="启用">
            <el-switch v-model="vrchatConfig.enabled" />
          </el-form-item>
          <el-form-item label="OSC地址">
            <el-input v-model="vrchatConfig.oscAddress" />
          </el-form-item>
          <el-form-item label="OSC端口">
            <el-input-number v-model="vrchatConfig.oscPort" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="自动重连">
            <el-switch v-model="vrchatConfig.autoReconnect" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveVrchatConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('system')

const systemConfig = ref({
  mode: 'development',
  logLevel: 'INFO'
})

const redisConfig = ref({
  host: 'localhost',
  port: 6379,
  db: 0
})

const asrConfig = ref({
  enabled: true,
  engine: 'whisper',
  model: 'base'
})

const vrchatConfig = ref({
  enabled: true,
  oscAddress: '127.0.0.1',
  oscPort: 9000,
  autoReconnect: true
})

const saveSystemConfig = () => ElMessage.success('系统配置已保存')
const saveRedisConfig = () => ElMessage.success('Redis配置已保存')
const saveAsrConfig = () => ElMessage.success('ASR配置已保存')
const saveVrchatConfig = () => ElMessage.success('VRChat配置已保存')
</script>

<style scoped>
.config-view {
  padding: 20px;
}
</style>
