<!-- src/views/RadiomicsTest.vue -->
<template>
  <div class="container">
    <h1>影像组学特征提取工具</h1>

    <!-- 文件上传区域 -->
    <div class="upload-box">
      <h3>请上传文件</h3>
      <!-- 影像文件上传 -->
      <div class="file-item">
        <label>影像文件（PNG/JPG）：</label>
        <input type="file" accept="image/png,image/jpeg" @change="handleUpload('image', $event)">
        <span class="file-name">{{ imageFile?.name || '未选择文件' }}</span>
      </div>

      <!-- ROI掩码文件上传 -->
      <div class="file-item">
        <label>ROI掩码文件（PNG/JPG）：</label>
        <input type="file" accept="image/png,image/jpeg" @change="handleUpload('roi', $event)">
        <span class="file-name">{{ roiFile?.name || '未选择文件' }}</span>
      </div>

      <!-- 提交按钮 -->
      <button class="submit-btn" @click="submit" :disabled="!imageFile || !roiFile">
        提交提取特征
      </button>
    </div>

    <!-- 加载状态 -->
    <div class="loading" v-if="isLoading">处理中，请稍候...</div>

    <!-- 结果展示区域 -->
    <div class="result-box" v-if="result">
      <h3>提取结果</h3>
      <div class="result-item">
        <h4>影像信息</h4>
        <p>尺寸：{{ result.image_info.尺寸 }}</p>
        <p>灰度范围：{{ result.image_info.灰度范围 }}</p>
      </div>
      <div class="result-item">
        <h4>ROI信息</h4>
        <p>尺寸：{{ result.roi_info.尺寸 }}</p>
        <p>有效像素数：{{ result.roi_info.有效像素数 }}</p>
      </div>
      <div class="result-item">
        <h4>特征值</h4>
        <ul>
          <li v-for="(value, key) in result.extracted_features" :key="key">
            {{ key }}：{{ value }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 错误提示 -->
    <div class="error" v-if="errorMsg">{{ errorMsg }}</div>
  </div>
</template>

<script setup>
// 导入需要的工具
import { ref } from 'vue'
import axios from 'axios'

// 存储上传的文件（响应式变量）
const imageFile = ref(null)  // 影像文件
const roiFile = ref(null)    // ROI掩码文件

// 存储状态：加载中、结果、错误信息
const isLoading = ref(false)
const result = ref(null)
const errorMsg = ref('')

// 处理文件上传（区分影像和ROI）
const handleUpload = (type, e) => {
  const file = e.target.files[0]
  if (file) {
    type === 'image' ? (imageFile.value = file) : (roiFile.value = file)
    errorMsg.value = ''
  }
}

// 提交请求到FastAPI接口
const submit = async () => {
  isLoading.value = true
  errorMsg.value = ''
  result.value = null

  try {
    const formData = new FormData()
    formData.append('image_file', imageFile.value)  // 键名必须和FastAPI接口参数一致
    formData.append('roi_file', roiFile.value)

    // 👇 关键：替换成你的FastAPI服务地址（端口要和你启动的一致！）
    const res = await axios.post(
      'http://127.0.0.1:8000/mock-extract-radiomics',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )

    result.value = res.data  // 保存接口返回结果
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '处理失败，请检查：1.后端服务是否启动 2.文件是否同尺寸 3.接口地址是否正确'
    console.error('错误：', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 50px auto;
  padding: 0 20px;
  font-family: Arial, sans-serif;
}
.upload-box {
  margin: 30px 0;
  padding: 25px;
  border: 1px dashed #ccc;
  border-radius: 8px;
}
.file-item {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.file-item label {
  width: 150px;
  font-weight: bold;
}
.file-item input {
  flex: 1;
  min-width: 200px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.file-name {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
  flex: 1 0 100%;
}
.submit-btn {
  padding: 12px 30px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.loading {
  text-align: center;
  color: #666;
  font-size: 18px;
  margin: 30px 0;
}
.result-box {
  margin-top: 30px;
  padding: 25px;
  border: 1px solid #eee;
  border-radius: 8px;
}
.result-item {
  margin-bottom: 25px;
}
.result-item h4 {
  margin-bottom: 10px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}
.result-item ul {
  list-style: none;
  padding: 0;
}
.result-item li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}
.error {
  text-align: center;
  color: #ff4d4f;
  font-size: 16px;
  margin: 30px 0;
}
</style>