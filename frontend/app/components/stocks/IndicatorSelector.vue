<script setup lang="ts">
import type { SupportedIndicator } from '~/api/types'
import { computed } from 'vue'
import { cn } from '@/lib/utils'

interface Props {
  supportedIndicators: SupportedIndicator[]
  selectedIndicators: string[]
  loading?: boolean
}

interface Emits {
  (e: 'toggle', indicatorName: string): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<Emits>()

const selectedValues = computed(() => new Set(props.selectedIndicators))

function toggleIndicator(indicatorName: string) {
  emit('toggle', indicatorName)
}

const displayText = computed(() => {
  if (props.selectedIndicators.length === 0) {
    return '选择技术指标'
  }
  if (props.selectedIndicators.length === 1) {
    const indicator = props.supportedIndicators.find(ind => ind.name === props.selectedIndicators[0])
    return indicator?.display_name || props.selectedIndicators[0]
  }
  return `已选择 ${props.selectedIndicators.length} 个指标`
})
</script>

<template>
  <div class="flex items-center">
    <div
      v-if="props.loading || props.supportedIndicators.length === 0"
      class="text-sm text-muted-foreground"
    >
      加载中...
    </div>
    <Popover v-else>
      <PopoverTrigger as-child>
        <Button variant="outline" class="justify-start whitespace-nowrap">
          <Icon name="lucide:bar-chart-2" class="mr-2 h-4 w-4" />
          {{ displayText }}
          <template v-if="props.selectedIndicators.length > 0">
            <Separator orientation="vertical" class="mx-2 h-4" />
            <Badge
              variant="secondary"
              class="rounded-sm px-1 font-normal"
            >
              {{ props.selectedIndicators.length }}
            </Badge>
          </template>
        </Button>
      </PopoverTrigger>
      <PopoverContent class="w-[300px] p-0" align="start">
        <Command>
          <CommandInput placeholder="搜索技术指标..." />
          <CommandList>
            <CommandEmpty>未找到技术指标</CommandEmpty>
            <CommandGroup>
              <CommandItem
                v-for="indicator in props.supportedIndicators"
                :key="indicator.name"
                :value="indicator.name"
                @select="() => toggleIndicator(indicator.name)"
              >
                <div
                  :class="cn(
                    'mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary',
                    selectedValues.has(indicator.name)
                      ? 'bg-primary text-primary-foreground'
                      : 'opacity-50 [&_svg]:invisible',
                  )"
                >
                  <Icon name="lucide:check" class="h-4 w-4" />
                </div>
                <span>{{ indicator.display_name }}</span>
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  </div>
</template>
