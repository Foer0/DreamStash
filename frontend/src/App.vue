<template>
  <RouterView v-if="isInitialized" />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from './store/auth'

const auth = useAuthStore()
const isInitialized = ref(false)

onMounted(async () => {
  try {
    // Ждем гарантированного восстановления сессии
    await auth.tryRestoreSession()
  } catch (error) {
    console.error('Ошибка при восстановлении сессии:', error)
  } finally {
    // Разрешаем рендер приложения
    isInitialized.value = true
  }
})
</script>

<style>
/* Глобальные стили для всего приложения.
  Обнуляем дефолтные отступы браузера, чтобы верстка встала идеально.
*/
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #f2f2f2; /* Легкий серый фон на бэкграунде всего сайта */
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>