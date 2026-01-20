import { Module } from '@nestjs/common';
import { ClientsModule } from '../clients/clients.module';
import { DashboardModule } from './dashboard/dashboard.module';
import { ItemsModule } from './items/items.module';
import { StocksModule } from './stocks/stocks.module';
import { HistoricalDataModule } from './historical-data/historical-data.module';
import { IndicatorsModule } from './indicators/indicators.module';

@Module({
  imports: [
    ClientsModule,
    DashboardModule,
    ItemsModule,
    StocksModule,
    HistoricalDataModule,
    IndicatorsModule,
  ],
})
export class ViewsModule {}
