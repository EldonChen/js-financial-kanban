import { Injectable } from '@nestjs/common';
import { Response } from 'express';
import { firstValueFrom } from 'rxjs';
import { HttpService } from '@nestjs/axios';
import {
  HistoricalDataClient,
  KlineData,
  HistoricalDataQueryParams,
  HistoricalDataStatistics,
} from '../../clients/historical-data.client';

export interface HistoricalDataResponse {
  ticker: string;
  period: string;
  count: number;
  data: KlineData[];
}

export interface PaginatedHistoricalDataResponse {
  items: KlineData[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

@Injectable()
export class HistoricalDataService {
  private readonly baseUrl: string;

  constructor(
    private readonly historicalDataClient: HistoricalDataClient,
    private readonly httpService: HttpService,
  ) {
    this.baseUrl =
      process.env.STOCK_INFO_SERVICE_URL || 'http://localhost:8001';
  }

  /**
   * 获取历史K线数据
   * 根据是否有分页参数,返回不同格式的响应
   */
  async getKlineData(
    ticker: string,
    params?: HistoricalDataQueryParams,
  ): Promise<HistoricalDataResponse | PaginatedHistoricalDataResponse> {
    try {
      // 判断是否需要分页
      const hasPagination =
        params?.page !== undefined || params?.page_size !== undefined;

      const data = await this.historicalDataClient.getKlineData(ticker, params);

      if (hasPagination) {
        // 分页模式：返回分页格式
        const page = params?.page || 1;
        const pageSize = params?.page_size || 20;
        const total = data.length;
        const totalPages = Math.ceil(total / pageSize);

        return {
          items: data,
          total,
          page,
          page_size: pageSize,
          total_pages: totalPages,
        };
      } else {
        // 列表模式：返回列表格式
        return {
          ticker,
          period: params?.period || '1d',
          count: data.length,
          data,
        };
      }
    } catch (error: any) {
      console.error(
        `HistoricalDataService.getKlineData(${ticker}) error:`,
        error.message || error,
      );
      // 返回空数据而不是抛出错误，允许部分失败
      const hasPagination =
        params?.page !== undefined || params?.page_size !== undefined;
      if (hasPagination) {
        return {
          items: [],
          total: 0,
          page: params?.page || 1,
          page_size: params?.page_size || 20,
          total_pages: 0,
        };
      } else {
        return {
          ticker,
          period: params?.period || '1d',
          count: 0,
          data: [],
        };
      }
    }
  }

  /**
   * 更新历史K线数据
   */
  async updateKlineData(
    ticker: string,
    params?: {
      period?: string;
      incremental?: boolean;
      data_source?: string;
    },
  ): Promise<{
    ticker: string;
    period: string;
    updated_count: number;
    new_count: number;
  }> {
    try {
      const result = await this.historicalDataClient.updateKlineData(
        ticker,
        params,
      );
      return {
        ticker,
        period: params?.period || '1d',
        ...result,
      };
    } catch (error: any) {
      console.error(
        `HistoricalDataService.updateKlineData(${ticker}) error:`,
        error.message || error,
      );
      throw error;
    }
  }

  /**
   * 获取历史K线数据统计
   */
  async getKlineDataStatistics(
    ticker: string,
    period?: string,
  ): Promise<HistoricalDataStatistics> {
    try {
      return await this.historicalDataClient.getKlineDataStatistics(
        ticker,
        period,
      );
    } catch (error: any) {
      console.error(
        `HistoricalDataService.getKlineDataStatistics(${ticker}) error:`,
        error.message || error,
      );
      // 返回默认统计信息
      return {
        total_count: 0,
        start_date: '',
        end_date: '',
        missing_dates: [],
        coverage_rate: 0,
      };
    }
  }

  /**
   * 删除历史K线数据
   */
  async deleteKlineData(
    ticker: string,
    params?: {
      period?: string;
      start_date?: string;
      end_date?: string;
    },
  ): Promise<{ ticker: string; deleted_count: number }> {
    try {
      const result = await this.historicalDataClient.deleteKlineData(
        ticker,
        params,
      );
      return {
        ticker,
        ...result,
      };
    } catch (error: any) {
      console.error(
        `HistoricalDataService.deleteKlineData(${ticker}) error:`,
        error.message || error,
      );
      throw error;
    }
  }

  /**
   * 批量更新历史K线数据（SSE）
   * 代理后台服务的 SSE 流，转发给前端
   */
  async batchUpdateKlineDataSSE(
    tickers: string[],
    params: {
      period?: string;
      start_date?: string;
      end_date?: string;
    },
    res: Response,
  ): Promise<void> {
    try {
      // 构建查询参数
      const queryParams: Record<string, any> = {
        tickers: tickers.join(','),
      };
      if (params.period) queryParams.period = params.period;
      if (params.start_date) queryParams.start_date = params.start_date;
      if (params.end_date) queryParams.end_date = params.end_date;

      const url = `${this.baseUrl}/api/v1/historical-data/batch`;

      // 使用 axios 获取流式响应
      const response = await firstValueFrom(
        this.httpService.get(url, {
          params: queryParams,
          responseType: 'stream',
          headers: {
            Accept: 'text/event-stream',
            'Cache-Control': 'no-cache',
            Connection: 'keep-alive',
          },
        }),
      );

      // 将后端流转发给前端
      response.data.pipe(res);

      // 处理流结束
      response.data.on('end', () => {
        if (!res.headersSent) {
          res.end();
        }
      });

      // 处理错误
      response.data.on('error', (error: any) => {
        console.error(
          'HistoricalDataService.batchUpdateKlineDataSSE stream error:',
          error,
        );
        if (!res.headersSent) {
          res.write(
            `data: ${JSON.stringify({ stage: 'error', message: error.message })}\n\n`,
          );
        }
        res.end();
      });
    } catch (error: any) {
      console.error(
        'HistoricalDataService.batchUpdateKlineDataSSE error:',
        error.message || error,
      );
      if (!res.headersSent) {
        res.write(
          `data: ${JSON.stringify({ stage: 'error', message: error.message || '批量更新失败' })}\n\n`,
        );
      }
      res.end();
    }
  }

  /**
   * 全量更新历史K线数据（SSE）
   * 代理后台服务的 SSE 流，转发给前端
   */
  async fullUpdateKlineDataSSE(
    params: {
      period?: string;
      start_date?: string;
      end_date?: string;
    },
    res: Response,
  ): Promise<void> {
    try {
      // 构建查询参数
      const queryParams: Record<string, any> = {};
      if (params.period) queryParams.period = params.period;
      if (params.start_date) queryParams.start_date = params.start_date;
      if (params.end_date) queryParams.end_date = params.end_date;

      const url = `${this.baseUrl}/api/v1/historical-data/full-update`;

      // 使用 axios 获取流式响应
      const response = await firstValueFrom(
        this.httpService.get(url, {
          params: queryParams,
          responseType: 'stream',
          headers: {
            Accept: 'text/event-stream',
            'Cache-Control': 'no-cache',
            Connection: 'keep-alive',
          },
        }),
      );

      // 将后端流转发给前端
      response.data.pipe(res);

      // 处理流结束
      response.data.on('end', () => {
        if (!res.headersSent) {
          res.end();
        }
      });

      // 处理错误
      response.data.on('error', (error: any) => {
        console.error(
          'HistoricalDataService.fullUpdateKlineDataSSE stream error:',
          error,
        );
        if (!res.headersSent) {
          res.write(
            `data: ${JSON.stringify({ stage: 'error', message: error.message })}\n\n`,
          );
        }
        res.end();
      });
    } catch (error: any) {
      console.error(
        'HistoricalDataService.fullUpdateKlineDataSSE error:',
        error.message || error,
      );
      if (!res.headersSent) {
        res.write(
          `data: ${JSON.stringify({ stage: 'error', message: error.message || '全量更新失败' })}\n\n`,
        );
      }
      res.end();
    }
  }
}
