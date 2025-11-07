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

    <div style="margin-bottom: 1rem;">
      <h1 style="font-size: 1.5rem; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 700; letter-spacing: -0.02em;">
        <span style="font-size: 1.25rem;">🔔</span> Webhook Bridge
      </h1>
      <p style="color: var(--text-secondary); font-size: 13px;">Configure multi-channel alerts • {{ providers.filter(p => p.active).length }} active</p>
    </div>

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
      <div class="card" style="margin-bottom: 1rem;">
        <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 0.5rem;">Universal Webhook URL</h3>
        <p style="color: var(--text-secondary); font-size: 12px; margin-bottom: 1rem;">Use this URL for GitLab, GitHub, and Bitbucket - automatically detects platform</p>
        <div class="webhook-url-box">
          <span class="webhook-url-text">{{ webhookUrl }}</span>
          <button class="btn btn-primary btn-sm" @click="copyWebhookUrl()">
            Copy
          </button>
        </div>
      </div>

      <!-- Platform Setup Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
        <!-- GitLab -->
        <div class="card">
          <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <div class="provider-icon" style="background: rgba(252, 109, 38, 0.1); color: #fc6d26; width: 36px; height: 36px;">
              <GitLabIcon :size="20" />
            </div>
            <div>
              <h3 style="font-size: 14px; font-weight: 600; margin: 0;">GitLab</h3>
              <p style="color: var(--text-secondary); font-size: 11px; margin: 0;">Settings → Webhooks</p>
            </div>
          </div>
          <ul style="list-style: none; padding: 0; font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
            <li>• Select triggers (Push, MR, Issues)</li>
            <li>• Click "Add webhook"</li>
          </ul>
        </div>

        <!-- GitHub -->
        <div class="card">
          <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <div class="provider-icon" style="background: rgba(36, 41, 47, 0.1); color: #fff; width: 36px; height: 36px;">
              <GitHubIcon :size="20" />
            </div>
            <div>
              <h3 style="font-size: 14px; font-weight: 600; margin: 0;">GitHub</h3>
              <p style="color: var(--text-secondary); font-size: 11px; margin: 0;">Settings → Webhooks</p>
            </div>
          </div>
          <ul style="list-style: none; padding: 0; font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
            <li>• Content type: application/json</li>
            <li>• Select events & save</li>
          </ul>
        </div>

        <!-- Bitbucket -->
        <div class="card">
          <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <div class="provider-icon" style="background: rgba(33, 110, 225, 0.1); color: #216ee1; width: 36px; height: 36px;">
              <BitbucketIcon :size="20" />
            </div>
            <div>
              <h3 style="font-size: 14px; font-weight: 600; margin: 0;">Bitbucket</h3>
              <p style="color: var(--text-secondary); font-size: 11px; margin: 0;">Repository → Webhooks</p>
            </div>
          </div>
          <ul style="list-style: none; padding: 0; font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
            <li>• Select triggers (Push, PR)</li>
            <li>• Click "Save"</li>
          </ul>
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
          :class="{ active: selectedProvider === type.id }"
          @click="selectedProvider = type.id"
        >
          <div class="provider-icon-small" :style="{ background: type.bgColor, color: type.color }">
            <component :is="type.icon" :size="20" />
          </div>
          <span>{{ type.name }}</span>
          <span class="provider-badge" :class="{ enabled: getProviderStatus(type.id) === 'Enabled' }">
            {{ getProviderStatus(type.id) === 'Enabled' ? '●' : '○' }}
          </span>
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
          <button class="btn btn-primary" @click="saveConfiguration">
            ✓ Save Configuration
          </button>
          <button class="btn btn-secondary" @click="testConnection">
            🔌 Test Connection
          </button>
        </div>
      </div>
    </div>

    <!-- History Tab -->
    <div v-if="currentTab === 'history'">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon primary">
            <span>📊</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">Total Alerts</div>
            <div class="stat-value">{{ stats?.total || 0 }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon success">
            <span>📈</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">Success Rate</div>
            <div class="stat-value">{{ stats?.success_rate || 0 }}%</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon success">
            <span>✅</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">Successful</div>
            <div class="stat-value">{{ stats?.success || 0 }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon danger">
            <span>❌</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">Failed</div>
            <div class="stat-value">{{ stats?.failed || 0 }}</div>
          </div>
        </div>
      </div>

      <div class="toolbar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input v-model="searchQuery" class="form-input" placeholder="Search by project name...">
        </div>
        <button class="btn btn-secondary">🔍 Filters</button>
        <button class="btn btn-success" @click="refresh">🔄 Refresh</button>
        <button class="btn btn-success">📥 CSV</button>
        <button class="btn btn-primary">📥 JSON</button>
        <button class="btn btn-danger" @click="clearAll">🗑️ Clear All</button>
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
import { useProvidersStore } from '../stores/providers'
import { useEventsStore } from '../stores/events'
import api from '../services/api'

// Import icon components
import TelegramIcon from '../components/icons/TelegramIcon.vue'
import SlackIcon from '../components/icons/SlackIcon.vue'
import DiscordIcon from '../components/icons/DiscordIcon.vue'
import MattermostIcon from '../components/icons/MattermostIcon.vue'
import EmailIcon from '../components/icons/EmailIcon.vue'
import WebhookIcon from '../components/icons/WebhookIcon.vue'
import GitLabIcon from '../components/icons/GitLabIcon.vue'
import GitHubIcon from '../components/icons/GitHubIcon.vue'
import BitbucketIcon from '../components/icons/BitbucketIcon.vue'

const providersStore = useProvidersStore()
const eventsStore = useEventsStore()

const currentTab = ref('webhook')
const selectedProvider = ref('telegram')
const configData = ref({})
const searchQuery = ref('')
const notifications = ref([])

const providers = computed(() => providersStore.providers)
const events = computed(() => eventsStore.events)
const stats = computed(() => eventsStore.stats)

const webhookUrl = computed(() => `${window.location.origin}/api/webhook/git`)

const providerTypes = [
  { id: 'telegram', name: 'Telegram', icon: TelegramIcon, color: '#0088cc', bgColor: 'rgba(0, 136, 204, 0.1)' },
  { id: 'slack', name: 'Slack', icon: SlackIcon, color: '#611f69', bgColor: 'rgba(97, 31, 105, 0.1)' },
  { id: 'discord', name: 'Discord', icon: DiscordIcon, color: '#5865F2', bgColor: 'rgba(88, 101, 242, 0.1)' },
  { id: 'mattermost', name: 'Mattermost', icon: MattermostIcon, color: '#0058CC', bgColor: 'rgba(0, 88, 204, 0.1)' },
  { id: 'email', name: 'Email', icon: EmailIcon, color: '#ea4335', bgColor: 'rgba(234, 67, 53, 0.1)' },
  { id: 'webhook', name: 'Webhook', icon: WebhookIcon, color: '#78716c', bgColor: 'rgba(120, 113, 108, 0.1)' },
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

onMounted(() => {
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
  return providerTypes.find(p => p.id === selectedProvider.value)?.icon || WebhookIcon
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

async function clearAll() {
  if (confirm('Are you sure you want to clear all events?')) {
    await eventsStore.clearEvents()
  }
}
</script>
