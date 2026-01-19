<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

interface Props {
  modelValue: string
  options: Array<{ label: string; value: string }>
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const period = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

// 周期值到简洁标识的映射
const periodShortLabels: Record<string, string> = {
  tick: '分',
  '1d': '日',
  '1m': '1',
  '5m': '5',
  '15m': '15',
  '30m': '30',
  '60m': 'H',
  '1w': '周',
  '1M': '月',
}

// 获取周期对应的简洁标识
function getPeriodShortLabel(value: string): string {
  return periodShortLabels[value] || value
}
</script>

<template>
  <div class="flex items-center gap-1">
    <Tooltip
      v-for="option in options"
      :key="option.value"
      :delay-duration="200"
    >
      <TooltipTrigger as-child>
        <button
          type="button"
          :class="cn(
            'flex h-8 w-8 items-center justify-center rounded-md text-xs font-medium transition-all',
            'hover:bg-accent hover:text-accent-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
            period === option.value
              ? 'bg-primary text-primary-foreground shadow-sm'
              : 'bg-muted text-muted-foreground',
          )"
          :aria-label="option.label"
          :aria-pressed="period === option.value"
          @click="period = option.value"
        >
          {{ getPeriodShortLabel(option.value) }}
        </button>
      </TooltipTrigger>
      <TooltipContent>
        {{ option.label }}
      </TooltipContent>
    </Tooltip>
  </div>
</template>

