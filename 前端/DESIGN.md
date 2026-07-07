---
name: 智面幻境 (OfferPilot)
colors:
  primary: "#2563eb"
  primary-dark: "#1d4ed8"
  primary-light: "#60a5fa"
  accent: "#12b8a6"
  warning: "#f59e0b"
  danger: "#ef4444"
  success: "#16a76a"
  text: "#172033"
  text-muted: "#667085"
  border: "#dce6f2"
  surface: "#ffffff"
  surface-soft: "#f8fbff"
  page-bg: "#f4f8fc"

gradients:
  nav-active: "linear-gradient(135deg, #347bff 0%, #1264ff 100%)"
  submit-btn: "linear-gradient(180deg, #2d80ff 0%, #0666f8 100%)"
  generate-btn: "linear-gradient(135deg, #7a38ff, #367fff)"
  score-card: "linear-gradient(135deg, #2563eb, #6d4aff)"
  action-purple: "linear-gradient(135deg, #8c57ff, #5a34ec)"
  action-blue: "linear-gradient(135deg, #4a93ff, #196eff)"
  action-green: "linear-gradient(135deg, #46dc95, #09bd76)"

status-colors:
  finished:
    text: "#09a878"
    background: "#dbfbef"
  ongoing:
    text: "#2874ef"
    background: "#e7f1ff"
  aborted:
    text: "#e8743b"
    background: "#fdeee4"

job-theme-colors:
  java: "#ed4d42"
  web: "#16a76a"
  ai: "#3477c8"
  product: "#11b981"

typography:
  fontFamily:
    ui: "PingFang SC, Microsoft YaHei, Helvetica Neue, Arial, sans-serif"
  page-title:
    fontSize: 28px
    fontWeight: 950
    lineHeight: 1.25
  section-heading:
    fontSize: 18px
    fontWeight: 900
  body:
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.8
  body-lg:
    fontSize: 15px
    fontWeight: 500
  label:
    fontSize: 12px
    fontWeight: 700
  nav-item:
    fontSize: 16px
    fontWeight: 700

spacing:
  page-gutter: 24px
  panel-padding: 24px
  card-gap: 16px
  section-gap: 20px
  element-gap: 12px
  inline-gap: 8px
  tight-gap: 6px

rounded:
  pill: 999px
  full: 50%
  lg: 22px
  md-lg: 18px
  md: 16px
  input: 14px
  sm-lg: 12px
  sm: 10px
  default: 8px
  xs: 6px

shadows:
  sm: "0 8px 24px rgba(37, 99, 235, 0.08)"
  md: "0 16px 40px rgba(37, 99, 235, 0.13)"
  panel: "0 14px 34px rgba(34, 74, 137, 0.06)"
  nav-active: "0 14px 28px rgba(37, 99, 235, 0.24)"
  sidebar: "12px 0 34px rgba(35, 83, 149, 0.04)"
  action-bar: "0 -12px 28px rgba(37, 99, 235, 0.08)"

layout:
  page-max-width: 1180px
  page-min-width: 320px
  sidebar-width: 248px
  sidebar-collapsed: 76px
  topbar-height: 72px
---

# Design System — 智面幻境 (OfferPilot)

## Overview

智面幻境 is an AI-powered mock interview training platform. The interface should feel **professional, trustworthy, and approachable** — like a clean SaaS dashboard with a hint of academic warmth. The visual language uses cool blues as the dominant brand color, softened by generous white space, frosted glass panels, and subtle blue-tinted shadows.

**Core aesthetic:** Clean, focused, modern Chinese SaaS. Low visual noise, high information clarity. Rounded corners on everything. Glass-morphism panels on key surfaces. Blue gradients for emphasis and CTAs.

**Tech stack:** Vue 3 + Element Plus 2.7 + Vite 5. Styling is a mix of CSS custom properties in `main.css` and scoped `<style>` blocks per `.vue` component.

---

## Colors

### Brand Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#2563eb` | CTAs, active states, key interactive elements, Element Plus primary buttons |
| `primary-dark` | `#1d4ed8` | Hover/active states for primary elements |
| `primary-light` | `#60a5fa` | Subtle highlights, focus rings |
| `accent` | `#12b8a6` | Sparing accent for variety; rarely used |
| `warning` | `#f59e0b` | Warning states, medium scores (60–70) |
| `danger` | `#ef4444` | Destructive actions, low scores (< 60) |
| `success` | `#16a76a` | Positive states, high scores (≥ 85) |

### Surface & Background

| Token | Hex | Usage |
|-------|-----|-------|
| `page-bg` | `#f4f8fc` | Full-page background |
| `surface-soft` | `#f8fbff` | Slightly elevated backgrounds, main content area |
| `surface` | `#ffffff` | Cards, panels, modals |
| Glass panel | `rgba(255,255,255,0.88)` | Frosted glass panels with `backdrop-filter: blur(16px)` |

### Text

| Token | Hex | Usage |
|-------|-----|-------|
| `text` | `#172033` | Primary body text, headings |
| `text-muted` | `#667085` | Secondary text, placeholders, descriptions |

### Semantic Gradients

Used for icon backgrounds, action buttons, and decorative elements — never applied to text or body copy.

- **Nav active / Primary emphasis:** `linear-gradient(135deg, #347bff, #1264ff)`
- **Submit button:** `linear-gradient(180deg, #2d80ff, #0666f8)`
- **Generate / AI actions:** `linear-gradient(135deg, #7a38ff, #367fff)`
- **Score cards:** `linear-gradient(135deg, #2563eb, #6d4aff)`
- **Dashboard stat icons (purple):** `linear-gradient(135deg, #8c57ff, #5a34ec)`
- **Dashboard stat icons (blue):** `linear-gradient(135deg, #4a93ff, #196eff)`
- **Dashboard stat icons (green):** `linear-gradient(135deg, #46dc95, #09bd76)`

### Status Colors

| Status | Text | Background | Meaning |
|--------|------|-----------|---------|
| Finished | `#09a878` | `#dbfbef` | Interview completed successfully |
| Ongoing | `#2874ef` | `#e7f1ff` | Interview in progress |
| Aborted | `#e8743b` | `#fdeee4` | Interview terminated early |

### Job Theme Colors

Each job category has a distinct accent color used for icons and category badges:

| Job | Color |
|-----|-------|
| Java / Backend | `#ed4d42` |
| Web / Frontend | `#16a76a` |
| AI / Algorithm | `#3477c8` |
| Product Manager | `#11b981` |

### Score Color Coding

Scores displayed in capability reports and dashboards use these thresholds:

| Range | Color | Token |
|-------|-------|-------|
| ≥ 85 | Green | `success` |
| 70–84 | Blue | `primary` |
| 60–69 | Amber | `warning` |
| < 60 | Red | `danger` |

---

## Typography

### Font Stack

```
PingFang SC, Microsoft YaHei, Helvetica Neue, Arial, sans-serif
```

Always use this stack — never fall back to system serif or monospace for UI text. Applied globally via `body { font-family: var(--font-ui) }`.

### Type Scale

| Role | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| Hero heading | 68px (clamped) | 950 | 0.98 | Login page brand title only |
| Page heading | 28–32px | 950 | 1.25 | Top-level page titles (`h1`, `h2` in `.page-title`) |
| Dashboard title | 30px | 900 | — | Dashboard `h1` |
| Section heading | 18–20px | 900 | — | Card headers, panel titles (`h2`, `h3`) |
| Card title | 18px | 900 | — | Job cards, action cards, form panels |
| Nav items | 16px | 700 | — | Sidebar navigation links |
| Body | 14px | 400 | 1.8 | Main body copy, descriptions |
| Body large | 15px | 500 | 1.8 | Record rows, form hints, context strips |
| Button text | 17–20px | 800–950 | — | Primary action buttons |
| Caption / Label | 12px | 700 | — | Eyebrow badges, tag text, form labels, filter labels |
| Small tag | 13px | — | — | Skill tags, role tags, score labels |

### Weight Conventions

- **Extra bold (900–950):** Brand headings, page titles, card titles, primary buttons
- **Bold (700–800):** Nav items, form labels, section headers, emphasized values
- **Medium (500–600):** Body copy, record rows, supporting text
- **Regular (400):** Descriptions, muted text, secondary content

### Font Smoothing

Always rendered with `-webkit-font-smoothing: antialiased` and `text-rendering: optimizeLegibility` on the body.

---

## Spacing & Layout

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| Tight | 4–6px | Icon-label gaps, eyebrow padding, section-title margin-top |
| Inline | 8px | Tag rows, description margin-top |
| Element | 12px | Flex/grid gaps, sidebar brand gap, search shell padding |
| Stack | 14–16px | Sidebar nav gap, panel gaps, card grids, sidebar padding |
| Block | 18–20px | Nav item padding, panel padding, form panel padding, dashboard grid gap |
| Section | 24px | Page title margin-bottom, main content padding, dialog body padding, answer area padding |
| Page | 28–34px | Main content padding (top), topbar padding |
| Shell | 48px | Page shell horizontal gutter (`calc(100vw - 48px)`) |

### Layout Widths

| Container | Width |
|-----------|-------|
| Page shell | `min(1180px, calc(100vw - 48px))` |
| Dashboard / Prep page | `min(1280px, 100%)` |
| Sidebar (default) | `248px` |
| Sidebar (collapsed) | `76px` |
| Auth card | `min(100%, 560px)` |
| Search shell | `min(420px, 43vw)` |

### Common Grids

- **Dashboard:** 3-column quick actions → 2-column (`1fr 420px`)
- **Login:** 2-column (`1fr minmax(440px, 0.72fr)`)
- **Job preparation:** content `1fr` / sidebar `360px`
- **Interview:** sidebar `280px` / dialog `1fr`
- **Report overview:** score card `280px` / summary `1fr`
- **Profile:** left `300px` / right `1fr`
- **Teacher stats:** 6 columns → collapses 3 → 2 → 1 on smaller screens
- **Status strips:** `repeat(4, 1fr)` with `14px` gap

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| Pill | `999px` | Eyebrow badges, Element Plus tags, step indicators |
| Full circle | `50%` | Avatars, circular icons |
| Large | `22px` | Portal cards (login) |
| Medium-large | `18px` | Auth cards, brand mark, action icons |
| Medium | `16px` | Chart panels, stat cards, content panels |
| Input | `14px` | Auth inputs, submit buttons, score cards, summary cards, interview cards |
| Small-large | `12px` | Nav items, stat icons, profile cards, settings cards, chat bubbles |
| Small | `10px` | Collapse buttons, focus item icons, problem icons |
| Default | `8px` | **Global default** (`--radius`): cards, panels, inputs, buttons, Element Plus components |
| Extra small | `6px` | Action card buttons, tag row spans, skill tags |

**Rule:** Always use `8px` as the baseline. Go larger for cards and panels, smaller only for nested elements inside cards. Use `999px` for anything pill-shaped (tags, badges, eyebrows).

---

## Components

### Page Shell & Title

Every content page uses this structure:

```html
<div class="page-shell">
  <div class="page-title">
    <span class="eyebrow"><el-icon /> 分类标签</span>
    <h2>页面标题</h2>
    <p>页面描述文字，最多一两行</p>
  </div>
  <!-- page content -->
</div>
```

- **Eyebrow:** `12px`, weight 700, pill-shaped, primary-tinted background with primary-dark text
- **Title:** `28px`, weight 950, line-height 1.25
- **Description:** `14px`, color `text-muted`, line-height 1.8, max-width 720px

### Buttons

Four distinct button styles:

| Type | Style | Usage |
|------|-------|-------|
| **Primary submit** | Full width, gradient `#2d80ff → #0666f8`, 14px radius, 64px height, 900 weight, white text | Main form submission |
| **Nav item** | 50px min-height, 12px radius, 16px/700 text. Active: blue gradient + nav-active shadow | Sidebar navigation |
| **Generate** | Full width, purple-to-blue gradient, 56px height, 950 weight | AI generation triggers |
| **Member / Outline** | White bg, blue text, `#cbd7f5` border, full width | Secondary actions on cards |
| **Action card** | Inline, 6px radius, gradient background per theme | Dashboard quick-action cards |

### Inputs

All inputs (text, textarea) share these rules via Element Plus overrides:

- **Border:** No visible border; uses `box-shadow: 0 0 0 1px rgba(220,230,242,0.95) inset` as the border
- **Height:** Minimum 44px (standard), 58px (auth page)
- **Radius:** 8px (default), 14px (auth page)
- **Hover:** Inset shadow shifts to `rgba(96,165,250,0.8)` (primary-light at 80% opacity)
- **Focus:** Inset shadow shifts to `var(--primary)` + outer glow `0 0 0 4px rgba(37,99,235,0.1)`
- **Placeholder:** Use `text-muted` color

### Cards & Panels

Three standard card variants, all using white or near-white backgrounds with subtle blue-tinted borders and shadows:

| Variant | Background | Border | Radius | Shadow | Usage |
|---------|------------|--------|--------|--------|-------|
| **Glass panel** | `rgba(255,255,255,0.88)` + blur 16px | `rgba(220,230,242,0.82)` | 8px | `shadow-md` | Report cards, insight cards, profile cards |
| **Panel** | `rgba(255,255,255,0.94)` | `#dbe4f2` | 8px | Panel shadow | Dashboard panels |
| **Content panel** | `#fff` | `rgba(215,225,241,0.92)` | 16px | Lighter shadow | Teacher dashboard, chart panels |

### Status Tags

Pill-shaped tags (via Element Plus `<el-tag>`) with `border-radius: 999px`:

- **Finished:** `#09a878` text on `#dbfbef` background
- **Ongoing:** `#2874ef` text on `#e7f1ff` background
- **Aborted:** `#e8743b` text on `#fdeee4` background

### Status Strip

A 4-column grid (`repeat(4, 1fr)`) with 14px gap, used to display key metrics in interview and resume views. Each cell contains a label/value pair.

### Action Bar

Fixed-bottom bar for persistent actions (submit, cancel, next step):

```css
position: fixed; right: 0; bottom: 0; left: 0; z-index: 15;
padding: 14px 24px;
background: rgba(255, 255, 255, 0.9);
border-top: 1px solid rgba(220, 230, 242, 0.95);
backdrop-filter: blur(14px);
```

### Avatars & Icons

- **Avatars:** 50% border radius, 42–76px depending on context
- **Stat icons:** 48–50px, 12–16px radius, gradient backgrounds
- **Action icons:** 64px, 18px radius, gradient backgrounds
- **Brand mark:** 52px, 18px radius
- **Small icons:** 30–38px, used for step indicators, targets, weaknesses

---

## Patterns

### Frosted Glass

The glass-morphism pattern is applied to key surfaces (report cards, profile panels, insight cards) to create depth without heavy shadows:

```css
.glass-panel {
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(220, 230, 242, 0.82);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(16px);
  border-radius: 8px;
}
```

Use glass panels sparingly — only on summary/insight cards where the blurred background adds meaningful depth. Do not use for forms or data tables.

### Gradients as Emphasis

Gradients are used for:
- **Active/highlighted states** (nav items)
- **Primary CTAs** (submit, generate buttons)
- **Decorative icon backgrounds** (stat cards, action cards)

Never apply gradients to body text, form labels, or data tables. Gradients should guide attention, not compete with content.

### Score Visualization

Scores follow a four-color semantic scale (green → blue → amber → red). When displaying scores on progress bars or charts:
- Use solid colors (not gradients) for score bars
- Label the score value prominently (56px, weight 950) inside score cards
- Supplement raw scores with a color indicator

### Empty States

Use a centered placeholder card with a large icon (72px), a title, and a muted description. Standard pattern from Element Plus empty state but with project-specific styling (glass panel, rounded corners).

### Responsive Breakpoints

- **768px:** Sidebar collapses, page shell gutter shrinks to 28px, bottom padding increases to 132px
- **Below 768px:** Single-column layouts, inputs go full-width, auth card gets 12px radius

---

## Do's and Don'ts

### Do

- ✅ Use `--primary: #2563eb` sparingly — it's for the single most important action on each screen
- ✅ Maintain the glass-panel pattern on summary and insight cards
- ✅ Use 8px as the default border radius; only deviate for specific component needs
- ✅ Keep headings bold (900+) and body text medium (500)
- ✅ Use the page-shell + page-title pattern on every content page for consistency
- ✅ Use pill-shaped tags (999px) for all status indicators and badges
- ✅ Apply blue-tinted shadows (using `rgba(37,99,235,…)`) — never pure black/gray shadows
- ✅ Use the font stack `PingFang SC, Microsoft YaHei, Helvetica Neue, Arial, sans-serif` everywhere
- ✅ Color-code scores using the defined thresholds (green ≥ 85, blue ≥ 70, amber ≥ 60, red < 60)

### Don't

- ❌ Don't introduce new colors without adding them to the CSS custom properties in `main.css`
- ❌ Don't mix sharp corners with rounded corners in the same view — everything is rounded
- ❌ Don't use pure black (`#000`) or pure gray shadows — always blue-tinted
- ❌ Don't use gradients on body text, labels, or data tables
- ❌ Don't add heavy box-shadows — use `backdrop-filter: blur()` with semi-transparent backgrounds instead
- ❌ Don't use border directly on inputs — use the inset box-shadow pattern
- ❌ Don't use system fonts — always use the project font stack via `var(--font-ui)`
- ❌ Don't create new page layout patterns — use the established page-shell/page-title convention
