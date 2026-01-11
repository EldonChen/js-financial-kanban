/**
 * Dashboard 服务 API 封装
 * 通过 BFF 层调用 Dashboard 视图接口
 */

import { BffAdapter } from '../adapters/bff'
import { ApiClient } from '../client'
import type { DashboardData } from '../types'

export class DashboardService {
  private client: ApiClient
  private basePath = '/v1/views/dashboard'

  constructor(bffApiUrl: string) {
    const adapter = new BffAdapter(bffApiUrl)
    this.client = new ApiClient(adapter)
  }

  /**
   * 获取 Dashboard 数据
   */
  async getDashboardData(): Promise<DashboardData> {
    const response = await this.client.get<DashboardData>(this.basePath)
    return response.data || {
      stats: {
        totalItems: 0,
        pythonItems: 0,
        nodeItems: 0,
        rustItems: 0,
        totalStocks: 0,
      },
      recentItems: [],
      recentStocks: [],
    }
  }
}

/**
 * 创建 Dashboard 服务实例
 */
export function createDashboardService(bffApiUrl: string): DashboardService {
  return new DashboardService(bffApiUrl)
}
