import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const systemApi = {
  getStatus: () => api.get('/system/status'),
  start: (services) => api.post('/system/start', { services }),
  stop: (services) => api.post('/system/stop', { services }),
}

export const configApi = {
  get: (key) => api.get(`/config/${key}`),
  set: (key, value) => api.put(`/config/${key}`, { value }),
  getAll: () => api.get('/config'),
}

export const actionApi = {
  getAll: () => api.get('/actions'),
  trigger: (action) => api.post('/actions/trigger', { action }),
  addMapping: (mapping) => api.post('/actions/mapping', mapping),
  removeMapping: (trigger) => api.delete(`/actions/mapping/${encodeURIComponent(trigger)}`),
}

export const logApi = {
  getRecent: (params) => api.get('/logs', { params }),
  stream: () => new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/logs`),
}

export default api
