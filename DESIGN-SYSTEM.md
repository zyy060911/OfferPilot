# 智面幻境 OfferPilot — 设计系统

## 一、设计优化方向（基于 2026 趋势）

### 原始设计问题诊断
| 问题 | 优化方案 |
|------|---------|
| 赛博朋克风过于夸张，可能影响可读性 | 保留科技感但降低霓虹强度，采用「克制赛博」风格 |
| 玻璃态卡片过度使用导致视觉疲劳 | 分层级使用：主导航用强玻璃态，内容区用弱玻璃态 |
| 粒子背景可能影响性能 | 用 CSS 渐变动画替代 canvas 粒子，关键页面保留轻量粒子 |
| 非对称网格可能造成认知负担 | 采用 Bento Grid 2.0：有机非对称但保持视觉节奏 |
| 纯黑深色背景不够高级 | 使用深灰蓝（非纯黑）作为底色，参考 Linear/Vercel 风格 |

### 2026 设计趋势融合
1. **Bento Grid 2.0** — 有机非对称网格，squircle 圆角卡片
2. **Glassmorphism 2.0** — 分层级模糊，色彩吸收效果
3. **Sentient UI** — 自适应布局，上下文感知
4. **Variable Fonts** — 可变字体，动态字重过渡
5. **Micro-interactions** — 精细微动画（150-300ms）
6. **Haptic Light** — 视觉反馈模拟触觉

---

## 二、Design Tokens

### 2.1 色彩系统

```css
/* === 主色板 === */
--color-primary-50:  #EEF6FF;
--color-primary-100: #D9EAFF;
--color-primary-200: #BCD8FF;
--color-primary-300: #8EBFFF;
--color-primary-400: #599AFF;
--color-primary-500: #3371FF;   /* 主品牌色 */
--color-primary-600: #1B4FF5;
--color-primary-700: #143AE1;
--color-primary-800: #1730B6;
--color-primary-900: #192D8F;

/* === 霓虹青（强调色） === */
--color-accent-50:  #ECFFFE;
--color-accent-100: #C6FFFE;
--color-accent-200: #8EFFFD;
--color-accent-300: #4DFFF9;
--color-accent-400: #14F0E8;    /* 主强调色 */
--color-accent-500: #00D4CE;
--color-accent-600: #00A8AA;
--color-accent-700: #008589;
--color-accent-800: #06696E;
--color-accent-900: #0A575C;

/* === 深色模式中性色 === */
--color-dark-bg:       #0A0E1A;   /* 最深底色（非纯黑） */
--color-dark-surface:  #111827;   /* 卡片/面板底色 */
--color-dark-elevated: #1A2235;   /* 悬浮/弹出层 */
--color-dark-border:   #1E293B;   /* 边框 */
--color-dark-border-light: #334155; /* 高亮边框 */

/* === 文字层级 === */
--text-primary:   #F1F5F9;   /* 主文字 - 不用纯白 */
--text-secondary: #94A3B8;   /* 辅助文字 */
--text-tertiary:  #64748B;   /* 次要信息 */
--text-disabled:  #475569;   /* 禁用态 */

/* === 语义色 === */
--color-success: #34D399;     /* 成功/优势 */
--color-warning: #FBBF24;     /* 警告/中等 */
--color-error:   #F87171;     /* 错误/劣势 */
--color-info:    #60A5FA;     /* 信息 */

/* === 渐变 === */
--gradient-brand:   linear-gradient(135deg, #3371FF 0%, #14F0E8 100%);
--gradient-surface: linear-gradient(180deg, #111827 0%, #0A0E1A 100%);
--gradient-glow:    radial-gradient(ellipse at 50% 0%, rgba(20,240,232,0.15) 0%, transparent 60%);
--gradient-hero:    linear-gradient(160deg, #0A0E1A 0%, #0F172A 30%, #111827 60%, #0A0E1A 100%);
```

### 2.2 字体系统

```css
/* === 字体族 === */
--font-display: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;  /* 标题 */
--font-body:    'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;  /* 正文 */
--font-mono:    'JetBrains Mono', 'Fira Code', 'Consolas', monospace;   /* 代码/数据 */

/* === 字体大小（基于 1.25 比例） === */
--text-xs:   0.75rem;    /* 12px - 标签/辅助 */
--text-sm:   0.875rem;   /* 14px - 小号正文 */
--text-base: 1rem;       /* 16px - 默认正文 */
--text-lg:   1.125rem;   /* 18px - 大号正文 */
--text-xl:   1.25rem;    /* 20px - 小标题 */
--text-2xl:  1.5rem;     /* 24px - 标题 */
--text-3xl:  1.875rem;   /* 30px - 大标题 */
--text-4xl:  2.25rem;    /* 36px - 页面标题 */
--text-5xl:  3rem;       /* 48px - Hero标题 */
--text-6xl:  3.75rem;    /* 60px - 超大标题 */

/* === 字重 === */
--font-light:    300;
--font-normal:   400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;

/* === 行高 === */
--leading-tight:  1.25;
--leading-snug:   1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;

/* === 字间距 === */
--tracking-tight:  -0.025em;
--tracking-normal:  0;
--tracking-wide:    0.025em;
--tracking-wider:   0.05em;
--tracking-widest:  0.1em;
```

### 2.3 间距系统

```css
/* === 基础间距（4px 基准） === */
--space-0:   0;
--space-1:   0.25rem;   /* 4px */
--space-2:   0.5rem;    /* 8px */
--space-3:   0.75rem;   /* 12px */
--space-4:   1rem;      /* 16px */
--space-5:   1.25rem;   /* 20px */
--space-6:   1.5rem;    /* 24px */
--space-8:   2rem;      /* 32px */
--space-10:  2.5rem;    /* 40px */
--space-12:  3rem;      /* 48px */
--space-16:  4rem;      /* 64px */
--space-20:  5rem;      /* 80px */
--space-24:  6rem;      /* 96px */

/* === 布局间距 === */
--gap-xs:   8px;
--gap-sm:   12px;
--gap-md:   16px;
--gap-lg:   24px;
--gap-xl:   32px;
--gap-2xl:  48px;
```

### 2.4 圆角系统

```css
--radius-sm:   6px;     /* 小元素：标签、小按钮 */
--radius-md:   10px;    /* 中元素：输入框、卡片 */
--radius-lg:   16px;    /* 大元素：面板、对话框 */
--radius-xl:   24px;    /* 特大：Hero卡片 */
--radius-full: 9999px;  /* 胶囊/圆形 */
```

### 2.5 阴影系统

```css
/* === 深色模式阴影（用发光替代） === */
--shadow-sm:     0 1px 2px rgba(0,0,0,0.3);
--shadow-md:     0 4px 12px rgba(0,0,0,0.4);
--shadow-lg:     0 8px 24px rgba(0,0,0,0.5);
--shadow-xl:     0 16px 48px rgba(0,0,0,0.6);

/* === 发光效果 === */
--glow-sm:       0 0 10px rgba(20,240,232,0.1);
--glow-md:       0 0 20px rgba(20,240,232,0.15);
--glow-lg:       0 0 40px rgba(20,240,232,0.2);
--glow-primary:  0 0 20px rgba(51,113,255,0.3);
```

### 2.6 玻璃态系统

```css
/* === 玻璃态层级 === */
--glass-light: {
  background: rgba(17,24,39,0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.06);
}

--glass-medium: {
  background: rgba(17,24,39,0.75);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08);
}

--glass-heavy: {
  background: rgba(17,24,39,0.9);
  backdrop-filter: blur(32px);
  border: 1px solid rgba(255,255,255,0.1);
}
```

### 2.7 动画系统

```css
/* === 缓动函数 === */
--ease-out:      cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out:   cubic-bezier(0.65, 0, 0.35, 1);
--ease-spring:   cubic-bezier(0.34, 1.56, 0.64, 1);

/* === 持续时间 === */
--duration-fast:    150ms;
--duration-normal:  200ms;
--duration-slow:    300ms;
--duration-slower:  500ms;

/* === 预设动画 === */
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(20,240,232,0.2); }
  50% { box-shadow: 0 0 40px rgba(20,240,232,0.4); }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### 2.8 响应式断点

```css
--breakpoint-sm:  640px;
--breakpoint-md:  768px;
--breakpoint-lg:  1024px;
--breakpoint-xl:  1280px;
--breakpoint-2xl: 1536px;
```

---

## 三、组件规范

### 3.1 按钮

| 类型 | 样式 | 用途 |
|------|------|------|
| Primary | 渐变填充 + 脉冲发光 | 主操作 |
| Secondary | 玻璃态 + 边框 | 次要操作 |
| Ghost | 透明 + 文字色 | 低强调 |
| Danger | 红色变体 | 危险操作 |

### 3.2 卡片

| 类型 | 玻璃层级 | 用途 |
|------|---------|------|
| Nav Card | glass-medium | 导航功能卡 |
| Content Card | glass-light | 内容展示 |
| Dialog | glass-heavy | 弹窗/对话框 |
| Stat Card | glass-light + 发光边框 | 数据统计 |

### 3.3 输入框

- 底部微光下划线（非全边框）
- Focus 状态：下划线变为霓虹青色 + 微弱 glow
- 等宽字体用于数据/代码输入

### 3.4 表格

- 玻璃态表头
- 悬停行：左侧青色指示条 + 背景提亮
- 得分列：语义色渐变（绿→橙→红）
