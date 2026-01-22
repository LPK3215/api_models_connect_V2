<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '../lib/api'
import type { ModelItem, PromptListItem, ProviderItem, TaskResult } from '../lib/types'

const providers = ref<ProviderItem[]>([])
const models = ref<ModelItem[]>([])
const prompts = ref<PromptListItem[]>([])

const providerKey = ref('')
const modelKey = ref('')
const promptId = ref('')

const files = ref<File[]>([])
const running = ref(false)
const error = ref<string | null>(null)
const result = ref<TaskResult | null>(null)

const canRun = computed(
  () =>
    !!providerKey.value &&
    !!modelKey.value &&
    !!promptId.value &&
    files.value.length > 0 &&
    !running.value,
)

async function loadProviders() {
  const { data } = await api.get<{ items: ProviderItem[] }>('/api/v1/providers')
  providers.value = data.items
}

async function loadModels() {
  models.value = []
  modelKey.value = ''
  if (!providerKey.value) return
  const { data } = await api.get<{ items: ModelItem[] }>(`/api/v1/providers/${providerKey.value}/models`)
  models.value = data.items
}

async function loadPrompts() {
  const { data } = await api.get<{ items: PromptListItem[] }>('/api/v1/prompts')
  prompts.value = data.items
}

function onFileChange(ev: Event) {
  const input = ev.target as HTMLInputElement
  const list = input.files ? Array.from(input.files) : []
  files.value = list
}

async function run() {
  if (!canRun.value) return
  running.value = true
  error.value = null
  result.value = null

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

onMounted(async () => {
  await Promise.all([loadProviders(), loadPrompts()])
})
</script>

<template>
  <section class="animate-fadeUp">
    <div class="panel">
      <div class="panel-header">
        <div>
          <div class="text-lg font-semibold">Task Runner</div>
          <div class="text-sm text-muted">Upload images, pick a model, run extraction.</div>
        </div>
        <button class="btn btn-primary" @click="run" :disabled="!canRun">
          {{ running ? 'Running...' : 'Run' }}
        </button>
      </div>

      <div class="panel-body space-y-4">
        <div v-if="error" class="rounded-xl border border-danger/40 bg-danger/10 p-3 text-sm text-danger">
          {{ error }}
        </div>

        <div class="grid grid-cols-1 gap-3 lg:grid-cols-3">
          <div class="space-y-2">
            <label class="text-xs font-semibold text-muted">Provider</label>
            <select class="input" v-model="providerKey" @change="loadModels">
              <option value="" disabled>Select provider...</option>
              <option v-for="p in providers" :key="p.key" :value="p.key">{{ p.display_name }}</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-semibold text-muted">Model</label>
            <select class="input" v-model="modelKey" :disabled="!providerKey">
              <option value="" disabled>Select model...</option>
              <option v-for="m in models" :key="m.key" :value="m.key">{{ m.key }} — {{ m.name }}</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-semibold text-muted">Prompt</label>
            <select class="input" v-model="promptId">
              <option value="" disabled>Select prompt...</option>
              <option v-for="p in prompts" :key="p.id" :value="p.id">{{ p.name }} ({{ p.id }})</option>
            </select>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <div class="text-sm font-semibold">Images</div>
            <span class="pill">multipart</span>
          </div>
          <div class="panel-body space-y-3">
            <input class="input" type="file" multiple accept="image/*" @change="onFileChange" />
            <div v-if="files.length" class="grid grid-cols-1 gap-2 md:grid-cols-2">
              <div v-for="f in files" :key="f.name" class="rounded-xl border border-border/50 bg-panel2/15 px-3 py-2">
                <div class="truncate text-sm font-semibold">{{ f.name }}</div>
                <div class="mt-0.5 font-mono text-xs text-muted">{{ Math.round(f.size / 1024) }} KB</div>
              </div>
            </div>
            <div v-else class="text-sm text-muted">Choose one or more images to process.</div>
          </div>
        </div>

        <div v-if="result" class="panel">
          <div class="panel-header">
            <div class="text-sm font-semibold">Result</div>
            <span class="pill">json</span>
          </div>
          <div class="panel-body">
            <pre class="max-h-[420px] overflow-auto rounded-xl border border-border/50 bg-panel2/15 p-3 font-mono text-xs text-text">{{ JSON.stringify(result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
