<template>
  <AppLayout>
    <div class="teacher-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">报告分析</h1>
        <p class="page-desc">班级整体能力分布与趋势分析</p>
      </div>
      <div class="header-actions">
        <select v-model="timeRange" class="filter-select">
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="all">全部</option>
        </select>
        <button class="btn-outline">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          导出报告
        </button>
      </div>
    </div>

    <!-- Score Distribution -->
    <div class="report-grid">
      <div class="card">
        <h2 class="card-title">得分分布</h2>
        <div class="distribution-chart">
          <div v-for="(range, i) in scoreDistribution" :key="i" class="dist-bar-group">
            <div class="dist-bar-track">
              <div class="dist-bar" :style="{ height: range.percent + '%', background: range.color }"></div>
            </div>
            <span class="dist-label">{{ range.label }}</span>
            <span class="dist-count">{{ range.count }}人</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="card-title">岗位分布</h2>
        <div class="job-distribution">
          <div v-for="(j, i) in jobDistribution" :key="i" class="job-item">
            <div class="job-icon" :style="{ background: j.iconBg }">{{ j.name.charAt(0) }}</div>
            <div class="job-info">
              <span class="job-name">{{ j.name }}</span>
              <div class="job-bar-track">
                <div class="job-bar" :style="{ width: j.percent + '%', background: j.color }"></div>
              </div>
            </div>
            <span class="job-count">{{ j.count }}次</span>
          </div>
        </div>
      </div>

      <!-- Ability Comparison -->
      <div class="card full-width">
        <h2 class="card-title">能力维度对比（班级平均 vs 全平台）</h2>
        <div class="comparison-grid">
          <div v-for="(item, i) in abilityComparison" :key="i" class="comp-item">
            <span class="comp-name">{{ item.name }}</span>
            <div class="comp-bars">
              <div class="comp-bar-row">
                <span class="comp-bar-label">班级</span>
                <div class="comp-bar-track">
                  <div class="comp-bar class-bar" :style="{ width: item.class + '%' }"></div>
                </div>
                <span class="comp-value">{{ item.class }}</span>
              </div>
              <div class="comp-bar-row">
                <span class="comp-bar-label">全平台</span>
                <div class="comp-bar-track">
                  <div class="comp-bar platform-bar" :style="{ width: item.platform + '%' }"></div>
                </div>
                <span class="comp-value">{{ item.platform }}</span>
              </div>
            </div>
            <span class="comp-diff" :class="item.diff >= 0 ? 'positive' : 'negative'">
              {{ item.diff >= 0 ? '+' : '' }}{{ item.diff }}
            </span>
          </div>
        </div>
      </div>

      <!-- Top Performers -->
      <div class="card">
        <h2 class="card-title">优秀学生 TOP 5</h2>
        <div class="top-list">
          <div v-for="(s, i) in topStudents" :key="i" class="top-item">
            <span class="top-rank" :class="'rank-' + (i + 1)">{{ i + 1 }}</span>
            <div class="top-avatar" :style="{ background: s.avatarBg }">{{ s.name.charAt(0) }}</div>
            <div class="top-info">
              <span class="top-name">{{ s.name }}</span>
              <span class="top-meta">{{ s.count }} 次面试</span>
            </div>
            <span class="top-score accent-score">{{ s.avg }}</span>
          </div>
        </div>
      </div>

      <!-- Needs Attention -->
      <div class="card">
        <h2 class="card-title">需要关注</h2>
        <div class="attention-list">
          <div v-for="(s, i) in needsAttention" :key="i" class="attention-item">
            <div class="attention-avatar" :style="{ background: s.avatarBg }">{{ s.name.charAt(0) }}</div>
            <div class="attention-info">
              <span class="attention-name">{{ s.name }}</span>
              <span class="attention-reason">{{ s.reason }}</span>
            </div>
            <span class="attention-action">{{ s.action }}</span>
          </div>
        </div>
      </div>
    </div>
    </div>
  </AppLayout>
</template>

<script setup>
// TODO: 接入后端 API - 接口待后端新增
import { ref } from 'vue'
import AppLayout from '../../components/layout/AppLayout.vue'

const timeRange = ref('week')

// 以下为硬编码数据，待后端报告分析接口就绪后替换
const scoreDistribution = [
  { label: '90-100', count: 5, percent: 12, color: '#10b981' },
  { label: '80-89', count: 12, percent: 29, color: '#059669' },
  { label: '70-79', count: 15, percent: 36, color: '#34d399' },
  { label: '60-69', count: 7, percent: 17, color: '#f59e0b' },
  { label: '<60', count: 3, percent: 7, color: '#ef4444' },
]

const jobDistribution = [
  { name: '前端开发', count: 85, percent: 40, color: '#10b981', iconBg: 'rgba(16,185,129,0.1)' },
  { name: '产品经理', count: 45, percent: 21, color: '#059669', iconBg: 'rgba(5,150,105,0.1)' },
  { name: '后端开发', count: 38, percent: 18, color: '#34d399', iconBg: 'rgba(52,211,153,0.1)' },
  { name: '数据分析师', count: 28, percent: 13, color: '#6ee7b7', iconBg: 'rgba(110,231,183,0.1)' },
  { name: 'UI 设计师', count: 17, percent: 8, color: '#a7f3d0', iconBg: 'rgba(167,243,208,0.15)' },
]

const abilityComparison = [
  { name: '表达能力', class: 78, platform: 72, diff: 6 },
  { name: '逻辑性', class: 72, platform: 70, diff: 2 },
  { name: '技术深度', class: 68, platform: 74, diff: -6 },
  { name: '岗位匹配', class: 75, platform: 71, diff: 4 },
  { name: '抗压能力', class: 62, platform: 66, diff: -4 },
]

const topStudents = [
  { name: '李明', avg: 88, count: 12, avatarBg: 'rgba(16,185,129,0.1)' },
  { name: '孙丽', avg: 83, count: 10, avatarBg: 'rgba(52,211,153,0.1)' },
  { name: '张伟', avg: 81, count: 15, avatarBg: 'rgba(5,150,105,0.1)' },
  { name: '陈静', avg: 78, count: 3, avatarBg: 'rgba(16,185,129,0.15)' },
  { name: '周杰', avg: 76, count: 8, avatarBg: 'rgba(110,231,183,0.1)' },
]

const needsAttention = [
  { name: '赵磊', reason: '仅完成 1 次面试，已 3 天未活跃', action: '建议联系', avatarBg: 'rgba(239,68,68,0.1)' },
  { name: '刘洋', reason: '连续 3 次得分低于 70，技术深度不足', action: '安排辅导', avatarBg: 'rgba(245,158,11,0.1)' },
  { name: '周杰', reason: '从未完成过面试', action: '了解情况', avatarBg: 'rgba(16,185,129,0.08)' },
]
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

.filter-select {
  padding: var(--space-2) var(--space-4);
  background: var(--surface-elevated);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  color: var(--neutral-700);
  font-size: var(--text-sm);
  outline: none;
  transition: all var(--duration-normal) var(--ease-out-expo);
}

.filter-select:focus {
  border-color: var(--accent-400);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
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
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-expo);
}

.btn-outline:hover {
  border-color: var(--neutral-300);
  background: var(--neutral-50);
}

/* Grid */
.report-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

.full-width {
  grid-column: 1 / -1;
}

.card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  animation: fade-in-up 0.4s var(--ease-out) 0.1s backwards;
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--neutral-900);
  margin-bottom: var(--space-5);
}

/* Distribution Chart */
.distribution-chart {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 180px;
  gap: var(--space-4);
}

.dist-bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  height: 100%;
}

.dist-bar-track {
  flex: 1;
  width: 100%;
  background: var(--neutral-100);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.dist-bar {
  width: 100%;
  border-radius: var(--radius-sm);
  transition: height 1s var(--ease-out);
  min-height: 4px;
}

.dist-label {
  font-size: 11px;
  color: var(--neutral-500);
}

.dist-count {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--neutral-700);
}

/* Job Distribution */
.job-distribution {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.job-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.job-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--accent-600);
  flex-shrink: 0;
}

.job-info {
  flex: 1;
}

.job-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-800);
  margin-bottom: 4px;
}

.job-bar-track {
  height: 6px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.job-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out);
}

.job-count {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-700);
}

/* Ability Comparison */
.comparison-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.comp-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.comp-name {
  width: 72px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-700);
  flex-shrink: 0;
}

.comp-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comp-bar-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.comp-bar-label {
  width: 40px;
  font-size: 11px;
  color: var(--neutral-500);
}

.comp-bar-track {
  flex: 1;
  height: 8px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.comp-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out);
}

.class-bar {
  background: var(--accent-500);
}

.platform-bar {
  background: var(--neutral-300);
}

.comp-value {
  width: 28px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--neutral-700);
}

.comp-diff {
  width: 40px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 700;
}

.comp-diff.positive { color: var(--accent-500); }
.comp-diff.negative { color: var(--color-error); }

/* Top Students */
.top-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.top-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast);
}

.top-item:hover {
  background: var(--neutral-50);
}

.top-rank {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.rank-1 {
  background: linear-gradient(135deg, #f59e0b, #10b981);
  color: white;
}

.rank-2 {
  background: var(--neutral-300);
  color: white;
}

.rank-3 {
  background: #a7f3d0;
  color: var(--accent-700);
}

.top-item:nth-child(n+4) .top-rank {
  background: var(--neutral-100);
  color: var(--neutral-500);
}

.top-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--accent-600);
}

.top-info {
  flex: 1;
}

.top-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-900);
}

.top-meta {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.top-score {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: 700;
}

.accent-score {
  color: var(--accent-500);
}

/* Attention */
.attention-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.attention-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(239, 68, 68, 0.03);
  border-radius: var(--radius-md);
  border-left: 3px solid rgba(239, 68, 68, 0.25);
}

.attention-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-error);
}

.attention-info {
  flex: 1;
}

.attention-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--neutral-800);
}

.attention-reason {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.attention-action {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 10px;
  background: rgba(239, 68, 68, 0.08);
  color: var(--color-error);
  border-radius: var(--radius-full);
  white-space: nowrap;
}

@media (max-width: 1024px) {
  .report-grid { grid-template-columns: 1fr; }
  .full-width { grid-column: auto; }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-4);
  }
  .header-actions {
    width: 100%;
  }
  .filter-select {
    flex: 1;
  }
}
</style>
