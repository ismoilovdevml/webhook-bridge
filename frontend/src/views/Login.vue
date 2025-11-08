<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo & Title -->
      <div class="login-header">
        <div class="login-logo">
          <span class="logo-icon">🔔</span>
          <h1 class="logo-text">Webhook Bridge</h1>
        </div>
        <p class="login-subtitle">Sign in to configure multi-channel alerts</p>
      </div>

      <!-- Login Form -->
      <form class="login-form" @submit.prevent="handleLogin">
        <!-- Username Field -->
        <div class="form-field">
          <label class="field-label">Username</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <input
              v-model="credentials.username"
              type="text"
              class="field-input"
              placeholder="Enter your username"
              autocomplete="username"
              required
              autofocus
            />
          </div>
        </div>

        <!-- Password Field -->
        <div class="form-field">
          <label class="field-label">Password</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input
              v-model="credentials.password"
              :type="showPassword ? 'text' : 'password'"
              class="field-input"
              placeholder="Enter your password"
              autocomplete="current-password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
              </svg>
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <transition name="fade">
          <div v-if="errorMessage" class="error-alert">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>{{ errorMessage }}</span>
          </div>
        </transition>

        <!-- Submit Button -->
        <button
          type="submit"
          class="login-button"
          :disabled="isLoading"
        >
          <svg v-if="!isLoading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
            <polyline points="10 17 15 12 10 7"></polyline>
            <line x1="15" y1="12" x2="3" y2="12"></line>
          </svg>
          <span v-if="!isLoading">Sign In</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>

      <!-- Footer Info -->
      <div class="login-footer">
        <div class="footer-divider"></div>
        <div class="footer-info">
          <p class="info-label">Default credentials:</p>
          <p class="info-value"><strong>admin</strong> / Check .env file</p>
        </div>
      </div>
    </div>

    <!-- Decorative Elements -->
    <div class="bg-decoration decoration-1"></div>
    <div class="bg-decoration decoration-2"></div>
    <div class="bg-decoration decoration-3"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  username: '',
  password: ''
})

const errorMessage = ref('')
const isLoading = ref(false)
const showPassword = ref(false)

const handleLogin = async () => {
  if (isLoading.value) return

  errorMessage.value = ''
  isLoading.value = true

  try {
    await authStore.login(credentials.value.username, credentials.value.password)
    router.push('/')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Invalid username or password'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* Decorative Background */
.bg-decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.15;
  pointer-events: none;
}

.decoration-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  top: -200px;
  right: -100px;
}

.decoration-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  bottom: -150px;
  left: -100px;
}

.decoration-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.login-container {
  width: 100%;
  max-width: 440px;
  background: var(--bg-secondary);
  border-radius: 20px;
  border: 1px solid var(--border-primary);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 48px;
  position: relative;
  z-index: 1;
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo-icon {
  font-size: 32px;
  line-height: 1;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-secondary);
  pointer-events: none;
}

.field-input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
}

.field-input::placeholder {
  color: var(--text-secondary);
  opacity: 0.6;
}

.field-input:focus {
  outline: none;
  border-color: var(--accent-blue);
  background: var(--bg-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: var(--text-primary);
}

/* Error Alert */
.error-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #ef4444;
  font-size: 13px;
}

.error-alert svg {
  flex-shrink: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Login Button */
.login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  font-family: inherit;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Footer */
.login-footer {
  margin-top: 32px;
}

.footer-divider {
  height: 1px;
  background: var(--border-primary);
  margin-bottom: 20px;
}

.footer-info {
  text-align: center;
}

.info-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.info-value {
  font-size: 13px;
  color: var(--text-primary);
  margin: 0;
  font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
}

.info-value strong {
  color: var(--accent-green);
  font-weight: 600;
}

/* Responsive */
@media (max-width: 640px) {
  .login-container {
    padding: 32px 24px;
  }

  .logo-text {
    font-size: 24px;
  }
}
</style>
