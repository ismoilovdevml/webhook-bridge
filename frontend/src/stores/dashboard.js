import { defineStore } from 'pinia'
import api from '../services/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    stats: null,
    recentEvents: [],
    activityTimeline: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchDashboardData() {
      this.loading = true
      this.error = null
      try {
        const [stats, recentEvents, timeline] = await Promise.all([
          api.getDashboardStats(),
          api.getRecentEvents(10),
          api.getActivityTimeline(7)
        ])

        this.stats = stats
        this.recentEvents = recentEvents
        this.activityTimeline = timeline
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        this.loading = false
      }
    },

    async refresh() {
      await this.fetchDashboardData()
    }
  }
})
