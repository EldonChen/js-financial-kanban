/**
 * Indicators Composables
 * 提供技术指标服务的便捷访问
 */

import type { IndicatorsService } from '~/api/services/indicators'
import { createIndicatorsService } from '~/api/services/indicators'

/**
 * 使用 Indicators 服务
 * 注意：数据支持模块的接口暂时使用 Mock，直到 BFF 层实现完成
 */
export function useIndicatorsService(): IndicatorsService {
  const config = useRuntimeConfig()
  const useMock = process.env.NUXT_PUBLIC_USE_DATA_SUPPORT_MOCK !== 'false'
  return createIndicatorsService(config.public.bffApiUrl || 'http://localhost:4000', useMock)
}
