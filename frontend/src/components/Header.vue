<script setup>
import { 
  SignalIcon, SignalSlashIcon, 
  ChevronLeftIcon, LockClosedIcon,
  MagnifyingGlassIcon
} from '@heroicons/vue/24/solid'

defineProps({
  status: String,
  apiInfo: Object,
  title: String,
  subtitle: String,
  showBack: Boolean,
  showLock: Boolean
})

defineEmits(['back', 'lock'])
</script>

<template>
  <header class="h-20 shrink-0 flex items-center justify-between px-8 glass-panel rounded-[2rem] relative z-20">
    
    <div class="flex items-center gap-6 flex-1">
      
      <button 
        v-if="showBack" 
        @click="$emit('back')"
        class="w-10 h-10 flex items-center justify-center rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 text-white transition-all hover:scale-105 active:scale-95"
      >
        <ChevronLeftIcon class="w-5 h-5" />
      </button>

      <div class="flex flex-col justify-center">
        <h2 class="text-xl font-bold text-white leading-tight flex items-center gap-3">
          {{ title }}
          <span v-if="showLock" class="px-2 py-0.5 bg-red-500/10 border border-red-500/20 rounded-lg text-[10px] text-red-400 font-bold uppercase tracking-wider">
            Secure
          </span>
        </h2>
        <p v-if="subtitle" class="text-xs text-white/40 font-medium truncate max-w-[300px]">
          {{ subtitle }}
        </p>
      </div>
    </div>

    <div class="flex items-center gap-4">
      
      <button 
        v-if="showLock"
        @click="$emit('lock')"
        class="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-300 text-xs font-bold uppercase tracking-wide rounded-xl transition-all mr-4 hover:shadow-[0_0_15px_rgba(239,68,68,0.2)]"
      >
        <LockClosedIcon class="w-4 h-4" />
        <span>Закрыть</span>
      </button>

      <div 
        class="flex items-center gap-2 px-3 py-1.5 rounded-xl border backdrop-blur-md transition-all duration-500"
        :class="status === 'Онлайн' 
          ? 'bg-green-500/5 border-green-500/10 text-green-400' 
          : 'bg-red-500/5 border-red-500/10 text-red-400'"
      >
        <span class="relative flex h-2 w-2">
          <span v-if="status === 'Онлайн'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2" :class="status === 'Онлайн' ? 'bg-green-500' : 'bg-red-500'"></span>
        </span>
        <span class="text-[10px] font-bold uppercase tracking-wider">{{ status }}</span>
      </div>

    </div>
  </header>
</template>