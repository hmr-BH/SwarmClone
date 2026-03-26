<script setup lang="ts">
import { useServicesStore } from '@/stores/services'
import { ElTag } from 'element-plus'

const store = useServicesStore()
</script>

<template>
  <div class="service-status">
    <h3>服务状态</h3>
    <div class="service-list">
      <div
        v-for="service in store.services"
        :key="service.id"
        class="service-item"
      >
        <span class="service-name">{{ service.name }}</span>
        <ElTag
          :type="
            service.status === 'running'
              ? 'success'
              : service.status === 'stopped'
                ? 'danger'
                : 'info'
          "
          size="small"
        >
          {{ service.status }}
        </ElTag>
      </div>
    </div>
  </div>
</template>

<style scoped>
.service-status {
  padding: 8px 0;
}

.service-status h3 {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
}

.service-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.service-name {
  font-size: 13px;
  color: #303133;
}
</style>
