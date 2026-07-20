<template>
  <nav class="navbar glass-medium">
    <div class="navbar-inner">
      <router-link to="/" class="logo">
        <div class="logo-icon">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 8C12 8 20 16 20 20C20 24 12 32 12 32" stroke="url(#g1)" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M28 8C28 8 20 16 20 20C20 24 28 32 28 32" stroke="url(#g2)" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="20" cy="20" r="4" fill="url(#g3)"/>
            <defs>
              <linearGradient id="g1" x1="12" y1="8" x2="12" y2="32">
                <stop stop-color="#34d399"/>
                <stop offset="1" stop-color="#059669"/>
              </linearGradient>
              <linearGradient id="g2" x1="28" y1="8" x2="28" y2="32">
                <stop stop-color="#059669"/>
                <stop offset="1" stop-color="#047857"/>
              </linearGradient>
              <radialGradient id="g3" cx="20" cy="20" r="4" gradientUnits="userSpaceOnUse">
                <stop stop-color="#6ee7b7"/>
                <stop offset="1" stop-color="#059669"/>
              </radialGradient>
            </defs>
          </svg>
        </div>
        <span class="logo-text">智面幻境</span>
      </router-link>

      <div class="nav-links">
        <router-link to="/dashboard" class="nav-link">首页</router-link>
        <router-link to="/job-select" class="nav-link">面试准备</router-link>
        <router-link to="/history" class="nav-link">历史记录</router-link>
        <router-link to="/settings" class="nav-link">设置</router-link>
      </div>

      <div class="nav-actions">
        <button class="notification-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span class="notification-dot"></span>
        </button>
        <div class="user-avatar">
          <span>张</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0 var(--space-6);
  height: 64px;
}

.navbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-decoration: none;
}

.logo-icon {
  width: 36px;
  height: 36px;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: var(--tracking-tight);
}

.nav-links {
  display: flex;
  gap: var(--space-1);
}

.nav-link {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  transition: all var(--duration-normal) var(--ease-out);
  text-decoration: none;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--text-primary);
  background: rgba(255,255,255,0.05);
}

.nav-link.router-link-active {
  color: var(--accent-400);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.notification-btn {
  position: relative;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast);
}

.notification-btn:hover {
  color: var(--text-primary);
  background: rgba(255,255,255,0.05);
}

.notification-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: var(--color-error);
  border-radius: 50%;
  border: 2px solid var(--surface-elevated);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--accent-500), var(--accent-600));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: box-shadow var(--duration-normal);
}

.user-avatar:hover {
  box-shadow: var(--shadow-accent);
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
}
</style>
