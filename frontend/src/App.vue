<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { PlusIcon, ArrowPathIcon } from '@heroicons/vue/24/solid'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'

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

const authStore = useAuthStore()
const notify = useNotificationStore()

const status = ref('Подключение...')
const apiInfo = ref(null)
const isSetupComplete = ref(true)
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

const initSystem = async () => {
  try {
    const health = await api.checkHealth()
    status.value = 'Онлайн'
    apiInfo.value = health.data
    const authStatus = await api.getAuthStatus()
    isSetupComplete.value = authStatus.data.is_setup
    
    if (isSetupComplete.value) await loadData()
  } catch (error) {
    status.value = 'Офлайн'
  } finally {
    checkingAuth.value = false
  }
}

const loadData = async () => {
  if (currentView.value === 'settings') return

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
const handlePinSubmit = async (pin) => {
  pinLoading.value = true
  pinError.value = ''
  if (await authStore.unlockVault(pin)) { await loadData() } else { pinError.value = 'Неверный PIN код' }
  pinLoading.value = false
}
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

onMounted(() => initSystem())
</script>

<template>
  <div class="h-screen w-full flex p-4 gap-4 overflow-hidden relative selection:bg-hub-accent selection:text-white font-sans">
    <ToastContainer />
    <input type="file" ref="fileInputRef" class="hidden" multiple accept="image/*,video/*,.cr2,.nef,.dng" @change="onFileChange" />
    <CreateAlbumModal :isOpen="isCreateAlbumOpen" @close="isCreateAlbumOpen = false" @create="handleCreateAlbum" />
    <MediaViewer :isOpen="viewerOpen" :item="activeItem" :nextItem="nextItem" :prevItem="prevItem" :hasNext="currentMediaIndex < mediaItems.length - 1" :hasPrev="currentMediaIndex > 0" @close="viewerOpen = false" @next="nextMedia" @prev="prevMedia" />
    <SetupWizard v-if="!checkingAuth && !isSetupComplete" @setup-complete="onSetupFinished" />

    <template v-else>
      <div class="w-72 flex flex-col gap-4 shrink-0">
        <div class="h-20 glass-panel rounded-3xl flex items-center px-6 gap-4">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30 border border-white/20">
            <span class="text-white font-black text-xl">H</span>
          </div>
          <div>
            <h1 class="font-bold text-xl tracking-tight text-white leading-none">HomeHub</h1>
            <span class="text-[10px] uppercase font-bold text-white/40 tracking-widest mt-0.5 block">Beta Vault</span>
          </div>
        </div>
        <Sidebar :currentView="currentView" @change-view="changeView" class="flex-1 rounded-3xl" />
      </div>

      <div class="flex-1 flex flex-col gap-4 min-w-0 h-full">
        <Header :status="status" :apiInfo="apiInfo" />

        <main class="flex-1 glass-panel rounded-[2.5rem] overflow-hidden relative flex flex-col border border-white/5">
          <div class="px-8 pt-8 pb-4 shrink-0 z-10">
            <div v-if="currentView === 'library'" class="flex items-center justify-between">
              <h2 class="text-3xl font-bold tracking-tight text-white flex items-center gap-3 drop-shadow-md">
                Библиотека <span class="text-xs font-bold text-white/50 bg-white/10 px-2.5 py-1 rounded-full border border-white/5">{{ mediaItems.length }}</span>
              </h2>
            </div>
            <div v-else-if="currentView === 'albums'" class="flex items-center justify-between">
              <h2 class="text-3xl font-bold tracking-tight text-white drop-shadow-md">Мои Альбомы</h2>
            </div>
            <div v-else-if="currentView === 'album_detail'" class="flex items-center gap-4">
              <button @click="changeView('albums')" class="p-3 hover:bg-white/10 rounded-2xl transition-colors text-white/70 hover:text-white border border-transparent hover:border-white/10">
                <ArrowLeftIcon class="w-6 h-6" />
              </button>
              <div>
                <h2 class="text-3xl font-bold text-white">{{ activeAlbum?.name }}</h2>
                <p class="text-white/40 text-sm">{{ activeAlbum?.description || 'Альбом' }}</p>
              </div>
            </div>
            <div v-else-if="currentView === 'vault' && authStore.isVaultUnlocked" class="flex justify-between items-center">
              <h2 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400 flex items-center gap-3 drop-shadow-sm">
                <span class="relative flex h-3 w-3"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span></span>
                Личный сейф
              </h2>
              <button @click="authStore.lockVault()" class="px-5 py-2 text-sm font-bold text-red-200 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-xl transition-all hover:shadow-[0_0_15px_rgba(239,68,68,0.2)]">LOCK</button>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto px-8 pb-8 scroll-smooth custom-scrollbar relative">
            <div v-if="currentView === 'library'">
              <div v-if="isLoading" class="loader"></div>
              <MediaGrid v-else :items="mediaItems" @refresh="loadData" @open-viewer="openViewer" />
            </div>
            <div v-else-if="currentView === 'albums'">
              <div v-if="isLoading" class="loader"></div>
              <AlbumList v-else :albums="albums" @open-album="openAlbum" @create-album="isCreateAlbumOpen = true" @delete-album="handleDeleteAlbum" />
            </div>
            <div v-else-if="currentView === 'album_detail'">
              <div v-if="isLoading" class="loader"></div>
              <MediaGrid v-else :items="mediaItems" @refresh="loadData" @open-viewer="openViewer" />
            </div>
            <div v-else-if="currentView === 'vault'" class="h-full">
              <PinPad v-if="!authStore.isVaultUnlocked" :error="pinError" :loading="pinLoading" @submit="handlePinSubmit" />
              <div v-else class="flex flex-col h-full">
                <div v-if="isLoading" class="loader border-red-500"></div>
                <div v-else-if="mediaItems.length > 0" class="flex-1"><MediaGrid :items="mediaItems" @refresh="loadData" @open-viewer="openViewer" /></div>
                <div v-else class="empty-state"><div class="text-6xl mb-4 grayscale opacity-30">🛡️</div><p class="text-xl font-medium text-white/70">Здесь пусто</p></div>
              </div>
            </div>
            <div v-else-if="currentView === 'settings'" class="h-full">
              <Settings />
            </div>
          </div>
          
          <div v-if="currentView !== 'vault' && currentView !== 'settings'" class="absolute bottom-8 right-8 z-20">
             <button @click="handleAddPhoto" :disabled="isUploading" class="h-16 w-16 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-2xl shadow-blue-600/40 flex items-center justify-center text-white transition-all hover:scale-105 active:scale-95 group border border-white/20 disabled:opacity-70 disabled:cursor-not-allowed">
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
.loader { @apply flex justify-center py-20 animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-hub-accent mx-auto; }
.empty-state { @apply flex flex-col items-center justify-center h-full text-center p-10 opacity-60; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>