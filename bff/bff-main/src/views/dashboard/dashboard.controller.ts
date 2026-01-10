import { Controller, Get } from '@nestjs/common';
import { DashboardService } from './dashboard.service';

@Controller('views/dashboard')
export class DashboardController {
  constructor(private readonly dashboardService: DashboardService) {}

  @Get()
  async getDashboard() {
    return this.dashboardService.getDashboardData();
  }
}
