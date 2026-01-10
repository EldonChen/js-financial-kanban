import { Module } from '@nestjs/common';
import { ClientsModule } from '../../clients/clients.module';
import { ItemsController } from './items.controller';
import { ItemsService } from './items.service';

@Module({
  imports: [ClientsModule],
  controllers: [ItemsController],
  providers: [ItemsService],
})
export class ItemsModule {}
