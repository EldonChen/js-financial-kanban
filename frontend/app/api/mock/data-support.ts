/**
 * 数据支持模块 Mock 数据
 * 用于前端开发和测试
 */

import type {
  HistoricalData,
  HistoricalDataStatistics,
  IndicatorData,
  SSEProgress,
  SupportedIndicator,
} from '../types'

// 生成日期范围
function generateDateRange(startDate: string, endDate: string, period: string = '1d'): string[] {
  const dates: string[] = []
  const start = new Date(startDate)
  const end = new Date(endDate)
  const step = period === '1m'
    ? 1
    : period === '5m'
      ? 5
      : period === '15m'
        ? 15
        : period === '30m' ? 30 : period === '60m' ? 60 : period === '1w' ? 7 : period === '1M' ? 30 : 1

  const current = new Date(start)
  while (current <= end) {
    const dateStr = current.toISOString().split('T')[0]
    if (dateStr) {
      dates.push(dateStr)
    }
    current.setDate(current.getDate() + step)
  }
  return dates
}

// 生成随机价格数据
function generatePrice(basePrice: number, volatility: number = 0.02): number {
  const change = (Math.random() - 0.5) * volatility * basePrice
  return Math.max(0.01, basePrice + change)
}

// 生成历史K线数据
export function generateMockHistoricalData(
  ticker: string,
  period: string = '1d',
  startDate: string | undefined = undefined,
  endDate: string | undefined = undefined,
  limit: number | undefined = undefined,
): HistoricalData[] {
  const defaultStart = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  const defaultEnd = new Date().toISOString().split('T')[0]
  const start = startDate ?? defaultStart!
  const end = endDate ?? defaultEnd!
  const dates = generateDateRange(start, end, period)

  const basePrice = 100 + Math.random() * 50
  let currentPrice = basePrice

  const data: HistoricalData[] = dates.slice(0, limit || dates.length).map((date, index) => {
    const open = currentPrice
    const close = generatePrice(open, 0.02)
    const high = Math.max(open, close) * (1 + Math.random() * 0.01)
    const low = Math.min(open, close) * (1 - Math.random() * 0.01)
    const volume = Math.floor(Math.random() * 10000000) + 1000000

    currentPrice = close

    return {
      date,
      timestamp: new Date(date).toISOString(),
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume,
      amount: volume * close,
      data_source: 'yfinance',
    }
  })

  return data
}

// 生成历史数据统计
export function generateMockHistoricalStatistics(
  ticker: string,
  period: string = '1d',
): HistoricalDataStatistics {
  const totalCount = Math.floor(Math.random() * 200) + 100
  const missingCount = Math.floor(Math.random() * 10)
  const defaultStart = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  const defaultEnd = new Date().toISOString().split('T')[0]
  const startDate = defaultStart!
  const endDate = defaultEnd!

  const missingDates: string[] = []
  for (let i = 0; i < missingCount; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + Math.floor(Math.random() * 365))
    const dateStr = date.toISOString().split('T')[0]
    if (dateStr) {
      missingDates.push(dateStr)
    }
  }

  return {
    total_count: totalCount,
    start_date: startDate,
    end_date: endDate,
    missing_dates: missingDates,
    coverage_rate: Math.round(((totalCount - missingCount) / totalCount) * 100),
  }
}

// 生成技术指标数据
export function generateMockIndicatorData(
  ticker: string,
  indicatorName: string,
  period: string = '1d',
  startDate: string | undefined = undefined,
  endDate: string | undefined = undefined,
): IndicatorData[] {
  const defaultStart = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  const defaultEnd = new Date().toISOString().split('T')[0]
  const start = startDate ?? defaultStart!
  const end = endDate ?? defaultEnd!
  const dates = generateDateRange(start, end, period)

  const baseValue = indicatorName.includes('MA') ? 100 : indicatorName.includes('RSI') ? 50 : indicatorName.includes('MACD') ? 0 : 100
  let currentValue = baseValue

  return dates.map((date) => {
    const change = (Math.random() - 0.5) * 2
    currentValue = Math.max(0, currentValue + change)

    return {
      date,
      timestamp: new Date(date).toISOString(),
      value: Number(currentValue.toFixed(4)),
      params: indicatorName.includes('MA') ? { period: 20 } : {},
    }
  })
}

// 支持的指标列表
export const mockSupportedIndicators: SupportedIndicator[] = [
  {
    name: 'MA',
    display_name: '移动平均线',
    description: 'Moving Average - 移动平均线指标',
    category: 'trend',
    params: [
      { name: 'period', type: 'number', default: 20, description: '周期' },
    ],
  },
  {
    name: 'RSI',
    display_name: '相对强弱指标',
    description: 'Relative Strength Index - 相对强弱指标',
    category: 'momentum',
    params: [
      { name: 'period', type: 'number', default: 14, description: '周期' },
    ],
  },
  {
    name: 'MACD',
    display_name: 'MACD',
    description: 'Moving Average Convergence Divergence - 指数平滑移动平均线',
    category: 'trend',
    params: [
      { name: 'fast', type: 'number', default: 12, description: '快线周期' },
      { name: 'slow', type: 'number', default: 26, description: '慢线周期' },
    ],
  },
  {
    name: 'BOLL',
    display_name: '布林带',
    description: 'Bollinger Bands - 布林带指标',
    category: 'volatility',
    params: [
      { name: 'period', type: 'number', default: 20, description: '周期' },
      { name: 'std', type: 'number', default: 2, description: '标准差倍数' },
    ],
  },
]

// SSE 进度模拟
export function simulateSSEProgress(
  onProgress: (progress: SSEProgress) => void,
  duration: number = 5000,
): Promise<void> {
  return new Promise((resolve) => {
    const startTime = Date.now()
    const total = 100
    let current = 0

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(100, Math.floor((elapsed / duration) * 100))
      current = Math.floor((progress / 100) * total)

      let stage: SSEProgress['stage'] = 'init'
      if (progress < 20)
        stage = 'init'
      else if (progress < 60)
        stage = 'fetching'
      else if (progress < 90)
        stage = 'saving'
      else if (progress >= 100)
        stage = 'completed'
      else
        stage = 'calculating'

      onProgress({
        stage,
        message: stage === 'init'
          ? '初始化...'
          : stage === 'fetching'
            ? `正在获取数据... (${current}/${total})`
            : stage === 'saving'
              ? `正在保存数据... (${current}/${total})`
              : stage === 'calculating'
                ? `正在计算... (${current}/${total})`
                : '完成',
        progress,
        total,
        current,
        success_count: Math.floor(current * 0.9),
        failed_count: Math.floor(current * 0.1),
        estimated_remaining_time: Math.max(0, Math.floor((duration - elapsed) / 1000)),
      })

      if (progress >= 100) {
        clearInterval(interval)
        resolve()
      }
    }, 200)
  })
}
