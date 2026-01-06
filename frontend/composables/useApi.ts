/**
 * 统一 API 调用封装
 * 使用 Fetch API 进行 HTTP 请求
 */

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface ApiError {
  code: number;
  message: string;
  data: null;
}

/**
 * 通用 API 请求函数
 */
export async function useApi<T = any>(
  url: string,
  options: RequestInit = {},
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        code: response.status,
        message: response.statusText || '请求失败',
        data: null,
      }));
      throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    const data: ApiResponse<T> = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('网络请求失败');
  }
}

/**
 * GET 请求
 */
export async function useGet<T = any>(url: string): Promise<ApiResponse<T>> {
  return useApi<T>(url, { method: 'GET' });
}

/**
 * POST 请求
 */
export async function usePost<T = any>(
  url: string,
  body: any,
): Promise<ApiResponse<T>> {
  return useApi<T>(url, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * PUT 请求
 */
export async function usePut<T = any>(
  url: string,
  body: any,
): Promise<ApiResponse<T>> {
  return useApi<T>(url, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/**
 * DELETE 请求
 */
export async function useDelete<T = any>(
  url: string,
): Promise<ApiResponse<T>> {
  return useApi<T>(url, { method: 'DELETE' });
}
