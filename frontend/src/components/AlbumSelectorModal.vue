<script setup>
import { ref, watch } from 'vue'
import { FolderIcon, PlusIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'select'])

const albums = ref([])
const loading = ref(false)

const loadAlbums = async () => {
  loading.value = true
  try {
    const res = await api.getAlbums()
    albums.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadAlbums()
  }
})

const selectAlbum = (id) => {
  emit('select', id)
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

    <div class="relative w-full max-w-md bg-[#1e293b] rounded-[2rem] border border-white/10 shadow-2xl overflow-hidden flex flex-col max-h-[80vh] animate-scale-in">
      
      <div class="p-6 border-b border-white/5 flex items-center justify-between shrink-0 bg-white/5">
        <h3 class="text-xl font-bold text-white">Добавить в альбом</h3>
        <button @click="$emit('close')" class="p-2 rounded-xl hover:bg-white/10 text-white/50 hover:text-white transition-colors">
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>

      <div class="overflow-y-auto p-4 custom-scrollbar">
        <div v-if="loading" class="flex justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
        </div>

        <div v-else-if="albums.length === 0" class="text-center py-8 text-white/40">
          <FolderIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>Нет альбомов</p>
        </div>

        <div v-else class="grid gap-2">
          <button 
            v-for="album in albums" 
            :key="album.id"
            @click="selectAlbum(album.id)"
            class="flex items-center gap-4 p-4 rounded-2xl hover:bg-white/5 border border-transparent hover:border-white/5 transition-all group text-left"
          >
            <div class="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-colors">
              <FolderIcon class="w-6 h-6" />
            </div>
            <div class="flex-1 min-w-0">
              <h4 class="text-white font-bold truncate">{{ album.name }}</h4>
              <p class="text-white/40 text-xs truncate">{{ album.media_count || 0 }} файлов</p>
            </div>
            <PlusIcon class="w-5 h-5 text-white/30 group-hover:text-white transition-colors" />
          </button>
        </div>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
</style>