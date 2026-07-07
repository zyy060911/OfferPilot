<template>
  <div class="page-shell">
    <div class="page-title">
      <span class="eyebrow"><el-icon><CircleCheck /></el-icon>第三步</span>
      <h2>确认面试信息</h2>
      <p>请仔细核对以下信息，确认无误后即可开始模拟面试。</p>
    </div>

    <!-- 空状态：未检测到面试准备数据 -->
    <div v-if="!prepStore.jobId" class="placeholder-card glass-panel">
      <el-icon :size="46"><WarningFilled /></el-icon>
      <p>未检测到面试准备数据，请先完成面试准备。</p>
      <el-button type="primary" @click="$router.push('/jobs')">前往面试准备</el-button>
    </div>

    <!-- 确认卡片 -->
    <div v-else class="confirm-card">
      <div class="summary-grid">
        <section class="summary-section">
          <h3><el-icon><User /></el-icon>候选人信息</h3>
          <dl>
            <div><dt>姓名</dt><dd>{{ prepStore.candidateName || '未填写' }}</dd></div>
            <div><dt>学校</dt><dd>{{ prepStore.candidateSchool || '未填写' }}</dd></div>
            <div><dt>专业</dt><dd>{{ prepStore.candidateMajor || '未填写' }}</dd></div>
            <div><dt>预计毕业</dt><dd>{{ prepStore.candidateGraduation || '未填写' }}</dd></div>
          </dl>
        </section>

        <section class="summary-section">
          <h3><el-icon><Setting /></el-icon>面试设置</h3>
          <dl>
            <div><dt>面试时长</dt><dd>{{ prepStore.duration }}</dd></div>
            <div><dt>难度等级</dt><dd>{{ prepStore.difficulty }}</dd></div>
            <div><dt>面试语言</dt><dd>{{ prepStore.language }}</dd></div>
          </dl>
        </section>

        <section class="summary-section">
          <h3><el-icon><Suitcase /></el-icon>目标岗位</h3>
          <dl>
            <div><dt>岗位名称</dt><dd>{{ prepStore.jobName || '未选择' }}</dd></div>
            <div><dt>相关技能</dt><dd>{{ prepStore.skills.length ? prepStore.skills.join('、') : '未选择' }}</dd></div>
          </dl>
        </section>

        <!-- 简历 / 项目经验（含 AI 提取功能） -->
        <section class="summary-section resume-section">
          <h3><el-icon><Document /></el-icon>简历 / 项目经验</h3>

          <!-- 上传的简历文件 -->
          <div v-if="prepStore.resumeFileName" class="uploaded-file">
            <el-icon><FolderOpened /></el-icon>
            <span>已上传简历：{{ prepStore.resumeFileName }}</span>
          </div>

          <!-- 手动填写的项目经验 -->
          <div v-if="prepStore.projectExperience" class="manual-project">
            <span class="manual-label">项目经验（手动填写）</span>
            <p>{{ prepStore.projectExperience }}</p>
          </div>

          <!-- 未提取：显示输入区 -->
          <div v-if="!extracted" class="resume-input">
            <el-input
              v-model="rawText"
              type="textarea"
              :rows="10"
              :placeholder="resumePlaceholder"
              maxlength="5000"
              show-word-limit
            />
            <div class="extract-btns">
              <el-button link type="primary" :icon="Notebook" @click="fillSample">填入示例</el-button>
              <el-button type="primary" :icon="MagicStick" :loading="extracting" @click="handleExtract">
                提取分析
              </el-button>
            </div>
          </div>

          <!-- 已提取：展示结果 -->
          <div v-else class="extracted-result">
            <div class="result-header">
              <span>AI 提取结果</span>
              <el-button link type="primary" @click="extracted = false">重新提取</el-button>
            </div>

            <div class="result-block">
              <h4>
                <el-icon><Star /></el-icon>
                技能关键词
                <small>{{ prepStore.extractedSkills.length }} 个</small>
              </h4>
              <div v-if="prepStore.extractedSkills.length" class="skill-tags">
                <el-tag v-for="s in prepStore.extractedSkills" :key="s" effect="light">{{ s }}</el-tag>
              </div>
              <el-text v-else type="info" size="small">未识别到技能关键词，可补充技术栈描述后重新提取。</el-text>
            </div>

            <div class="result-block">
              <h4>
                <el-icon><Files /></el-icon>
                项目经历
                <small>{{ prepStore.extractedProjects.length }} 段</small>
              </h4>
              <div v-if="prepStore.extractedProjects.length" class="project-list">
                <article v-for="(p, i) in prepStore.extractedProjects" :key="i" class="project-item">
                  <span class="project-index">{{ i + 1 }}</span>
                  <p>{{ p }}</p>
                </article>
              </div>
              <el-text v-else type="info" size="small">未识别到项目段落，可用"项目经历："开头分段后重新提取。</el-text>
            </div>
          </div>
        </section>
      </div>

      <div class="confirm-action">
        <el-checkbox v-model="confirmed" size="large">确认以上信息无误</el-checkbox>
        <el-button type="primary" size="large" :disabled="!confirmed" @click="startInterview">
          <el-icon><MagicStick /></el-icon>
          开始模拟面试
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  CircleCheck,
  Document,
  Files,
  FolderOpened,
  MagicStick,
  Notebook,
  Setting,
  Star,
  Suitcase,
  User,
  WarningFilled
} from '@element-plus/icons-vue'
import { useInterviewPrepStore } from '@/store/interviewPrep'
import { saveResume, getMyResume } from '@/api'

const router = useRouter()
const prepStore = useInterviewPrepStore()
const confirmed = ref(false)

// ---- 简历提取相关 ----
const rawText = ref('')
const extracted = ref(false)
const extracting = ref(false)

const resumePlaceholder =
  '例如：\n熟悉 Java 核心、JVM、并发编程，掌握 Spring Boot、MyBatis、Redis。\n\n项目经历：基于 Spring Boot + Redis 的高并发秒杀系统，使用消息队列削峰，解决高并发下的超卖问题。'

const parseList = (str) => {
  try {
    return JSON.parse(str || '[]')
  } catch {
    return []
  }
}

const fillSample = () => {
  rawText.value =
    '熟悉 Java 核心、JVM 内存模型与垃圾回收、并发编程（多线程、锁、线程池），掌握 Spring Boot、Spring Cloud、MyBatis，熟练使用 MySQL、Redis，了解 Kafka 消息队列与分布式微服务。\n\n' +
    '项目经历：基于 Spring Boot + Redis 的高并发秒杀系统。使用 Redis 预减库存、Kafka 削峰，通过分布式锁解决超卖问题，QPS 从 200 提升到 3000。\n\n' +
    '项目经历：校园二手交易平台。Vue3 + Element Plus 前端，Spring Boot 后端，实现商品发布、即时聊天与订单管理。'
}

const handleExtract = async () => {
  if (!rawText.value.trim()) {
    ElMessage.warning('请先填写简历内容')
    return
  }
  extracting.value = true
  try {
    const resume = await saveResume({ rawText: rawText.value })
    prepStore.setExtracted({
      skills: parseList(resume.skills),
      projects: parseList(resume.projects)
    })
    extracted.value = true
    ElMessage.success('已提取并保存')
  } catch {
    // 错误由请求拦截器统一处理
  } finally {
    extracting.value = false
  }
}

// ---- 进入面试 ----
const difficultyMap = { '简单': 1, '中等': 2, '困难': 3 }

const startInterview = () => {
  if (!confirmed.value || !prepStore.jobId) return
  const d = difficultyMap[prepStore.difficulty] || 2
  router.push({
    path: '/interview',
    query: { jobId: prepStore.jobId, difficulty: d, resumeReady: 1 }
  })
}

// 挂载时尝试加载历史简历数据
onMounted(async () => {
  try {
    const resume = await getMyResume()
    if (resume) {
      const skills = parseList(resume.skills)
      const projects = parseList(resume.projects)
      if (skills.length || projects.length) {
        prepStore.setExtracted({ skills, projects })
        rawText.value = resume.rawText || ''
        extracted.value = true
      }
    }
  } catch {
    // 静默失败，不影响页面使用
  }
})
</script>

<style scoped>
.confirm-card {
  padding: 32px;
  background: #fff;
  border: 1px solid #dce6f2;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28px 48px;
}

.summary-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  color: #1b2d49;
  font-size: 16px;
  font-weight: 900;
}

.summary-section h3 .el-icon {
  font-size: 20px;
  color: var(--primary);
}

.summary-section dl {
  display: grid;
  gap: 14px;
}

.summary-section dl > div {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: 12px;
}

.summary-section dt {
  color: #7b879c;
  font-size: 13px;
  font-weight: 800;
}

.summary-section dd {
  min-width: 0;
  color: #1b2d49;
  font-size: 14px;
  font-weight: 800;
  word-break: break-word;
}

/* ---- 简历/项目经验区块 ---- */
.resume-section {
  grid-column: 1 / -1;
}

.uploaded-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding: 10px 14px;
  color: #34435f;
  background: #f4f8fc;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.uploaded-file .el-icon {
  color: var(--primary);
  font-size: 18px;
}

.manual-project {
  margin-bottom: 16px;
  padding: 12px 14px;
  background: #f8fbff;
  border: 1px solid #dce6f2;
  border-radius: 6px;
}

.manual-label {
  display: block;
  margin-bottom: 6px;
  color: #7b879c;
  font-size: 12px;
  font-weight: 700;
}

.manual-project p {
  margin: 0;
  color: #1b2d49;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.7;
  white-space: pre-wrap;
}

.resume-input {
  margin-top: 4px;
}

.resume-input :deep(.el-textarea__inner) {
  min-height: 200px;
  font-size: 14px;
  line-height: 1.7;
}

.extract-btns {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.extract-btns .el-button--primary {
  min-width: 140px;
}

/* ---- 提取结果 ---- */
.extracted-result {
  margin-top: 8px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.result-header > span {
  color: #16a76a;
  font-size: 13px;
  font-weight: 700;
}

.result-block {
  margin-bottom: 16px;
}

.result-block h4 {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  color: #1b2d49;
  font-size: 14px;
  font-weight: 800;
}

.result-block h4 .el-icon {
  color: var(--primary);
  font-size: 16px;
}

.result-block h4 small {
  color: #7b879c;
  font-weight: 600;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tags .el-tag {
  font-weight: 600;
}

.project-list {
  display: grid;
  gap: 10px;
}

.project-item {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
}

.project-index {
  display: grid;
  width: 28px;
  height: 28px;
  color: var(--primary);
  place-items: center;
  background: rgba(37, 99, 235, 0.09);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 800;
}

.project-item p {
  margin: 0;
  color: #1b2d49;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.7;
}

/* ---- 确认操作栏 ---- */
.confirm-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #dce6f2;
}

.confirm-action :deep(.el-checkbox) {
  color: #1b2d49;
  font-size: 15px;
  font-weight: 700;
}

.confirm-action .el-button {
  min-width: 200px;
  height: 56px;
  font-size: 18px;
  font-weight: 950;
  border-radius: 12px;
}

/* ---- 空状态 ---- */
.placeholder-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 360px;
  padding: 48px 24px;
  text-align: center;
  border-radius: 8px;
}

.placeholder-card .el-icon {
  color: #c0c8d6;
}

.placeholder-card p {
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.8;
}

.placeholder-card .el-button {
  margin-top: 8px;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .confirm-card {
    padding: 22px 16px;
  }

  .confirm-action {
    flex-direction: column;
    gap: 16px;
  }

  .confirm-action .el-button {
    width: 100%;
  }
}
</style>
