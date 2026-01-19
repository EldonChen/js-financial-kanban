/**
 * Historical Data 服务 API 封装
 * 通过 BFF 层调用历史数据服务
 */

import type {
  HistoricalData,
  HistoricalDataQueryParams,
  HistoricalDataStatistics,
  PaginatedResponse,
  SSEProgress,
} from '../types'
import { BffAdapter } from '../adapters/bff'
import { MockBffAdapter } from '../adapters/mock-bff'
import { ApiClient } from '../client'

export class HistoricalDataService {
  private client: ApiClient
  private basePath = '/v1/views/historical-data'
  private useMock: boolean

  constructor(bffApiUrl: string, useMock: boolean = true) {
    // 数据支持模块的接口暂时使用 Mock，直到 BFF 层实现完成
    // useMock 默认为 true，表示默认使用 Mock
    const adapter = useMock
      ? new MockBffAdapter(bffApiUrl || 'http://localhost:4000')
      : new BffAdapter(bffApiUrl)
    this.client = new ApiClient(adapter)
    this.useMock = useMock
  }

  /**
   * 获取历史K线数据
   */
  async getKlineData(
    ticker: string,
    params?: {
      period?: string
      start_date?: string
      end_date?: string
      limit?: number
    },
  ): Promise<HistoricalData[]> {
    const queryParams = new URLSearchParams()
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

    const response = await this.client.get<{ data: HistoricalData[], ticker?: string, period?: string, count?: number }>(url)
    // 兼容不同的响应格式
    if (Array.isArray(response.data)) {
      return response.data
    }
    return response.data?.data || []
  }

  /**
   * 获取历史K线数据（分页）
   */
  async getKlineDataPaginated(
    ticker: string,
    params?: HistoricalDataQueryParams,
  ): Promise<PaginatedResponse<HistoricalData>> {
    const queryParams = new URLSearchParams()
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

    const response = await this.client.get<PaginatedResponse<HistoricalData>>(url)
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
   * 更新历史K线数据
   */
  async updateKlineData(
    ticker: string,
    params?: {
      period?: string
      incremental?: boolean
      data_source?: string
    },
  ): Promise<{ updated_count: number, new_count: number }> {
    const queryParams = new URLSearchParams()
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.incremental !== undefined)
      queryParams.append('incremental', params.incremental.toString())
    if (params?.data_source)
      queryParams.append('data_source', params.data_source)

    const queryString = queryParams.toString()
    const url = queryString
      ? `${this.basePath}/${ticker}/update?${queryString}`
      : `${this.basePath}/${ticker}/update`

    const response = await this.client.post<{
      data: { updated_count: number, new_count: number }
    }>(url)
    return response.data?.data || { updated_count: 0, new_count: 0 }
  }

  /**
   * 批量更新历史K线数据（SSE）
   */
  async batchUpdateKlineData(
    tickers: string[],
    params?: {
      period?: string
      start_date?: string
      end_date?: string
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
      }, 3000)
    }

    // 使用 EventSource 接收 SSE 进度更新
    const queryParams = new URLSearchParams()
    queryParams.append('tickers', tickers.join(','))
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.start_date)
      queryParams.append('start_date', params.start_date)
    if (params?.end_date)
      queryParams.append('end_date', params.end_date)

    // 构建 SSE URL（需要从 BFF 获取 baseUrl）
    const config = useRuntimeConfig()
    const bffApiUrl = config.public.bffApiUrl || 'http://localhost:4000'
    const url = `${bffApiUrl}/api/bff${this.basePath}/batch?${queryParams.toString()}`

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
              reject(new Error(progress.error || '批量更新失败'))
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
        reject(new Error('批量更新失败'))
      }
    })
  }

  /**
   * 全量更新历史K线数据（SSE）
   */
  async fullUpdateKlineData(
    params?: {
      period?: string
      start_date?: string
      end_date?: string
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
      }, 5000)
    }

    const queryParams = new URLSearchParams()
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.start_date)
      queryParams.append('start_date', params.start_date)
    if (params?.end_date)
      queryParams.append('end_date', params.end_date)

    const config = useRuntimeConfig()
    const bffApiUrl = config.public.bffApiUrl || 'http://localhost:4000'
    const url = `${bffApiUrl}/api/bff${this.basePath}/full-update?${queryParams.toString()}`

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
              reject(new Error(progress.error || '全量更新失败'))
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
        reject(new Error('全量更新失败'))
      }
    })
  }

  /**
   * 删除历史K线数据
   */
  async deleteKlineData(
    ticker: string,
    params?: {
      period?: string
      start_date?: string
      end_date?: string
    },
  ): Promise<void> {
    const queryParams = new URLSearchParams()
    if (params?.period)
      queryParams.append('period', params.period)
    if (params?.start_date)
      queryParams.append('start_date', params.start_date)
    if (params?.end_date)
      queryParams.append('end_date', params.end_date)

    const queryString = queryParams.toString()
    const url = queryString
      ? `${this.basePath}/${ticker}?${queryString}`
      : `${this.basePath}/${ticker}`

    await this.client.delete(url)
  }

  /**
   * 获取历史K线数据统计
   */
  async getKlineDataStatistics(
    ticker?: string,
    period?: string,
  ): Promise<HistoricalDataStatistics> {
    const queryParams = new URLSearchParams()
    if (period)
      queryParams.append('period', period)

    const queryString = queryParams.toString()
    const url = ticker
      ? queryString
        ? `${this.basePath}/${ticker}/statistics?${queryString}`
        : `${this.basePath}/${ticker}/statistics`
      : queryString
        ? `${this.basePath}/statistics?${queryString}`
        : `${this.basePath}/statistics`

    const response = await this.client.get<{ data: HistoricalDataStatistics }>(url)
    return response.data?.data || {
      total_count: 0,
      start_date: '',
      end_date: '',
      missing_dates: [],
      coverage_rate: 0,
    }
  }
}

/**
 * 创建 Historical Data 服务实例
 */
export function createHistoricalDataService(bffApiUrl: string, useMock?: boolean): HistoricalDataService {
  return new HistoricalDataService(bffApiUrl, useMock)
}
