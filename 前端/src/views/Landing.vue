<template>
  <div class="landing" @mousemove="onGlobalMouseMove">
    <!-- Scroll Progress -->
    <div class="scroll-progress"><div class="scroll-progress-bar" :style="{ width: scrollPercent + '%' }"></div></div>

    <!-- Navbar -->
    <nav class="nav">
      <div class="nav-inner">
        <div class="nav-logo">
          <LogoIcon :size="26" />
          <span class="nav-brand">OfferPilot</span>
        </div>
        <div class="nav-links">
          <a href="#features">功能</a>
          <a href="#process">流程</a>
          <a href="#stats">数据</a>
        </div>
        <div class="nav-actions">
          <router-link to="/login" class="btn-nav-ghost">登录</router-link>
          <router-link to="/login" class="btn-nav-accent">免费注册</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-gradient"></div>
        <div class="hero-dots"></div>
      </div>

      <div class="hero-wrap">
        <div class="hero-content">
          <div class="hero-text">
            <div class="hero-badge">
              <span class="badge-pulse"></span>
              AI 驱动, 下一代面试训练
            </div>

            <h1 class="hero-title">
              <span class="typewriter-line">{{ typedLine1 }}<span class="tw-cursor" v-if="twPhase === 0">|</span></span><br />
              <span class="typewriter-line">{{ typedLine2 }}<span class="tw-cursor" v-if="twPhase === 1">|</span></span>
            </h1>

            <p class="hero-desc">
              上传简历, 匹配目标岗位, AI 实时追问并生成多维评估报告。每一次模拟练习都在缩短你和真实 Offer 的距离。
            </p>

            <div class="hero-cta">
              <router-link to="/login" class="btn btn-primary btn-lg">
                免费开始
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </router-link>
              <a href="#features" class="btn btn-ghost btn-lg">了解更多</a>
            </div>

            <div class="hero-proof">
              <span class="proof-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-500)" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
                免费使用
              </span>
              <span class="proof-dot"></span>
              <span class="proof-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-500)" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
                无需下载
              </span>
              <span class="proof-dot"></span>
              <span class="proof-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-500)" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
                即刻体验
              </span>
            </div>
          </div>

          <div class="hero-visual">
            <!-- Simulated Interview Interface -->
            <div class="mock-window" ref="mockWindowRef" @mousemove="onMockMouseMove" @mouseleave="onMockMouseLeave" :style="mockTiltStyle">
              <div class="mock-titlebar">
                <div class="mock-dots">
                  <span class="dot-r"></span>
                  <span class="dot-y"></span>
                  <span class="dot-g"></span>
                </div>
                <span class="mock-title">AI 模拟面试</span>
                <span class="mock-timer">24:36</span>
              </div>
              <div class="mock-body">
                <div class="mock-chat">
                  <!-- AI Message -->
                  <div class="mock-msg mock-ai">
                    <div class="mock-avatar-ai">AI</div>
                    <div class="mock-bubble-ai">
                      <span class="mock-followup">追问</span>
                      <p>你提到使用了 Vue 3 的 Composition API, 能具体说说和 Options API 相比, 在这个项目中它带来了哪些优势吗?</p>
                    </div>
                  </div>
                  <!-- User Message -->
                  <div class="mock-msg mock-user">
                    <div class="mock-bubble-user">
                      <p>好的, Composition API 让我可以把相关逻辑组织在一起, 比如把所有的表格搜索、分页、排序逻辑抽成一个 useTable 的 composable 函数...</p>
                    </div>
                    <div class="mock-avatar-user">张</div>
                  </div>
                  <!-- AI Evaluation -->
                  <div class="mock-msg mock-ai">
                    <div class="mock-avatar-ai">AI</div>
                    <div class="mock-bubble-ai mock-eval">
                      <div class="mock-eval-row">
                        <span class="mock-eval-label">技术深度</span>
                        <div class="mock-eval-bar"><div class="mock-eval-fill" style="width: 85%"></div></div>
                        <span class="mock-eval-val">85</span>
                      </div>
                      <div class="mock-eval-row">
                        <span class="mock-eval-label">逻辑表达</span>
                        <div class="mock-eval-bar"><div class="mock-eval-fill" style="width: 72%"></div></div>
                        <span class="mock-eval-val">72</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Floating Score Card -->
            <div class="float-card float-card-score">
              <span class="float-value">92</span>
              <span class="float-label">综合得分</span>
            </div>
            <!-- Floating Improvement Card -->
            <div class="float-card float-card-improve">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-500)" stroke-width="2.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
              <span class="float-text">能力提升 +15%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features (Bento) -->
    <section id="features" class="features-section">
      <div class="section-inner">
        <div class="section-header">
          <h2 class="section-title">不只是问答, 是完整的训练闭环</h2>
          <p class="section-desc">从简历分析到能力评估, OfferPilot 覆盖面试准备的每个环节</p>
        </div>

        <div class="bento-grid">
          <div class="bento-left">
            <div class="bento-card bento-card-ai" data-reveal @mousemove="onCardSpotlight" @mouseleave="onCardLeave">
              <div class="bento-icon bento-icon-ai">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-600)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              </div>
              <h3 class="bento-title">AI 追问引擎</h3>
              <p class="bento-desc">不是简单的一问一答。AI 实时分析你的回答, 动态生成深度追问, 帮你训练临场应变能力。</p>
              <div class="bento-tag-row">
                <span class="bento-tag">追问分析</span>
                <span class="bento-tag">实时生成</span>
              </div>
            </div>

            <div class="bento-card bento-card-resume" data-reveal @mousemove="onCardSpotlight" @mouseleave="onCardLeave">
              <div class="bento-icon bento-icon-resume">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-600)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              </div>
              <h3 class="bento-title">智能简历分析</h3>
              <p class="bento-desc">上传简历, AI 自动提取技能标签和项目经历, 为你生成个性化面试方案。</p>
            </div>
          </div>

          <div class="bento-card bento-card-report" data-reveal @mousemove="onCardSpotlight" @mouseleave="onCardLeave">
            <div class="bento-icon bento-icon-report">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-600)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V10"/><path d="M6 20V4"/><path d="M18 20v-6"/></svg>
            </div>
            <h3 class="bento-title">多维能力报告</h3>
            <p class="bento-desc">五维雷达图、优劣势分析、提升建议, 用数据驱动你的成长。</p>
            <div class="bento-chart">
              <div class="bento-chart-ring"></div>
              <div class="bento-chart-ring bento-chart-ring-2"></div>
              <div class="bento-chart-ring bento-chart-ring-3"></div>
            </div>
            <div class="bento-img-wrap">
              <svg viewBox="0 0 160 160" class="bento-radar" xmlns="http://www.w3.org/2000/svg">
                <!-- Grid -->
                <polygon v-for="s in [0.3,0.55,0.8]" :key="s" :points="radarGridPoints(s)" fill="none" :stroke="s===0.8?'var(--accent-300)':'var(--accent-100)'" stroke-width="1"/>
                <!-- Axis -->
                <line v-for="(_, i) in 5" :key="i" :x1="80" :y1="80" :x2="radarAngles[i].x*60+80" :y2="radarAngles[i].y*60+80" stroke="var(--accent-100)" stroke-width="0.8"/>
                <!-- Data -->
                <polygon :points="landingRadarData" fill="rgba(16,185,129,0.12)" stroke="var(--accent-500)" stroke-width="1.5" stroke-linejoin="round"/>
                <!-- Dots -->
                <circle v-for="(p, i) in landingRadarDots" :key="i" :cx="p.x" :cy="p.y" r="3" fill="var(--accent-500)"/>
                <!-- Labels -->
                <text v-for="(l, i) in ['表达','逻辑','技术','匹配','抗压']" :key="i" :x="radarAngles[i].x*78+80" :y="radarAngles[i].y*78+80+4" text-anchor="middle" font-size="11" fill="var(--neutral-400)" font-family="var(--font-body)">{{ l }}</text>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Process -->
    <section id="process" class="process-section">
      <div class="section-inner">
        <div class="section-header section-header-left">
          <h2 class="section-title">四步开启面试之旅</h2>
        </div>

        <div class="process-grid">
          <div v-for="(step, i) in steps" :key="i" class="step-card" data-reveal>
            <div class="step-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <div class="step-connector" v-if="i < steps.length - 1">
              <svg width="48" height="2" viewBox="0 0 48 2"><line x1="0" y1="1" x2="48" y2="1" stroke="var(--neutral-300)" stroke-width="2" stroke-dasharray="6 4"/></svg>
            </div>
            <h4 class="step-title">{{ step.title }}</h4>
            <p class="step-desc">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats -->
    <section id="stats" class="stats-section">
      <div class="section-inner">
        <div class="stats-grid">
          <div v-for="(stat, i) in stats" :key="i" class="stat-card" data-reveal>
            <span class="stat-value">{{ animatedStats[i] || stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="section-inner">
        <div class="cta-card">
          <h2 class="cta-title">准备好开启你的面试之旅了吗?</h2>
          <p class="cta-desc">免费注册, 立即体验 AI 模拟面试</p>
          <router-link to="/login" class="btn btn-primary btn-lg magnetic-btn" ref="ctaRef" @mousemove="onCtaMouseMove" @mouseleave="onCtaMouseLeave" :style="ctaMagnetStyle">
            立即开始, 免费体验
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <LogoIcon :size="22" />
          <span>OfferPilot</span>
        </div>
        <div class="footer-links">
          <a href="#">隐私政策</a>
          <a href="#">使用条款</a>
          <a href="#">联系我们</a>
        </div>
        <span class="footer-copy">&copy; 2026 OfferPilot. Built with AI.</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, reactive, computed } from 'vue'
import LogoIcon from '../components/ui/LogoIcon.vue'

// Landing page radar chart data
const radarAngles = [0, 1, 2, 3, 4].map(i => {
  const a = (Math.PI * 2 * i) / 5 - Math.PI / 2
  return { x: Math.cos(a), y: Math.sin(a) }
})

const radarValues = [85, 72, 88, 68, 79]

const radarGridPoints = (scale) =>
  radarValues.map((_, i) => {
    const r = 56 * scale
    return `${80 + r * radarAngles[i].x},${80 + r * radarAngles[i].y}`
  }).join(' ')

const landingRadarDots = computed(() =>
  radarValues.map((v, i) => ({
    x: 80 + radarAngles[i].x * 56 * (v / 100),
    y: 80 + radarAngles[i].y * 56 * (v / 100),
  }))
)

const landingRadarData = computed(() =>
  landingRadarDots.value.map(p => `${p.x},${p.y}`).join(' ')
)

const features = [
  { title: 'AI 追问引擎', desc: '不是简单的一问一答。AI 实时分析你的回答, 动态生成深度追问, 帮你训练临场应变能力。' },
  { title: '智能简历分析', desc: '上传简历, AI 自动提取技能标签和项目经历, 为你生成个性化面试方案。' },
  { title: '多维能力报告', desc: '五维雷达图、优劣势分析、提升建议, 用数据驱动你的成长。' },
]

const steps = [
  { title: '上传简历', desc: 'PDF 或图片, AI 自动提取技能画像' },
  { title: '匹配岗位', desc: '智能推荐目标岗位和面试题库' },
  { title: 'AI 面试', desc: '沉浸式模拟, 实时追问与互动' },
  { title: '获得报告', desc: '五维评估 + 精准提升建议' },
]

const stats = [
  { value: '10,000+', target: 10000, suffix: '+', label: '模拟面试完成' },
  { value: '50+', target: 50, suffix: '+', label: '覆盖岗位' },
  { value: '95%', target: 95, suffix: '%', label: '用户满意度' },
  { value: '4.9/5', target: 4.9, suffix: '/5', label: '平均评分', decimal: true },
]

// === Scroll Progress ===
const scrollPercent = ref(0)
function onScroll() {
  const h = document.documentElement
  scrollPercent.value = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100
}

// === Typewriter ===
const twPhase = ref(0)
const typedLine1 = ref('')
const typedLine2 = ref('')
const line1Text = '和 AI 面试官'
const line2Text = '练出你的 Offer'
let twTimer = null

function startTypewriter() {
  let i = 0
  twPhase.value = 0
  twTimer = setInterval(() => {
    if (i < line1Text.length) {
      typedLine1.value = line1Text.slice(0, i + 1)
      i++
    } else {
      clearInterval(twTimer)
      setTimeout(() => {
        twPhase.value = 1
        let j = 0
        twTimer = setInterval(() => {
          if (j < line2Text.length) {
            typedLine2.value = line2Text.slice(0, j + 1)
            j++
          } else {
            clearInterval(twTimer)
            setTimeout(() => { twPhase.value = -1 }, 600)
          }
        }, 70)
      }, 300)
    }
  }, 80)
}

// === Mock Window 3D Tilt ===
const mockWindowRef = ref(null)
const mockTilt = reactive({ x: 0, y: 0 })
const mockTiltStyle = computed(() => ({
  transform: `perspective(800px) rotateY(${mockTilt.x}deg) rotateX(${-mockTilt.y}deg) translateY(16px)`,
}))

function onMockMouseMove(e) {
  const el = mockWindowRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const x = (e.clientX - rect.left) / rect.width - 0.5
  const y = (e.clientY - rect.top) / rect.height - 0.5
  mockTilt.x = x * 8
  mockTilt.y = y * 6
}

function onMockMouseLeave() {
  mockTilt.x = 0
  mockTilt.y = 0
}

// === Bento Card Spotlight ===
function onCardSpotlight(e) {
  const card = e.currentTarget
  const rect = card.getBoundingClientRect()
  card.style.setProperty('--spot-x', (e.clientX - rect.left) + 'px')
  card.style.setProperty('--spot-y', (e.clientY - rect.top) + 'px')
  card.classList.add('spotlight')
}

function onCardLeave(e) {
  e.currentTarget.classList.remove('spotlight')
}

// === Stats Counter ===
const animatedStats = reactive({})
let statsAnimated = false

function animateStats() {
  if (statsAnimated) return
  statsAnimated = true
  stats.forEach((stat, i) => {
    const duration = 1500
    const start = performance.now()
    const target = stat.target
    const isDecimal = stat.decimal
    function tick(now) {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = target * eased
      if (isDecimal) {
        animatedStats[i] = current.toFixed(1) + stat.suffix
      } else if (target >= 1000) {
        animatedStats[i] = Math.floor(current).toLocaleString() + stat.suffix
      } else {
        animatedStats[i] = Math.floor(current) + stat.suffix
      }
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  })
}

// === Global Mouse (for potential future use) ===
function onGlobalMouseMove() {}

// === CTA Magnetic Button ===
const ctaRef = ref(null)
const ctaMagnet = reactive({ x: 0, y: 0 })
const ctaMagnetStyle = computed(() => ({
  transform: `translate(${ctaMagnet.x}px, ${ctaMagnet.y}px)`,
}))

function onCtaMouseMove(e) {
  const el = ctaRef.value?.$el || ctaRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height / 2
  ctaMagnet.x = (e.clientX - cx) * 0.15
  ctaMagnet.y = (e.clientY - cy) * 0.15
}

function onCtaMouseLeave() {
  ctaMagnet.x = 0
  ctaMagnet.y = 0
}

// === Observer + Mount ===
const observerRef = ref(null)
const statsObserverRef = ref(null)

onMounted(() => {
  // Scroll listener
  window.addEventListener('scroll', onScroll, { passive: true })

  // Typewriter
  setTimeout(startTypewriter, 500)

  // Scroll reveal
  const els = document.querySelectorAll('[data-reveal]')
  if (!('IntersectionObserver' in window) || els.length === 0) {
    els.forEach((el) => el.classList.add('is-visible'))
    return
  }

  observerRef.value = new IntersectionObserver(
    (entries) => {
      const entering = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => a.target.getBoundingClientRect().top - b.target.getBoundingClientRect().top)
      entering.forEach((entry, i) => {
        entry.target.style.transitionDelay = `${i * 80}ms`
        entry.target.classList.add('is-visible')
        observerRef.value.unobserve(entry.target)
      })
    },
    { threshold: 0.15 }
  )
  els.forEach((el) => observerRef.value.observe(el))

  // Stats counter observer
  const statsEl = document.querySelector('.stats-section')
  if (statsEl) {
    statsObserverRef.value = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          animateStats()
          statsObserverRef.value?.unobserve(statsEl)
        }
      },
      { threshold: 0.3 }
    )
    statsObserverRef.value.observe(statsEl)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  clearInterval(twTimer)
  observerRef.value?.disconnect()
  statsObserverRef.value?.disconnect()
})
</script>

<style scoped>
/* === Scroll Progress === */
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 200;
  background: transparent;
}
.scroll-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-400), var(--accent-600));
  transition: width 0.1s linear;
  border-radius: 0 2px 2px 0;
}

/* === Typewriter === */
.tw-cursor {
  color: var(--accent-500);
  animation: blink 0.6s step-end infinite;
  font-weight: 300;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* === Mock Window Tilt === */
.mock-window {
  transition: transform 0.15s ease-out;
  will-change: transform;
}

/* === Bento Spotlight === */
.bento-card.spotlight::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(
    300px circle at var(--spot-x) var(--spot-y),
    rgba(16, 185, 129, 0.08) 0%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 0;
  opacity: 1;
  transition: opacity 0.3s;
}
.bento-card {
  position: relative;
  overflow: hidden;
}

/* === Magnetic Button === */
.magnetic-btn {
  transition: transform 0.2s var(--ease-spring), background var(--duration-normal) var(--ease-out-expo), box-shadow var(--duration-normal) var(--ease-out-expo);
  will-change: transform;
}

/* === Nav === */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(16px) saturate(1.6);
  -webkit-backdrop-filter: blur(16px) saturate(1.6);
  border-bottom: 1px solid var(--neutral-200);
}

.nav-inner {
  max-width: var(--container-max);
  margin: 0 auto;
  height: var(--nav-height);
  padding: 0 var(--space-8);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.nav-brand {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--neutral-900);
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  gap: var(--space-8);
}

.nav-links a {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-500);
  transition: color var(--duration-fast) var(--ease-out-expo);
}

.nav-links a:hover {
  color: var(--neutral-900);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.btn-nav-ghost {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-600);
  padding: var(--space-2) var(--space-4);
  transition: color var(--duration-fast) var(--ease-out-expo);
}

.btn-nav-ghost:hover {
  color: var(--neutral-900);
}

.btn-nav-accent {
  font-size: var(--text-sm);
  font-weight: 600;
  color: white;
  padding: var(--space-2) var(--space-5);
  background: var(--accent-500);
  border-radius: var(--radius-sm);
  transition:
    background var(--duration-normal) var(--ease-out-expo),
    box-shadow var(--duration-normal) var(--ease-out-expo),
    transform var(--duration-normal) var(--ease-spring);
}

.btn-nav-accent:hover {
  background: var(--accent-600);
  box-shadow: var(--shadow-accent);
  transform: translateY(-1px);
  color: white;
}

/* === Hero === */
.hero {
  position: relative;
  min-height: 100dvh;
  padding-top: var(--nav-height);
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(155deg, var(--neutral-950) 0%, #1a2e2a 45%, var(--neutral-900) 100%);
}

.hero-dots {
  position: absolute;
  inset: 0;
  opacity: 0.18;
  background-image:
    radial-gradient(circle, var(--accent-400) 1px, transparent 1px);
  background-size: 48px 48px;
}

.hero-wrap {
  position: relative;
  z-index: 1;
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--space-16) var(--space-8);
  width: 100%;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  align-items: center;
  gap: var(--space-16);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--accent-300);
  margin-bottom: var(--space-6);
}

.badge-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-400);
  animation: breathe 2.5s ease-in-out infinite;
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 5vw, 3.75rem);
  font-weight: 700;
  line-height: 1.15;
  color: var(--neutral-50);
  letter-spacing: -0.03em;
  margin-bottom: var(--space-6);
}

.hero-desc {
  font-size: var(--text-lg);
  color: var(--neutral-400);
  line-height: 1.75;
  margin-bottom: var(--space-8);
  max-width: 480px;
}

.hero-cta {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.hero-proof {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.proof-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--neutral-400);
}

.proof-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--neutral-600);
}

/* === Buttons === */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-weight: 600;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition:
    transform var(--duration-normal) var(--ease-spring),
    box-shadow var(--duration-normal) var(--ease-out-expo),
    background var(--duration-normal) var(--ease-out-expo),
    border-color var(--duration-normal) var(--ease-out-expo);
}

.btn:active {
  transform: scale(0.97);
}

.btn-lg {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
}

.btn-primary {
  background: var(--accent-500);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-600);
  box-shadow: var(--shadow-accent-lg);
  transform: translateY(-2px);
  color: white;
}

.btn-ghost {
  background: transparent;
  color: var(--neutral-300);
  border: 1px solid var(--neutral-600);
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--neutral-400);
  color: var(--neutral-100);
  transform: translateY(-2px);
}

/* === Hero Visual === */
.hero-visual {
  position: relative;
  display: flex;
  justify-content: flex-end;
}

/* === Mock Interview Window === */
.mock-window {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow:
    0 32px 80px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(255, 255, 255, 0.06);
  max-width: 520px;
  width: 100%;
  background: var(--neutral-900);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.mock-titlebar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.mock-dots {
  display: flex;
  gap: 6px;
}
.dot-r, .dot-y, .dot-g {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot-r { background: #ef4444; opacity: 0.7; }
.dot-y { background: #f59e0b; opacity: 0.7; }
.dot-g { background: var(--accent-500); opacity: 0.7; }

.mock-title {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
}

.mock-timer {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-400);
}

.mock-body {
  padding: 16px;
}

.mock-chat {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mock-msg {
  display: flex;
  gap: 10px;
  max-width: 90%;
}
.mock-msg.mock-ai { align-self: flex-start; }
.mock-msg.mock-user { align-self: flex-end; flex-direction: row-reverse; }

.mock-avatar-ai, .mock-avatar-user {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
.mock-avatar-ai {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-400);
}
.mock-avatar-user {
  background: linear-gradient(135deg, var(--accent-500), var(--accent-600));
  color: white;
}

.mock-bubble-ai {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  border-top-left-radius: 4px;
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

.mock-followup {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  color: var(--accent-400);
  background: rgba(16, 185, 129, 0.12);
  padding: 1px 8px;
  border-radius: 20px;
  margin-bottom: 6px;
}

.mock-bubble-user {
  background: var(--accent-600);
  border-radius: 12px;
  border-bottom-right-radius: 4px;
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.6;
  color: white;
}

.mock-eval {
  padding: 12px;
}
.mock-eval-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.mock-eval-row:last-child { margin-bottom: 0; }
.mock-eval-label {
  width: 56px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}
.mock-eval-bar {
  flex: 1;
  height: 5px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}
.mock-eval-fill {
  height: 100%;
  background: var(--accent-500);
  border-radius: 3px;
}
.mock-eval-val {
  width: 24px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-400);
}

/* Floating Cards */
.float-card {
  position: absolute;
  background: var(--surface-elevated);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  box-shadow:
    var(--shadow-lg),
    0 0 0 1px rgba(0, 0, 0, 0.04);
  animation: float 5s ease-in-out infinite;
  z-index: 2;
}

.float-card-score {
  top: -8px;
  right: -16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  animation-delay: -1.5s;
}

.float-value {
  font-family: var(--font-mono);
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
  color: var(--accent-500);
}

.float-label {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.float-card-improve {
  bottom: 20px;
  left: -28px;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-800);
  animation-delay: -3s;
}

.float-text {
  white-space: nowrap;
}

/* === Section Commons === */
.section-inner {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 var(--space-8);
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-16);
}

.section-header-left {
  text-align: left;
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.5vw, var(--text-3xl));
  font-weight: 700;
  color: var(--neutral-900);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-3);
}

.section-header-left .section-title {
  margin-bottom: 0;
}

.section-desc {
  font-size: var(--text-lg);
  color: var(--neutral-500);
  max-width: 540px;
  margin: 0 auto;
}

/* === Features (Bento) === */
.features-section {
  padding: var(--space-32) 0 var(--space-24);
  background: var(--surface-primary);
}

.bento-grid {
  display: grid;
  grid-template-columns: 1fr 1.15fr;
  gap: var(--space-6);
  align-items: stretch;
}

.bento-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.bento-card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  position: relative;
  overflow: hidden;
  transition:
    transform var(--duration-slow) var(--ease-spring),
    box-shadow var(--duration-slow) var(--ease-out-expo),
    border-color var(--duration-slow) var(--ease-out-expo);
}

.bento-card:hover {
  transform: translateY(-4px) scale(1.005);
  box-shadow: var(--shadow-lg);
  border-color: var(--accent-200);
}

.bento-card-ai {
  flex: 1;
}

.bento-card-ai::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-400), var(--accent-500));
}

.bento-card-resume {
  flex: 1;
}

.bento-card-resume::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-500), var(--accent-300));
}

.bento-card-report {
  display: flex;
  flex-direction: column;
}

.bento-card-report::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-600), var(--accent-400));
}

.bento-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-5);
  background: var(--accent-50);
  border: 1px solid var(--accent-100);
}

.bento-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--neutral-900);
  margin-bottom: var(--space-3);
  letter-spacing: -0.01em;
}

.bento-desc {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  line-height: 1.7;
}

.bento-tag-row {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
  flex-wrap: wrap;
}

.bento-tag {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--accent-700);
  padding: var(--space-1) var(--space-3);
  background: var(--accent-50);
  border: 1px solid var(--accent-100);
  border-radius: var(--radius-full);
}

/* Report card chart decoration */
.bento-chart {
  position: absolute;
  top: var(--space-8);
  right: var(--space-8);
  width: 80px;
  height: 80px;
  opacity: 0.12;
  pointer-events: none;
}

.bento-chart-ring {
  position: absolute;
  inset: 0;
  border: 2px solid var(--accent-500);
  border-radius: 50%;
}

.bento-chart-ring-2 {
  inset: 12px;
  border-color: var(--accent-400);
}

.bento-chart-ring-3 {
  inset: 24px;
  border-color: var(--accent-300);
}

.bento-img-wrap {
  margin-top: auto;
  padding-top: var(--space-6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.bento-radar {
  width: 160px;
  height: 160px;
}

.bento-img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

/* === Process === */
.process-section {
  padding: var(--space-24) 0;
  background: var(--surface-sunken);
}

.process-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-6);
}

.step-card {
  position: relative;
  padding: var(--space-8) var(--space-6);
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  text-align: center;
  transition:
    transform var(--duration-slow) var(--ease-spring),
    box-shadow var(--duration-slow) var(--ease-out-expo),
    border-color var(--duration-slow) var(--ease-out-expo);
}

.step-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--accent-200);
}

.step-num {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--accent-100);
  line-height: 1;
  margin-bottom: var(--space-4);
  letter-spacing: -0.04em;
}

.step-connector {
  position: absolute;
  top: 50%;
  right: -30px;
  transform: translateY(-50%);
  z-index: 1;
  pointer-events: none;
}

.step-title {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--neutral-800);
  margin-bottom: var(--space-2);
}

.step-desc {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  line-height: 1.6;
}

/* === Stats === */
.stats-section {
  padding: var(--space-20) 0;
  background: var(--surface-elevated);
  border-top: 1px solid var(--neutral-200);
  border-bottom: 1px solid var(--neutral-200);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-8);
  text-align: center;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.stat-value {
  font-family: var(--font-mono);
  font-size: clamp(var(--text-3xl), 4vw, var(--text-4xl));
  font-weight: 700;
  color: var(--accent-500);
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--neutral-500);
}

/* === CTA === */
.cta-section {
  padding: var(--space-24) 0;
  background: var(--surface-primary);
}

.cta-card {
  background: linear-gradient(145deg, var(--neutral-950), #1a2e2a, var(--neutral-900));
  border-radius: var(--radius-xl);
  padding: var(--space-16) var(--space-8);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.cta-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background-image:
    radial-gradient(circle, var(--accent-400) 1px, transparent 1px);
  background-size: 36px 36px;
  pointer-events: none;
}

.cta-title {
  font-family: var(--font-display);
  font-size: clamp(var(--text-2xl), 3.5vw, var(--text-3xl));
  font-weight: 700;
  color: var(--neutral-50);
  margin-bottom: var(--space-4);
  letter-spacing: -0.02em;
  position: relative;
}

.cta-desc {
  font-size: var(--text-lg);
  color: var(--neutral-400);
  margin-bottom: var(--space-8);
  position: relative;
}

.cta-section .btn-primary {
  position: relative;
}

/* === Footer === */
.site-footer {
  padding: var(--space-8) 0;
  background: var(--surface-elevated);
  border-top: 1px solid var(--neutral-200);
}

.footer-inner {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 var(--space-8);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-sm);
  color: var(--neutral-700);
}

.footer-links {
  display: flex;
  gap: var(--space-6);
}

.footer-links a {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  transition: color var(--duration-fast) var(--ease-out-expo);
}

.footer-links a:hover {
  color: var(--neutral-700);
}

.footer-copy {
  font-size: var(--text-xs);
  color: var(--neutral-400);
  font-family: var(--font-mono);
}

/* === Scroll Reveal === */
[data-reveal] {
  opacity: 0;
  transform: translateY(24px);
  transition:
    opacity var(--duration-slower) var(--ease-out-expo),
    transform var(--duration-slower) var(--ease-out-expo);
}

[data-reveal].is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* === Responsive === */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: var(--space-12);
  }

  .hero-text {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .hero-desc {
    max-width: 520px;
  }

  .hero-cta {
    justify-content: center;
  }

  .hero-proof {
    justify-content: center;
  }

  .hero-visual {
    justify-content: center;
  }

  .mock-window {
    max-width: 460px;
  }

  .float-card-score {
    right: 0;
  }

  .float-card-improve {
    left: 0;
  }

  .bento-grid {
    grid-template-columns: 1fr;
  }

  .process-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .step-connector {
    display: none;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-6);
  }
}

@media (max-width: 640px) {
  .nav-links {
    display: none;
  }

  .nav-inner {
    padding: 0 var(--space-4);
  }

  .hero-wrap {
    padding: var(--space-10) var(--space-4);
  }

  .hero-title {
    font-size: var(--text-3xl);
  }

  .hero-cta {
    flex-direction: column;
    width: 100%;
  }

  .hero-cta .btn {
    width: 100%;
    justify-content: center;
  }

  .float-card {
    display: none;
  }

  .mock-window {
    transform: none !important;
  }

  .section-inner {
    padding: 0 var(--space-4);
  }

  .process-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .footer-inner {
    flex-direction: column;
    gap: var(--space-4);
    text-align: center;
  }
}

/* === Reduced Motion === */
@media (prefers-reduced-motion: reduce) {
  [data-reveal] {
    opacity: 1;
    transform: none;
    transition: none;
  }

  .float-card {
    animation: none;
  }

  .badge-pulse {
    animation: none;
  }

  .scroll-progress { display: none; }
  .tw-cursor { display: none; }
  .mock-window { transition: none !important; transform: translateY(16px) !important; }
  .magnetic-btn { transition: background var(--duration-normal), box-shadow var(--duration-normal) !important; }
  .bento-card.spotlight::before { display: none; }
}
</style>
