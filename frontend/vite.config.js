import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const backendPort = process.env.BACKEND_PORT || process.env.PSO_API_PORT || '8000'
const frontendPort = Number(process.env.FRONTEND_PORT || '5173')
const apiTarget = process.env.VITE_API_TARGET || `http://127.0.0.1:${backendPort}`

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: frontendPort,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true
      }
    }
  }
})
