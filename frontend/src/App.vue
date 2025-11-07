<template>
  <div id="app" class="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <h1>🔗 Webhook Bridge</h1>
      </div>
      <div class="navbar-menu">
        <router-link to="/" class="nav-link">Dashboard</router-link>
        <router-link to="/providers" class="nav-link">Providers</router-link>
        <router-link to="/events" class="nav-link">Events</router-link>
        <router-link to="/settings" class="nav-link">Settings</router-link>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>Webhook Bridge v1.0.0 | Universal Git Notification System</p>
    </footer>
  </div>
</template>

<script setup>
// App component - main layout
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.navbar-brand h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.navbar-menu {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

.nav-link:hover {
  opacity: 0.8;
}

.nav-link.router-link-active {
  border-bottom: 2px solid white;
  padding-bottom: 2px;
}

.main-content {
  flex: 1;
  padding: 2rem;
  background: #f5f7fa;
}

.footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 1rem;
}

.footer p {
  margin: 0;
  font-size: 0.875rem;
}
</style>
