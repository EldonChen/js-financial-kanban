/**
 * Historical Data Composables
 * 提供历史数据服务的便捷访问
 */

import type { HistoricalDataService } from '~/api/services/historical-data'
import { createHistoricalDataService } from '~/api/services/historical-data'

/**
 * 使用 Historical Data 服务
 * 注意：数据支持模块的接口暂时使用 Mock，直到 BFF 层实现完成
 */
export function useHistoricalDataService(): HistoricalDataService {
  const config = useRuntimeConfig()
  // 数据支持模块暂时使用 Mock（默认 true），直到 BFF 层实现完成
  // 可以通过环境变量 NUXT_PUBLIC_USE_DATA_SUPPORT_MOCK=false 来禁用 Mock
  const useMock = process.env.NUXT_PUBLIC_USE_DATA_SUPPORT_MOCK !== 'false'
  return createHistoricalDataService(config.public.bffApiUrl || 'http://localhost:4000', useMock)
}
