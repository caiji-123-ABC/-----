import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 允许所有网络接口访问
    port: 5173,      // 指定端口，默认是5173
    strictPort: true, // 如果端口被占用，直接退出
    open: true,      // 自动打开浏览器
    cors: true,      // 允许跨域
    hmr: {
      host: '192.168.1.231',
      port: 5173
    }
  }
})
