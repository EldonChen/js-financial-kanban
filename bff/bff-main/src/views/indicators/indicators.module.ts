import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { IndicatorsController } from './indicators.controller';
import { IndicatorsService } from './indicators.service';
import { IndicatorsClient } from '../../clients/indicators.client';

@Module({
  imports: [HttpModule],
  controllers: [IndicatorsController],
  providers: [IndicatorsService, IndicatorsClient],
  exports: [IndicatorsService],
})
export class IndicatorsModule {}
