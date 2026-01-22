<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

import QuickRunner from '../components/QuickRunner.vue'
</script>

<template>
  <section class="animate-fadeUp">
    <div class="flex flex-col items-start justify-between gap-3 md:flex-row md:items-center">
      <div>
        <div class="text-xs font-semibold text-muted">Run</div>
        <div class="mt-1 text-2xl font-semibold tracking-tight">Task Runner</div>
        <div class="mt-1 text-sm text-muted">Upload images, pick a model, run extraction.</div>
      </div>
      <RouterLink class="btn btn-primary" to="/history">
        查看运行历史
        <ArrowRight class="h-4 w-4" />
      </RouterLink>
    </div>

    <div class="mt-5">
      <QuickRunner />
    </div>
  </section>
</template>

