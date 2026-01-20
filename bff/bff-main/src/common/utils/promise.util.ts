/**
 * Promise 工具函数
 */

/**
 * 并行执行多个 Promise，允许部分失败
 * @param promises Promise 数组（支持不同类型）
 * @returns 结果数组，失败的项为 null
 */
export async function allSettledWithNull<
  T extends readonly unknown[],
>(promises: { [K in keyof T]: Promise<T[K]> }): Promise<{
  [K in keyof T]: T[K] | null;
}> {
  const results = await Promise.allSettled(promises);
  return results.map((result) =>
    result.status === 'fulfilled' ? result.value : null,
  ) as { [K in keyof T]: T[K] | null };
}

/**
 * 带超时的 Promise
 * @param promise 原始 Promise
 * @param timeout 超时时间（毫秒）
 * @returns Promise 结果或抛出超时错误
 */
export function withTimeout<T>(
  promise: Promise<T>,
  timeout: number,
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), timeout),
    ),
  ]);
}

/**
 * 重试 Promise
 * @param fn 返回 Promise 的函数
 * @param retries 重试次数
 * @param delay 重试延迟（毫秒）
 * @returns Promise 结果
 */
export async function retry<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000,
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, delay));
      return retry(fn, retries - 1, delay);
    }
    throw error;
  }
}
