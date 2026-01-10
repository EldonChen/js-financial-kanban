import { Module } from '@nestjs/common';
import { ClientsModule } from '../../clients/clients.module';
import { StocksController } from './stocks.controller';
import { StocksService } from './stocks.service';

@Module({
  imports: [ClientsModule],
  controllers: [StocksController],
  providers: [StocksService],
})
export class StocksModule {}
