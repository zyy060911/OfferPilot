<template>
  <AppLayout>
    <div class="profile-page">
      <!-- Profile Header -->
      <div class="profile-header card">
        <div class="profile-cover"></div>
        <div class="profile-info">
          <div class="profile-avatar">
            <span>{{ avatarChar }}</span>
          </div>
          <div class="profile-details">
            <h1 class="profile-name">{{ nickname }}</h1>
            <p class="profile-bio">{{ bio }}</p>
            <div class="profile-stats-row">
              <div class="profile-stat">
                <span class="stat-num">{{ stats.totalInterviews }}</span>
                <span class="stat-text">面试次数</span>
              </div>
              <div class="profile-stat">
                <span class="stat-num">{{ stats.averageScore }}</span>
                <span class="stat-text">平均得分</span>
              </div>
              <div class="profile-stat">
                <span class="stat-num">{{ stats.streakDays }}天</span>
                <span class="stat-text">连续练习</span>
              </div>
            </div>
          </div>
          <button class="edit-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            编辑资料
          </button>
        </div>
      </div>

      <!-- Content Grid -->
      <div class="profile-grid">
        <!-- Skills & Tags -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">技能标签</h2>
            <button class="card-action">编辑</button>
          </div>
          <div class="skills-grid">
            <span v-for="skill in skills" :key="skill.name" class="skill-item" :class="skill.level">
              {{ skill.name }}
            </span>
          </div>
        </div>

        <!-- Activity Calendar -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">练习日历</h2>
            <span class="card-subtitle">最近 30 天</span>
          </div>
          <div class="calendar-grid">
            <div
              v-for="(day, i) in calendarData"
              :key="i"
              class="calendar-cell"
              :class="'level-' + day.level"
              :title="day.date + ': ' + day.count + '次'"
            ></div>
          </div>
          <div class="calendar-legend">
            <span class="legend-label">少</span>
            <div class="legend-cell level-0"></div>
            <div class="legend-cell level-1"></div>
            <div class="legend-cell level-2"></div>
            <div class="legend-cell level-3"></div>
            <div class="legend-cell level-4"></div>
            <span class="legend-label">多</span>
          </div>
        </div>

        <!-- Ability Compare -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">能力对比</h2>
          </div>
          <div class="compare-list">
            <div v-for="(item, i) in compareData" :key="i" class="compare-row">
              <span class="compare-name">{{ item.name }}</span>
              <div class="compare-bars">
                <div class="compare-bar-track">
                  <div class="compare-bar compare-bar-user" :style="{ width: item.user + '%' }"></div>
                </div>
                <div class="compare-bar-track compare-track-avg">
                  <div class="compare-bar compare-bar-avg" :style="{ width: item.avg + '%' }"></div>
                </div>
              </div>
              <span class="compare-score">{{ item.user }}</span>
            </div>
          </div>
          <div class="compare-legend">
            <span class="legend-dot legend-dot-user"></span> 你的成绩
            <span class="legend-dot legend-dot-avg"></span> 平台平均
          </div>
        </div>

        <!-- Interview History Summary -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">岗位分布</h2>
          </div>
          <div class="distribution-list">
            <div v-for="(item, i) in jobDistribution" :key="i" class="distribution-item">
              <span class="dist-name">{{ item.name }}</span>
              <div class="dist-bar-container">
                <div class="dist-bar" :style="{ width: item.percent + '%', background: item.color }"></div>
              </div>
              <span class="dist-count">{{ item.count }}次</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getMe, getMyStats } from '../api'
import { useUserStore } from '../store/user'
import AppLayout from '../components/layout/AppLayout.vue'

const userStore = useUserStore()

const nickname = ref('加载中...')
const bio = ref('')
const stats = ref({
  totalInterviews: 0,
  averageScore: 0,
  streakDays: 0,
})

const avatarChar = computed(() => {
  return nickname.value ? nickname.value.charAt(0) : '用'
})

const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const [meRes, statsRes] = await Promise.all([getMe(), getMyStats()])
    nickname.value = meRes.nickname || meRes.username || '用户'
    userStore.$patch({
      userId: meRes.id,
      username: meRes.username,
      nickname: meRes.nickname || '',
      role: meRes.role,
    })
    stats.value = {
      totalInterviews: statsRes.totalInterviews ?? 0,
      averageScore: statsRes.averageScore ?? 0,
      streakDays: statsRes.streakDays ?? 0,
    }
  } catch (e) {
    console.error('Failed to load profile:', e)
    error.value = '加载个人信息失败'
    nickname.value = userStore.nickname || userStore.username || '用户'
  } finally {
    loading.value = false
  }
})

const skills = [
  { name: 'JavaScript', level: 'high' },
  { name: 'Vue.js', level: 'high' },
  { name: 'React', level: 'mid' },
  { name: 'TypeScript', level: 'mid' },
  { name: 'Node.js', level: 'mid' },
  { name: 'CSS3', level: 'high' },
  { name: 'Webpack', level: 'low' },
  { name: 'Git', level: 'high' },
  { name: 'RESTful API', level: 'mid' },
  { name: '算法', level: 'low' },
]

const calendarData = Array.from({ length: 35 }, (_, i) => ({
  date: `2026-06-${(i % 30) + 1}`,
  count: Math.floor(Math.random() * 5),
  level: Math.floor(Math.random() * 5),
}))

const compareData = [
  { name: '表达能力', user: 88, avg: 72 },
  { name: '逻辑性', user: 72, avg: 65 },
  { name: '技术深度', user: 85, avg: 70 },
  { name: '岗位匹配', user: 78, avg: 68 },
  { name: '抗压能力', user: 65, avg: 60 },
]

const jobDistribution = [
  { name: '前端开发', count: 5, percent: 42, color: 'var(--accent-500)' },
  { name: '产品经理', count: 3, percent: 25, color: 'var(--accent-400)' },
  { name: '后端开发', count: 2, percent: 17, color: 'var(--accent-600)' },
  { name: '数据分析师', count: 2, percent: 16, color: 'var(--accent-300)' },
]
</script>

<style scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--space-8) 0 var(--space-16);
}

.card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  animation: fade-in-up 0.4s var(--ease-out-expo);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--neutral-900);
}

.card-subtitle {
  font-size: var(--text-xs);
  color: var(--neutral-400);
}

.card-action {
  font-size: var(--text-sm);
  color: var(--accent-600);
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: color var(--duration-fast);
}

.card-action:hover {
  color: var(--accent-500);
}

/* Profile Header */
.profile-header {
  margin-bottom: var(--space-6);
  padding: 0;
  overflow: hidden;
}

.profile-cover {
  height: 120px;
  background: linear-gradient(135deg, var(--accent-500), var(--accent-600));
}

.profile-info {
  padding: var(--space-6);
  display: flex;
  align-items: flex-start;
  gap: var(--space-5);
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--accent-500), var(--accent-600));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-2xl);
  font-weight: 700;
  color: white;
  margin-top: -40px;
  border: 4px solid var(--surface-elevated);
  box-shadow: var(--shadow-sm);
}

.profile-details {
  flex: 1;
}

.profile-name {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.profile-bio {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-top: var(--space-1);
}

.profile-stats-row {
  display: flex;
  gap: var(--space-8);
  margin-top: var(--space-4);
}

.profile-stat {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-family: var(--font-mono);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.stat-text {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.edit-btn {
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
  transition: all var(--duration-normal);
}

.edit-btn:hover {
  border-color: var(--accent-300);
  background: var(--accent-50);
  color: var(--accent-700);
}

/* Profile Grid */
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

/* Skills */
.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.skill-item {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 500;
  transition: transform var(--duration-fast);
}

.skill-item:hover {
  transform: scale(1.05);
}

.skill-item.high {
  background: var(--accent-50);
  color: var(--accent-700);
}

.skill-item.mid {
  background: #dbeafe;
  color: #1d4ed8;
}

.skill-item.low {
  background: #fef3c7;
  color: #b45309;
}

/* Calendar */
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
}

.calendar-cell {
  aspect-ratio: 1;
  border-radius: var(--radius-xs);
  transition: transform var(--duration-fast);
}

.calendar-cell:hover {
  transform: scale(1.2);
}

.level-0 { background: var(--neutral-100); }
.level-1 { background: rgba(16, 185, 129, 0.15); }
.level-2 { background: rgba(16, 185, 129, 0.35); }
.level-3 { background: rgba(16, 185, 129, 0.6); }
.level-4 { background: var(--accent-500); }

.calendar-legend {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  justify-content: flex-end;
  margin-top: var(--space-3);
}

.legend-label {
  font-size: 10px;
  color: var(--neutral-400);
}

.legend-cell {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-xs);
}

/* Ability Compare */
.compare-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.compare-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.compare-name {
  width: 64px;
  font-size: var(--text-sm);
  color: var(--neutral-700);
  flex-shrink: 0;
}

.compare-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.compare-bar-track {
  width: 100%;
  height: 8px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.compare-track-avg {
  height: 5px;
}

.compare-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out-expo);
}

.compare-bar-user {
  background: var(--accent-500);
}

.compare-bar-avg {
  background: var(--neutral-300);
}

.compare-score {
  width: 28px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--accent-600);
}

.compare-legend {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.compare-legend span + span {
  margin-left: var(--space-2);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  display: inline-block;
}

.legend-dot-user {
  background: var(--accent-500);
}

.legend-dot-avg {
  background: var(--neutral-300);
}

/* Distribution */
.distribution-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dist-name {
  width: 80px;
  font-size: var(--text-sm);
  color: var(--neutral-600);
}

.dist-bar-container {
  flex: 1;
  height: 8px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.dist-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out-expo);
}

.dist-count {
  width: 36px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-700);
}

@media (max-width: 768px) {
  .profile-grid { grid-template-columns: 1fr; }
  .profile-info { flex-direction: column; }
  .profile-stats-row { gap: var(--space-4); }
  .edit-btn { align-self: flex-start; }
}
</style>
