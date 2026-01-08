<script setup>
import { ref } from 'vue'
import { FolderIcon, PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  albums: Array
})

const emit = defineEmits(['open-album', 'create-album', 'delete-album'])

const handleDelete = (id, name) => {
  if (confirm(`Удалить альбом "${name}"? Фотографии останутся в библиотеке.`)) {
    emit('delete-album', id)
  }
}
</script>

<template>
  <div>
    <!-- Кнопка создания -->
    <button 
      @click="$emit('create-album')"
      class="mb-6 flex items-center gap-2 px-4 py-2 bg-hub-panel hover:bg-gray-700 rounded-lg text-sm text-white transition-colors border border-gray-700"
    >
      <PlusIcon class="w-5 h-5 text-hub-accent" />
      Создать альбом
    </button>

    <!-- Сетка альбомов -->
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
      <div 
        v-for="album in albums" 
        :key="album.id"
        class="group cursor-pointer"
        @click="$emit('open-album', album)"
      >
        <!-- Обложка -->
        <div class="aspect-square bg-gray-800 rounded-2xl border border-gray-700 relative overflow-hidden shadow-lg group-hover:border-hub-accent transition-colors">
          <img 
            v-if="album.cover_photo" 
            :src="`/thumbnails/${album.cover_photo}`" 
            class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
          />
          <div v-else class="w-full h-full flex items-center justify-center bg-gray-800">
            <FolderIcon class="w-16 h-16 text-gray-600 group-hover:text-hub-accent transition-colors" />
          </div>
          
          <!-- Удаление -->
          <button 
            @click.stop="handleDelete(album.id, album.name)"
            class="absolute top-2 right-2 p-1.5 bg-black/60 rounded-full text-red-400 opacity-0 group-hover:opacity-100 hover:bg-red-500 hover:text-white transition-all"
            title="Удалить альбом"
          >
            <TrashIcon class="w-4 h-4" />
          </button>
        </div>

        <!-- Информация -->
        <div class="mt-3">
          <h3 class="text-white font-medium truncate pr-2 group-hover:text-hub-accent transition-colors">{{ album.name }}</h3>
          <p class="text-xs text-gray-500">{{ album.media_count }} объектов</p>
        </div>
      </div>
    </div>
  </div>
</template>