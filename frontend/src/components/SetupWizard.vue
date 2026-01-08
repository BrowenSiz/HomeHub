<!-- Path: frontend/src/components/SetupWizard.vue -->
<script setup>
import { ref, computed } from 'vue'
import { ShieldCheckIcon, KeyIcon, LockClosedIcon, CheckCircleIcon } from '@heroicons/vue/24/solid'
import api from '@/services/api'

const emit = defineEmits(['setup-complete'])

const step = ref(1)
const loading = ref(false)
const error = ref('')

// Данные формы
const form = ref({
  masterPassword: '',
  confirmPassword: '',
  pin: '',
  confirmPin: ''
})

// Валидация
const isPasswordValid = computed(() => {
  return form.value.masterPassword.length >= 8 && 
         form.value.masterPassword === form.value.confirmPassword
})

const isPinValid = computed(() => {
  return form.value.pin.length >= 4 && 
         form.value.pin === form.value.confirmPin
})

const nextStep = () => {
  error.value = ''
  step.value++
}

const finishSetup = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await api.setupSecurity(form.value.masterPassword, form.value.pin)
    // Успех! Переходим на финальный шаг
    step.value = 4
    setTimeout(() => {
      emit('setup-complete')
    }, 2000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка настройки'
    loading.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-hub-dark flex items-center justify-center z-[100] p-4">
    <div class="w-full max-w-lg bg-hub-panel rounded-2xl shadow-2xl border border-gray-700 overflow-hidden flex flex-col">
      
      <!-- Прогресс бар -->
      <div class="h-1 bg-gray-800 w-full">
        <div class="h-full bg-hub-accent transition-all duration-500" :style="{ width: `${(step / 4) * 100}%` }"></div>
      </div>

      <div class="p-8 flex-1 flex flex-col">
        
        <!-- ШАГ 1: Приветствие -->
        <div v-if="step === 1" class="text-center space-y-6 animate-fade-in">
          <div class="mx-auto w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center">
            <ShieldCheckIcon class="w-10 h-10 text-blue-500" />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-white">Добро пожаловать в HomeHub</h2>
            <p class="mt-2 text-gray-400">
              Это безопасное хранилище для ваших фото и видео. Перед началом работы необходимо создать ключи шифрования.
            </p>
          </div>
          <button @click="nextStep" class="w-full btn-primary">Начать настройку</button>
        </div>

        <!-- ШАГ 2: Мастер-пароль -->
        <div v-if="step === 2" class="space-y-6 animate-fade-in">
          <div class="flex items-center gap-3 mb-2">
            <KeyIcon class="w-6 h-6 text-hub-accent" />
            <h2 class="text-xl font-bold text-white">Мастер-пароль</h2>
          </div>
          <p class="text-sm text-gray-400">
            Этот пароль нужен <b>только</b> для восстановления доступа, если вы забудете PIN. Храните его надежно!
          </p>
          
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">Придумайте пароль (мин. 8 символов)</label>
              <input v-model="form.masterPassword" type="password" class="input-field" placeholder="••••••••" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">Повторите пароль</label>
              <input v-model="form.confirmPassword" type="password" class="input-field" placeholder="••••••••" />
            </div>
          </div>

          <button @click="nextStep" :disabled="!isPasswordValid" class="w-full btn-primary">Далее</button>
        </div>

        <!-- ШАГ 3: PIN код -->
        <div v-if="step === 3" class="space-y-6 animate-fade-in">
          <div class="flex items-center gap-3 mb-2">
            <LockClosedIcon class="w-6 h-6 text-hub-accent" />
            <h2 class="text-xl font-bold text-white">Код доступа (PIN)</h2>
          </div>
          <p class="text-sm text-gray-400">
            Используйте этот код для ежедневного входа в защищенную зону.
          </p>
          
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">PIN код (мин. 4 цифры)</label>
              <input v-model="form.pin" type="password" class="input-field tracking-widest" placeholder="1234" maxlength="8" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">Повторите PIN</label>
              <input v-model="form.confirmPin" type="password" class="input-field tracking-widest" placeholder="1234" maxlength="8" />
            </div>
          </div>

          <div v-if="error" class="text-red-400 text-sm text-center bg-red-900/20 p-2 rounded">
            {{ error }}
          </div>

          <button @click="finishSetup" :disabled="!isPinValid || loading" class="w-full btn-primary flex justify-center">
            <span v-if="loading" class="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mr-2"></span>
            {{ loading ? 'Генерация ключей...' : 'Завершить настройку' }}
          </button>
        </div>

        <!-- ШАГ 4: Успех -->
        <div v-if="step === 4" class="text-center space-y-6 animate-fade-in py-10">
          <CheckCircleIcon class="w-20 h-20 text-green-500 mx-auto animate-bounce" />
          <h2 class="text-2xl font-bold text-white">Все готово!</h2>
          <p class="text-gray-400">Система настроена и зашифрована.</p>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.input-field {
  @apply w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-hub-accent focus:ring-1 focus:ring-hub-accent transition-all;
}
.btn-primary {
  @apply bg-hub-accent hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}
.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>