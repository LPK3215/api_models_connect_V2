<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { AlertTriangle, ArrowRight, Copy, Download, FileJson, Image, Loader2, PlayCircle, X } from 'lucide-vue-next'

import { api } from '../lib/api'
import type { ModelItem, PromptListItem, ProviderItem, TaskResult } from '../lib/types'

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
      api.get<{ items: ProviderItem[] }>('/api/v1/providers'),
      api.get<{ items: PromptListItem[] }>('/api/v1/prompts'),
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
    error.value = e?.message || 'Failed to load runner data'
  } finally {
    loading.value = false
  }
}

async function loadModels() {
  models.value = []
  modelKey.value = ''
  if (!providerKey.value) return
  try {
    const { data } = await api.get<{ items: ModelItem[] }>(`/api/v1/providers/${providerKey.value}/models`)
    models.value = data.items
    const pending = pendingModelKey.value
    if (pending && models.value.some((m) => m.key === pending)) modelKey.value = pending
    pendingModelKey.value = null
  } catch (e: any) {
    error.value = e?.message || 'Failed to load models'
  }
}

function setFiles(list: File[]) {
  files.value = list
}

function onFileChange(ev: Event) {
  const input = ev.target as HTMLInputElement
  const list = input.files ? Array.from(input.files) : []
  setFiles(list)
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

async function run() {
  if (!canRun.value) return
  running.value = true
  error.value = null
  result.value = null
  copyOk.value = false

  try {
    const form = new FormData()
    form.append('provider', providerKey.value)
    form.append('model', modelKey.value)
    form.append('prompt_id', promptId.value)
    for (const f of files.value) form.append('files', f)

    const { data } = await api.post<TaskResult>('/api/v1/tasks/process', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    result.value = data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Run failed'
  } finally {
    running.value = false
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
      error.value = 'Copy failed'
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
})
</script>

<template>
  <div class="grid gap-3 lg:grid-cols-[360px_1fr]">
    <div class="glass p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="text-xs font-semibold text-muted">Task Runner</div>
          <div class="mt-1 text-base font-semibold">Upload images, pick a model, run extraction.</div>
        </div>
        <button v-if="showClose" class="btn" type="button" aria-label="Close runner" @click="emit('close')">
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
          <label class="text-xs font-semibold text-muted">Provider</label>
          <select class="input" v-model="providerKey" :disabled="loading">
            <option value="" disabled>Select provider...</option>
            <option v-for="p in providers" :key="p.key" :value="p.key">{{ p.display_name }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <label class="text-xs font-semibold text-muted">Model</label>
          <select class="input" v-model="modelKey" :disabled="loading || !providerKey">
            <option value="" disabled>Select model...</option>
            <option v-for="m in models" :key="m.key" :value="m.key">{{ m.key }} - {{ m.name || m.key }}</option>
          </select>
        </div>

        <div class="space-y-2">
          <label class="text-xs font-semibold text-muted">Prompt</label>
          <select class="input" v-model="promptId" :disabled="loading">
            <option value="" disabled>Select prompt...</option>
            <option v-for="p in prompts" :key="p.id" :value="p.id">{{ p.name || p.id }} ({{ p.id }})</option>
          </select>
        </div>

        <button class="btn btn-primary mt-2 w-full" type="button" :disabled="!canRun" @click="run">
          <Loader2 v-if="running" class="h-4 w-4 animate-spin" />
          <PlayCircle v-else class="h-4 w-4" />
          {{ running ? 'Running...' : 'Run' }}
          <ArrowRight class="h-4 w-4" />
        </button>

        <div class="rounded-2xl border border-border/70 bg-white/40 p-3 text-xs text-muted backdrop-blur">
          Results are saved under <span class="font-mono text-text">backend/data/outputs/</span> by the backend.
        </div>
      </div>
    </div>

    <div class="grid gap-3">
      <div class="glass p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs font-semibold text-muted">Images</div>
            <div class="mt-1 text-base font-semibold">Drop files or click to choose</div>
          </div>
          <span class="pill">multipart</span>
        </div>

        <div
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
            <div class="text-sm font-semibold">Drag & drop images here</div>
            <div class="text-sm text-muted">PNG, JPG, WEBP. Multiple files supported.</div>
            <label class="btn mt-1 cursor-pointer">
              Choose files
              <input class="hidden" type="file" multiple accept="image/*" @change="onFileChange" />
            </label>
          </div>
        </div>

        <div class="mt-4">
          <div v-if="!files.length" class="text-sm text-muted">No files selected.</div>
          <div v-else class="grid grid-cols-1 gap-2 md:grid-cols-2">
            <div v-for="f in files" :key="f.name" class="rounded-2xl border border-border/70 bg-white/35 px-3 py-2 backdrop-blur">
              <div class="truncate text-sm font-semibold">{{ f.name }}</div>
              <div class="mt-0.5 font-mono text-xs text-muted">{{ Math.round(f.size / 1024) }} KB</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="result" class="glass p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs font-semibold text-muted">Result</div>
            <div class="mt-1 text-base font-semibold">Structured JSON</div>
          </div>
          <div class="flex flex-wrap items-center justify-end gap-2">
            <RouterLink
              v-if="outputDir"
              class="btn"
              :to="{ path: '/history', query: { output_dir: outputDir } }"
              title="Open matching history record"
            >
              History
              <ArrowRight class="h-4 w-4" />
            </RouterLink>
            <button class="btn" type="button" @click="copyResult" :disabled="!resultJson">
              <Copy class="h-4 w-4" />
              {{ copyOk ? 'Copied' : 'Copy' }}
            </button>
            <button class="btn" type="button" @click="downloadResult" :disabled="!resultJson">
              <Download class="h-4 w-4" />
              Download
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
