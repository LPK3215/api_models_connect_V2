<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, API_PATHS } from '../lib/api'
import type { PromptDetail, PromptListItem } from '../lib/types'

const items = ref<PromptListItem[]>([])
const selected = ref<string>('')
const detail = ref<PromptDetail | null>(null)
const busy = ref(false)
const error = ref<string | null>(null)

const form = ref({
  name: '',
  category: '通用',
  description: '',
  tags: '' as string,
  prompt: '',
})

async function loadList() {
  const { data } = await api.get<{ items: PromptListItem[] }>(API_PATHS.prompts)
  items.value = data.items
}

async function loadDetail(id: string) {
  if (!id) return
  const { data } = await api.get<PromptDetail>(`${API_PATHS.prompts}/${id}`)
  detail.value = data
  form.value.name = data.name || ''
  form.value.category = data.category || '通用'
  form.value.description = data.description || ''
  form.value.tags = (data.tags || []).join(', ')
  form.value.prompt = data.prompt || ''
}

function newPrompt() {
  selected.value = ''
  detail.value = null
  form.value = { name: '', category: '通用', description: '', tags: '', prompt: '' }
}

async function save() {
  busy.value = true
  error.value = null
  try {
    await api.post(API_PATHS.prompts, {
      name: form.value.name,
      category: form.value.category,
      description: form.value.description,
      tags: form.value.tags.split(',').map((s) => s.trim()).filter(Boolean),
      prompt: form.value.prompt,
    })

    await loadList()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '保存失败'
  } finally {
    busy.value = false
  }
}

async function remove() {
  if (!detail.value?.id) return
  busy.value = true
  error.value = null
  try {
    await api.delete(`${API_PATHS.prompts}/${detail.value.id}`)
    await loadList()
    newPrompt()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '删除失败'
  } finally {
    busy.value = false
  }
}

onMounted(loadList)
</script>

<template>
  <section class="animate-fadeUp">
      <div class="panel">
      <div class="panel-header">
        <div>
          <div class="text-lg font-semibold">提示词库</div>
          <div class="text-sm text-muted">管理可复用的抽取提示词。</div>
        </div>
        <button class="btn" @click="newPrompt">新建</button>
      </div>

      <div class="panel-body space-y-4">
        <div v-if="error" class="rounded-xl border border-danger/40 bg-danger/10 p-3 text-sm text-danger">{{ error }}</div>

        <div class="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
          <div class="panel">
            <div class="panel-header">
              <div class="text-sm font-semibold">列表</div>
              <span class="pill">{{ items.length }}</span>
            </div>
            <div class="max-h-[520px] overflow-auto p-2">
              <button
                v-for="p in items"
                :key="p.id"
                class="w-full rounded-xl border border-transparent px-3 py-2 text-left transition-colors"
                :class="selected === p.id ? 'bg-primary/15 ring-1 ring-primary/30' : 'hover:bg-panel2/25'"
                @click="selected = p.id; loadDetail(p.id)"
              >
                <div class="truncate text-sm font-semibold">{{ p.name || p.id }}</div>
                <div class="mt-0.5 truncate text-xs text-muted">{{ p.category }} · {{ p.id }}</div>
              </button>
            </div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <div class="text-sm font-semibold">编辑</div>
              <div class="flex items-center gap-2">
                <button class="btn btn-primary" @click="save" :disabled="busy">保存</button>
                <button class="btn btn-danger" @click="remove" :disabled="busy || !detail?.id">删除</button>
              </div>
            </div>

            <div class="panel-body space-y-3">
              <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                <div class="space-y-2">
                  <label class="text-xs font-semibold text-muted">名称</label>
                  <input class="input" v-model="form.name" placeholder="例如：发票抽取" />
                </div>
                <div class="space-y-2">
                  <label class="text-xs font-semibold text-muted">分类</label>
                  <input class="input" v-model="form.category" placeholder="通用" />
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-xs font-semibold text-muted">描述</label>
                <input class="input" v-model="form.description" placeholder="简短描述..." />
              </div>

              <div class="space-y-2">
                <label class="text-xs font-semibold text-muted">标签（逗号分隔）</label>
                <input class="input" v-model="form.tags" placeholder="JSON, OCR, 发票" />
              </div>

              <div class="space-y-2">
                <label class="text-xs font-semibold text-muted">提示词内容</label>
                <textarea class="input min-h-[280px] font-mono" v-model="form.prompt" placeholder="在这里编写提示词..." />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
