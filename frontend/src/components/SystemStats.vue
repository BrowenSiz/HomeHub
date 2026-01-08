<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { 
  ServerIcon, 
  CpuChipIcon, 
  PhotoIcon, 
  LockClosedIcon, 
  FolderIcon,
  CircleStackIcon 
} from '@heroicons/vue/24/outline'

const stats = ref(null)
const loading = ref(true)

const loadStats = async () => {
  loading.value = true
  try {
    const res = await api.getSystemStats()
    stats.value = res.data
  } catch (e) {
    console.error("Failed to load stats", e)
  } finally {
    loading.value = false
  }
}

const formatBytes = (bytes, decimals = 2) => {
  if (!+bytes) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div class="max-w-5xl mx-auto pb-10">
    
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
    </div>

    <div v-else-if="stats" class="space-y-6">
      
      <!-- 1. ДИСКОВОЕ ПРОСТРАНСТВО -->
      <section class="bg-white/5 rounded-3xl p-8 border border-white/10 backdrop-blur-md">
        <div class="flex items-center gap-4 mb-6">
          <div class="p-3 bg-purple-500/20 rounded-2xl text-purple-400">
            <CpuChipIcon class="w-8 h-8" />
          </div>
          <div>
            <h3 class="text-xl font-bold text-white">Дисковое пространство</h3>
            <p class="text-white/50 text-sm">Использование жесткого диска</p>
          </div>
        </div>

        <div class="bg-black/20 rounded-2xl p-6 border border-white/5">
          <div class="flex justify-between items-end mb-3">
              <span class="text-white font-medium flex items-center gap-2">
                  <ServerIcon class="w-5 h-5 text-white/50" />
                  Системный диск
              </span>
              <span class="text-3xl font-bold text-white">{{ stats.storage.percent }}%</span>
          </div>
          
          <div class="w-full bg-white/10 rounded-full h-5 overflow-hidden mb-4">
              <div 
                  class="h-full rounded-full transition-all duration-1000 ease-out relative overflow-hidden"
                  :class="{
                      'bg-gradient-to-r from-green-500 to-emerald-400': stats.storage.percent < 70,
                      'bg-gradient-to-r from-yellow-500 to-orange-400': stats.storage.percent >= 70 && stats.storage.percent < 90,
                      'bg-gradient-to-r from-red-500 to-red-400': stats.storage.percent >= 90
                  }"
                  :style="{ width: `${stats.storage.percent}%` }"
              >
                <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
              </div>
          </div>
          
          <div class="grid grid-cols-3 gap-4 text-center divide-x divide-white/10">
              <div>
                  <div class="text-white/40 text-xs uppercase font-bold tracking-wider mb-1">Всего</div>
                  <div class="text-white font-mono">{{ formatBytes(stats.storage.total) }}</div>
              </div>
              <div>
                  <div class="text-white/40 text-xs uppercase font-bold tracking-wider mb-1">Занято</div>
                  <div class="text-white font-mono">{{ formatBytes(stats.storage.used) }}</div>
              </div>
              <div>
                  <div class="text-white/40 text-xs uppercase font-bold tracking-wider mb-1">Свободно</div>
                  <div class="text-white font-mono">{{ formatBytes(stats.storage.free) }}</div>
              </div>
          </div>
        </div>
      </section>

      <!-- 2. СТАТИСТИКА ПРИЛОЖЕНИЯ -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white/5 rounded-3xl p-6 border border-white/10 backdrop-blur-md flex items-center gap-5">
            <div class="p-4 bg-blue-500/10 rounded-2xl text-blue-400">
                <PhotoIcon class="w-8 h-8" />
            </div>
            <div>
                <div class="text-3xl font-bold text-white">{{ stats.app.total_files }}</div>
                <div class="text-white/50">Файлов в библиотеке</div>
            </div>
        </div>

        <div class="bg-white/5 rounded-3xl p-6 border border-white/10 backdrop-blur-md flex items-center gap-5">
            <div class="p-4 bg-orange-500/10 rounded-2xl text-orange-400">
                <LockClosedIcon class="w-8 h-8" />
            </div>
            <div>
                <div class="text-3xl font-bold text-white">{{ stats.app.encrypted_files }}</div>
                <div class="text-white/50">Зашифровано в сейфе</div>
            </div>
        </div>

        <div class="bg-white/5 rounded-3xl p-6 border border-white/10 backdrop-blur-md flex items-center gap-5">
            <div class="p-4 bg-emerald-500/10 rounded-2xl text-emerald-400">
                <CircleStackIcon class="w-8 h-8" />
            </div>
            <div>
                <div class="text-3xl font-bold text-white">{{ formatBytes(stats.app.db_size) }}</div>
                <div class="text-white/50">Размер базы данных</div>
            </div>
        </div>

        <div class="bg-white/5 rounded-3xl p-6 border border-white/10 backdrop-blur-md flex items-center gap-5">
            <div class="p-4 bg-pink-500/10 rounded-2xl text-pink-400">
                <FolderIcon class="w-8 h-8" />
            </div>
            <div>
                <div class="text-3xl font-bold text-white">{{ stats.app.albums }}</div>
                <div class="text-white/50">Альбомов создано</div>
            </div>
        </div>
      </section>

      <section class="bg-white/5 rounded-3xl p-8 border border-white/10 backdrop-blur-md">
        <h3 class="text-lg font-bold text-white mb-4">Физическое расположение</h3>
        <div class="bg-black/40 rounded-xl p-4 border border-white/10 font-mono text-sm text-white/70 break-all select-all flex items-center justify-between group">
            <span>{{ stats.paths.data_root }}</span>
            <FolderIcon class="w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
        <p class="text-white/30 text-xs mt-2 ml-1">Рекомендуется делать резервную копию этой папки.</p>
      </section>

    </div>
  </div>
</template>