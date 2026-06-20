<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">

      <button class="close-btn" @click="$emit('close')">&times;</button>

      <div class="image-upload-wrapper" @click="triggerFileInput">
        <input
          type="file"
          ref="fileInput"
          accept="image/*"
          style="display: none"
          @change="onFileSelected"
        />
        <img v-if="imagePreview" :src="imagePreview" class="preview-img" />
        <div v-else class="plus-placeholder">+</div>
      </div>

      <form @submit.prevent="handleSubmit" class="goal-form">

        <div class="form-group">
          <label>Title*</label>
          <input type="text" v-model="form.title" maxlength="20" required />
        </div>

        <div class="form-group">
          <label>Description</label>
          <input type="text" v-model="form.description" maxlength="255" />
        </div>

        <div class="form-group">
          <label>Link</label>
          <input type="text" v-model="form.link" maxlength="2048" placeholder="https://..." />
        </div>

        <div class="form-group">
          <label>Goal Amount*</label>
          <input type="number" v-model.number="form.goal_amount" step="0.01" required />
        </div>

        <div class="date-row">
          <div class="form-group flex-1">
            <label>Start Date</label>
            <input type="date" v-model="form.start_date" />
          </div>
          <div class="form-group flex-1">
            <label>End Date</label>
            <input type="date" v-model="form.end_date" />
          </div>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="button-wrapper">
          <button type="submit" class="add-btn">ADD</button>
        </div>
      </form>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const emit = defineEmits(['close', 'goal-created'])

const fileInput = ref(null)
const imagePreview = ref(null)
const selectedFile = ref(null)
const errorMessage = ref('')

const form = ref({
  title: '',
  description: '',
  link: '',
  goal_amount: null,
  start_date: '',
  end_date: ''
})

const triggerFileInput = () => fileInput.value.click()

const onFileSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

const handleSubmit = async () => {
  try {
    errorMessage.value = ''

    await auth.tryRestoreSession()
    const token = auth.accessToken
    if (!token) {
      errorMessage.value = 'Сессия истекла. Пожалуйста, войдите в аккаунт заново.'
      return
    }

    if (!form.value.title.trim()) {
      errorMessage.value = 'Укажите название цели'
      return
    }
    if (!form.value.goal_amount) {
      errorMessage.value = 'Укажите сумму цели'
      return
    }

    if (form.value.end_date) {
      const today = new Date().toISOString().split('T')[0]
      if (form.value.end_date < today) {
        errorMessage.value = 'Конечная дата не может быть в прошлом'
        return
      }
    }

    const formData = new FormData()
    formData.append('title', form.value.title.trim())
    formData.append('goal_amount', String(form.value.goal_amount))

    if (form.value.description?.trim())
      formData.append('description', form.value.description.trim())
    if (form.value.link?.trim())
      formData.append('link', form.value.link.trim())
    if (form.value.start_date)
      formData.append('start_date', form.value.start_date)
    if (form.value.end_date)
      formData.append('end_date', form.value.end_date)
    if (selectedFile.value)
      formData.append('img', selectedFile.value)

    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/goals/`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    emit('goal-created', response.data)
    emit('close')

  } catch (error) {
    console.error(error)
    if (error.response?.data?.detail) {
      errorMessage.value = Array.isArray(error.response.data.detail)
        ? error.response.data.detail[0].msg
        : error.response.data.detail
    } else {
      errorMessage.value = 'Произошла ошибка при создании цели.'
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.2);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-container {
  background: #ffffff;
  border: 2px solid #00a2ff;
  border-radius: 8px;
  width: 450px; padding: 25px;
  position: relative;
  display: flex; flex-direction: column; gap: 15px;
}
.close-btn {
  position: absolute; top: 10px; right: 15px;
  background: none; border: none; font-size: 24px; cursor: pointer;
}
.image-upload-wrapper {
  width: 120px; height: 120px; background: #e0e0e0;
  border-radius: 12px; margin: 0 auto;
  display: flex; justify-content: center; align-items: center;
  cursor: pointer; overflow: hidden;
}
.plus-placeholder { font-size: 48px; color: #b0b0b0; line-height: 1; }
.preview-img { width: 100%; height: 100%; object-fit: cover; }

.goal-form { display: flex; flex-direction: column; gap: 12px; }
.form-group { display: flex; flex-direction: column; gap: 4px; font-family: sans-serif; }
.form-group label { font-size: 14px; font-weight: bold; color: #111; }
.form-group input {
  background: #e8e8e8; border: none; border-radius: 6px;
  padding: 8px 12px; font-size: 14px; outline: none;
}
.date-row { display: flex; gap: 15px; }
.flex-1 { flex: 1; }

.button-wrapper { display: flex; justify-content: flex-end; margin-top: 10px; }
.add-btn {
  background: #5eff5e; border: none; padding: 6px 18px;
  border-radius: 6px; font-weight: bold; font-size: 14px;
  cursor: pointer; transition: background 0.2s;
}
.add-btn:hover { background: #4cdb4c; }
.error-text { color: red; font-size: 12px; margin: 0; }
</style>