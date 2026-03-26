import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSystemStore = defineStore('system', () => {
  const version = ref('0.1.0')
  const mode = ref('development')
  const uptime = ref(0)
  
  const services = ref({
    core: { status: 'stopped', uptime: 0, pid: null },
    asr: { status: 'stopped', uptime: 0, pid: null },
    vrchat: { status: 'stopped', uptime: 0, pid: null },
    keyboard: { status: 'stopped', uptime: 0, pid: null },
    web: { status: 'stopped', uptime: 0, pid: null },
  })
  
  function updateServiceStatus(name, status) {
    if (services.value[name]) {
      services.value[name].status = status
    }
  }
  
  function setServicesStatus(status) {
    Object.keys(services.value).forEach(name => {
      services.value[name].status = status
    })
  }
  
  return {
    version,
    mode,
    uptime,
    services,
    updateServiceStatus,
    setServicesStatus,
  }
})
