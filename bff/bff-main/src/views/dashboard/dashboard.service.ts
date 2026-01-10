import { Injectable } from '@nestjs/common';
import { PythonClient } from '../../clients/python.client';
import { NodeClient } from '../../clients/node.client';
import { RustClient } from '../../clients/rust.client';
import { StockInfoClient } from '../../clients/stock-info.client';
import { allSettledWithNull } from '../../common/utils/promise.util';

export interface DashboardData {
  stats: {
    totalItems: number;
    pythonItems: number;
    nodeItems: number;
    rustItems: number;
    totalStocks: number;
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
    // 并行获取所有数据，允许部分失败
    const [pythonItems, nodeItems, rustItems, stocks] =
      await allSettledWithNull([
        this.pythonClient.getItems(),
        this.nodeClient.getItems(),
        this.rustClient.getItems(),
        this.stockInfoClient.getStocks(),
      ]);

    const pythonItemsList = pythonItems || [];
    const nodeItemsList = nodeItems || [];
    const rustItemsList = rustItems || [];
    const stocksList = stocks || [];

    // 获取最近的 items（取前 5 个）
    const allItems = [
      ...pythonItemsList.map((item) => ({ ...item, source: 'python' })),
      ...nodeItemsList.map((item) => ({ ...item, source: 'node' })),
      ...rustItemsList.map((item) => ({ ...item, source: 'rust' })),
    ];
    const recentItems = allItems
      .sort(
        (a, b) =>
          new Date(b.updated_at || b.updatedAt || 0).getTime() -
          new Date(a.updated_at || a.updatedAt || 0).getTime(),
      )
      .slice(0, 5);

    // 获取最近的 stocks（取前 5 个）
    const recentStocks = stocksList
      .sort(
        (a, b) =>
          new Date(b.last_updated || 0).getTime() -
          new Date(a.last_updated || 0).getTime(),
      )
      .slice(0, 5);

    return {
      stats: {
        totalItems:
          pythonItemsList.length +
          nodeItemsList.length +
          rustItemsList.length,
        pythonItems: pythonItemsList.length,
        nodeItems: nodeItemsList.length,
        rustItems: rustItemsList.length,
        totalStocks: stocksList.length,
      },
      recentItems,
      recentStocks,
    };
  }
}
