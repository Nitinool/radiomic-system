// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
// 导入路由配置
import router from './router/index.js'

// 创建Vue应用，并使用路由
const app = createApp(App)
app.use(router)  // 启用路由
app.mount('#app')  // 挂载到页面