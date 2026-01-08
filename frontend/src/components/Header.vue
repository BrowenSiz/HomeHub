<script setup>
import ScannerControl from './ScannerControl.vue'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

defineProps({
  status: String,
  apiInfo: Object
})
</script>

<template>
  <header class="h-20 glass-panel rounded-[2rem] flex items-center justify-between px-8 shrink-0 z-30">
    <!-- Поиск -->
    <div class="relative w-1/3 group">
      <MagnifyingGlassIcon class="w-5 h-5 text-gray-500 absolute left-4 top-1/2 -translate-y-1/2 group-hover:text-hub-accent transition-colors" />
      <input 
        type="text" 
        placeholder="Поиск..." 
        class="w-full bg-[#0f1016]/50 border border-white/5 rounded-2xl py-3 pl-12 pr-4 text-sm text-gray-300 placeholder-gray-600 focus:outline-none focus:border-hub-accent/50 focus:bg-[#0f1016] transition-all"
        disabled
      />
    </div>

    <div class="flex items-center gap-8">
      <div class="flex flex-col items-end">
        <span class="text-[10px] font-bold text-gray-600 uppercase tracking-widest mb-0.5">Система</span>
        <div class="flex items-center gap-2">
          <span class="text-sm font-bold" :class="status === 'Онлайн' ? 'text-green-400' : 'text-red-400'">{{ status }}</span>
          <div class="w-2 h-2 rounded-full" :class="status === 'Онлайн' ? 'bg-green-500 shadow-[0_0_10px_#22c55e]' : 'bg-red-500'"></div>
        </div>
      </div>
      
      <div class="h-8 w-px bg-white/10"></div>
      
      <ScannerControl />
    </div>
  </header>
</template>