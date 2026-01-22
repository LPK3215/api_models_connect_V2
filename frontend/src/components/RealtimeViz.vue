<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type Point = { x: number; y: number }

const w = 560
const h = 300
const pad = 28

const points = ref<Point[]>([])
const lastValue = ref(0)
const rpm = ref(1280)
const p95 = ref(420)
const err = ref(0.18)

function seed() {
  const arr: Point[] = []
  let v = 52
  for (let i = 0; i < 24; i++) {
    v += (Math.random() - 0.5) * 14
    v = Math.max(10, Math.min(90, v))
    arr.push({ x: i, y: v })
  }
  points.value = arr
  lastValue.value = arr[arr.length - 1]?.y ?? 50
}

function step() {
  const arr = points.value.slice(1)
  const prev = lastValue.value
  let v = prev + (Math.random() - 0.5) * 12
  v = Math.max(8, Math.min(92, v))
  arr.push({ x: (arr[arr.length - 1]?.x ?? 0) + 1, y: v })
  points.value = arr.map((p, i) => ({ x: i, y: p.y }))
  lastValue.value = v

  rpm.value = Math.max(120, Math.round(rpm.value + (Math.random() - 0.5) * 120))
  p95.value = Math.max(90, Math.round(p95.value + (Math.random() - 0.5) * 40))
  err.value = Math.max(0.01, Math.min(1.2, +(err.value + (Math.random() - 0.5) * 0.08).toFixed(2)))
}

let t: number | null = null
onMounted(() => {
  seed()
  t = window.setInterval(step, 1100)
})
onBeforeUnmount(() => {
  if (t) window.clearInterval(t)
})

const yMin = computed(() => 0)
const yMax = computed(() => 100)

function sx(i: number) {
  const n = Math.max(1, points.value.length - 1)
  return pad + (i / n) * (w - pad * 2)
}
function sy(v: number) {
  const t = (v - yMin.value) / (yMax.value - yMin.value)
  return h - pad - t * (h - pad * 2)
}

const d = computed(() => {
  if (!points.value.length) return ''
  return points.value
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${sx(i).toFixed(2)} ${sy(p.y).toFixed(2)}`)
    .join(' ')
})

const last = computed(() => {
  const p = points.value[points.value.length - 1]
  if (!p) return null
  return { cx: sx(points.value.length - 1), cy: sy(p.y), v: p.y }
})
</script>

<template>
  <div class="glass p-5">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <div class="text-xs font-semibold text-muted">Real-time Signal</div>
        <div class="mt-1 truncate text-sm font-semibold">Pipeline Throughput</div>
      </div>
      <span class="pill border-primary/25 bg-white/40 text-primary">live</span>
    </div>

    <div class="mt-4 overflow-hidden rounded-2xl border border-border/70 bg-white/40 backdrop-blur-xl">
      <svg :viewBox="`0 0 ${w} ${h}`" class="h-[220px] w-full">
        <defs>
          <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="rgb(var(--c-primary2))" stop-opacity="0.85" />
            <stop offset="70%" stop-color="rgb(var(--c-primary))" stop-opacity="0.95" />
            <stop offset="100%" stop-color="rgb(var(--c-cta))" stop-opacity="0.85" />
          </linearGradient>
          <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="rgb(var(--c-primary))" stop-opacity="0.20" />
            <stop offset="100%" stop-color="rgb(var(--c-primary))" stop-opacity="0.02" />
          </linearGradient>
        </defs>

        <g opacity="0.55">
          <path
            v-for="i in 6"
            :key="i"
            :d="`M ${pad} ${pad + (i - 1) * ((h - pad * 2) / 5)} H ${w - pad}`"
            stroke="rgb(var(--c-border) / 0.25)"
            stroke-width="1"
          />
        </g>

        <path :d="`${d} L ${w - pad} ${h - pad} L ${pad} ${h - pad} Z`" fill="url(#fill)" opacity="0.9" />
        <path :d="d" fill="none" stroke="url(#line)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />

        <circle v-if="last" :cx="last.cx" :cy="last.cy" r="7" fill="rgb(var(--c-panel))" stroke="rgb(var(--c-primary))" stroke-width="3" />
      </svg>
    </div>

    <div class="mt-4 grid grid-cols-3 gap-3">
      <div class="rounded-2xl border border-border/70 bg-white/40 px-3 py-2 backdrop-blur">
        <div class="text-[11px] font-semibold text-muted">Requests / min</div>
        <div class="mt-1 font-mono text-base font-semibold">{{ rpm.toLocaleString() }}</div>
      </div>
      <div class="rounded-2xl border border-border/70 bg-white/40 px-3 py-2 backdrop-blur">
        <div class="text-[11px] font-semibold text-muted">P95 latency</div>
        <div class="mt-1 font-mono text-base font-semibold">{{ p95 }} ms</div>
      </div>
      <div class="rounded-2xl border border-border/70 bg-white/40 px-3 py-2 backdrop-blur">
        <div class="text-[11px] font-semibold text-muted">Error rate</div>
        <div class="mt-1 font-mono text-base font-semibold">{{ err.toFixed(2) }}%</div>
      </div>
    </div>
  </div>
</template>

