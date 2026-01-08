<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { 
  ShieldCheckIcon, 
  ArrowPathIcon, 
  KeyIcon,
  CloudArrowDownIcon,
  PowerIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const notify = useNotificationStore()

const currentPin = ref('')
const newPin = ref('')
const confirmPin = ref('')
const masterPassword = ref('')
const loading = ref(false)

const updateInfo = ref(null)
const updateLoading = ref(false)
const updateInstalling = ref(false)
const updateReadyToRestart = ref(false)

const handleChangePin = async () => {
  if (newPin.value !== confirmPin.value) {
    notify.show('PIN коды не совпадают', 'error')
    return
  }
  if (newPin.value.length < 4) {
    notify.show('PIN код слишком короткий', 'error')
    return
  }

  loading.value = true
  try {
    await api.changePin(masterPassword.value, newPin.value)
    notify.show('PIN код успешно изменен', 'success')
    currentPin.value = ''
    newPin.value = ''
    confirmPin.value = ''
    masterPassword.value = ''
  } catch (error) {
    notify.show('Ошибка смены PIN кода. Проверьте мастер-пароль.', 'error')
  } finally {
    loading.value = false
  }
}

const checkForUpdates = async () => {
  updateLoading.value = true
  try {
    const res = await api.checkUpdates()
    updateInfo.value = res.data
    if (!res.data.update_available) {
      notify.show('У вас установлена последняя версия', 'success')
    }
  } catch (e) {
    notify.show('Ошибка проверки обновлений', 'error')
  } finally {
    updateLoading.value = false
  }
}

const installUpdate = async () => {
  if (!updateInfo.value?.update_available) return
  
  updateInstalling.value = true
  try {
    await api.installUpdate()
    updateReadyToRestart.value = true
    notify.show('Обновление готово к установке', 'success')
  } catch (e) {
    notify.show('Ошибка скачивания обновления', 'error')
    updateInstalling.value = false
  }
}

const restartApp = async () => {
  try {
    await api.restartApp()
  } catch (e) {
  }
}

onMounted(() => {
  checkForUpdates()
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-10">
    
    <!-- СЕКЦИЯ ОБНОВЛЕНИЯ -->
    <section class="bg-white/5 rounded-3xl p-8 border border-white/10 backdrop-blur-md">
      <div class="flex items-center gap-4 mb-6">
        <div class="p-3 bg-blue-500/20 rounded-2xl text-blue-400">
          <CloudArrowDownIcon class="w-8 h-8" />
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">Обновление системы</h3>
          <p class="text-white/50 text-sm">Текущая версия: {{ updateInfo?.current_version || '...' }}</p>
        </div>
      </div>

      <div class="bg-black/20 rounded-2xl p-6 border border-white/5">
        <div v-if="updateLoading" class="flex items-center gap-3 text-white/70">
          <ArrowPathIcon class="w-5 h-5 animate-spin" />
          Проверка обновлений...
        </div>

        <div v-else-if="updateReadyToRestart" class="space-y-4">
          <div class="text-green-400 font-medium flex items-center gap-2">
            <ShieldCheckIcon class="w-5 h-5" />
            Обновление скачано и готово
          </div>
          <p class="text-white/60 text-sm">Приложение перезапустится для завершения установки.</p>
          <button @click="restartApp" class="px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-xl font-bold transition-all flex items-center gap-2 w-full justify-center">
            <PowerIcon class="w-5 h-5" />
            Перезапустить HomeHub
          </button>
        </div>

        <div v-else-if="updateInfo?.update_available" class="space-y-4">
          <div class="flex justify-between items-start">
            <div>
              <div class="text-lg font-bold text-white mb-1">Доступна версия {{ updateInfo.latest_version }}</div>
              <div class="text-white/50 text-sm">Рекомендуется установить обновление</div>
            </div>
            <span class="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs font-bold rounded-full">NEW</span>
          </div>
          
          <button 
            @click="installUpdate" 
            :disabled="updateInstalling"
            class="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2"
          >
            <ArrowPathIcon v-if="updateInstalling" class="w-5 h-5 animate-spin" />
            <span v-if="updateInstalling">Скачивание и установка...</span>
            <span v-else>Скачать и обновить</span>
          </button>
        </div>

        <div v-else class="flex items-center justify-between text-white/60">
          <span>У вас установлена последняя версия</span>
          <button @click="checkForUpdates" class="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">Проверить снова</button>
        </div>
      </div>
    </section>

    <!-- СЕКЦИЯ БЕЗОПАСНОСТИ -->
    <section class="bg-white/5 rounded-3xl p-8 border border-white/10 backdrop-blur-md">
      <div class="flex items-center gap-4 mb-6">
        <div class="p-3 bg-red-500/20 rounded-2xl text-red-400">
          <KeyIcon class="w-8 h-8" />
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">Безопасность</h3>
          <p class="text-white/50 text-sm">Смена PIN кода доступа</p>
        </div>
      </div>

      <div class="space-y-4 max-w-md">
        <div>
          <label class="block text-white/70 text-sm font-medium mb-2">Мастер-пароль</label>
          <input type="password" v-model="masterPassword" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500/50 transition-colors" placeholder="Введите мастер-пароль" />
        </div>
        
        <div>
          <label class="block text-white/70 text-sm font-medium mb-2">Новый PIN код</label>
          <input type="password" v-model="newPin" maxlength="4" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500/50 transition-colors text-center tracking-[1em] font-mono" placeholder="••••" />
        </div>

        <div>
          <label class="block text-white/70 text-sm font-medium mb-2">Подтвердите PIN</label>
          <input type="password" v-model="confirmPin" maxlength="4" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500/50 transition-colors text-center tracking-[1em] font-mono" placeholder="••••" />
        </div>

        <button 
          @click="handleChangePin" 
          :disabled="loading || !masterPassword || newPin.length < 4"
          class="w-full py-4 bg-white/10 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-bold transition-all mt-4"
        >
          <span v-if="loading">Сохранение...</span>
          <span v-else>Изменить PIN</span>
        </button>
      </div>
    </section>
  </div>
</template>