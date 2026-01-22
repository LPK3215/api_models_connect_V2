<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, RouterLink, RouterView } from 'vue-router'
import {
  BarChart3,
  Boxes,
  Home,
  History as HistoryIcon,
  Menu,
  ScrollText,
  Settings as SettingsIcon,
  Sparkles,
  X,
} from 'lucide-vue-next'

const route = useRoute()

const nav = [
  { to: '/dashboard', label: '概览', icon: BarChart3 },
  { to: '/run', label: '运行', icon: Sparkles },
  { to: '/models', label: '模型', icon: Boxes },
  { to: '/prompts', label: '提示词', icon: ScrollText },
  { to: '/history', label: '历史', icon: HistoryIcon },
  { to: '/settings', label: '设置', icon: SettingsIcon },
]

const current = computed(() => route.path)
const isLanding = computed(() => route.path === '/')
const mobileMenu = ref(false)
</script>

<template>
  <div class="min-h-dvh">
    <RouterView v-if="isLanding" />

    <div v-else>
      <header class="sticky top-0 z-40 border-b border-border/60 bg-white/55 backdrop-blur-xl">
        <div class="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 md:px-6">
          <RouterLink to="/" class="flex items-center gap-3">
            <div class="grid h-9 w-9 place-items-center rounded-2xl border border-border/70 bg-white/50 shadow-sm backdrop-blur">
              <Home class="h-4.5 w-4.5 text-primary" />
            </div>
            <div class="leading-tight">
              <div class="text-sm font-semibold tracking-tight">API Models Connect</div>
              <div class="text-[11px] font-medium text-muted">控制台</div>
            </div>
          </RouterLink>

          <nav class="hidden items-center gap-2 md:flex">
            <RouterLink
              v-for="item in nav"
              :key="item.to"
              :to="item.to"
              class="inline-flex items-center gap-2 rounded-xl border border-transparent bg-white/0 px-3 py-2 text-sm font-semibold text-muted transition hover:bg-white/40 hover:text-text"
              :class="current === item.to ? 'border-border/70 bg-white/55 text-text' : ''"
            >
              <component :is="item.icon" class="h-4 w-4 opacity-90" />
              <span>{{ item.label }}</span>
            </RouterLink>
          </nav>

          <div class="flex items-center gap-2">
            <div class="hidden rounded-xl border border-border/70 bg-white/40 px-3 py-2 text-xs text-muted backdrop-blur md:block">
              backend: <span class="font-mono text-text">cd backend; python run_api.py</span>
            </div>
            <button class="btn md:hidden" type="button" @click="mobileMenu = !mobileMenu" aria-label="Toggle menu">
              <Menu v-if="!mobileMenu" class="h-4 w-4" />
              <X v-else class="h-4 w-4" />
            </button>
          </div>
        </div>

        <div v-if="mobileMenu" class="md:hidden">
          <div class="mx-auto max-w-7xl px-4 pb-4">
            <div class="glass-strong p-3">
              <nav class="grid gap-1">
                <RouterLink
                  v-for="item in nav"
                  :key="item.to"
                  :to="item.to"
                  class="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-muted transition hover:bg-white/45 hover:text-text"
                  :class="current === item.to ? 'bg-white/55 text-text' : ''"
                  @click="mobileMenu = false"
                >
                  <component :is="item.icon" class="h-4 w-4 opacity-90" />
                  <span>{{ item.label }}</span>
                </RouterLink>
              </nav>
            </div>
          </div>
        </div>
      </header>

      <main class="mx-auto max-w-7xl px-4 py-6 md:px-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
