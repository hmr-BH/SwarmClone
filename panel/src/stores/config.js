import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useConfigStore = defineStore('config', () => {
  const system = ref({
    mode: 'development',
    logLevel: 'INFO',
  })
  
  const redis = ref({
    host: 'localhost',
    port: 6379,
    db: 0,
  })
  
  const asr = ref({
    enabled: true,
    engine: 'whisper',
    model: 'base',
    language: 'zh',
  })
  
  const vrchat = ref({
    enabled: true,
    oscAddress: '127.0.0.1',
    oscPort: 9000,
    autoReconnect: true,
  })
  
  const keyboard = ref({
    enabled: true,
  })
  
  function updateConfig(section, data) {
    if (section === 'system') {
      Object.assign(system.value, data)
    } else if (section === 'redis') {
      Object.assign(redis.value, data)
    } else if (section === 'asr') {
      Object.assign(asr.value, data)
    } else if (section === 'vrchat') {
      Object.assign(vrchat.value, data)
    } else if (section === 'keyboard') {
      Object.assign(keyboard.value, data)
    }
  }
  
  return {
    system,
    redis,
    asr,
    vrchat,
    keyboard,
    updateConfig,
  }
})
