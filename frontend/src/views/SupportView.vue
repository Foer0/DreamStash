<template>
  <div class="main-page-container">
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
          <button class="nav-item active-nav" @click="router.push('/support')">SUPPORT</button>
        </nav>
      </div>

      <nav class="mobile-nav-menu">
        <button v-if="isLoggedIn" class="nav-item" @click="router.push('/profile')">PROFILE</button>
        <span v-if="isLoggedIn" class="nav-divider">|</span>
        <button v-if="!isLoggedIn" class="nav-item" @click="router.push('/login')">SIGN IN</button>
        <button v-if="isLoggedIn" class="nav-item" @click="handleSignOut">SIGN OUT</button>
        <span class="nav-divider">|</span>
        <button class="nav-item active-nav" @click="router.push('/support')">SUPPORT</button>
      </nav>
    </header>

    <main class="slider-main-section support-override">
      <button class="slider-arrow arrow-left" @click="router.push('/')">&lt;</button>

      <div class="support-content-area">

        <!-- ── FAQ ──────────────────────────────────────────────── -->
        <section class="support-block faq-block">
          <h2 class="support-block-title">FAQ</h2>

          <div class="faq-list">
            <div
              v-for="(item, i) in faqs"
              :key="i"
              class="faq-item"
              :class="{ 'faq-open': openFaq === i }"
            >
              <button class="faq-question" @click="toggleFaq(i)">
                <span>{{ item.q }}</span>
                <span class="faq-chevron">{{ openFaq === i ? '▲' : '▼' }}</span>
              </button>
              <transition name="faq-slide">
                <div v-if="openFaq === i" class="faq-answer">{{ item.a }}</div>
              </transition>
            </div>
          </div>
        </section>

        <!-- ── CONTACT ───────────────────────────────────────────── -->
        <section class="support-block contact-block">
          <h2 class="support-block-title">CONTACT</h2>

          <p class="contact-intro">
            Didn't find an answer? Our team is happy to help.
          </p>

          <a href="mailto:support@dream_stash.app" class="contact-email-link">
            <span class="contact-email-icon">✉</span>
            support@dream_stash.app
          </a>

          <p class="contact-response">
            We typically respond within <strong>1–2 business days</strong>.
          </p>

          <hr class="contact-divider" />

          <div class="contact-tip">
            <span class="tip-icon">💡</span>
            <span>Include your account email when writing to us — it helps us find your account faster.</span>
          </div>
        </section>

      </div>
    </main>

    <div class="bg-animation-layer" aria-hidden="true"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth   = useAuthStore()

const isLoggedIn = computed(() => !!auth.accessToken)
function handleSignOut() { auth.logout(); router.push('/login') }

// ── FAQ ──────────────────────────────────────────────────────────────
const openFaq = ref(null)

const toggleFaq = (i) => {
  openFaq.value = openFaq.value === i ? null : i
}

const faqs = [
  {
    q: 'How do I create a savings goal?',
    a: 'On the home page click the "+" card or the Add Goal button. Enter a title, target amount, optional deadline, and description, then save.',
  },
  {
    q: 'How do I record a deposit or withdrawal?',
    a: 'Open any goal card and use the Deposit or Withdraw buttons. Enter the amount, choose the currency, optionally add a note, and confirm.',
  },
  {
    q: 'How do I change my display currency?',
    a: 'Go to the Profile page, click EDIT, and pick your preferred currency from the dropdown. All history amounts are automatically converted.',
  },
  {
    q: 'Why is my balance different from what I entered?',
    a: 'Amounts are shown in your profile currency using fixed exchange rates. If you recently changed your currency the values will look different.',
  },
  {
    q: 'How do I view transaction details?',
    a: 'On the Profile page, under HISTORY, click any transaction row to open a detail view showing the date, goal, amount, type, and your note.',
  },
  {
    q: 'Can I delete a goal?',
    a: 'Open the goal and scroll to the bottom to find the Delete button. Deleting a goal permanently removes it along with all its transaction history.',
  },
]
</script>

<style scoped>
/* ==========================================================================
   БАЗОВЫЕ СТИЛИ
   ========================================================================== */
*, *::before, *::after { box-sizing: border-box; }

.main-page-container {
  width: 100%; min-height: 100vh; background: transparent;
  display: flex; flex-direction: column; font-family: sans-serif; overflow-x: hidden;
}

/* ==========================================================================
   НАВИГАЦИЯ
   ========================================================================== */
.navbar-header {
  position: relative; z-index: 10;
  display: flex; flex-direction: column; align-items: center;
  gap: 10px; width: 100%; padding: 12px 15px;
}
.logo-area { display: flex; justify-content: center; }
.logo-img  { height: 45px; object-fit: contain; }

.mobile-nav-menu {
  background: #2e3192; border-radius: 6px; padding: 6px 14px;
  display: flex; align-items: center; gap: 6px;
}
.nav-item {
  background: none; border: none; color: #ffffff;
  font-size: 13px; font-weight: 500; cursor: pointer; transition: opacity 0.2s;
}
.nav-item:hover { opacity: 0.8; }
.active-nav { text-decoration: underline; text-underline-offset: 3px; }
.nav-divider { color: #ffffff; opacity: 0.6; font-size: 13px; }
.desktop-menu-container { display: none; }

/* ==========================================================================
   СЛАЙДЕР / СТРЕЛКИ
   ========================================================================== */
.slider-main-section {
  position: relative; z-index: 10;
  flex: 1; display: flex; justify-content: center;
  align-items: flex-start;
  width: 100%; min-height: 240px;
}

.support-override { padding: 40px 0 60px; }

.slider-arrow {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 44px; height: 200px; display: flex; align-items: center; justify-content: center;
  padding: 0; background: transparent; border: none; font-size: 36px;
  color: #b5b5b5; cursor: pointer; user-select: none;
  transition: background 0.2s, color 0.2s; z-index: 10;
}
.arrow-left { left: 0; }
.slider-arrow:hover { background: rgba(0,0,0,0.08); color: #555; }

/* ==========================================================================
   SUPPORT — LAYOUT
   ========================================================================== */
.support-content-area {
  display: flex; flex-direction: column; align-items: center;
  width: 100%;
  padding: 0 16px 0 56px;
  gap: 40px;
}

.support-block {
  width: 100%; max-width: 520px;
  display: flex; flex-direction: column;
  align-items: stretch;
  border: 2px solid #2e3192; border-radius: 12px; padding: 30px;
  background-color: #ffffff; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.support-block-title {
  font-size: 22px; font-weight: bold; color: #333;
  margin: 0 0 24px 0; letter-spacing: 0.5px;
  text-align: center;
}

/* ==========================================================================
   FAQ ACCORDION
   ========================================================================== */
.faq-list { display: flex; flex-direction: column; gap: 6px; }

.faq-item {
  border: 1px solid #e8e8e8; border-radius: 8px;
  overflow: hidden; transition: border-color 0.2s;
}
.faq-item.faq-open { border-color: #2e3192; }

.faq-question {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  gap: 12px; padding: 14px 16px;
  background: none; border: none; text-align: left;
  font-size: 14px; font-weight: 600; color: #333; cursor: pointer; transition: background 0.15s;
}
.faq-question:hover { background: #f5f5ff; }
.faq-item.faq-open .faq-question { background: #f0f0fd; color: #2e3192; }

.faq-chevron { font-size: 11px; flex-shrink: 0; color: #999; }
.faq-item.faq-open .faq-chevron { color: #2e3192; }

.faq-answer {
  padding: 0 16px 14px;
  font-size: 14px; color: #555; line-height: 1.6; background: #f0f0fd;
}

.faq-slide-enter-active, .faq-slide-leave-active { transition: all 0.22s ease; overflow: hidden; }
.faq-slide-enter-from, .faq-slide-leave-to       { max-height: 0; opacity: 0; padding-top: 0; padding-bottom: 0; }
.faq-slide-enter-to,   .faq-slide-leave-from     { max-height: 200px; opacity: 1; }

/* ==========================================================================
   CONTACT
   ========================================================================== */
.contact-intro {
  font-size: 15px; color: #555; text-align: center; margin: 0 0 20px;
}

.contact-email-link {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  padding: 14px 16px; border-radius: 8px;
  background: #f0f0fd; border: 2px solid #2e3192;
  font-size: 15px; font-weight: 700; color: #2e3192;
  text-decoration: none; transition: background 0.2s; margin-bottom: 16px;
  word-break: break-all;
}
.contact-email-link:hover { background: #e4e4fa; }
.contact-email-icon { font-size: 18px; flex-shrink: 0; }

.contact-response {
  font-size: 13px; color: #888; text-align: center; margin: 0 0 20px;
}

.contact-divider {
  border: none; border-top: 1px solid #eee; margin: 0 0 18px;
}

.contact-tip {
  display: flex; align-items: flex-start; gap: 10px;
  font-size: 13px; color: #777; line-height: 1.5;
}
.tip-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }

/* ==========================================================================
   DESKTOP (≥ 1024px)
   ========================================================================== */
@media (min-width: 1024px) {
  .navbar-header {
    flex-direction: column; justify-content: center; align-items: center;
    gap: 15px; height: auto; padding: 10px 0;
  }
  .logo-area { flex: none; justify-content: center; }
  .logo-img  { height: 70px; }
  .mobile-nav-menu { display: none; }

  .desktop-menu-container { display: flex; justify-content: center; align-items: center; }
  .desktop-nav-menu {
    background: #2e3192; border-radius: 6px; padding: 6px 16px;
    display: flex; align-items: center; gap: 10px; white-space: nowrap;
  }
  .nav-divider-white { color: rgba(255,255,255,0.4); font-size: 14px; }

  .slider-main-section { min-height: 360px; }
  .slider-arrow { width: 65px; height: 100%; font-size: 56px; top: 50%; }

  .support-content-area {
    flex-direction: row; justify-content: center;
    align-items: flex-start;
    padding: 0 90px; gap: 40px;
  }

  .faq-block    { max-width: 560px; flex: 2; }
  .contact-block { max-width: 300px; flex: 1; }
}

/* ==========================================================================
   АНИМАЦИЯ ФОНА
   ========================================================================== */
.bg-animation-layer {
  position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}
.bg-animation-layer::before,
.bg-animation-layer::after {
  content: ''; position: absolute; border-radius: 50%;
  opacity: 0.5; background: #FFDB58; animation: floatBlob 20s infinite ease-in-out;
}
.bg-animation-layer::before {
  width: 500px; height: 500px; top: -10%; left: -15%; animation-delay: -5s;
}
.bg-animation-layer::after {
  width: 400px; height: 400px; bottom: 25%; right: -10%; animation-delay: -12s;
}
@keyframes floatBlob {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25%       { transform: translate(40px, -30px) scale(1.05); }
  50%       { transform: translate(-20px, 20px) scale(0.95); }
  75%       { transform: translate(30px, 10px) scale(1.02); }
}
</style>