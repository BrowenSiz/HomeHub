<script setup>
import { CloudArrowUpIcon } from '@heroicons/vue/24/outline'
import { useUploadStore } from '@/stores/upload'

defineProps({
  targetName: {
    type: String,
    default: 'библиотеку'
  }
})

const uploadStore = useUploadStore()
</script>

<template>
  <Transition name="fade">
    <div 
      v-if="uploadStore.isDragging" 
      class="fixed inset-0 z-[9999] bg-blue-600/20 backdrop-blur-md border-4 border-blue-500/50 m-4 rounded-[2.5rem] flex flex-col items-center justify-center pointer-events-none"
    >
      <div class="bg-[#0f172a]/80 p-8 rounded-3xl backdrop-blur-xl border border-white/10 shadow-2xl flex flex-col items-center animate-bounce-slow">
        <CloudArrowUpIcon class="w-24 h-24 text-blue-400 mb-4" />
        <h2 class="text-3xl font-bold text-white mb-2">Отпустите файлы</h2>
        <p class="text-white/70 text-lg">
          Импорт медиа в <span class="text-blue-300 font-bold">{{ targetName }}</span>
        </p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-bounce-slow {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(-5%); }
  50% { transform: translateY(5%); }
}
</style>