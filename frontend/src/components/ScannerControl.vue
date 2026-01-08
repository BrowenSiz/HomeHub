<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import { ArrowPathIcon } from '@heroicons/vue/24/solid'

const isScanning = ref(false)
const message = ref('')

const startScan = async () => {
  isScanning.value = true
  message.value = 'Запуск...'
  try {
    const response = await api.scanLibrary()
    message.value = 'Сканирование запущено'
    setTimeout(() => {
      isScanning.value = false
      message.value = ''
    }, 3000)
  } catch (error) {
    console.error(error)
    isScanning.value = false
    message.value = 'Ошибка запуска'
  }
}
</script>

<template>
  <div class="flex items-center space-x-3">
    <span v-if="message" class="text-xs text-hub-accent animate-pulse">{{ message }}</span>
    <button 
      @click="startScan"
      :disabled="isScanning"
      class="flex items-center gap-2 px-4 py-2 bg-hub-panel hover:bg-gray-700 text-white text-sm font-medium rounded-lg transition-colors border border-gray-700 disabled:opacity-50"
    >
      <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': isScanning }" />
      {{ isScanning ? 'Сканирование...' : 'Обновить библиотеку' }}
    </button>
  </div>
</template>