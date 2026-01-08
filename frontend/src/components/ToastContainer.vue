<script setup>
import { useNotificationStore } from '@/stores/notification'
import { XMarkIcon, CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon } from '@heroicons/vue/24/outline'

const store = useNotificationStore()
const getIcon = (type) => {
  switch (type) {
    case 'success': return CheckCircleIcon
    case 'error': return ExclamationCircleIcon
    case 'warning': return ExclamationCircleIcon
    default: return InformationCircleIcon
  }
}
</script>

<template>
  <div class="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 pointer-events-none">
    <TransitionGroup name="toast">
      <div 
        v-for="notification in store.notifications" 
        :key="notification.id"
        class="glass-popup pointer-events-auto min-w-[320px] rounded-2xl p-4 flex items-start gap-4 backdrop-blur-md"
      >
        <div class="p-2 rounded-full bg-white/5 shrink-0">
           <component :is="getIcon(notification.type)" class="w-5 h-5" :class="{
             'text-green-400': notification.type === 'success',
             'text-red-400': notification.type === 'error',
             'text-yellow-400': notification.type === 'warning',
             'text-blue-400': notification.type === 'info'
           }" />
        </div>
        
        <div class="pt-1.5">
           <p class="text-sm font-medium text-white leading-tight">{{ notification.message }}</p>
        </div>
        
        <button @click="store.remove(notification.id)" class="ml-auto text-gray-500 hover:text-white transition-colors">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.glass-popup {
  background: rgba(30, 30, 36, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.toast-enter-active, .toast-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.toast-enter-from { opacity: 0; transform: translateY(20px) scale(0.9); }
.toast-leave-to { opacity: 0; transform: translateX(50px); }
</style>