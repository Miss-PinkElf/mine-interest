import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// 需要由 Vite 开发服务器转发的 API 路径前缀。
const API_PATH_PREFIX = '/api'
// 后端默认回环地址；启动脚本可通过 BACKEND_TARGET 覆盖。
const DEFAULT_BACKEND_TARGET = 'http://127.0.0.1:8000'

export default defineConfig(({ mode }) => {
  // 读取进程环境变量，兼容一键启动脚本动态端口。
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget =
    process.env.BACKEND_TARGET ||
    env.BACKEND_TARGET ||
    DEFAULT_BACKEND_TARGET

  return {
    plugins: [react()],
    server: {
      // 允许脚本指定前端端口；未指定时使用 Vite 默认 5173。
      port: Number(process.env.FRONTEND_PORT || env.FRONTEND_PORT || 5173),
      strictPort: true,
      host: process.env.FRONTEND_HOST || '127.0.0.1',
      proxy: {
        [API_PATH_PREFIX]: {
          target: backendTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
