<script setup>
import { ref } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({ isOpen: Boolean })
const emit = defineEmits(['close', 'create'])
const name = ref('')

const handleSubmit = () => {
  if (name.value.trim()) {
    emit('create', { name: name.value })
    name.value = ''
    emit('close')
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
    <div class="bg-hub-panel w-full max-w-sm p-6 rounded-xl border border-gray-700 shadow-2xl animate-pop">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold text-white">Новый альбом</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-white"><XMarkIcon class="w-6 h-6" /></button>
      </div>

      <input 
        v-model="name" 
        type="text" 
        placeholder="Название альбома" 
        class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-hub-accent focus:ring-1 focus:ring-hub-accent outline-none mb-6 transition-none"
        @keyup.enter="handleSubmit"
        autofocus
      />

      <div class="flex justify-end gap-2">
        <button @click="$emit('close')" class="px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-lg">Отмена</button>
        <button 
          @click="handleSubmit" 
          :disabled="!name.trim()"
          class="px-4 py-2 text-sm bg-hub-accent text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          Создать
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-pop { animation: pop 0.15s ease-out; }
@keyframes pop { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>