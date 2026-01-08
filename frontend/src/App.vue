<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { PlusIcon, ArrowPathIcon } from '@heroicons/vue/24/solid'

import Header from '@/components/Header.vue'
import Sidebar from '@/components/Sidebar.vue'
import MediaGrid from '@/components/MediaGrid.vue'
import AlbumList from '@/components/AlbumList.vue'
import CreateAlbumModal from '@/components/CreateAlbumModal.vue'
import SetupWizard from '@/components/SetupWizard.vue'
import PinPad from '@/components/PinPad.vue'
import ToastContainer from '@/components/ToastContainer.vue'
import MediaViewer from '@/components/MediaViewer.vue'
import Settings from '@/components/Settings.vue'
import SystemStats from '@/components/SystemStats.vue'

const authStore = useAuthStore()
const notify = useNotificationStore()

const status = ref('Запуск...')
const apiInfo = ref(null)
const isSetupComplete = ref(false)
const checkingAuth = ref(true)
const currentView = ref('library') 
const activeAlbum = ref(null)

const mediaItems = ref([])
const albums = ref([])
const isLoading = ref(false)
const pinError = ref('')
const pinLoading = ref(false)
const isCreateAlbumOpen = ref(false)
const isUploading = ref(false)

const viewerOpen = ref(false)
const currentMediaIndex = ref(0)
const activeItem = computed(() => mediaItems.value[currentMediaIndex.value] || null)
const nextItem = computed(() => mediaItems.value[currentMediaIndex.value + 1] || null)
const prevItem = computed(() => mediaItems.value[currentMediaIndex.value - 1] || null)

const fileInputRef = ref(null)
let heartbeatInterval = null

const pageTitle = computed(() => {
  switch (currentView.value) {
    case 'library': return 'Библиотека'
    case 'albums': return 'Альбомы'
    case 'album_detail': return activeAlbum.value?.name || 'Альбом'
    case 'vault': return 'Личный сейф'
    case 'system': return 'Хранилище'
    case 'settings': return 'Настройки'
    default: return 'HomeHub'
  }
})

const pageSubtitle = computed(() => {
  switch (currentView.value) {
    case 'library': return `Все медиафайлы • ${mediaItems.value.length} объектов`
    case 'albums': return 'Ваши коллекции'
    case 'album_detail': return activeAlbum.value?.description || 'Просмотр содержимого'
    case 'vault': return authStore.isVaultUnlocked ? 'Зашифрованное хранилище' : 'Доступ ограничен'
    case 'system': return 'Статистика и ресурсы'
    case 'settings': return 'Безопасность и обновления'
    default: return ''
  }
})

const startHeartbeat = () => {
  if (heartbeatInterval) clearInterval(heartbeatInterval)
  heartbeatInterval = setInterval(() => {
    api.sendHeartbeat().catch(() => {
      status.value = 'Офлайн'
    })
  }, 3000)
}

const initSystem = async (retryCount = 0) => {
  checkingAuth.value = true
  try {
    const health = await api.checkHealth()
    apiInfo.value = health.data
    status.value = 'Онлайн'
    
    const authStatus = await api.getAuthStatus()
    isSetupComplete.value = authStatus.data.is_setup
    
    startHeartbeat()

    if (isSetupComplete.value) await loadData()
    checkingAuth.value = false
    
  } catch (error) {
    if (retryCount < 20) {
      setTimeout(() => initSystem(retryCount + 1), 500)
    } else {
      status.value = 'Офлайн'
      checkingAuth.value = false
    }
  }
}

const loadData = async () => {
  if (currentView.value === 'settings' || currentView.value === 'system') return

  isLoading.value = true
  mediaItems.value = [] 
  try {
    if (currentView.value === 'library') {
      const response = await api.getMedia()
      mediaItems.value = response.data
    } else if (currentView.value === 'albums') {
      const response = await api.getAlbums()
      albums.value = response.data
    } else if (currentView.value === 'album_detail' && activeAlbum.value) {
      const response = await api.getAlbumDetails(activeAlbum.value.id)
      mediaItems.value = response.data.media_items
    } else if (currentView.value === 'vault' && authStore.isVaultUnlocked) {
      const response = await api.getVaultMedia()
      mediaItems.value = response.data
    }
  } catch (e) { console.error(e) } finally { isLoading.value = false }
}

const changeView = (viewId) => {
  currentView.value = viewId
  activeAlbum.value = null
  if (viewId === 'vault' && !authStore.isVaultUnlocked) {
    mediaItems.value = []
  } else {
    loadData()
  }
}

const openAlbum = (album) => { activeAlbum.value = album; currentView.value = 'album_detail'; loadData() }
const handleCreateAlbum = async (data) => { await api.createAlbum(data); loadData() }
const handleDeleteAlbum = async (id) => { await api.deleteAlbum(id); loadData() }

const onSetupFinished = async () => { isSetupComplete.value = true; await loadData() }
const openViewer = (item) => {
  const index = mediaItems.value.findIndex(i => i.id === item.id)
  if (index !== -1) { currentMediaIndex.value = index; viewerOpen.value = true }
}
const nextMedia = () => { if (currentMediaIndex.value < mediaItems.value.length - 1) currentMediaIndex.value++ }
const prevMedia = () => { if (currentMediaIndex.value > 0) currentMediaIndex.value-- }

const handleAddPhoto = () => { if (fileInputRef.value) fileInputRef.value.click() }
const onFileChange = async (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  isUploading.value = true
  const formData = new FormData()
  for (let i = 0; i < files.length; i++) { formData.append('files', files[i]) }
  try {
    const res = await api.uploadFiles(formData)
    notify.show(`Загружено файлов: ${res.data.count}`, 'success')
    event.target.value = '' 
    await loadData()
  } catch (e) { notify.show('Ошибка загрузки', 'error') } 
  finally { isUploading.value = false }
}

const handlePinSubmit = async (pin) => {
  pinLoading.value = true
  pinError.value = ''
  if (await authStore.unlockVault(pin)) { 
    await loadData() 
  } else { 
    pinError.value = 'Неверный PIN код' 
  }
  pinLoading.value = false
}

onMounted(() => initSystem())
onUnmounted(() => {
  if (heartbeatInterval) clearInterval(heartbeatInterval)
})
</script>

<template>
  <div class="h-screen w-full flex p-5 gap-5 overflow-hidden relative selection:bg-blue-500 selection:text-white font-sans bg-[#0f172a]">
    
    <!-- Фоновые пятна -->
    <div class="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none"></div>

    <ToastContainer />
    <input type="file" ref="fileInputRef" class="hidden" multiple accept="image/*,video/*,.cr2,.nef,.dng" @change="onFileChange" />
    
    <CreateAlbumModal :isOpen="isCreateAlbumOpen" @close="isCreateAlbumOpen = false" @create="handleCreateAlbum" />
    <MediaViewer :isOpen="viewerOpen" :item="activeItem" :nextItem="nextItem" :prevItem="prevItem" :hasNext="currentMediaIndex < mediaItems.length - 1" :hasPrev="currentMediaIndex > 0" @close="viewerOpen = false" @next="nextMedia" @prev="prevMedia" />
    
    <!-- LOADING -->
    <div v-if="checkingAuth" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0f172a] text-white gap-6">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-blue-500/20 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
        </div>
        <div class="text-white/40 text-sm uppercase tracking-[0.2em] animate-pulse">Запуск системы</div>
    </div>

    <!-- ERROR -->
    <div v-else-if="status === 'Офлайн'" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 text-white gap-6">
       <div class="text-3xl font-bold text-red-500">Система недоступна</div>
       <p class="text-white/50">Сервер не отвечает на запросы</p>
       <button @click="initSystem(0)" class="px-8 py-3 bg-white/10 hover:bg-white/20 border border-white/10 rounded-xl transition-all">Повторить попытку</button>
    </div>

    <!-- WIZARD -->
    <SetupWizard v-else-if="!isSetupComplete" @setup-complete="onSetupFinished" />

    <!-- MAIN UI -->
    <template v-else>
      <div class="w-72 flex flex-col gap-5 shrink-0 z-10">
        <div class="h-20 glass-panel rounded-[2rem] flex items-center px-6 gap-5 relative overflow-hidden group">
           <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
           
           <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 border border-white/20 z-10">
            <span class="text-white font-black text-xl">H</span>
          </div>
          <div class="z-10">
            <h1 class="font-bold text-xl tracking-tight text-white leading-none">HomeHub</h1>
            <span class="text-[10px] uppercase font-bold text-white/30 tracking-[0.2em] mt-0.5 block">
              v{{ apiInfo?.version || '...' }}
            </span>
          </div>
        </div>
        <!-- Меню -->
        <Sidebar :currentView="currentView" @change-view="changeView" class="flex-1" />
      </div>

      <div class="flex-1 flex flex-col gap-5 min-w-0 h-full z-10">
        <Header 
          :status="status" 
          :apiInfo="apiInfo"
          :title="pageTitle"
          :subtitle="pageSubtitle"
          :showBack="currentView === 'album_detail'"
          :showLock="currentView === 'vault' && authStore.isVaultUnlocked"
          @back="changeView('albums')"
          @lock="authStore.lockVault()"
        />
        
        <main class="flex-1 glass-panel rounded-[2rem] overflow-hidden relative flex flex-col">
          
          <div class="flex-1 overflow-y-auto px-8 py-8 scroll-smooth custom-scrollbar relative">
            <div v-if="currentView === 'library' || currentView === 'album_detail'">
              <div v-if="isLoading" class="loader"></div>
              <MediaGrid v-else :items="mediaItems" @refresh="loadData" @open-viewer="openViewer" />
            </div>
            
            <div v-else-if="currentView === 'albums'">
              <div v-if="isLoading" class="loader"></div>
              <AlbumList v-else :albums="albums" @open-album="openAlbum" @create-album="isCreateAlbumOpen = true" @delete-album="handleDeleteAlbum" />
            </div>
            
            <div v-else-if="currentView === 'vault'" class="h-full">
              <PinPad v-if="!authStore.isVaultUnlocked" :error="pinError" :loading="pinLoading" @submit="handlePinSubmit" />
              <div v-else class="flex flex-col h-full">
                <div v-if="isLoading" class="loader border-red-500"></div>
                <div v-else-if="mediaItems.length > 0" class="flex-1"><MediaGrid :items="mediaItems" @refresh="loadData" @open-viewer="openViewer" /></div>
                <div v-else class="empty-state"><div class="text-6xl mb-6 opacity-20 blur-sm">🔒</div><p class="text-2xl font-bold text-white/40">Сейф пуст</p></div>
              </div>
            </div>
            
            <div v-else-if="currentView === 'system'" class="h-full">
              <SystemStats />
            </div>

            <div v-else-if="currentView === 'settings'" class="h-full">
              <Settings />
            </div>
          </div>
          
          <div v-if="currentView !== 'vault' && currentView !== 'settings' && currentView !== 'system'" class="absolute bottom-10 right-10 z-20">
             <button 
                @click="handleAddPhoto" 
                :disabled="isUploading" 
                class="h-16 w-16 rounded-[1.5rem] bg-gradient-to-br from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-2xl shadow-blue-600/40 flex items-center justify-center text-white transition-all hover:scale-110 active:scale-95 group border border-white/20 disabled:opacity-70 disabled:grayscale"
              >
               <ArrowPathIcon v-if="isUploading" class="w-8 h-8 animate-spin" />
               <PlusIcon v-else class="w-8 h-8 group-hover:rotate-90 transition-transform duration-300" />
             </button>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped>
.loader { @apply flex justify-center py-20 animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white mx-auto opacity-50; }
.empty-state { @apply flex flex-col items-center justify-center h-full text-center p-10 opacity-60; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>