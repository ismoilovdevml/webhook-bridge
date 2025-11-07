import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // Providers
  getProviders() {
    return api.get('/providers')
  },
  getProvider(id) {
    return api.get(`/providers/${id}`)
  },
  createProvider(data) {
    return api.post('/providers', data)
  },
  updateProvider(id, data) {
    return api.put(`/providers/${id}`, data)
  },
  deleteProvider(id) {
    return api.delete(`/providers/${id}`)
  },
  testProvider(id) {
    return api.post(`/providers/${id}/test`)
  },

  // Events
  getEvents(params = {}) {
    return api.get('/events', { params })
  },
  getEvent(id) {
    return api.get(`/events/${id}`)
  },
  getEventStats() {
    return api.get('/events/stats')
  },
  clearEvents(status = null) {
    return api.delete('/events', { params: { status } })
  },

  // Dashboard
  getDashboardStats() {
    return api.get('/dashboard/stats')
  },
  getRecentEvents(limit = 10) {
    return api.get('/dashboard/recent-events', { params: { limit } })
  },
  getActivityTimeline(days = 7) {
    return api.get('/dashboard/activity-timeline', { params: { days } })
  },

  // Webhook
  testWebhook() {
    return api.get('/webhook/test')
  }
}
