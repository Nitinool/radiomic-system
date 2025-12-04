<!-- src/App.vue -->
<template>
  <!-- 引入路由：显示我们的特征提取页面 -->
  <router-view />
</template>

<script setup>
// 导入路由
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
/* 全局样式：清除默认边距 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>