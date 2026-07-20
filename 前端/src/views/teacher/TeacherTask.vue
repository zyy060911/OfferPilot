<template>
  <AppLayout>
    <div class="teacher-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">任务发布</h1>
        <p class="page-desc">为班级布置面试练习任务</p>
      </div>
      <button class="btn-primary" @click="showCreate = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        创建任务
      </button>
    </div>

    <!-- Task List -->
    <div class="task-list">
      <div v-for="(task, i) in tasks" :key="i" class="task-card card" :style="{ animationDelay: (i * 0.06) + 's' }">
        <div class="task-header">
          <span class="task-status" :class="task.status">
            {{ task.status === 'active' ? '进行中' : task.status === 'completed' ? '已结束' : '未开始' }}
          </span>
          <span class="task-deadline">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            截止：{{ task.deadline }}
          </span>
        </div>
        <h3 class="task-title">{{ task.title }}</h3>
        <p class="task-desc">{{ task.desc }}</p>
        <div class="task-meta">
          <span class="meta-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>
            {{ task.position }}
          </span>
          <span class="meta-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
            {{ task.completed }}/{{ task.total }} 已完成
          </span>
          <span class="meta-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            平均 {{ task.avgScore }} 分
          </span>
        </div>
        <div class="task-progress">
          <div class="progress-bar-track">
            <div class="progress-bar" :style="{ width: (task.completed / task.total * 100) + '%' }"></div>
          </div>
          <span class="progress-label">{{ Math.round(task.completed / task.total * 100) }}%</span>
        </div>
      </div>
    </div>

    <!-- Create Task Modal -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal-card">
        <button class="modal-close" @click="showCreate = false">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <h2 class="modal-title">创建面试任务</h2>
        <div class="form-group">
          <label class="form-label">任务名称</label>
          <input type="text" class="form-input" placeholder="例如：前端开发第 3 次练习" />
        </div>
        <div class="form-group">
          <label class="form-label">目标岗位</label>
          <select class="form-select">
            <option>前端开发工程师</option>
            <option>Java 后端开发</option>
            <option>产品经理</option>
            <option>数据分析师</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">截止日期</label>
          <input type="date" class="form-input" />
        </div>
        <div class="form-group">
          <label class="form-label">任务说明（可选）</label>
          <textarea class="form-textarea" rows="3" placeholder="添加任务要求或说明..."></textarea>
        </div>
        <button class="btn-primary" style="width: 100%">发布任务</button>
      </div>
    </div>
    </div>
  </AppLayout>
</template>

<script setup>
// TODO: 接入后端 API - 接口待后端新增
import { ref } from 'vue'
import AppLayout from '../../components/layout/AppLayout.vue'

const showCreate = ref(false)

// 以下为硬编码数据，待后端任务 CRUD 接口就绪后替换
const tasks = [
  { title: '前端开发第 3 次练习', desc: '重点练习项目经验描述和技术原理问题，注意使用 STAR 法则组织回答。', position: '前端开发', deadline: '2026-07-15', status: 'active', completed: 18, total: 42, avgScore: 76 },
  { title: '产品经理模拟面试', desc: '完整模拟产品经理面试流程，包含行为面试和案例分析。', position: '产品经理', deadline: '2026-07-12', status: 'active', completed: 32, total: 42, avgScore: 72 },
  { title: '前端开发第 2 次练习', desc: '算法基础与框架原理。', position: '前端开发', deadline: '2026-07-08', status: 'completed', completed: 40, total: 42, avgScore: 78 },
  { title: '自我介绍专项训练', desc: '每人完成至少 2 次自我介绍练习。', position: '通用', deadline: '2026-07-05', status: 'completed', completed: 42, total: 42, avgScore: 81 },
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

/* Tasks */
.task-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.card {
  background: var(--surface-elevated);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: all var(--duration-normal) var(--ease-out-expo);
  animation: fade-in-up 0.4s var(--ease-out) backwards;
}

.card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--neutral-300);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.task-status {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-full);
}

.task-status.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-600);
}

.task-status.completed {
  background: var(--neutral-100);
  color: var(--neutral-500);
}

.task-status.upcoming {
  background: var(--accent-50);
  color: var(--accent-600);
}

.task-deadline {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.task-title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--neutral-900);
  margin-bottom: var(--space-2);
}

.task-desc {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  line-height: 1.6;
  margin-bottom: var(--space-4);
}

.task-meta {
  display: flex;
  gap: var(--space-6);
  margin-bottom: var(--space-4);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--neutral-500);
}

.task-progress {
  margin-top: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.progress-bar-track {
  flex: 1;
  height: 6px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--accent-500);
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out);
}

.progress-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--neutral-500);
  width: 32px;
  text-align: right;
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
  max-width: 480px;
  box-shadow: var(--shadow-lg);
  position: relative;
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
  margin-bottom: var(--space-6);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-700);
  margin-bottom: var(--space-2);
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  color: var(--neutral-900);
  font-size: var(--text-sm);
  font-family: var(--font-body);
  outline: none;
  transition: all var(--duration-normal) var(--ease-out-expo);
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: var(--accent-400);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-textarea {
  resize: vertical;
}
</style>
