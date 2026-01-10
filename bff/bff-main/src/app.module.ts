import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ViewsModule } from './views/views.module';
import { ClientsModule } from './clients/clients.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),
    ClientsModule,
    ViewsModule,
  ],
})
export class AppModule {}
