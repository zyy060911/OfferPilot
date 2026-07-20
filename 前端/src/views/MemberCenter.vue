<template>
  <AppLayout>
    <div class="member-page">
    <!-- Current Status Card -->
    <div class="member-status-card">
      <div class="status-bg"></div>
      <div class="status-content">
        <div class="status-left">
          <span class="status-greeting">{{ userName }}，你好</span>
          <div class="status-plan">
            <span class="plan-label">当前方案</span>
            <span class="plan-name">免费版</span>
          </div>
          <div class="status-usage">
            <span class="usage-text">已使用 {{ usedCount }}/{{ totalCount }} 次面试机会</span>
            <div class="usage-bar">
              <div class="usage-fill" :style="{ width: usagePercent + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="status-right">
          <button class="upgrade-main-btn" @click="showUpgrade = true">
            立即升级，解锁无限面试
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Pricing Comparison -->
    <div class="pricing-section">
      <h2 class="section-title">方案对比</h2>
      <div class="pricing-grid">
        <!-- Free Plan -->
        <div class="plan-card">
          <div class="plan-header">
            <span class="plan-icon">🆓</span>
            <h3 class="plan-title">免费版</h3>
            <div class="plan-price">
              <span class="price-amount">¥0</span>
              <span class="price-period">永久免费</span>
            </div>
          </div>
          <div class="plan-features">
            <div class="feature-row" v-for="f in freeFeatures" :key="f.name">
              <svg v-if="f.included" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-500)" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--neutral-300)" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
              <span :class="{ disabled: !f.included }">{{ f.name }}</span>
            </div>
          </div>
          <button class="plan-btn current">当前方案</button>
        </div>

        <!-- Pro Plan -->
        <div class="plan-card pro">
          <div class="pro-badge">推荐</div>
          <div class="plan-header">
            <span class="plan-icon">⚡</span>
            <h3 class="plan-title">Pro 版</h3>
            <div class="plan-price">
              <span class="price-amount">¥<span class="price-big">29</span></span>
              <span class="price-period">/月</span>
            </div>
            <span class="price-annual">年付 ¥288（省 ¥60）</span>
          </div>
          <div class="plan-features">
            <div class="feature-row" v-for="f in proFeatures" :key="f.name">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-500)" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{{ f.name }}</span>
              <span v-if="f.tag" class="feature-tag">{{ f.tag }}</span>
            </div>
          </div>
          <button class="plan-btn upgrade" @click="showUpgrade = true">立即升级</button>
        </div>

        <!-- Enterprise Plan -->
        <div class="plan-card">
          <div class="plan-header">
            <span class="plan-icon">🏫</span>
            <h3 class="plan-title">院校版</h3>
            <div class="plan-price">
              <span class="price-amount">定制</span>
              <span class="price-period">按需报价</span>
            </div>
          </div>
          <div class="plan-features">
            <div class="feature-row" v-for="f in enterpriseFeatures" :key="f.name">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-500)" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{{ f.name }}</span>
            </div>
          </div>
          <button class="plan-btn contact">联系我们</button>
        </div>
      </div>
    </div>

    <!-- FAQ -->
    <div class="faq-section">
      <h2 class="section-title">常见问题</h2>
      <div class="faq-list">
        <div v-for="(faq, i) in faqs" :key="i" class="faq-item" :class="{ expanded: expandedFaq === i }">
          <button class="faq-question" @click="expandedFaq = expandedFaq === i ? -1 : i">
            <span>{{ faq.q }}</span>
            <svg :class="['faq-arrow', { rotated: expandedFaq === i }]" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div v-if="expandedFaq === i" class="faq-answer">
            <p>{{ faq.a }}</p>
          </div>
        </div>
      </div>
    </div>
    </div>

    <!-- Upgrade Modal -->
    <div v-if="showUpgrade" class="modal-overlay" @click.self="showUpgrade = false">
      <div class="modal-card">
        <button class="modal-close" @click="showUpgrade = false">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <div class="modal-header">
          <h2 class="modal-title">升级到 Pro 版</h2>
          <p class="modal-desc">解锁全部功能，加速你的面试准备</p>
        </div>
        <div class="plan-options">
          <button
            v-for="plan in upgradePlans"
            :key="plan.id"
            :class="['option-card', { selected: selectedPlan === plan.id }]"
            @click="selectedPlan = plan.id"
          >
            <span v-if="plan.recommended" class="option-badge">推荐</span>
            <span class="option-period">{{ plan.period }}</span>
            <span class="option-price">¥{{ plan.price }}</span>
            <span class="option-unit">{{ plan.unit }}</span>
            <span v-if="plan.save" class="option-save">{{ plan.save }}</span>
          </button>
        </div>
        <div class="payment-methods">
          <span class="pay-label">支付方式</span>
          <div class="pay-options">
            <button :class="['pay-btn', { active: payMethod === 'wechat' }]" @click="payMethod = 'wechat'">
              <span class="pay-icon-wechat">W</span> 微信支付
            </button>
            <button :class="['pay-btn', { active: payMethod === 'alipay' }]" @click="payMethod = 'alipay'">
              <span class="pay-icon-alipay">A</span> 支付宝
            </button>
          </div>
        </div>
        <button class="confirm-pay-btn">
          确认支付 ¥{{ selectedPlanData?.price || '29' }}
        </button>
        <p class="pay-note">支付即表示同意《服务协议》和《隐私政策》</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'

const userName = ref('张同学')
const usedCount = ref(12)
const totalCount = ref(15)
const usagePercent = computed(() => (usedCount.value / totalCount.value) * 100)
const showUpgrade = ref(false)
const selectedPlan = ref('monthly')
const payMethod = ref('wechat')
const expandedFaq = ref(-1)

const freeFeatures = [
  { name: '每月 15 次面试', included: true },
  { name: '基础岗位覆盖', included: true },
  { name: '初级/中级难度', included: true },
  { name: '面试报告查看', included: true },
  { name: '报告导出 PDF/Word', included: false },
  { name: '追问深度分析', included: false },
  { name: '能力趋势追踪', included: false },
  { name: '高级岗位解锁', included: false },
]

const proFeatures = [
  { name: '无限次面试', tag: '无限制' },
  { name: '全部岗位覆盖', tag: '' },
  { name: '初级/中级/高级难度', tag: '' },
  { name: '面试报告 + 导出', tag: 'PDF & Word' },
  { name: '追问深度分析', tag: '' },
  { name: '能力趋势追踪', tag: '' },
  { name: '优先体验新功能', tag: '' },
  { name: 'VR 面试官（即将上线）', tag: '抢先体验' },
]

const enterpriseFeatures = [
  { name: 'Pro 版全部功能' },
  { name: '教师端管理后台' },
  { name: '班级管理与统计' },
  { name: '共性短板分析' },
  { name: '任务发布系统' },
  { name: '专属客服支持' },
  { name: '数据安全保障' },
]

const upgradePlans = [
  { id: 'monthly', period: '月付', price: '29', unit: '/月', save: '', recommended: false },
  { id: 'quarterly', period: '季付', price: '79', unit: '/季', save: '省 ¥8', recommended: false },
  { id: 'yearly', period: '年付', price: '288', unit: '/年', save: '省 ¥60', recommended: true },
]

const selectedPlanData = computed(() => upgradePlans.find(p => p.id === selectedPlan.value))

const faqs = [
  { q: '升级后可以退款吗？', a: '支持 7 天无理由退款。如果在购买后 7 天内对产品不满意，可以联系客服申请全额退款。' },
  { q: '免费版的面试次数什么时候重置？', a: '每月 1 日 00:00 自动重置。未使用的次数不会累积到下个月。' },
  { q: 'Pro 版到期后数据会丢失吗？', a: '不会。到期后你的历史数据、面试记录和报告都会保留，只是无法使用 Pro 功能。续费后即可恢复。' },
  { q: '支持哪些支付方式？', a: '支持微信支付和支付宝。院校版支持对公转账。' },
]
</script>

<style scoped>
.member-page {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--space-8) 0 var(--space-16);
}

/* Status Card */
.member-status-card {
  position: relative;
  border-radius: var(--radius-xl);
  overflow: hidden;
  margin-bottom: var(--space-8);
  animation: fade-in-up 0.4s var(--ease-out-expo);
}

.status-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--accent-600), var(--accent-500));
}

.status-content {
  position: relative;
  padding: var(--space-8);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-8);
}

.status-greeting {
  display: block;
  font-size: var(--text-lg);
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: var(--space-4);
}

.plan-label {
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.plan-name {
  display: block;
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: white;
  margin-top: var(--space-1);
}

.status-usage {
  margin-top: var(--space-4);
}

.usage-text {
  font-size: var(--text-sm);
  color: rgba(255, 255, 255, 0.6);
  font-family: var(--font-mono);
}

.usage-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-full);
  margin-top: var(--space-2);
  overflow: hidden;
  width: 240px;
}

.usage-fill {
  height: 100%;
  background: rgba(255, 255, 255, 0.85);
  border-radius: var(--radius-full);
  transition: width 1s var(--ease-out-expo);
}

.upgrade-main-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-8);
  background: white;
  border: none;
  border-radius: var(--radius-md);
  color: var(--accent-700);
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 700;
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out-expo);
  box-shadow: var(--shadow-lg);
}

.upgrade-main-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

/* Section Title */
.section-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
  margin-bottom: var(--space-8);
}

/* Pricing Grid */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
  margin-bottom: var(--space-12);
}

.plan-card {
  background: var(--surface-elevated);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  position: relative;
  transition: all var(--duration-slow) var(--ease-out-expo);
  animation: fade-in-up 0.4s var(--ease-out-expo) backwards;
}

.plan-card:nth-child(2) { animation-delay: 0.1s; }
.plan-card:nth-child(3) { animation-delay: 0.2s; }

.plan-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.plan-card.pro {
  border-color: var(--accent-400);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.12);
}

.pro-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  padding: var(--space-1) var(--space-4);
  background: var(--accent-500);
  color: white;
  font-size: var(--text-xs);
  font-weight: 700;
  border-radius: var(--radius-full);
  letter-spacing: 0.05em;
}

.plan-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.plan-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: var(--space-2);
}

.plan-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.plan-price {
  margin-top: var(--space-3);
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}

.price-amount {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--neutral-900);
}

.price-big {
  font-size: var(--text-4xl);
}

.price-period {
  font-size: var(--text-sm);
  color: var(--neutral-500);
}

.price-annual {
  display: block;
  font-size: var(--text-xs);
  color: var(--accent-600);
  margin-top: var(--space-1);
}

/* Features */
.plan-features {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.feature-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--neutral-700);
}

.feature-row .disabled {
  color: var(--neutral-400);
}

.feature-tag {
  font-size: 10px;
  padding: 1px 6px;
  background: var(--accent-50);
  color: var(--accent-600);
  border-radius: var(--radius-full);
  font-weight: 600;
}

/* Plan Buttons */
.plan-btn {
  width: 100%;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  font-family: var(--font-display);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-normal);
}

.plan-btn.current {
  background: var(--neutral-100);
  border: 1.5px solid var(--neutral-200);
  color: var(--neutral-500);
  cursor: default;
}

.plan-btn.upgrade {
  background: var(--accent-500);
  border: none;
  color: white;
  box-shadow: var(--shadow-accent);
}

.plan-btn.upgrade:hover {
  background: var(--accent-600);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.plan-btn.contact {
  background: var(--surface-elevated);
  border: 1.5px solid var(--accent-400);
  color: var(--accent-600);
}

.plan-btn.contact:hover {
  background: var(--accent-50);
}

/* FAQ */
.faq-section {
  max-width: 700px;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.faq-item {
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--duration-fast);
}

.faq-item.expanded {
  border-color: var(--accent-300);
}

.faq-question {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--surface-elevated);
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-800);
  text-align: left;
  transition: background var(--duration-fast);
}

.faq-question:hover {
  background: var(--accent-50);
}

.faq-arrow {
  color: var(--neutral-400);
  transition: transform var(--duration-normal) var(--ease-out-expo);
  flex-shrink: 0;
}

.faq-arrow.rotated {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 var(--space-4) var(--space-4);
  animation: fade-in 0.2s var(--ease-out-expo);
}

.faq-answer p {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  line-height: 1.7;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fade-in 0.2s var(--ease-out-expo);
}

.modal-card {
  background: var(--surface-elevated);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  width: 100%;
  max-width: 480px;
  position: relative;
  animation: fade-in-up 0.3s var(--ease-out-expo);
  box-shadow: var(--shadow-lg);
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
  color: var(--neutral-700);
  background: var(--neutral-100);
}

.modal-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.modal-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.modal-desc {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-top: var(--space-1);
}

/* Plan Options */
.plan-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.option-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-4);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  background: var(--surface-elevated);
  cursor: pointer;
  transition: all var(--duration-normal);
  position: relative;
}

.option-card:hover {
  border-color: var(--neutral-300);
}

.option-card.selected {
  border-color: var(--accent-500);
  background: var(--accent-50);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.12);
}

.option-badge {
  position: absolute;
  top: -10px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  background: var(--accent-500);
  color: white;
  border-radius: var(--radius-full);
}

.option-period {
  font-size: var(--text-sm);
  color: var(--neutral-600);
}

.option-price {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
}

.option-unit {
  font-size: var(--text-xs);
  color: var(--neutral-500);
}

.option-save {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-600);
}

/* Payment */
.payment-methods {
  margin-bottom: var(--space-6);
}

.pay-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-700);
  margin-bottom: var(--space-3);
}

.pay-options {
  display: flex;
  gap: var(--space-3);
}

.pay-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1.5px solid var(--neutral-200);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-700);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.pay-btn:hover {
  border-color: var(--neutral-300);
}

.pay-btn.active {
  border-color: var(--accent-500);
  background: var(--accent-50);
  color: var(--accent-700);
}

.pay-icon-wechat {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #07c160;
  color: white;
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 700;
}

.pay-icon-alipay {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #1677ff;
  color: white;
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 700;
}

.confirm-pay-btn {
  width: 100%;
  padding: var(--space-4);
  background: var(--accent-500);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 700;
  cursor: pointer;
  transition: all var(--duration-normal);
  box-shadow: var(--shadow-accent);
}

.confirm-pay-btn:hover {
  background: var(--accent-600);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.pay-note {
  text-align: center;
  font-size: var(--text-xs);
  color: var(--neutral-400);
  margin-top: var(--space-3);
}

@media (max-width: 1024px) {
  .pricing-grid { grid-template-columns: 1fr; max-width: 400px; }
  .status-content { flex-direction: column; text-align: center; }
  .usage-bar { width: 100%; }
}

@media (max-width: 768px) {
  .plan-options { grid-template-columns: 1fr; }
  .pay-options { flex-direction: column; }
}
</style>
