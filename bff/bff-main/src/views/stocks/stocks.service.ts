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
}
