import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosResponse } from 'axios';

export interface IndicatorData {
  date: string;
  timestamp: string;
  indicator_name: string;
  value: number | Record<string, number>;
  params?: Record<string, any>;
}

export interface IndicatorQueryParams {
  indicator_name?: string;
  period?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export interface SupportedIndicator {
  name: string;
  display_name: string;
  category: 'trend' | 'momentum' | 'volatility' | 'volume';
  description?: string;
  params?: Record<string, any>;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

@Injectable()
export class IndicatorsClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl =
      process.env.STOCK_INFO_SERVICE_URL || 'http://localhost:8001';
  }

  /**
   * 获取支持的指标列表
   */
  async getSupportedIndicators(): Promise<SupportedIndicator[]> {
    try {
      const response: AxiosResponse<ApiResponse<SupportedIndicator[]>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/indicators/supported`),
        );

      return response.data.data || [];
    } catch (error: any) {
      console.error(
        'IndicatorsClient.getSupportedIndicators error:',
        error.message || error,
      );
      throw error;
    }
  }

  /**
   * 计算技术指标
   */
  async calculateIndicator(
    ticker: string,
    indicatorName: string,
    params?: Record<string, any>,
  ): Promise<IndicatorData[]> {
    try {
      const queryParams: Record<string, any> = {
        indicator_name: indicatorName,
      };

      const response: AxiosResponse<ApiResponse<IndicatorData[]>> =
        await firstValueFrom(
          this.httpService.post(
            `${this.baseUrl}/api/v1/indicators/${ticker}/calculate`,
            params || {},
            { params: queryParams },
          ),
        );

      return response.data.data || [];
    } catch (error: any) {
      console.error(
        `IndicatorsClient.calculateIndicator(${ticker}, ${indicatorName}) error:`,
        error.message || error,
      );
      throw error;
    }
  }

  /**
   * 查询技术指标数据
   */
  async queryIndicatorData(
    ticker: string,
    params?: IndicatorQueryParams,
  ): Promise<IndicatorData[]> {
    try {
      const queryParams: Record<string, any> = {};
      if (params?.indicator_name)
        queryParams.indicator_name = params.indicator_name;
      if (params?.period) queryParams.period = params.period;
      if (params?.start_date) queryParams.start_date = params.start_date;
      if (params?.end_date) queryParams.end_date = params.end_date;
      if (params?.page) queryParams.page = params.page;
      if (params?.page_size) queryParams.page_size = params.page_size;

      const response: AxiosResponse<ApiResponse<{ data: IndicatorData[] }>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/indicators/${ticker}`, {
            params: queryParams,
          }),
        );

      return response.data.data?.data || [];
    } catch (error: any) {
      console.error(
        `IndicatorsClient.queryIndicatorData(${ticker}) error:`,
        error.message || error,
      );
      throw error;
    }
  }
}
