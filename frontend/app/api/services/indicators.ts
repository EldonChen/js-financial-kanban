/**
 * Indicators 服务 API 封装
 * 通过 BFF 层调用技术指标服务
 */

import type {
  IndicatorData,
  IndicatorQueryParams,
  PaginatedResponse,
  SSEProgress,
  SupportedIndicator,
} from '../types'
import { BffAdapter } from '../adapters/bff'
import { MockBffAdapter } from '../adapters/mock-bff'
import { ApiClient } from '../client'

export class IndicatorsService {
  private client: ApiClient
  private basePath = '/v1/views/indicators'
  private useMock: boolean

  constructor(bffApiUrl: string, useMock: boolean = true) {
    // 数据支持模块的接口暂时使用 Mock，直到 BFF 层实现完成
    const adapter = useMock
      ? new MockBffAdapter(bffApiUrl || 'http://localhost:4000')
      : new BffAdapter(bffApiUrl)
    this.client = new ApiClient(adapter)
    this.useMock = useMock
  }

  /**
   * 计算技术指标
   */
  async calculateIndicator(
    ticker: string,
    indicatorName: string,
    params?: {
      period?: string
      start_date?: string
      end_date?: string
      indicator_params?: Record<string, any>
    },
  ): Promise<IndicatorData[]> {
    const queryParams = new URLSearchParams()
    queryParams.append('indicator_name', indicatorName)
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.start_date)
      queryParams.append('start_date', params.start_date)
    if (params?.end_date)
      queryParams.append('end_date', params.end_date)

    const url = `${this.basePath}/${ticker}/calculate?${queryParams.toString()}`

    const body: any = {}
    if (params?.indicator_params) {
      body.indicator_params = params.indicator_params
    }

    const response = await this.client.post<{ data: IndicatorData[], ticker?: string, indicator_name?: string, count?: number }>(url, body)
    // 兼容不同的响应格式
    if (Array.isArray(response.data)) {
      return response.data
    }
    return response.data?.data || []
  }

  /**
   * 获取技术指标数据
   */
  async getIndicatorData(
    ticker: string,
    indicatorName: string,
    params?: {
      period?: string
      start_date?: string
      end_date?: string
      limit?: number
    },
  ): Promise<IndicatorData[]> {
    const queryParams = new URLSearchParams()
    queryParams.append('indicator_name', indicatorName)
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.start_date)
      queryParams.append('start_date', params.start_date)
    if (params?.end_date)
      queryParams.append('end_date', params.end_date)
    if (params?.limit)
      queryParams.append('limit', params.limit.toString())

    const queryString = queryParams.toString()
    const url = queryString
      ? `${this.basePath}/${ticker}?${queryString}`
      : `${this.basePath}/${ticker}`

    const response = await this.client.get<{ data: IndicatorData[], ticker?: string, indicator_name?: string, count?: number }>(url)
    // 兼容不同的响应格式
    if (Array.isArray(response.data)) {
      return response.data
    }
    return response.data?.data || []
  }

  /**
   * 获取技术指标数据（分页）
   */
  async getIndicatorDataPaginated(
    ticker: string,
    indicatorName: string,
    params?: IndicatorQueryParams,
  ): Promise<PaginatedResponse<IndicatorData>> {
    const queryParams = new URLSearchParams()
    queryParams.append('indicator_name', indicatorName)
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.start_date)
      queryParams.append('start_date', params.start_date)
    if (params?.end_date)
      queryParams.append('end_date', params.end_date)
    if (params?.page)
      queryParams.append('page', params.page.toString())
    if (params?.page_size)
      queryParams.append('page_size', params.page_size.toString())

    const queryString = queryParams.toString()
    const url = queryString
      ? `${this.basePath}/${ticker}?${queryString}`
      : `${this.basePath}/${ticker}`

    const response = await this.client.get<PaginatedResponse<IndicatorData>>(url)
    // 如果响应格式正确，直接返回
    if (response.data && 'items' in response.data) {
      return response.data
    }
    // 否则返回默认值
    return {
      items: [],
      total: 0,
      page: params?.page || 1,
      page_size: params?.page_size || 20,
      total_pages: 0,
    }
  }

  /**
   * 批量计算技术指标（SSE）
   */
  async batchCalculateIndicators(
    tickers: string[],
    indicatorNames: string[],
    params?: {
      period?: string
      start_date?: string
      end_date?: string
      indicator_params?: Record<string, any>
    },
    onProgress?: (progress: SSEProgress) => void,
  ): Promise<void> {
    // 如果使用 Mock，模拟 SSE 进度
    if (this.useMock) {
      const { simulateSSEProgress } = await import('../mock/data-support')
      return simulateSSEProgress((progress) => {
        if (onProgress) {
          onProgress(progress)
        }
      }, 4000)
    }

    const queryParams = new URLSearchParams()
    queryParams.append('tickers', tickers.join(','))
    queryParams.append('indicator_names', indicatorNames.join(','))
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.start_date)
      queryParams.append('start_date', params.start_date)
    if (params?.end_date)
      queryParams.append('end_date', params.end_date)

    const config = useRuntimeConfig()
    const bffApiUrl = config.public.bffApiUrl || 'http://localhost:4000'
    const url = `${bffApiUrl}/api/bff${this.basePath}/batch-calculate?${queryParams.toString()}`

    return new Promise((resolve, reject) => {
      const eventSource = new EventSource(url)

      eventSource.onmessage = (event) => {
        try {
          const progress = JSON.parse(event.data) as SSEProgress
          if (onProgress) {
            onProgress(progress)
          }
          if (progress.stage === 'completed' || progress.stage === 'error') {
            eventSource.close()
            if (progress.stage === 'error') {
              reject(new Error(progress.error || '批量计算失败'))
            }
            else {
              resolve()
            }
          }
        }
        catch (error) {
          console.error('SSE message parse error:', error)
        }
      }

      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
        eventSource.close()
        reject(new Error('批量计算失败'))
      }
    })
  }

  /**
   * 获取支持的指标列表
   */
  async getSupportedIndicators(): Promise<SupportedIndicator[]> {
    const response = await this.client.get<{ data: SupportedIndicator[] }>(
      `${this.basePath}/supported`,
    )
    // 兼容不同的响应格式
    if (Array.isArray(response.data)) {
      return response.data
    }
    return response.data?.data || []
  }
}

/**
 * 创建 Indicators 服务实例
 */
export function createIndicatorsService(bffApiUrl: string, useMock?: boolean): IndicatorsService {
  return new IndicatorsService(bffApiUrl, useMock)
}
