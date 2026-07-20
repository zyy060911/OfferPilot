<template>
  <AppLayout>
    <div class="teacher-page">
    <router-link to="/teacher/class" class="back-link">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
      返回班级管理
    </router-link>

    <!-- Student Header -->
    <div class="student-header card">
      <div class="sh-avatar">李</div>
      <div class="sh-info">
        <h1 class="sh-name">李明</h1>
        <p class="sh-email">liming@edu.cn · 加入于 2026-06-15</p>
      </div>
      <div class="sh-stats">
        <div class="sh-stat"><span class="sh-stat-value">12</span><span class="sh-stat-label">面试次数</span></div>
        <div class="sh-stat"><span class="sh-stat-value accent-val">88</span><span class="sh-stat-label">平均得分</span></div>
        <div class="sh-stat"><span class="sh-stat-value">5天</span><span class="sh-stat-label">连续练习</span></div>
      </div>
    </div>

    <!-- Content -->
    <div class="student-grid">
      <!-- Radar -->
      <div class="card">
        <h2 class="card-title">能力雷达图</h2>
        <RadarChart :labels="radarLabels" :values="radarValues" />
      </div>

      <!-- Interview History -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">面试记录</h2>
        </div>
        <div class="record-list">
          <div v-for="(r, i) in records" :key="i" class="record-item">
            <div class="record-info">
              <span class="record-position">{{ r.position }}</span>
              <span class="record-date">{{ r.date }}</span>
            </div>
            <span class="record-score" :class="getScoreClass(r.score)">{{ r.score }}分</span>
          </div>
        </div>
      </div>

      <!-- Growth Trend -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">成长趋势</h2>
          <span class="card-subtitle">最近 5 次</span>
        </div>
        <div class="trend-list">
          <div v-for="(t, i) in trendData" :key="i" class="trend-item">
            <span class="trend-date">{{ t.date }}</span>
            <div class="trend-bar-track">
              <div class="trend-bar" :style="{ width: t.score + '%' }"></div>
            </div>
            <span class="trend-score" :class="getScoreClass(t.score)">{{ t.score }}</span>
          </div>
        </div>
      </div>

      <!-- Teacher Notes -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">教师备注</h2>
          <button class="btn-text">编辑</button>
        </div>
        <div class="notes-content">
          <p>该学生基础扎实，表达能力优秀。主要短板在于追问环节的逻辑组织，建议加强 STAR 法则训练。推荐安排一次 1v1 辅导。</p>
        </div>
      </div>
    </div>
    </div>
  </AppLayout>
</template>

<script setup>
// TODO: 接入后端 API - 接口待后端新增 GET /api/teacher/students/:id
import AppLayout from '../../components/layout/AppLayout.vue'
import RadarChart from '../../components/ui/RadarChart.vue'

const radarLabels = ['表达能力', '逻辑性', '技术深度', '岗位匹配', '抗压能力']
const radarValues = [92, 78, 88, 82, 70]

const records = [
  { position: '前端开发工程师', date: '2026-07-11', score: 88 },
  { position: '前端开发工程师', date: '2026-07-09', score: 85 },
  { position: '产品经理', date: '2026-07-07', score: 91 },
  { position: '前端开发工程师', date: '2026-07-05', score: 82 },
  { position: '数据分析师', date: '2026-07-03', score: 79 },
]

const trendData = [
  { date: '07-03', score: 79 },
  { date: '07-05', score: 82 },
  { date: '07-07', score: 91 },
  { date: '07-09', score: 85 },
  { date: '07-11', score: 88 },
]

function getScoreClass(score) {
  if (score >= 85) return 'score-high'
  if (score >= 70) return 'score-mid'
  return 'score-low'
}
</script>

<style scoped>
.teacher-page {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--space-8) 0 var(--space-16);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-bottom: var(--space-6);
  text-decoration: none;
  transition: color var(--duration-fast);
}

.back-link:hover {
  color: var(--accent-600);
}

.card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  animation: fade-in-up 0.4s var(--ease-out);
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

/* Header */
.student-header {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.sh-avatar {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--accent-400), var(--accent-600));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-2xl);
  font-weight: 700;
  color: white;
}

.sh-name {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.sh-email {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-top: var(--space-1);
}

.sh-stats {
  display: flex;
  gap: var(--space-8);
  margin-left: auto;
}

.sh-stat {
  text-align: center;
}

.sh-stat-value {
  display: block;
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.accent-val {
  color: var(--accent-500);
}

.sh-stat-label {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

/* Grid */
.student-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

/* Records */
.record-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast);
}

.record-item:hover {
  background: var(--neutral-50);
}

.record-position {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-900);
}

.record-date {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.record-score {
  font-family: var(--font-mono);
  font-weight: 700;
}

.score-high { color: var(--accent-500); }
.score-mid { color: var(--color-warning); }
.score-low { color: var(--color-error); }

/* Trend */
.trend-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.trend-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.trend-date {
  width: 40px;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.trend-bar-track {
  flex: 1;
  height: 8px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.trend-bar {
  height: 100%;
  background: var(--accent-500);
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out);
}

.trend-score {
  width: 28px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 700;
}

/* Notes */
.notes-content p {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  line-height: 1.7;
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
  color: var(--accent-700);
}

@media (max-width: 1024px) {
  .student-grid { grid-template-columns: 1fr; }
  .student-header { flex-wrap: wrap; }
  .sh-stats { margin-left: 0; }
}
</style>
