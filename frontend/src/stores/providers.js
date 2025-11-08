import { defineStore } from 'pinia'
import api from '../services/api'

export const useProvidersStore = defineStore('providers', {
  state: () => ({
    providers: [],
    loading: false,
    error: null
  }),

  getters: {
    activeProviders: (state) => state.providers.filter(p => p.active),
    inactiveProviders: (state) => state.providers.filter(p => !p.active),
    providersByType: (state) => {
      const grouped = {}
      state.providers.forEach(p => {
        if (!grouped[p.type]) grouped[p.type] = []
        grouped[p.type].push(p)
      })
      return grouped
    }
  },

  actions: {
    async fetchProviders() {
      this.loading = true
      this.error = null
      try {
        this.providers = await api.getProviders()
      } catch (error) {
        this.error = error.message
        // Error handled by setting this.error
      } finally {
        this.loading = false
      }
    },

    async createProvider(providerData) {
      this.loading = true
      this.error = null
      try {
        const newProvider = await api.createProvider(providerData)
        this.providers.push(newProvider)
        return newProvider
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateProvider(id, data) {
      this.loading = true
      this.error = null
      try {
        const updated = await api.updateProvider(id, data)
        const index = this.providers.findIndex(p => p.id === id)
        if (index !== -1) {
          this.providers[index] = updated
        }
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteProvider(id) {
      this.loading = true
      this.error = null
      try {
        await api.deleteProvider(id)
        this.providers = this.providers.filter(p => p.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async testProvider(id) {
      try {
        return await api.testProvider(id)
      } catch (error) {
        throw error
      }
    }
  }
})
