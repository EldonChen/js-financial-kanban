/**
 * Stock Formatters Composable
 * 提供股票相关的格式化函数
 */

/**
 * 格式化数字
 */
export function formatNumber(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  return new Intl.NumberFormat('zh-CN', {
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * 格式化货币
 */
export function formatCurrency(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * 格式化市值
 */
export function formatMarketCap(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  if (value >= 1e12)
    return `$${(value / 1e12).toFixed(2)}T`
  if (value >= 1e9)
    return `$${(value / 1e9).toFixed(2)}B`
  if (value >= 1e6)
    return `$${(value / 1e6).toFixed(2)}M`
  return formatCurrency(value)
}

/**
 * 格式化日期
 */
export function formatDate(dateString?: string): string {
  if (!dateString)
    return '-'
  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }
  catch {
    return dateString
  }
}

/**
 * 获取市场类型的 Badge 样式
 */
export function getMarketTypeVariant(
  marketType?: string,
): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (!marketType)
    return 'outline'
  if (marketType.includes('A股'))
    return 'destructive' // 红色表示 A 股
  if (marketType.includes('港股'))
    return 'secondary' // 灰色表示港股
  if (marketType.includes('美股'))
    return 'default' // 默认样式表示美股
  return 'outline'
}

/**
 * 数据源链接映射
 */
const dataSourceLinks: Record<string, string> = {
  'akshare': 'https://github.com/akfamily/akshare',
  'yfinance': 'https://github.com/ranaroussi/yfinance',
  'easyquotation': 'https://github.com/shidenggui/easyquotation',
  'tushare': 'https://tushare.pro/',
  'iex-cloud': 'https://iexcloud.io/',
  'alpha-vantage': 'https://www.alphavantage.co/',
}

/**
 * 获取数据源链接
 */
export function getDataSourceUrl(dataSource?: string): string | null {
  if (!dataSource)
    return null
  // 处理可能的变体名称
  const normalized = dataSource.toLowerCase().replace(/_/g, '-')
  return (
    dataSourceLinks[normalized]
    || dataSourceLinks[dataSource.toLowerCase()]
    || null
  )
}

