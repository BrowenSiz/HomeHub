<script setup>
import { computed } from 'vue'
import { 
  PhotoIcon, LockClosedIcon, LockOpenIcon, 
  FolderIcon, Cog6ToothIcon
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({ currentView: String })
const emit = defineEmits(['change-view'])
const authStore = useAuthStore()

const menuItems = [
  { id: 'library', label: 'Библиотека', icon: PhotoIcon },
  { id: 'albums', label: 'Альбомы', icon: FolderIcon },
]

const vaultIcon = computed(() => authStore.isVaultUnlocked ? LockOpenIcon : LockClosedIcon)
</script>

<template>
  <!-- Просто стеклянная панель с меню, без лого -->
  <aside class="glass-panel rounded-3xl flex flex-col p-4 gap-2 overflow-hidden relative">
    
    <p class="px-4 py-2 text-[10px] font-bold text-white/30 uppercase tracking-widest">Навигация</p>
    
    <button 
      v-for="item in menuItems" 
      :key="item.id"
      @click="emit('change-view', item.id)"
      class="nav-item"
      :class="{ 'glass-button-active': currentView === item.id || (item.id === 'library' && currentView === 'library') }"
    >
      <component :is="item.icon" class="w-6 h-6" :class="currentView === item.id ? 'text-hub-accent' : 'text-gray-400'" />
      <span :class="currentView === item.id ? 'text-white font-bold' : 'text-gray-300'">{{ item.label }}</span>
    </button>

    <div class="h-px bg-white/5 my-4 mx-2"></div>

    <p class="px-4 py-2 text-[10px] font-bold text-white/30 uppercase tracking-widest">Приватность</p>

    <button 
      @click="emit('change-view', 'vault')"
      class="nav-item group"
      :class="{ 'active-vault': currentView === 'vault' }"
    >
      <component :is="vaultIcon" class="w-6 h-6 transition-transform group-hover:scale-110" :class="currentView === 'vault' ? 'text-red-400' : 'text-gray-400'" />
      <span :class="currentView === 'vault' ? 'text-white font-bold' : 'text-gray-300'">Сейф</span>
      <div v-if="authStore.isVaultUnlocked" class="ml-auto w-2 h-2 rounded-full bg-green-400 shadow-[0_0_10px_#4ade80]"></div>
    </button>

    <div class="mt-auto"></div>
    
    <button 
      @click="emit('change-view', 'settings')"
      class="nav-item text-white/40 hover:text-white"
    >
      <Cog6ToothIcon class="w-6 h-6" />
      <span>Настройки</span>
    </button>
  </aside>
</template>

<style scoped>
.nav-item {
  @apply w-full flex items-center gap-4 px-5 py-3.5 rounded-2xl text-sm font-medium transition-all duration-200 border border-transparent hover:bg-white/5 hover:border-white/5;
}
.active-vault {
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%);
  border: 1px solid rgba(239, 68, 68, 0.2);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.1);
}
</style>