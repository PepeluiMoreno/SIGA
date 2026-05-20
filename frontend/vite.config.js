import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 3000,
    allowedHosts: true,
    hmr: process.env.VITE_HMR_CLIENT_PORT
      ? { clientPort: parseInt(process.env.VITE_HMR_CLIENT_PORT) }
      : {},
    proxy: (() => {
      const target = process.env.VITE_BACKEND_URL || 'http://localhost:8000'
      return {
        '/api': { target, changeOrigin: true, rewrite: (path) => path.replace(/^\/api/, '') },
        // Recursos servidos por el backend sin prefijo /api: fotos (/media),
        // documentos subidos (/uploads) y endpoints de subida (/upload, /uploads).
        '/media': { target, changeOrigin: true },
        '/uploads': { target, changeOrigin: true },
        '/upload': { target, changeOrigin: true },
      }
    })()
  }
})
