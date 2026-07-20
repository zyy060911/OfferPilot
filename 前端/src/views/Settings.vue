<template>
  <AppLayout>
    <div class="settings-layout">
      <!-- Left Nav -->
      <div class="settings-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['nav-item', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <span class="nav-icon" v-html="tab.icon"></span>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- Right Content -->
      <div class="settings-content">
        <!-- General -->
        <div v-if="activeTab === 'general'" class="card">
          <h2 class="card-title">通用设置</h2>

          <div class="setting-group">
            <label class="setting-label">头像</label>
            <div class="avatar-row">
              <div class="avatar-preview"><span>张</span></div>
              <button class="btn-outline">更换头像</button>
            </div>
          </div>

          <div class="setting-row">
            <div class="setting-group">
              <label class="setting-label">昵称</label>
              <input type="text" class="setting-input" value="张同学" />
            </div>
            <div class="setting-group">
              <label class="setting-label">学校/公司</label>
              <input type="text" class="setting-input" value="某985高校" />
            </div>
          </div>

          <div class="setting-group">
            <label class="setting-label">通知偏好</label>
            <div class="toggle-list">
              <div class="toggle-item" v-for="t in toggles" :key="t.key">
                <div>
                  <span class="toggle-name">{{ t.name }}</span>
                  <span class="toggle-desc">{{ t.desc }}</span>
                </div>
                <button :class="['toggle-switch', { on: t.value }]" @click="t.value = !t.value">
                  <span class="toggle-knob"></span>
                </button>
              </div>
            </div>
          </div>

          <button class="btn-primary" @click="saveSettings">保存更改</button>
        </div>

        <!-- Account -->
        <div v-if="activeTab === 'account'" class="card">
          <h2 class="card-title">账号安全</h2>

          <div class="setting-group">
            <label class="setting-label">修改密码</label>
            <div class="password-fields">
              <input type="password" class="setting-input" placeholder="当前密码" />
              <input type="password" class="setting-input" placeholder="新密码（至少 8 位）" />
              <input type="password" class="setting-input" placeholder="确认新密码" />
            </div>
            <button class="btn-outline" style="margin-top: var(--space-3)">更新密码</button>
          </div>

          <div class="setting-group">
            <label class="setting-label">绑定手机</label>
            <div class="bind-row">
              <span class="bind-value">138****8888</span>
              <button class="btn-text">更换</button>
            </div>
          </div>

          <div class="setting-group">
            <label class="setting-label">绑定邮箱</label>
            <div class="bind-row">
              <span class="bind-value">zhang@example.com</span>
              <button class="btn-text">更换</button>
            </div>
          </div>

          <div class="danger-zone">
            <h3 class="danger-title">危险操作</h3>
            <div class="danger-item">
              <div>
                <span class="danger-name">注销账号</span>
                <span class="danger-desc">所有数据将被永久删除，无法恢复</span>
              </div>
              <button class="btn-danger">注销账号</button>
            </div>
          </div>
        </div>

        <!-- Appearance -->
        <div v-if="activeTab === 'appearance'" class="card">
          <h2 class="card-title">外观设置</h2>

          <div class="setting-group">
            <label class="setting-label">主题</label>
            <div class="theme-options">
              <button :class="['theme-btn', { active: theme === 'light' }]" @click="theme = 'light'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                </svg>
                浅色
              </button>
              <button :class="['theme-btn', { active: theme === 'dark' }]" @click="theme = 'dark'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
                深色
              </button>
              <button :class="['theme-btn', { active: theme === 'auto' }]" @click="theme = 'auto'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                跟随系统
              </button>
            </div>
          </div>

          <div class="setting-group">
            <label class="setting-label">语言</label>
            <select class="setting-select">
              <option>简体中文</option>
              <option>English</option>
            </select>
          </div>
        </div>

        <!-- Data -->
        <div v-if="activeTab === 'data'" class="card">
          <h2 class="card-title">数据管理</h2>

          <div class="setting-group">
            <label class="setting-label">数据导出</label>
            <p class="setting-desc">导出你的所有面试记录和个人数据</p>
            <div class="export-row">
              <button class="btn-outline">导出 JSON</button>
              <button class="btn-outline">导出 CSV</button>
            </div>
          </div>

          <div class="setting-group">
            <label class="setting-label">存储使用</label>
            <div class="storage-bar">
              <div class="storage-fill" style="width: 35%"></div>
            </div>
            <div class="storage-info">
              <span>已使用 350 MB / 1 GB</span>
              <span class="storage-percent">35%</span>
            </div>
          </div>

          <div class="setting-group">
            <label class="setting-label">清除缓存</label>
            <p class="setting-desc">清除本地缓存的面试数据和临时文件</p>
            <button class="btn-outline btn-warning">清除缓存</button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'

const activeTab = ref('general')
const theme = ref('light')

const tabs = [
  { id: 'general', label: '通用设置', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>' },
  { id: 'account', label: '账号安全', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>' },
  { id: 'appearance', label: '外观', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>' },
  { id: 'data', label: '数据管理', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>' },
]

const toggles = reactive([
  { key: 'reminder', name: '面试提醒', desc: '在预约面试前 30 分钟提醒你', value: true },
  { key: 'report', name: '每周报告', desc: '每周发送练习总结和能力趋势', value: true },
  { key: 'features', name: '新功能通知', desc: '产品更新和新功能上线通知', value: false },
])

function saveSettings() {
  // Save logic
}
</script>

<style scoped>
.settings-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: var(--space-6);
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-8) 0 var(--space-16);
}

.settings-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--neutral-600);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
  text-align: left;
  position: relative;
}

.nav-item:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.nav-item.active {
  background: var(--accent-50);
  color: var(--accent-700);
  font-weight: 500;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent-500);
  border-radius: var(--radius-full);
}

.nav-icon {
  display: flex;
  align-items: center;
}

.card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  animation: fade-in-up 0.3s var(--ease-out-expo);
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--neutral-900);
  margin-bottom: var(--space-6);
}

.setting-group {
  margin-bottom: var(--space-6);
}

.setting-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-700);
  margin-bottom: var(--space-2);
}

.setting-desc {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-bottom: var(--space-3);
}

.setting-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.setting-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  color: var(--neutral-900);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  outline: none;
  transition: border-color var(--duration-normal), box-shadow var(--duration-normal);
}

.setting-input:focus {
  border-color: var(--accent-400);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.setting-input::placeholder {
  color: var(--neutral-400);
}

.setting-select {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  color: var(--neutral-900);
  font-size: var(--text-sm);
  outline: none;
  transition: border-color var(--duration-normal);
}

.setting-select:focus {
  border-color: var(--accent-400);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* Avatar */
.avatar-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.avatar-preview {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--accent-500), var(--accent-600));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xl);
  font-weight: 700;
  color: white;
}

/* Password */
.password-fields {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Bind */
.bind-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-primary);
  border-radius: var(--radius-md);
}

.bind-value {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--neutral-600);
}

/* Toggle */
.toggle-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-primary);
  border-radius: var(--radius-md);
}

.toggle-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-800);
}

.toggle-desc {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.toggle-switch {
  width: 44px;
  height: 24px;
  border-radius: var(--radius-full);
  border: none;
  background: var(--neutral-300);
  cursor: pointer;
  position: relative;
  transition: background var(--duration-normal);
  flex-shrink: 0;
}

.toggle-switch.on {
  background: var(--accent-500);
}

.toggle-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  transition: transform var(--duration-normal);
  box-shadow: var(--shadow-sm);
}

.toggle-switch.on .toggle-knob {
  transform: translateX(20px);
}

/* Theme */
.theme-options {
  display: flex;
  gap: var(--space-3);
}

.theme-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  background: var(--surface-elevated);
  color: var(--neutral-600);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-normal);
}

.theme-btn:hover {
  border-color: var(--neutral-300);
}

.theme-btn.active {
  border-color: var(--accent-500);
  background: var(--accent-50);
  color: var(--accent-700);
}

/* Danger */
.danger-zone {
  margin-top: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1px solid rgba(239, 68, 68, 0.2);
}

.danger-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: #ef4444;
  margin-bottom: var(--space-4);
}

.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: rgba(239, 68, 68, 0.03);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: var(--radius-md);
}

.danger-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-800);
  margin-bottom: 2px;
}

.danger-desc {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  background: var(--accent-500);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-normal);
  box-shadow: var(--shadow-accent);
}

.btn-primary:hover {
  background: var(--accent-600);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  color: var(--neutral-700);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.btn-outline:hover {
  border-color: var(--neutral-300);
  background: var(--neutral-50);
}

.btn-warning {
  color: #d97706;
  border-color: rgba(217, 119, 6, 0.3);
}

.btn-warning:hover {
  background: rgba(217, 119, 6, 0.05);
  border-color: rgba(217, 119, 6, 0.5);
}

.btn-text {
  background: none;
  border: none;
  color: var(--accent-600);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: color var(--duration-fast);
}

.btn-text:hover {
  color: var(--accent-500);
}

.btn-danger {
  padding: var(--space-2) var(--space-4);
  border: 1.5px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.05);
  color: #ef4444;
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* Export */
.export-row {
  display: flex;
  gap: var(--space-3);
}

/* Storage */
.storage-bar {
  height: 8px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.storage-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-400), var(--accent-500));
  border-radius: var(--radius-full);
}

.storage-info {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.storage-percent {
  font-family: var(--font-mono);
  color: var(--accent-500);
  font-weight: 600;
}

@media (max-width: 768px) {
  .settings-layout { grid-template-columns: 1fr; }
  .settings-nav {
    flex-direction: row;
    overflow-x: auto;
    gap: var(--space-1);
    padding-bottom: var(--space-2);
  }
  .nav-item { white-space: nowrap; }
  .nav-item.active::before { display: none; }
  .setting-row { grid-template-columns: 1fr; }
  .theme-options { flex-direction: column; }
  .export-row { flex-direction: column; }
}
</style>
