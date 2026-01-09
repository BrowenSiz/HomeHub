<script setup>
import { ref } from 'vue'
import { XMarkIcon, MinusIcon, Square2StackIcon } from '@heroicons/vue/24/outline'

const logoError = ref(false)

const minimize = () => {
  if (window.pywebview) window.pywebview.api.minimize()
}

const maximize = () => {
  if (window.pywebview) window.pywebview.api.maximize()
}

const close = () => {
  if (window.pywebview) window.pywebview.api.close()
}
</script>

<template>
  <div class="h-10 flex items-center justify-between px-4 select-none relative z-[9999] bg-[#0f172a] border-b border-white/5">
    
    <div class="absolute inset-0 pywebview-drag-region w-full h-full z-0"></div>

    <div class="flex items-center gap-3 relative z-10 pointer-events-none">
      <div class="w-6 h-6 rounded-lg overflow-hidden flex items-center justify-center">
        <img 
          v-if="!logoError"
          src="/logo.png" 
          alt="Logo" 
          class="w-full h-full object-contain"
          @error="logoError = true" 
        />
        <div v-else class="w-full h-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
          <span class="text-white font-black text-[8px]">H</span>
        </div>
      </div>
      <span class="text-xs font-bold text-white/50 tracking-widest uppercase">HomeHub</span>
    </div>

    <div class="flex items-center gap-1 relative z-10">
      <button @click="minimize" class="win-btn hover:bg-white/10" title="Свернуть">
        <MinusIcon class="w-4 h-4" />
      </button>
      <button @click="maximize" class="win-btn hover:bg-white/10" title="Развернуть">
        <Square2StackIcon class="w-3.5 h-3.5" />
      </button>
      <button @click="close" class="win-btn hover:bg-red-500 hover:text-white" title="Закрыть">
        <XMarkIcon class="w-4 h-4" />
      </button>
    </div>

  </div>
</template>

<style scoped>
.win-btn {
  @apply w-8 h-8 flex items-center justify-center rounded-lg text-white/50 transition-colors cursor-pointer;
  -webkit-app-region: no-drag; 
}

.pywebview-drag-region {
  -webkit-app-region: drag;
  cursor: default;
}
</style>