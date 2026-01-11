import { Controller, Get, Post, Delete, Param } from '@nestjs/common';
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
    return this.stocksService.getStock(ticker);
  }

  @Post(':ticker/update')
  async updateStock(@Param('ticker') ticker: string) {
    return this.stocksService.updateStock(ticker);
  }

  @Delete(':ticker')
  async deleteStock(@Param('ticker') ticker: string) {
    return this.stocksService.deleteStock(ticker);
  }
}
