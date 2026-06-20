<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">

      <button class="close-btn" @click="$emit('close')">&times;</button>

      <h3 class="modal-title">{{ txType === 'deposit' ? 'Deposit' : 'Withdraw' }}</h3>

      <form @submit.prevent="handleSave" class="tx-form">

        <div class="form-group">
          <label>Amount*</label>
          <input
            type="number"
            v-model.number="form.amount"
            step="0.01"
            min="0.01"
            required
          />
        </div>

        <div class="form-group">
          <label>Note</label>
          <input
            type="text"
            v-model="form.note"
            maxlength="300"
          />
        </div>

        <div class="bottom-row">
          <div class="form-group date-group">
            <label>Date</label>
            <input
              type="date"
              v-model="form.created_at"
              :max="today"
            />
          </div>
          <button type="submit" class="save-btn" :disabled="isLoading">Save</button>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

const props = defineProps({
  goalId: { type: Number, required: true },
  txType: { type: String, required: true }
})

const emit = defineEmits(['close', 'transaction-added'])
const auth = useAuthStore()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const today = new Date().toISOString().split('T')[0]

const form = ref({
  amount: null,
  note: '',
  created_at: today
})

const isLoading = ref(false)
const errorMessage = ref('')

const handleSave = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    await auth.tryRestoreSession()

    if (!form.value.amount || form.value.amount <= 0) {
      errorMessage.value = 'Введите корректную сумму'
      return
    }

    const payload = {
      amount: form.value.amount,
      note: form.value.note || null,
      created_at: form.value.created_at || today
    }

    const response = await axios.post(
      `${API_BASE}/goals/${props.goalId}/operation/${props.txType}`,
      payload,
      { headers: { Authorization: `Bearer ${auth.accessToken}` } }
    )

    emit('transaction-added', response.data)
  } catch (error) {
    console.error(error)
    errorMessage.value = error.response?.data?.detail || 'Ошибка при сохранении.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-container {
  background: #ffffff;
  border-radius: 8px;
  width: 400px; padding: 30px;
  position: relative;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  font-family: sans-serif;
}
.close-btn {
  position: absolute; top: 10px; right: 15px;
  background: none; border: none; font-size: 24px; cursor: pointer;
}
.modal-title {
  margin-top: 0; margin-bottom: 20px;
  text-transform: capitalize; color: #333;
}
.tx-form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 16px; color: #111; }
.form-group input {
  background: #e8e8e8; border: none; border-radius: 6px;
  padding: 10px 12px; font-size: 16px; outline: none;
}
.bottom-row {
  display: flex; justify-content: space-between; align-items: flex-end;
}
.date-group { width: 60%; }
.save-btn {
  background: #66ff66; border: none; border-radius: 6px;
  padding: 10px 24px; font-size: 16px; font-weight: bold;
  cursor: pointer; color: #000; transition: background 0.2s;
}
.save-btn:hover { background: #55e655; }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.error-text { color: red; font-size: 14px; margin: 0; }
</style>