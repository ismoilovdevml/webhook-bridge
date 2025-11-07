<template>
  <div class="container">
    <h2 style="margin-bottom: 2rem;">Settings</h2>

    <!-- Webhook URL -->
    <div class="card">
      <h3 class="card-title">Webhook Configuration</h3>
      <p style="margin-bottom: 1rem; color: #718096;">
        Use this URL to configure webhooks in your Git platform (GitLab, GitHub, Bitbucket):
      </p>

      <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
        <input
          :value="webhookUrl"
          readonly
          class="form-input"
          style="font-family: monospace;"
        >
        <button class="btn btn-primary" @click="copyWebhookUrl">Copy</button>
      </div>

      <div style="background: #f7fafc; padding: 1rem; border-radius: 4px;">
        <h4 style="margin-bottom: 0.5rem;">Setup Instructions:</h4>
        <ol style="padding-left: 1.5rem; color: #4a5568;">
          <li>Copy the webhook URL above</li>
          <li>Go to your Git repository settings</li>
          <li>Navigate to Webhooks section</li>
          <li>Add new webhook and paste the URL</li>
          <li>Select events you want to receive</li>
          <li>Save the webhook</li>
        </ol>
      </div>
    </div>

    <!-- System Info -->
    <div class="card">
      <h3 class="card-title">System Information</h3>
      <table class="table">
        <tbody>
          <tr>
            <td><strong>Service</strong></td>
            <td>Webhook Bridge</td>
          </tr>
          <tr>
            <td><strong>Version</strong></td>
            <td>1.0.0</td>
          </tr>
          <tr>
            <td><strong>Status</strong></td>
            <td><span class="badge badge-success">Running</span></td>
          </tr>
          <tr>
            <td><strong>Supported Platforms</strong></td>
            <td>GitLab, GitHub, Bitbucket</td>
          </tr>
          <tr>
            <td><strong>Supported Providers</strong></td>
            <td>Telegram, Slack, Mattermost, Discord</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- API Documentation -->
    <div class="card">
      <h3 class="card-title">API Documentation</h3>
      <p style="margin-bottom: 1rem; color: #718096;">
        Access the interactive API documentation:
      </p>
      <div style="display: flex; gap: 0.5rem;">
        <a :href="`${apiUrl}/docs`" target="_blank" class="btn btn-primary" style="text-decoration: none;">
          Swagger UI
        </a>
        <a :href="`${apiUrl}/redoc`" target="_blank" class="btn btn-secondary" style="text-decoration: none;">
          ReDoc
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const apiUrl = computed(() => {
  return window.location.origin
})

const webhookUrl = computed(() => {
  return `${apiUrl.value}/api/webhook/git`
})

function copyWebhookUrl() {
  navigator.clipboard.writeText(webhookUrl.value)
  alert('Webhook URL copied to clipboard!')
}
</script>
