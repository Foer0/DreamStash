import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // Добавляем этот блок для Docker
  server: {
    host: true, // Позволяет принимать подключения извне контейнера
    port: 5173,      // Явно указываем стандартный порт
    watch: {
      usePolling: true // Обязательно для Windows/macOS, чтобы Vite видел изменения файлов внутри Docker
    }
  }
})