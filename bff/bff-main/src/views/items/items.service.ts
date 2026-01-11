import { Injectable } from '@nestjs/common';
import { PythonClient } from '../../clients/python.client';
import { NodeClient } from '../../clients/node.client';
import { RustClient } from '../../clients/rust.client';
import { allSettledWithNull } from '../../common/utils/promise.util';
import {
  transformPythonItem,
  transformNodeItem,
  transformRustItem,
  mergeAndDeduplicateItems,
  sortItemsByUpdatedAt,
  UnifiedItem,
} from '../../common/utils/transform.util';

@Injectable()
export class ItemsService {
  constructor(
    private readonly pythonClient: PythonClient,
    private readonly nodeClient: NodeClient,
    private readonly rustClient: RustClient,
  ) {}

  async getAllItems(): Promise<UnifiedItem[]> {
    // 并行获取所有服务的 items，允许部分失败
    const [pythonItems, nodeItems, rustItems] = await allSettledWithNull([
      this.pythonClient.getItems(),
      this.nodeClient.getItems(),
      this.rustClient.getItems(),
    ] as const);

    // 转换数据格式
    const unifiedItems: UnifiedItem[] = [];

    if (pythonItems) {
      unifiedItems.push(...pythonItems.map(transformPythonItem));
    }

    if (nodeItems) {
      unifiedItems.push(...nodeItems.map(transformNodeItem));
    }

    if (rustItems) {
      unifiedItems.push(...rustItems.map(transformRustItem));
    }

    // 合并去重并排序
    const merged = mergeAndDeduplicateItems(unifiedItems);
    return sortItemsByUpdatedAt(merged);
  }
}
