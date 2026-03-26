import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useActionStore = defineStore('action', () => {
  const mappings = ref([
    { trigger: '你好', actionName: 'wave', actionType: 'gesture', cooldown: 2.0, enabled: true },
    { trigger: '谢谢', actionName: 'bow', actionType: 'gesture', cooldown: 2.0, enabled: true },
    { trigger: '开心', actionName: 'happy', actionType: 'expression', cooldown: 1.0, enabled: true },
    { trigger: '难过', actionName: 'sad', actionType: 'expression', cooldown: 1.0, enabled: true },
  ])
  
  function addMapping(mapping) {
    mappings.value.push(mapping)
  }
  
  function removeMapping(index) {
    mappings.value.splice(index, 1)
  }
  
  function updateMapping(index, mapping) {
    if (index >= 0 && index < mappings.value.length) {
      mappings.value[index] = { ...mappings.value[index], ...mapping }
    }
  }
  
  return {
    mappings,
    addMapping,
    removeMapping,
    updateMapping,
  }
})
