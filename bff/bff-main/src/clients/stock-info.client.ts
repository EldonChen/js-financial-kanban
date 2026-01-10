import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosResponse } from 'axios';

export interface Stock {
  ticker: string;
  name?: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  price?: number;
  volume?: number;
  created_at?: string;
  last_updated?: string;
}

export interface StockApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

@Injectable()
export class StockInfoClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl =
      process.env.STOCK_INFO_SERVICE_URL || 'http://localhost:8001';
  }

  /**
   * 获取所有股票
   */
  async getStocks(): Promise<Stock[]> {
    try {
      const response: AxiosResponse<StockApiResponse<Stock[]>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/stocks`),
        );
      return response.data.data || [];
    } catch (error) {
      console.error('StockInfoClient.getStocks error:', error);
      throw error;
    }
  }

  /**
   * 获取单个股票
   */
  async getStock(ticker: string): Promise<Stock | null> {
    try {
      const response: AxiosResponse<StockApiResponse<Stock>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/stocks/${ticker}`),
        );
      return response.data.data || null;
    } catch (error) {
      console.error(`StockInfoClient.getStock(${ticker}) error:`, error);
      throw error;
    }
  }

  /**
   * 创建或更新股票
   */
  async upsertStock(ticker: string): Promise<Stock> {
    try {
      const response: AxiosResponse<StockApiResponse<Stock>> =
        await firstValueFrom(
          this.httpService.post(
            `${this.baseUrl}/api/v1/stocks/${ticker}/update`,
          ),
        );
      return response.data.data;
    } catch (error) {
      console.error(`StockInfoClient.upsertStock(${ticker}) error:`, error);
      throw error;
    }
  }

  /**
   * 删除股票
   */
  async deleteStock(ticker: string): Promise<void> {
    try {
      await firstValueFrom(
        this.httpService.delete(`${this.baseUrl}/api/v1/stocks/${ticker}`),
      );
    } catch (error) {
      console.error(`StockInfoClient.deleteStock(${ticker}) error:`, error);
      throw error;
    }
  }
}
