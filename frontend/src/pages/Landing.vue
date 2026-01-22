<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  ArrowRight,
  Bolt,
  BookText,
  Cloud,
  FileJson,
  Gauge,
  History,
  Image,
  KeyRound,
  PlayCircle,
  Settings,
  Terminal,
  Wrench,
} from 'lucide-vue-next'

import { api } from '../lib/api'
import type { SystemStatus } from '../lib/types'
import QuickRunner from '../components/QuickRunner.vue'
import RealtimeViz from '../components/RealtimeViz.vue'

const year = new Date().getFullYear()
const apiOrigin = (import.meta as any).env?.VITE_API_ORIGIN || 'http://127.0.0.1:8000'
const openApiUrl = `${apiOrigin}/docs`

const mobileMenu = ref(false)
function toggleMenu() {
  mobileMenu.value = !mobileMenu.value
}

const runnerOpen = ref(false)
function openRunner() {
  runnerOpen.value = true
  requestAnimationFrame(() => {
    document.getElementById('quick-run')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

const status = ref<SystemStatus | null>(null)
const statusLoading = ref(false)
const statusOnline = ref(false)

async function loadStatus() {
  statusLoading.value = true
  try {
    const { data } = await api.get<SystemStatus>('/api/v1/system/status')
    status.value = data
    statusOnline.value = true
  } catch {
    status.value = null
    statusOnline.value = false
  } finally {
    statusLoading.value = false
  }
}

onMounted(loadStatus)

const configuredKeyCount = computed(() => {
  const keys = status.value?.api_keys || {}
  return Object.values(keys).filter((k) => k.configured).length
})
const totalKeyCount = computed(() => Object.keys(status.value?.api_keys || {}).length || 4)

const modules = [
  { to: '/run', title: '任务运行', desc: '上传图片, 选择云平台/模型/提示词, 一键处理并拿到 JSON.', icon: PlayCircle, tag: 'multipart' },
  { to: '/models', title: '模型池', desc: '按云平台查看可用模型, 环境变量和 API Base 一目了然.', icon: Cloud, tag: 'providers' },
  { to: '/prompts', title: '提示词库', desc: '把抽取提示词做成资产: 分类, 标签, 版本化管理.', icon: BookText, tag: 'yaml' },
  { to: '/history', title: '历史记录', desc: '后端记录最近运行, 快速回溯输出目录与成功率.', icon: History, tag: 'runs' },
  { to: '/settings', title: '系统设置', desc: '查看目录状态与配置文件, 为后续扩展保留入口.', icon: Settings, tag: 'local' },
  { to: '/dashboard', title: '系统概览', desc: '一眼看懂 keys/路径/统计, 发现问题就地修复.', icon: Gauge, tag: 'status' },
]

const providers = [
  { name: '阿里云 DashScope', env: 'DASHSCOPE_API_KEY' },
  { name: '豆包/火山方舟', env: 'ARK_API_KEY' },
  { name: '魔塔 ModelScope', env: 'MODELSCOPE_ACCESS_TOKEN' },
  { name: '腾讯混元', env: 'HUNYUAN_API_KEY' },
]

function providerConfigured(name: string) {
  return !!status.value?.api_keys?.[name]?.configured
}
</script>

<template>
  <div class="min-h-dvh">
    <header class="sticky top-0 z-50 border-b border-border/60 bg-white/55 backdrop-blur-xl">
      <div class="mx-auto flex max-w-[86rem] items-center justify-between gap-3 px-4 py-3 md:px-6">
        <div class="flex items-center gap-3">
          <div class="grid h-9 w-9 place-items-center rounded-2xl border border-border/70 bg-white/50 shadow-sm backdrop-blur">
            <Bolt class="h-4.5 w-4.5 text-primary" />
          </div>
          <div class="leading-tight">
            <div class="text-sm font-semibold tracking-tight">API Models Connect</div>
            <div class="text-[11px] font-medium text-muted">多云多模态批处理 - FastAPI + Vue</div>
          </div>
        </div>

        <nav class="hidden items-center gap-6 text-sm font-semibold text-muted md:flex">
          <a class="hover:text-text transition-colors" href="#workflow">工作流</a>
          <a class="hover:text-text transition-colors" href="#modules">模块</a>
          <a class="hover:text-text transition-colors" href="#providers">云平台</a>
          <a class="hover:text-text transition-colors" href="#outputs">输出</a>
          <a class="hover:text-text transition-colors" href="#get-started">开始</a>
        </nav>

        <div class="hidden items-center gap-2 md:flex">
          <RouterLink class="btn" to="/dashboard">打开控制台</RouterLink>
          <button class="btn btn-primary" type="button" @click="openRunner">
            立即运行
            <ArrowRight class="h-4 w-4" />
          </button>
        </div>

        <button class="btn md:hidden" type="button" @click="toggleMenu" aria-label="Toggle navigation">
          Menu
        </button>
      </div>

      <div v-if="mobileMenu" class="md:hidden">
        <div class="mx-auto max-w-[86rem] px-4 pb-4">
          <div class="glass-strong p-4">
            <div class="grid gap-3 text-sm font-semibold">
              <a class="text-muted hover:text-text transition-colors" href="#workflow" @click="mobileMenu = false">工作流</a>
              <a class="text-muted hover:text-text transition-colors" href="#modules" @click="mobileMenu = false">模块</a>
              <a class="text-muted hover:text-text transition-colors" href="#providers" @click="mobileMenu = false">云平台</a>
              <a class="text-muted hover:text-text transition-colors" href="#outputs" @click="mobileMenu = false">输出</a>
              <a class="text-muted hover:text-text transition-colors" href="#get-started" @click="mobileMenu = false">开始</a>
              <div class="grid gap-2 pt-1">
                <button class="btn btn-primary w-full" type="button" @click="mobileMenu = false; openRunner()">立即运行</button>
                <RouterLink class="btn w-full" to="/dashboard" @click="mobileMenu = false">打开控制台</RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <section class="mx-auto max-w-[86rem] px-4 py-10 md:px-6 md:py-16">
      <div class="glass p-6 md:p-8">
        <div class="grid items-start gap-10 lg:grid-cols-2">
          <div class="animate-fadeUp">
          <div class="inline-flex flex-wrap items-center gap-2 rounded-full border border-border/70 bg-white/45 px-3 py-1 text-xs font-semibold text-muted backdrop-blur">
            <span class="inline-flex items-center gap-1.5">
              <Wrench class="h-3.5 w-3.5 text-primary" />
              批量图片 -> 结构化 JSON
            </span>
            <span class="text-muted/60">|</span>
            <span class="inline-flex items-center gap-1.5">
              <Terminal class="h-3.5 w-3.5 text-primary" />
              Web / API / CLI
            </span>
          </div>

          <h1 class="mt-5 text-balance text-4xl font-semibold tracking-tight md:text-5xl">
            用一个控制台, 连接多云大模型, 把多模态批处理跑得又快又稳.
          </h1>

          <p class="mt-4 max-w-xl text-pretty text-base text-muted md:text-lg">
            你的项目核心不是页面, 而是一条可靠流程: 选择云平台与模型, 套用提示词, 批量处理图片, 输出 JSON 并沉淀历史.
            这个首页按你的功能把流程展示出来, 不做模板复刻.
          </p>

          <div class="mt-6 flex flex-col gap-2 sm:flex-row sm:items-center">
            <button class="btn btn-primary w-full justify-center sm:w-auto" type="button" @click="openRunner">
              立即运行一次任务
              <ArrowRight class="h-4 w-4" />
            </button>
            <RouterLink class="btn w-full justify-center sm:w-auto" to="/dashboard">查看系统状态</RouterLink>
            <a class="btn w-full justify-center sm:w-auto" :href="openApiUrl" target="_blank" rel="noreferrer">OpenAPI</a>
          </div>

          <div class="mt-6 flex flex-wrap items-center gap-2">
            <span class="pill">
              API
              <span
                class="ml-1 h-2 w-2 rounded-full"
                :class="statusLoading ? 'bg-warn' : statusOnline ? 'bg-success' : 'bg-danger'"
              />
              <span class="ml-1">{{ statusLoading ? 'checking' : statusOnline ? 'online' : 'offline' }}</span>
            </span>
            <span v-if="status?.statistics" class="pill font-mono">
              providers {{ status.statistics.providers }} | models {{ status.statistics.models }} | prompts {{ status.statistics.prompts }}
            </span>
            <span class="pill font-mono">keys {{ configuredKeyCount }}/{{ totalKeyCount }}</span>
          </div>
          </div>

          <div class="animate-fadeUp [animation-delay:90ms]">
            <RealtimeViz />
          </div>
        </div>

        <div class="mt-6 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          <div class="rounded-2xl border border-border/70 bg-white/30 p-5 backdrop-blur-xl">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="text-xs font-semibold text-muted">一次任务由什么组成</div>
                <div class="mt-1 text-sm font-semibold">Provider + Model + Prompt + Images</div>
              </div>
              <span class="pill">task</span>
            </div>
            <div class="mt-4 grid gap-2">
              <div class="flex flex-wrap gap-2">
                <span class="pill border-primary/25 bg-white/45 text-primary">provider</span>
                <span class="pill border-primary/25 bg-white/45 text-primary">model</span>
                <span class="pill border-primary/25 bg-white/45 text-primary">prompt</span>
                <span class="pill border-primary/25 bg-white/45 text-primary">files</span>
              </div>
              <div class="rounded-2xl border border-border/70 bg-white/40 p-3 text-sm text-muted backdrop-blur">
                UI 负责选择与发起请求, 后端负责处理、落盘与记录历史.
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-border/70 bg-white/30 p-5 backdrop-blur-xl">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="text-xs font-semibold text-muted">输出是可以复盘的</div>
                <div class="mt-1 text-sm font-semibold">结构化 JSON + 输出目录</div>
              </div>
              <span class="pill">local</span>
            </div>
            <div class="mt-4 rounded-2xl border border-border/70 bg-white/40 p-3 font-mono text-[12px] leading-relaxed text-text backdrop-blur">
              <div class="text-muted">{</div>
              <div class="pl-4"><span class="text-muted">"summary"</span>: { <span class="text-muted">"ok"</span>: 12, <span class="text-muted">"fail"</span>: 0 },</div>
              <div class="pl-4"><span class="text-muted">"results"</span>: [ ... ]</div>
              <div class="text-muted">}</div>
            </div>
          </div>

          <div class="rounded-2xl border border-border/70 bg-white/30 p-5 backdrop-blur-xl">
            <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div class="min-w-0">
                <div class="text-xs font-semibold text-muted">三种使用方式</div>
                <div class="mt-1 text-sm font-semibold">Web 控制台 / FastAPI / CLI</div>
                <div class="mt-2 text-sm text-muted">先在 UI 跑通流程, 再用 API 或 CLI 脚本化批量执行.</div>
              </div>
              <div class="flex flex-col gap-2 sm:flex-row">
                <RouterLink class="btn btn-primary justify-center" to="/run">
                  <PlayCircle class="h-4 w-4" />
                  Task Runner
                </RouterLink>
                <a class="btn justify-center" :href="openApiUrl" target="_blank" rel="noreferrer">
                  <FileJson class="h-4 w-4" />
                  API Docs
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="quick-run" class="mx-auto max-w-[86rem] px-4 pb-12 md:px-6 md:pb-16">
      <div class="glass p-6">
        <div class="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
          <div class="min-w-0">
            <div class="text-xs font-semibold text-muted">Quick Run</div>
            <div class="mt-1 text-lg font-semibold tracking-tight">直接在主页执行 Task Runner</div>
            <div class="mt-1 text-sm text-muted">
              这里只做关键步骤: 选择 provider/model/prompt + 上传图片 + run. 其它 CRUD 在对应模块里完成.
            </div>
          </div>
          <div class="flex w-full flex-col gap-2 sm:w-auto sm:flex-row">
            <button class="btn w-full justify-center sm:w-auto" type="button" @click="runnerOpen = !runnerOpen">
              {{ runnerOpen ? '收起' : '展开' }}
            </button>
            <RouterLink class="btn btn-primary w-full justify-center sm:w-auto" to="/run">全屏运行</RouterLink>
          </div>
        </div>

        <div v-if="runnerOpen" class="mt-6">
          <QuickRunner :active="runnerOpen" />
        </div>
        <div v-else class="mt-6 grid gap-3 md:grid-cols-3">
          <div class="rounded-2xl border border-border/70 bg-white/40 p-4 backdrop-blur">
            <div class="text-sm font-semibold">1. 选择模型</div>
            <div class="mt-1 text-sm text-muted">Provider + Model + Prompt</div>
          </div>
          <div class="rounded-2xl border border-border/70 bg-white/40 p-4 backdrop-blur">
            <div class="text-sm font-semibold">2. 上传图片</div>
            <div class="mt-1 text-sm text-muted">拖拽或选择多个图片文件</div>
          </div>
          <div class="rounded-2xl border border-border/70 bg-white/40 p-4 backdrop-blur">
            <div class="text-sm font-semibold">3. 运行并拿到 JSON</div>
            <div class="mt-1 text-sm text-muted">结果会由后端落盘并写入历史</div>
          </div>
        </div>
      </div>
    </section>

    <section id="workflow" class="mx-auto max-w-[86rem] px-4 pb-12 md:px-6 md:pb-16">
      <div class="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div class="animate-fadeUp">
          <div class="text-xs font-semibold text-muted">Workflow</div>
          <h2 class="mt-2 text-2xl font-semibold tracking-tight">把你的后端能力, 翻译成清晰可执行的流程.</h2>
          <p class="mt-3 text-sm text-muted">
            这个项目本质是图片批处理 + 云模型调用 + 提示词抽取 + JSON 落地. 首页用 4 步讲清楚, 每一步都有对应页面.
          </p>
        </div>

        <div class="grid gap-3 md:grid-cols-4">
          <div class="glass p-5">
            <div class="flex items-start justify-between gap-3">
              <div class="grid h-10 w-10 place-items-center rounded-2xl border border-border/70 bg-white/55 shadow-sm backdrop-blur">
                <KeyRound class="h-5 w-5 text-primary" />
              </div>
              <span class="pill">1</span>
            </div>
            <div class="mt-3 text-sm font-semibold">配置密钥</div>
            <div class="mt-1 text-sm text-muted">只在环境变量/.env, UI 只显示状态.</div>
          </div>

          <div class="glass p-5">
            <div class="flex items-start justify-between gap-3">
              <div class="grid h-10 w-10 place-items-center rounded-2xl border border-border/70 bg-white/55 shadow-sm backdrop-blur">
                <Cloud class="h-5 w-5 text-primary" />
              </div>
              <span class="pill">2</span>
            </div>
            <div class="mt-3 text-sm font-semibold">选择云平台/模型</div>
            <div class="mt-1 text-sm text-muted">Model pool 按 provider 组织, 随时可扩展.</div>
          </div>

          <div class="glass p-5">
            <div class="flex items-start justify-between gap-3">
              <div class="grid h-10 w-10 place-items-center rounded-2xl border border-border/70 bg-white/55 shadow-sm backdrop-blur">
                <Image class="h-5 w-5 text-primary" />
              </div>
              <span class="pill">3</span>
            </div>
            <div class="mt-3 text-sm font-semibold">上传图片批处理</div>
            <div class="mt-1 text-sm text-muted">multipart 上传, 后端负责压缩/重试/落盘.</div>
          </div>

          <div class="glass p-5">
            <div class="flex items-start justify-between gap-3">
              <div class="grid h-10 w-10 place-items-center rounded-2xl border border-border/70 bg-white/55 shadow-sm backdrop-blur">
                <FileJson class="h-5 w-5 text-primary" />
              </div>
              <span class="pill">4</span>
            </div>
            <div class="mt-3 text-sm font-semibold">拿到 JSON 并复盘</div>
            <div class="mt-1 text-sm text-muted">输出目录 + 历史记录, 为迭代提示词服务.</div>
          </div>
        </div>
      </div>
    </section>

    <section id="modules" class="mx-auto max-w-[86rem] px-4 pb-12 md:px-6 md:pb-16">
      <div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <div class="text-xs font-semibold text-muted">Console</div>
          <h2 class="mt-2 text-2xl font-semibold tracking-tight">你的功能, 变成一组明确的页面.</h2>
        </div>
        <RouterLink class="btn w-full justify-center md:w-auto" to="/dashboard">进入控制台</RouterLink>
      </div>

      <div class="mt-6 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        <RouterLink
          v-for="m in modules"
          :key="m.to"
          :to="m.to"
          class="glass group p-6 transition-all hover:-translate-y-0.5 hover:bg-white/45"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="grid h-10 w-10 place-items-center rounded-2xl border border-border/70 bg-white/55 shadow-sm backdrop-blur">
              <component :is="m.icon" class="h-5 w-5 text-primary" />
            </div>
            <span class="pill">{{ m.tag }}</span>
          </div>
          <div class="mt-4 text-sm font-semibold">{{ m.title }}</div>
          <div class="mt-1 text-sm text-muted">{{ m.desc }}</div>
          <div class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary">
            打开
            <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </div>
        </RouterLink>
      </div>
    </section>

    <section id="providers" class="mx-auto max-w-[86rem] px-4 pb-12 md:px-6 md:pb-16">
      <div class="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div>
          <div class="text-xs font-semibold text-muted">Providers</div>
          <h2 class="mt-2 text-2xl font-semibold tracking-tight">多云平台接入, 但密钥永远留在你本机.</h2>
          <p class="mt-3 text-sm text-muted">
            后端只读取环境变量, UI 只展示 configured/missing. 你之后要改配置方式, 也可以在这里继续演进.
          </p>
          <div class="mt-4 flex flex-wrap gap-2">
            <span class="pill">
              <KeyRound class="h-3.5 w-3.5 text-primary" />
              keys {{ configuredKeyCount }}/{{ totalKeyCount }}
            </span>
            <RouterLink class="pill hover:bg-panel2/60" to="/dashboard">去 Dashboard 查看详情</RouterLink>
          </div>
        </div>

        <div class="grid gap-3 md:grid-cols-2">
          <div v-for="p in providers" :key="p.env" class="glass p-6">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="truncate text-sm font-semibold">{{ p.name }}</div>
                <div class="mt-1 font-mono text-xs text-muted">{{ p.env }}</div>
              </div>
              <span
                class="pill"
                :class="providerConfigured(p.name) ? 'border-success/40 text-success bg-success/10' : 'border-warn/40 text-warn bg-warn/10'"
              >
                {{ providerConfigured(p.name) ? 'configured' : 'missing' }}
              </span>
            </div>
            <div class="mt-4 rounded-2xl border border-border/70 bg-white/40 p-3 text-sm text-muted backdrop-blur">
              <div class="font-semibold text-text">模型池与路由</div>
              <div class="mt-1">模型清单来自 `backend/config/models.yml`, 你可按 provider 持续扩展.</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="outputs" class="mx-auto max-w-[86rem] px-4 pb-12 md:px-6 md:pb-16">
      <div class="grid gap-6 lg:grid-cols-2">
        <div>
          <div class="text-xs font-semibold text-muted">Outputs</div>
          <h2 class="mt-2 text-2xl font-semibold tracking-tight">输出可追溯: 目录 + JSON + run history.</h2>
          <p class="mt-3 text-sm text-muted">
            你关心的不是这次生成了多少字, 而是每次都有结构化结果可复盘. 这让你能快速迭代提示词, 并对比不同模型表现.
          </p>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <div class="glass p-5">
              <div class="text-sm font-semibold">落盘目录</div>
              <div class="mt-2 font-mono text-xs text-muted">
                backend/data/outputs/<br />
                &nbsp;&nbsp;&lt;provider-model&gt;/<br />
                &nbsp;&nbsp;&nbsp;&nbsp;*_result.json
              </div>
            </div>
            <div class="glass p-5">
              <div class="text-sm font-semibold">历史记录</div>
              <div class="mt-2 text-sm text-muted">记录最近 100 次运行, 包含输出目录与成功/失败数量.</div>
              <RouterLink class="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-primary" to="/history">
                打开 History
                <ArrowRight class="h-4 w-4" />
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="glass p-6">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-xs font-semibold text-muted">Example</div>
              <div class="mt-1 text-sm font-semibold">一次处理请求 (curl)</div>
            </div>
            <span class="pill">api</span>
          </div>
          <pre class="mt-4 overflow-auto rounded-2xl border border-border/70 bg-white/40 p-4 font-mono text-xs text-text backdrop-blur"><code>curl -X POST "{{ apiOrigin }}/api/v1/tasks/process" ^
  -F "provider=modelscope" ^
  -F "model=Qwen-Qwen2.5-VL-72B-Instruct" ^
  -F "prompt_id=default" ^
  -F "files=@input.png"</code></pre>
          <div class="mt-3 text-sm text-muted">
            Web 控制台对应的就是同一条 API. UI 只是帮你把 provider/model/prompt/files 组织起来.
          </div>
        </div>
      </div>
    </section>

    <section id="get-started" class="mx-auto max-w-[86rem] px-4 pb-16 md:px-6 md:pb-24">
      <div class="glass p-6">
        <div class="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div class="min-w-0">
            <div class="text-xs font-semibold text-muted">Get Started</div>
            <div class="mt-1 text-lg font-semibold">本地启动 (开发模式)</div>
            <div class="mt-2 text-sm text-muted">先跑后端, 再跑前端. 建议先跑一次环境检测脚本.</div>
          </div>
          <div class="flex flex-col gap-2 sm:flex-row">
            <button class="btn" type="button" @click="loadStatus">刷新状态</button>
            <RouterLink class="btn btn-primary" to="/run">打开 Task Runner</RouterLink>
          </div>
        </div>

        <div class="mt-5 grid gap-3 lg:grid-cols-3">
          <div class="rounded-2xl border border-border/70 bg-white/40 p-4 backdrop-blur">
            <div class="flex items-center gap-2 text-sm font-semibold">
              <Wrench class="h-4 w-4 text-primary" />
              环境检测
            </div>
            <pre class="mt-3 overflow-auto font-mono text-xs text-text"><code>cd backend
python scripts/check_auto.py</code></pre>
          </div>
          <div class="rounded-2xl border border-border/70 bg-white/40 p-4 backdrop-blur">
            <div class="flex items-center gap-2 text-sm font-semibold">
              <Bolt class="h-4 w-4 text-primary" />
              后端 API
            </div>
            <pre class="mt-3 overflow-auto font-mono text-xs text-text"><code>cd backend
python run_api.py</code></pre>
          </div>
          <div class="rounded-2xl border border-border/70 bg-white/40 p-4 backdrop-blur">
            <div class="flex items-center gap-2 text-sm font-semibold">
              <Terminal class="h-4 w-4 text-primary" />
              前端 UI
            </div>
            <pre class="mt-3 overflow-auto font-mono text-xs text-text"><code>cd frontend
npm install
npm run dev</code></pre>
          </div>
        </div>
      </div>
    </section>

    <footer class="border-t border-border/70 bg-white/35 backdrop-blur-xl">
      <div class="mx-auto max-w-[86rem] px-4 py-10 md:px-6">
        <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div class="flex items-center gap-3">
            <div class="grid h-9 w-9 place-items-center rounded-2xl border border-border/70 bg-white/50 shadow-sm backdrop-blur">
              <Bolt class="h-4.5 w-4.5 text-primary" />
            </div>
            <div class="leading-tight">
              <div class="text-sm font-semibold tracking-tight">API Models Connect</div>
              <div class="text-[11px] text-muted">© {{ year }}. Local-first, batch-first.</div>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm font-semibold text-muted">
            <a class="hover:text-text transition-colors" href="#workflow">工作流</a>
            <a class="hover:text-text transition-colors" href="#modules">模块</a>
            <a class="hover:text-text transition-colors" href="#providers">云平台</a>
            <a class="hover:text-text transition-colors" href="#get-started">开始</a>
            <RouterLink class="hover:text-text transition-colors" to="/dashboard">控制台</RouterLink>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
