/**
 * Mock BFF Adapter
 * 用于前端开发和测试，返回 Mock 数据
 */

import type { ApiResponse, RequestConfig } from '../types'
import type { ApiAdapter } from './index'
import {
  generateMockHistoricalData,
  generateMockHistoricalStatistics,
  generateMockIndicatorData,
  mockSupportedIndicators,
} from '../mock/data-support'
import { ApiError } from '../types'

export class MockBffAdapter implements ApiAdapter {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '')
  }

  /**
   * 模拟延迟
   */
  private async delay(ms: number = 300): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * 解析 URL 路径
   */
  private parsePath(url: string): { path: string, params: URLSearchParams } {
    const fullUrl = url.startsWith('http') ? url : `${this.baseUrl}${url}`
    const urlObj = new URL(fullUrl)
    return {
      path: urlObj.pathname,
      params: urlObj.searchParams,
    }
  }

  /**
   * 处理分页响应
   */
  private createPaginatedResponse<T>(
    items: T[],
    page: number = 1,
    pageSize: number = 20,
  ): ApiResponse<{ items: T[], total: number, page: number, page_size: number, total_pages: number }> {
    const total = items.length
    const start = (page - 1) * pageSize
    const end = start + pageSize
    const paginatedItems = items.slice(start, end)
    const totalPages = Math.ceil(total / pageSize)

    return {
      code: 200,
      message: 'success',
      data: {
        items: paginatedItems,
        total,
        page,
        page_size: pageSize,
        total_pages: totalPages,
      },
    }
  }

  async get<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    await this.delay(300)

    const { path, params } = this.parsePath(url)

    // Mock 适配器只处理数据支持模块的接口
    // 如果遇到其他接口，应该使用真实的 BFF 适配器
    if (!path.includes('/historical-data') && !path.includes('/indicators')) {
      throw new ApiError(
        500,
        `Mock 适配器不支持此接口: ${path}。请使用真实的 BFF 适配器。`,
        { path },
      )
    }

    // 历史数据相关接口
    if (path.includes('/v1/views/historical-data')) {
      // 提取 ticker（从路径中，格式：/v1/views/historical-data/{ticker} 或 /v1/views/historical-data/{ticker}/statistics）
      const pathParts = path.split('/').filter(p => p)
      const tickerIndex = pathParts.indexOf('historical-data')
      const ticker = (tickerIndex >= 0 && tickerIndex < pathParts.length - 1 ? pathParts[tickerIndex + 1] : 'AAPL') as string
      const period = params.get('period') || '1d'
      const startDate: string | undefined = params.get('start_date') ?? undefined
      const endDate: string | undefined = params.get('end_date') ?? undefined
      const page = params.get('page') ? Number.parseInt(params.get('page')!) : 1
      const pageSize = params.get('page_size') ? Number.parseInt(params.get('page_size')!) : 20
      const limit = params.get('limit') ? Number.parseInt(params.get('limit')!) : undefined

      // 统计数据接口
      if (path.includes('/statistics')) {
        return {
          code: 200,
          message: 'success',
          data: generateMockHistoricalStatistics(ticker, period) as T,
        }
      }

      // 获取历史数据接口
      const allData = generateMockHistoricalData(ticker, period, startDate ?? undefined, endDate ?? undefined, limit ? limit * 2 : 200)

      // 如果有分页参数，返回分页格式
      if (params.has('page') || params.has('page_size')) {
        return this.createPaginatedResponse(allData, page, pageSize) as ApiResponse<T>
      }

      // 否则返回完整数据（但限制数量）
      const limitedData = allData.slice(0, limit || 100)
      return {
        code: 200,
        message: 'success',
        data: {
          ticker,
          period,
          count: limitedData.length,
          data: limitedData,
        } as T,
      }
    }

    // 技术指标相关接口
    if (path.includes('/v1/views/indicators')) {
      // 支持的指标列表
      if (path.includes('/supported')) {
        return {
          code: 200,
          message: 'success',
          data: { data: mockSupportedIndicators } as T,
        }
      }

      // 提取 ticker（从路径中，格式：/v1/views/indicators/{ticker}）
      const pathParts = path.split('/').filter(p => p)
      const indicatorsIndex = pathParts.indexOf('indicators')
      const ticker = (indicatorsIndex >= 0 && indicatorsIndex < pathParts.length - 1 ? pathParts[indicatorsIndex + 1] : 'AAPL') as string
      const indicatorName = params.get('indicator_name') || 'MA'
      const period = params.get('period') || '1d'
      const startDate = params.get('start_date') ?? undefined
      const endDate = params.get('end_date') ?? undefined
      const page = params.get('page') ? Number.parseInt(params.get('page')!) : 1
      const pageSize = params.get('page_size') ? Number.parseInt(params.get('page_size')!) : 20

      // 获取指标数据
      const allData = generateMockIndicatorData(ticker, indicatorName, period, startDate, endDate)

      // 如果有分页参数，返回分页格式
      if (params.has('page') || params.has('page_size')) {
        return this.createPaginatedResponse(allData, page, pageSize) as ApiResponse<T>
      }

      // 否则返回完整数据
      return {
        code: 200,
        message: 'success',
        data: {
          ticker,
          indicator_name: indicatorName,
          count: allData.length,
          data: allData,
        } as T,
      }
    }

    // 默认返回空数据
    return {
      code: 200,
      message: 'success',
      data: {} as T,
    }
  }

  async post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    await this.delay(500)

    const { path, params } = this.parsePath(url)

    // Mock 适配器只处理数据支持模块的接口
    if (!path.includes('/historical-data') && !path.includes('/indicators')) {
      throw new ApiError(
        500,
        `Mock 适配器不支持此接口: ${path}。请使用真实的 BFF 适配器。`,
        { path },
      )
    }

    // 历史数据更新接口
    if (path.includes('/v1/views/historical-data') && path.includes('/update')) {
      const pathParts = path.split('/').filter(p => p)
      const tickerIndex = pathParts.indexOf('historical-data')
      const ticker = (tickerIndex >= 0 && tickerIndex < pathParts.length - 1 ? pathParts[tickerIndex + 1] : 'AAPL') as string
      return {
        code: 200,
        message: 'success',
        data: {
          data: {
            ticker,
            period: params.get('period') || '1d',
            updated_count: Math.floor(Math.random() * 50) + 10,
            new_count: Math.floor(Math.random() * 20) + 5,
          },
        } as T,
      }
    }

    // 技术指标计算接口
    if (path.includes('/v1/views/indicators') && path.includes('/calculate')) {
      const pathParts = path.split('/').filter(p => p)
      const indicatorsIndex = pathParts.indexOf('indicators')
      const ticker = (indicatorsIndex >= 0 && indicatorsIndex < pathParts.length - 1 ? pathParts[indicatorsIndex + 1] : 'AAPL') as string
      const indicatorName = params.get('indicator_name') || 'MA'
      const period = params.get('period') || '1d'
      const startDate: string | undefined = params.get('start_date') ?? undefined
      const endDate: string | undefined = params.get('end_date') ?? undefined

      const indicatorData = generateMockIndicatorData(ticker, indicatorName, period, startDate, endDate)
      return {
        code: 200,
        message: 'success',
        data: { data: indicatorData } as T,
      }
    }

    return {
      code: 200,
      message: 'success',
      data: {} as T,
    }
  }

  async put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    await this.delay(500)

    const { path } = this.parsePath(url)

    // Mock 适配器只处理数据支持模块的接口
    if (!path.includes('/historical-data') && !path.includes('/indicators')) {
      throw new ApiError(
        500,
        `Mock 适配器不支持此接口: ${path}。请使用真实的 BFF 适配器。`,
        { path },
      )
    }

    return {
      code: 200,
      message: 'success',
      data: {} as T,
    }
  }

  async delete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    await this.delay(500)

    const { path } = this.parsePath(url)

    // Mock 适配器只处理数据支持模块的接口
    if (!path.includes('/historical-data') && !path.includes('/indicators')) {
      throw new ApiError(
        500,
        `Mock 适配器不支持此接口: ${path}。请使用真实的 BFF 适配器。`,
        { path },
      )
    }

    return {
      code: 200,
      message: 'success',
      data: {} as T,
    }
  }
}
