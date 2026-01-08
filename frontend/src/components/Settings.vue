<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  ShieldCheckIcon, ServerStackIcon, CalculatorIcon, 
  ArrowPathIcon, CheckCircleIcon 
} from '@heroicons/vue/24/outline'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

const notify = useNotificationStore()

const stats = ref(null)
const isLoadingStats = ref(true)

const masterPassword = ref('')
const newPin = ref('')
const confirmPin = ref('')
const isChangingPin = ref(false)

const canSubmit = computed(() => {
  return masterPassword.value.length > 0 &&
         newPin.value.length >= 4 &&
         newPin.value === confirmPin.value
})

const loadStats = async () => {
  isLoadingStats.value = true
  try {
    const res = await api.getSystemStats()
    stats.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingStats.value = false
  }
}

const handleChangePin = async () => {
  if (!canSubmit.value) return
  isChangingPin.value = true
  try {
    await api.changePin(masterPassword.value, newPin.value)
    notify.show('PIN код успешно изменен', 'success')
    masterPassword.value = ''
    newPin.value = ''
    confirmPin.value = ''
  } catch (e) {
    const msg = e.response?.data?.detail || 'Ошибка смены PIN'
    notify.show(msg, 'error')
  } finally {
    isChangingPin.value = false
  }
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div class="p-8 max-w-4xl mx-auto space-y-8 animate-fade-in pb-20">
    <div>
      <h2 class="text-3xl font-bold text-white mb-2">Настройки</h2>
      <p class="text-gray-400">Управление безопасностью и системой</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      
      <div class="space-y-6">
        <h3 class="text-xl font-bold text-white flex items-center gap-2">
          <ShieldCheckIcon class="w-6 h-6 text-hub-accent" />
          Безопасность
        </h3>
        
        <div class="bg-hub-panel border border-gray-700 rounded-2xl p-6 shadow-xl">
          <h4 class="text-lg font-medium text-white mb-4">Смена PIN кода</h4>
          <p class="text-xs text-gray-500 mb-6">
            Для смены PIN кода необходимо ввести ваш текущий Мастер-пароль. Это гарантирует, что изменения вносит владелец.
          </p>

          <form @submit.prevent="handleChangePin" class="space-y-4">
            <div>
              <label class="label">Мастер-пароль</label>
              <input v-model="masterPassword" type="password" class="input" placeholder="Ваш длинный пароль" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="label">Новый PIN</label>
                <input v-model="newPin" type="password" maxlength="8" class="input font-mono tracking-widest" placeholder="1234" />
              </div>
              <div>
                <label class="label">Повторите PIN</label>
                <input v-model="confirmPin" type="password" maxlength="8" class="input font-mono tracking-widest" placeholder="1234" />
              </div>
            </div>

            <button 
              type="submit" 
              :disabled="!canSubmit || isChangingPin"
              class="w-full bg-hub-accent hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl transition-all flex justify-center"
            >
              <ArrowPathIcon v-if="isChangingPin" class="w-5 h-5 animate-spin" />
              <span v-else>Обновить PIN</span>
            </button>
          </form>
        </div>
      </div>

      <div class="space-y-6">
        <h3 class="text-xl font-bold text-white flex items-center gap-2">
          <ServerStackIcon class="w-6 h-6 text-purple-400" />
          Система
        </h3>

        <div class="bg-hub-panel border border-gray-700 rounded-2xl p-6 shadow-xl relative overflow-hidden">
          <div class="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none"></div>

          <div v-if="isLoadingStats" class="flex justify-center py-10">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-white"></div>
          </div>

          <div v-else class="space-y-6 relative z-10">
            <div class="flex justify-between items-center border-b border-white/5 pb-4">
              <span class="text-gray-400">Версия HomeHub</span>
              <span class="font-mono text-white">{{ stats.version }}</span>
            </div>
            
            <div class="flex justify-between items-center border-b border-white/5 pb-4">
              <span class="text-gray-400">Всего файлов</span>
              <span class="text-white font-bold text-xl">{{ stats.total_files }}</span>
            </div>

            <div class="flex justify-between items-center border-b border-white/5 pb-4">
              <span class="text-gray-400">Занято места</span>
              <span class="text-white font-bold text-xl">{{ formatBytes(stats.total_size_bytes) }}</span>
            </div>

            <div class="flex items-start gap-3 bg-green-500/10 p-3 rounded-lg border border-green-500/20">
              <CheckCircleIcon class="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
              <div>
                <p class="text-sm font-medium text-green-400">Система активна</p>
                <p class="text-xs text-green-400/70">База данных и хранилище работают корректно.</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-hub-panel border border-gray-700 rounded-2xl p-6 shadow-xl">
          <h4 class="text-white font-medium mb-2 flex items-center gap-2">
            <CalculatorIcon class="w-5 h-5 text-gray-400" />
            О проекте
          </h4>
          <p class="text-sm text-gray-400 leading-relaxed">
            HomeHub — это локальное решение для хранения ваших воспоминаний. Ваши данные никогда не покидают это устройство.
            <br><br>
            В версии <b>v1.0</b> добавлены функции смены PIN-кода и улучшенная производительность сканирования.
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.label { @apply block text-xs font-medium text-gray-500 mb-1.5 uppercase tracking-wide; }
.input { @apply w-full bg-black/30 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:border-hub-accent focus:ring-1 focus:ring-hub-accent outline-none transition-all placeholder-gray-700; }
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>