import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = '/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token')
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated
  },

  actions: {
    async login(username, password) {
      try {
        const response = await axios.post(`${API_URL}/auth/login`, {
          username,
          password
        })

        const { access_token, user } = response.data

        // Store token and user
        this.token = access_token
        this.user = user
        this.isAuthenticated = true

        // Save to localStorage
        localStorage.setItem('token', access_token)
        localStorage.setItem('user', JSON.stringify(user))

        // Set default authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

        return user
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async fetchCurrentUser() {
      if (!this.token) return null

      try {
        const response = await axios.get(`${API_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })

        this.user = response.data
        this.isAuthenticated = true
        localStorage.setItem('user', JSON.stringify(response.data))

        return response.data
      } catch {
        this.logout()
        return null
      }
    },

    logout() {
      this.token = null
      this.user = null
      this.isAuthenticated = false

      localStorage.removeItem('token')
      localStorage.removeItem('user')

      delete axios.defaults.headers.common['Authorization']
    },

    initializeAuth() {
      const token = localStorage.getItem('token')
      const userStr = localStorage.getItem('user')

      if (token && userStr) {
        this.token = token
        this.user = JSON.parse(userStr)
        this.isAuthenticated = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }
    }
  }
})
