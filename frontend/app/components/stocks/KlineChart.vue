<script setup lang="ts">
import type { HistoricalData, IndicatorData } from '~/api/types'
import * as echarts from 'echarts'

interface Props {
  data: HistoricalData[]
  indicators?: IndicatorData[]
  period?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
})

const chartRef = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

// 转换数据为 ECharts 格式
const klineData = computed(() => {
  return props.data.map(item => [
    item.open,
    item.close,
    item.low,
    item.high,
  ])
})

const dates = computed(() => {
  return props.data.map(item => item.date)
})

// 初始化图表
onMounted(() => {
  if (import.meta.client && chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  }
})

// 更新图表
watch([() => props.data, () => props.indicators], () => {
  updateChart()
}, { deep: true })

// 响应式调整
onMounted(() => {
  if (import.meta.client) {
    window.addEventListener('resize', handleResize)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

function updateChart() {
  if (!chartInstance || !props.data.length)
    return

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['K线', ...(props.indicators ? ['指标'] : [])],
    },
    grid: {
      left: '3%',
      right: '2%',
      bottom: '15%',
    },
    xAxis: [
      {
        type: 'category' as const,
        data: dates.value,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
      },
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true,
        },
      },
    ],
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100,
      },
      {
        show: true,
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100,
      },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData.value,
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a',
        },
      },
      // 如果有指标数据，添加指标线
      ...(props.indicators
        ? [{
            name: '指标',
            type: 'line' as const,
            data: props.indicators.map(item => item.value),
            smooth: true,
            lineStyle: {
              width: 2,
            },
          }]
        : []),
    ] as echarts.SeriesOption[],
  }

  chartInstance.setOption(option, true)
}
</script>

<template>
  <div ref="chartRef" :style="{ height, width: '100%' }" />
</template>
