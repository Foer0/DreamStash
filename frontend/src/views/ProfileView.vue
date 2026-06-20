<template>
  <div class="main-page-container">
    <header class="navbar-header">
      <div class="logo-area">
        <img src="/logo.png" alt="POtencial Logo" class="logo-img" />
      </div>

      <div class="desktop-menu-container">
        <nav class="desktop-nav-menu">
          <button v-if="isLoggedIn" class="nav-item active-nav" @click="router.push('/profile')">PROFILE</button>
          <span v-if="isLoggedIn" class="nav-divider-white">|</span>
          <button v-if="!isLoggedIn" class="nav-item" @click="router.push('/login')">SIGN IN</button>
          <button v-if="isLoggedIn" class="nav-item" @click="handleSignOut">SIGN OUT</button>
          <span class="nav-divider-white">|</span>
          <button class="nav-item" @click="router.push('/support')">SUPPORT</button>
        </nav>
      </div>

      <nav class="mobile-nav-menu">
        <button v-if="isLoggedIn" class="nav-item active-nav" @click="router.push('/profile')">PROFILE</button>
        <span v-if="isLoggedIn" class="nav-divider">|</span>
        <button v-if="!isLoggedIn" class="nav-item" @click="router.push('/login')">SIGN IN</button>
        <button v-if="isLoggedIn" class="nav-item" @click="handleSignOut">SIGN OUT</button>
        <span class="nav-divider">|</span>
        <button class="nav-item" @click="router.push('/support')">SUPPORT</button>
      </nav>
    </header>

    <main class="slider-main-section profile-override">
      <button class="slider-arrow arrow-left" @click="router.push('/')">&lt;</button>

      <div class="profile-content-area">
        <section class="profile-block user-data-block">
          <h2 class="profile-block-title">USER DATA</h2>

          <div class="profile-form">
            <div class="profile-form-group">
              <label>Email:</label>
              <input
                type="email"
                v-model="editForm.email"
                :disabled="!isEditing"
                :class="{ 'input-disabled': !isEditing }"
              />
            </div>

            <div class="profile-form-group">
              <label>Currency:</label>
              <select
                v-model="editForm.currency"
                class="profile-currency-select"
                :disabled="!isEditing"
                :class="{ 'input-disabled': !isEditing }"
              >
                <option value="BYN">BYN</option>
                <option value="RUB">RUB</option>
                <option value="USD">USD</option>
              </select>
            </div>

            <template v-if="isEditing">
              <div class="profile-form-group">
                <label>Current Pass:</label>
                <input type="password" v-model="editForm.passwd" placeholder="Required for changes" />
              </div>
              <div class="profile-form-group">
                <label>New Pass:</label>
                <input type="password" v-model="editForm.new_passwd" placeholder="Leave empty to keep" />
              </div>
              <div class="profile-form-group">
                <label>Confirm Pass:</label>
                <input type="password" v-model="editForm.confirm_passwd" />
              </div>
            </template>

            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

            <div class="profile-btn-container">
              <button v-if="!isEditing" @click="startEdit" class="action-btn edit-btn">EDIT</button>
              <div v-else class="edit-actions">
                <button @click="cancelEdit" class="action-btn cancel-btn">CANCEL</button>
                <button @click="saveProfile" class="action-btn save-btn">SAVE</button>
              </div>
            </div>
          </div>
        </section>
        <section class="profile-block history-block">
          <h2 class="profile-block-title">HISTORY</h2>

          <div class="profile-table-container">
            <div class="profile-table-header">

              <div
                class="p-col p-col-date"
                :class="{
                  'col-sort-active': sortConfig.column === 'date',
                  'col-filter-active': hasFilter('date'),
                }"
                @click="openModal('date')"
              >Date {{ getSortIcon('date') }}</div>

              <div
                class="p-col p-col-goal"
                :class="{
                  'col-sort-active': sortConfig.column === 'goal',
                  'col-filter-active': hasFilter('goal'),
                }"
                @click="openModal('goal')"
              >Goal {{ getSortIcon('goal') }}</div>

              <div
                class="p-col p-col-total"
                :class="{
                  'col-sort-active': sortConfig.column === 'total',
                  'col-filter-active': hasFilter('total'),
                }"
                @click="openModal('total')"
              >Total {{ getSortIcon('total') }}</div>

              <div class="p-col p-col-type">
                <select
                  v-model="filters.type"
                  @change="onTypeChange"
                  class="type-filter-select"
                  :class="{ 'col-filter-active': !!filters.type }"
                >
                  <option value="">Type ▾</option>
                  <option value="deposit">↓ Deposit</option>
                  <option value="withdraw">↑ Withdraw</option>
                </select>
              </div>
            </div>

            <hr class="profile-table-divider" />

            <div class="profile-table-body">
              <div v-if="isLoading" class="history-empty">Loading…</div>
              <div v-else-if="historyPage.items.length === 0" class="history-empty">
                History is empty.
              </div>

              <div
                v-for="tx in historyPage.items"
                :key="tx.id"
                class="profile-table-row tx-clickable-row"
                @click="openTxModal(tx)"
                :title="tx.note ? '📝 ' + tx.note : 'Click for details'"
              >
                <div class="p-col p-col-date">{{ formatDate(tx.created_at) }}</div>
                <div class="p-col p-col-goal" :title="tx.goal_title">{{ tx.goal_title }}</div>
                <div class="p-col p-col-total">{{ tx.amount }}</div>
                <div class="p-col p-col-type" :class="tx.operation_type">
                  {{ formatType(tx.operation_type) }}
                </div>
              </div>
            </div>
          </div>

          <div class="profile-pagination">
            <button class="p-page-arrow" @click="prevPage" :disabled="currentPage <= 1">&lt;</button>
            <span class="p-page-number">{{ currentPage }} / {{ historyPage.total_pages || 1 }}</span>
            <button class="p-page-arrow" @click="nextPage" :disabled="currentPage >= (historyPage.total_pages || 1)">&gt;</button>
          </div>

          <div v-if="historyPage.total > 0" class="pagination-info">
            {{ paginationInfo }}
          </div>
        </section>
      </div>
    </main>
    <Teleport to="body">
      <div v-if="activeModal === 'date'" class="sort-modal-overlay" @click.self="closeModal">
        <div class="sort-modal-content">
          <h3 class="sort-modal-title">Filter — Date</h3>
          <div class="modal-filter-group">
            <div class="modal-filter-row">
              <label class="modal-label">From</label>
              <input type="date" v-model="modalTemp.date_from" class="modal-input" />
            </div>
            <div class="modal-filter-row">
              <label class="modal-label">To</label>
              <input type="date" v-model="modalTemp.date_to" class="modal-input" />
            </div>
          </div>
          <div class="modal-btn-row">
            <button class="sort-btn clear-btn" @click="clearFilter('date')">Clear</button>
            <button class="sort-btn apply-btn" @click="applyFilter('date')">Apply</button>
          </div>
          <button class="sort-close-btn" @click="closeModal">CLOSE</button>
        </div>
      </div>
    </Teleport>
    <Teleport to="body">
      <div v-if="activeModal === 'goal'" class="sort-modal-overlay" @click.self="closeModal">
        <div class="sort-modal-content">
          <h3 class="sort-modal-title">Filter — Goal</h3>
          <div class="modal-filter-group">
            <div class="modal-filter-row">
              <label class="modal-label">Name</label>
              <input
                type="text"
                v-model="modalTemp.goal"
                class="modal-input"
                placeholder="Search by goal name…"
                @keyup.enter="applyFilter('goal')"
              />
            </div>
          </div>
          <div class="modal-btn-row">
            <button class="sort-btn clear-btn" @click="clearFilter('goal')">Clear</button>
            <button class="sort-btn apply-btn" @click="applyFilter('goal')">Apply</button>
          </div>
          <button class="sort-close-btn" @click="closeModal">CLOSE</button>
        </div>
      </div>
    </Teleport>
    <Teleport to="body">
      <div v-if="activeModal === 'total'" class="sort-modal-overlay" @click.self="closeModal">
        <div class="sort-modal-content">
          <h3 class="sort-modal-title">Filter — Total</h3>
          <div class="modal-filter-group">
            <div class="modal-filter-row">
              <label class="modal-label">Min</label>
              <input
                type="number"
                v-model="modalTemp.amount_from"
                class="modal-input"
                placeholder="0.00"
                min="0"
                step="0.01"
              />
            </div>
            <div class="modal-filter-row">
              <label class="modal-label">Max</label>
              <input
                type="number"
                v-model="modalTemp.amount_to"
                class="modal-input"
                placeholder="No limit"
                min="0"
                step="0.01"
              />
            </div>
          </div>
          <div class="modal-btn-row">
            <button class="sort-btn clear-btn" @click="clearFilter('total')">Clear</button>
            <button class="sort-btn apply-btn" @click="applyFilter('total')">Apply</button>
          </div>
          <button class="sort-close-btn" @click="closeModal">CLOSE</button>
        </div>
      </div>
    </Teleport>
    <Teleport to="body">
      <div v-if="activeModal === 'tx' && selectedTx" class="sort-modal-overlay" @click.self="closeModal">
        <div class="sort-modal-content tx-detail-modal">
          <h3 class="sort-modal-title">Transaction Details</h3>

          <div class="tx-detail-list">
            <div class="tx-detail-row">
              <span class="tx-detail-label">Date</span>
              <span class="tx-detail-value">{{ formatDate(selectedTx.created_at) }}</span>
            </div>
            <div class="tx-detail-row">
              <span class="tx-detail-label">Goal</span>
              <span class="tx-detail-value">{{ selectedTx.goal_title }}</span>
            </div>
            <div class="tx-detail-row">
              <span class="tx-detail-label">Amount</span>
              <span class="tx-detail-value">
                {{ selectedTx.amount }} {{ selectedTx.currency }}
              </span>
            </div>
            <div class="tx-detail-row">
              <span class="tx-detail-label">Type</span>
              <span class="tx-detail-value tx-type-value" :class="selectedTx.operation_type">
                {{ formatType(selectedTx.operation_type) }}
              </span>
            </div>
            <div class="tx-detail-row tx-note-row">
              <span class="tx-detail-label">Note</span>
              <span class="tx-detail-value tx-note-value">
                {{ selectedTx.note || '—' }}
              </span>
            </div>
          </div>

          <button class="sort-close-btn" @click="closeModal">CLOSE</button>
        </div>
      </div>
    </Teleport>

    <div class="bg-animation-layer" aria-hidden="true"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth   = useAuthStore()

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const isLoggedIn = computed(() => !!auth.accessToken)
function handleSignOut() { auth.logout(); router.push('/login') }

const userData     = ref({ email: '', currency: 'BYN' })
const editForm     = ref({ email: '', currency: 'BYN', passwd: '', new_passwd: '', confirm_passwd: '' })
const isEditing    = ref(false)
const errorMessage = ref('')

const fetchProfile = async () => {
  try {
    const { data } = await axios.get(`${API_BASE}/profile`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` },
    })
    userData.value = { email: data.email, currency: data.currency }
    resetForm()
  } catch (e) { console.error('Profile load error:', e) }
}

const resetForm = () => {
  editForm.value = {
    email: userData.value.email, currency: userData.value.currency,
    passwd: '', new_passwd: '', confirm_passwd: '',
  }
  errorMessage.value = ''
}

const startEdit  = () => { resetForm(); isEditing.value = true }
const cancelEdit = () => { isEditing.value = false; resetForm() }

const saveProfile = async () => {
  errorMessage.value = ''
  const payload = {}

  if (editForm.value.currency !== userData.value.currency)
    payload.currency = editForm.value.currency

  if (editForm.value.email !== userData.value.email) {
    payload.email = editForm.value.email
    if (!editForm.value.passwd) {
      errorMessage.value = 'To change email, you must enter your current password.'
      return
    }
  }

  if (editForm.value.new_passwd) {
    if (editForm.value.new_passwd !== editForm.value.confirm_passwd) {
      errorMessage.value = "The passwords don't match."
      return
    }
    payload.new_passwd     = editForm.value.new_passwd
    payload.confirm_passwd = editForm.value.confirm_passwd
  }

  if (payload.email || payload.new_passwd) payload.passwd = editForm.value.passwd
  if (!Object.keys(payload).length) { isEditing.value = false; return }

  try {
    const { data } = await axios.patch(`${API_BASE}/profile`, payload, {
      headers: { Authorization: `Bearer ${auth.accessToken}` },
    })
    userData.value = { email: data.email, currency: data.currency }
    isEditing.value = false
    if (payload.currency) await fetchHistory()
  } catch (e) {
    errorMessage.value = e.response?.data?.detail || 'An error occurred while updating.'
  }
}

const PAGE_SIZE   = 10
const isLoading   = ref(false)
const currentPage = ref(1)

const historyPage = ref({
  items: [], total: 0, page: 1, page_size: PAGE_SIZE, total_pages: 1,
})

const filters = ref({
  goal: '', date_from: '', date_to: '', type: '',
  amount_from: '', amount_to: '',
})

const sortConfig = ref({ column: 'date', direction: 'desc' })

const fetchHistory = async () => {
  isLoading.value = true
  try {
    const params = {
      page:      currentPage.value,
      page_size: PAGE_SIZE,
      sort_by:   sortConfig.value.column,
      sort_dir:  sortConfig.value.direction,
    }
    if (filters.value.goal)               params.goal           = filters.value.goal
    if (filters.value.date_from)          params.date_from      = filters.value.date_from
    if (filters.value.date_to)            params.date_to        = filters.value.date_to
    if (filters.value.type)               params.operation_type = filters.value.type
    if (filters.value.amount_from !== '') params.amount_from    = filters.value.amount_from
    if (filters.value.amount_to   !== '') params.amount_to      = filters.value.amount_to

    const { data } = await axios.get(`${API_BASE}/profile/history`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` },
      params,
    })
    historyPage.value = data
  } catch (e) {
    console.error('History load error:', e)
  } finally {
    isLoading.value = false
  }
}

const activeModal = ref('')
const selectedTx  = ref(null)

const modalTemp = ref({
  goal: '', date_from: '', date_to: '',
  amount_from: '', amount_to: '',
  sort_column: 'date', sort_direction: 'desc',
})

const openModal = (col) => {
  activeModal.value = col
  modalTemp.value = {
    goal:           filters.value.goal,
    date_from:      filters.value.date_from,
    date_to:        filters.value.date_to,
    amount_from:    filters.value.amount_from,
    amount_to:      filters.value.amount_to,
    sort_column:    sortConfig.value.column,
    sort_direction: sortConfig.value.direction,
  }
}

const openTxModal = (tx) => {
  selectedTx.value  = tx
  activeModal.value = 'tx'
}

const closeModal = () => {
  activeModal.value = ''
  selectedTx.value  = null
}

const applyFilter = (col) => {
  sortConfig.value = {
    column:    modalTemp.value.sort_column    || 'date',
    direction: modalTemp.value.sort_direction || 'desc',
  }
  currentPage.value = 1
  if (col === 'date') {
    filters.value.date_from = modalTemp.value.date_from
    filters.value.date_to   = modalTemp.value.date_to
  } else if (col === 'goal') {
    filters.value.goal = modalTemp.value.goal
  } else if (col === 'total') {
    filters.value.amount_from = modalTemp.value.amount_from
    filters.value.amount_to   = modalTemp.value.amount_to
  }
  closeModal()
  fetchHistory()
}

const clearFilter = (col) => {
  currentPage.value = 1
  if (col === 'date') { filters.value.date_from = ''; filters.value.date_to = '' }
  else if (col === 'goal')  { filters.value.goal = '' }
  else if (col === 'total') { filters.value.amount_from = ''; filters.value.amount_to = '' }
  closeModal()
  fetchHistory()
}

const onTypeChange = () => { currentPage.value = 1; fetchHistory() }

const prevPage = () => {
  if (currentPage.value > 1) { currentPage.value--; fetchHistory() }
}
const nextPage = () => {
  if (currentPage.value < historyPage.value.total_pages) { currentPage.value++; fetchHistory() }
}

const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE + 1
  const end   = Math.min(currentPage.value * PAGE_SIZE, historyPage.value.total)
  return `Showing ${start}–${end} of ${historyPage.value.total}`
})

const getSortIcon = (col) => {
  if (sortConfig.value.column !== col) return '▾'
  return sortConfig.value.direction === 'asc' ? '↑' : '↓'
}

const hasFilter = (col) => {
  if (col === 'date')  return !!(filters.value.date_from || filters.value.date_to)
  if (col === 'goal')  return !!filters.value.goal
  if (col === 'total') return filters.value.amount_from !== '' || filters.value.amount_to !== ''
  return false
}

/**
 * FIX: Поддержка как "YYYY-MM-DD", так и "YYYY-MM-DDTHH:mm:ss.sssZ" форматов.
 * Оригинальный split('-') ломался на datetime-строках API.
 */
const formatDate = (s) => {
  if (!s) return ''
  const dateOnly = s.split('T')[0]
  const parts = dateOnly.split('-')
  if (parts.length < 3) return dateOnly
  const [y, m, d] = parts
  return `${d}.${m}.${y}`
}

const formatType = (t) => t ? t.charAt(0).toUpperCase() + t.slice(1) : ''

onMounted(() => {
  if (auth.accessToken) { fetchProfile(); fetchHistory() }
})
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
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: opacity 0.2s;
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
.profile-override { padding: 40px 0 60px; }

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
   ПРОФИЛЬ — LAYOUT
   ========================================================================== */
.profile-content-area {
  display: flex; flex-direction: column; align-items: center;
  width: 100%;
  padding: 0 16px 0 56px;
  gap: 40px;
}

.profile-block {
  width: 100%; max-width: 520px;
  display: flex; flex-direction: column;
  align-items: stretch;
  border: 2px solid #2e3192; border-radius: 12px; padding: 30px;
  background-color: #ffffff; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.profile-block-title {
  font-size: 22px; font-weight: bold; color: #333;
  margin-bottom: 25px; letter-spacing: 0.5px;
  text-align: center;
}

/* ==========================================================================
   ФОРМА USER DATA
   ========================================================================== */
.profile-form { display: flex; flex-direction: column; gap: 18px; width: 100%; }
.profile-form-group {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
}
.profile-form-group label {
  font-size: 15px; width: 110px; color: #333; font-weight: 500; flex-shrink: 0;
}
.profile-form-group input,
.profile-currency-select {
  flex: 1;
  min-width: 0;
  background: #f0f0f0; border: 1px solid #ccc;
  border-radius: 5px; padding: 10px 12px; font-size: 15px; outline: none;
  transition: background 0.2s, border-color 0.2s;
}
.profile-form-group input:focus { border-color: #2e3192; background: #f8f8ff; }
.input-disabled {
  background: transparent !important; border: 1px solid transparent !important;
  color: #555; font-weight: bold; appearance: none; -moz-appearance: none;
  -webkit-appearance: none; padding-left: 0;
}
.error-message { color: #ff3b30; font-size: 13px; text-align: right; margin-top: -5px; }

.profile-btn-container { display: flex; justify-content: flex-end; margin-top: 10px; }
.edit-actions { display: flex; gap: 10px; }
.action-btn {
  border: none; padding: 9px 24px; border-radius: 6px;
  font-size: 13px; font-weight: bold; letter-spacing: 1px; cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
}
.edit-btn   { background: #262626; color: #ffffff; }
.edit-btn:hover { background: #404040; }
.save-btn   { background: #4cd964; color: #000; }
.save-btn:hover { opacity: 0.8; }
.cancel-btn { background: #e0e0e0; color: #333; }
.cancel-btn:hover { background: #ccc; }

/* ==========================================================================
   ТАБЛИЦА HISTORY
   ========================================================================== */
.profile-table-container {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.profile-table-header, .profile-table-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; width: 100%;
  min-width: 310px;
}
.profile-table-header { font-weight: bold; color: #333; user-select: none; }
.profile-table-header .p-col:not(.p-col-type) { cursor: pointer; }
.profile-table-header .p-col:not(.p-col-type):hover { color: #2e3192; }

.col-sort-active   { color: #2e3192 !important; }
.col-filter-active { color: #e07000 !important; }

.p-col {
  flex: 1; font-size: 14px; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}
.p-col-date  { text-align: left;   flex: 1.2; min-width: 80px; }
.p-col-goal  { text-align: center; flex: 1.8; min-width: 88px; padding: 0 4px; }
.p-col-total { text-align: center; flex: 1.2; min-width: 70px; }
.p-col-type  { text-align: right;  flex: 1;   min-width: 72px; }

.profile-table-divider { border: none; border-top: 2px solid #000; margin: 4px 0 12px 0; }

.deposit  { color: #4cd964 !important; font-weight: bold; }
.withdraw { color: #ff3b30 !important; font-weight: bold; }

.history-empty { text-align: center; margin-top: 20px; color: #888; font-size: 16px; }

.tx-clickable-row {
  cursor: pointer; border-radius: 6px;
  margin: 0 -4px; padding: 10px 4px;
  transition: background 0.15s;
}
.tx-clickable-row:hover { background: rgba(46, 49, 146, 0.06); }

.type-filter-select {
  background: none; border: none; font-size: 14px; font-weight: bold;
  color: #333; cursor: pointer; padding: 0; width: 100%;
  text-align: right; outline: none; appearance: none; -webkit-appearance: none;
  transition: color 0.2s;
}
.type-filter-select:hover { color: #2e3192; }
.type-filter-select.col-filter-active { color: #e07000; }

.profile-pagination {
  display: flex; align-items: center; justify-content: center; gap: 20px; margin-top: 20px;
}
.p-page-arrow {
  background: none; border: none; font-size: 22px; cursor: pointer;
  color: #8c8c8c; transition: color 0.2s;
}
.p-page-arrow:hover:not(:disabled) { color: #333; }
.p-page-arrow:disabled { opacity: 0.3; cursor: not-allowed; }
.p-page-number { font-size: 16px; color: #2e3192; font-weight: bold; }
.pagination-info { text-align: center; margin-top: 6px; font-size: 13px; color: #888; }

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

  .profile-content-area {
    flex-direction: row;
    justify-content: center;
    align-items: flex-start;
    padding: 0 90px; gap: 40px;
    flex-wrap: wrap;
  }

  .user-data-block {
    max-width: 400px;
    flex: 0 1 380px;
  }

  .history-block {
    max-width: 680px;
    flex: 1 1 420px;
  }
}

/* ==========================================================================
   МОДАЛЬНЫЕ ОКНА (фильтры)
   ========================================================================== */
.sort-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.sort-modal-content {
  background: #ffffff; padding: 30px; border-radius: 12px;
  width: 90%; max-width: 350px;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.sort-modal-title { margin: 0 0 20px 0; font-size: 18px; color: #333; font-weight: bold; }

.modal-filter-group { width: 100%; display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.modal-filter-row { display: flex; align-items: center; gap: 10px; }
.modal-label { font-size: 14px; color: #555; width: 40px; font-weight: 500; flex-shrink: 0; }
.modal-input {
  flex: 1; min-width: 0; background: #f0f0f0; border: 1px solid #ccc; border-radius: 6px;
  padding: 9px 12px; font-size: 14px; outline: none; transition: border-color 0.2s;
}
.modal-input:focus { border-color: #2e3192; background: #f8f8ff; }

.modal-btn-row { display: flex; gap: 10px; width: 100%; margin-bottom: 12px; }
.sort-btn {
  padding: 11px; border-radius: 8px; font-size: 14px; font-weight: bold;
  cursor: pointer; transition: all 0.2s; text-align: center; border: none;
}
.clear-btn { flex: 1; background: #f0f0f0; color: #555; border: 1px solid #ccc !important; }
.clear-btn:hover { background: #e0e0e0; }
.apply-btn { flex: 1; background: #2e3192; color: #ffffff; }
.apply-btn:hover { background: #232882; }
.sort-close-btn {
  background: #262626; color: #ffffff; border: none;
  padding: 10px 30px; border-radius: 6px; font-weight: bold;
  letter-spacing: 1px; cursor: pointer; transition: background 0.2s; width: 100%;
}
.sort-close-btn:hover { background: #404040; }

/* ==========================================================================
   МОДАЛКА — ДЕТАЛИ ТРАНЗАКЦИИ
   ========================================================================== */
.tx-detail-modal { max-width: 400px; padding: 28px; }

.tx-detail-list {
  width: 100%; border: 1px solid #e8e8e8;
  border-radius: 10px; overflow: hidden; margin-bottom: 24px;
}

.tx-detail-row {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 13px 16px; border-bottom: 1px solid #f0f0f0; gap: 16px;
}
.tx-detail-row:last-child { border-bottom: none; }
.tx-detail-row:nth-child(odd) { background: #fafafa; }

.tx-detail-label {
  font-size: 12px; font-weight: 700; color: #999;
  text-transform: uppercase; letter-spacing: 0.6px;
  min-width: 56px; flex-shrink: 0; padding-top: 2px;
}
.tx-detail-value {
  font-size: 15px; color: #222; font-weight: 500;
  text-align: right; flex: 1;
}
.tx-type-value { font-weight: 700; }
.tx-note-row { background: #fffdf4 !important; }
.tx-note-value {
  font-style: italic; color: #666; font-weight: 400;
  line-height: 1.5; white-space: pre-wrap; word-break: break-word;
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