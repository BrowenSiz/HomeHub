// Path: frontend/src/stores/notification.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  let nextId = 1

  const show = (message, type = 'info') => { // type: 'info', 'success', 'error', 'warning'
    const id = nextId++
    notifications.value.push({ id, message, type })

    // Автоматическое удаление через 3 секунды
    setTimeout(() => {
      remove(id)
    }, 3000)
  }

  const remove = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  return {
    notifications,
    show,
    remove
  }
})