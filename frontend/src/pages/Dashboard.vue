<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../lib/api'
import type { SystemStatus } from '../lib/types'

const loading = ref(true)
const error = ref<string | null>(null)
const status = ref<SystemStatus | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    const { data } = await api.get<SystemStatus>('/api/v1/system/status')
    status.value = data
  } catch (e: any) {
    error.value = e?.message || 'Failed to load'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="animate-fadeUp">
    <div class="panel">
      <div class="panel-header">
        <div>
          <div class="text-lg font-semibold">Dashboard</div>
          <div class="text-sm text-muted">System status, keys, and quick telemetry.</div>
        </div>
        <button class="btn" @click="load" :disabled="loading">Refresh</button>
      </div>

      <div class="panel-body">
        <div v-if="error" class="rounded-xl border border-danger/40 bg-danger/10 p-3 text-sm text-danger">
          {{ error }}
        </div>

        <div v-else class="space-y-5">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div class="kpi">
              <div class="label">Providers</div>
              <div class="value">{{ status?.statistics?.providers ?? '—' }}</div>
            </div>
            <div class="kpi">
              <div class="label">Models</div>
              <div class="value">{{ status?.statistics?.models ?? '—' }}</div>
            </div>
            <div class="kpi">
              <div class="label">Prompts</div>
              <div class="value">{{ status?.statistics?.prompts ?? '—' }}</div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <div class="panel">
              <div class="panel-header">
                <div class="text-sm font-semibold">API Keys</div>
                <span class="pill">env</span>
              </div>
              <div class="panel-body">
                <div class="space-y-2">
                  <div
                    v-for="(v, k) in status?.api_keys"
                    :key="k"
                    class="flex items-center justify-between gap-3 rounded-xl border border-border/50 bg-panel2/15 px-3 py-2"
                  >
                    <div class="min-w-0">
                      <div class="truncate text-sm font-semibold">{{ k }}</div>
                      <div class="font-mono text-xs text-muted">{{ v.env_key }}</div>
                    </div>
                    <span
                      class="pill"
                      :class="v.configured ? 'border-success/40 text-success bg-success/10' : 'border-warn/40 text-warn bg-warn/10'"
                    >
                      {{ v.configured ? 'configured' : 'missing' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="panel">
              <div class="panel-header">
                <div class="text-sm font-semibold">Project Paths</div>
                <span class="pill">fs</span>
              </div>
              <div class="panel-body">
                <div class="space-y-2">
                  <div
                    v-for="(v, k) in status?.directories"
                    :key="k"
                    class="rounded-xl border border-border/50 bg-panel2/15 px-3 py-2"
                  >
                    <div class="flex items-center justify-between gap-3">
                      <div class="text-sm font-semibold">{{ k }}</div>
                      <span class="pill" :class="v.exists ? 'border-success/40 text-success bg-success/10' : 'border-danger/40 text-danger bg-danger/10'">
                        {{ v.exists ? 'ok' : 'missing' }}
                      </span>
                    </div>
                    <div class="mt-1 truncate font-mono text-xs text-muted">{{ v.path }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
