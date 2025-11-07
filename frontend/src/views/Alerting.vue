<template>
  <div>
    <div style="margin-bottom: 2rem;">
      <h1 style="font-size: 2rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
        <span>🔔</span> Alerting & Notifications
      </h1>
      <p style="color: var(--text-secondary);">Configure multi-channel alerts for pipeline events • {{ providers.filter(p => p.active).length }} channels enabled</p>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" :class="{ active: currentTab === 'webhook' }" @click="currentTab = 'webhook'">
        <span>🔧</span> Webhook Setup <span v-if="currentTab === 'webhook'">⚡</span>
      </button>
      <button class="tab" :class="{ active: currentTab === 'channels' }" @click="currentTab = 'channels'">
        <span>⚙️</span> Channels ({{ providers.length }})
      </button>
      <button class="tab" :class="{ active: currentTab === 'history' }" @click="currentTab = 'history'">
        <span>🕐</span> History
      </button>
    </div>

    <!-- Webhook Setup Tab -->
    <div v-if="currentTab === 'webhook'" class="card">
      <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
        <div class="provider-icon" style="background: rgba(249, 115, 22, 0.1); color: var(--accent-primary);">
          <span>🔧</span>
        </div>
        <div>
          <h3 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.25rem;">GitLab Webhook Setup</h3>
          <p style="color: var(--text-secondary); font-size: 0.875rem;">Real-time alerts using GitLab webhooks (instant notifications)</p>
        </div>
      </div>

      <div class="card" style="background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3);">
        <h4 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
          <span>✅</span> Why use webhooks?
        </h4>
        <ul style="list-style: none; padding: 0;">
          <li style="margin-bottom: 0.5rem;">⚡ <strong>Instant alerts</strong> - No delay, get notified immediately</li>
          <li style="margin-bottom: 0.5rem;">🎯 <strong>Accurate</strong> - GitLab sends event directly to us</li>
          <li style="margin-bottom: 0.5rem;">📊 <strong>Efficient</strong> - No polling, saves resources</li>
          <li>📦 <strong>Complete data</strong> - Full pipeline information</li>
        </ul>
      </div>

      <h3 style="margin: 2rem 0 1rem;">Your Webhook URL</h3>
      <div class="webhook-url-box">
        <span class="webhook-url-text">{{ webhookUrl }}</span>
        <button class="btn btn-primary btn-sm" @click="copyWebhookUrl">
          📋 Copy
        </button>
      </div>

      <div class="card">
        <h4 style="margin-bottom: 1rem;">☑️ Setup Instructions</h4>
        <ol style="padding-left: 1.5rem; color: var(--text-secondary); line-height: 2;">
          <li><strong>Go to your GitLab project</strong><br><span style="font-size: 0.875rem;">Settings → Webhooks</span></li>
          <li><strong>Paste the webhook URL above</strong><br><span style="font-size: 0.875rem;">In the "URL" field</span></li>
          <li><strong>Select "Pipeline events" trigger</strong><br><span style="font-size: 0.875rem;">Check only "Pipeline events"</span></li>
          <li><strong>Click "Add webhook"</strong><br><span style="font-size: 0.875rem;">Done! Test it by running a pipeline</span></li>
        </ol>
      </div>
    </div>

    <!-- Channels Tab -->
    <div v-if="currentTab === 'channels'" class="provider-layout">
      <div class="provider-sidebar">
        <div
          v-for="type in providerTypes"
          :key="type.id"
          class="provider-item"
          :class="{ active: selectedProvider === type.id }"
          @click="selectedProvider = type.id"
        >
          <div class="provider-icon" :style="{ background: type.color + '20', color: type.color }">
            <span>{{ type.icon }}</span>
          </div>
          <div class="provider-info">
            <div class="provider-name">{{ type.name }}</div>
            <div class="provider-status">{{ getProviderStatus(type.id) }}</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="font-size: 1.5rem;">{{ getCurrentProviderIcon() }}</span>
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
import { ref, computed, onMounted } from 'vue'
import { useProvidersStore } from '../stores/providers'
import { useEventsStore } from '../stores/events'
import api from '../services/api'

const providersStore = useProvidersStore()
const eventsStore = useEventsStore()

const currentTab = ref('webhook')
const selectedProvider = ref('telegram')
const configData = ref({})
const searchQuery = ref('')

const providers = computed(() => providersStore.providers)
const events = computed(() => eventsStore.events)
const stats = computed(() => eventsStore.stats)

const webhookUrl = computed(() => `${window.location.origin}/api/webhook/git`)

const providerTypes = [
  { id: 'telegram', name: 'Telegram', icon: '✈️', color: '#3b82f6' },
  { id: 'slack', name: 'Slack', icon: '#️⃣', color: '#8b5cf6' },
  { id: 'discord', name: 'Discord', icon: '🎮', color: '#6366f1' },
  { id: 'email', name: 'Email', icon: '📧', color: '#64748b' },
  { id: 'webhook', name: 'Webhook', icon: '🔗', color: '#78716c' },
]

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
  return providerTypes.find(p => p.id === selectedProvider.value)?.icon || '🔧'
}

function getCurrentProviderName() {
  return providerTypes.find(p => p.id === selectedProvider.value)?.name || 'Provider'
}

function copyWebhookUrl() {
  navigator.clipboard.writeText(webhookUrl.value)
  alert('Webhook URL copied to clipboard!')
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
    alert('Configuration saved successfully!')
  } catch (error) {
    alert('Failed to save configuration: ' + error.message)
  }
}

async function testConnection() {
  try {
    const provider = providers.value.find(p => p.type === selectedProvider.value)
    if (provider) {
      const result = await api.testProvider(provider.id)
      alert(result.message || 'Test successful!')
    } else {
      alert('Please save configuration first')
    }
  } catch (error) {
    alert('Test failed: ' + error.message)
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
