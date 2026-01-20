import { Injectable } from '@nestjs/common';
import { Response } from 'express';
import { firstValueFrom } from 'rxjs';
import { HttpService } from '@nestjs/axios';
import {
  IndicatorsClient,
  IndicatorData,
  IndicatorQueryParams,
  SupportedIndicator,
} from '../../clients/indicators.client';

export interface IndicatorDataResponse {
  ticker: string;
  indicator_name: string;
  count: number;
  data: IndicatorData[];
}

export interface PaginatedIndicatorDataResponse {
  items: IndicatorData[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

@Injectable()
export class IndicatorsService {
  private readonly baseUrl: string;

  constructor(
    private readonly indicatorsClient: IndicatorsClient,
    private readonly httpService: HttpService,
  ) {
    this.baseUrl =
      process.env.STOCK_INFO_SERVICE_URL || 'http://localhost:8001';
  }

  /**
   * 获取支持的指标列表
   */
  async getSupportedIndicators(): Promise<SupportedIndicator[]> {
    try {
      return await this.indicatorsClient.getSupportedIndicators();
    } catch (error: any) {
      console.error(
        'IndicatorsService.getSupportedIndicators error:',
        error.message || error,
      );
      // 返回空数组而不是抛出错误
      return [];
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
      return await this.indicatorsClient.calculateIndicator(
        ticker,
        indicatorName,
        params,
      );
    } catch (error: any) {
      console.error(
        `IndicatorsService.calculateIndicator(${ticker}, ${indicatorName}) error:`,
        error.message || error,
      );
      throw error;
    }
  }

  /**
   * 查询技术指标数据
   * 根据是否有分页参数，返回不同格式的响应
   */
  async queryIndicatorData(
    ticker: string,
    params?: IndicatorQueryParams,
  ): Promise<IndicatorDataResponse | PaginatedIndicatorDataResponse> {
    try {
      // 判断是否需要分页
      const hasPagination =
        params?.page !== undefined || params?.page_size !== undefined;

      const data = await this.indicatorsClient.queryIndicatorData(
        ticker,
        params,
      );

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
          indicator_name: params?.indicator_name || '',
          count: data.length,
          data,
        };
      }
    } catch (error: any) {
      console.error(
        `IndicatorsService.queryIndicatorData(${ticker}) error:`,
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
          indicator_name: params?.indicator_name || '',
          count: 0,
          data: [],
        };
      }
    }
  }

  /**
   * 批量计算技术指标（SSE）
   * 代理后台服务的 SSE 流，转发给前端
   */
  async batchCalculateIndicatorsSSE(
    tickers: string[],
    indicatorNames: string[],
    res: Response,
  ): Promise<void> {
    try {
      // 构建查询参数
      const queryParams: Record<string, any> = {
        tickers: tickers.join(','),
        indicator_names: indicatorNames.join(','),
      };

      const url = `${this.baseUrl}/api/v1/indicators/batch-calculate`;

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
          'IndicatorsService.batchCalculateIndicatorsSSE stream error:',
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
        'IndicatorsService.batchCalculateIndicatorsSSE error:',
        error.message || error,
      );
      if (!res.headersSent) {
        res.write(
          `data: ${JSON.stringify({ stage: 'error', message: error.message || '批量计算失败' })}\n\n`,
        );
      }
      res.end();
    }
  }
}
