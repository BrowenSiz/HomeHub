<script setup>
import { 
  SignalIcon, SignalSlashIcon, 
  ChevronLeftIcon, LockClosedIcon,
  PhotoIcon, VideoCameraIcon, Squares2X2Icon
} from '@heroicons/vue/24/solid'

defineProps({
  status: String,
  apiInfo: Object,
  title: String,
  subtitle: String,
  showBack: Boolean,
  showLock: Boolean,
  showTools: Boolean,
  gridSize: Number,
  filterType: String
})

const emit = defineEmits(['back', 'lock', 'update:gridSize', 'update:filterType'])

const handleSliderChange = (e) => {
  emit('update:gridSize', parseInt(e.target.value))
}
</script>

<template>
  <header class="h-20 shrink-0 flex items-center justify-between px-8 glass-panel rounded-[2rem] relative z-20 transition-all duration-300">
    
    <div class="flex items-center gap-6 min-w-[200px]">
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
        <p v-if="subtitle" class="text-xs text-white/40 font-medium truncate max-w-[250px]">
          {{ subtitle }}
        </p>
      </div>
    </div>

    <div v-if="showTools" class="flex-1 flex justify-center items-center gap-8 animate-fade-in">
      
      <div class="flex p-1 bg-black/20 rounded-xl border border-white/5 backdrop-blur-sm">
        <button 
          @click="$emit('update:filterType', 'all')"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-300 flex items-center gap-2"
          :class="filterType === 'all' ? 'bg-white/10 text-white shadow-sm' : 'text-white/40 hover:text-white/70'"
        >
          <Squares2X2Icon class="w-3.5 h-3.5" />
          Все
        </button>
        <button 
          @click="$emit('update:filterType', 'photo')"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-300 flex items-center gap-2"
          :class="filterType === 'photo' ? 'bg-blue-500/20 text-blue-300 shadow-sm' : 'text-white/40 hover:text-white/70'"
        >
          <PhotoIcon class="w-3.5 h-3.5" />
          Фото
        </button>
        <button 
          @click="$emit('update:filterType', 'video')"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-300 flex items-center gap-2"
          :class="filterType === 'video' ? 'bg-purple-500/20 text-purple-300 shadow-sm' : 'text-white/40 hover:text-white/70'"
        >
          <VideoCameraIcon class="w-3.5 h-3.5" />
          Видео
        </button>
      </div>

      <div class="flex items-center gap-3 w-40 group">
        <PhotoIcon class="w-3 h-3 text-white/30" />
        
        <div class="relative flex-1 h-8 flex items-center">
           <input 
            type="range" 
            min="2" 
            max="8" 
            step="1"
            :value="gridSize"
            @input="handleSliderChange"
            class="w-full h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer hover:bg-white/20 transition-colors focus:outline-none slider-thumb"
          />
          <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-1 bg-white/30 rounded-full pointer-events-none"></div>
        </div>

        <PhotoIcon class="w-5 h-5 text-white/30" />
      </div>

    </div>

    <div class="flex items-center gap-4 min-w-[200px] justify-end">
      <button 
        v-if="showLock"
        @click="$emit('lock')"
        class="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-300 text-xs font-bold uppercase tracking-wide rounded-xl transition-all mr-2 hover:shadow-[0_0_15px_rgba(239,68,68,0.2)]"
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

<style scoped>
.slider-thumb::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  transition: transform 0.1s;
  margin-top: -2px; /* Выравнивание */
}

.slider-thumb::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>