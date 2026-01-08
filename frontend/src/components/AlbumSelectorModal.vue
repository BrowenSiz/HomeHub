<script setup>
import { ref, watch } from 'vue'
import { XMarkIcon, FolderIcon, FolderPlusIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const props = defineProps({
  isOpen: Boolean,
  mediaItem: Object 
})
const emit = defineEmits(['close', 'select'])
const albums = ref([])
const isLoading = ref(false)

const loadAlbums = async () => {
  isLoading.value = true
  try {
    const response = await api.getAlbums()
    albums.value = response.data
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

watch(() => props.isOpen, (newVal) => { if (newVal) loadAlbums() })
const selectAlbum = (album) => { emit('select', album); emit('close'); }
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 animate-fade-in">
    <div class="bg-hub-panel w-full max-w-md rounded-xl border border-gray-700 shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
      <div class="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800/50">
        <div>
          <h3 class="text-lg font-bold text-white">Добавить в альбом</h3>
          <p class="text-xs text-gray-400 truncate max-w-[250px]">
            {{ mediaItem ? mediaItem.filename : 'Выбрано несколько' }}
          </p>
        </div>
        <button @click="$emit('close')" class="p-1 rounded-full hover:bg-gray-700 text-gray-400 hover:text-white transition-colors">
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div v-if="isLoading" class="py-10 text-center"><div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-hub-accent mx-auto"></div></div>
        <div v-else-if="albums.length === 0" class="py-10 text-center text-gray-500">
          <FolderPlusIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>Нет альбомов</p>
        </div>
        <button 
          v-else v-for="album in albums" :key="album.id" @click="selectAlbum(album)"
          class="w-full flex items-center gap-4 p-3 rounded-lg hover:bg-gray-700/50 transition-colors text-left group border border-transparent hover:border-gray-600"
        >
          <div class="w-12 h-12 bg-gray-800 rounded-md flex items-center justify-center overflow-hidden shrink-0 border border-gray-700">
            <img v-if="album.cover_photo" :src="`/thumbnails/${album.cover_photo}`" class="w-full h-full object-cover" />
            <FolderIcon v-else class="w-6 h-6 text-gray-500 group-hover:text-hub-accent" />
          </div>
          <div>
            <h4 class="text-white font-medium group-hover:text-hub-accent transition-colors">{{ album.name }}</h4>
            <p class="text-xs text-gray-400">{{ album.media_count }} фото</p>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.15s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>