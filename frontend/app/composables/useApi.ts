/**
 * API 服务 Composables
 * 提供便捷的 API 服务访问
 */

import type { DashboardService } from '~/api/services/dashboard'
import type { NodeService } from '~/api/services/node'
import type { PythonService } from '~/api/services/python'
import type { RustService } from '~/api/services/rust'
import type { StocksService } from '~/api/services/stocks'
import { createDashboardService } from '~/api/services/dashboard'
import { createNodeService } from '~/api/services/node'
import { createPythonService } from '~/api/services/python'
import { createRustService } from '~/api/services/rust'
import { createStocksService } from '~/api/services/stocks'

/**
 * 使用 Node.js 服务
 */
export function useNodeService(): NodeService {
  const config = useRuntimeConfig()
  return createNodeService(config.public.nodeApiUrl)
}

/**
 * 使用 Python 服务
 */
export function usePythonService(): PythonService {
  const config = useRuntimeConfig()
  return createPythonService(config.public.pythonApiUrl)
}

/**
 * 使用 Rust 服务
 */
export function useRustService(): RustService {
  const config = useRuntimeConfig()
  return createRustService(config.public.rustApiUrl)
}

/**
 * 使用 Stocks 服务
 */
export function useStocksService(): StocksService {
  const config = useRuntimeConfig()
  return createStocksService(config.public.bffApiUrl)
}

/**
 * 使用 Dashboard 服务
 */
export function useDashboardService(): DashboardService {
  const config = useRuntimeConfig()
  return createDashboardService(config.public.bffApiUrl)
}
