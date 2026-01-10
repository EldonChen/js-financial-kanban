/**
 * Node.js 服务 API 封装
 */

import { createApiClient } from '../client'
import type { ApiClient } from '../client'
import type { Item, CreateItemDto, UpdateItemDto, NodeItem } from '../types'

/**
 * 将 Node.js 服务的 Item（使用 _id）转换为统一的 Item（使用 id）
 */
function transformNodeItem(nodeItem: NodeItem): Item {
  return {
    id: nodeItem._id,
    name: nodeItem.name,
    description: nodeItem.description,
    price: nodeItem.price,
    createdAt: nodeItem.createdAt,
    updatedAt: nodeItem.updatedAt,
  }
}

export class NodeService {
  private client: ApiClient
  private basePath = '/api/v1/items'

  constructor(apiUrl: string) {
    this.client = createApiClient(apiUrl)
  }

  /**
   * 获取所有 items
   */
  async getItems(): Promise<Item[]> {
    const response = await this.client.get<NodeItem[]>(this.basePath)
    return response.data.map(transformNodeItem)
  }

  /**
   * 获取单个 item
   */
  async getItem(id: string): Promise<Item> {
    const response = await this.client.get<NodeItem>(`${this.basePath}/${id}`)
    return transformNodeItem(response.data)
  }

  /**
   * 创建 item
   */
  async createItem(data: CreateItemDto): Promise<Item> {
    const response = await this.client.post<NodeItem>(this.basePath, data)
    return transformNodeItem(response.data)
  }

  /**
   * 更新 item
   */
  async updateItem(id: string, data: UpdateItemDto): Promise<Item> {
    const response = await this.client.put<NodeItem>(`${this.basePath}/${id}`, data)
    return transformNodeItem(response.data)
  }

  /**
   * 删除 item
   */
  async deleteItem(id: string): Promise<void> {
    await this.client.delete(`${this.basePath}/${id}`)
  }
}

/**
 * 创建 Node.js 服务实例
 */
export function createNodeService(apiUrl: string): NodeService {
  return new NodeService(apiUrl)
}
