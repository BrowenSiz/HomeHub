import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from './notification'

export const useUploadStore = defineStore('upload', () => {
  const notify = useNotificationStore()
  
  const isDragging = ref(false)
  const isUploading = ref(false)
  const progress = ref(0)
  const totalFiles = ref(0)
  const finishedFiles = ref(0)
  const currentFileName = ref('')
  
  const queue = ref([])

  let dragCounter = 0

  const onDragEnter = (e) => {
    e.preventDefault()
    dragCounter++
    isDragging.value = true
  }

  const onDragLeave = (e) => {
    e.preventDefault()
    dragCounter--
    if (dragCounter === 0) {
      isDragging.value = false
    }
  }

  const onDrop = async (e, currentAlbumId = null) => {
    e.preventDefault()
    isDragging.value = false
    dragCounter = 0
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await startUpload(e.dataTransfer.files, currentAlbumId)
    }
  }

  const startUpload = async (fileList, albumId = null) => {
    if (isUploading.value) {
      notify.show('Подождите завершения текущей загрузки', 'warning')
      return
    }

    const files = Array.from(fileList)
    if (files.length === 0) return

    isUploading.value = true
    totalFiles.value = files.length
    finishedFiles.value = 0
    progress.value = 0
    
    for (const file of files) {
      currentFileName.value = file.name
      const formData = new FormData()
      formData.append('files', file)
      
      try {
        const res = await api.uploadFiles(formData)
        
        if (albumId && res.data.ids && res.data.ids.length > 0) {
           await api.setAlbum(res.data.ids, albumId)
        }

        finishedFiles.value++
        progress.value = (finishedFiles.value / totalFiles.value) * 100
      } catch (e) {
        console.error(`Failed to upload ${file.name}`, e)
        notify.show(`Ошибка загрузки: ${file.name}`, 'error')
      }
    }

    notify.show(`Загружено файлов: ${finishedFiles.value}`, 'success')
    isUploading.value = false
    currentFileName.value = ''
    
    return true
  }

  return {
    isDragging,
    isUploading,
    progress,
    totalFiles,
    finishedFiles,
    currentFileName,
    onDragEnter,
    onDragLeave,
    onDrop,
    startUpload
  }
})