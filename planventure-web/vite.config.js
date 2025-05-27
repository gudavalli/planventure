import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.js'],
    define: {
      global: 'globalThis',
    },
  },
  define: {
    global: 'globalThis',
  },
  server: {
    proxy: {
      '/api/auth': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        credentials: 'include',
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      },
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
        credentials: 'include',
      },
    },
  },
})
