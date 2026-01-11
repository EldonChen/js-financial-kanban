/**
 * API 服务 Composables
 * 提供便捷的 API 服务访问
 */

import { createNodeService, type NodeService } from '~/api/services/node'
import { createPythonService, type PythonService } from '~/api/services/python'
import { createRustService, type RustService } from '~/api/services/rust'
import { createStocksService, type StocksService } from '~/api/services/stocks'

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
