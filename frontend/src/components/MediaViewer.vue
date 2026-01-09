<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'
import { 
  XMarkIcon, ChevronLeftIcon, ChevronRightIcon, 
  InformationCircleIcon, ArrowDownTrayIcon,
  MagnifyingGlassPlusIcon, MagnifyingGlassMinusIcon,
  ArrowPathIcon, ArrowsPointingOutIcon,
  CameraIcon, CalendarIcon, ServerIcon,
  MapPinIcon, DocumentDuplicateIcon, GlobeAltIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  isOpen: Boolean,
  item: Object,
  nextItem: Object,
  prevItem: Object,
  hasNext: Boolean,
  hasPrev: Boolean
})

const emit = defineEmits(['close', 'next', 'prev'])

const scale = ref(1)
const rotation = ref(0)
const position = ref({ x: 0, y: 0 })
const isDragging = ref(false)

const showInfo = ref(false)
const isLoading = ref(true)
const details = ref(null)
const loadError = ref(false)

const megapixel = (width, height) => {
  if (!width || !height) return null
  const mp = (width * height) / 1000000
  return mp.toFixed(1) + ' MP'
}

const mapLink = (gps) => {
  if (!gps) return null
  return `https://www.google.com/maps/search/?api=1&query=${gps.lat},${gps.lng}`
}

const getContentUrl = (item) => item ? `/api/media/${item.id}/content` : ''

const formatBytes = (bytes) => {
  if (!bytes || isNaN(bytes)) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDate = (dateInput) => {
  if (!dateInput) return '—'
  const date = typeof dateInput === 'number' ? new Date(dateInput * 1000) : new Date(dateInput)
  return date.toLocaleString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
}

const loadDetails = async () => {
  if (!props.item) return
  try {
    const res = await api.getMediaDetails(props.item.id)
    details.value = res.data
  } catch (e) {
    console.error(e)
  }
}

watch(() => showInfo.value, (val) => { 
  if (val && !details.value) loadDetails() 
})

watch(() => props.item, () => {
  resetView()
  details.value = null
  isLoading.value = true
  loadError.value = false
  if (showInfo.value) loadDetails()
})

const resetView = () => {
  scale.value = 1
  rotation.value = 0
  position.value = { x: 0, y: 0 }
}

const zoomIn = () => { if (scale.value < 5) scale.value += 0.5 }
const zoomOut = () => { 
  if (scale.value > 0.5) scale.value -= 0.5 
  if (scale.value <= 1) position.value = { x: 0, y: 0 } 
}
const rotate = () => { rotation.value = (rotation.value + 90) % 360 }

const close = () => {
  emit('close')
  showInfo.value = false
  resetView()
}

const startDrag = (e) => {
  if (scale.value > 1) {
    e.preventDefault()
    isDragging.value = true
  }
}

const onDrag = (e) => {
  if (!isDragging.value) return
  e.preventDefault()
  position.value.x += e.movementX
  position.value.y += e.movementY
}

const stopDrag = () => { isDragging.value = false }

const handleKeydown = (e) => {
  if (!props.isOpen) return
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowRight' && props.hasNext) emit('next')
  if (e.key === 'ArrowLeft' && props.hasPrev) emit('prev')
  if (e.key === 'ArrowUp') zoomIn()
  if (e.key === 'ArrowDown') zoomOut()
}

const handleWheel = (e) => {
  if (!props.isOpen) return
  e.preventDefault()
  if (e.deltaY < 0) zoomIn()
  else zoomOut()
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('wheel', handleWheel, { passive: false })
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('wheel', handleWheel)
})
</script>

<template>
  <Transition name="fade">
    <div v-if="isOpen" class="fixed inset-0 z-[200] bg-[#000000]/98 backdrop-blur-3xl overflow-hidden select-none">
      
      <div class="absolute top-0 left-0 right-0 h-24 flex items-start pt-6 justify-between px-8 z-50 bg-gradient-to-b from-black/60 to-transparent pointer-events-none">
        
        <div class="pointer-events-auto flex flex-col gap-1 max-w-lg opacity-0 hover:opacity-100 transition-opacity duration-300">
          <h3 class="text-white font-bold text-lg truncate drop-shadow-md tracking-wide">{{ item?.filename }}</h3>
        </div>

        <div class="flex items-center gap-3 pointer-events-auto">
          <button 
            @click="showInfo = !showInfo" 
            class="icon-btn" 
            :class="{ 'bg-blue-600 border-blue-500 text-white': showInfo, 'bg-white/5 border-white/10 text-white/70': !showInfo }" 
            title="Инфо"
          >
            <InformationCircleIcon class="w-6 h-6" />
          </button>
          
          <a :href="getContentUrl(item)" :download="item?.filename" class="icon-btn bg-white/5 border-white/10 text-white/70 hover:text-white" title="Скачать">
            <ArrowDownTrayIcon class="w-6 h-6" />
          </a>

          <div class="w-px h-8 bg-white/10 mx-2"></div>

          <button @click="close" class="icon-btn bg-white/5 border-white/10 text-white/70 hover:bg-red-500/20 hover:border-red-500/30 hover:text-red-400" title="Закрыть">
            <XMarkIcon class="w-7 h-7" />
          </button>
        </div>
      </div>

      <div 
        class="absolute inset-0 flex items-center justify-center cursor-default"
        :class="{ 'cursor-grab': scale > 1, 'cursor-grabbing': isDragging }"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @mouseup="stopDrag"
        @mouseleave="stopDrag"
      >
        <button v-if="hasPrev" @click.stop="emit('prev')" class="nav-btn left-6 group z-50">
          <ChevronLeftIcon class="w-10 h-10 group-hover:-translate-x-1 transition-transform" />
        </button>
        <button v-if="hasNext" @click.stop="emit('next')" class="nav-btn right-6 group z-50">
          <ChevronRightIcon class="w-10 h-10 group-hover:translate-x-1 transition-transform" />
        </button>

        <div 
          class="transition-transform duration-100 ease-linear origin-center will-change-transform z-10"
          :style="{ 
            transform: `translate(${position.x}px, ${position.y}px) scale(${scale}) rotate(${rotation}deg)` 
          }"
        >
          <video 
            v-if="item?.media_type.startsWith('video')" 
            :src="getContentUrl(item)" 
            controls 
            autoplay 
            class="max-h-screen max-w-screen shadow-[0_0_50px_rgba(0,0,0,0.5)] rounded-lg"
            @loadeddata="isLoading = false"
          ></video>

          <img 
            v-else 
            :src="getContentUrl(item)" 
            class="max-h-[95vh] max-w-[95vw] object-contain shadow-[0_0_50px_rgba(0,0,0,0.5)] rounded-sm"
            @load="isLoading = false"
            @error="loadError = true"
            draggable="false"
          />
        </div>

        <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
           <div class="w-12 h-12 border-4 border-white/10 border-t-white/80 rounded-full animate-spin"></div>
        </div>
      </div>

      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 z-50 animate-slide-up pointer-events-auto">
        <div class="flex items-center gap-2 px-3 py-2 bg-[#1e293b]/60 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl hover:bg-[#1e293b]/80 transition-colors">
          <button @click="zoomOut" class="control-btn"><MagnifyingGlassMinusIcon class="w-5 h-5" /></button>
          <span class="w-12 text-center text-xs font-mono text-white/80 select-none">{{ Math.round(scale * 100) }}%</span>
          <button @click="zoomIn" class="control-btn"><MagnifyingGlassPlusIcon class="w-5 h-5" /></button>
          <div class="w-px h-4 bg-white/10 mx-2"></div>
          <button @click="rotate" class="control-btn"><ArrowPathIcon class="w-5 h-5" /></button>
          <button @click="resetView" class="control-btn text-white hover:text-blue-300"><ArrowsPointingOutIcon class="w-5 h-5" /></button>
        </div>
      </div>

      <Transition name="slide-right">
        <div v-if="showInfo" class="absolute top-4 right-4 bottom-4 w-96 z-[60] flex flex-col pointer-events-none">
          <div class="bg-[#0f172a] border border-white/10 rounded-[2rem] shadow-2xl flex-1 flex flex-col overflow-hidden pointer-events-auto mr-4">
            
            <div class="p-6 pb-4 flex items-center justify-between border-b border-white/5 bg-white/5">
              <h2 class="text-xl font-bold text-white flex items-center gap-3">
                <InformationCircleIcon class="w-6 h-6 text-blue-400" />
                Свойства
              </h2>
              <button @click="showInfo = false" class="p-2 rounded-full hover:bg-white/10 text-white/40 hover:text-white transition-colors">
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>

            <div class="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
              
              <div v-if="!details" class="flex justify-center py-20">
                <div class="w-8 h-8 border-2 border-white/10 border-t-blue-500 rounded-full animate-spin"></div>
              </div>

              <div v-else class="space-y-6 animate-fade-in">
                
                <div class="grid grid-cols-2 gap-3">
                  <div class="stat-card">
                    <div class="flex items-center gap-2 mb-1"><ServerIcon class="w-4 h-4 text-purple-400" /><span class="lbl">Вес</span></div>
                    <span class="val">{{ formatBytes(details.size) }}</span>
                  </div>
                  <div class="stat-card">
                    <div class="flex items-center gap-2 mb-1"><CameraIcon class="w-4 h-4 text-blue-400" /><span class="lbl">MP</span></div>
                    <span class="val">{{ megapixel(details.width, details.height) }}</span>
                  </div>
                </div>

                <div class="bg-white/5 rounded-2xl p-4 border border-white/5 flex items-center justify-between">
                  <div>
                    <div class="text-[10px] text-white/40 font-bold uppercase mb-1">Разрешение</div>
                    <div class="text-lg font-mono text-white">{{ details.width }} × {{ details.height }}</div>
                  </div>
                  <div class="text-[10px] bg-white/10 px-2 py-1 rounded text-white/60 font-bold uppercase">{{ details.mime.split('/')[1] }}</div>
                </div>

                <div class="bg-white/5 rounded-2xl p-4 border border-white/5 space-y-3">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-white/5 rounded-xl"><CalendarIcon class="w-4 h-4 text-white/70" /></div>
                    <div>
                      <div class="text-[10px] text-white/40 font-bold uppercase">Дата съемки</div>
                      <div class="text-sm text-white font-bold">{{ formatDate(details.created) }}</div>
                    </div>
                  </div>
                </div>

                <div v-if="details.exif && Object.keys(details.exif).length > 0" class="space-y-3">
                  <div class="text-xs font-bold text-white/40 uppercase tracking-widest pl-1">Камера</div>
                  
                  <div v-if="details.exif.model" class="bg-gradient-to-br from-white/10 to-white/5 p-4 rounded-2xl border border-white/10">
                    <div class="flex justify-between items-start">
                      <div>
                        <p class="text-[10px] text-white/50 mb-1 uppercase">{{ details.exif.make }}</p>
                        <p class="text-sm font-bold text-white leading-tight">{{ details.exif.model }}</p>
                      </div>
                      <CameraIcon class="w-5 h-5 text-white/20" />
                    </div>
                    <div v-if="details.exif.lens" class="mt-3 pt-3 border-t border-white/10 flex items-center gap-2">
                      <div class="w-2 h-2 rounded-full bg-green-500"></div>
                      <p class="text-xs text-white/70 truncate w-full">{{ details.exif.lens }}</p>
                    </div>
                  </div>

                  <div class="grid grid-cols-3 gap-2">
                    <div class="exif-box" v-if="details.exif.iso"><span class="exif-val">ISO {{ details.exif.iso }}</span><span class="exif-lbl">Sens</span></div>
                    <div class="exif-box" v-if="details.exif.f_number"><span class="exif-val">ƒ/{{ details.exif.f_number }}</span><span class="exif-lbl">Aperture</span></div>
                    <div class="exif-box" v-if="details.exif.exposure"><span class="exif-val">{{ details.exif.exposure }}s</span><span class="exif-lbl">Shutter</span></div>
                  </div>
                </div>

                <div v-if="details.exif && details.exif.gps" class="bg-white/5 rounded-2xl p-4 border border-white/5 space-y-3">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2 text-xs font-bold text-white/40 uppercase"><MapPinIcon class="w-4 h-4" /> Локация</div>
                    <a :href="mapLink(details.exif.gps)" target="_blank" class="text-[10px] text-blue-400 hover:text-blue-300 font-bold uppercase flex items-center gap-1">Карта <GlobeAltIcon class="w-3 h-3" /></a>
                  </div>
                  <div class="text-xs font-mono text-white/70">{{ details.exif.gps.lat.toFixed(5) }}, {{ details.exif.gps.lng.toFixed(5) }}</div>
                </div>

                <div class="pt-4 group cursor-pointer" @click="copyToClipboard(details.filename)">
                  <div class="label mb-2 flex justify-between">
                    <span>Имя файла</span>
                    <span class="text-[9px] opacity-0 group-hover:opacity-100 transition-opacity text-blue-400">Копировать</span>
                  </div>
                  <div class="bg-black/30 rounded-xl p-3 border border-white/5 font-mono text-[10px] text-white/50 break-all hover:text-white/80 hover:bg-black/50 transition-all flex items-center gap-2">
                    <DocumentDuplicateIcon class="w-4 h-4 shrink-0 opacity-50" />
                    {{ details.filename }}
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </Transition>

    </div>
  </Transition>
</template>

<style scoped>
.icon-btn { @apply w-12 h-12 flex items-center justify-center rounded-2xl border border-transparent transition-all duration-300 active:scale-95 shadow-lg backdrop-blur-md; }
.control-btn { @apply w-8 h-8 flex items-center justify-center rounded-full text-white/60 hover:text-white hover:bg-white/20 transition-all active:scale-95; }
.nav-btn { @apply absolute top-1/2 -translate-y-1/2 p-4 rounded-full bg-black/40 text-white/70 hover:text-white hover:bg-black/60 transition-all outline-none active:scale-95 shadow-lg backdrop-blur-sm border border-white/10; }
.stat-card { @apply bg-white/5 rounded-2xl p-3 border border-white/5 flex flex-col justify-center hover:bg-white/10 transition-colors h-20 pl-4; }
.stat-card .val { @apply text-lg font-bold text-white mt-0.5; }
.stat-card .lbl { @apply text-[10px] text-white/40 font-bold uppercase tracking-wider; }
.exif-box { @apply bg-white/5 rounded-xl p-2 border border-white/5 flex flex-col items-center justify-center text-center min-h-[60px]; }
.exif-val { @apply text-xs font-bold text-white leading-tight break-words w-full; }
.exif-lbl { @apply text-[9px] text-white/40 mt-1 uppercase; }
.label { @apply text-[10px] font-bold text-white/40 uppercase tracking-wider; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateX(50px); opacity: 0; }
.animate-slide-up { animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideUp { from { transform: translate(-50%, 100%); opacity: 0; } to { transform: translate(-50%, 0); opacity: 1; } }
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>