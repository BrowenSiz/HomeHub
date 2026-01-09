<script setup>
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

defineProps({
  isOpen: Boolean,
  title: String,
  message: String
})

const emit = defineEmits(['close', 'confirm'])
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

      <div class="relative w-full max-w-sm bg-[#1e293b] rounded-[2rem] border border-white/10 shadow-2xl p-6 flex flex-col gap-4 animate-scale-in">
        
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center shrink-0">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-500" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white leading-tight">{{ title }}</h3>
            <p class="text-white/50 text-sm mt-1">{{ message }}</p>
          </div>
        </div>

        <div class="flex gap-3 mt-2">
          <button 
            @click="$emit('close')"
            class="flex-1 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium transition-colors"
          >
            Отмена
          </button>
          <button 
            @click="$emit('confirm')"
            class="flex-1 py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold transition-colors shadow-lg shadow-red-900/20"
          >
            Удалить
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>