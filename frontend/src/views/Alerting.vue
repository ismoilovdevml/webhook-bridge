<template>
  <div class="container">
    <!-- Toast Notifications -->
    <div class="toast-container">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="toast"
        :class="notification.type"
      >
        <span class="toast-icon">{{ notification.type === 'success' ? '✓' : '✕' }}</span>
        <span class="toast-message">{{ notification.message }}</span>
      </div>
    </div>

    <!-- Header -->
    <div class="header-container">
      <div>
        <h1 style="font-size: 1.5rem; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 700; letter-spacing: -0.02em;">
          <span style="font-size: 1.25rem;">🔔</span> Webhook Bridge
        </h1>
        <p style="color: var(--text-secondary); font-size: 13px;">Configure multi-channel alerts • {{ providers.filter(p => p.active).length }} active</p>
      </div>

      <div class="header-actions">
        <!-- GitHub Link -->
        <a href="https://github.com/ismoilovdevml/webhook-bridge" target="_blank" rel="noopener noreferrer" class="github-link">
          <GitHubIcon :size="20" />
        </a>

        <!-- Theme Toggle -->
        <button class="theme-toggle" @click="toggleTheme" :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
          <div class="theme-toggle-track">
            <div class="theme-toggle-thumb" :class="{ active: !isDarkMode }">
              <span v-if="isDarkMode" class="theme-icon">🌙</span>
              <span v-else class="theme-icon">☀️</span>
            </div>
          </div>
        </button>

        <!-- Logout Button -->
        <button class="logout-btn" @click="showLogoutConfirm = true" title="Logout">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          <span>Logout</span>
        </button>
      </div>
    </div>

    <!-- Logout Confirmation Modal -->
    <ConfirmDialog
      v-model="showLogoutConfirm"
      title="Logout"
      message="Are you sure you want to logout?"
      confirm-text="Logout"
      cancel-text="Cancel"
      variant="danger"
      @confirm="confirmLogout"
    />

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" :class="{ active: currentTab === 'webhook' }" @click="currentTab = 'webhook'">
        Webhook Setup
      </button>
      <button class="tab" :class="{ active: currentTab === 'channels' }" @click="currentTab = 'channels'">
        Channels
      </button>
      <button class="tab" :class="{ active: currentTab === 'history' }" @click="currentTab = 'history'">
        History
      </button>
    </div>

    <!-- Webhook Setup Tab -->
    <div v-if="currentTab === 'webhook'">
      <!-- Webhook URL Card -->
      <div class="card webhook-url-card">
        <h3 class="webhook-url-title">
          <span class="webhook-icon">🔗</span>
          Universal Webhook URL
        </h3>
        <p class="webhook-url-description">Use this URL for GitLab, GitHub, and Bitbucket - automatically detects platform</p>
        <div class="webhook-url-box-new">
          <input type="text" readonly :value="webhookUrl" class="webhook-url-input-new" @click="$event.target.select()">
          <button class="btn-copy-new" @click="copyWebhookUrl()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span>Copy</span>
          </button>
        </div>
      </div>

      <!-- Platform Setup Cards -->
      <div class="platform-cards-grid">
        <!-- GitLab -->
        <div class="platform-card gitlab-card">
          <div class="platform-card-header">
            <div class="platform-icon-large" style="background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);">
              <GitLabIcon :size="36" />
            </div>
            <div class="platform-card-info">
              <h3 class="platform-card-title">GitLab</h3>
              <p class="platform-card-path">Settings → Webhooks</p>
            </div>
          </div>
          <div class="platform-card-steps">
            <div class="platform-step">
              <span class="step-number">1</span>
              <span class="step-text">Select triggers (Push, Merge Request, Issues)</span>
            </div>
            <div class="platform-step">
              <span class="step-number">2</span>
              <span class="step-text">Click "Add webhook" button</span>
            </div>
          </div>
        </div>

        <!-- GitHub -->
        <div class="platform-card github-card">
          <div class="platform-card-header">
            <div class="platform-icon-large" style="background: linear-gradient(135deg, #333 0%, #24292f 100%);">
              <GitHubIcon :size="36" />
            </div>
            <div class="platform-card-info">
              <h3 class="platform-card-title">GitHub</h3>
              <p class="platform-card-path">Settings → Webhooks</p>
            </div>
          </div>
          <div class="platform-card-steps">
            <div class="platform-step">
              <span class="step-number">1</span>
              <span class="step-text">Content type: application/json</span>
            </div>
            <div class="platform-step">
              <span class="step-number">2</span>
              <span class="step-text">Select events & save</span>
            </div>
          </div>
        </div>

        <!-- Bitbucket -->
        <div class="platform-card bitbucket-card">
          <div class="platform-card-header">
            <div class="platform-icon-large" style="background: linear-gradient(135deg, #2684FF 0%, #0052CC 100%);">
              <BitbucketIcon :size="36" />
            </div>
            <div class="platform-card-info">
              <h3 class="platform-card-title">Bitbucket</h3>
              <p class="platform-card-path">Repository → Webhooks</p>
            </div>
          </div>
          <div class="platform-card-steps">
            <div class="platform-step">
              <span class="step-number">1</span>
              <span class="step-text">Select triggers (Push, Pull Request)</span>
            </div>
            <div class="platform-step">
              <span class="step-number">2</span>
              <span class="step-text">Click "Save" button</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Channels Tab -->
    <div v-if="currentTab === 'channels'">
      <!-- Horizontal Provider Tabs -->
      <div class="provider-tabs">
        <button
          v-for="type in providerTypes"
          :key="type.id"
          class="provider-tab"
          :class="{ active: selectedProvider === type.id, enabled: getProviderStatus(type.id) === 'Enabled' }"
          @click="selectedProvider = type.id"
        >
          <div class="provider-icon-small" :style="{ background: type.bgColor, color: type.color }">
            <component :is="type.icon" :size="24" />
          </div>
          <span class="provider-tab-name">{{ type.name }}</span>
        </button>
      </div>

      <!-- Configuration Card -->
      <div class="card" style="margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="provider-icon" :style="{ background: getCurrentProviderBgColor(), color: getCurrentProviderColor() }">
              <component :is="getCurrentProviderIcon()" :size="28" />
            </div>
            <h3 style="font-size: 1.25rem; font-weight: 600;">{{ getCurrentProviderName() }} Configuration</h3>
          </div>
          <label class="toggle">
            <input type="checkbox" :checked="isProviderEnabled()" @change="toggleProvider">
            <span class="toggle-slider"></span>
          </label>
        </div>

        <!-- Telegram Config -->
        <div v-if="selectedProvider === 'telegram'">
          <div class="form-group">
            <label class="form-label">Bot Token</label>
            <input v-model="configData.bot_token" class="form-input" placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz">
            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">Get from @BotFather</p>
          </div>
          <div class="form-group">
            <label class="form-label">Chat ID</label>
            <input v-model="configData.chat_id" class="form-input" placeholder="-1001234567890">
            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">Use @userinfobot or @getmyid_bot to get your chat ID</p>
          </div>
          <div class="form-group">
            <label class="form-label">Thread ID (Optional)</label>
            <input v-model="configData.thread_id" class="form-input" placeholder="123456">
            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">For Telegram group topics/forums. Leave empty for regular chats</p>
          </div>
        </div>

        <!-- Slack Config -->
        <div v-if="selectedProvider === 'slack'">
          <div class="form-group">
            <label class="form-label">Webhook URL</label>
            <input v-model="configData.webhook_url" class="form-input" placeholder="https://hooks.slack.com/services/...">
          </div>
          <div class="form-group">
            <label class="form-label">Channel (Optional)</label>
            <input v-model="configData.channel" class="form-input" placeholder="#general">
          </div>
        </div>

        <!-- Discord Config -->
        <div v-if="selectedProvider === 'discord'">
          <div class="form-group">
            <label class="form-label">Webhook URL</label>
            <input v-model="configData.webhook_url" class="form-input" placeholder="https://discord.com/api/webhooks/...">
          </div>
        </div>

        <!-- Mattermost Config -->
        <div v-if="selectedProvider === 'mattermost'">
          <div class="form-group">
            <label class="form-label">Webhook URL</label>
            <input v-model="configData.webhook_url" class="form-input" placeholder="https://your-mattermost.com/hooks/...">
          </div>
        </div>

        <!-- Email Config -->
        <div v-if="selectedProvider === 'email'">
          <div class="form-group">
            <label class="form-label">SMTP Host</label>
            <input v-model="configData.smtp_host" class="form-input" placeholder="smtp.gmail.com">
          </div>
          <div class="form-group">
            <label class="form-label">SMTP User</label>
            <input v-model="configData.smtp_user" class="form-input" placeholder="your@email.com">
          </div>
          <div class="form-group">
            <label class="form-label">SMTP Password</label>
            <input v-model="configData.smtp_password" type="password" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">To Emails (comma-separated)</label>
            <input v-model="configData.to_emails" class="form-input" placeholder="user1@example.com, user2@example.com">
          </div>
        </div>

        <div style="display: flex; gap: 0.75rem; margin-top: 2rem;">
          <button class="btn btn-success" @click="saveConfiguration">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>Save Configuration</span>
          </button>
          <button class="btn btn-secondary" @click="testConnection">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
            </svg>
            <span>Test Connection</span>
          </button>
        </div>
      </div>
    </div>

    <!-- History Tab -->
    <div v-if="currentTab === 'history'">
      <div class="stats-grid-compact">
        <div class="stat-card-compact">
          <div class="stat-icon-compact">📊</div>
          <div class="stat-content-compact">
            <div class="stat-label-compact">Total</div>
            <div class="stat-value-compact">{{ stats?.total || 0 }}</div>
          </div>
        </div>
        <div class="stat-card-compact stat-success">
          <div class="stat-icon-compact">✅</div>
          <div class="stat-content-compact">
            <div class="stat-label-compact">Successful</div>
            <div class="stat-value-compact">{{ stats?.success || 0 }}</div>
          </div>
        </div>
        <div class="stat-card-compact stat-danger">
          <div class="stat-icon-compact">❌</div>
          <div class="stat-content-compact">
            <div class="stat-label-compact">Failed</div>
            <div class="stat-value-compact">{{ stats?.failed || 0 }}</div>
          </div>
        </div>
      </div>

      <div class="toolbar-compact">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input v-model="searchQuery" class="form-input" placeholder="Search by project name...">
        </div>
        <button class="btn btn-secondary" @click="refresh">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          <span>Refresh</span>
        </button>
      </div>

      <div v-if="events.length === 0" class="empty-state">
        <div class="empty-icon">🕐</div>
        <div class="empty-text">No Alert History</div>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">No alerts found matching your filters</p>
      </div>

      <div v-else class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Event Type</th>
              <th>Project</th>
              <th>Status</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in events" :key="event.id">
              <td><span class="badge badge-info">{{ event.platform }}</span></td>
              <td>{{ event.event_type }}</td>
              <td>{{ event.project }}</td>
              <td><span :class="['badge', getStatusClass(event.status)]">{{ event.status }}</span></td>
              <td>{{ formatDate(event.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProvidersStore } from '../stores/providers'
import { useEventsStore } from '../stores/events'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

// Import components
import ConfirmDialog from '../components/ConfirmDialog.vue'

// Import icon components
import TelegramIcon from '../components/icons/TelegramIcon.vue'
import SlackIcon from '../components/icons/SlackIcon.vue'
import DiscordIcon from '../components/icons/DiscordIcon.vue'
import MattermostIcon from '../components/icons/MattermostIcon.vue'
import EmailIcon from '../components/icons/EmailIcon.vue'
import GitLabIcon from '../components/icons/GitLabIcon.vue'
import GitHubIcon from '../components/icons/GitHubIcon.vue'
import BitbucketIcon from '../components/icons/BitbucketIcon.vue'

const router = useRouter()
const authStore = useAuthStore()
const providersStore = useProvidersStore()
const eventsStore = useEventsStore()

const currentTab = ref('webhook')
const selectedProvider = ref('telegram')
const configData = ref({})
const searchQuery = ref('')
const notifications = ref([])
const isDarkMode = ref(true)
const showLogoutConfirm = ref(false)

const providers = computed(() => providersStore.providers)
const events = computed(() => eventsStore.events)
const stats = computed(() => eventsStore.stats)

const webhookUrl = computed(() => {
  // Use current origin for production, fallback to env var or localhost for development
  const backendUrl = window.location.origin.includes('localhost')
    ? (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000')
    : window.location.origin
  return `${backendUrl}/api/webhook/git`
})

const providerTypes = [
  { id: 'telegram', name: 'Telegram', icon: TelegramIcon, color: '#0088cc', bgColor: 'rgba(0, 136, 204, 0.1)' },
  { id: 'slack', name: 'Slack', icon: SlackIcon, color: '#611f69', bgColor: 'rgba(97, 31, 105, 0.1)' },
  { id: 'discord', name: 'Discord', icon: DiscordIcon, color: '#5865F2', bgColor: 'rgba(88, 101, 242, 0.1)' },
  { id: 'mattermost', name: 'Mattermost', icon: MattermostIcon, color: '#0058CC', bgColor: 'rgba(0, 88, 204, 0.1)' },
  { id: 'email', name: 'Email', icon: EmailIcon, color: '#ea4335', bgColor: 'rgba(234, 67, 53, 0.1)' }
]

// Watch for provider selection changes
watch(selectedProvider, (newProvider) => {
  if (newProvider) {
    const provider = providers.value.find(p => p.type === newProvider)
    if (provider && provider.config) {
      configData.value = { ...provider.config }
    } else {
      configData.value = {}
    }
  }
})

// Theme management
function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
  const theme = isDarkMode.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

function loadTheme() {
  const savedTheme = localStorage.getItem('theme') || 'dark'
  isDarkMode.value = savedTheme === 'dark'
  document.documentElement.setAttribute('data-theme', savedTheme)
}

onMounted(() => {
  loadTheme()
  providersStore.fetchProviders()
  eventsStore.fetchEvents()
  eventsStore.fetchStats()
})

function getProviderStatus(type) {
  const provider = providers.value.find(p => p.type === type)
  return provider && provider.active ? 'Enabled' : 'Disabled'
}

function isProviderEnabled() {
  const provider = providers.value.find(p => p.type === selectedProvider.value)
  return provider?.active || false
}

function getCurrentProviderIcon() {
  return providerTypes.find(p => p.id === selectedProvider.value)?.icon || TelegramIcon
}

function getCurrentProviderName() {
  return providerTypes.find(p => p.id === selectedProvider.value)?.name || 'Provider'
}

function getCurrentProviderColor() {
  return providerTypes.find(p => p.id === selectedProvider.value)?.color || '#78716c'
}

function getCurrentProviderBgColor() {
  return providerTypes.find(p => p.id === selectedProvider.value)?.bgColor || 'rgba(120, 113, 108, 0.1)'
}

function showNotification(message, type = 'success') {
  const id = Date.now()
  notifications.value.push({ id, message, type })
  setTimeout(() => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }, 4000)
}

function copyWebhookUrl(suffix = '') {
  const fullUrl = webhookUrl.value + suffix
  navigator.clipboard.writeText(fullUrl)
  showNotification('Webhook URL copied to clipboard!', 'success')
}

async function saveConfiguration() {
  try {
    const provider = providers.value.find(p => p.type === selectedProvider.value)
    if (provider) {
      await providersStore.updateProvider(provider.id, { config: configData.value })
    } else {
      await providersStore.createProvider({
        name: getCurrentProviderName(),
        type: selectedProvider.value,
        config: configData.value,
        active: true
      })
    }
    showNotification('Configuration saved successfully!', 'success')
    await providersStore.fetchProviders()
  } catch (error) {
    showNotification('Failed to save configuration: ' + error.message, 'error')
  }
}

async function testConnection() {
  try {
    const provider = providers.value.find(p => p.type === selectedProvider.value)
    if (provider) {
      const result = await api.testProvider(provider.id)
      showNotification(result.message || 'Test successful!', 'success')
    } else {
      showNotification('Please save configuration first', 'error')
    }
  } catch (error) {
    showNotification('Test failed: ' + error.message, 'error')
  }
}

async function toggleProvider() {
  const provider = providers.value.find(p => p.type === selectedProvider.value)
  if (provider) {
    await providersStore.updateProvider(provider.id, { active: !provider.active })
  }
}

function getStatusClass(status) {
  return status === 'success' ? 'badge-success' : 'badge-danger'
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}

async function refresh() {
  await eventsStore.fetchEvents()
  await eventsStore.fetchStats()
}

function confirmLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
