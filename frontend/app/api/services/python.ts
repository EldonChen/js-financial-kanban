/**
 * Python 服务 API 封装
 */

import { createApiClient } from '../client'
import type { ApiClient } from '../client'
import type { Item, CreateItemDto, UpdateItemDto, PythonItem } from '../types'

/**
 * 将 Python 服务的 Item（使用 created_at）转换为统一的 Item（使用 createdAt）
 */
function transformPythonItem(pythonItem: PythonItem): Item {
  return {
    id: pythonItem.id,
    name: pythonItem.name,
    description: pythonItem.description,
    price: pythonItem.price,
    createdAt: pythonItem.created_at,
    updatedAt: pythonItem.updated_at,
  }
}

export class PythonService {
  private client: ApiClient
  private basePath = '/api/v1/items'

  constructor(apiUrl: string) {
    this.client = createApiClient(apiUrl)
  }

  /**
   * 获取所有 items
   */
  async getItems(): Promise<Item[]> {
    const response = await this.client.get<PythonItem[]>(this.basePath)
    return response.data.map(transformPythonItem)
  }

  /**
   * 获取单个 item
   */
  async getItem(id: string): Promise<Item> {
    const response = await this.client.get<PythonItem>(`${this.basePath}/${id}`)
    return transformPythonItem(response.data)
  }

  /**
   * 创建 item
   */
  async createItem(data: CreateItemDto): Promise<Item> {
    const response = await this.client.post<PythonItem>(this.basePath, data)
    return transformPythonItem(response.data)
  }

  /**
   * 更新 item
   */
  async updateItem(id: string, data: UpdateItemDto): Promise<Item> {
    const response = await this.client.put<PythonItem>(`${this.basePath}/${id}`, data)
    return transformPythonItem(response.data)
  }

  /**
   * 删除 item
   */
  async deleteItem(id: string): Promise<void> {
    await this.client.delete(`${this.basePath}/${id}`)
  }
}

/**
 * 创建 Python 服务实例
 */
export function createPythonService(apiUrl: string): PythonService {
  return new PythonService(apiUrl)
}
