import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosResponse } from 'axios';

export interface PythonItem {
  id: string;
  name: string;
  description?: string;
  price?: number;
  created_at: string;
  updated_at: string;
}

export interface PythonApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

@Injectable()
export class PythonClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';
  }

  /**
   * 获取所有 items
   */
  async getItems(): Promise<PythonItem[]> {
    try {
      const response: AxiosResponse<PythonApiResponse<PythonItem[]>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/items`),
        );
      return response.data.data || [];
    } catch (error) {
      console.error('PythonClient.getItems error:', error);
      throw error;
    }
  }

  /**
   * 获取单个 item
   */
  async getItem(id: string): Promise<PythonItem | null> {
    try {
      const response: AxiosResponse<PythonApiResponse<PythonItem>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/items/${id}`),
        );
      return response.data.data || null;
    } catch (error) {
      console.error(`PythonClient.getItem(${id}) error:`, error);
      throw error;
    }
  }

  /**
   * 创建 item
   */
  async createItem(data: {
    name: string;
    description?: string;
    price?: number;
  }): Promise<PythonItem> {
    try {
      const response: AxiosResponse<PythonApiResponse<PythonItem>> =
        await firstValueFrom(
          this.httpService.post(`${this.baseUrl}/api/v1/items`, data),
        );
      return response.data.data;
    } catch (error) {
      console.error('PythonClient.createItem error:', error);
      throw error;
    }
  }

  /**
   * 更新 item
   */
  async updateItem(
    id: string,
    data: { name?: string; description?: string; price?: number },
  ): Promise<PythonItem> {
    try {
      const response: AxiosResponse<PythonApiResponse<PythonItem>> =
        await firstValueFrom(
          this.httpService.put(`${this.baseUrl}/api/v1/items/${id}`, data),
        );
      return response.data.data;
    } catch (error) {
      console.error(`PythonClient.updateItem(${id}) error:`, error);
      throw error;
    }
  }

  /**
   * 删除 item
   */
  async deleteItem(id: string): Promise<void> {
    try {
      await firstValueFrom(
        this.httpService.delete(`${this.baseUrl}/api/v1/items/${id}`),
      );
    } catch (error) {
      console.error(`PythonClient.deleteItem(${id}) error:`, error);
      throw error;
    }
  }
}
