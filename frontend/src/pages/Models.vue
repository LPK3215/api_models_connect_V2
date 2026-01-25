<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api, API_PATHS } from '../lib/api'
import type { ModelItem, ProviderItem } from '../lib/types'

const providers = ref<ProviderItem[]>([])
const providerKey = ref('')
const models = ref<ModelItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const providerLabel = computed(
  () => providers.value.find((p) => p.key === providerKey.value)?.display_name || providerKey.value,
)

async function loadProviders() {
  const { data } = await api.get<{ items: ProviderItem[] }>(API_PATHS.providers)
  providers.value = data.items
}

async function loadModels() {
  models.value = []
  error.value = null
  if (!providerKey.value) return
  loading.value = true
  try {
    const { data } = await api.get<{ items: ModelItem[] }>(`${API_PATHS.providers}/${providerKey.value}/models`)
    models.value = data.items
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadProviders)
</script>

<template>
  <section class="animate-fadeUp">
    <div class="panel">
      <div class="panel-header">
        <div>
          <div class="text-lg font-semibold">模型池</div>
          <div class="text-sm text-muted">按云平台查看模型池与关键配置。</div>
        </div>
      </div>

      <div class="panel-body space-y-4">
        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <div class="space-y-2">
            <label class="text-xs font-semibold text-muted">云平台</label>
            <select class="input" v-model="providerKey" @change="loadModels">
              <option value="" disabled>请选择云平台...</option>
              <option v-for="p in providers" :key="p.key" :value="p.key">{{ p.display_name }}</option>
            </select>
          </div>

          <div class="rounded-xl border border-border/50 bg-panel2/15 p-3">
            <div class="text-xs text-muted">当前选择</div>
            <div class="mt-1 text-sm font-semibold">{{ providerLabel || '—' }}</div>
          </div>
        </div>

        <div v-if="error" class="rounded-xl border border-danger/40 bg-danger/10 p-3 text-sm text-danger">
          {{ error }}
        </div>

        <div class="grid grid-cols-1 gap-3">
          <div v-if="loading" class="rounded-xl border border-border/50 bg-panel2/15 p-4 text-sm text-muted">
            加载中...
          </div>

          <div v-else-if="!models.length" class="rounded-xl border border-border/50 bg-panel2/15 p-4 text-sm text-muted">
            请选择云平台以查看模型池。
          </div>

          <div v-else class="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <div v-for="m in models" :key="m.key" class="panel">
              <div class="panel-header">
                <div class="min-w-0">
                  <div class="truncate font-mono text-sm font-semibold">{{ m.key }}</div>
                  <div class="mt-0.5 truncate text-xs text-muted">{{ m.name }}</div>
                </div>
                <span class="pill">model</span>
              </div>
              <div class="panel-body space-y-2">
                <div class="text-sm text-muted">{{ m.info }}</div>
                <div class="rounded-xl border border-border/50 bg-panel2/15 p-3">
                  <div class="text-xs text-muted">环境变量键</div>
                  <div class="mt-1 font-mono text-xs text-text">{{ m.env_key || '—' }}</div>
                </div>
                <div class="rounded-xl border border-border/50 bg-panel2/15 p-3">
                  <div class="text-xs text-muted">API Base URL</div>
                  <div class="mt-1 truncate font-mono text-xs text-text">{{ m.api_base_url || '—' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
