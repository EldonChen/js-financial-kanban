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
}
