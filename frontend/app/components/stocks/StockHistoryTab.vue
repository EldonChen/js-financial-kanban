<script setup lang="ts">
import SSEProgressComponent from '~/components/common/SSEProgress.vue'
import { useStockHistory } from '~/composables/useStockHistory'
import IndicatorChart from './IndicatorChart.vue'
import IndicatorSelector from './IndicatorSelector.vue'
import PeriodSelector from './PeriodSelector.vue'

interface Props {
  ticker: string
}

const props = defineProps<Props>()

// 使用股票历史 composable
const tickerRef = computed(() => props.ticker)
const {
  historicalData,
  historicalLoading,
  historicalQueryParams,
  historicalSSEProgress,
  isUpdatingHistorical,
  periodOptions,
  selectedIndicators,
  indicatorDataMap,
  supportedIndicators,
  isCalculating,
  indicatorSSEProgress,
  loadHistoricalData,
  updateHistoricalData,
  handlePeriodChange,
  loadSupportedIndicators,
  toggleIndicator,
} = useStockHistory(tickerRef)

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadSupportedIndicators(),
    loadHistoricalData(),
  ])
})

// 暴露方法供外部调用（如果需要）
defineExpose({
  loadHistoricalData,
})
</script>

<template>
  <div class="space-y-4">
    <!-- K线图 -->
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle>K线图</CardTitle>
          <Button
            variant="outline"
            :disabled="isUpdatingHistorical"
            @click="updateHistoricalData"
          >
            <Icon
              :name="
                isUpdatingHistorical
                  ? 'lucide:loader-2'
                  : 'lucide:refresh-cw'
              "
              class="mr-2 h-4 w-4"
              :class="[isUpdatingHistorical && 'animate-spin']"
            />
            更新数据
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <!-- 时间周期选择和技术指标选择 -->
        <div class="mb-4 flex items-center justify-between gap-4">
          <PeriodSelector
            :model-value="historicalQueryParams.period || '1d'"
            :options="periodOptions"
            @update:model-value="handlePeriodChange"
          />

          <IndicatorSelector
            :supported-indicators="supportedIndicators"
            :selected-indicators="selectedIndicators"
            @toggle="toggleIndicator"
          />
        </div>

        <div
          v-if="historicalLoading"
          class="flex items-center justify-center py-8"
        >
          <Icon name="lucide:loader-2" class="h-6 w-6 animate-spin" />
        </div>
        <div
          v-else-if="historicalData.length === 0"
          class="py-8 text-center text-muted-foreground"
        >
          暂无数据
        </div>
        <div v-else>
          <IndicatorChart
          :kline-data="historicalData"
          :indicator-data-map="indicatorDataMap"
          :selected-indicators="selectedIndicators"
          :period="historicalQueryParams.period || '1d'"
        />
        </div>
        <!-- SSE 进度显示 -->
        <div
          v-if="isUpdatingHistorical && historicalSSEProgress"
          class="mt-4"
        >
          <SSEProgressComponent :progress="historicalSSEProgress" />
        </div>
        <div
          v-if="isCalculating && indicatorSSEProgress"
          class="mt-4"
        >
          <SSEProgressComponent :progress="indicatorSSEProgress" />
        </div>
      </CardContent>
    </Card>
  </div>
</template>
