<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">

      <button class="close-btn" @click="$emit('close')">&times;</button>

      <div class="image-upload-wrapper" @click="isEditing ? triggerFileInput() : null" :style="{ cursor: isEditing ? 'pointer' : 'default' }">
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

      <form @submit.prevent="handleSave" class="goal-form">

        <div class="form-group">
          <label>Title*</label>
          <input type="text" v-model="form.title" maxlength="20" :disabled="!isEditing" required />
        </div>

        <div class="form-group">
          <label>Description</label>
          <input type="text" v-model="form.description" maxlength="255" :disabled="!isEditing" />
        </div>

        <div class="form-group">
          <label>Link</label>
          <input type="text" v-model="form.link" maxlength="2048" :disabled="!isEditing" placeholder="https://..." />
        </div>

        <div class="form-group">
          <label>Goal Amount*</label>
          <input type="number" v-model.number="form.goal_amount" step="0.01" :disabled="!isEditing" required />
        </div>

        <div class="date-row">
          <div class="form-group flex-1">
            <label>Start Date</label>
            <input type="date" v-model="form.start_date" :disabled="!isEditing" />
          </div>
          <div class="form-group flex-1">
            <label>End Date</label>
            <input type="date" v-model="form.end_date" :disabled="!isEditing" />
          </div>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="button-wrapper">
          <template v-if="!isEditing">
            <button type="button" class="delete-btn" @click="handleDelete">DELETE</button>
            <button type="button" class="edit-btn" @click="isEditing = true">EDIT</button>
          </template>
          <template v-else>
            <button type="button" class="cancel-btn" @click="handleCancel">CANCEL</button>
            <button type="submit" class="save-btn">SAVE</button>
          </template>
        </div>
      </form>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

const props = defineProps({
  goal: { type: Object, required: true }
})

const emit = defineEmits(['close', 'goal-updated', 'goal-deleted'])
const auth = useAuthStore()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const isEditing = ref(false)
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

const initForm = () => {
  form.value = {
    title: props.goal.title || '',
    description: props.goal.description || '',
    link: props.goal.link || '',
    goal_amount: props.goal.goal_amount || null,
    start_date: props.goal.start_date || '',
    end_date: props.goal.end_date || ''
  }
  if (props.goal.img_path) {
    imagePreview.value = props.goal.img_path.startsWith('/static/')
      ? `${API_BASE}${props.goal.img_path}`
      : props.goal.img_path
  } else {
    imagePreview.value = '/placeholder.png'
  }
  selectedFile.value = null
}

onMounted(() => {
  initForm()
})

const triggerFileInput = () => fileInput.value.click()

const onFileSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

const handleCancel = () => {
  initForm()
  isEditing.value = false
  errorMessage.value = ''
}

const handleDelete = async () => {
  try {
    errorMessage.value = ''
    await auth.tryRestoreSession()

    await axios.delete(`${API_BASE}/goals/${props.goal.id}`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })
    emit('goal-deleted', props.goal.id)
    emit('close')
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Не удалось удалить цель.'
  }
}

const handleSave = async () => {
  try {
    errorMessage.value = ''
    await auth.tryRestoreSession()

    if (!form.value.title.trim()) {
      errorMessage.value = 'Укажите название цели'
      return
    }

    const formData = new FormData()
    formData.append('title', form.value.title.trim())
    formData.append('goal_amount', String(form.value.goal_amount))
    formData.append('description', form.value.description?.trim() || '')
    formData.append('link', form.value.link?.trim() || '')
    formData.append('start_date', form.value.start_date || '')
    formData.append('end_date', form.value.end_date || '')

    if (selectedFile.value) {
      formData.append('img', selectedFile.value)
    }

    const response = await axios.patch(`${API_BASE}/goals/${props.goal.id}`, formData, {
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })

    emit('goal-updated', response.data)
    isEditing.value = false
  } catch (error) {
    console.error(error)
    errorMessage.value = error.response?.data?.detail || 'Ошибка при сохранении изменений.'
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4);
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
  overflow: hidden;
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
.form-group input:disabled { background: #f5f5f5; color: #666; cursor: not-allowed; }
.date-row { display: flex; gap: 15px; }
.flex-1 { flex: 1; }

.button-wrapper { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }

.edit-btn, .save-btn {
  background: #5eff5e; border: none; padding: 6px 18px;
  border-radius: 6px; font-weight: bold; font-size: 14px; cursor: pointer;
}
.delete-btn, .cancel-btn {
  background: #ff5e5e; border: none; padding: 6px 18px;
  border-radius: 6px; font-weight: bold; font-size: 14px; color: white; cursor: pointer;
}
.edit-btn:hover { background: #4cdb4c; }
.delete-btn:hover { background: #e04b4b; }
.cancel-btn:hover { background: #cccccc; color: black; }
.error-text { color: red; font-size: 12px; margin: 0; }
</style>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4);
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
  overflow: hidden;
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
.form-group input:disabled { background: #f5f5f5; color: #666; cursor: not-allowed; }
.date-row { display: flex; gap: 15px; }
.flex-1 { flex: 1; }

.button-wrapper { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }

.edit-btn, .save-btn {
  background: #5eff5e; border: none; padding: 6px 18px;
  border-radius: 6px; font-weight: bold; font-size: 14px; cursor: pointer;
}
.delete-btn, .cancel-btn {
  background: #ff5e5e; border: none; padding: 6px 18px;
  border-radius: 6px; font-weight: bold; font-size: 14px; color: white; cursor: pointer;
}
.edit-btn:hover { background: #4cdb4c; }
.delete-btn:hover { background: #e04b4b; }
.cancel-btn:hover { background: #cccccc; color: black; }
.error-text { color: red; font-size: 12px; margin: 0; }
</style>