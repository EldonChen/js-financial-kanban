# 技术方案设计 - 数据支持模块（BFF层实现）

> **项目状态**：设计阶段  
> **创建时间**：2025-01-12  
> **文档位置**：docs/  
> **优先级**：P0 - 最高优先级

## 项目概述

本文档描述数据支持模块的 BFF（Backend For Frontend）层实现方案，包括历史数据视图、技术指标视图、数据质量视图、数据同步视图等模块的设计和实现。

## 技术栈

### 现有技术栈（保持不变）
- **框架**：NestJS
- **运行时**：Bun
- **HTTP 客户端**：@nestjs/axios
- **包管理**：bun

### 新增需求
- **SSE 支持**：用于实时进度推送
  - **使用**：NestJS 的 `@Sse()` 装饰器或 `StreamingResponse`

## 架构设计

### 1. 模块结构

**目录结构**：
```
bff/bff-main/src/
├── views/
│   ├── dashboard/              # Dashboard 视图（已存在）
│   ├── items/                  # Items 视图（已存在）
│   ├── stocks/                 # Stocks 视图（已存在）
│   ├── historical-data/        # 历史数据视图（新增）
│   │   ├── historical-data.controller.ts
│   │   ├── historical-data.service.ts
│   │   └── historical-data.module.ts
│   ├── indicators/             # 技术指标视图（新增）
│   │   ├── indicators.controller.ts
│   │   ├── indicators.service.ts
│   │   └── indicators.module.ts
│   ├── data-quality/           # 数据质量视图（新增）
│   │   ├── data-quality.controller.ts
│   │   ├── data-quality.service.ts
│   │   └── data-quality.module.ts
│   └── data-sync/              # 数据同步视图（新增）
│       ├── data-sync.controller.ts
│       ├── data-sync.service.ts
│       └── data-sync.module.ts
├── clients/
│   ├── python.client.ts        # Python 服务客户端（已存在）
│   ├── node.client.ts           # Node.js 服务客户端（已存在）
│   ├── rust.client.ts          # Rust 服务客户端（已存在）
│   └── stock-info.client.ts    # 股票信息服务客户端（已存在）
│   └── historical-data.client.ts  # 历史数据服务客户端（新增）
└── views.module.ts             # 视图模块（更新）
```

### 2. HTTP 客户端设计

#### 2.1 历史数据服务客户端

**文件位置**：`bff/bff-main/src/clients/historical-data.client.ts`

**设计模式**：与现有 `stock-info.client.ts` 保持一致

```typescript
import { Injectable, HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

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
}

@Injectable()
export class HistoricalDataClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl = process.env.STOCK_INFO_SERVICE_URL || 'http://localhost:8001';
  }

  /**
   * 获取历史K线数据
   */
  async getKlineData(
    ticker: string,
    params?: HistoricalDataQueryParams
  ): Promise<KlineData[]> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.period) queryParams.append('period', params.period);
      if (params?.start_date) queryParams.append('start_date', params.start_date);
      if (params?.end_date) queryParams.append('end_date', params.end_date);
      if (params?.limit) queryParams.append('limit', params.limit.toString());

      const queryString = queryParams.toString();
      const url = queryString
        ? `${this.baseUrl}/api/v1/historical-data/${ticker}?${queryString}`
        : `${this.baseUrl}/api/v1/historical-data/${ticker}`;

      const response = await firstValueFrom(
        this.httpService.get<{ code: number; message: string; data: { data: KlineData[] } }>(url)
      );

      return response.data.data?.data || [];
    } catch (error: any) {
      console.error('HistoricalDataClient.getKlineData error:', error);
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
    }
  ): Promise<{ updated_count: number; new_count: number }> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.period) queryParams.append('period', params.period);
      if (params?.incremental !== undefined) queryParams.append('incremental', params.incremental.toString());
      if (params?.data_source) queryParams.append('data_source', params.data_source);

      const queryString = queryParams.toString();
      const url = queryString
        ? `${this.baseUrl}/api/v1/historical-data/${ticker}/update?${queryString}`
        : `${this.baseUrl}/api/v1/historical-data/${ticker}/update`;

      const response = await firstValueFrom(
        this.httpService.post<{ code: number; message: string; data: { updated_count: number; new_count: number } }>(url)
      );

      return response.data.data || { updated_count: 0, new_count: 0 };
    } catch (error: any) {
      console.error('HistoricalDataClient.updateKlineData error:', error);
      throw error;
    }
  }

  /**
   * 获取历史K线数据统计
   */
  async getKlineDataStatistics(
    ticker?: string,
    period?: string
  ): Promise<{
    total_count: number;
    start_date: string;
    end_date: string;
    missing_dates: string[];
  }> {
    try {
      const queryParams = new URLSearchParams();
      if (period) queryParams.append('period', period);

      const queryString = queryParams.toString();
      const url = ticker
        ? queryString
          ? `${this.baseUrl}/api/v1/historical-data/${ticker}/statistics?${queryString}`
          : `${this.baseUrl}/api/v1/historical-data/${ticker}/statistics`
        : queryString
          ? `${this.baseUrl}/api/v1/historical-data/statistics?${queryString}`
          : `${this.baseUrl}/api/v1/historical-data/statistics`;

      const response = await firstValueFrom(
        this.httpService.get<{ code: number; message: string; data: any }>(url)
      );

      return response.data.data || {
        total_count: 0,
        start_date: '',
        end_date: '',
        missing_dates: []
      };
    } catch (error: any) {
      console.error('HistoricalDataClient.getKlineDataStatistics error:', error);
      throw error;
    }
  }
}
```

### 3. 视图服务设计

#### 3.1 历史数据视图服务

**文件位置**：`bff/bff-main/src/views/historical-data/historical-data.service.ts`

**设计模式**：与现有 `stocks.service.ts` 保持一致

```typescript
import { Injectable } from '@nestjs/common';
import { HistoricalDataClient } from '../../clients/historical-data.client';

export interface HistoricalDataQueryParams {
  ticker?: string;
  period?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
}

@Injectable()
export class HistoricalDataService {
  constructor(private readonly historicalDataClient: HistoricalDataClient) {}

  /**
   * 获取历史K线数据
   */
  async getKlineData(
    ticker: string,
    params?: HistoricalDataQueryParams
  ): Promise<{ ticker: string; period: string; count: number; data: any[] }> {
    try {
      const data = await this.historicalDataClient.getKlineData(ticker, params);
      return {
        ticker,
        period: params?.period || '1d',
        count: data.length,
        data
      };
    } catch (error: any) {
      console.error('HistoricalDataService.getKlineData error:', error);
      // 返回空数据而不是抛出错误，允许部分失败
      return {
        ticker,
        period: params?.period || '1d',
        count: 0,
        data: []
      };
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
    }
  ): Promise<{ ticker: string; period: string; updated_count: number; new_count: number }> {
    try {
      const result = await this.historicalDataClient.updateKlineData(ticker, params);
      return {
        ticker,
        period: params?.period || '1d',
        ...result
      };
    } catch (error: any) {
      console.error('HistoricalDataService.updateKlineData error:', error);
      throw error;
    }
  }

  /**
   * 获取历史K线数据统计
   */
  async getKlineDataStatistics(
    ticker?: string,
    period?: string
  ): Promise<any> {
    try {
      return await this.historicalDataClient.getKlineDataStatistics(ticker, period);
    } catch (error: any) {
      console.error('HistoricalDataService.getKlineDataStatistics error:', error);
      // 返回默认统计信息
      return {
        total_count: 0,
        start_date: '',
        end_date: '',
        missing_dates: []
      };
    }
  }
}
```

#### 3.2 历史数据视图控制器

**文件位置**：`bff/bff-main/src/views/historical-data/historical-data.controller.ts`

**设计模式**：与现有 `stocks.controller.ts` 保持一致

```typescript
import {
  Controller,
  Get,
  Post,
  Param,
  Query,
  Res,
} from '@nestjs/common';
import { Response } from 'express';
import { HistoricalDataService } from './historical-data.service';

@Controller('views/historical-data')
export class HistoricalDataController {
  constructor(private readonly historicalDataService: HistoricalDataService) {}

  @Get(':ticker')
  async getKlineData(
    @Param('ticker') ticker: string,
    @Query('period') period?: string,
    @Query('start_date') startDate?: string,
    @Query('end_date') endDate?: string,
    @Query('limit') limit?: string,
  ) {
    const limitNum = limit ? parseInt(limit, 10) : undefined;
    return this.historicalDataService.getKlineData(ticker, {
      period,
      start_date: startDate,
      end_date: endDate,
      limit: limitNum,
    });
  }

  @Post(':ticker/update')
  async updateKlineData(
    @Param('ticker') ticker: string,
    @Query('period') period?: string,
    @Query('incremental') incremental?: string,
    @Query('data_source') dataSource?: string,
  ) {
    return this.historicalDataService.updateKlineData(ticker, {
      period,
      incremental: incremental === 'true',
      data_source: dataSource,
    });
  }

  @Get(':ticker/statistics')
  async getKlineDataStatistics(
    @Param('ticker') ticker: string,
    @Query('period') period?: string,
  ) {
    return this.historicalDataService.getKlineDataStatistics(ticker, period);
  }

  @Post('batch')
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

    // 调用服务层方法，代理 SSE 流
    await this.historicalDataService.batchUpdateKlineDataSSE(
      tickers?.split(',') || [],
      { period, start_date: startDate, end_date: endDate },
      res
    );
  }
}
```

### 4. 模块注册

**文件位置**：`bff/bff-main/src/views/historical-data/historical-data.module.ts`

```typescript
import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { HistoricalDataController } from './historical-data.controller';
import { HistoricalDataService } from './historical-data.service';
import { HistoricalDataClient } from '../../clients/historical-data.client';

@Module({
  imports: [HttpModule],
  controllers: [HistoricalDataController],
  providers: [HistoricalDataService, HistoricalDataClient],
  exports: [HistoricalDataService],
})
export class HistoricalDataModule {}
```

**文件位置**：`bff/bff-main/src/views/views.module.ts`（更新）

```typescript
import { Module } from '@nestjs/common';
import { DashboardModule } from './dashboard/dashboard.module';
import { ItemsModule } from './items/items.module';
import { StocksModule } from './stocks/stocks.module';
import { HistoricalDataModule } from './historical-data/historical-data.module';
import { IndicatorsModule } from './indicators/indicators.module';
import { DataQualityModule } from './data-quality/data-quality.module';
import { DataSyncModule } from './data-sync/data-sync.module';

@Module({
  imports: [
    DashboardModule,
    ItemsModule,
    StocksModule,
    HistoricalDataModule,  // 新增
    IndicatorsModule,       // 新增
    DataQualityModule,      // 新增
    DataSyncModule,         // 新增
  ],
})
export class ViewsModule {}
```

## API 路由设计

### 1. 历史数据视图 API

**路由前缀**：`/api/bff/v1/views/historical-data`

**接口列表**：
- `GET /api/bff/v1/views/historical-data/:ticker` - 获取历史K线数据
- `POST /api/bff/v1/views/historical-data/:ticker/update` - 更新历史K线数据
- `GET /api/bff/v1/views/historical-data/:ticker/statistics` - 获取历史K线数据统计
- `POST /api/bff/v1/views/historical-data/batch` - 批量更新历史K线数据（SSE）

### 2. 技术指标视图 API

**路由前缀**：`/api/bff/v1/views/indicators`

**接口列表**：
- `POST /api/bff/v1/views/indicators/calculate` - 计算技术指标
- `POST /api/bff/v1/views/indicators/batch-calculate` - 批量计算技术指标（SSE）
- `GET /api/bff/v1/views/indicators/:ticker` - 查询技术指标数据
- `GET /api/bff/v1/views/indicators/supported` - 获取支持的指标列表

### 3. 数据质量视图 API

**路由前缀**：`/api/bff/v1/views/data-quality`

**接口列表**：
- `POST /api/bff/v1/views/data-quality/check` - 运行数据质量检查
- `POST /api/bff/v1/views/data-quality/fix` - 修复数据问题
- `GET /api/bff/v1/views/data-quality/report` - 获取数据质量报告

### 4. 数据同步视图 API

**路由前缀**：`/api/bff/v1/views/data-sync`

**接口列表**：
- `POST /api/bff/v1/views/data-sync/sync` - 触发数据同步（SSE）
- `GET /api/bff/v1/views/data-sync/status` - 获取同步状态

## SSE 实现设计

### SSE 代理模式

**设计思路**：
- BFF 层作为 SSE 代理，接收后台服务的 SSE 流
- 将后台服务的 SSE 流转发给前端
- 处理错误和超时

**实现示例**（`historical-data.service.ts`）：
```typescript
async batchUpdateKlineDataSSE(
  tickers: string[],
  params: any,
  res: Response
): Promise<void> {
  try {
    // 调用后台服务的批量更新接口（SSE）
    const backendUrl = `${process.env.STOCK_INFO_SERVICE_URL}/api/v1/historical-data/batch`;
    const queryParams = new URLSearchParams();
    queryParams.append('tickers', tickers.join(','));
    if (params.period) queryParams.append('period', params.period);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);

    const url = `${backendUrl}?${queryParams.toString()}`;
    
    // 使用 axios 接收 SSE 流
    const response = await firstValueFrom(
      this.httpService.get(url, {
        responseType: 'stream',
        headers: {
          'Accept': 'text/event-stream',
        },
      })
    );

    // 将流转发给前端
    response.data.pipe(res);
  } catch (error: any) {
    console.error('HistoricalDataService.batchUpdateKlineDataSSE error:', error);
    res.write(`data: ${JSON.stringify({ stage: 'error', message: error.message })}\n\n`);
    res.end();
  }
}
```

## 错误处理

### 统一错误处理

**设计模式**：与现有错误处理保持一致

```typescript
// 在控制器中处理错误
@Post(':ticker/update')
async updateKlineData(
  @Param('ticker') ticker: string,
  @Query('period') period?: string,
) {
  try {
    return await this.historicalDataService.updateKlineData(ticker, { period });
  } catch (error: any) {
    // 根据错误类型返回适当的 HTTP 状态码和错误信息
    if (error.status) {
      throw new HttpException(
        {
          code: error.status,
          message: error.message || '更新失败',
          data: null,
        },
        error.status,
      );
    }
    throw new HttpException(
      {
        code: 500,
        message: error.message || '更新失败',
        data: null,
      },
      HttpStatus.INTERNAL_SERVER_ERROR,
    );
  }
}
```

## 实施步骤

### Phase 1：HTTP 客户端实现
1. 创建 `historical-data.client.ts`
2. 创建 `indicators.client.ts`
3. 创建 `data-quality.client.ts`
4. 创建 `data-sync.client.ts`

### Phase 2：视图服务实现
1. 创建 `historical-data` 模块（controller, service, module）
2. 创建 `indicators` 模块
3. 创建 `data-quality` 模块
4. 创建 `data-sync` 模块

### Phase 3：SSE 实现
1. 实现 SSE 代理功能
2. 实现错误处理和超时处理

### Phase 4：模块注册和测试
1. 在 `views.module.ts` 中注册新模块
2. 测试所有接口
3. 测试 SSE 功能

## 注意事项

1. **向后兼容**：
   - 新增模块不影响现有模块
   - 新增路由不影响现有路由
   - 新增客户端不影响现有客户端

2. **错误处理**：
   - 统一错误响应格式
   - 允许部分服务失败（返回空数据）
   - 记录详细错误日志

3. **性能优化**：
   - 使用连接池管理 HTTP 连接
   - 设置合理的超时时间
   - 实现请求重试机制

4. **代码规范**：
   - 遵循现有代码风格
   - 使用 TypeScript 类型定义
   - 模块和函数命名清晰

---

**BFF层实现方案设计已完成**

**参考文档**：
- `docs/技术方案设计-数据支持模块-后台服务.md`（后台服务 API 设计）
- `docs/技术方案设计-数据支持模块-前端实现.md`（前端 API 调用设计）
