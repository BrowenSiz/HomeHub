<script setup>
import { ref, computed } from 'vue'
import { useElementSize, useScroll } from '@vueuse/core'
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

const containerRef = ref(null)
const { width: containerWidth, height: containerHeight } = useElementSize(containerRef)
const { y: scrollTop } = useScroll(containerRef)

const GAP = 16
const PADDING_TOP = 40
const PADDING_X = 48 

const rows = computed(() => {
  const result = []
  const cols = 10 - props.columns
  for (let i = 0; i < props.items.length; i += cols) {
    result.push(props.items.slice(i, i + cols))
  }
  return result
})

const rowHeight = computed(() => {
  if (!containerWidth.value) return 200
  const contentWidth = containerWidth.value - (PADDING_X * 2) 
  const cols = 10 - props.columns
  return (contentWidth - (GAP * (cols - 1))) / cols
})

const visibleRowsRange = computed(() => {
  const itemHeight = rowHeight.value + GAP
  const buffer = 4
  const scrollY = Math.max(0, scrollTop.value - PADDING_TOP)
  const startIndex = Math.floor(scrollY / itemHeight)
  const visibleCount = Math.ceil(containerHeight.value / itemHeight)
  
  const start = Math.max(0, startIndex - buffer)
  const end = Math.min(rows.value.length, startIndex + visibleCount + buffer)
  
  return { start, end }
})

const visibleRows = computed(() => {
  const { start, end } = visibleRowsRange.value
  return rows.value.slice(start, end).map((items, index) => ({
    items,
    rowIndex: start + index
  }))
})

const spacerStyle = computed(() => {
  const { start, end } = visibleRowsRange.value
  const itemHeight = rowHeight.value + GAP
  const paddingTop = start * itemHeight
  const paddingBottom = (rows.value.length - end) * itemHeight
  
  return {
    paddingTop: `${paddingTop}px`,
    paddingBottom: `${paddingBottom}px`
  }
})

const rowGridStyle = computed(() => {
  const cols = 10 - props.columns
  return {
    display: 'grid',
    gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
    gap: `${GAP}px`,
    marginBottom: `${GAP}px`
  }
})

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
    notify.show(`Перемещено в сейф: ${ids.length}`, 'success')
    emit('refresh')
    exitSelectionMode()
  } catch (e) {
    if (e.response && e.response.status === 403) {
      notify.show('Доступ запрещен. Сейф заблокирован.', 'error')
    } else {
      notify.show('Ошибка перемещения в сейф', 'error')
    }
  }
}

const handleUnlock = async (ids) => {
  try {
    await api.decryptMedia(ids)
    notify.show(`Восстановлено: ${ids.length}`, 'success')
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
</script>

<template>
  <div 
    ref="containerRef" 
    class="h-full w-full overflow-y-auto px-12 py-8 scroll-smooth custom-scrollbar relative pb-40"
  >
    <div v-if="items.length === 0" class="flex flex-col items-center justify-center h-64 text-white/30">
      <p>Нет медиафайлов</p>
    </div>

    <div v-else :style="spacerStyle">
      <div 
        v-for="row in visibleRows" 
        :key="row.rowIndex" 
        :style="rowGridStyle"
      >
        <div 
          v-for="item in row.items" 
          :key="item.id"
          class="group aspect-square relative bg-white/5 rounded-2xl overflow-hidden cursor-pointer transition-all duration-200 border border-transparent hover:border-white/20 hover:shadow-2xl hover:scale-[1.02]"
          :class="selectedItems.has(item.id) ? 'ring-4 ring-blue-500/50 scale-95' : ''"
          @click="handleClick(item)"
          @contextmenu="handleContextMenu($event, item)"
        >
          <img 
            :src="getThumbnailUrl(item)" 
            class="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity"
            loading="lazy"
            @error="$event.target.src = '/assets/placeholder.png'"
          />
          
          <div class="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

          <div v-if="isSelectionMode" class="absolute top-3 right-3 z-30">
            <div 
              class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors bg-black/40 backdrop-blur-md"
              :class="selectedItems.has(item.id) ? 'bg-blue-500 border-blue-500' : 'border-white/50'"
            >
              <CheckCircleIcon v-if="selectedItems.has(item.id)" class="w-4 h-4 text-white" />
            </div>
          </div>

          <template v-else>
            <div class="absolute top-3 left-3 flex flex-col gap-1.5 items-start max-w-[70%] z-20">
              <div v-if="item.is_encrypted" class="w-7 h-7 bg-red-500/80 backdrop-blur-md rounded-xl flex items-center justify-center shadow-lg border border-white/10">
                <LockClosedIcon class="w-4 h-4 text-white" />
              </div>
              <div v-if="item.album" class="flex items-center gap-1.5 px-2.5 py-1 bg-blue-600/80 backdrop-blur-md rounded-lg border border-white/10 shadow-lg">
                <FolderIcon class="w-3 h-3 text-white/90" />
                <span class="text-[10px] font-bold text-white truncate max-w-[80px]">{{ item.album.name }}</span>
              </div>
            </div>
            
            <div class="absolute top-3 right-3 flex flex-col gap-1.5 items-end z-20">
              <div v-if="item.media_type.startsWith('video')" class="w-8 h-8 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/20 shadow-lg">
                <PlayIcon class="w-4 h-4 text-white fill-current" />
              </div>
              <div class="px-2 py-0.5 bg-black/40 backdrop-blur-md rounded-md text-[9px] font-bold text-white/70 uppercase tracking-wider border border-white/5">
                {{ getFileExtension(item.filename) }}
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="isSelectionMode" class="fixed bottom-10 left-1/2 -translate-x-1/2 z-[9999] flex flex-col items-center animate-slide-up">
      <div class="bg-[#1e293b]/90 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl p-2 px-6 flex items-center gap-4">
        
        <div class="text-white font-bold text-sm border-r border-white/10 pr-4 mr-1">
          <span class="text-blue-400 text-lg">{{ selectedItems.size }}</span> <span class="text-white/50 text-xs uppercase tracking-widest">Selected</span>
        </div>

        <button @click="handleBulkLock" class="action-btn text-white hover:bg-white/10 group" title="В сейф">
          <LockClosedIcon class="w-5 h-5 text-red-400 group-hover:scale-110 transition-transform" />
        </button>

        <button @click="handleBulkAlbum" class="action-btn text-white hover:bg-white/10 group" title="В альбом">
          <FolderIcon class="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform" />
        </button>

        <button @click="handleBulkDelete" class="action-btn text-white hover:bg-white/10 group" title="Удалить">
          <TrashIcon class="w-5 h-5 text-white/70 group-hover:text-red-500 group-hover:scale-110 transition-transform" />
        </button>

        <div class="w-px h-6 bg-white/10 mx-1"></div>

        <button @click="exitSelectionMode" class="p-3 rounded-full hover:bg-white/10 text-white transition-colors" title="Отмена">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
    
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
  @apply p-3 rounded-full transition-all active:scale-95 flex items-center justify-center;
}

.animate-slide-up {
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { transform: translate(-50%, 100%); opacity: 0; }
  to { transform: translate(-50%, 0); opacity: 1; }
}
</style>