<script setup>
import { ref, computed } from 'vue'
import { 
  PlayCircleIcon, 
  LockClosedIcon, LockOpenIcon, TrashIcon, FolderPlusIcon, XMarkIcon
} from '@heroicons/vue/24/outline'
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/vue/24/solid'
import ContextMenu from './ContextMenu.vue'
import AlbumSelectorModal from './AlbumSelectorModal.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const props = defineProps({ items: { type: Array, required: true } })
const emit = defineEmits(['refresh', 'open-viewer'])
const authStore = useAuthStore()
const notify = useNotificationStore()

// State
const selectedIds = ref(new Set())
const isSelectionMode = computed(() => selectedIds.value.size > 0)

// Context Menu State
const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const activeItem = ref(null) // Элемент под курсором при вызове меню

// Modals State
const showConfirm = ref(false)
const confirmAction = ref(null)
const showAlbumSelector = ref(false)

const isSelected = (id) => selectedIds.value.has(id)
const isVideo = (item) => item.media_type && item.media_type.startsWith('video/')
const getFileExtension = (filename) => filename.split('.').pop().toUpperCase().slice(0, 4)

// --- MOUSE INTERACTIONS ---

const handleLeftClick = (event, item) => {
  // 1. Ctrl/Cmd Click -> Toggle Selection
  if (event.ctrlKey || event.metaKey) {
    toggleSelection(item.id)
    return
  }
  
  // 2. Shift Click (Range) - Simplified
  if (event.shiftKey && isSelectionMode.value) {
    toggleSelection(item.id)
    return
  }

  // 3. Selection Mode -> Toggle
  if (isSelectionMode.value) {
    toggleSelection(item.id)
  } 
  // 4. Normal Mode -> Open Viewer
  else {
    emit('open-viewer', item)
  }
}

const handleRightClick = (event, item) => {
  event.preventDefault() // Предотвращаем нативное меню
  
  // Логика: Если кликаем по файлу, который УЖЕ выбран -> меню для всей группы
  // Если кликаем по невыбранному -> меню только для него (но не выбираем его визуально сразу)
  if (!selectedIds.value.has(item.id)) {
    activeItem.value = item
  } else {
    // Если кликнули по уже выбранному, то активный элемент - это он, но действие будет для всех
    activeItem.value = item
  }

  // Позиционирование (прямо под курсором)
  menuX.value = event.clientX
  menuY.value = event.clientY
  menuVisible.value = true
}

const toggleSelection = (id) => {
  if (selectedIds.value.has(id)) selectedIds.value.delete(id)
  else selectedIds.value.add(id)
}

const clearSelection = () => selectedIds.value.clear()

// --- ACTIONS ---

const handleMenuAction = (action, item) => {
  menuVisible.value = false
  const targetItem = item || activeItem.value

  if (action === 'open') {
    emit('open-viewer', targetItem)
    return
  }

  if (action === 'select') {
    selectedIds.value.add(targetItem.id)
    return
  }

  // Определяем список ID для операции
  let ids = []
  // Если мультивыбор активен И целевой элемент входит в выборку -> применяем ко всем
  if (selectedIds.value.has(targetItem.id)) {
    ids = Array.from(selectedIds.value)
  } else {
    // Иначе применяем только к этому элементу
    ids = [targetItem.id]
  }

  if (ids.length === 0) return

  // Сохраняем IDs для модалок
  // Используем временный объект, чтобы не мутировать реальный item
  activeItem.value = { ...targetItem, _targetIds: ids } 

  if (action === 'add-to-album') showAlbumSelector.value = true
  else if (action === 'encrypt') {
    if (!authStore.isVaultUnlocked) { notify.show('Сначала разблокируйте Сейф!', 'warning'); return }
    confirmAction.value = 'encrypt'; showConfirm.value = true
  } 
  else if (action === 'decrypt') { confirmAction.value = 'decrypt'; showConfirm.value = true }
  else if (action === 'delete') { confirmAction.value = 'delete'; showConfirm.value = true }
}

const executeConfirm = async () => {
  showConfirm.value = false
  const ids = activeItem.value._targetIds || [activeItem.value.id]
  try {
    let res;
    if (confirmAction.value === 'encrypt') res = await api.encryptMedia(ids)
    else if (confirmAction.value === 'decrypt') res = await api.decryptMedia(ids)
    else if (confirmAction.value === 'delete') res = await api.deleteMedia(ids)
    
    notify.show('Операция выполнена успешно', 'success')
    // Очищаем выделение только если удалили или скрыли файлы
    if (confirmAction.value !== 'decrypt') clearSelection() 
    emit('refresh')
  } catch (e) { notify.show('Ошибка операции', 'error') }
}

const handleAlbumSelect = async (album) => {
  const ids = activeItem.value._targetIds || [activeItem.value.id]
  try {
    await api.setAlbum(ids, album.id)
    notify.show('Альбом обновлен', 'success')
    clearSelection()
    emit('refresh')
  } catch (e) { notify.show('Ошибка', 'error') }
}

const getMediaSource = (item) => {
  return `/api/media/${item.id}/thumbnail`
}

const dialogMessage = () => {
  const count = activeItem.value?._targetIds?.length || 1
  return `Выбрано объектов: ${count}. Вы уверены?`
}
</script>

<template>
  <div v-if="items.length === 0" class="flex flex-col items-center justify-center h-64 text-white/30">
    <p class="text-lg">Нет файлов</p>
  </div>

  <div v-else class="relative min-h-[50vh] pb-32">
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 select-none">
      
      <div 
        v-for="item in items" 
        :key="item.id" 
        @click="handleLeftClick($event, item)"
        @contextmenu="handleRightClick($event, item)"
        class="group relative aspect-square bg-[#0f1016] rounded-2xl overflow-hidden cursor-pointer shadow-lg border border-white/5"
      >
        <!-- THUMBNAIL -->
        <img 
          :src="getMediaSource(item)" 
          class="w-full h-full object-cover transition-transform duration-700"
          :class="{ 'opacity-60': isSelected(item.id) }"
          loading="lazy"
        />
        
        <!-- VIDEO ICON -->
        <div v-if="isVideo(item)" class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="bg-black/30 backdrop-blur-md rounded-full p-2 border border-white/10 group-hover:scale-110 transition-transform">
            <PlayCircleIcon class="w-8 h-8 text-white/90" />
          </div>
        </div>

        <!-- SELECTION OVERLAY (Inner Border & Icon) -->
        <div v-if="isSelected(item.id)" class="absolute inset-0 z-20 pointer-events-none rounded-2xl border-[3px] border-hub-accent flex items-center justify-center bg-hub-accent/10">
          <CheckCircleSolid class="w-10 h-10 text-hub-accent bg-white rounded-full shadow-lg" />
        </div>

        <!-- BADGES (Always Visible) -->
        <div class="absolute bottom-0 left-0 right-0 p-3 flex justify-between items-end bg-gradient-to-t from-black/90 to-transparent pointer-events-none">
           <!-- Album -->
           <div v-if="item.album" class="glass-badge truncate max-w-[60%] text-[10px] font-bold text-white px-2 py-1 rounded-lg">
             {{ item.album.name }}
           </div>
           <div v-else></div>

           <!-- Ext -->
           <div class="glass-badge text-[9px] font-black uppercase text-white/80 tracking-wider px-1.5 py-0.5 rounded">
             {{ getFileExtension(item.filename) }}
           </div>
        </div>

        <!-- Encrypted Lock -->
        <div v-if="item.is_encrypted" class="absolute top-2 right-2 bg-black/50 backdrop-blur-sm p-1 rounded-full text-green-400 border border-white/10">
          <LockClosedIcon class="w-3 h-3" />
        </div>

      </div>
    </div>

    <!-- FLOATING ACTION BAR (Only when selection > 0) -->
    <Transition name="slide-up">
      <div v-if="isSelectionMode" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-40 glass-panel rounded-2xl px-6 py-3 flex items-center gap-6 shadow-2xl border border-white/10">
        
        <div class="flex items-center gap-3 border-r border-white/10 pr-6">
          <div class="bg-hub-accent text-white font-bold rounded-lg px-2 py-0.5 text-sm">
            {{ selectedIds.size }}
          </div>
          <span class="text-sm text-gray-300">выбрано</span>
          <button @click="clearSelection" class="p-1 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <div class="flex items-center gap-2">
          <!-- Actions -->
          <button @click="handleMenuAction('encrypt')" class="action-btn text-blue-400 hover:bg-blue-500/10">
            <LockClosedIcon class="w-5 h-5" />
            <span class="hidden sm:inline text-sm font-medium">В сейф</span>
          </button>

          <button @click="handleMenuAction('add-to-album')" class="action-btn text-gray-300 hover:bg-white/10">
            <FolderPlusIcon class="w-5 h-5" />
            <span class="hidden sm:inline text-sm font-medium">В альбом</span>
          </button>

          <div class="w-px h-6 bg-white/10 mx-2"></div>

          <button @click="handleMenuAction('delete')" class="action-btn text-red-400 hover:bg-red-500/10">
            <TrashIcon class="w-5 h-5" />
            <span class="hidden sm:inline text-sm font-medium">Удалить</span>
          </button>
        </div>
      </div>
    </Transition>

    <!-- GLOBAL COMPONENTS (Teleported) -->
    <Teleport to="body">
      <ContextMenu 
        :visible="menuVisible" 
        :x="menuX" 
        :y="menuY" 
        :item="activeItem" 
        :selectedCount="selectedIds.size" 
        @close="menuVisible = false" 
        @action="handleMenuAction" 
      />
      <ConfirmDialog 
        :isOpen="showConfirm" 
        title="Подтверждение действия" 
        :message="dialogMessage()" 
        :isDestructive="confirmAction === 'delete'" 
        @confirm="executeConfirm" 
        @cancel="showConfirm = false" 
      />
      <AlbumSelectorModal 
        :isOpen="showAlbumSelector" 
        :mediaItem="activeItem" 
        @close="showAlbumSelector = false" 
        @select="handleAlbumSelect" 
      />
    </Teleport>
  </div>
</template>

<style scoped>
.glass-badge {
  @apply bg-white/10 backdrop-blur-md border border-white/10 shadow-sm;
}
.action-btn {
  @apply flex items-center gap-2 px-3 py-2 rounded-xl transition-all active:scale-95;
}
.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translate(-50%, 150%);
  opacity: 0;
}
</style>