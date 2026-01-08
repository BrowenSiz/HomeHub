<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth' 
import { 
  HomeIcon, 
  FolderIcon, 
  LockClosedIcon, 
  LockOpenIcon,
  Cog6ToothIcon,
  ServerIcon
} from '@heroicons/vue/24/outline'

import { 
  HomeIcon as HomeSolid, 
  FolderIcon as FolderSolid, 
  LockClosedIcon as LockSolid, 
  LockOpenIcon as LockOpenSolid,
  Cog6ToothIcon as CogSolid,
  ServerIcon as ServerSolid
} from '@heroicons/vue/24/solid'

defineProps({
  currentView: String
})

defineEmits(['change-view'])

const authStore = useAuthStore()

const menuItems = computed(() => [
  { id: 'library', label: 'Библиотека', icon: HomeIcon, activeIcon: HomeSolid },
  { id: 'albums', label: 'Альбомы', icon: FolderIcon, activeIcon: FolderSolid },
  { 
    id: 'vault', 
    label: 'Сейф', 
    icon: authStore.isVaultUnlocked ? LockOpenIcon : LockClosedIcon, 
    activeIcon: authStore.isVaultUnlocked ? LockOpenSolid : LockSolid,
    isVault: true 
  },
  { id: 'system', label: 'Хранилище', icon: ServerIcon, activeIcon: ServerSolid },
])
</script>

<template>
  <div class="flex flex-col h-full glass-panel rounded-[2rem] p-4 relative overflow-hidden">
    <div class="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>

    <nav class="flex-1 space-y-2 mt-2 z-10">
      <button 
        v-for="item in menuItems" 
        :key="item.id"
        @click="$emit('change-view', item.id)"
        class="w-full flex items-center gap-4 px-4 py-4 rounded-2xl transition-all duration-300 group relative"
        :class="currentView === item.id ? 'text-white shadow-lg shadow-black/20' : 'text-white/60 hover:text-white hover:bg-white/5'"
      >
        <div 
          v-if="currentView === item.id" 
          class="absolute inset-0 bg-gradient-to-r from-blue-600/80 to-indigo-600/80 backdrop-blur-md border border-white/10 rounded-2xl"
        ></div>

        <component :is="currentView === item.id ? item.activeIcon : item.icon" class="w-6 h-6 z-10 relative transition-transform duration-300 group-hover:scale-110" />
        <span class="font-bold text-sm z-10 relative tracking-wide">{{ item.label }}</span>
        
        <div 
          v-if="item.isVault && authStore.isVaultUnlocked" 
          class="absolute right-4 w-2 h-2 bg-green-400 rounded-full shadow-[0_0_10px_rgba(74,222,128,0.6)] animate-pulse z-20"
        ></div>
      </button>
    </nav>

    <div class="pt-4 mt-2 border-t border-white/5 z-10">
      <button 
        @click="$emit('change-view', 'settings')"
        class="w-full flex items-center gap-4 px-4 py-4 rounded-2xl transition-all duration-300 text-white/60 hover:text-white hover:bg-white/5 relative group overflow-hidden"
        :class="currentView === 'settings' ? 'text-white bg-white/10 border border-white/5' : ''"
      >
        <component :is="currentView === 'settings' ? CogSolid : Cog6ToothIcon" class="w-6 h-6 z-10 group-hover:rotate-90 transition-transform duration-500" />
        <span class="font-bold text-sm z-10">Настройки</span>
      </button>
    </div>
  </div>
</template>