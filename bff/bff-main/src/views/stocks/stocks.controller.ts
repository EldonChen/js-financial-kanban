import {
  Controller,
  Get,
  Post,
  Delete,
  Param,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { StocksService } from './stocks.service';

@Controller('views/stocks')
export class StocksController {
  constructor(private readonly stocksService: StocksService) {}

  @Get()
  async getStocks() {
    return this.stocksService.getAllStocks();
  }

  @Get(':ticker')
  async getStock(@Param('ticker') ticker: string) {
    const stock = await this.stocksService.getStock(ticker);
    if (!stock) {
      throw new HttpException(
        {
          code: 404,
          message: `股票 ${ticker} 不存在`,
          data: null,
        },
        HttpStatus.NOT_FOUND,
      );
    }
    return stock;
  }

  @Post(':ticker/update')
  async updateStock(@Param('ticker') ticker: string) {
    try {
      return await this.stocksService.updateStock(ticker);
    } catch (error: any) {
      // 根据错误类型返回适当的 HTTP 状态码和错误信息
      if (error.code === 'STOCK_UPDATE_TIMEOUT') {
        throw new HttpException(
          {
            code: 408,
            message: error.message || '股票更新超时',
            data: null,
          },
          HttpStatus.REQUEST_TIMEOUT,
        );
      }
      if (error.code === 'STOCK_UPDATE_NETWORK_ERROR') {
        throw new HttpException(
          {
            code: 503,
            message: error.message || '股票信息服务不可用',
            data: null,
          },
          HttpStatus.SERVICE_UNAVAILABLE,
        );
      }
      if (error.status) {
        // HTTP 错误响应
        throw new HttpException(
          {
            code: error.status,
            message: error.message || '股票更新失败',
            data: null,
          },
          error.status,
        );
      }
      // 其他错误
      throw new HttpException(
        {
          code: 500,
          message: error.message || '股票更新失败',
          data: null,
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Delete(':ticker')
  async deleteStock(@Param('ticker') ticker: string) {
    return this.stocksService.deleteStock(ticker);
  }
}
