<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <el-aside width="200px">
        <el-menu
          :default-active="$route.path"
          router
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="/">
            <el-icon><Monitor /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/config">
            <el-icon><Setting /></el-icon>
            <span>配置管理</span>
          </el-menu-item>
          <el-menu-item index="/actions">
            <el-icon><Operation /></el-icon>
            <span>动作管理</span>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Document /></el-icon>
            <span>日志查看</span>
          </el-menu-item>
          <el-menu-item index="/model">
            <el-icon><User /></el-icon>
            <span>模型预览</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

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
  height: 100%;
}

.el-aside {
  background-color: #545c64;
}

.el-menu {
  border-right: none;
}
</style>
