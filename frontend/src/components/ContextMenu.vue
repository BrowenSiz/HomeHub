<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { 
  LockClosedIcon, LockOpenIcon, TrashIcon, 
  FolderPlusIcon, EyeIcon, CheckCircleIcon 
} from '@heroicons/vue/24/outline'

const props = defineProps({
  visible: Boolean,
  x: Number,
  y: Number,
  item: Object,
  selectedCount: Number
})

const emit = defineEmits(['close', 'action'])
const menuRef = ref(null)

const handleClickOutside = (e) => {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    emit('close')
  }
}

watch(() => props.visible, (val) => {
  if (val) setTimeout(() => document.addEventListener('click', handleClickOutside), 0)
  else document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div 
    v-if="visible"
    ref="menuRef"
    class="fixed z-[100] bg-[#1e1e20]/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-[0_10px_40px_rgba(0,0,0,0.6)] py-1.5 min-w-[220px] animate-scale-in origin-top-left overflow-hidden"
    :style="{ top: `${y}px`, left: `${x}px` }"
    @contextmenu.prevent
  >
    <!-- Header info -->
    <div class="px-4 py-2 border-b border-white/5 mb-1">
      <p class="text-xs font-bold text-gray-500 uppercase tracking-wider truncate">
        {{ selectedCount > 0 ? `Выбрано: ${selectedCount}` : item?.filename }}
      </p>
    </div>

    <!-- Actions -->
    <div class="flex flex-col gap-0.5">
      
      <!-- Open (Only single) -->
      <button v-if="selectedCount === 0" @click="$emit('action', 'open', item)" class="menu-item">
        <EyeIcon class="w-4 h-4" />
        <span>Открыть</span>
      </button>

      <!-- Select -->
      <button v-if="selectedCount === 0" @click="$emit('action', 'select', item)" class="menu-item">
        <CheckCircleIcon class="w-4 h-4" />
        <span>Выбрать</span>
      </button>

      <div class="h-px bg-white/10 my-1 mx-2"></div>

      <!-- Add to Album -->
      <button @click="$emit('action', 'add-to-album', item)" class="menu-item">
        <FolderPlusIcon class="w-4 h-4" />
        <span>Добавить в альбом...</span>
      </button>

      <!-- Encrypt / Decrypt -->
      <button v-if="!item?.is_encrypted" @click="$emit('action', 'encrypt', item)" class="menu-item text-blue-400 hover:text-blue-300">
        <LockClosedIcon class="w-4 h-4" />
        <span>Переместить в Сейф</span>
      </button>
      
      <button v-else @click="$emit('action', 'decrypt', item)" class="menu-item text-green-400 hover:text-green-300">
        <LockOpenIcon class="w-4 h-4" />
        <span>Восстановить из Сейфа</span>
      </button>

      <div class="h-px bg-white/10 my-1 mx-2"></div>

      <!-- Delete -->
      <button @click="$emit('action', 'delete', item)" class="menu-item text-red-400 hover:bg-red-500/10 hover:text-red-300">
        <TrashIcon class="w-4 h-4" />
        <span>Удалить</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.menu-item {
  @apply flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors w-full text-left;
}
.animate-scale-in {
  animation: scaleIn 0.1s ease-out;
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>