import { Injectable } from '@nestjs/common';
import { StockInfoClient, Stock } from '../../clients/stock-info.client';

@Injectable()
export class StocksService {
  constructor(private readonly stockInfoClient: StockInfoClient) {}

  async getAllStocks(): Promise<Stock[]> {
    try {
      return await this.stockInfoClient.getStocks();
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
