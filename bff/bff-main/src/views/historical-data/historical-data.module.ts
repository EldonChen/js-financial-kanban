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
