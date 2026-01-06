/**
 * Python FastAPI 服务 API 封装
 */

import { useGet, usePost, usePut, useDelete, type ApiResponse } from '~/composables/useApi';

const config = useRuntimeConfig();
const baseUrl = config.public.pythonApiUrl;

export interface Item {
  id: string;
  name: string;
  description?: string;
  price?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateItemDto {
  name: string;
  description?: string;
  price?: number;
}

export interface UpdateItemDto {
  name?: string;
  description?: string;
  price?: number;
}

/**
 * 获取所有 items
 */
export async function getItems(): Promise<ApiResponse<Item[]>> {
  return useGet<Item[]>(`${baseUrl}/api/v1/items`);
}

/**
 * 获取单个 item
 */
export async function getItem(id: string): Promise<ApiResponse<Item>> {
  return useGet<Item>(`${baseUrl}/api/v1/items/${id}`);
}

/**
 * 创建 item
 */
export async function createItem(
  data: CreateItemDto,
): Promise<ApiResponse<Item>> {
  return usePost<Item>(`${baseUrl}/api/v1/items`, data);
}

/**
 * 更新 item
 */
export async function updateItem(
  id: string,
  data: UpdateItemDto,
): Promise<ApiResponse<Item>> {
  return usePut<Item>(`${baseUrl}/api/v1/items/${id}`, data);
}

/**
 * 删除 item
 */
export async function deleteItem(id: string): Promise<ApiResponse<void>> {
  return useDelete<void>(`${baseUrl}/api/v1/items/${id}`);
}
