<template>
  <div class="logo-animated" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Glow background -->
      <circle cx="60" cy="60" r="50" fill="url(#anim-glow)" opacity="0" class="glow-circle" />

      <!-- Outer ring -->
      <circle cx="60" cy="60" r="54" stroke="url(#anim-grad)" stroke-width="0.5" opacity="0.2" class="ring ring-outer" />

      <!-- "m" letterform - animated stroke drawing -->
      <!-- Left vertical -->
      <path
        class="stroke-draw stroke-1"
        d="M30 85 L30 42 Q30 32 40 32 L44 32 Q54 32 54 42 L54 68"
        stroke="url(#anim-grad)"
        stroke-width="3.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        fill="none"
      />
      <!-- Middle arc -->
      <path
        class="stroke-draw stroke-2"
        d="M54 68 L54 42 Q54 32 64 32 L64 32 Q74 32 74 42 L74 68"
        stroke="url(#anim-grad)"
        stroke-width="3.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        fill="none"
      />
      <!-- Right ascending -->
      <path
        class="stroke-draw stroke-3"
        d="M74 68 L74 48 Q74 32 84 32 L90 32"
        stroke="url(#anim-grad)"
        stroke-width="3.5"
        stroke-linecap="round"
        fill="none"
      />

      <!-- Arrow tip -->
      <path
        class="stroke-draw stroke-4"
        d="M82 24 L92 32 L82 40"
        stroke="url(#anim-grad)"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        fill="none"
        opacity="0.8"
      />

      <!-- Base line -->
      <path
        class="stroke-draw stroke-5"
        d="M24 85 L96 85"
        stroke="url(#anim-grad)"
        stroke-width="2"
        stroke-linecap="round"
        opacity="0.3"
      />

      <!-- Center dot pulse -->
      <circle cx="60" cy="50" r="4" fill="url(#anim-grad)" class="center-dot" />

      <!-- Particle dots -->
      <circle class="particle p1" cx="20" cy="40" r="1.5" fill="#059669" opacity="0" />
      <circle class="particle p2" cx="100" cy="50" r="1.5" fill="#34d399" opacity="0" />
      <circle class="particle p3" cx="40" cy="100" r="1" fill="#10b981" opacity="0" />
      <circle class="particle p4" cx="85" cy="95" r="1" fill="#6ee7b7" opacity="0" />

      <defs>
        <linearGradient id="anim-grad" x1="20" y1="20" x2="100" y2="100" gradientUnits="userSpaceOnUse">
          <stop stop-color="#059669" />
          <stop offset="1" stop-color="#34d399" />
        </linearGradient>
        <radialGradient id="anim-glow" cx="60" cy="60" r="50" gradientUnits="userSpaceOnUse">
          <stop stop-color="rgba(16,185,129,0.15)" />
          <stop offset="1" stop-color="transparent" />
        </radialGradient>
      </defs>
    </svg>
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: Number,
    default: 120,
  },
})
</script>

<style scoped>
.logo-animated {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Stroke drawing animation */
.stroke-draw {
  stroke-dasharray: 300;
  stroke-dashoffset: 300;
}

.stroke-1 {
  animation: draw-stroke 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.2s forwards;
}

.stroke-2 {
  animation: draw-stroke 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.5s forwards;
}

.stroke-3 {
  animation: draw-stroke 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.8s forwards;
}

.stroke-4 {
  animation: draw-stroke 0.4s cubic-bezier(0.4, 0, 0.2, 1) 1.1s forwards;
}

.stroke-5 {
  animation: draw-stroke 0.5s cubic-bezier(0.4, 0, 0.2, 1) 1.3s forwards;
}

@keyframes draw-stroke {
  to {
    stroke-dashoffset: 0;
  }
}

/* Glow circle */
.glow-circle {
  animation: glow-in 1.5s cubic-bezier(0.4, 0, 0.2, 1) 1.5s forwards;
}

@keyframes glow-in {
  to {
    opacity: 1;
  }
}

/* Ring rotation */
.ring-outer {
  transform-origin: 60px 60px;
  animation: ring-spin 20s linear infinite;
}

@keyframes ring-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Center dot */
.center-dot {
  opacity: 0;
  transform-origin: 60px 50px;
  animation: dot-appear 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 1.6s forwards;
}

@keyframes dot-appear {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Breathing animation after initial load */
.center-dot {
  animation: dot-appear 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 1.6s forwards,
             dot-breathe 3s ease-in-out 2.5s infinite;
}

@keyframes dot-breathe {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

/* Particles */
.particle {
  animation: particle-drift 4s ease-in-out infinite;
}

.p1 {
  animation-delay: 1.8s;
  animation-name: particle-drift-1;
}

.p2 {
  animation-delay: 2.2s;
  animation-name: particle-drift-2;
}

.p3 {
  animation-delay: 2.5s;
  animation-name: particle-drift-3;
}

.p4 {
  animation-delay: 2.8s;
  animation-name: particle-drift-4;
}

@keyframes particle-drift-1 {
  0%, 100% { opacity: 0; transform: translate(0, 0); }
  20% { opacity: 0.6; }
  80% { opacity: 0.4; }
  50% { transform: translate(8px, -12px); }
}

@keyframes particle-drift-2 {
  0%, 100% { opacity: 0; transform: translate(0, 0); }
  20% { opacity: 0.5; }
  80% { opacity: 0.3; }
  50% { transform: translate(-10px, -8px); }
}

@keyframes particle-drift-3 {
  0%, 100% { opacity: 0; transform: translate(0, 0); }
  20% { opacity: 0.4; }
  80% { opacity: 0.2; }
  50% { transform: translate(6px, -15px); }
}

@keyframes particle-drift-4 {
  0%, 100% { opacity: 0; transform: translate(0, 0); }
  20% { opacity: 0.5; }
  80% { opacity: 0.3; }
  50% { transform: translate(-8px, -10px); }
}
</style>
