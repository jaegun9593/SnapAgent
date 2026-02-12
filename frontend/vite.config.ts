import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

const isDocker = process.env.DOCKER === 'true'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
    ...(isDocker && {
      watch: {
        usePolling: true,
        interval: 1000,
      },
    }),
  },
})
