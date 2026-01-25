<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api, API_PATHS } from '../lib/api'
import type { SystemStatus } from '../lib/types'

const status = ref<SystemStatus | null>(null)
const error = ref<string | null>(null)

const apiOrigin = import.meta.env.VITE_API_ORIGIN || 'http://127.0.0.1:8000'

const envList = computed(() => {
  const keys = status.value?.api_keys || {}
  return Object.entries(keys).map(([name, v]) => ({ name, env: v.env_key, ok: v.configured }))
})

onMounted(async () => {
  try {
    const { data } = await api.get<SystemStatus>(API_PATHS.systemStatus)
    status.value = data
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  }
})
</script>

<template>
  <section class="animate-fadeUp">
    <div class="panel">
      <div class="panel-header">
        <div>
          <div class="text-lg font-semibold">Settings</div>
          <div class="text-sm text-muted">环境变量、API 地址与运行状态。</div>
        </div>
      </div>

      <div class="panel-body space-y-4">
        <div v-if="error" class="rounded-xl border border-danger/40 bg-danger/10 p-3 text-sm text-danger">{{ error }}</div>

        <div class="panel">
          <div class="panel-header">
            <div class="text-sm font-semibold">前端 API 地址</div>
            <span class="pill">env</span>
          </div>
          <div class="panel-body">
            <div class="font-mono text-sm">{{ apiOrigin }}</div>
            <div class="mt-1 text-xs text-muted">在 frontend/.env.development 中设置 VITE_API_ORIGIN。</div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <div class="text-sm font-semibold">所需 API Key</div>
            <span class="pill">.env</span>
          </div>
          <div class="panel-body space-y-2">
            <div v-for="k in envList" :key="k.env" class="flex items-center justify-between rounded-xl border border-border/50 bg-panel2/15 px-3 py-2">
              <div>
                <div class="text-sm font-semibold">{{ k.name }}</div>
                <div class="font-mono text-xs text-muted">{{ k.env }}</div>
              </div>
              <span class="pill" :class="k.ok ? 'border-success/40 text-success bg-success/10' : 'border-warn/40 text-warn bg-warn/10'">
                {{ k.ok ? '已配置' : '缺失' }}
              </span>
            </div>
          </div>
        </div>

        <div class="rounded-xl border border-border/60 bg-panel2/15 p-3 text-sm text-muted">
          后端接口文档：<span class="font-mono text-text">/docs</span> 与 <span class="font-mono text-text">/redoc</span>（FastAPI）。
        </div>
      </div>
    </div>
  </section>
</template>
