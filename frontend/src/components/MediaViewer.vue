<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { 
  XMarkIcon, ChevronLeftIcon, ChevronRightIcon, 
  ArrowDownTrayIcon, InformationCircleIcon,
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

const mediaUrl = computed(() => props.item ? `/api/media/${props.item.id}/content` : '')
const isVideo = computed(() => props.item?.media_type?.startsWith('video/'))

const videoRef = ref(null)
const isPlaying = ref(false)
const videoError = ref(false)
const showInfo = ref(false)

// State для зума и панорамирования
const scale = ref(1)
const translate = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const startPos = ref({ x: 0, y: 0 })
const containerRef = ref(null)

// Сброс при смене
watch(() => props.item, () => {
  videoError.value = false
  isPlaying.value = false
  resetZoom()
  showInfo.value = false
})

const resetZoom = () => {
  scale.value = 1
  translate.value = { x: 0, y: 0 }
}

const handleVideoError = () => { videoError.value = true }

const togglePlay = () => {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play()
    isPlaying.value = true
  } else {
    videoRef.value.pause()
    isPlaying.value = false
  }
}

const downloadMedia = () => {
  if (!props.item) return
  const link = document.createElement('a')
  link.href = mediaUrl.value
  link.download = props.item.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const formatBytes = (bytes) => {
  // Проверка на валидность числа
  if (bytes === undefined || bytes === null || isNaN(bytes)) return 'Неизвестно'
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('ru-RU', { 
    day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' 
  })
}

// === ЛОГИКА ЗУМА И ПАН ===

const handleWheel = (e) => {
  if (isVideo.value) return
  e.preventDefault()

  const delta = e.deltaY * -0.002
  const newScale = Math.min(Math.max(1, scale.value + delta), 5)
  
  if (containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect()
    // Координаты мыши относительно центра контейнера
    const mouseX = e.clientX - rect.left - rect.width / 2
    const mouseY = e.clientY - rect.top - rect.height / 2
    
    // Корректируем смещение, чтобы зумить в точку курсора
    const scaleRatio = newScale / scale.value
    translate.value.x = mouseX - (mouseX - translate.value.x) * scaleRatio
    translate.value.y = mouseY - (mouseY - translate.value.y) * scaleRatio
  }

  scale.value = newScale
  // Если масштаб вернулся к 1 (или меньше), сбрасываем позицию в центр
  if (scale.value <= 1.01) {
    scale.value = 1
    translate.value = { x: 0, y: 0 }
  }
}

const startDrag = (e) => {
  // Перетаскивание работает только если есть увеличение
  if (scale.value <= 1) return
  isDragging.value = true
  startPos.value = { x: e.clientX - translate.value.x, y: e.clientY - translate.value.y }
  e.preventDefault() // предотвращаем выделение текста
}

const onDrag = (e) => {
  if (!isDragging.value) return
  translate.value = {
    x: e.clientX - startPos.value.x,
    y: e.clientY - startPos.value.y
  }
}

const stopDrag = () => { isDragging.value = false }

// Обработка клавиатуры
const handleKeydown = (e) => {
  if (!props.isOpen) return
  if (e.key === 'Escape') emit('close')
  if (e.key === 'ArrowRight') emit('next')
  if (e.key === 'ArrowLeft') emit('prev')
  if (e.key === ' ' && isVideo.value) { e.preventDefault(); togglePlay() }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 bg-black/95 backdrop-blur-xl flex flex-col animate-fade-in select-none"
       @mouseup="stopDrag" @mouseleave="stopDrag">
    
    <!-- Toolbar -->
    <div class="h-20 flex items-center justify-between px-8 z-30 pointer-events-none">
      <div class="flex items-center gap-4 pointer-events-auto">
         <!-- Имя файла -->
         <div class="glass-pill px-4 py-2 text-white/90 font-medium truncate max-w-xs">
            {{ item?.filename }}
         </div>
         
         <!-- Индикатор масштаба (только для фото и если > 100%) -->
         <div v-if="!isVideo && scale > 1.01" class="glass-pill px-3 py-2 text-hub-accent font-bold text-xs animate-scale-in">
            {{ Math.round(scale * 100) }}%
         </div>
      </div>

      <div class="flex items-center gap-3 pointer-events-auto">
        <button @click="showInfo = !showInfo" class="glass-btn" :class="{ 'bg-white/20': showInfo }" title="Информация">
          <InformationCircleIcon class="w-6 h-6" />
        </button>
        <button @click="downloadMedia" class="glass-btn" title="Скачать">
          <ArrowDownTrayIcon class="w-6 h-6" />
        </button>
        <button @click="$emit('close')" class="glass-btn hover:bg-red-500/30 hover:border-red-500/50 hover:text-red-200" title="Закрыть">
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>
    </div>

    <!-- Stage (Область просмотра) -->
    <div class="flex-1 flex items-center justify-center relative overflow-hidden group w-full h-full" ref="containerRef">
      
      <!-- Кнопки Навигации -->
      <button v-if="hasPrev" @click.stop="$emit('prev')" class="nav-btn left-6 pointer-events-auto">
        <ChevronLeftIcon class="w-8 h-8" />
      </button>
      
      <button v-if="hasNext" @click.stop="$emit('next')" class="nav-btn right-6 pointer-events-auto">
        <ChevronRightIcon class="w-8 h-8" />
      </button>

      <!-- Контейнер медиа (Обрабатывает события мыши) -->
      <div 
        class="relative w-full h-full flex items-center justify-center p-0 overflow-hidden"
        :class="{ 'cursor-grab': scale > 1 && !isDragging, 'cursor-grabbing': isDragging }"
        @wheel="handleWheel"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @click.stop
      >
        <!-- VIDEO -->
        <template v-if="isVideo">
          <div v-if="videoError" class="glass-card p-10 text-center pointer-events-auto">
            <h3 class="text-xl font-bold text-white mb-2">Видео не поддерживается</h3>
            <p class="text-gray-400 mb-4 text-sm">Ваш браузер не может воспроизвести этот формат.</p>
            <button @click="downloadMedia" class="bg-hub-accent hover:bg-blue-600 px-6 py-2 rounded-xl text-white font-bold transition-colors">Скачать файл</button>
          </div>
          <video 
            v-else
            ref="videoRef"
            :src="mediaUrl" 
            class="max-h-full max-w-full rounded-lg shadow-2xl pointer-events-auto"
            controls autoplay playsinline
            @error="handleVideoError"
          ></video>
        </template>

        <!-- IMAGE -->
        <img 
          v-else
          :src="mediaUrl" 
          class="max-h-full max-w-full object-contain rounded-lg shadow-2xl transition-transform duration-75 ease-out will-change-transform"
          :style="{ transform: `translate(${translate.x}px, ${translate.y}px) scale(${scale})` }"
          draggable="false"
        />
      </div>

      <!-- Info Panel (Сбоку) -->
      <transition name="slide-fade">
        <div v-if="showInfo" class="absolute right-8 top-8 bottom-20 w-80 glass-card p-6 flex flex-col gap-4 overflow-y-auto z-40 pointer-events-auto">
           <h3 class="text-lg font-bold text-white border-b border-white/10 pb-2">Информация</h3>
           
           <div class="info-row">
             <span class="label">Имя файла</span>
             <span class="value break-all">{{ item?.filename }}</span>
           </div>
           
           <div class="info-row">
             <span class="label">Размер</span>
             <span class="value">{{ formatBytes(item?.file_size) }}</span>
           </div>
           
           <div class="info-row">
             <span class="label">Тип</span>
             <span class="value uppercase">{{ item?.media_type }}</span>
           </div>
           
           <div class="info-row">
             <span class="label">Дата</span>
             <span class="value">{{ formatDate(item?.created_at) }}</span>
           </div>
           
           <div v-if="item?.album" class="info-row mt-2 p-3 bg-white/5 rounded-xl border border-white/5">
             <span class="label text-hub-accent font-bold mb-1 block">Альбом</span>
             <span class="value block truncate">{{ item.album.name }}</span>
           </div>
           
           <div class="info-row mt-auto pt-4 border-t border-white/5">
             <span class="label">Путь</span>
             <span class="value text-[10px] font-mono text-gray-500 break-all leading-tight">{{ item?.original_path }}</span>
           </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<style scoped>
.glass-pill { 
  @apply bg-black/40 backdrop-blur-xl border border-white/10 rounded-full shadow-lg; 
}
.glass-btn { 
  @apply p-3 rounded-full bg-black/30 hover:bg-white/10 border border-white/10 text-white/80 hover:text-white transition-all backdrop-blur-md active:scale-95; 
}
.glass-card { 
  @apply bg-[#1a1a1a]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl; 
}
.nav-btn { 
  @apply absolute top-1/2 -translate-y-1/2 p-4 rounded-full bg-black/20 hover:bg-white/10 border border-white/5 text-white/40 hover:text-white backdrop-blur-md transition-all z-40 outline-none hover:scale-110 active:scale-95; 
}
.info-row { 
  @apply flex flex-col gap-1; 
}
.label { 
  @apply text-xs text-gray-500 uppercase tracking-wider font-bold; 
}
.value { 
  @apply text-sm text-gray-200 font-medium; 
}

/* Animations */
.animate-fade-in { animation: fadeIn 0.25s ease-out; }
.animate-scale-in { animation: scaleIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { transform: scale(0.8); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateX(30px); opacity: 0; }
</style>