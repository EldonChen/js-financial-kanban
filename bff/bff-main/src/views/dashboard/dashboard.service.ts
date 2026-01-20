import { Injectable } from '@nestjs/common';
import { PythonClient } from '../../clients/python.client';
import { NodeClient } from '../../clients/node.client';
import { RustClient } from '../../clients/rust.client';
import { StockInfoClient } from '../../clients/stock-info.client';

export interface DashboardData {
  stats: {
    totalItems: number;
    pythonItems: number;
    nodeItems: number;
    rustItems: number;
    totalStocks: number;
    aStockCount: number;
    usStockCount: number;
    hkStockCount: number;
    providerCount: number;
    lastFullUpdateTime?: string;
  };
  recentItems: any[];
  recentStocks: any[];
}

@Injectable()
export class DashboardService {
  constructor(
    private readonly pythonClient: PythonClient,
    private readonly nodeClient: NodeClient,
    private readonly rustClient: RustClient,
    private readonly stockInfoClient: StockInfoClient,
  ) {}

  async getDashboardData(): Promise<DashboardData> {
    // 并行获取股票数据和数据源状态
    const [stocksResult, providerStatus] = await Promise.all([
      this.stockInfoClient
        .getStocks({ page: 1, pageSize: 100 })
        .catch(() => null),
      this.stockInfoClient.getProviderStatus().catch(() => null),
    ]);

    const stocksList = stocksResult?.items || [];
    const totalStocks = stocksResult?.total || 0;

    // 统计各市场类型的股票数量
    // 获取所有股票数据以进行统计（需要获取足够的数据）
    const [aStockResult, usStockResult, hkStockResult] = await Promise.all([
      this.stockInfoClient
        .getStocks({ marketType: 'A股', page: 1, pageSize: 1 })
        .catch(() => null),
      this.stockInfoClient
        .getStocks({ marketType: '美股', page: 1, pageSize: 1 })
        .catch(() => null),
      this.stockInfoClient
        .getStocks({ marketType: '港股', page: 1, pageSize: 1 })
        .catch(() => null),
    ]);

    const aStockCount = aStockResult?.total || 0;
    const usStockCount = usStockResult?.total || 0;
    const hkStockCount = hkStockResult?.total || 0;
    const providerCount = providerStatus?.total_providers || 0;

    // 获取最近的 stocks（按更新时间排序，取前 5 个）
    const recentStocks = stocksList
      .sort(
        (a, b) =>
          new Date(b.last_updated || 0).getTime() -
          new Date(a.last_updated || 0).getTime(),
      )
      .slice(0, 5);

    // 计算上次全量更新时间（取所有股票中最早的 created_at）
    // 全量更新时，所有股票会在同一时间创建，所以使用最早的 created_at 作为全量更新时间
    // 为了性能考虑，我们使用已获取的 stocksList 来计算（如果数据量很大，可能需要单独查询）
    let lastFullUpdateTime: string | undefined;
    if (stocksList.length > 0) {
      // 从已获取的股票列表中查找最早的 created_at
      const createdTimes = stocksList
        .map((s) => s.created_at)
        .filter((t) => t)
        .map((t) => new Date(t).getTime())
        .filter((t) => !isNaN(t));

      if (createdTimes.length > 0) {
        // 取最早的时间（全量更新时所有股票会在同一时间创建）
        const earliestTime = Math.min(...createdTimes);
        lastFullUpdateTime = new Date(earliestTime).toISOString();
      }
    }

    return {
      stats: {
        totalItems: 0,
        pythonItems: 0,
        nodeItems: 0,
        rustItems: 0,
        totalStocks,
        aStockCount,
        usStockCount,
        hkStockCount,
        providerCount,
        lastFullUpdateTime,
      },
      recentItems: [],
      recentStocks,
    };
  }
}
