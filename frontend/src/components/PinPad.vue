<!-- Path: frontend/src/components/PinPad.vue -->
<script setup>
import { ref, watch } from 'vue'
import { LockClosedIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  error: String,
  loading: Boolean
})

const emit = defineEmits(['submit'])

const pin = ref('')

// Автоматическая отправка при вводе 4 символов (или больше, если PIN длиннее)
// Но для надежности сделаем кнопку или Enter
const submit = () => {
  if (pin.value.length >= 4) {
    emit('submit', pin.value)
    pin.value = '' // Очищаем после попытки
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-full animate-fade-in">
    <div class="bg-hub-panel p-8 rounded-2xl shadow-2xl border border-gray-700 text-center max-w-sm w-full">
      <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
        <LockClosedIcon class="w-8 h-8 text-red-500" />
      </div>
      
      <h2 class="text-xl font-bold text-white mb-2">Вход в Сейф</h2>
      <p class="text-gray-400 text-sm mb-6">Введите PIN-код для доступа к зашифрованным файлам.</p>

      <form @submit.prevent="submit" class="space-y-4">
        <input 
          v-model="pin" 
          type="password" 
          inputmode="numeric" 
          maxlength="8"
          class="w-full text-center text-3xl tracking-[0.5em] bg-gray-900 border border-gray-700 rounded-lg py-3 text-white focus:border-hub-accent focus:ring-1 focus:ring-hub-accent outline-none transition-all placeholder-gray-700"
          placeholder="••••"
          autofocus
        />
        
        <div v-if="error" class="text-red-400 text-xs bg-red-900/20 p-2 rounded">
          {{ error }}
        </div>

        <button 
          type="submit" 
          :disabled="pin.length < 4 || loading"
          class="w-full bg-hub-accent hover:bg-blue-600 text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50 flex justify-center items-center"
        >
          <span v-if="loading" class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
          {{ loading ? 'Проверка...' : 'Разблокировать' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>