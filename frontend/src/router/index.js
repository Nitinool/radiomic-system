// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
// 导入我们后续要创建的特征提取页面
import RadiomicsTest from '../views/RadiomicsTest.vue'

// 配置路由：访问根路径时，显示 RadiomicsTest 页面
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'radiomics',
      component: RadiomicsTest
    }
  ]
})

export default router