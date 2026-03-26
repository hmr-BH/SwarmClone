<template>
  <div class="actions-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>动作映射配置</span>
          <el-button type="primary" @click="addMapping">添加映射</el-button>
        </div>
      </template>
      
      <el-table :data="mappings" border>
        <el-table-column prop="trigger" label="触发条件" width="200" />
        <el-table-column prop="actionName" label="动作名称" width="150" />
        <el-table-column prop="actionType" label="动作类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.actionType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cooldown" label="冷却时间" width="100">
          <template #default="{ row }">
            {{ row.cooldown }}s
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row, $index }">
            <el-button size="small" @click="editMapping(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteMapping($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>动作测试</template>
      <el-form inline>
        <el-form-item label="触发条件">
          <el-input v-model="testTrigger" placeholder="输入触发条件" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="testAction">测试</el-button>
        </el-form-item>
      </el-form>
      <el-alert v-if="testResult" :title="testResult" type="success" show-icon style="margin-top: 10px;" />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const mappings = ref([
  { trigger: '你好', actionName: 'wave', actionType: 'gesture', cooldown: 2.0, enabled: true },
  { trigger: '谢谢', actionName: 'bow', actionType: 'gesture', cooldown: 2.0, enabled: true },
  { trigger: '开心', actionName: 'happy', actionType: 'expression', cooldown: 1.0, enabled: true },
  { trigger: '难过', actionName: 'sad', actionType: 'expression', cooldown: 1.0, enabled: true },
])

const testTrigger = ref('')
const testResult = ref('')

const addMapping = () => {
  ElMessage.info('添加映射功能开发中')
}

const editMapping = (row) => {
  ElMessage.info(`编辑映射: ${row.trigger}`)
}

const deleteMapping = (index) => {
  ElMessageBox.confirm('确定要删除此映射吗？', '提示', {
    type: 'warning'
  }).then(() => {
    mappings.value.splice(index, 1)
    ElMessage.success('已删除')
  }).catch(() => {})
}

const testAction = () => {
  if (!testTrigger.value) {
    ElMessage.warning('请输入触发条件')
    return
  }
  testResult.value = `触发条件 "${testTrigger.value}" 已执行`
  ElMessage.success('动作已触发')
}
</script>

<style scoped>
.actions-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
