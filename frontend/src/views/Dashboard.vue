<template>
  <div class="container">
    <h2 style="margin-bottom: 2rem;">Dashboard</h2>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else>
      <!-- Stats Grid -->
      <div class="grid grid-4" style="margin-bottom: 2rem;">
        <div class="stat-card">
          <div class="stat-value">{{ stats?.providers?.total || 0 }}</div>
          <div class="stat-label">Total Providers</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);">
          <div class="stat-value">{{ stats?.events?.total || 0 }}</div>
          <div class="stat-label">Total Events</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);">
          <div class="stat-value">{{ stats?.events?.last_24h || 0 }}</div>
          <div class="stat-label">Events (24h)</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);">
          <div class="stat-value">{{ stats?.events?.success_rate || 0 }}%</div>
          <div class="stat-label">Success Rate</div>
        </div>
      </div>

      <!-- Recent Events -->
      <div class="card">
        <h3 class="card-title">Recent Events</h3>
        <table class="table" v-if="recentEvents.length">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Type</th>
              <th>Project</th>
              <th>Author</th>
              <th>Status</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in recentEvents" :key="event.id">
              <td><span class="badge badge-info">{{ event.platform }}</span></td>
              <td>{{ event.event_type }}</td>
              <td>{{ event.project }}</td>
              <td>{{ event.author }}</td>
              <td>
                <span :class="['badge', event.status === 'success' ? 'badge-success' : 'badge-danger']">
                  {{ event.status }}
                </span>
              </td>
              <td>{{ formatDate(event.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else style="text-align: center; color: #718096;">No events yet</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard'

const dashboardStore = useDashboardStore()

const stats = computed(() => dashboardStore.stats)
const recentEvents = computed(() => dashboardStore.recentEvents)
const loading = computed(() => dashboardStore.loading)
const error = computed(() => dashboardStore.error)

onMounted(() => {
  dashboardStore.fetchDashboardData()
})

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString()
}
</script>
