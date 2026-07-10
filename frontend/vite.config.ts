import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 本地 FastAPI 开发服务的回环地址。
const LOCAL_BACKEND_TARGET = 'http://127.0.0.1:8000'
// 需要由 Vite 开发服务器转发的 API 路径前缀。
const API_PATH_PREFIX = '/api'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      [API_PATH_PREFIX]: LOCAL_BACKEND_TARGET,
    },
  },
})
