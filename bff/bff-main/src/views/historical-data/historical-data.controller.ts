import {
  Controller,
  Get,
  Post,
  Delete,
  Param,
  Query,
  Res,
  ParseBoolPipe,
  ParseIntPipe,
  DefaultValuePipe,
} from '@nestjs/common';
import { Response } from 'express';
import { HistoricalDataService } from './historical-data.service';

@Controller('views/historical-data')
export class HistoricalDataController {
  constructor(private readonly historicalDataService: HistoricalDataService) {}

  /**
   * 获取历史K线数据
   * GET /api/bff/v1/views/historical-data/:ticker
   * 支持分页和非分页模式
   */
  @Get(':ticker')
  async getKlineData(
    @Param('ticker') ticker: string,
    @Query('period') period?: string,
    @Query('start_date') startDate?: string,
    @Query('end_date') endDate?: string,
    @Query(
      'limit',
      new DefaultValuePipe(undefined),
      new ParseIntPipe({ optional: true }),
    )
    limit?: number,
    @Query(
      'page',
      new DefaultValuePipe(undefined),
      new ParseIntPipe({ optional: true }),
    )
    page?: number,
    @Query(
      'page_size',
      new DefaultValuePipe(undefined),
      new ParseIntPipe({ optional: true }),
    )
    pageSize?: number,
  ) {
    return this.historicalDataService.getKlineData(ticker, {
      period,
      start_date: startDate,
      end_date: endDate,
      limit,
      page,
      page_size: pageSize,
    });
  }

  /**
   * 获取历史K线数据统计
   * GET /api/bff/v1/views/historical-data/:ticker/statistics
   */
  @Get(':ticker/statistics')
  async getKlineDataStatistics(
    @Param('ticker') ticker: string,
    @Query('period') period?: string,
  ) {
    return this.historicalDataService.getKlineDataStatistics(ticker, period);
  }

  /**
   * 更新历史K线数据
   * POST /api/bff/v1/views/historical-data/:ticker/update
   */
  @Post(':ticker/update')
  async updateKlineData(
    @Param('ticker') ticker: string,
    @Query('period') period?: string,
    @Query('incremental', new DefaultValuePipe('false'), ParseBoolPipe)
    incremental?: boolean,
    @Query('data_source') dataSource?: string,
  ) {
    return this.historicalDataService.updateKlineData(ticker, {
      period,
      incremental,
      data_source: dataSource,
    });
  }

  /**
   * 批量更新历史K线数据（SSE）
   * GET /api/bff/v1/views/historical-data/batch
   * ⚠️ 使用 GET 而非 POST，因为 EventSource 只支持 GET
   */
  @Get('batch')
  async batchUpdateKlineData(
    @Res({ passthrough: false }) res: Response,
    @Query('tickers') tickers?: string,
    @Query('period') period?: string,
    @Query('start_date') startDate?: string,
    @Query('end_date') endDate?: string,
  ) {
    // 设置 SSE 响应头
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');

    // 解析 tickers 参数
    const tickerList = tickers ? tickers.split(',').map((t) => t.trim()) : [];

    // 调用服务层方法，代理 SSE 流
    await this.historicalDataService.batchUpdateKlineDataSSE(
      tickerList,
      {
        period,
        start_date: startDate,
        end_date: endDate,
      },
      res,
    );
  }

  /**
   * 全量更新历史K线数据（SSE）
   * GET /api/bff/v1/views/historical-data/full-update
   * ⚠️ 使用 GET 而非 POST，因为 EventSource 只支持 GET
   */
  @Get('full-update')
  async fullUpdateKlineData(
    @Res({ passthrough: false }) res: Response,
    @Query('period') period?: string,
    @Query('start_date') startDate?: string,
    @Query('end_date') endDate?: string,
  ) {
    // 设置 SSE 响应头
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');

    // 调用服务层方法，代理 SSE 流
    await this.historicalDataService.fullUpdateKlineDataSSE(
      {
        period,
        start_date: startDate,
        end_date: endDate,
      },
      res,
    );
  }

  /**
   * 删除历史K线数据
   * DELETE /api/bff/v1/views/historical-data/:ticker
   */
  @Delete(':ticker')
  async deleteKlineData(
    @Param('ticker') ticker: string,
    @Query('period') period?: string,
    @Query('start_date') startDate?: string,
    @Query('end_date') endDate?: string,
  ) {
    return this.historicalDataService.deleteKlineData(ticker, {
      period,
      start_date: startDate,
      end_date: endDate,
    });
  }
}
