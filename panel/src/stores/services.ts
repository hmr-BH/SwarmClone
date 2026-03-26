import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Service {
  id: string
  name: string
  status: 'running' | 'stopped' | 'unknown'
  lastUpdate: Date
}

export const useServicesStore = defineStore('services', () => {
  const services = ref<Service[]>([
    { id: 'core', name: 'Core (Python)', status: 'unknown', lastUpdate: new Date() },
    { id: 'panel', name: 'Panel (Vue.js)', status: 'unknown', lastUpdate: new Date() },
    { id: 'frontend', name: 'Frontend (Godot)', status: 'unknown', lastUpdate: new Date() },
    { id: 'asr', name: 'ASR Client', status: 'unknown', lastUpdate: new Date() },
    { id: 'vision', name: 'Vision Capture', status: 'unknown', lastUpdate: new Date() },
    { id: 'vrchat', name: 'VRChat Service', status: 'unknown', lastUpdate: new Date() },
  ])

  const runningCount = computed(() =>
    services.value.filter((s) => s.status === 'running').length
  )

  const updateServiceStatus = (
    id: string,
    status: Service['status']
  ) => {
    const service = services.value.find((s) => s.id === id)
    if (service) {
      service.status = status
      service.lastUpdate = new Date()
    }
  }

  return {
    services,
    runningCount,
    updateServiceStatus,
  }
})
