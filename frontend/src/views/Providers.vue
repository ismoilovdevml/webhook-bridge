<template>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h2>Providers</h2>
      <button class="btn btn-primary" @click="showCreateModal = true">+ Add Provider</button>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="grid grid-3">
      <div v-for="provider in providers" :key="provider.id" class="card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div>
            <h3>{{ provider.name }}</h3>
            <span class="badge badge-info">{{ provider.type }}</span>
            <span :class="['badge', provider.active ? 'badge-success' : 'badge-danger']" style="margin-left: 0.5rem;">
              {{ provider.active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
          <button class="btn btn-secondary" @click="testProvider(provider.id)">Test</button>
          <button class="btn btn-danger" @click="deleteProvider(provider.id)">Delete</button>
        </div>
      </div>
    </div>

    <!-- Create Provider Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Add Provider</h3>
          <button class="modal-close" @click="showCreateModal = false">&times;</button>
        </div>

        <form @submit.prevent="createProvider">
          <div class="form-group">
            <label class="form-label">Name</label>
            <input v-model="newProvider.name" class="form-input" required>
          </div>

          <div class="form-group">
            <label class="form-label">Type</label>
            <select v-model="newProvider.type" class="form-select" required>
              <option value="">Select type</option>
              <option value="telegram">Telegram</option>
              <option value="slack">Slack</option>
              <option value="mattermost">Mattermost</option>
              <option value="discord">Discord</option>
            </select>
          </div>

          <div v-if="newProvider.type === 'telegram'" class="form-group">
            <label class="form-label">Bot Token</label>
            <input v-model="newProvider.config.bot_token" class="form-input" required>
            <label class="form-label" style="margin-top: 0.5rem;">Chat ID</label>
            <input v-model="newProvider.config.chat_id" class="form-input" required>
          </div>

          <div v-else-if="['slack', 'mattermost', 'discord'].includes(newProvider.type)" class="form-group">
            <label class="form-label">Webhook URL</label>
            <input v-model="newProvider.config.webhook_url" class="form-input" required>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary">Create</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProvidersStore } from '../stores/providers'

const providersStore = useProvidersStore()

const showCreateModal = ref(false)
const newProvider = ref({
  name: '',
  type: '',
  config: {},
  active: true
})

const providers = computed(() => providersStore.providers)
const loading = computed(() => providersStore.loading)
const error = computed(() => providersStore.error)

onMounted(() => {
  providersStore.fetchProviders()
})

async function createProvider() {
  try {
    await providersStore.createProvider(newProvider.value)
    showCreateModal.value = false
    newProvider.value = { name: '', type: '', config: {}, active: true }
    alert('Provider created successfully!')
  } catch (error) {
    alert('Failed to create provider: ' + error.message)
  }
}

async function testProvider(id) {
  try {
    const result = await providersStore.testProvider(id)
    alert(result.message)
  } catch (error) {
    alert('Test failed: ' + error.message)
  }
}

async function deleteProvider(id) {
  if (confirm('Are you sure you want to delete this provider?')) {
    try {
      await providersStore.deleteProvider(id)
      alert('Provider deleted successfully!')
    } catch (error) {
      alert('Failed to delete provider: ' + error.message)
    }
  }
}
</script>
