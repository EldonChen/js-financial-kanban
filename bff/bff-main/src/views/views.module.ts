import { Module } from '@nestjs/common';
import { ClientsModule } from '../clients/clients.module';
import { DashboardModule } from './dashboard/dashboard.module';
import { ItemsModule } from './items/items.module';
import { StocksModule } from './stocks/stocks.module';

@Module({
  imports: [ClientsModule, DashboardModule, ItemsModule, StocksModule],
})
export class ViewsModule {}
