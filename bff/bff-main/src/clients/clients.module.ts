import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { PythonClient } from './python.client';
import { NodeClient } from './node.client';
import { RustClient } from './rust.client';
import { StockInfoClient } from './stock-info.client';

@Module({
  imports: [
    HttpModule.register({
      timeout: parseInt(process.env.HTTP_TIMEOUT || '30000', 10), // 默认 30 秒，股票数据更新可能需要更长时间
      maxRedirects: parseInt(process.env.HTTP_MAX_REDIRECTS || '5', 10),
    }),
  ],
  providers: [PythonClient, NodeClient, RustClient, StockInfoClient],
  exports: [PythonClient, NodeClient, RustClient, StockInfoClient],
})
export class ClientsModule {}
