// Path: frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // Состояние: разблокирован ли сейф
  const isVaultUnlocked = ref(false)
  // Токен сессии (пока простой флаг)
  const sessionToken = ref(null)

  // Попытка входа в сейф
  const unlockVault = async (pin) => {
    try {
      const response = await api.login(pin)
      if (response.data.status === 'success') {
        isVaultUnlocked.value = true
        sessionToken.value = response.data.token
        return true
      }
    } catch (error) {
      console.error("Auth failed", error)
      return false
    }
    return false
  }

  // Блокировка (например, при сворачивании или тайм-ауте)
  const lockVault = () => {
    isVaultUnlocked.value = false
    sessionToken.value = null
  }

  return {
    isVaultUnlocked,
    unlockVault,
    lockVault
  }
})