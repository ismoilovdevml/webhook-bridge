<template>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h2>Events Log</h2>
      <div style="display: flex; gap: 0.5rem;">
        <button class="btn btn-secondary" @click="refreshEvents">Refresh</button>
        <button class="btn btn-danger" @click="clearAllEvents">Clear All</button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="grid grid-4">
        <div class="form-group">
          <label class="form-label">Platform</label>
          <select v-model="filters.platform" @change="applyFilters" class="form-select">
            <option value="">All</option>
            <option value="gitlab">GitLab</option>
            <option value="github">GitHub</option>
            <option value="bitbucket">Bitbucket</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Status</label>
          <select v-model="filters.status" @change="applyFilters" class="form-select">
            <option value="">All</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Event Type</label>
          <input v-model="filters.event_type" @input="applyFilters" class="form-input" placeholder="push, merge_request...">
        </div>

        <div class="form-group">
          <label class="form-label">Project</label>
          <input v-model="filters.project" @input="applyFilters" class="form-input" placeholder="Search project...">
        </div>
      </div>
    </div>

    <!-- Events Table -->
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="card">
      <table class="table" v-if="events.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Platform</th>
            <th>Event Type</th>
            <th>Project</th>
            <th>Author</th>
            <th>Branch</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="event in events" :key="event.id">
            <td>{{ event.id }}</td>
            <td><span class="badge badge-info">{{ event.platform }}</span></td>
            <td>{{ event.event_type }}</td>
            <td>{{ event.project }}</td>
            <td>{{ event.author }}</td>
            <td>{{ event.branch || '-' }}</td>
            <td>
              <span :class="['badge', getStatusClass(event.status)]">
                {{ event.status }}
              </span>
            </td>
            <td>{{ formatDate(event.created_at) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else style="text-align: center; color: #718096; padding: 2rem;">No events found</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEventsStore } from '../stores/events'

const eventsStore = useEventsStore()

const filters = ref({
  platform: '',
  event_type: '',
  status: '',
  project: ''
})

const events = computed(() => eventsStore.events)
const loading = computed(() => eventsStore.loading)
const error = computed(() => eventsStore.error)

onMounted(() => {
  eventsStore.fetchEvents()
  eventsStore.fetchStats()
})

function applyFilters() {
  const params = {}
  if (filters.value.platform) params.platform = filters.value.platform
  if (filters.value.event_type) params.event_type = filters.value.event_type
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.project) params.project = filters.value.project

  eventsStore.fetchEvents(params)
}

function refreshEvents() {
  eventsStore.fetchEvents()
  eventsStore.fetchStats()
}

async function clearAllEvents() {
  if (confirm('Are you sure you want to clear all events?')) {
    try {
      await eventsStore.clearEvents()
      alert('Events cleared successfully!')
    } catch (error) {
      alert('Failed to clear events: ' + error.message)
    }
  }
}

function getStatusClass(status) {
  return {
    success: 'badge-success',
    failed: 'badge-danger',
    pending: 'badge-warning'
  }[status] || 'badge-info'
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString()
}
</script>
