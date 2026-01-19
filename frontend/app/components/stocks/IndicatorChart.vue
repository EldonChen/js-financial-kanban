<script setup lang="ts">
import type { HistoricalData, IndicatorData } from '~/api/types'
import * as echarts from 'echarts'

interface Props {
  klineData: HistoricalData[]
  indicatorData?: IndicatorData[]
  indicatorName?: string
  indicatorDataMap?: Record<string, IndicatorData[]>
  selectedIndicators?: string[]
  period?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '600px',
  indicatorData: () => [],
  indicatorDataMap: () => ({}),
  selectedIndicators: () => [],
})

// 根据附图数量动态计算高度
const chartHeight = computed(() => {
  if (!props.indicatorDataMap || !props.selectedIndicators)
    return props.height

  const validIndicators = props.selectedIndicators ?? []
  const indicatorMap = props.indicatorDataMap ?? {}
  const subChartCount = validIndicators.filter((name) => {
    const data = indicatorMap[name]
    return data && data.length > 0 && !isMainChartIndicator(name)
  }).length

  if (subChartCount === 0)
    return '500px'
  // 每个附图增加 150px 高度
  return `${500 + subChartCount * 150}px`
})

const chartRef = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

// 转换数据为 ECharts 格式
const klineData = computed(() => {
  return props.klineData.map(item => [
    item.open,
    item.close,
    item.low,
    item.high,
  ])
})

const dates = computed(() => {
  return props.klineData.map(item => item.date)
})

// 判断指标是否为主图指标（显示在K线图上）
function isMainChartIndicator(indicatorName: string): boolean {
  const upperName = indicatorName.toUpperCase()
  const mainChartIndicators = ['MA', 'EMA', 'SMA', 'BOLL', 'BB', 'SAR', 'BBI']
  return mainChartIndicators.some(main => upperName.includes(main))
}

// 初始化图表
onMounted(() => {
  if (import.meta.client && chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  }
})

// 更新图表
watch(
  [
    () => props.klineData,
    () => props.indicatorData,
    () => props.indicatorName,
    () => props.indicatorDataMap,
    () => props.selectedIndicators,
  ],
  () => {
    updateChart()
  },
  { deep: true },
)

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

// 指标颜色列表
const indicatorColors = [
  '#5470c6',
  '#91cc75',
  '#fac858',
  '#ee6666',
  '#73c0de',
  '#3ba272',
  '#fc8452',
  '#9a60b4',
  '#ea7ccc',
]

function updateChart() {
  if (!chartInstance) {
    return
  }
  if (!props.klineData.length) {
    console.warn('[IndicatorChart] No kline data available')
    return
  }

  // 确定要显示的指标数据
  let indicatorsToShow: Array<{ name: string, data: IndicatorData[] }> = []

  console.log('[IndicatorChart] updateChart called', {
    selectedIndicators: props.selectedIndicators,
    indicatorDataMapKeys: Object.keys(props.indicatorDataMap || {}),
    indicatorDataMap: props.indicatorDataMap,
  })

  // 优先使用 indicatorDataMap 和 selectedIndicators（多指标模式）
  if (
    props.indicatorDataMap
    && Object.keys(props.indicatorDataMap).length > 0
    && props.selectedIndicators
    && props.selectedIndicators.length > 0
  ) {
    indicatorsToShow = props.selectedIndicators
      .filter(name => {
        const data = props.indicatorDataMap![name]
        const hasData = data && Array.isArray(data) && data.length > 0
        if (!hasData) {
          console.warn(`[IndicatorChart] Indicator ${name} has no data:`, data)
        }
        return hasData
      })
      .map(name => ({
        name,
        data: props.indicatorDataMap![name]!,
      }))
    
    console.log('[IndicatorChart] Indicators to show:', indicatorsToShow.map(ind => ({ 
      name: ind.name, 
      count: ind.data.length,
      firstItem: ind.data[0]
    })))
  }
  // 兼容单指标模式
  else if (props.indicatorData && props.indicatorData.length > 0 && props.indicatorName) {
    indicatorsToShow = [{ name: props.indicatorName, data: props.indicatorData }]
  }

  // 分类指标：主图指标和附图指标
  const mainChartIndicators = indicatorsToShow.filter(ind => isMainChartIndicator(ind.name))
  const subChartIndicators = indicatorsToShow.filter(ind => !isMainChartIndicator(ind.name))

  const hasMainIndicators = mainChartIndicators.length > 0
  const hasSubIndicators = subChartIndicators.length > 0
  const hasIndicators = hasMainIndicators || hasSubIndicators

  // 构建图例数据
  const legendData = ['K线', ...mainChartIndicators.map(ind => ind.name), ...subChartIndicators.map(ind => ind.name)]

  // 计算 grid 布局
  const gridCount = 1 + (hasSubIndicators ? subChartIndicators.length : 0) // 主图 + 附图数量

  const grids: any[] = []

  if (hasSubIndicators) {
    // 有附图时：主图占 50%，每个附图平均分配剩余空间
    const mainChartHeight = '50%'
    const subChartHeightPercent = 50 / subChartIndicators.length // 剩余 50% 平均分配

    grids.push({
      left: '3%',
      right: '2%',
      top: '10%',
      height: mainChartHeight,
    })

    // 为每个附图指标创建 grid
    let currentTop = 60 // 主图结束位置（10% + 50%）
    subChartIndicators.forEach(() => {
      grids.push({
        left: '3%',
        right: '2%',
        top: `${currentTop}%`,
        height: `${subChartHeightPercent}%`,
      })
      currentTop += subChartHeightPercent
    })
  }
  else {
    // 无附图时：主图占 80%
    grids.push({
      left: '3%',
      right: '2%',
      top: '10%',
      height: '80%',
    })
  }

  // 构建 xAxis（所有共享相同的数据）
  const xAxes: any[] = []
  for (let i = 0; i < gridCount; i++) {
    xAxes.push({
      type: 'category',
      data: dates.value,
      scale: true,
      // 使用 boundaryGap 数组来添加安全距离：左右各留出 5% 的空间
      // [leftGap, rightGap] 表示左右两侧的留白比例
      boundaryGap: [0.05, 0.05],
      axisLine: { onZero: false },
      splitLine: { show: false },
      gridIndex: i,
      axisLabel: {
        show: i === gridCount - 1, // 只在最后一个 xAxis 显示标签
      },
    })
  }

  // 构建 yAxis
  const yAxes: any[] = [
    {
      scale: true,
      splitArea: {
        show: true,
      },
      gridIndex: 0,
    },
  ]

  // 为每个附图添加 yAxis
  for (let i = 1; i < gridCount; i++) {
    yAxes.push({
      scale: true,
      gridIndex: i,
    })
  }

  // 构建 series
  const series: any[] = [
    {
      name: 'K线',
      type: 'candlestick',
      data: klineData.value,
      xAxisIndex: 0,
      yAxisIndex: 0,
      itemStyle: {
        color: '#ef5350',
        color0: '#26a69a',
        borderColor: '#ef5350',
        borderColor0: '#26a69a',
      },
    },
  ]

  // 添加主图指标（显示在 K 线图上）
  mainChartIndicators.forEach((indicator, index) => {
    // 创建日期映射表以提高查找效率
    const indicatorDateMap = new Map<string, number>()
    indicator.data.forEach(item => {
      indicatorDateMap.set(item.date, item.value)
    })
    
    const indicatorValues = dates.value.map((date) => {
      const value = indicatorDateMap.get(date)
      if (value === undefined) {
        // 尝试模糊匹配（去除时间部分）
        const dateParts = date.split(' ')
        const dateOnly = dateParts[0] ?? date
        const matchedItem = indicator.data.find(item => item.date.startsWith(dateOnly))
        if (matchedItem) {
          return matchedItem.value
        }
      }
      return value !== undefined ? value : null
    })
    
    console.log(`[IndicatorChart] Main indicator ${indicator.name}:`, {
      klineDates: dates.value.slice(0, 5),
      indicatorDates: indicator.data.slice(0, 5).map(item => item.date),
      values: indicatorValues.filter(v => v !== null).length,
      total: indicatorValues.length
    })

    series.push({
      name: indicator.name,
      type: 'line',
      data: indicatorValues,
      xAxisIndex: 0,
      yAxisIndex: 0,
      smooth: true,
      lineStyle: {
        width: 2,
        color: indicatorColors[index % indicatorColors.length],
      },
      itemStyle: {
        color: indicatorColors[index % indicatorColors.length],
      },
    })
  })

  // 添加附图指标（每个指标一个 grid）
  subChartIndicators.forEach((indicator, index) => {
    // 创建日期映射表以提高查找效率
    const indicatorDateMap = new Map<string, number>()
    indicator.data.forEach(item => {
      indicatorDateMap.set(item.date, item.value)
    })
    
    const indicatorValues = dates.value.map((date) => {
      const value = indicatorDateMap.get(date)
      if (value === undefined) {
        // 尝试模糊匹配（去除时间部分）
        const dateParts = date.split(' ')
        const dateOnly = dateParts[0] ?? date
        const matchedItem = indicator.data.find(item => item.date.startsWith(dateOnly))
        if (matchedItem) {
          return matchedItem.value
        }
      }
      return value !== undefined ? value : null
    })
    
    console.log(`[IndicatorChart] Sub indicator ${indicator.name}:`, {
      klineDates: dates.value.slice(0, 5),
      indicatorDates: indicator.data.slice(0, 5).map(item => item.date),
      values: indicatorValues.filter(v => v !== null).length,
      total: indicatorValues.length
    })

    const gridIndex = index + 1 // 从 1 开始（0 是主图）

    series.push({
      name: indicator.name,
      type: 'line',
      data: indicatorValues,
      xAxisIndex: gridIndex,
      yAxisIndex: gridIndex,
      smooth: true,
      lineStyle: {
        width: 2,
        color: indicatorColors[(mainChartIndicators.length + index) % indicatorColors.length],
      },
      itemStyle: {
        color: indicatorColors[(mainChartIndicators.length + index) % indicatorColors.length],
      },
    })
  })

  // 构建 dataZoom（所有 xAxis 同步）
  const xAxisIndices = Array.from({ length: gridCount }, (_, i) => i)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: legendData,
      top: 0,
    },
    grid: grids,
    xAxis: xAxes,
    yAxis: yAxes,
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: xAxisIndices,
        start: 50,
        end: 100,
      },
      {
        show: true,
        xAxisIndex: xAxisIndices,
        type: 'slider',
        bottom: '2%',
        start: 50,
        end: 100,
      },
    ],
    series,
  }

  chartInstance.setOption(option, true)
}
</script>

<template>
  <div ref="chartRef" :style="{ height: chartHeight, width: '100%' }" />
</template>
