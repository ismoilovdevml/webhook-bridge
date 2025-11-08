import { defineStore } from 'pinia'
import api from '../services/api'

export const useEventsStore = defineStore('events', {
  state: () => ({
    events: [],
    stats: null,
    loading: false,
    error: null,
    filters: {
      platform: null,
      event_type: null,
      status: null,
      project: null
    }
  }),

  getters: {
    filteredEvents: (state) => {
      let filtered = [...state.events]

      if (state.filters.platform) {
        filtered = filtered.filter(e => e.platform === state.filters.platform)
      }
      if (state.filters.event_type) {
        filtered = filtered.filter(e => e.event_type === state.filters.event_type)
      }
      if (state.filters.status) {
        filtered = filtered.filter(e => e.status === state.filters.status)
      }
      if (state.filters.project) {
        filtered = filtered.filter(e => e.project.includes(state.filters.project))
      }

      return filtered
    }
  },

  actions: {
    async fetchEvents(params = {}) {
      this.loading = true
      this.error = null
      try {
        this.events = await api.getEvents(params)
      } catch (error) {
        this.error = error.message
        // Error handled by setting this.error
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      try {
        this.stats = await api.getEventStats()
      } catch {
        // Stats fetch error - non-critical
      }
    },

    async clearEvents(status = null) {
      this.loading = true
      try {
        await api.clearEvents(status)
        await this.fetchEvents()
        await this.fetchStats()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    setFilter(filterName, value) {
      this.filters[filterName] = value
    },

    clearFilters() {
      this.filters = {
        platform: null,
        event_type: null,
        status: null,
        project: null
      }
    }
  }
})
