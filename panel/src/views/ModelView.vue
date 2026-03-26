<template>
  <div class="model-view">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>3D模型预览</span>
              <el-space>
                <el-button @click="loadModel">加载模型</el-button>
                <el-button @click="resetModel">重置</el-button>
              </el-space>
            </div>
          </template>
          <div class="model-preview">
            <div class="placeholder">
              <el-icon :size="64"><User /></el-icon>
              <p>模型预览区域</p>
              <p class="hint">支持 Live2D / VRM 模型</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>参数控制</template>
          <el-form label-width="100px">
            <el-form-item label="表情">
              <el-select v-model="currentExpression" @change="setExpression">
                <el-option label="默认" value="neutral" />
                <el-option label="开心" value="happy" />
                <el-option label="难过" value="sad" />
                <el-option label="生气" value="angry" />
                <el-option label="惊讶" value="surprised" />
              </el-select>
            </el-form-item>
            <el-form-item label="表情强度">
              <el-slider v-model="expressionIntensity" :min="0" :max="1" :step="0.1" />
            </el-form-item>
            <el-divider />
            <el-form-item label="动作">
              <el-select v-model="currentAction" @change="playAction">
                <el-option label="无" value="" />
                <el-option label="挥手" value="wave" />
                <el-option label="鞠躬" value="bow" />
                <el-option label="点头" value="nod" />
                <el-option label="摇头" value="shake" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card style="margin-top: 20px;">
          <template #header>VRChat状态</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="连接状态">
              <el-tag :type="vrchatConnected ? 'success' : 'danger'">
                {{ vrchatConnected ? '已连接' : '未连接' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Avatar ID">{{ avatarId || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const currentExpression = ref('neutral')
const expressionIntensity = ref(1.0)
const currentAction = ref('')
const vrchatConnected = ref(false)
const avatarId = ref('')

const loadModel = () => {
  ElMessage.info('请选择模型文件')
}

const resetModel = () => {
  currentExpression.value = 'neutral'
  expressionIntensity.value = 1.0
  currentAction.value = ''
  ElMessage.success('模型已重置')
}

const setExpression = () => {
  ElMessage.success(`设置表情: ${currentExpression.value}`)
}

const playAction = () => {
  if (currentAction.value) {
    ElMessage.success(`播放动作: ${currentAction.value}`)
  }
}
</script>

<style scoped>
.model-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-preview {
  height: 500px;
  background: #f5f5f5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder {
  text-align: center;
  color: #999;
}

.placeholder .hint {
  font-size: 12px;
  color: #bbb;
  margin-top: 10px;
}
</style>
