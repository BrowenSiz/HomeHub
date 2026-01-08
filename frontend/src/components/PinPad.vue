<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { LockClosedIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  error: String,
  loading: Boolean
})

const emit = defineEmits(['submit'])

const pin = ref('')
const shake = ref(false)
const inputRef = ref(null)

const handleInput = (event) => {
  const val = event.target.value.replace(/\D/g, '')
  pin.value = val

  if (pin.value.length === 4) {
    emit('submit', pin.value)
  }
}

watch(() => props.error, (newVal) => {
  if (newVal) {
    shake.value = true
    setTimeout(() => {
      shake.value = false
      pin.value = ''
      // Возвращаем фокус
      nextTick(() => inputRef.value?.focus())
    }, 500)
  }
})

onMounted(() => {
  nextTick(() => inputRef.value?.focus())
})
</script>

<template>
  <div class="h-full flex flex-col items-center justify-center p-6 animate-fade-in">
    <div class="w-full max-w-xs bg-black/40 backdrop-blur-xl rounded-[2.5rem] p-8 border border-white/10 shadow-2xl relative overflow-hidden">
      
      <!-- Фоновый эффект -->
      <div class="absolute -top-20 -left-20 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl"></div>

      <div class="relative z-10 flex flex-col items-center">
        <div class="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mb-6 shadow-inner border border-white/5">
          <LockClosedIcon class="w-8 h-8 text-white/50" />
        </div>

        <h2 class="text-xl font-bold text-white mb-2">Доступ к сейфу</h2>
        <p class="text-white/40 text-sm mb-8 text-center">Введите PIN код с клавиатуры</p>

        <div class="relative w-full mb-4">
          <input 
            ref="inputRef"
            type="password" 
            v-model="pin"
            @input="handleInput"
            maxlength="4"
            :disabled="loading"
            class="w-full bg-black/50 border-2 border-white/10 rounded-2xl py-4 text-center text-3xl tracking-[0.5em] text-white focus:outline-none focus:border-blue-500/50 transition-all font-mono shadow-inner no-eye placeholder:text-white/10"
            :class="{ 'border-red-500/50 animate-shake': shake }"
            placeholder="••••"
            inputmode="numeric"
          />
          <div v-if="error" class="absolute -bottom-6 left-0 w-full text-center text-red-400 text-xs font-bold animate-pulse">
            {{ error }}
          </div>
        </div>

        <div v-if="loading" class="mt-4 flex justify-center">
           <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-white/50"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.no-eye::-ms-reveal,
.no-eye::-ms-clear {
  display: none;
}
.no-eye::-webkit-credentials-auto-fill-button {
    visibility: hidden;
    pointer-events: none;
    position: absolute;
    right: 0;
}

.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
</style>