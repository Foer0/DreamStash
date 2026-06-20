<template>
  <div class="auth-container">

    <header class="auth-header">
      <div class="logo-area">
        <img src="/logo.png" alt="DreamStash Logo" class="logo-img" />
      </div>

      <div class="desktop-menu-container">
        <div class="dots-trigger">...</div>
        <nav class="dropdown-menu-horizontal">
          <button class="nav-item" @click="router.push('/login')">SIGN IN</button>
          <span class="nav-divider-white">|</span>
          <button class="nav-item">SUPPORT</button>
        </nav>
      </div>

      <nav class="mobile-nav-menu">
        <button class="nav-item" @click="router.push('/login')">SIGN IN</button>
        <span class="nav-divider">/</span>
        <button class="nav-item">SUPPORT</button>
      </nav>
    </header>

    <button class="back-btn" @click="router.back()" aria-label="Go back">
      &lt;
    </button>

    <main class="auth-main">
      <h1 class="auth-title">Sign Up</h1>

      <div class="auth-form">
        <input
          v-model="email"
          type="email"
          placeholder="Email Address"
          class="auth-input"
          autocomplete="email"
          @keyup.enter="handleRegister"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="auth-input"
          autocomplete="new-password"
          @keyup.enter="handleRegister"
        />

        <transition name="fade">
          <p v-if="errorMsg" class="msg msg--error">{{ errorMsg }}</p>
        </transition>

        <button
          class="btn-primary"
          :disabled="isLoading"
          @click="handleRegister"
        >
          {{ isLoading ? 'Загрузка...' : 'Continue to Verify Email' }}
        </button>

        <button class="btn-ghost" @click="router.push('/')">Back to Options</button>

        <p class="auth-switch">
          Already have an account?
          <span class="text-link" @click="router.push('/login')">Login</span>
        </p>

        <p class="policy-text">
          By continuing to use our services, you acknowledge that you have both
          read and agree to our
          <span class="policy-link">Terms of Service</span> and
          <span class="policy-link">Privacy Policy</span>.
        </p>

        <div class="google-btn-wrapper">
          <GoogleLogin :callback="handleGoogleAuthCallback" prompt />
        </div>
      </div>
    </main>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'


const auth = useAuthStore()
const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const email     = ref('')
const password  = ref('')
const isLoading = ref(false)
const errorMsg  = ref('')

async function handleRegister() {
  errorMsg.value = ''

  if (!email.value.trim() || !password.value) {
    errorMsg.value = 'Пожалуйста, заполните все поля.'
    return
  }

  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/register`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        email: email.value.trim(),
        password: password.value
      }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail ?? 'Ошибка при регистрации')

    alert('Регистрация успешна!')
    router.push('/login')
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    isLoading.value = false
  }
}

async function handleGoogleAuthCallback(response) {
  errorMsg.value = ''
  try {
    const res = await fetch(`${API_BASE}/google-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: response.credential })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail ?? 'Ошибка авторизации Google')

    auth.setToken(data.access_token)
    router.push('/')
  } catch (err) {
    errorMsg.value = err.message
  }
}
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; }
.auth-container { width: 100%; min-height: 100vh; background: #ffffff; display: flex; flex-direction: column; align-items: center; font-family: sans-serif; overflow-x: hidden; position: relative; }
.auth-header { display: flex; flex-direction: column; align-items: center; gap: 6px; width: 100%; padding: 14px 15px 10px; z-index: 10; }
.logo-area { display: flex; justify-content: center; }
.logo-img  { height: 45px; object-fit: contain; }
.mobile-nav-menu { background: #2e3192; border-radius: 6px; padding: 6px 14px; display: flex; align-items: center; gap: 6px; }
.nav-item { background: none; border: none; color: #ffffff; font-size: 13px; font-weight: 500; cursor: pointer; }
.nav-divider { color: #ffffff; opacity: 0.6; font-size: 13px; }
.desktop-menu-container { display: none; }

.back-btn {
  position: absolute; left: 0; top: 0; bottom: 0; width: 50px; display: flex; align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0); border: none; font-size: 32px; color: #b0b0b0; cursor: pointer; transition: background 0.2s, color 0.2s; z-index: 5; padding: 0; user-select: none;
}
.back-btn:hover { background: rgba(0, 0, 0, 0.05); color: #444444; }

.auth-main {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px 24px 60px; width: 100%; max-width: 420px; z-index: 10;
}
.auth-title { font-size: 42px; font-weight: 700; color: #111111; margin: 0 0 30px; letter-spacing: -0.5px; }
.auth-form { display: flex; flex-direction: column; gap: 12px; width: 100%; }
.auth-input {
  width: 100%; padding: 12px 16px; font-size: 14px; color: #111; background: #f2f2f2; border: 1px solid #e0e0e0; border-radius: 8px; outline: none; transition: border-color 0.18s;
}
.auth-input:focus { border-color: #2e3192; background: #fff; }
.msg { font-size: 13px; margin: 0; padding: 8px 12px; border-radius: 4px; }
.msg--error { background: #fff0f0; color: #cc0000; border: 1px solid #f5c6c6; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }

.btn-primary {
  width: 100%; padding: 14px; background: #000000; color: #ffffff; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.18s; margin-top: 4px;
}
.btn-primary:hover:not(:disabled) { background: #222222; }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-ghost { background: none; border: none; color: #666; font-size: 13px; cursor: pointer; padding: 4px 0; text-align: center; transition: color 0.18s; }
.btn-ghost:hover { color: #111; }
.google-btn-wrapper { margin-top: 15px; width: 100%; display: flex; justify-content: center; }
.auth-switch { font-size: 13px; color: #555; margin: 8px 0 0; text-align: center; }
.text-link { color: #2e3192; cursor: pointer; font-weight: bold; text-decoration: underline; }
.policy-text { font-size: 11px; color: #999; text-align: center; line-height: 1.5; margin: 10px 0 0; }
.policy-link { text-decoration: underline; cursor: pointer; }

@media (min-width: 1024px) {
  .auth-header { padding: 20px 30px 10px; }
  .logo-img { height: 60px; }
  .mobile-nav-menu { display: none; }
  .desktop-menu-container { display: block; position: relative; height: 28px; }
  .dots-trigger { font-size: 28px; font-weight: bold; color: #111; cursor: pointer; line-height: 0.8; text-align: center; }
  .dropdown-menu-horizontal {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) scaleX(0); background: #2e3192; border-radius: 6px; padding: 6px 16px; display: flex; align-items: center; gap: 10px; white-space: nowrap; opacity: 0; pointer-events: none; transition: transform 0.25s ease, opacity 0.2s ease; transform-origin: center;
  }
  .desktop-menu-container:hover .dots-trigger             { opacity: 0; }
  .desktop-menu-container:hover .dropdown-menu-horizontal { opacity: 1; pointer-events: auto; transform: translate(-50%, -50%) scaleX(1); }
  .back-btn { width: 70px; font-size: 44px; }
}
</style>