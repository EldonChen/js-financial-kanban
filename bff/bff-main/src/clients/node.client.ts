import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosResponse } from 'axios';

export interface NodeItem {
  _id: string;
  name: string;
  description?: string;
  price?: number;
  createdAt: string;
  updatedAt: string;
}

export interface NodeApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

@Injectable()
export class NodeClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl = process.env.NODE_SERVICE_URL || 'http://localhost:3000';
  }

  /**
   * 获取所有 items
   */
  async getItems(): Promise<NodeItem[]> {
    try {
      const response: AxiosResponse<NodeApiResponse<NodeItem[]>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/items`),
        );
      return response.data.data || [];
    } catch (error) {
      console.error('NodeClient.getItems error:', error);
      throw error;
    }
  }

  /**
   * 获取单个 item
   */
  async getItem(id: string): Promise<NodeItem | null> {
    try {
      const response: AxiosResponse<NodeApiResponse<NodeItem>> =
        await firstValueFrom(
          this.httpService.get(`${this.baseUrl}/api/v1/items/${id}`),
        );
      return response.data.data || null;
    } catch (error) {
      console.error(`NodeClient.getItem(${id}) error:`, error);
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
  }): Promise<NodeItem> {
    try {
      const response: AxiosResponse<NodeApiResponse<NodeItem>> =
        await firstValueFrom(
          this.httpService.post(`${this.baseUrl}/api/v1/items`, data),
        );
      return response.data.data;
    } catch (error) {
      console.error('NodeClient.createItem error:', error);
      throw error;
    }
  }

  /**
   * 更新 item
   */
  async updateItem(
    id: string,
    data: { name?: string; description?: string; price?: number },
  ): Promise<NodeItem> {
    try {
      const response: AxiosResponse<NodeApiResponse<NodeItem>> =
        await firstValueFrom(
          this.httpService.put(`${this.baseUrl}/api/v1/items/${id}`, data),
        );
      return response.data.data;
    } catch (error) {
      console.error(`NodeClient.updateItem(${id}) error:`, error);
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
      console.error(`NodeClient.deleteItem(${id}) error:`, error);
      throw error;
    }
  }
}
