<template>
  <div class="login-page" @mousemove="onMouseMove">
    <!-- Unified Background -->
    <div class="bg-layer">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-glow" :style="{ left: mouse.x + 'px', top: mouse.y + 'px' }"></div>
    </div>

    <!-- Left: Interactive AI Stage -->
    <div class="stage-panel">
      <div class="stage-content">
        <div class="stage-logo">
          <LogoIcon :size="36" />
          <span class="stage-brand">OfferPilot</span>
        </div>

        <h1 class="stage-title">
          在这里<br />
          <span class="title-accent">练出自信</span>
        </h1>
        <p class="stage-desc">AI 面试官实时追问, 多维能力评估, 让每次练习都接近真实</p>

        <!-- Interactive Scene -->
        <div class="scene">
          <!-- Central AI Orb -->
          <div
            class="ai-orb"
            @mouseenter="orbActive = true"
            @mouseleave="orbActive = false"
            :class="{ active: orbActive }"
          >
            <div class="orb-ring orb-ring-1"></div>
            <div class="orb-ring orb-ring-2"></div>
            <div class="orb-ring orb-ring-3"></div>
            <div class="orb-core">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 2a5 5 0 0 1 5 5v3a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
              </svg>
            </div>
            <span class="orb-label">AI 面试官</span>
          </div>

          <!-- Floating Question Bubbles -->
          <div
            v-for="(q, i) in questionBubbles"
            :key="i"
            class="q-bubble"
            :class="{ popped: q.popped }"
            :style="q.style"
            @mouseenter="popBubble(i)"
          >
            <span class="q-text">{{ q.text }}</span>
            <div v-if="q.popped" class="q-ripple"></div>
          </div>

          <!-- Score Meter -->
          <div
            class="score-meter"
            :class="{ expanded: scoreExpanded }"
            @mouseenter="scoreExpanded = true"
            @mouseleave="scoreExpanded = false"
          >
            <div class="meter-track">
              <div class="meter-fill" :style="{ width: interactionScore + '%' }"></div>
            </div>
            <div class="meter-label">
              <span class="meter-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </span>
              <span class="meter-val">{{ interactionScore }}</span>
              <span class="meter-hint">试试与场景互动</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: Login Form -->
    <div class="form-panel">
      <div class="form-card">
        <router-link to="/" class="back-link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回首页
        </router-link>

        <div class="form-header">
          <h1 class="form-title">欢迎回来</h1>
          <p class="form-sub">登录你的 OfferPilot 账号</p>
        </div>

        <!-- Role Tabs -->
        <div class="role-tabs">
          <button
            v-for="role in roles"
            :key="role.id"
            :class="['role-tab', { active: activeRole === role.id }]"
            @click="activeRole = role.id"
          >
            <span v-html="role.icon"></span>
            <span>{{ role.label }}</span>
          </button>
        </div>

        <!-- Form -->
        <form class="login-form" @submit.prevent="handleLogin">
          <div class="field">
            <label class="field-label">账号</label>
            <div class="field-input">
              <svg class="field-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
              <input type="text" placeholder="请输入账号" v-model="form.account" />
            </div>
          </div>

          <div class="field">
            <label class="field-label">密码</label>
            <div class="field-input">
              <svg class="field-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input :type="showPwd ? 'text' : 'password'" placeholder="请输入密码" v-model="form.password" />
              <button type="button" class="pwd-toggle" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

          <div class="form-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.remember" />
              <span class="cb-box"></span>
              记住我
            </label>
            <router-link to="/forgot-password" class="forgot">忘记密码?</router-link>
          </div>

          <button type="submit" class="submit-btn" :class="{ loading }" :disabled="loading">
            <span v-if="loading">登录中...</span>
            <template v-else>
            <span>登 录</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
            </svg>
            </template>
          </button>
        </form>

        <p class="form-foot">
          还没有账号?<router-link to="/register" class="reg-link">立即注册</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { login as loginApi } from '../api'
import LogoIcon from '../components/ui/LogoIcon.vue'

const router = useRouter()
const userStore = useUserStore()
const activeRole = ref('student')
const showPwd = ref(false)
const orbActive = ref(false)
const scoreExpanded = ref(false)
const btnHover = ref(false)
const interactionScore = ref(12)
const errorMsg = ref('')
const loading = ref(false)

const mouse = reactive({ x: -200, y: -200 })

const questionBubbles = reactive([
  { text: '介绍一下你自己', style: { '--x': '10%', '--y': '20%', '--delay': '0s' }, popped: false },
  { text: '你的优势是什么?', style: { '--x': '65%', '--y': '10%', '--delay': '0.3s' }, popped: false },
  { text: '遇到过什么挑战?', style: { '--x': '75%', '--y': '55%', '--delay': '0.6s' }, popped: false },
  { text: '为什么选我们?', style: { '--x': '5%', '--y': '65%', '--delay': '0.9s' }, popped: false },
  { text: '技术栈是什么?', style: { '--x': '50%', '--y': '78%', '--delay': '1.2s' }, popped: false },
])

const roles = [
  { id: 'student', label: '学生端', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  { id: 'teacher', label: '教师端', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  { id: 'admin', label: '管理端', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4"/></svg>' },
]

const form = reactive({ account: '', password: '', remember: false })

function onMouseMove(e) {
  mouse.x = e.clientX
  mouse.y = e.clientY
}

function popBubble(i) {
  if (!questionBubbles[i].popped) {
    questionBubbles[i].popped = true
    interactionScore.value = Math.min(100, interactionScore.value + 8)
    setTimeout(() => { questionBubbles[i].popped = false }, 2000)
  }
}

async function handleLogin() {
  if (loading.value) return
  errorMsg.value = ''
  loading.value = true
  try {
    const data = await loginApi({ username: form.account, password: form.password })
    userStore.setAuth(data)
    const role = (data.role || '').toUpperCase()
    if (role === 'TEACHER' || role === 'ADMIN') {
      router.push('/teacher/dashboard')
    } else {
      router.push('/home')
    }
  } catch (e) {
    errorMsg.value = e.response?.data?.message || e.message || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Ticking score animation on orb hover
  let interval = null
  const watchOrb = () => {
    if (orbActive.value) {
      interval = setInterval(() => {
        interactionScore.value = Math.min(100, interactionScore.value + 1)
      }, 300)
    } else {
      clearInterval(interval)
    }
  }
  // Simple reactive watcher
  setInterval(() => {
    if (orbActive.value && interactionScore.value < 100) {
      interactionScore.value = Math.min(100, interactionScore.value + 0.5)
    }
  }, 200)
})
</script>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: flex;
  position: relative;
  overflow: hidden;
}

/* === Background === */
.bg-layer {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #f8faf9 0%, #f0faf5 30%, #fafafa 60%, #f5f5f5 100%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 1px 1px, rgba(16, 185, 129, 0.06) 1px, transparent 0);
  background-size: 40px 40px;
}

.bg-glow {
  position: fixed;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  transition: left 0.3s ease-out, top 0.3s ease-out;
  pointer-events: none;
}

/* === Stage Panel (Left) === */
.stage-panel {
  position: relative;
  z-index: 1;
  flex: 0 0 50%;
  display: flex;
  align-items: center;
  padding: var(--space-10);
}

.stage-content {
  max-width: 500px;
  width: 100%;
}

.stage-logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-10);
}

.stage-brand {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--neutral-800);
}

.stage-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 700;
  color: var(--neutral-900);
  line-height: 1.2;
  letter-spacing: -0.03em;
  margin-bottom: var(--space-4);
}

.title-accent {
  color: var(--accent-600);
}

.stage-desc {
  font-size: var(--text-base);
  color: var(--neutral-500);
  line-height: 1.7;
  margin-bottom: var(--space-10);
  max-width: 380px;
}

/* === Interactive Scene === */
.scene {
  position: relative;
  height: 280px;
  margin-top: var(--space-4);
}

/* AI Orb */
.ai-orb {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  cursor: pointer;
  z-index: 5;
}

.orb-core {
  position: absolute;
  inset: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-500), var(--accent-400));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 2;
  transition: all 0.4s var(--ease-spring);
  box-shadow: 0 0 24px rgba(16, 185, 129, 0.25);
}

.ai-orb.active .orb-core {
  transform: scale(1.15);
  box-shadow: 0 0 40px rgba(16, 185, 129, 0.4);
}

.orb-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1.5px solid rgba(16, 185, 129, 0.15);
  animation: orb-spin 8s linear infinite;
}

.orb-ring-1 { animation-duration: 8s; }
.orb-ring-2 { inset: -10px; animation-duration: 12s; animation-direction: reverse; border-color: rgba(16, 185, 129, 0.08); }
.orb-ring-3 { inset: -20px; animation-duration: 16s; border-color: rgba(16, 185, 129, 0.04); }

.ai-orb.active .orb-ring {
  border-color: rgba(16, 185, 129, 0.3);
  animation-duration: 3s;
}

@keyframes orb-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.orb-label {
  position: absolute;
  bottom: -28px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-600);
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s;
}

.ai-orb.active .orb-label { opacity: 1; }

/* Question Bubbles */
.q-bubble {
  position: absolute;
  left: var(--x);
  top: var(--y);
  padding: var(--space-2) var(--space-3);
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  font-size: 13px;
  color: var(--neutral-600);
  cursor: pointer;
  animation: bubble-float 4s ease-in-out infinite;
  animation-delay: var(--delay);
  transition: all 0.3s var(--ease-spring);
  z-index: 3;
  box-shadow: var(--shadow-sm);
}

.q-bubble:hover {
  transform: scale(1.08);
  border-color: var(--accent-300);
  color: var(--accent-700);
  box-shadow: var(--shadow-accent);
}

.q-bubble.popped {
  transform: scale(0);
  opacity: 0;
  border-color: var(--accent-400);
}

.q-ripple {
  position: absolute;
  inset: -4px;
  border-radius: inherit;
  border: 2px solid var(--accent-400);
  animation: ripple-out 0.6s ease-out forwards;
}

@keyframes ripple-out {
  from { transform: scale(1); opacity: 1; }
  to { transform: scale(2); opacity: 0; }
}

@keyframes bubble-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.q-bubble:hover {
  animation-play-state: paused;
}

/* Score Meter */
.score-meter {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--space-3);
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  transition: all 0.3s var(--ease-out-expo);
  z-index: 4;
  cursor: pointer;
}

.score-meter:hover {
  border-color: var(--accent-300);
  box-shadow: var(--shadow-accent);
}

.meter-track {
  height: 6px;
  background: var(--neutral-100);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-400), var(--accent-500));
  border-radius: 3px;
  transition: width 0.5s var(--ease-out-expo);
}

.meter-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 12px;
}

.meter-icon {
  color: var(--accent-500);
  display: flex;
}

.meter-val {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--accent-600);
  min-width: 20px;
}

.meter-hint {
  color: var(--neutral-400);
  margin-left: auto;
}

/* === Form Panel (Right) === */
.form-panel {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}

.form-card {
  width: 100%;
  max-width: 420px;
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(20px);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--neutral-400);
  text-decoration: none;
  margin-bottom: var(--space-6);
  transition: color var(--duration-fast);
}
.back-link:hover { color: var(--accent-600); }

.form-header { margin-bottom: var(--space-6); }

.form-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
  margin-bottom: var(--space-1);
}

.form-sub {
  font-size: var(--text-sm);
  color: var(--neutral-500);
}

/* Role Tabs */
.role-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  background: var(--neutral-100);
  border-radius: var(--radius-lg);
  padding: 3px;
}

.role-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-2);
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--neutral-500);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out-expo);
}
.role-tab:hover { color: var(--neutral-700); }
.role-tab.active {
  background: var(--surface-elevated);
  color: var(--accent-700);
  box-shadow: var(--shadow-sm);
}

/* Form Fields */
.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.field-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-700);
  margin-bottom: var(--space-2);
}

.field-input {
  position: relative;
  display: flex;
  align-items: center;
}

.field-icon {
  position: absolute;
  left: 12px;
  color: var(--neutral-400);
  pointer-events: none;
  z-index: 1;
}

.field-input input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  color: var(--neutral-800);
  font-family: var(--font-body);
  font-size: var(--text-base);
  outline: none;
  transition: all var(--duration-normal) var(--ease-out-expo);
}
.field-input input::placeholder { color: var(--neutral-400); }
.field-input input:focus {
  border-color: var(--accent-400);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.pwd-toggle {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: var(--neutral-400);
  cursor: pointer;
  padding: 4px;
  transition: color var(--duration-fast);
}
.pwd-toggle:hover { color: var(--accent-600); }

/* Form Row */
.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-sm);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--neutral-600);
  cursor: pointer;
}
.checkbox-label input { display: none; }

.cb-box {
  width: 16px;
  height: 16px;
  border: 1.5px solid var(--neutral-300);
  border-radius: 4px;
  transition: all var(--duration-fast);
  position: relative;
  flex-shrink: 0;
}
.checkbox-label input:checked + .cb-box {
  background: var(--accent-500);
  border-color: var(--accent-500);
}
.checkbox-label input:checked + .cb-box::after {
  content: '';
  position: absolute;
  left: 4px; top: 1px;
  width: 5px; height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.forgot {
  color: var(--accent-600);
  text-decoration: none;
  font-weight: 500;
}
.forgot:hover { color: var(--accent-700); }

.error-msg {
  padding: var(--space-3);
  background: var(--color-error-bg);
  color: var(--color-error);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: 14px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--accent-500);
  color: white;
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out-expo);
  margin-top: var(--space-2);
}
.submit-btn:hover {
  background: var(--accent-600);
  box-shadow: var(--shadow-accent-lg);
  transform: translateY(-2px);
}
.submit-btn:active {
  transform: scale(0.98);
}
.submit-btn svg {
  transition: transform 0.3s var(--ease-spring);
}
.submit-btn:hover svg {
  transform: translateX(4px);
}

.form-foot {
  text-align: center;
  margin-top: var(--space-6);
  font-size: var(--text-sm);
  color: var(--neutral-500);
}
.reg-link {
  color: var(--accent-600);
  font-weight: 600;
  margin-left: 4px;
  text-decoration: none;
}
.reg-link:hover { color: var(--accent-700); }

/* === Responsive === */
@media (max-width: 900px) {
  .login-page {
    flex-direction: column;
  }
  .stage-panel {
    flex: 0 0 auto;
    padding: var(--space-8) var(--space-6) var(--space-4);
  }
  .stage-title {
    font-size: var(--text-2xl);
  }
  .scene { height: 200px; }
  .q-bubble { font-size: 11px; padding: 4px 10px; }
  .form-panel { padding: var(--space-4) var(--space-6) var(--space-8); }
  .form-card {
    padding: var(--space-6);
    box-shadow: none;
    border: 1px solid var(--neutral-200);
  }
}

@media (prefers-reduced-motion: reduce) {
  .orb-ring, .q-bubble { animation: none; }
  .bg-glow { display: none; }
  .q-ripple { animation: none; }
}
</style>
