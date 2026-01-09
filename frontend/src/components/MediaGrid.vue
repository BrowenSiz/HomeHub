<script setup>
import { ref, computed } from 'vue'
import { PlayIcon, LockClosedIcon, FolderIcon, CheckCircleIcon, XMarkIcon, TrashIcon } from '@heroicons/vue/24/solid'
import ContextMenu from './ContextMenu.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import AlbumSelectorModal from './AlbumSelectorModal.vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  items: { type: Array, required: true },
  columns: { type: Number, default: 5 }
})

const emit = defineEmits(['refresh', 'open-viewer'])
const notify = useNotificationStore()
const authStore = useAuthStore()

const contextMenu = ref({ isOpen: false, x: 0, y: 0, item: null })
const deleteDialog = ref({ isOpen: false, item: null, isBulk: false })
const albumDialog = ref({ isOpen: false, item: null, isBulk: false })

const isSelectionMode = ref(false)
const selectedItems = ref(new Set())

const getThumbnailUrl = (item) => {
  if (item.is_encrypted) return `/api/media/${item.id}/thumbnail`
  return item.thumbnail_path 
    ? `/thumbnails/${item.thumbnail_path}`
    : `/api/media/${item.id}/thumbnail`
}

const getFileExtension = (filename) => {
  if (!filename) return ''
  return filename.split('.').pop().toUpperCase()
}

const toggleSelection = (item) => {
  if (selectedItems.value.has(item.id)) {
    selectedItems.value.delete(item.id)
    if (selectedItems.value.size === 0) isSelectionMode.value = false
  } else {
    selectedItems.value.add(item.id)
  }
}

const exitSelectionMode = () => {
  isSelectionMode.value = false
  selectedItems.value.clear()
}

const handleClick = (item) => {
  if (isSelectionMode.value) {
    toggleSelection(item)
  } else {
    emit('open-viewer', item)
  }
}

const handleContextMenu = (e, item) => {
  if (isSelectionMode.value) return
  
  e.preventDefault()
  e.stopPropagation()
  
  let x = e.clientX
  let y = e.clientY
  
  if (x > window.innerWidth - 220) x = window.innerWidth - 220
  if (y > window.innerHeight - 300) y = window.innerHeight - 300

  contextMenu.value = { isOpen: true, x, y, item }
}

const handleAction = (action) => {
  const item = contextMenu.value.item
  contextMenu.value.isOpen = false
  
  if (!item && action !== 'select' && action !== 'bulk') return

  switch (action) {
    case 'select':
      isSelectionMode.value = true
      selectedItems.value.add(item.id)
      break
    case 'lock':
      handleLock([item.id])
      break
    case 'unlock':
      handleUnlock([item.id])
      break
    case 'album':
      albumDialog.value = { isOpen: true, item: item, isBulk: false }
      break
    case 'delete':
      deleteDialog.value = { isOpen: true, item: item, isBulk: false }
      break
  }
}

const handleBulkLock = () => handleLock(Array.from(selectedItems.value))
const handleBulkUnlock = () => handleUnlock(Array.from(selectedItems.value))
const handleBulkDelete = () => {
  deleteDialog.value = { isOpen: true, item: null, isBulk: true }
}
const handleBulkAlbum = () => {
  albumDialog.value = { isOpen: true, item: null, isBulk: true }
}

const handleLock = async (ids) => {
  if (!authStore.isVaultUnlocked) {
    notify.show('Сейф закрыт! Введите PIN код.', 'error')
    return
  }

  try {
    await api.encryptMedia(ids)
    notify.show(`Файлов перемещено: ${ids.length}`, 'success')
    emit('refresh')
    exitSelectionMode()
  } catch (e) {
    notify.show('Ошибка доступа к сейфу', 'error')
  }
}

const handleUnlock = async (ids) => {
  try {
    await api.decryptMedia(ids)
    notify.show(`Файлов восстановлено: ${ids.length}`, 'success')
    emit('refresh')
    exitSelectionMode()
  } catch (e) {
    notify.show('Ошибка восстановления', 'error')
  }
}

const confirmDelete = async () => {
  let ids = []
  if (deleteDialog.value.isBulk) {
    ids = Array.from(selectedItems.value)
  } else if (deleteDialog.value.item) {
    ids = [deleteDialog.value.item.id]
  }

  if (ids.length === 0) {
    deleteDialog.value.isOpen = false
    return
  }
  
  try {
    await api.deleteMedia(ids)
    notify.show('Файлы удалены', 'success')
    emit('refresh')
    exitSelectionMode()
  } catch (e) {
    notify.show('Ошибка удаления', 'error')
  } finally {
    deleteDialog.value.isOpen = false
  }
}

const handleAddToAlbum = async (albumId) => {
  let ids = []
  if (albumDialog.value.isBulk) {
    ids = Array.from(selectedItems.value)
  } else if (albumDialog.value.item) {
    ids = [albumDialog.value.item.id]
  }

  if (ids.length === 0) {
    albumDialog.value.isOpen = false
    return
  }

  try {
    await api.setAlbum(ids, albumId)
    notify.show('Альбом изменен', 'success')
    emit('refresh')
    exitSelectionMode()
  } catch (e) {
    notify.show('Ошибка перемещения', 'error')
  } finally {
    albumDialog.value.isOpen = false
  }
}

const gridStyle = computed(() => {
  const cols = (10 - props.columns) 
  return {
    gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`
  }
})
</script>

<template>
  <div v-if="items.length === 0" class="flex flex-col items-center justify-center h-64 text-white/30">
    <p>Нет медиафайлов</p>
  </div>

  <div 
    v-else 
    class="grid gap-4 transition-all duration-500 ease-in-out w-full pb-32"
    :style="gridStyle"
  >
    <div 
      v-for="item in items" 
      :key="item.id"
      class="group aspect-square relative bg-white/5 rounded-2xl overflow-hidden cursor-pointer border hover:border-white/20 transition-all duration-200"
      :class="selectedItems.has(item.id) ? 'border-blue-500 ring-2 ring-blue-500/50 scale-95' : 'hover:shadow-xl hover:scale-[1.02]'"
      @click="handleClick(item)"
      @contextmenu="handleContextMenu($event, item)"
    >
      <img 
        :src="getThumbnailUrl(item)" 
        class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-90 group-hover:opacity-100"
        loading="lazy"
        @error="$event.target.src = '/assets/placeholder.png'"
      />
      
      <div class="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity"></div>

      <div v-if="isSelectionMode" class="absolute top-3 right-3 z-30">
        <div 
          class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors bg-black/40 backdrop-blur-md"
          :class="selectedItems.has(item.id) ? 'bg-blue-500 border-blue-500' : 'border-white/50'"
        >
          <CheckCircleIcon v-if="selectedItems.has(item.id)" class="w-4 h-4 text-white" />
        </div>
      </div>

      <template v-else>
        <div class="absolute top-2 left-2 flex flex-col gap-1.5 items-start max-w-[70%] z-20">
          <div v-if="item.is_encrypted" class="w-6 h-6 bg-red-500/80 backdrop-blur-md rounded-lg flex items-center justify-center shadow-lg border border-white/10">
            <LockClosedIcon class="w-3.5 h-3.5 text-white" />
          </div>
          <div v-if="item.album" class="flex items-center gap-1 px-2 py-1 bg-blue-600/80 backdrop-blur-md rounded-lg border border-white/10 shadow-lg">
            <FolderIcon class="w-3 h-3 text-white/80" />
            <span class="text-[10px] font-bold text-white truncate max-w-[80px]">{{ item.album.name }}</span>
          </div>
        </div>

        <div class="absolute top-2 right-2 flex flex-col gap-1.5 items-end z-20">
          <div v-if="item.media_type.startsWith('video')" class="w-8 h-8 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/20 shadow-lg">
            <PlayIcon class="w-4 h-4 text-white fill-current" />
          </div>
          <div class="px-1.5 py-0.5 bg-black/40 backdrop-blur-md rounded text-[9px] font-bold text-white/70 uppercase tracking-wider border border-white/5">
            {{ getFileExtension(item.filename) }}
          </div>
        </div>
      </template>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="isSelectionMode" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[9999] flex flex-col items-center animate-slide-up">
      <div class="bg-[#1e293b]/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-2 px-4 flex items-center gap-4">
        
        <div class="text-white font-bold text-sm border-r border-white/10 pr-4 mr-2">
          {{ selectedItems.size }} выбрано
        </div>

        <button @click="handleBulkLock" class="action-btn text-white hover:bg-white/10 group" title="В сейф">
          <LockClosedIcon class="w-5 h-5 text-red-400 group-hover:scale-110 transition-transform" />
          <span class="text-sm font-medium">В сейф</span>
        </button>

        <button @click="handleBulkAlbum" class="action-btn text-white hover:bg-white/10 group" title="В альбом">
          <FolderIcon class="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform" />
          <span class="text-sm font-medium">В альбом</span>
        </button>

        <button @click="handleBulkDelete" class="action-btn text-white hover:bg-white/10 group" title="Удалить">
          <TrashIcon class="w-5 h-5 text-white/70 group-hover:text-red-500 group-hover:scale-110 transition-transform" />
          <span class="text-sm font-medium group-hover:text-red-400">Удалить</span>
        </button>

        <div class="w-px h-6 bg-white/10 mx-2"></div>

        <button @click="exitSelectionMode" class="p-2 hover:bg-white/10 rounded-xl text-white transition-colors">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
  </Teleport>

  <Teleport to="body">
    <ContextMenu 
      v-if="contextMenu.isOpen"
      :x="contextMenu.x" :y="contextMenu.y" :item="contextMenu.item"
      @close="contextMenu.isOpen = false"
      @action="handleAction"
    />

    <ConfirmDialog 
      :isOpen="deleteDialog.isOpen"
      :title="deleteDialog.isBulk ? `Удалить ${selectedItems.size} файлов?` : 'Удалить файл?'"
      message="Это действие нельзя отменить."
      @close="deleteDialog.isOpen = false"
      @confirm="confirmDelete"
    />

    <AlbumSelectorModal 
      :isOpen="albumDialog.isOpen"
      @close="albumDialog.isOpen = false"
      @select="handleAddToAlbum"
    />
  </Teleport>
</template>

<style scoped>
.action-btn {
  @apply flex items-center gap-2 px-3 py-2 rounded-xl transition-all active:scale-95;
}

.animate-slide-up {
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideUp {
  from { transform: translate(-50%, 100%); opacity: 0; }
  to { transform: translate(-50%, 0); opacity: 1; }
}
</style>