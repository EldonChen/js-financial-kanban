import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ViewsModule } from './views/views.module';
import { ClientsModule } from './clients/clients.module';
import { HealthModule } from './health/health.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),
    ClientsModule,
    ViewsModule,
    HealthModule,
  ],
})
export class AppModule {}
