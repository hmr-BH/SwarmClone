<script setup lang="ts">
import { RouterView } from 'vue-router'
import ServiceStatus from '@/components/ServiceStatus.vue'
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1>SwarmClone 控制面板</h1>
    </header>
    <main class="app-main">
      <aside class="app-sidebar">
        <ServiceStatus />
      </aside>
      <section class="app-content">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.app-header {
  background: #409eff;
  color: white;
  padding: 16px 24px;
}

.app-header h1 {
  font-size: 20px;
  font-weight: 500;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  width: 280px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  padding: 16px;
  overflow-y: auto;
}

.app-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
