import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosResponse } from 'axios';

export interface Stock {
  ticker: string;
  name?: string;
  sector?: string;
  industry?: string;
  market?: string; // 市场（NASDAQ, NYSE, SSE, SZSE 等）
  market_type?: string; // 市场类型（A股、港股、美股）
  country?: string; // 国家
  exchange?: string; // 交易所代码
  currency?: string; // 货币
  market_cap?: number;
  price?: number;
  volume?: number;
  data_source?: string; // 数据来源（yfinance、akshare、easyquotation 等）
  created_at?: string;
  last_updated?: string;
}

export interface StockApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

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
export class StockInfoClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl =
      process.env.STOCK_INFO_SERVICE_URL || 'http://localhost:8001';
  }

  /**
   * 获取股票列表（支持分页和筛选）
   */
  async getStocks(
    params?: StocksQueryParams,
  ): Promise<PaginatedStocksResponse> {
    try {
      const queryParams: Record<string, any> = {};
      if (params?.ticker) queryParams.ticker = params.ticker;
      if (params?.name) queryParams.name = params.name;
      if (params?.market) queryParams.market = params.market;
      if (params?.marketType) queryParams.market_type = params.marketType;
      if (params?.sector) queryParams.sector = params.sector;
      if (params?.page) queryParams.page = params.page;
      if (params?.pageSize) queryParams.page_size = params.pageSize;

      const response: AxiosResponse<
        StockApiResponse<PaginatedStocksResponse>
      > = await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/api/v1/stocks`, {
          params: queryParams,
        }),
      );
      return response.data.data || {
        items: [],
        total: 0,
        page: params?.page || 1,
        page_size: params?.pageSize || 20,
        total_pages: 0,
      };
    } catch (error) {
      console.error('StockInfoClient.getStocks error:', error);
      throw error;
    }
  }

  /**
   * 获取所有股票（无分页，向后兼容）
   * 注意：股票信息服务返回的是分页格式，需要提取 items 数组
   */
  async getAllStocks(): Promise<Stock[]> {
    try {
      const response: AxiosResponse<StockApiResponse<PaginatedStocksResponse | Stock[]>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/stocks`),
        );
      
      const data = response.data.data;
      
      // 如果返回的是分页格式（包含 items 字段），提取 items 数组
      if (data && typeof data === 'object' && 'items' in data && Array.isArray((data as PaginatedStocksResponse).items)) {
        return (data as PaginatedStocksResponse).items;
      }
      
      // 如果返回的是数组，直接返回
      if (Array.isArray(data)) {
        return data;
      }
      
      // 否则返回空数组
      return [];
    } catch (error) {
      console.error('StockInfoClient.getAllStocks error:', error);
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
   * 注意：股票更新操作可能需要从外部数据源获取数据，耗时较长
   */
  async upsertStock(ticker: string): Promise<Stock> {
    try {
      // 为股票更新操作设置更长的超时时间（60秒）
      const updateTimeout = parseInt(
        process.env.STOCK_UPDATE_TIMEOUT || '60000',
        10,
      );
      const response: AxiosResponse<StockApiResponse<Stock>> =
        await firstValueFrom(
          this.httpService.post(
            `${this.baseUrl}/api/v1/stocks/${ticker}/update`,
            {},
            {
              timeout: updateTimeout,
            },
          ),
        );
      return response.data.data;
    } catch (error: any) {
      // 改进错误处理，提供更友好的错误信息
      if (error.code === 'ECONNABORTED') {
        const timeoutError = new Error(
          `股票更新超时：${ticker} 的数据更新操作超过 ${error.config?.timeout || 60000}ms，请稍后重试`,
        );
        (timeoutError as any).code = 'STOCK_UPDATE_TIMEOUT';
        console.error(`StockInfoClient.upsertStock(${ticker}) timeout:`, timeoutError.message);
        throw timeoutError;
      }
      if (error.response) {
        // HTTP 错误响应
        const httpError = new Error(
          `股票更新失败：${error.response.data?.detail || error.response.data?.message || error.message}`,
        );
        (httpError as any).status = error.response.status;
        (httpError as any).code = 'STOCK_UPDATE_HTTP_ERROR';
        console.error(`StockInfoClient.upsertStock(${ticker}) HTTP error:`, httpError.message);
        throw httpError;
      }
      if (error.request) {
        // 请求已发出但没有收到响应
        const networkError = new Error(
          `股票更新失败：无法连接到股票信息服务 (${this.baseUrl})，请检查服务是否运行`,
        );
        (networkError as any).code = 'STOCK_UPDATE_NETWORK_ERROR';
        console.error(`StockInfoClient.upsertStock(${ticker}) network error:`, networkError.message);
        throw networkError;
      }
      // 其他错误
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

  /**
   * 获取数据源状态信息
   */
  async getProviderStatus(): Promise<{
    total_providers: number;
    providers: Record<string, any>;
    market_coverage: Record<string, string[]>;
  }> {
    try {
      const response: AxiosResponse<
        StockApiResponse<{
          total_providers: number;
          providers: Record<string, any>;
          market_coverage: Record<string, string[]>;
        }>
      > = await firstValueFrom(
        this.httpService.get(`${this.baseUrl}/api/v1/providers/status`),
      );
      return response.data.data || {
        total_providers: 0,
        providers: {},
        market_coverage: {},
      };
    } catch (error) {
      console.error('StockInfoClient.getProviderStatus error:', error);
      throw error;
    }
  }
}
