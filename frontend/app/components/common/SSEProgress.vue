<script setup lang="ts">
import type { SSEProgress } from '~/api/types'

interface Props {
  progress: SSEProgress | null
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: true,
})

// 阶段显示文本
const stageText = computed(() => {
  if (!props.progress)
    return '等待开始'
  const stageMap: Record<string, string> = {
    init: '初始化',
    fetching: '获取中',
    saving: '保存中',
    calculating: '计算中',
    completed: '已完成',
    error: '错误',
  }
  return stageMap[props.progress.stage] || '未知'
})

// 阶段颜色
const stageColor = computed(() => {
  if (!props.progress)
    return 'default'
  const colorMap: Record<string, string> = {
    init: 'default',
    fetching: 'primary',
    saving: 'primary',
    calculating: 'primary',
    completed: 'success',
    error: 'destructive',
  }
  return colorMap[props.progress.stage] || 'default'
})

// 预计剩余时间文本
const remainingTimeText = computed(() => {
  if (!props.progress?.estimated_remaining_time)
    return ''
  const seconds = props.progress.estimated_remaining_time
  if (seconds < 60)
    return `${Math.round(seconds)}秒`
  if (seconds < 3600)
    return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600)}小时`
})
</script>

<template>
  <div v-if="progress" class="space-y-4">
    <!-- 进度条 -->
    <div class="space-y-2">
      <div class="flex items-center justify-between text-sm">
        <span class="font-medium">{{ stageText }}</span>
        <span class="text-muted-foreground">{{ progress.progress }}%</span>
      </div>
      <div class="h-2 w-full overflow-hidden rounded-full bg-secondary">
        <div
          class="h-full transition-all duration-300"
          :class="{
            'bg-primary': progress.stage !== 'error' && progress.stage !== 'completed',
            'bg-green-500': progress.stage === 'completed',
            'bg-destructive': progress.stage === 'error',
          }"
          :style="{ width: `${progress.progress}%` }"
        />
      </div>
    </div>

    <!-- 消息 -->
    <p class="text-sm text-muted-foreground">
      {{ progress.message }}
    </p>

    <!-- 详细信息 -->
    <div v-if="showDetails" class="grid grid-cols-2 gap-4 text-sm">
      <!-- 总数 -->
      <div v-if="progress.total !== undefined" class="space-y-1">
        <span class="text-muted-foreground">总数</span>
        <div class="font-medium">
          {{ progress.total }}
        </div>
      </div>

      <!-- 当前进度 -->
      <div v-if="progress.current !== undefined" class="space-y-1">
        <span class="text-muted-foreground">当前</span>
        <div class="font-medium">
          {{ progress.current }}
        </div>
      </div>

      <!-- 成功数 -->
      <div v-if="progress.success_count !== undefined" class="space-y-1">
        <span class="text-muted-foreground">成功</span>
        <div class="font-medium text-green-600">
          {{ progress.success_count }}
        </div>
      </div>

      <!-- 失败数 -->
      <div v-if="progress.failed_count !== undefined" class="space-y-1">
        <span class="text-muted-foreground">失败</span>
        <div class="font-medium text-red-600">
          {{ progress.failed_count }}
        </div>
      </div>

      <!-- 预计剩余时间 -->
      <div v-if="remainingTimeText" class="space-y-1">
        <span class="text-muted-foreground">预计剩余</span>
        <div class="font-medium">
          {{ remainingTimeText }}
        </div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="progress.stage === 'error' && progress.error" class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
      {{ progress.error }}
    </div>
  </div>
  <div v-else class="text-sm text-muted-foreground">
    等待开始...
  </div>
</template>
