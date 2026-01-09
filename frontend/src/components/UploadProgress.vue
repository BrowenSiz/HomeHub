<script setup>
import { useUploadStore } from '@/stores/upload'
import { ArrowPathIcon, CheckCircleIcon } from '@heroicons/vue/24/solid'

const uploadStore = useUploadStore()
</script>

<template>
  <Transition name="slide-up">
    <div 
      v-if="uploadStore.isUploading" 
      class="fixed bottom-8 right-8 z-50 w-80 glass-panel rounded-2xl p-4 shadow-2xl border border-white/10 bg-[#1e293b]/90 backdrop-blur-xl"
    >
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center">
            <ArrowPathIcon class="w-6 h-6 text-blue-400 animate-spin" />
          </div>
          <div>
            <h4 class="text-sm font-bold text-white">Загрузка...</h4>
            <p class="text-xs text-white/50">
              {{ uploadStore.finishedFiles }} из {{ uploadStore.totalFiles }} файлов
            </p>
          </div>
        </div>
        <span class="text-xs font-mono font-bold text-blue-400">
          {{ Math.round(uploadStore.progress) }}%
        </span>
      </div>

      <!-- Progress Bar -->
      <div class="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
        <div 
          class="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300 ease-out"
          :style="{ width: `${uploadStore.progress}%` }"
        ></div>
      </div>

      <!-- Current File -->
      <div class="mt-2 flex justify-between items-center">
        <p class="text-[10px] text-white/30 truncate max-w-[200px]">
          {{ uploadStore.currentFileName }}
        </p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.glass-panel {
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>