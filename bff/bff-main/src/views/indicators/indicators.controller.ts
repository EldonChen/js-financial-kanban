import {
  Controller,
  Get,
  Post,
  Param,
  Query,
  Body,
  Res,
  ParseIntPipe,
  DefaultValuePipe,
} from '@nestjs/common';
import { Response } from 'express';
import { IndicatorsService } from './indicators.service';

@Controller('views/indicators')
export class IndicatorsController {
  constructor(private readonly indicatorsService: IndicatorsService) {}

  /**
   * 获取支持的指标列表
   * GET /api/bff/v1/views/indicators/supported
   */
  @Get('supported')
  async getSupportedIndicators() {
    return this.indicatorsService.getSupportedIndicators();
  }

  /**
   * 计算技术指标
   * POST /api/bff/v1/views/indicators/:ticker/calculate
   */
  @Post(':ticker/calculate')
  async calculateIndicator(
    @Param('ticker') ticker: string,
    @Query('indicator_name') indicatorName: string,
    @Body() params?: Record<string, any>,
  ) {
    return this.indicatorsService.calculateIndicator(
      ticker,
      indicatorName,
      params,
    );
  }

  /**
   * 查询技术指标数据
   * GET /api/bff/v1/views/indicators/:ticker
   * 支持分页和非分页模式
   */
  @Get(':ticker')
  async queryIndicatorData(
    @Param('ticker') ticker: string,
    @Query('indicator_name') indicatorName?: string,
    @Query('period') period?: string,
    @Query('start_date') startDate?: string,
    @Query('end_date') endDate?: string,
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
    return this.indicatorsService.queryIndicatorData(ticker, {
      indicator_name: indicatorName,
      period,
      start_date: startDate,
      end_date: endDate,
      page,
      page_size: pageSize,
    });
  }

  /**
   * 批量计算技术指标（SSE）
   * GET /api/bff/v1/views/indicators/batch-calculate
   * ⚠️ 使用 GET 而非 POST，因为 EventSource 只支持 GET
   */
  @Get('batch-calculate')
  async batchCalculateIndicators(
    @Res({ passthrough: false }) res: Response,
    @Query('tickers') tickers?: string,
    @Query('indicator_names') indicatorNames?: string,
  ) {
    // 设置 SSE 响应头
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');

    // 解析参数
    const tickerList = tickers ? tickers.split(',').map((t) => t.trim()) : [];
    const indicatorList = indicatorNames
      ? indicatorNames.split(',').map((i) => i.trim())
      : [];

    // 调用服务层方法，代理 SSE 流
    await this.indicatorsService.batchCalculateIndicatorsSSE(
      tickerList,
      indicatorList,
      res,
    );
  }
}
