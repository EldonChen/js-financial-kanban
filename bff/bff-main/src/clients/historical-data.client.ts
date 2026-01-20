import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosResponse } from 'axios';

export interface KlineData {
  date: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number;
  adj_close?: number;
  data_source: string;
}

export interface HistoricalDataQueryParams {
  period?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  page?: number;
  page_size?: number;
}

export interface HistoricalDataStatistics {
  total_count: number;
  start_date: string;
  end_date: string;
  missing_dates?: string[];
  coverage_rate?: number;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

@Injectable()
export class HistoricalDataClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl =
      process.env.STOCK_INFO_SERVICE_URL || 'http://localhost:8001';
  }

  /**
   * 获取历史K线数据
   */
  async getKlineData(
    ticker: string,
    params?: HistoricalDataQueryParams,
  ): Promise<KlineData[]> {
    try {
      const queryParams: Record<string, any> = {};
      if (params?.period) queryParams.period = params.period;
      if (params?.start_date) queryParams.start_date = params.start_date;
      if (params?.end_date) queryParams.end_date = params.end_date;
      if (params?.limit) queryParams.limit = params.limit;
      if (params?.page) queryParams.page = params.page;
      if (params?.page_size) queryParams.page_size = params.page_size;

      const response: AxiosResponse<ApiResponse<{ data: KlineData[] }>> =
        await firstValueFrom(
          this.httpService.get(
            `${this.baseUrl}/api/v1/historical-data/${ticker}`,
            { params: queryParams },
          ),
        );

      return response.data.data?.data || [];
    } catch (error: any) {
      console.error(
        `HistoricalDataClient.getKlineData(${ticker}) error:`,
        error.message || error,
      );
      throw error;
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
  ): Promise<{ updated_count: number; new_count: number }> {
    try {
      const queryParams: Record<string, any> = {};
      if (params?.period) queryParams.period = params.period;
      if (params?.incremental !== undefined)
        queryParams.incremental = params.incremental;
      if (params?.data_source) queryParams.data_source = params.data_source;

      const response: AxiosResponse<
        ApiResponse<{ updated_count: number; new_count: number }>
      > = await firstValueFrom(
        this.httpService.post(
          `${this.baseUrl}/api/v1/historical-data/${ticker}/update`,
          {},
          { params: queryParams },
        ),
      );

      return response.data.data || { updated_count: 0, new_count: 0 };
    } catch (error: any) {
      console.error(
        `HistoricalDataClient.updateKlineData(${ticker}) error:`,
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
      const queryParams: Record<string, any> = {};
      if (period) queryParams.period = period;

      const response: AxiosResponse<ApiResponse<HistoricalDataStatistics>> =
        await firstValueFrom(
          this.httpService.get(
            `${this.baseUrl}/api/v1/historical-data/${ticker}/statistics`,
            { params: queryParams },
          ),
        );

      return (
        response.data.data || {
          total_count: 0,
          start_date: '',
          end_date: '',
          missing_dates: [],
          coverage_rate: 0,
        }
      );
    } catch (error: any) {
      console.error(
        `HistoricalDataClient.getKlineDataStatistics(${ticker}) error:`,
        error.message || error,
      );
      throw error;
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
  ): Promise<{ deleted_count: number }> {
    try {
      const queryParams: Record<string, any> = {};
      if (params?.period) queryParams.period = params.period;
      if (params?.start_date) queryParams.start_date = params.start_date;
      if (params?.end_date) queryParams.end_date = params.end_date;

      const response: AxiosResponse<ApiResponse<{ deleted_count: number }>> =
        await firstValueFrom(
          this.httpService.delete(
            `${this.baseUrl}/api/v1/historical-data/${ticker}`,
            { params: queryParams },
          ),
        );

      return response.data.data || { deleted_count: 0 };
    } catch (error: any) {
      console.error(
        `HistoricalDataClient.deleteKlineData(${ticker}) error:`,
        error.message || error,
      );
      throw error;
    }
  }
}
