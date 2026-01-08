<script setup>
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  isOpen: Boolean,
  title: String,
  message: String,
  confirmText: { type: String, default: 'Подтвердить' },
  cancelText: { type: String, default: 'Отмена' },
  isDestructive: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 animate-fade-in">
    <div class="bg-hub-panel w-full max-w-md rounded-xl border border-gray-700 shadow-2xl p-6 transform transition-none animate-scale-in">
      <div class="flex items-start gap-4">
        <div class="p-2 bg-gray-800 rounded-full shrink-0">
          <ExclamationTriangleIcon class="w-6 h-6 text-yellow-500" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-white">{{ title }}</h3>
          <p class="mt-2 text-sm text-gray-400">{{ message }}</p>
        </div>
      </div>
      <div class="mt-6 flex justify-end gap-3">
        <button @click="$emit('cancel')" class="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">{{ cancelText }}</button>
        <button @click="$emit('confirm')" class="px-4 py-2 text-sm font-medium text-white rounded-lg shadow-lg transition-colors" :class="isDestructive ? 'bg-red-600 hover:bg-red-700' : 'bg-hub-accent hover:bg-blue-600'">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.15s ease-out; }
.animate-scale-in { animation: scaleIn 0.15s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>