import { Injectable } from '@nestjs/common';
import { StockInfoClient, Stock } from '../../clients/stock-info.client';

export interface StocksQueryParams {
  ticker?: string;
  name?: string;
  market?: string;
  marketType?: string;
  sector?: string;
  page?: number;
  pageSize?: number;
}

export interface PaginatedStocksResponse {
  items: Stock[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

@Injectable()
export class StocksService {
  constructor(private readonly stockInfoClient: StockInfoClient) {}

  async getStocks(params: StocksQueryParams): Promise<PaginatedStocksResponse> {
    try {
      return await this.stockInfoClient.getStocks(params);
    } catch (error) {
      console.error('StocksService.getStocks error:', error);
      // 返回空分页响应而不是抛出错误，允许部分失败
      return {
        items: [],
        total: 0,
        page: params.page || 1,
        page_size: params.pageSize || 20,
        total_pages: 0,
      };
    }
  }

  async getAllStocks(): Promise<Stock[]> {
    try {
      return await this.stockInfoClient.getAllStocks();
    } catch (error) {
      console.error('StocksService.getAllStocks error:', error);
      // 返回空数组而不是抛出错误，允许部分失败
      return [];
    }
  }

  async getStock(ticker: string): Promise<Stock | null> {
    try {
      return await this.stockInfoClient.getStock(ticker);
    } catch (error) {
      console.error(`StocksService.getStock(${ticker}) error:`, error);
      return null;
    }
  }

  async updateStock(ticker: string): Promise<Stock> {
    try {
      return await this.stockInfoClient.upsertStock(ticker);
    } catch (error: any) {
      console.error(`StocksService.updateStock(${ticker}) error:`, error);
      // 重新抛出错误，让 Controller 层处理
      // 错误信息已经在 StockInfoClient 中进行了改进
      throw error;
    }
  }

  async deleteStock(ticker: string): Promise<void> {
    try {
      await this.stockInfoClient.deleteStock(ticker);
    } catch (error) {
      console.error(`StocksService.deleteStock(${ticker}) error:`, error);
      throw error;
    }
  }

  /**
   * 批量更新股票（SSE 流式响应）
   * 代理后端的 SSE 流，转发给前端
   */
  async fetchAllStocksSSE(
    market?: string,
    delay?: string,
    res?: any,
  ): Promise<void> {
    try {
      await this.stockInfoClient.fetchAllStocksSSE(market, delay, res);
    } catch (error) {
      console.error('StocksService.fetchAllStocksSSE error:', error);
      // 如果响应头还没有发送，发送错误响应
      if (res && !res.headersSent) {
        res.status(500).json({
          code: 500,
          message: '批量更新失败',
          data: null,
        });
      } else if (res) {
        res.end();
      }
      throw error;
    }
  }

  /**
   * 获取更新计划列表
   */
  async getSchedules(params?: {
    page?: number;
    page_size?: number;
    is_active?: boolean;
  }): Promise<{
    items: any[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }> {
    try {
      return await this.stockInfoClient.getSchedules(params);
    } catch (error) {
      console.error('StocksService.getSchedules error:', error);
      // 返回空分页响应而不是抛出错误，允许部分失败
      return {
        items: [],
        total: 0,
        page: params?.page || 1,
        page_size: params?.page_size || 20,
        total_pages: 0,
      };
    }
  }

  /**
   * 获取更新计划状态统计
   */
  async getScheduleStatus(): Promise<{
    total: number;
    active: number;
    inactive: number;
    next_run_count: number;
  }> {
    try {
      return await this.stockInfoClient.getScheduleStatus();
    } catch (error) {
      console.error('StocksService.getScheduleStatus error:', error);
      // 返回默认值而不是抛出错误
      return {
        total: 0,
        active: 0,
        inactive: 0,
        next_run_count: 0,
      };
    }
  }

  /**
   * 切换更新计划激活状态
   */
  async toggleSchedule(scheduleId: string): Promise<any> {
    try {
      return await this.stockInfoClient.toggleSchedule(scheduleId);
    } catch (error) {
      console.error(`StocksService.toggleSchedule(${scheduleId}) error:`, error);
      throw error;
    }
  }

  /**
   * 删除更新计划
   */
  async deleteSchedule(scheduleId: string): Promise<void> {
    try {
      await this.stockInfoClient.deleteSchedule(scheduleId);
    } catch (error) {
      console.error(`StocksService.deleteSchedule(${scheduleId}) error:`, error);
      throw error;
    }
  }

  /**
   * 获取数据源状态信息
   */
  async getProviderStatus(): Promise<{
    total_providers: number;
    providers: Record<string, any>;
    market_coverage: Record<string, string[]>;
  }> {
    try {
      return await this.stockInfoClient.getProviderStatus();
    } catch (error) {
      console.error('StocksService.getProviderStatus error:', error);
      // 返回默认值而不是抛出错误
      return {
        total_providers: 0,
        providers: {},
        market_coverage: {},
      };
    }
  }

  /**
   * 创建更新计划
   */
  async createSchedule(scheduleData: {
    schedule_type: 'cron' | 'interval';
    schedule_config: {
      cron?: string;
      interval?: number;
    };
    is_active?: boolean;
    ticker?: string;
    name?: string;
  }): Promise<any> {
    try {
      return await this.stockInfoClient.createSchedule(scheduleData);
    } catch (error) {
      console.error('StocksService.createSchedule error:', error);
      throw error;
    }
  }
}
