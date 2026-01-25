<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { AlertTriangle, ArrowRight, Copy, Download, FileJson, Image, Loader2, PlayCircle, X } from 'lucide-vue-next'

import { api, apiOrigin, API_PATHS } from '../lib/api'
import type { ModelItem, PromptListItem, ProviderItem, TaskResult, TaskStreamEvent } from '../lib/types'

type Props = {
  active?: boolean
  showClose?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  active: true,
  showClose: false,
})

const emit = defineEmits<{ close: [] }>()

const providers = ref<ProviderItem[]>([])
const models = ref<ModelItem[]>([])
const prompts = ref<PromptListItem[]>([])

const providerKey = ref('')
const modelKey = ref('')
const promptId = ref('')

const files = ref<File[]>([])
const dragging = ref(false)

const running = ref(false)
const error = ref<string | null>(null)
const result = ref<TaskResult | null>(null)
const copyOk = ref(false)
const streamEvents = ref<TaskStreamEvent[]>([])
const aborter = ref<AbortController | null>(null)

const loaded = ref(false)
const loading = ref(false)

const storageKey = 'api-models-connect.quick-runner.v1'
type RunnerPrefs = { providerKey: string; modelKey: string; promptId: string }
const pendingModelKey = ref<string | null>(null)

function readPrefs(): RunnerPrefs | null {
  try {
    const raw = window.localStorage.getItem(storageKey)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return null
    const provider = typeof parsed.providerKey === 'string' ? parsed.providerKey : ''
    const model = typeof parsed.modelKey === 'string' ? parsed.modelKey : ''
    const prompt = typeof parsed.promptId === 'string' ? parsed.promptId : ''
    return { providerKey: provider, modelKey: model, promptId: prompt }
  } catch {
    return null
  }
}

function writePrefs(prefs: RunnerPrefs) {
  try {
    window.localStorage.setItem(storageKey, JSON.stringify(prefs))
  } catch {
    // ignore
  }
}

const canRun = computed(
  () =>
    !!providerKey.value &&
    !!modelKey.value &&
    !!promptId.value &&
    files.value.length > 0 &&
    !running.value,
)

async function loadInitial() {
  if (loaded.value || loading.value) return
  loading.value = true
  error.value = null
  try {
    const [p, pr] = await Promise.all([
      api.get<{ items: ProviderItem[] }>(API_PATHS.providers),
      api.get<{ items: PromptListItem[] }>(API_PATHS.prompts),
    ])
    providers.value = p.data.items
    prompts.value = pr.data.items

    const prefs = readPrefs()
    if (prefs) {
      if (prefs.providerKey && providers.value.some((x) => x.key === prefs.providerKey)) providerKey.value = prefs.providerKey
      if (prefs.promptId && prompts.value.some((x) => x.id === prefs.promptId)) promptId.value = prefs.promptId
      if (prefs.modelKey) pendingModelKey.value = prefs.modelKey
    }

    const first = prompts.value[0]
    if (!promptId.value && first) promptId.value = first.id
    loaded.value = true
  } catch (e: any) {
    error.value = e?.message || '加载运行器数据失败'
  } finally {
    loading.value = false
  }
}

async function loadModels() {
  models.value = []
  modelKey.value = ''
  if (!providerKey.value) return
  try {
    const { data } = await api.get<{ items: ModelItem[] }>(`${API_PATHS.providers}/${providerKey.value}/models`)
    models.value = data.items
    const pending = pendingModelKey.value
    if (pending && models.value.some((m) => m.key === pending)) modelKey.value = pending
    pendingModelKey.value = null
  } catch (e: any) {
    error.value = e?.message || '加载模型列表失败'
  }
}

type PreviewItem = { file: File; url: string }

const previews = ref<PreviewItem[]>([])
const selectedPreviewIndex = ref(0)

const viewScale = ref(1)
const viewX = ref(0)
const viewY = ref(0)
const viewDragging = ref(false)
const viewDragStart = ref({ x: 0, y: 0, ox: 0, oy: 0 })

function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n))
}

function resetView() {
  viewScale.value = 1
  viewX.value = 0
  viewY.value = 0
}

function setFiles(list: File[]) {
  for (const p of previews.value) {
    try {
      URL.revokeObjectURL(p.url)
    } catch {
      // ignore
    }
  }
  previews.value = list.map((file) => ({ file, url: URL.createObjectURL(file) }))
  files.value = list
  selectedPreviewIndex.value = 0
  resetView()
}

const activePreviewUrl = computed(() => previews.value[selectedPreviewIndex.value]?.url || '')

function zoom(delta: number) {
  const next = clamp(viewScale.value + delta, 0.2, 6)
  viewScale.value = next
}

function onViewerWheel(ev: WheelEvent) {
  ev.preventDefault()
  const step = ev.deltaY < 0 ? 0.15 : -0.15
  zoom(step)
}

function onViewerPointerDown(ev: PointerEvent) {
  ;(ev.currentTarget as HTMLElement | null)?.setPointerCapture?.(ev.pointerId)
  viewDragging.value = true
  viewDragStart.value = { x: ev.clientX, y: ev.clientY, ox: viewX.value, oy: viewY.value }
}

function onViewerPointerMove(ev: PointerEvent) {
  if (!viewDragging.value) return
  viewX.value = viewDragStart.value.ox + (ev.clientX - viewDragStart.value.x)
  viewY.value = viewDragStart.value.oy + (ev.clientY - viewDragStart.value.y)
}

function onViewerPointerUp(ev: PointerEvent) {
  ;(ev.currentTarget as HTMLElement | null)?.releasePointerCapture?.(ev.pointerId)
  viewDragging.value = false
}

function onFileChange(ev: Event) {
  const input = ev.target as HTMLInputElement
  const list = input.files ? Array.from(input.files) : []
  setFiles(list.filter((f) => f.type.startsWith('image/')))
}

function onDrop(ev: DragEvent) {
  ev.preventDefault()
  dragging.value = false
  const list = ev.dataTransfer?.files ? Array.from(ev.dataTransfer.files) : []
  setFiles(list.filter((f) => f.type.startsWith('image/')))
}

function onDragOver(ev: DragEvent) {
  ev.preventDefault()
  dragging.value = true
}
function onDragLeave() {
  dragging.value = false
}

const runMeta = ref<{ api_key_env?: string; api_base_url?: string; mode?: string } | null>(null)
const stage = ref<'idle' | 'connecting' | 'thinking' | 'streaming' | 'finishing' | 'done'>('idle')
const runStartAt = ref(0)
const stageStartAt = ref(0)
const nowTick = ref(0)
let tickTimer: number | null = null
const streamFinished = ref(false)

const connectSeconds = ref<number | null>(null)
const thinkingSeconds = ref<number | null>(null)
const genSeconds = ref<number | null>(null)
const streamTotalSeconds = ref<number | null>(null)
const parseSeconds = ref<number | null>(null)
const saveSeconds = ref<number | null>(null)
const allSeconds = ref<number | null>(null)

const streamedText = ref('')
const streamLog = ref<string[]>([])

const streamTextEl = ref<HTMLElement | null>(null)
const streamLogEl = ref<HTMLElement | null>(null)

function startTick() {
  stopTick()
  nowTick.value = performance.now()
  tickTimer = window.setInterval(() => (nowTick.value = performance.now()), 100)
}

function stopTick() {
  if (tickTimer) window.clearInterval(tickTimer)
  tickTimer = null
}

function fmt(n: number | null) {
  if (n == null || !Number.isFinite(n)) return '—'
  return `${n.toFixed(3)}s`
}

const totalLiveSeconds = computed(() => {
  if (!runStartAt.value) return null
  const base = stage.value === 'done' ? (allSeconds.value ?? null) : (nowTick.value - runStartAt.value) / 1000
  return typeof base === 'number' ? base : null
})

const connectLiveSeconds = computed(() => {
  if (connectSeconds.value != null) return connectSeconds.value
  if (stage.value !== 'connecting' || !stageStartAt.value) return null
  return (nowTick.value - stageStartAt.value) / 1000
})

const thinkingLiveSeconds = computed(() => {
  if (thinkingSeconds.value != null) return thinkingSeconds.value
  if (stage.value !== 'thinking' || !stageStartAt.value) return null
  return (nowTick.value - stageStartAt.value) / 1000
})

const streamingLiveSeconds = computed(() => {
  if (genSeconds.value != null) return genSeconds.value
  if (stage.value !== 'streaming' || !stageStartAt.value) return null
  return (nowTick.value - stageStartAt.value) / 1000
})

function appendLog(line: string) {
  streamLog.value.push(line)
  requestAnimationFrame(() => {
    if (streamLogEl.value) streamLogEl.value.scrollTop = streamLogEl.value.scrollHeight
  })
}

function appendText(chunk: string) {
  streamedText.value += chunk
  requestAnimationFrame(() => {
    if (streamTextEl.value) streamTextEl.value.scrollTop = streamTextEl.value.scrollHeight
  })
}

function handleStreamEvent(ev: TaskStreamEvent) {
  streamEvents.value.push(ev)
  if (ev.event === 'run_start') {
    runMeta.value = { api_key_env: ev.api_key_env, api_base_url: ev.api_base_url, mode: ev.mode }
    appendLog(`ℹ️ 使用环境变量键: ${ev.api_key_env || '—'}`)
    appendLog(`ℹ️ API Base: ${ev.api_base_url || '—'}`)
    appendLog(`ℹ️ 模式: ${ev.mode || 'streaming'}`)
    return
  }

  if (ev.event === 'fatal') {
    error.value = ev.error
    appendLog(`错误: ${ev.error}`)
    stage.value = 'done'
    streamFinished.value = true
    stopTick()
    return
  }

  if (ev.event === 'done') {
    result.value = ev.result
    stage.value = 'done'
    streamFinished.value = true
    stopTick()
    const totals = ((ev.result as any)?.summary as any)?.totals
    const outDir = ((ev.result as any)?.summary as any)?.output_dir
    if (totals) {
      appendLog('============================================================')
      appendLog(`✅ 处理完成！`)
      appendLog(`✅ 成功: ${totals.success ?? '—'} 张`)
      appendLog(`⚠️ 失败: ${totals.failed ?? '—'} 张`)
      appendLog(`ℹ️ 总数: ${totals.all ?? '—'} 张`)
    }
    if (outDir) appendLog(`📦 结果保存在: ${outDir}`)
    return
  }

  const idx = typeof (ev as any).index === 'number' ? (ev as any).index : null
  const total = typeof (ev as any).total === 'number' ? (ev as any).total : null
  const prefix = idx && total ? `[${idx}/${total}] ` : ''
  const name = typeof (ev as any).image_name === 'string' ? (ev as any).image_name : ''

  if (ev.event === 'image_start') {
    appendLog('')
    appendLog(`📸 ${prefix}${name}`)
    return
  }
  if (ev.event === 'preprocess_done') {
    appendLog(`[TIME] preprocess=${fmt((ev as any).preprocess_seconds as any)}`)
    return
  }
  if (ev.event === 'connect_done') {
    connectSeconds.value = Number((ev as any).connect_seconds) || 0
    stage.value = 'thinking'
    stageStartAt.value = performance.now()
    appendLog(`[TIME] connect=${fmt(connectSeconds.value)}`)
    return
  }
  if (ev.event === 'ttft') {
    thinkingSeconds.value = Number((ev as any).thinking_seconds) || 0
    const ttftSeconds = Number((ev as any).ttft_seconds) || 0
    stage.value = 'streaming'
    stageStartAt.value = performance.now()
    appendLog(`[TIME] TTFT=${fmt(ttftSeconds)} thinking=${fmt(thinkingSeconds.value)}`)
    return
  }
  if (ev.event === 'delta') {
    const c = typeof (ev as any).content === 'string' ? ((ev as any).content as string) : ''
    if (c) appendText(c)
    return
  }
  if (ev.event === 'stream_done') {
    genSeconds.value = Number((ev as any).gen_seconds) || 0
    streamTotalSeconds.value = Number((ev as any).stream_total_seconds) || 0
    appendLog(`[TIME] gen=${fmt(genSeconds.value)} total=${fmt(streamTotalSeconds.value)} chars=${(ev as any).char_count ?? '—'}`)
    stage.value = 'finishing'
    return
  }
  if (ev.event === 'parse_done') {
    parseSeconds.value = Number((ev as any).parse_seconds) || 0
    appendLog(`[JSON] parse=${fmt(parseSeconds.value)} valid=${(ev as any).json_valid ? 'true' : 'false'}`)
    return
  }
  if (ev.event === 'image_done') {
    const timings = (ev as any).timings || {}
    saveSeconds.value = Number(timings.save_seconds) || saveSeconds.value
    allSeconds.value = Number(timings.all_seconds) || allSeconds.value
    const out = typeof (ev as any).output_file === 'string' ? ((ev as any).output_file as string) : ''
    if (out) appendLog(`[SAVE] path=${out}`)
    appendLog(`[TIME] all=${fmt(allSeconds.value)}`)
  }
}

const streamLogText = computed(() => streamLog.value.join('\n'))

async function run() {
  if (!canRun.value) return
  aborter.value?.abort()
  aborter.value = new AbortController()
  running.value = true
  error.value = null
  result.value = null
  copyOk.value = false
  streamEvents.value = []
  streamLog.value = []
  streamedText.value = ''
  runMeta.value = null
  streamFinished.value = false

  connectSeconds.value = null
  thinkingSeconds.value = null
  genSeconds.value = null
  streamTotalSeconds.value = null
  parseSeconds.value = null
  saveSeconds.value = null
  allSeconds.value = null

  stage.value = 'connecting'
  runStartAt.value = performance.now()
  stageStartAt.value = runStartAt.value
  startTick()

  try {
    const form = new FormData()
    form.append('provider', providerKey.value)
    form.append('model', modelKey.value)
    form.append('prompt_id', promptId.value)
    for (const f of files.value) form.append('files', f)

    const res = await fetch(`${apiOrigin}${API_PATHS.tasksProcessStream}`, {
      method: 'POST',
      body: form,
      signal: aborter.value.signal,
    })

    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || `HTTP ${res.status}`)
    }

    const reader = res.body?.getReader()
    if (!reader) throw new Error('浏览器不支持流式响应读取')

    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      while (true) {
        const nl = buffer.indexOf('\n')
        if (nl < 0) break
        const line = buffer.slice(0, nl).trim()
        buffer = buffer.slice(nl + 1)
        if (!line) continue
        try {
          handleStreamEvent(JSON.parse(line) as TaskStreamEvent)
        } catch {
          // ignore malformed line
        }
      }
    }
    const tail = buffer.trim()
    if (tail) {
      try {
        handleStreamEvent(JSON.parse(tail) as TaskStreamEvent)
      } catch {
        // ignore
      }
    }
    if (!streamFinished.value) {
      stage.value = 'done'
      stopTick()
    }
  } catch (e: any) {
    if (e?.name === 'AbortError') {
      error.value = '已取消'
      appendLog('已取消')
    } else {
      error.value = e?.message || '运行失败'
      appendLog(`错误: ${error.value}`)
    }
    stage.value = 'done'
    stopTick()
  } finally {
    running.value = false
    aborter.value = null
  }
}

const resultJson = computed(() => (result.value ? JSON.stringify(result.value, null, 2) : ''))
const outputDir = computed(() => (result.value as any)?.summary?.output_dir as string | undefined)

async function copyResult() {
  if (!resultJson.value) return
  try {
    await navigator.clipboard.writeText(resultJson.value)
    copyOk.value = true
    window.setTimeout(() => (copyOk.value = false), 1100)
  } catch {
    try {
      const ta = document.createElement('textarea')
      ta.value = resultJson.value
      ta.style.position = 'fixed'
      ta.style.left = '-9999px'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
      copyOk.value = true
      window.setTimeout(() => (copyOk.value = false), 1100)
    } catch {
      error.value = '复制失败'
    }
  }
}

function downloadResult() {
  if (!resultJson.value) return
  const stamp = new Date().toISOString().replace(/[:.]/g, '-')
  const safe = (s: string) => s.replace(/[^\w.-]+/g, '_').slice(0, 60)
  const name = `result_${safe(providerKey.value || 'provider')}_${safe(modelKey.value || 'model')}_${stamp}.json`
  const blob = new Blob([resultJson.value], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

watch(
  () => props.active,
  (v) => {
    if (v) loadInitial()
  },
  { immediate: true },
)

watch(
  () => [providerKey.value, modelKey.value, promptId.value] as const,
  ([p, m, pr]) => {
    if (!props.active || !loaded.value) return
    writePrefs({ providerKey: p, modelKey: m, promptId: pr })
  },
)

let t: number | null = null
watch(
  () => providerKey.value,
  async () => {
    if (!props.active) return
    if (t) window.clearTimeout(t)
    t = window.setTimeout(() => void loadModels(), 80)
  },
)
onBeforeUnmount(() => {
  if (t) window.clearTimeout(t)
  aborter.value?.abort()
  stopTick()
  for (const p of previews.value) {
    try {
      URL.revokeObjectURL(p.url)
    } catch {
      // ignore
    }
  }
})
</script>

<template>
  <div class="grid gap-3 lg:grid-cols-[360px_1fr]">
    <div class="glass p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="text-xs font-semibold text-muted">任务运行</div>
          <div class="mt-1 text-base font-semibold">上传图片，选择模型与提示词，实时查看流式输出与耗时。</div>
        </div>
        <button v-if="showClose" class="btn" type="button" aria-label="关闭运行器" @click="emit('close')">
          <X class="h-4 w-4" />
        </button>
      </div>

      <div class="mt-5 space-y-3">
        <div v-if="error" class="rounded-2xl border border-danger/40 bg-danger/10 p-3 text-sm text-danger">
          <div class="flex items-start gap-2">
            <AlertTriangle class="mt-0.5 h-4 w-4" />
            <div class="min-w-0">{{ error }}</div>
          </div>
        </div>

        <div class="space-y-2">
          <label class="text-xs font-semibold text-muted">云平台</label>
          <select class="input" v-model="providerKey" :disabled="loading">
            <option value="" disabled>请选择云平台...</option>
            <option v-for="p in providers" :key="p.key" :value="p.key">{{ p.display_name }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <label class="text-xs font-semibold text-muted">模型</label>
          <select class="input" v-model="modelKey" :disabled="loading || !providerKey">
            <option value="" disabled>请选择模型...</option>
            <option v-for="m in models" :key="m.key" :value="m.key">{{ m.key }} - {{ m.name || m.key }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <label class="text-xs font-semibold text-muted">提示词</label>
          <select class="input" v-model="promptId" :disabled="loading">
            <option value="" disabled>请选择提示词...</option>
            <option v-for="p in prompts" :key="p.id" :value="p.id">{{ p.name || p.id }} ({{ p.id }})</option>
          </select>
        </div>

        <button class="btn btn-primary mt-2 w-full" type="button" :disabled="!canRun" @click="run">
          <Loader2 v-if="running" class="h-4 w-4 animate-spin" />
          <PlayCircle v-else class="h-4 w-4" />
          {{ running ? '运行中...' : '运行' }}
          <ArrowRight class="h-4 w-4" />
        </button>

        <div class="rounded-2xl border border-border/70 bg-white/40 p-3 text-xs text-muted backdrop-blur">
          结果由后端保存至 <span class="font-mono text-text">backend/data/outputs/</span>。
        </div>
      </div>
    </div>

    <div class="grid gap-3">
      <div class="glass p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs font-semibold text-muted">图片</div>
            <div class="mt-1 text-base font-semibold">拖拽图片或点击选择</div>
          </div>
          <span class="pill">multipart</span>
        </div>

        <div
          v-if="!previews.length"
          class="mt-5 rounded-3xl border border-dashed border-border/90 bg-white/30 p-5 backdrop-blur transition"
          :class="dragging ? 'ring-2 ring-primary/40 bg-white/45' : ''"
          @drop="onDrop"
          @dragover="onDragOver"
          @dragleave="onDragLeave"
        >
          <div class="flex flex-col items-center justify-center gap-3 text-center">
            <div class="grid h-12 w-12 place-items-center rounded-3xl border border-border/70 bg-white/55 shadow-sm backdrop-blur">
              <Image class="h-5 w-5 text-primary" />
            </div>
            <div class="text-sm font-semibold">将图片拖到这里</div>
            <div class="text-sm text-muted">支持 PNG / JPG / WEBP，可多选。</div>
            <label class="btn mt-1 cursor-pointer">
              选择文件
              <input class="hidden" type="file" multiple accept="image/*" @change="onFileChange" />
            </label>
          </div>
        </div>

        <div class="mt-4">
          <div v-if="!previews.length" class="text-sm text-muted">未选择图片。</div>

          <div v-else class="grid gap-3 md:grid-cols-[170px_1fr]">
            <div class="space-y-2">
              <div class="flex items-center justify-between gap-2">
                <div class="text-xs font-semibold text-muted">预览列表</div>
                <label class="btn cursor-pointer">
                  重新选择
                  <input class="hidden" type="file" multiple accept="image/*" @change="onFileChange" />
                </label>
              </div>
              <div class="max-h-[280px] overflow-auto rounded-2xl border border-border/60 bg-white/30 p-2 backdrop-blur">
                <button
                  v-for="(p, i) in previews"
                  :key="p.file.name + i"
                  class="mb-2 flex w-full items-center gap-2 rounded-xl border border-transparent p-2 text-left transition-colors last:mb-0"
                  :class="i === selectedPreviewIndex ? 'bg-primary/15 ring-1 ring-primary/30' : 'hover:bg-panel2/25'"
                  type="button"
                  @click="selectedPreviewIndex = i; resetView()"
                >
                  <img :src="p.url" class="h-10 w-10 rounded-lg border border-border/60 object-cover" alt="" />
                  <div class="min-w-0">
                    <div class="truncate text-sm font-semibold">{{ p.file.name }}</div>
                    <div class="mt-0.5 font-mono text-xs text-muted">{{ Math.round(p.file.size / 1024) }} KB</div>
                  </div>
                </button>
              </div>
            </div>

            <div class="rounded-3xl border border-border/70 bg-white/35 p-3 backdrop-blur">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="min-w-0">
                  <div class="truncate text-sm font-semibold">{{ previews[selectedPreviewIndex]?.file.name }}</div>
                  <div class="mt-0.5 font-mono text-xs text-muted">滚轮缩放 / 拖拽平移 / 双击重置</div>
                </div>
                <div class="flex items-center gap-2">
                  <button class="btn" type="button" @click="zoom(-0.2)">缩小</button>
                  <button class="btn" type="button" @click="zoom(0.2)">放大</button>
                  <button class="btn" type="button" @click="resetView">重置</button>
                </div>
              </div>

              <div
                class="mt-3 relative h-[320px] overflow-hidden rounded-2xl border border-border/70 bg-white/40"
                @wheel.prevent="onViewerWheel"
                @pointerdown="onViewerPointerDown"
                @pointermove="onViewerPointerMove"
                @pointerup="onViewerPointerUp"
                @pointercancel="onViewerPointerUp"
                @dblclick="resetView"
              >
                <img
                  v-if="activePreviewUrl"
                  :src="activePreviewUrl"
                  class="absolute left-1/2 top-1/2 max-w-none select-none"
                  :style="{
                    transform: `translate(calc(-50% + ${viewX}px), calc(-50% + ${viewY}px)) scale(${viewScale})`,
                    transformOrigin: 'center center',
                  }"
                  draggable="false"
                  alt=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="running || streamLog.length || streamedText" class="glass p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs font-semibold text-muted">执行过程</div>
            <div class="mt-1 text-base font-semibold">连接 / 思考(TTFT) / 流式输出 / 解析 / 保存</div>
          </div>
          <span class="pill">stream</span>
        </div>

        <div class="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-2xl border border-border/60 bg-white/35 p-3 backdrop-blur">
            <div class="text-xs text-muted">连接云服务器</div>
            <div class="mt-1 font-mono text-sm text-text">{{ fmt(connectLiveSeconds) }}</div>
          </div>
          <div class="rounded-2xl border border-border/60 bg-white/35 p-3 backdrop-blur">
            <div class="text-xs text-muted">模型思考 (TTFT)</div>
            <div class="mt-1 font-mono text-sm text-text">{{ fmt(thinkingLiveSeconds) }}</div>
          </div>
          <div class="rounded-2xl border border-border/60 bg-white/35 p-3 backdrop-blur">
            <div class="text-xs text-muted">输出中</div>
            <div class="mt-1 font-mono text-sm text-text">{{ fmt(streamingLiveSeconds) }}</div>
          </div>
          <div class="rounded-2xl border border-border/60 bg-white/35 p-3 backdrop-blur">
            <div class="text-xs text-muted">总耗时</div>
            <div class="mt-1 font-mono text-sm text-text">{{ fmt(totalLiveSeconds) }}</div>
          </div>
        </div>

        <div v-if="runMeta" class="mt-3 rounded-2xl border border-border/60 bg-white/35 p-3 text-xs backdrop-blur">
          <div class="grid gap-1 font-mono">
            <div><span class="text-muted">环境变量键:</span> <span class="text-text">{{ runMeta.api_key_env || '—' }}</span></div>
            <div><span class="text-muted">API Base:</span> <span class="text-text">{{ runMeta.api_base_url || '—' }}</span></div>
            <div><span class="text-muted">输出模式:</span> <span class="text-text">{{ runMeta.mode || 'streaming' }}</span></div>
          </div>
        </div>

        <div class="mt-4 grid gap-3 lg:grid-cols-2">
          <div class="rounded-2xl border border-border/70 bg-white/40 p-3 backdrop-blur">
            <div class="text-xs font-semibold text-muted">阶段日志</div>
            <pre ref="streamLogEl" class="mt-3 max-h-[260px] overflow-auto whitespace-pre-wrap font-mono text-xs text-text"><code>{{ streamLogText }}</code></pre>
          </div>
          <div class="rounded-2xl border border-border/70 bg-white/40 p-3 backdrop-blur">
            <div class="text-xs font-semibold text-muted">模型输出 (流式)</div>
            <pre ref="streamTextEl" class="mt-3 max-h-[260px] overflow-auto whitespace-pre-wrap font-mono text-xs text-text"><code>{{ streamedText }}</code></pre>
          </div>
        </div>
      </div>

      <div v-if="result" class="glass p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs font-semibold text-muted">结果</div>
            <div class="mt-1 text-base font-semibold">结构化 JSON</div>
          </div>
          <div class="flex flex-wrap items-center justify-end gap-2">
            <RouterLink
              v-if="outputDir"
              class="btn"
              :to="{ path: '/history', query: { output_dir: outputDir } }"
              title="打开对应的历史记录"
            >
              历史
              <ArrowRight class="h-4 w-4" />
            </RouterLink>
            <button class="btn" type="button" @click="copyResult" :disabled="!resultJson">
              <Copy class="h-4 w-4" />
              {{ copyOk ? '已复制' : '复制' }}
            </button>
            <button class="btn" type="button" @click="downloadResult" :disabled="!resultJson">
              <Download class="h-4 w-4" />
              下载
            </button>
            <span class="pill">
              <FileJson class="h-3.5 w-3.5 text-primary" />
              json
            </span>
          </div>
        </div>
        <pre class="mt-4 max-h-[520px] overflow-auto rounded-2xl border border-border/70 bg-white/40 p-4 font-mono text-xs text-text backdrop-blur"><code>{{ resultJson }}</code></pre>
      </div>
    </div>
  </div>
</template>
