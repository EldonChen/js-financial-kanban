/**
 * 数据转换工具函数
 */

import { PythonItem } from '../../clients/python.client';
import { NodeItem } from '../../clients/node.client';
import { RustItem } from '../../clients/rust.client';

/**
 * 统一的 Item 格式
 */
export interface UnifiedItem {
  id: string;
  name: string;
  description?: string;
  price?: number;
  source: 'python' | 'node' | 'rust';
  created_at: string;
  updated_at: string;
}

/**
 * 将 Python Item 转换为统一格式
 */
export function transformPythonItem(item: PythonItem): UnifiedItem {
  return {
    id: item.id,
    name: item.name,
    description: item.description,
    price: item.price,
    source: 'python',
    created_at: item.created_at,
    updated_at: item.updated_at,
  };
}

/**
 * 将 Node Item 转换为统一格式
 */
export function transformNodeItem(item: NodeItem): UnifiedItem {
  return {
    id: item._id,
    name: item.name,
    description: item.description,
    price: item.price,
    source: 'node',
    created_at: item.createdAt,
    updated_at: item.updatedAt,
  };
}

/**
 * 将 Rust Item 转换为统一格式
 */
export function transformRustItem(item: RustItem): UnifiedItem {
  return {
    id: item.id,
    name: item.name,
    description: item.description,
    price: item.price,
    source: 'rust',
    created_at: item.created_at,
    updated_at: item.updated_at,
  };
}

/**
 * 合并并去重 Items（按 name 去重，保留最新的）
 */
export function mergeAndDeduplicateItems(items: UnifiedItem[]): UnifiedItem[] {
  const itemMap = new Map<string, UnifiedItem>();

  for (const item of items) {
    const existing = itemMap.get(item.name);
    if (
      !existing ||
      new Date(item.updated_at) > new Date(existing.updated_at)
    ) {
      itemMap.set(item.name, item);
    }
  }

  return Array.from(itemMap.values());
}

/**
 * 按更新时间排序 Items（最新的在前）
 */
export function sortItemsByUpdatedAt(items: UnifiedItem[]): UnifiedItem[] {
  return [...items].sort(
    (a, b) =>
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
  );
}
