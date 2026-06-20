import { ref } from 'vue'
import { defineStore } from 'pinia'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function isTokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)

  function setToken(token) {
    accessToken.value = token
    localStorage.setItem('access_token', token)
  }

  function logout() {
    accessToken.value = null
    localStorage.removeItem('access_token')
  }

  async function tryRestoreSession() {
    const token = accessToken.value
    if (!token || isTokenExpired(token)) {
      try {
        const res = await fetch(`${API_BASE}/refresh`, {
          method: 'POST',
          credentials: 'include',
        })
        if (res.ok) {
          const data = await res.json()
          setToken(data.access_token)
        } else {
          logout()
        }
      } catch {
        logout()
      }
    }
  }

  return { accessToken, setToken, logout, tryRestoreSession }
})