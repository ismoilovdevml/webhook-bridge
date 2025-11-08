<template>
  <div class="container">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <div class="logo">Webhook Bridge</div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-label">Providers</span>
            <span class="stat-value">{{ providers.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Events Today</span>
            <span class="stat-value">{{ stats.eventsToday || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Success Rate</span>
            <span class="stat-value">{{ stats.successRate || 0 }}%</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-icon" @click="refreshData" title="Refresh">
          🔄
        </button>
        <button class="btn btn-primary" @click="showAddProvider">
          + Add Provider
        </button>
      </div>
    </header>

    <!-- Main Content - 3 Column Grid -->
    <div class="main-content">
      <!-- Left Panel - Providers -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">Notification Providers</span>
        </div>
        <div class="panel-content">
          <div v-if="providers.length === 0" class="empty-state">
            <div class="empty-icon">📢</div>
            <div class="empty-text">No Providers</div>
            <div class="empty-subtext">Add your first provider</div>
          </div>
          <div v-else class="provider-list">
            <div
              v-for="provider in providers"
              :key="provider.id"
              class="provider-item"
              :class="{ active: selectedProvider?.id === provider.id }"
              @click="selectProvider(provider)"
            >
              <div class="provider-icon">
                {{ getProviderIcon(provider.type) }}
              </div>
              <div class="provider-info">
                <div class="provider-name">{{ provider.name }}</div>
                <div class="provider-status">{{ provider.type }}</div>
              </div>
              <div class="provider-actions">
                <label class="toggle-switch" @click.stop>
                  <input
                    type="checkbox"
                    class="toggle-input"
                    :checked="provider.active"
                    @change="toggleProvider(provider)"
                  />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Panel - Provider Config / Dashboard -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">
            {{ selectedProvider ? 'Provider Configuration' : 'Dashboard' }}
          </span>
          <button
            v-if="selectedProvider"
            class="btn btn-small btn-secondary"
            @click="selectedProvider = null"
          >
            ← Back
          </button>
        </div>
        <div class="panel-content">
          <!-- Provider Config Form -->
          <div v-if="selectedProvider">
            <div class="form-group">
              <label class="form-label">Provider Name</label>
              <input
                v-model="selectedProvider.name"
                type="text"
                class="form-input"
                placeholder="My Telegram Channel"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Type</label>
              <select v-model="selectedProvider.type" class="form-select" disabled>
                <option value="telegram">Telegram</option>
                <option value="slack">Slack</option>
                <option value="discord">Discord</option>
                <option value="mattermost">Mattermost</option>
                <option value="email">Email</option>
              </select>
            </div>

            <div v-if="selectedProvider.type === 'telegram'">
              <div class="form-group">
                <label class="form-label">Bot Token</label>
                <input
                  v-model="selectedProvider.config.bot_token"
                  type="password"
                  class="form-input"
                  placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Chat ID</label>
                <input
                  v-model="selectedProvider.config.chat_id"
                  type="text"
                  class="form-input"
                  placeholder="-100123456789"
                />
              </div>
            </div>

            <div v-if="selectedProvider.type === 'slack'">
              <div class="form-group">
                <label class="form-label">Webhook URL</label>
                <input
                  v-model="selectedProvider.config.webhook_url"
                  type="text"
                  class="form-input"
                  placeholder="https://hooks.slack.com/services/..."
                />
              </div>
            </div>

            <div v-if="selectedProvider.type === 'discord'">
              <div class="form-group">
                <label class="form-label">Webhook URL</label>
                <input
                  v-model="selectedProvider.config.webhook_url"
                  type="text"
                  class="form-input"
                  placeholder="https://discord.com/api/webhooks/..."
                />
              </div>
            </div>

            <div class="form-group">
              <button class="btn btn-primary" @click="saveProvider" style="width: 100%">
                💾 Save Changes
              </button>
            </div>
            <div class="form-group">
              <button class="btn btn-secondary" @click="deleteProvider" style="width: 100%">
                🗑️ Delete Provider
              </button>
            </div>
          </div>

          <!-- Dashboard View -->
          <div v-else>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px">
              <div style="background: var(--bg-secondary); padding: 20px; border-radius: 12px">
                <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px">TOTAL EVENTS</div>
                <div style="font-size: 32px; font-weight: 700; color: var(--apple-blue)">{{ stats.totalEvents || 0 }}</div>
              </div>
              <div style="background: var(--bg-secondary); padding: 20px; border-radius: 12px">
                <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px">ACTIVE PROVIDERS</div>
                <div style="font-size: 32px; font-weight: 700; color: var(--apple-green)">{{ activeProvidersCount }}</div>
              </div>
            </div>

            <div style="background: var(--bg-secondary); padding: 20px; border-radius: 12px">
              <div style="font-size: 13px; font-weight: 600; margin-bottom: 12px">Webhook URL</div>
              <div style="background: var(--bg-primary); padding: 12px; border-radius: 8px; font-family: monospace; font-size: 12px; color: var(--apple-blue)">
                {{ webhookUrl }}
              </div>
              <button class="btn btn-secondary btn-small" @click="copyWebhookUrl" style="margin-top: 12px">
                📋 Copy URL
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel - Recent Events -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">Recent Events</span>
        </div>
        <div class="panel-content">
          <div v-if="events.length === 0" class="empty-state">
            <div class="empty-icon">📬</div>
            <div class="empty-text">No Events</div>
            <div class="empty-subtext">Waiting for webhooks</div>
          </div>
          <div v-else class="event-list">
            <div
              v-for="event in events"
              :key="event.id"
              class="event-item"
              :class="event.status"
            >
              <div class="event-header">
                <span class="event-platform">{{ event.platform?.toUpperCase() }}</span>
                <span class="event-time">{{ formatTime(event.created_at) }}</span>
              </div>
              <div class="event-project">{{ event.project }}</div>
              <div class="event-meta">
                <span>{{ event.event_type }}</span>
                <span>•</span>
                <span>{{ event.author }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Provider Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">Add New Provider</div>
        <div class="form-group">
          <label class="form-label">Provider Name</label>
          <input
            v-model="newProvider.name"
            type="text"
            class="form-input"
            placeholder="My Notification Channel"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="newProvider.type" class="form-select">
            <option value="telegram">📱 Telegram</option>
            <option value="slack">💬 Slack</option>
            <option value="discord">🎮 Discord</option>
            <option value="mattermost">📨 Mattermost</option>
            <option value="email">📧 Email</option>
          </select>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="createProvider">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

// State
const providers = ref([])
const events = ref([])
const stats = ref({})
const selectedProvider = ref(null)
const showModal = ref(false)
const newProvider = ref({
  name: '',
  type: 'telegram',
  config: {},
  active: true
})

// Computed
const activeProvidersCount = computed(() => {
  return providers.value.filter(p => p.active).length
})

const webhookUrl = computed(() => {
  return `${window.location.origin}/api/webhook/git`
})

// Methods
const getProviderIcon = (type) => {
  const icons = {
    telegram: '📱',
    slack: '💬',
    discord: '🎮',
    mattermost: '📨',
    email: '📧'
  }
  return icons[type] || '📡'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

const loadProviders = async () => {
  try {
    const response = await api.get('/providers')
    providers.value = response.data
  } catch {
    // Error loading providers - handled silently
  }
}

const loadEvents = async () => {
  try {
    const response = await api.get('/events?limit=20')
    events.value = response.data.events || []
  } catch {
    // Error loading events - handled silently
  }
}

const loadStats = async () => {
  try {
    const response = await api.get('/dashboard/stats')
    stats.value = response.data
  } catch {
    // Error loading stats - handled silently
  }
}

const refreshData = async () => {
  await Promise.all([loadProviders(), loadEvents(), loadStats()])
}

const selectProvider = (provider) => {
  selectedProvider.value = { ...provider }
}

const toggleProvider = async (provider) => {
  try {
    await api.patch(`/providers/${provider.id}`, {
      active: !provider.active
    })
    await loadProviders()
  } catch {
    // Error toggling provider - handled silently
  }
}

const showAddProvider = () => {
  newProvider.value = {
    name: '',
    type: 'telegram',
    config: {},
    active: true
  }
  showModal.value = true
}

const createProvider = async () => {
  try {
    await api.post('/providers', newProvider.value)
    showModal.value = false
    await loadProviders()
  } catch {
    // Error creating provider - handled silently
  }
}

const saveProvider = async () => {
  try {
    await api.put(`/providers/${selectedProvider.value.id}`, selectedProvider.value)
    selectedProvider.value = null
    await loadProviders()
  } catch {
    // Error saving provider - handled silently
  }
}

const deleteProvider = async () => {
  if (!confirm('Are you sure you want to delete this provider?')) return
  try {
    await api.delete(`/providers/${selectedProvider.value.id}`)
    selectedProvider.value = null
    await loadProviders()
  } catch {
    // Error deleting provider - handled silently
  }
}

const copyWebhookUrl = () => {
  navigator.clipboard.writeText(webhookUrl.value)
  alert('Webhook URL copied to clipboard!')
}

// Lifecycle
onMounted(() => {
  refreshData()
  // Auto-refresh events every 30 seconds
  setInterval(() => {
    loadEvents()
    loadStats()
  }, 30000)
})
</script>
