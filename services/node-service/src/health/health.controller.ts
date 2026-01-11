import { Controller, Get } from '@nestjs/common';

@Controller('health')
export class HealthController {
  @Get()
  health() {
    return {
      status: 'healthy',
      service: 'node-service',
      timestamp: new Date().toISOString(),
    };
  }
}

