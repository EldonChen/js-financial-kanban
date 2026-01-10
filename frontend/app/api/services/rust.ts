/**
 * Rust 服务 API 封装
 */

import { createApiClient } from '../client'
import type { ApiClient } from '../client'
import type { Item, CreateItemDto, UpdateItemDto, RustItem } from '../types'

/**
 * 将 Rust 服务的 Item（使用 created_at）转换为统一的 Item（使用 createdAt）
 */
function transformRustItem(rustItem: RustItem): Item {
  return {
    id: rustItem.id,
    name: rustItem.name,
    description: rustItem.description,
    price: rustItem.price,
    createdAt: rustItem.created_at,
    updatedAt: rustItem.updated_at,
  }
}

export class RustService {
  private client: ApiClient
  private basePath = '/api/v1/items'

  constructor(apiUrl: string) {
    this.client = createApiClient(apiUrl)
  }

  /**
   * 获取所有 items
   */
  async getItems(): Promise<Item[]> {
    const response = await this.client.get<RustItem[]>(this.basePath)
    return response.data.map(transformRustItem)
  }

  /**
   * 获取单个 item
   */
  async getItem(id: string): Promise<Item> {
    const response = await this.client.get<RustItem>(`${this.basePath}/${id}`)
    return transformRustItem(response.data)
  }

  /**
   * 创建 item
   */
  async createItem(data: CreateItemDto): Promise<Item> {
    const response = await this.client.post<RustItem>(this.basePath, data)
    return transformRustItem(response.data)
  }

  /**
   * 更新 item
   */
  async updateItem(id: string, data: UpdateItemDto): Promise<Item> {
    const response = await this.client.put<RustItem>(`${this.basePath}/${id}`, data)
    return transformRustItem(response.data)
  }

  /**
   * 删除 item
   */
  async deleteItem(id: string): Promise<void> {
    await this.client.delete(`${this.basePath}/${id}`)
  }
}

/**
 * 创建 Rust 服务实例
 */
export function createRustService(apiUrl: string): RustService {
  return new RustService(apiUrl)
}
