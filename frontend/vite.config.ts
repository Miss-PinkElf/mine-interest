import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const LOCAL_BACKEND_TARGET = 'http://127.0.0.1:8000'
const API_PATH_PREFIX = '/api'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      [API_PATH_PREFIX]: LOCAL_BACKEND_TARGET,
    },
  },
})
