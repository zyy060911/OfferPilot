<template>
  <AppLayout>
    <div class="teacher-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">班级概览</h1>
        <p class="page-desc">2026 春季班 - 前端开发</p>
      </div>
      <div class="header-actions">
        <button class="btn-outline">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          导出报告
        </button>
        <button class="btn-primary" @click="showInvite = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>
          </svg>
          邀请学生
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div v-for="(stat, i) in stats" :key="i" class="stat-card">
        <div class="stat-icon-wrap" :style="{ background: stat.iconBg }">
          <span v-html="stat.icon"></span>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Content Grid -->
    <div class="teacher-grid">
      <!-- Recent Activity -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">最近动态</h2>
          <router-link to="/teacher/students" class="card-link">查看全部</router-link>
        </div>
        <div class="activity-list">
          <div v-for="(a, i) in recentActivity" :key="i" class="activity-item">
            <div class="activity-avatar" :style="{ background: a.avatarBg }">{{ a.name.charAt(0) }}</div>
            <div class="activity-info">
              <span class="activity-text"><strong>{{ a.name }}</strong> {{ a.action }}</span>
              <span class="activity-time">{{ a.time }}</span>
            </div>
            <span v-if="a.score" class="activity-score" :class="getScoreClass(a.score)">{{ a.score }}分</span>
          </div>
        </div>
      </div>

      <!-- Class Ability Distribution -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">班级能力分布</h2>
        </div>
        <div class="ability-list">
          <div v-for="(item, i) in abilityDistribution" :key="i" class="ability-item">
            <span class="ability-name">{{ item.name }}</span>
            <div class="ability-bar-track">
              <div class="ability-bar" :style="{ width: item.avg + '%', background: item.color }"></div>
            </div>
            <span class="ability-avg">{{ item.avg }}</span>
          </div>
        </div>
      </div>

      <!-- Common Weakness -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">共性短板</h2>
          <span class="card-badge">AI 分析</span>
        </div>
        <div class="weakness-list">
          <div v-for="(w, i) in commonWeakness" :key="i" class="weakness-item">
            <span class="weakness-rank">{{ i + 1 }}</span>
            <div class="weakness-info">
              <span class="weakness-name">{{ w.name }}</span>
              <span class="weakness-desc">{{ w.desc }}</span>
            </div>
            <span class="weakness-percent">{{ w.percent }}%</span>
          </div>
        </div>
      </div>

      <!-- Weekly Trend -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">本周活跃度</h2>
        </div>
        <div class="weekly-bars">
          <div v-for="(day, i) in weeklyData" :key="i" class="week-bar-group">
            <div class="week-bar-track">
              <div class="week-bar" :style="{ height: day.value + '%' }"></div>
            </div>
            <span class="week-label">{{ day.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Invite Modal -->
    <div v-if="showInvite" class="modal-overlay" @click.self="showInvite = false">
      <div class="modal-card">
        <button class="modal-close" @click="showInvite = false">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <h2 class="modal-title">邀请学生</h2>
        <p class="modal-desc">分享邀请码或链接，学生注册后自动加入班级</p>
        <div class="invite-code-box">
          <span class="invite-code">SPRING2026</span>
          <button class="copy-btn" @click="copyCode">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            复制
          </button>
        </div>
        <div class="invite-link">
          <span class="invite-link-text">https://offerpilot.com/join?code=SPRING2026</span>
          <button class="copy-btn">复制链接</button>
        </div>
      </div>
    </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/layout/AppLayout.vue'
import { getTeacherOverview } from '../../api'

const showInvite = ref(false)
const loading = ref(true)
const error = ref(null)

// 后端原始数据
const summary = ref({})
const studentList = ref([])
const weaknessDistribution = ref([])
const commonProblems = ref([])
const trainingTrend = ref([])

onMounted(async () => {
  try {
    const data = await getTeacherOverview()
    summary.value = data.summary || {}
    studentList.value = data.studentList || []
    weaknessDistribution.value = data.weaknessDistribution || []
    commonProblems.value = data.commonProblems || []
    trainingTrend.value = data.trainingTrend || []
  } catch (e) {
    error.value = e.message || '加载失败'
    console.error('获取教师概览数据失败:', e)
  } finally {
    loading.value = false
  }
})

// 映射到模板所需的 stats 格式
const stats = computed(() => [
  { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>', iconBg: 'rgba(16,185,129,0.1)', color: '#10b981', value: String(summary.value.totalStudents ?? '-'), label: '学生总数' },
  { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>', iconBg: 'rgba(16,185,129,0.08)', color: '#059669', value: String(summary.value.activeStudents ?? '-'), label: '本周活跃' },
  { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>', iconBg: 'rgba(52,211,153,0.1)', color: '#34d399', value: String(summary.value.averageScore ?? '-'), label: '平均得分' },
  { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>', iconBg: 'rgba(245,158,11,0.1)', color: '#f59e0b', value: String(summary.value.pendingReviews ?? '-'), label: '待批改' },
])

// 将 studentList 映射为最近动态（取前5名活跃学生）
const recentActivity = computed(() => {
  const avatarBgs = ['rgba(16,185,129,0.1)', 'rgba(52,211,153,0.1)', 'rgba(5,150,105,0.1)', 'rgba(16,185,129,0.08)', 'rgba(16,185,129,0.15)']
  return studentList.value.slice(0, 5).map((s, i) => ({
    name: s.nickname,
    action: s.status === 'ACTIVE' ? '最近有练习记录' : '暂无近期活动',
    time: formatRelativeTime(s.lastActiveTime),
    score: s.averageScore > 0 ? s.averageScore : null,
    avatarBg: avatarBgs[i % avatarBgs.length],
  }))
})

// 班级能力分布 - 无对应 API 字段，保留硬编码
const abilityDistribution = [
  { name: '表达能力', avg: 78, color: '#10b981' },
  { name: '逻辑性', avg: 72, color: '#059669' },
  { name: '技术深度', avg: 68, color: '#34d399' },
  { name: '岗位匹配', avg: 75, color: '#6ee7b7' },
  { name: '抗压能力', avg: 62, color: '#a7f3d0' },
]

// 映射 commonProblems 到模板所需的 commonWeakness 格式
const commonWeakness = computed(() =>
  commonProblems.value.map((p) => ({
    name: p.problem,
    desc: `${Math.round(p.ratio * 100)}% 的学生存在此问题`,
    percent: Math.round(p.ratio * 100),
  }))
)

// 映射 trainingTrend 到模板所需的 weeklyData 格式
const weeklyData = computed(() => {
  if (!trainingTrend.value.length) return []
  const max = Math.max(...trainingTrend.value.map((d) => d.count), 1)
  return trainingTrend.value.slice(-7).map((d) => {
    const dateObj = new Date(d.date)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return {
      label: weekdays[dateObj.getDay()],
      value: Math.round((d.count / max) * 100),
    }
  })
})

function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

function getScoreClass(score) {
  if (score >= 85) return 'score-high'
  if (score >= 70) return 'score-mid'
  return 'score-low'
}

function copyCode() {
  navigator.clipboard?.writeText('SPRING2026')
}
</script>

<style scoped>
.teacher-page {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--space-8) 0 var(--space-16);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-6);
  animation: fade-in-up 0.4s var(--ease-out);
}

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.page-desc {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-top: var(--space-1);
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

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
  transition: all var(--duration-normal) var(--ease-out-expo);
}

.btn-primary:hover {
  background: var(--accent-600);
  box-shadow: var(--shadow-accent);
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  color: var(--neutral-700);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-expo);
}

.btn-outline:hover {
  border-color: var(--neutral-300);
  background: var(--neutral-50);
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: all var(--duration-normal) var(--ease-out-expo);
  animation: fade-in-up 0.4s var(--ease-out) backwards;
}

.stat-card:nth-child(1) { animation-delay: 0.05s; }
.stat-card:nth-child(2) { animation-delay: 0.1s; }
.stat-card:nth-child(3) { animation-delay: 0.15s; }
.stat-card:nth-child(4) { animation-delay: 0.2s; }

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-600);
  flex-shrink: 0;
}

.stat-value {
  display: block;
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
  line-height: 1.2;
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

/* Grid */
.teacher-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

.card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  animation: fade-in-up 0.4s var(--ease-out) 0.2s backwards;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--neutral-900);
}

.card-link {
  font-size: var(--text-sm);
  color: var(--accent-600);
  font-weight: 500;
  text-decoration: none;
}

.card-link:hover {
  color: var(--accent-700);
}

.card-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  background: var(--accent-50);
  color: var(--accent-600);
  border-radius: var(--radius-full);
}

/* Activity */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast);
}

.activity-item:hover {
  background: var(--neutral-50);
}

.activity-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--accent-600);
  flex-shrink: 0;
}

.activity-info {
  flex: 1;
}

.activity-text {
  display: block;
  font-size: var(--text-sm);
  color: var(--neutral-700);
}

.activity-text strong {
  color: var(--neutral-900);
}

.activity-time {
  font-size: var(--text-xs);
  color: var(--neutral-400);
}

.activity-score {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 700;
}

.score-high { color: var(--accent-500); }
.score-mid { color: var(--color-warning); }
.score-low { color: var(--color-error); }

/* Ability */
.ability-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.ability-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.ability-name {
  width: 72px;
  font-size: var(--text-sm);
  color: var(--neutral-600);
}

.ability-bar-track {
  flex: 1;
  height: 8px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.ability-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out);
}

.ability-avg {
  width: 32px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-700);
}

/* Weakness */
.weakness-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.weakness-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(239, 68, 68, 0.03);
  border-radius: var(--radius-md);
  border-left: 3px solid rgba(239, 68, 68, 0.25);
}

.weakness-rank {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: rgba(239, 68, 68, 0.08);
  color: var(--color-error);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 700;
  flex-shrink: 0;
}

.weakness-info {
  flex: 1;
}

.weakness-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-800);
}

.weakness-desc {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.weakness-percent {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-error);
}

/* Weekly */
.weekly-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 160px;
  gap: var(--space-3);
}

.week-bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  height: 100%;
}

.week-bar-track {
  flex: 1;
  width: 100%;
  background: var(--neutral-100);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.week-bar {
  width: 100%;
  background: var(--accent-500);
  border-radius: var(--radius-sm);
  transition: height 1s var(--ease-out);
  min-height: 4px;
}

.week-label {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fade-in 0.2s var(--ease-out);
}

.modal-card {
  background: var(--surface-elevated);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  width: 100%;
  max-width: 440px;
  position: relative;
  box-shadow: var(--shadow-lg);
  animation: fade-in-up 0.3s var(--ease-out-expo);
}

.modal-close {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  background: none;
  border: none;
  color: var(--neutral-400);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast);
}

.modal-close:hover {
  color: var(--neutral-600);
  background: var(--neutral-100);
}

.modal-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--neutral-900);
  margin-bottom: var(--space-2);
}

.modal-desc {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-bottom: var(--space-6);
}

.invite-code-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: var(--accent-50);
  border: 1px solid var(--accent-200);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
}

.invite-code {
  font-family: var(--font-mono);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--accent-600);
  letter-spacing: 0.1em;
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  color: var(--neutral-700);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-expo);
}

.copy-btn:hover {
  border-color: var(--accent-400);
  color: var(--accent-600);
}

.invite-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--neutral-50);
  border-radius: var(--radius-md);
}

.invite-link-text {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  font-family: var(--font-mono);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .teacher-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .page-header { flex-direction: column; gap: var(--space-4); }
  .header-actions { width: 100%; }
  .btn-outline, .btn-primary { flex: 1; justify-content: center; }
}
</style>
