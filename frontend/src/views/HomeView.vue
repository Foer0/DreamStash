<template>
  <transition name="fade" mode="out-in">
    <div v-if="showIntro" class="intro-overlay" @click="showIntro = false">
      <div class="intro-content">
        <img src="/intro-bg.png" alt="Welcome" class="intro-image" />
        <div class="intro-arrow">▼</div>
      </div>
    </div>

    <div v-else class="main-page-container">
      <header class="navbar-header">
        <div class="logo-area">
          <img src="/logo.png" alt="POtencial Logo" class="logo-img" />
        </div>

        <div class="desktop-menu-container">
          <nav class="desktop-nav-menu">
            <button v-if="isLoggedIn" class="nav-item" @click="router.push('/profile')">PROFILE</button>
            <span v-if="isLoggedIn" class="nav-divider-white">|</span>
            <button v-if="!isLoggedIn" class="nav-item" @click="router.push('/login')">SIGN IN</button>
            <button v-if="isLoggedIn" class="nav-item" @click="handleSignOut">SIGN OUT</button>
            <span class="nav-divider-white">|</span>
            <button class="nav-item" @click="router.push('/support')">SUPPORT</button>
          </nav>
        </div>

        <nav class="mobile-nav-menu">
          <button v-if="isLoggedIn" class="nav-item" @click="router.push('/profile')">PROFILE</button>
          <span v-if="isLoggedIn" class="nav-divider">|</span>
          <button v-if="!isLoggedIn" class="nav-item" @click="router.push('/login')">SIGN IN</button>
          <button v-if="isLoggedIn" class="nav-item" @click="handleSignOut">SIGN OUT</button>
          <span class="nav-divider">|</span>
          <button class="nav-item" @click="router.push('/support')">SUPPORT</button>
        </nav>
      </header>

      <main class="slider-main-section">
        <button
          v-if="currentIndex > 0"
          class="slider-arrow arrow-left"
          @click="prevPage"
        >
          &lt;
        </button>

        <div class="card-display-area">
          <div v-if="currentIndex < goals.length" class="goal-card">
            <div class="goal-image-wrapper">
              <img
                :src="getImageUrl(goals[currentIndex].img_path)"
                alt="Goal target"
                class="goal-img-render"
              />
            </div>
          </div>

          <div v-else class="center-card-trigger" @click="isModalOpen = true">
            <span class="main-plus-icon">+</span>
          </div>
        </div>

        <button
          v-if="currentIndex < goals.length"
          class="slider-arrow arrow-right"
          @click="nextPage"
        >
          &gt;
        </button>
      </main>

      <footer class="footer-progress-area">
        <div class="progress-title">
          {{ currentGoal ? `Goal: ${currentGoal.title}` : 'New Goal' }}
        </div>

        <div class="progress-bar-wrapper">
          <button class="control-btn minus" @click="openTxModal('withdraw')">-</button>

          <div class="progress-track">
            <div
              class="progress-fill status-delayed"
              :style="{ width: progressPercentage + '%' }"
            >
              <span v-if="currentGoal && progressPercentage > 10">
                {{ progressPercentage.toFixed(0) }}%
              </span>
            </div>
            <div class="progress-text-remain">
              {{ currentGoal
                ? `Left: ${amountRemaining} ${currentGoal.currency || ''}`
                : '0.00' }}
            </div>
          </div>

          <button class="control-btn plus" @click="openTxModal('deposit')">+</button>
        </div>

        <button v-if="currentIndex < goals.length" class="info-btn" @click="isInfoModalOpen = true">INFO</button>

        <div class="pagination-indicator">
          <span
            v-for="pageNumber in totalPages"
            :key="pageNumber"
            :class="['page-num', { active: currentIndex === pageNumber - 1 }]"
            @click="goToPage(pageNumber - 1)"
          >
            {{ pageNumber }}
          </span>
        </div>
      </footer>

      <GoalModal
        v-if="isModalOpen"
        @close="isModalOpen = false"
        @goal-created="handleGoalCreated"
      />

      <GoalDetailsModal
        v-if="isInfoModalOpen"
        :goal="currentGoal"
        @close="isInfoModalOpen = false"
        @goal-updated="handleGoalUpdated"
        @goal-deleted="handleGoalDeleted"
      />

      <TransactionModal
        v-if="isTxModalOpen"
        :goalId="currentGoal.id"
        :txType="currentTxType"
        @close="isTxModalOpen = false"
        @transaction-added="handleTransactionAdded"
      />

      <div class="bg-animation-layer" aria-hidden="true"></div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import GoalModal from '../components/GoalModal.vue'
import GoalDetailsModal from '../components/GoalDetailsModal.vue'
import TransactionModal from '../components/TransactionModal.vue'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// ── AUTH ───────────────────────────────────────────────────────────
const isLoggedIn = computed(() => !!auth.accessToken)

function handleSignOut() {
  auth.logout()
  goals.value = []
  currentIndex.value = 0
}

// ── GOALS & TRANSACTIONS ───────────────────────────────────────────
const isModalOpen = ref(false)
const isInfoModalOpen = ref(false)
const isTxModalOpen = ref(false)
const currentTxType = ref('deposit')
const showIntro = ref(true)

const currentIndex = ref(0)
const goals = ref([])

const totalPages   = computed(() => goals.value.length + 1)
const currentGoal  = computed(() =>
  currentIndex.value < goals.value.length ? goals.value[currentIndex.value] : null
)

const progressPercentage = computed(() => {
  if (!currentGoal.value) return 0
  const pct = (currentGoal.value.current_amount || 0) / (currentGoal.value.goal_amount || 1) * 100
  return Math.min(Math.max(pct, 0), 100)
})

const amountRemaining = computed(() => {
  if (!currentGoal.value) return '0.00'
  const rem = currentGoal.value.goal_amount - (currentGoal.value.current_amount || 0)
  return rem > 0 ? rem.toFixed(2) : '0.00'
})

const fetchGoals = async () => {
  try {
    const response = await axios.get(`${API_BASE}/goals/`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })
    goals.value = response.data
  } catch (error) {
    console.error('Не удалось загрузить цели:', error)
  }
}

const getImageUrl = (path) => {
  if (!path) return '/placeholder.png'
  if (path.startsWith('/static/')) {
    return `${API_BASE}${path}`
  }
  return path
}

onMounted(async () => {
  if (auth.accessToken) {
    await fetchGoals()
  }
})

// ── NAVIGATION ──────────────────────────────────────────────────────────────
const nextPage = () => { if (currentIndex.value < totalPages.value - 1) currentIndex.value++ }
const prevPage = () => { if (currentIndex.value > 0) currentIndex.value-- }
const goToPage = (i) => { currentIndex.value = i }

const openTxModal = (type) => {
  if (!currentGoal.value) return
  currentTxType.value = type
  isTxModalOpen.value = true
}

// ── CALLBACKS ───────────────────────────────────────────────────
const handleGoalCreated = (newGoal) => {
  goals.value.push({ ...newGoal, current_amount: newGoal.current_amount ?? 0 })
  currentIndex.value = goals.value.length - 1
}

const handleGoalUpdated = (updatedGoal) => {
  goals.value[currentIndex.value] = { ...updatedGoal }
}

const handleGoalDeleted = (deletedId) => {
  goals.value = goals.value.filter(g => g.id !== deletedId)
  if (currentIndex.value >= goals.value.length && currentIndex.value > 0) {
    currentIndex.value--
  }
}

const handleTransactionAdded = async (txData) => {
  const goal = goals.value[currentIndex.value]
  const amount = parseFloat(txData.amount)

  if (txData.type === 'deposit') {
    goal.current_amount = parseFloat(goal.current_amount || 0) + amount
  } else if (txData.type === 'withdraw') {
    goal.current_amount = Math.max(0, parseFloat(goal.current_amount || 0) - amount)
  }

  isTxModalOpen.value = false

  setTimeout(async () => {
    await fetchGoals()
    if (currentIndex.value >= goals.value.length) {
      currentIndex.value = Math.max(0, goals.value.length - 1)
    }
  }, 500)
}
</script>

<style scoped>
/* ==========================================================================
   RESET & MOBILE-FIRST STYLES
   ========================================================================== */

*, *::before, *::after { box-sizing: border-box; }

.main-page-container {
  width: 100%;
  min-height: 100vh;
  background: transparent; /* Обязательно прозрачный, чтобы было видно слой кругов */
  display: flex;
  flex-direction: column;
  font-family: sans-serif;
  overflow-x: hidden;
  position: relative;
}

/* ── HEADER ── */
.navbar-header {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 15px;
}

.logo-area { display: flex; justify-content: center; }
.logo-img  { height: 45px; object-fit: contain; }

.mobile-nav-menu {
  background: #2e3192; border-radius: 6px; padding: 6px 14px;
  display: flex; align-items: center; gap: 6px;
}
.nav-item {
  background: none; border: none; color: #ffffff;
  font-size: 13px; font-weight: 500; cursor: pointer;
}
.nav-divider { color: #ffffff; opacity: 0.6; font-size: 13px; }
.desktop-menu-container { display: none; }

/* ── SLIDER ── */
.slider-main-section {
  position: relative;
  z-index: 10;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 240px;
}

.slider-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: rgba(0, 0, 0, 0);
  border: none;
  border-radius: 0;
  font-size: 36px;
  color: #b5b5b5;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s, color 0.2s;
  z-index: 10;
}

.arrow-left  { left: 0; }
.arrow-right { right: 0; }

.slider-arrow:hover { background: rgba(0, 0, 0, 0.08); color: #555555; }

.card-display-area { display: flex; justify-content: center; align-items: center; padding: 0 54px; }

.goal-card { width: 200px; height: 200px; display: flex; justify-content: center; align-items: center; }
.goal-image-wrapper { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
.goal-img-render { max-width: 100%; max-height: 100%; object-fit: contain; }

.center-card-trigger {
  width: 200px; height: 200px; background: #e0e0e0; border-radius: 45px;
  display: flex; justify-content: center; align-items: center;
  cursor: pointer; transition: background 0.2s, transform 0.1s;
}
.center-card-trigger:hover { background: #d0d0d0; transform: scale(1.01); }
.main-plus-icon { font-size: 64px; color: #ffffff; font-weight: 300; }

/* ── FOOTER ── */
.footer-progress-area {
  position: relative;
  z-index: 10;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  width: 100%; padding: 0 15px 20px;
}

.progress-title { font-size: 15px; font-weight: bold; color: #333; }
.progress-bar-wrapper { display: flex; align-items: center; gap: 8px; width: 100%; max-width: 320px; }

.control-btn {
  width: 22px; height: 22px; border-radius: 5px; border: none;
  font-weight: bold; cursor: pointer; display: flex; justify-content: center; align-items: center;
}
.control-btn.minus { background: #e0e0e0; color: #ff3b30; }
.control-btn.plus  { background: #e0e0e0; color: #007bff; }

.progress-track {
  flex: 1; height: 22px; background: #e0e0e0; border-radius: 11px; overflow: hidden; display: flex; position: relative;
}
.progress-fill.status-delayed {
  height: 100%; background: #4cd964; display: flex; align-items: center;
  padding-left: 12px; font-size: 11px; font-weight: bold; color: #000;
  transition: width 0.5s ease-out;
}
.progress-text-remain {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  font-size: 11px; font-weight: bold; color: #333;
}

.info-btn {
  background: #262626; color: #ffffff; border: none; padding: 4px 16px; border-radius: 6px;
  font-size: 12px; font-weight: bold; letter-spacing: 1px; cursor: pointer; margin-top: 5px; transition: background 0.2s;
}
.info-btn:hover { background: #404040; }

.pagination-indicator { display: flex; gap: 12px; margin-top: 5px; user-select: none; }
.page-num { font-size: 16px; color: #8c8c8c; cursor: pointer; transition: color 0.2s; }
.page-num:hover  { color: #333; }
.page-num.active { color: #2e3192; font-weight: bold; }

/* ==========================================================================
   DESKTOP STYLES (≥ 1024px)
   ========================================================================== */
@media (min-width: 1024px) {
  .main-page-container { padding: 20px 0 0 0; }

  .navbar-header {
    flex-direction: column; justify-content: center; align-items: center; gap: 15px; height: auto; padding: 10px 0;
  }

  .logo-area { flex: none; justify-content: center; }
  .logo-img  { height: 70px; }
  .mobile-nav-menu { display: none; }

  .desktop-menu-container {
    display: flex; justify-content: center; align-items: center;
    width: auto;
  }
  .desktop-nav-menu {
    background: #2e3192; border-radius: 6px; padding: 6px 16px; display: flex; align-items: center; gap: 10px;
    white-space: nowrap;
  }
  .nav-divider-white { color: rgba(255,255,255,0.4); font-size: 14px; }

  .slider-main-section { min-height: 360px; margin: 0; }
  .slider-arrow { width: 65px; top: 0; transform: none; height: 100%; font-size: 56px; }
  .card-display-area { padding: 0 90px; }
  .goal-card, .center-card-trigger { width: 260px; height: 260px; border-radius: 55px; }
  .main-plus-icon { font-size: 80px; }

  .footer-progress-area { padding: 15px 30px 25px; /* Убрал background: #ffffff; чтобы фон не перекрывал круги */ z-index: 20; position: relative; }
  .progress-bar-wrapper { max-width: 450px; }
}

.intro-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
  background-size: cover; background-position: center; background-repeat: no-repeat;
  display: flex; justify-content: center; align-items: flex-end; z-index: 2000; cursor: pointer;
}
.intro-content { width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.intro-image { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; }
.intro-arrow {
  position: relative; font-size: 48px; color: white; text-shadow: 0 2px 6px rgba(0,0,0,0.6);
  margin-bottom: 30px; animation: bounce 2s infinite; z-index: 1;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── АНИМАЦИОННЫЙ ФОН ── */
.bg-animation-layer {
  position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}

.bg-animation-layer::before,
.bg-animation-layer::after {
  content: ''; position: absolute; border-radius: 50%; opacity: 0.5;
  background: #FFDB58; animation: floatBlob 20s infinite ease-in-out;
}
.bg-animation-layer::before { width: 500px; height: 500px; top: -10%; left: -15%; animation-delay: -5s; }
.bg-animation-layer::after  { width: 400px; height: 400px; bottom: 25%; right: -10%; animation-delay: -12s; }

@keyframes floatBlob {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(40px, -30px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(30px, 10px) scale(1.02); }
}
</style>

<style>
html, body, #app {
  margin: 0 !important; padding: 0 !important; width: 100% !important; max-width: 100% !important;
  min-height: 100vh; display: block !important; background-color: #f2f2f2;
}
</style>