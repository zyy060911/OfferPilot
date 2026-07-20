<template>
  <AppLayout>
    <div class="teacher-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">班级管理</h1>
        <p class="page-desc">管理学生、查看班级信息</p>
      </div>
      <div class="header-actions">
        <div class="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <input type="text" placeholder="搜索学生姓名..." v-model="searchQuery" class="search-input" />
        </div>
        <button class="btn-primary" @click="showInvite = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          添加学生
        </button>
      </div>
    </div>

    <!-- Student Table -->
    <div class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>学生</th>
            <th>面试次数</th>
            <th>平均得分</th>
            <th>最近活跃</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in filteredStudents" :key="student.id" class="table-row">
            <td>
              <div class="student-cell">
                <div class="student-avatar" :style="{ background: student.avatarBg }">{{ student.name.charAt(0) }}</div>
                <div>
                  <span class="student-name">{{ student.name }}</span>
                  <span class="student-email">{{ student.email }}</span>
                </div>
              </div>
            </td>
            <td><span class="mono-value">{{ student.count }}</span></td>
            <td><span class="mono-value" :class="getScoreClass(student.avg)">{{ student.avg }}</span></td>
            <td class="text-muted">{{ student.lastActive }}</td>
            <td>
              <span :class="['status-tag', student.status]">
                {{ student.status === 'active' ? '活跃' : student.status === 'inactive' ? '不活跃' : '新加入' }}
              </span>
            </td>
            <td>
              <router-link :to="`/teacher/students/${student.id}`" class="action-link">查看详情</router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Class Stats Summary -->
    <div class="summary-grid">
      <div class="card summary-card">
        <h3 class="summary-title">活跃率</h3>
        <span class="summary-value accent-value">{{ activeRate }}</span>
        <span class="summary-desc">{{ activeStudents }}/{{ totalStudents }} 学生本周活跃</span>
      </div>
      <div class="card summary-card">
        <h3 class="summary-title">平均得分</h3>
        <span class="summary-value accent-value">{{ averageScore }}</span>
        <span class="summary-desc">班级平均面试得分</span>
      </div>
      <div class="card summary-card">
        <h3 class="summary-title">学生总数</h3>
        <span class="summary-value" style="color: var(--accent-500)">{{ totalStudents }}</span>
        <span class="summary-desc">当前班级注册学生数</span>
      </div>
    </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/layout/AppLayout.vue'
import { getTeacherOverview } from '../../api'

const searchQuery = ref('')
const showInvite = ref(false)
const loading = ref(true)
const error = ref(null)

// 后端原始数据
const totalStudents = ref(0)
const activeStudents = ref(0)
const averageScore = ref(0)
const students = ref([])

onMounted(async () => {
  try {
    const data = await getTeacherOverview()
    const summary = data.summary || {}
    totalStudents.value = summary.totalStudents || 0
    activeStudents.value = summary.activeStudents || 0
    averageScore.value = summary.averageScore || 0

    const avatarBgs = [
      'rgba(16,185,129,0.1)', 'rgba(52,211,153,0.1)', 'rgba(5,150,105,0.1)',
      'rgba(16,185,129,0.08)', 'rgba(16,185,129,0.15)', 'rgba(236,72,153,0.1)',
      'rgba(52,211,153,0.12)', 'rgba(110,231,183,0.1)',
    ]

    students.value = (data.studentList || []).map((s, i) => ({
      id: s.userId,
      name: s.nickname,
      email: '', // 后端未返回邮箱字段
      count: s.totalInterviews,
      avg: s.averageScore,
      lastActive: formatRelativeTime(s.lastActiveTime),
      status: mapStatus(s.status),
      avatarBg: avatarBgs[i % avatarBgs.length],
    }))
  } catch (e) {
    error.value = e.message || '加载失败'
    console.error('获取班级数据失败:', e)
  } finally {
    loading.value = false
  }
})

function mapStatus(status) {
  if (status === 'ACTIVE') return 'active'
  if (status === 'INACTIVE') return 'inactive'
  return 'new'
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return '从未'
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

// 从学生数据计算汇总统计
const activeRate = computed(() => {
  if (!totalStudents.value) return '0%'
  return Math.round((activeStudents.value / totalStudents.value) * 100) + '%'
})

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  return students.value.filter(s => s.name.includes(searchQuery.value))
})

function getScoreClass(score) {
  if (score >= 85) return 'score-high'
  if (score >= 70) return 'score-mid'
  if (score > 0) return 'score-low'
  return ''
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
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--surface-elevated);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  color: var(--neutral-400);
  transition: all var(--duration-normal) var(--ease-out-expo);
}

.search-box:focus-within {
  border-color: var(--accent-400);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.search-input {
  border: none;
  background: none;
  color: var(--neutral-900);
  font-size: var(--text-sm);
  outline: none;
  width: 180px;
}

.search-input::placeholder {
  color: var(--neutral-400);
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

/* Table */
.card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  animation: fade-in-up 0.4s var(--ease-out) 0.1s backwards;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--neutral-500);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--neutral-200);
}

.data-table td {
  padding: var(--space-4);
  font-size: var(--text-sm);
  border-bottom: 1px solid var(--neutral-100);
}

.table-row {
  transition: background var(--duration-fast);
}

.table-row:hover {
  background: var(--neutral-50);
}

.student-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.student-avatar {
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

.student-name {
  display: block;
  font-weight: 500;
  color: var(--neutral-900);
}

.student-email {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.mono-value {
  font-family: var(--font-mono);
  font-weight: 600;
}

.score-high { color: var(--accent-500); }
.score-mid { color: var(--color-warning); }
.score-low { color: var(--color-error); }

.text-muted { color: var(--neutral-500); }

.status-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.status-tag.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-600);
}

.status-tag.inactive {
  background: var(--neutral-100);
  color: var(--neutral-500);
}

.status-tag.new {
  background: var(--accent-50);
  color: var(--accent-600);
}

.action-link {
  font-size: var(--text-sm);
  color: var(--accent-600);
  font-weight: 500;
  text-decoration: none;
}

.action-link:hover {
  color: var(--accent-700);
}

/* Summary */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.summary-card {
  text-align: center;
  animation: fade-in-up 0.4s var(--ease-out) 0.2s backwards;
}

.summary-title {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-bottom: var(--space-2);
}

.summary-value {
  display: block;
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: 700;
  margin-bottom: var(--space-1);
  color: var(--neutral-900);
}

.accent-value {
  color: var(--accent-500);
}

.summary-desc {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-4);
  }
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  .summary-grid {
    grid-template-columns: 1fr;
  }
  .data-table {
    font-size: var(--text-xs);
  }
}
</style>
