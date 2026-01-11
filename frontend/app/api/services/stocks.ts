/**
 * Stocks 服务 API 封装
 * 通过 BFF 层调用股票信息服务
 */

import { BffAdapter } from '../adapters/bff'
import { ApiClient } from '../client'
import type { Stock } from '../types'

export class StocksService {
  private client: ApiClient
  private basePath = '/v1/views/stocks'

  constructor(bffApiUrl: string) {
    const adapter = new BffAdapter(bffApiUrl)
    this.client = new ApiClient(adapter)
  }

  /**
   * 获取所有股票
   */
  async getStocks(): Promise<Stock[]> {
    const response = await this.client.get<Stock[]>(this.basePath)
    return response.data || []
  }

  /**
   * 获取单个股票
   * 如果股票不存在，返回 null
   */
  async getStock(ticker: string): Promise<Stock | null> {
    try {
      const response = await this.client.get<Stock>(`${this.basePath}/${ticker}`)
      // 如果 data 为 null，表示股票不存在
      return response.data || null
    }
    catch (error: any) {
      // 如果是 404 错误，返回 null 而不是抛出错误
      if (error.code === 404) {
        return null
      }
      // 其他错误继续抛出
      throw error
    }
  }

  /**
   * 更新股票（从数据源拉取最新数据）
   */
  async updateStock(ticker: string): Promise<Stock> {
    const response = await this.client.post<Stock>(`${this.basePath}/${ticker}/update`)
    return response.data
  }

  /**
   * 删除股票
   */
  async deleteStock(ticker: string): Promise<void> {
    await this.client.delete(`${this.basePath}/${ticker}`)
  }
}

/**
 * 创建 Stocks 服务实例
 */
export function createStocksService(bffApiUrl: string): StocksService {
  return new StocksService(bffApiUrl)
}
