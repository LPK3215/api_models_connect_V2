<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../lib/api'
import type { TaskHistoryRecord } from '../lib/types'

const route = useRoute()
const matchOutputDir = computed(() => (typeof route.query.output_dir === 'string' ? route.query.output_dir : ''))
const matchEl = ref<HTMLElement | null>(null)

function setMatchEl(el: any, r: TaskHistoryRecord) {
  const node: HTMLElement | null = el ? ((el as any).$el ? (el as any).$el : el) : null
  if (!node) return
  if (!matchOutputDir.value) return
  if (r.output_dir !== matchOutputDir.value) return
  matchEl.value = node
}

const items = ref<TaskHistoryRecord[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    const { data } = await api.get<{ items: TaskHistoryRecord[] }>('/api/v1/history')
    items.value = data.items
    await nextTick()
    if (matchEl.value) matchEl.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  } catch (e: any) {
    error.value = e?.message || 'Failed to load'
  } finally {
    loading.value = false
  }
}

async function clear() {
  await api.delete('/api/v1/history')
  await load()
}

onMounted(load)
</script>

<template>
  <section class="animate-fadeUp">
    <div class="panel">
      <div class="panel-header">
        <div>
          <div class="text-lg font-semibold">History</div>
          <div class="text-sm text-muted">Last 100 runs (recorded by backend).</div>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn" @click="load" :disabled="loading">Refresh</button>
          <button class="btn btn-danger" @click="clear" :disabled="loading || !items.length">Clear</button>
        </div>
      </div>

      <div class="panel-body">
        <div v-if="error" class="rounded-xl border border-danger/40 bg-danger/10 p-3 text-sm text-danger">{{ error }}</div>

        <div v-else-if="loading" class="text-sm text-muted">Loading...</div>

        <div v-else-if="!items.length" class="text-sm text-muted">No history yet.</div>

        <div v-else class="overflow-auto rounded-xl border border-border/50">
          <table class="w-full min-w-[720px] border-collapse text-left text-sm">
            <thead class="bg-panel2/25 text-muted">
              <tr>
                <th class="px-3 py-2 font-semibold">Time</th>
                <th class="px-3 py-2 font-semibold">Provider</th>
                <th class="px-3 py-2 font-semibold">Model</th>
                <th class="px-3 py-2 font-semibold">Files</th>
                <th class="px-3 py-2 font-semibold">OK</th>
                <th class="px-3 py-2 font-semibold">Fail</th>
                <th class="px-3 py-2 font-semibold">Output</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="r in items"
                :key="r.timestamp"
                :ref="(el) => setMatchEl(el, r)"
                class="border-t border-border/40"
                :class="
                  matchOutputDir && r.output_dir === matchOutputDir
                    ? 'bg-primary/10 ring-1 ring-primary/25'
                    : 'hover:bg-panel2/15'
                "
              >
                <td class="px-3 py-2 font-mono text-xs text-muted">{{ r.timestamp }}</td>
                <td class="px-3 py-2">{{ r.provider }}</td>
                <td class="px-3 py-2 font-mono text-xs">{{ r.model }}</td>
                <td class="px-3 py-2">{{ r.file_count }}</td>
                <td class="px-3 py-2 text-success">{{ r.success_count }}</td>
                <td class="px-3 py-2 text-danger">{{ r.failed_count }}</td>
                <td class="px-3 py-2 font-mono text-xs text-muted">{{ r.output_dir || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>
