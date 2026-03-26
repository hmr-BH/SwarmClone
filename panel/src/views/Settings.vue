<script setup lang="ts">
import { ref } from 'vue'
import { ElCard, ElForm, ElFormItem, ElInput, ElButton, ElSwitch } from 'element-plus'

const form = ref({
  host: '127.0.0.1',
  port: 8765,
  logLevel: 'INFO',
  debug: false,
})

const saveSettings = () => {
  console.log('保存设置:', form.value)
}
</script>

<template>
  <div class="settings">
    <ElCard>
      <template #header>
        <span>系统设置</span>
      </template>
      <ElForm :model="form" label-width="120px">
        <ElFormItem label="主机地址">
          <ElInput v-model="form.host" placeholder="127.0.0.1" />
        </ElFormItem>
        <ElFormItem label="端口">
          <ElInput v-model="form.port" placeholder="8765" />
        </ElFormItem>
        <ElFormItem label="日志级别">
          <ElInput v-model="form.logLevel" placeholder="INFO" />
        </ElFormItem>
        <ElFormItem label="调试模式">
          <ElSwitch v-model="form.debug" />
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" @click="saveSettings">保存设置</ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>
  </div>
</template>

<style scoped>
.settings {
  max-width: 600px;
}
</style>
