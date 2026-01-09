<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { 
  LockClosedIcon, 
  LockOpenIcon, 
  FolderIcon, 
  TrashIcon, 
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  x: Number,
  y: Number,
  item: Object
})

const emit = defineEmits(['close', 'action'])
const menuRef = ref(null)

const handleClickOutside = (e) => {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    emit('close')
  }
}

onMounted(() => {
  setTimeout(() => {
    document.addEventListener('click', handleClickOutside)
    document.addEventListener('contextmenu', handleClickOutside)
  }, 50)
  
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('contextmenu', handleClickOutside)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="fixed inset-0 z-[99999] pointer-events-none">
    <div 
      ref="menuRef"
      class="absolute min-w-[200px] bg-[#1e293b]/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-1.5 pointer-events-auto animate-scale-in origin-top-left"
      :style="{ top: `${y}px`, left: `${x}px` }"
    >
      <div class="px-3 py-2 border-b border-white/5 mb-1">
        <p class="text-[10px] font-bold text-white/40 uppercase tracking-wider truncate max-w-[160px]">
          {{ item.filename }}
        </p>
      </div>

      <div class="flex flex-col gap-0.5">
        
        <button 
          @click="emit('action', 'select')"
          class="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-white hover:bg-white/10 transition-colors group text-left"
        >
          <CheckCircleIcon class="w-4 h-4 text-white/70 group-hover:text-white" />
          Выбрать
        </button>

        <div class="h-px bg-white/5 my-1"></div>

        <button 
          v-if="!item.is_encrypted"
          @click="emit('action', 'lock')"
          class="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-white hover:bg-white/10 transition-colors group text-left"
        >
          <LockClosedIcon class="w-4 h-4 text-red-400 group-hover:scale-110 transition-transform" />
          В сейф
        </button>

        <button 
          v-else
          @click="emit('action', 'unlock')"
          class="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-white hover:bg-white/10 transition-colors group text-left"
        >
          <LockOpenIcon class="w-4 h-4 text-green-400 group-hover:scale-110 transition-transform" />
          Восстановить
        </button>

        <button 
          @click="emit('action', 'album')"
          class="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-white hover:bg-white/10 transition-colors group text-left"
        >
          <FolderIcon class="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
          В альбом
        </button>

        <div class="h-px bg-white/5 my-1"></div>

        <button 
          @click="emit('action', 'delete')"
          class="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-red-400 hover:bg-red-500/10 transition-colors group text-left"
        >
          <TrashIcon class="w-4 h-4 group-hover:scale-110 transition-transform" />
          Удалить
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.1s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>