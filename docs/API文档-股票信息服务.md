# API 文档 - 股票信息服务

> **服务名称**：Stock Info Service  
> **服务端口**：8001  
> **API 版本**：v1  
> **基础路径**：`/api/v1`

## 概述

股票信息服务提供股票基本信息的查询、更新和管理功能，支持多数据源（akshare、yfinance、easyquotation 等）和多市场（A 股、港股、美股）。

## 数据源支持

### 第一优先级数据源（免费优先、无需认证）

- **akshare**：A 股主数据源，支持全量股票列表
- **yfinance**：美股/港股主数据源，支持全量股票列表
- **easyquotation**：A 股实时行情补充（可选）

### 第二优先级数据源（需要注册 API Key，可选）

- **Tushare**：A 股备用数据源（需要 token）
- **IEX Cloud**：美股备用数据源（需要 API Key）
- **Alpha Vantage**：美股备用数据源（需要 API Key）

## 股票查询接口

### GET /api/v1/stocks

获取股票列表（支持筛选和分页）。

**查询参数**：
- `ticker` (string, 可选) - 股票代码（精确匹配）
- `name` (string, 可选) - 股票名称（模糊查询）
- `market` (string, 可选) - 市场（精确匹配，如 NASDAQ、SSE、SZSE）
- `market_type` (string, 可选) - 市场类型（精确匹配：A股、港股、美股）
- `sector` (string, 可选) - 行业板块（精确匹配）
- `page` (int, 可选) - 页码（默认 1）
- `page_size (int, 可选) - 每页数量（默认 20，最大 100）

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "507f1f77bcf86cd799439011",
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "market": "NASDAQ",
        "market_type": "美股",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "currency": "USD",
        "exchange": "NMS",
        "country": "United States",
        "market_cap": 3000000000000,
        "pe_ratio": 30.5,
        "pb_ratio": 45.2,
        "dividend_yield": 0.005,
        "data_source": "yfinance",
        "last_updated": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### GET /api/v1/stocks/{ticker}

获取单个股票的详细信息。

**路径参数**：
- `ticker` (string, 必填) - 股票代码

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "market": "NASDAQ",
    "market_type": "美股",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "currency": "USD",
    "exchange": "NMS",
    "country": "United States",
    "data_source": "yfinance",
    "last_updated": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

## 股票更新接口

### POST /api/v1/stocks/{ticker}/update

手动触发单个股票的更新（支持多数据源）。

**路径参数**：
- `ticker` (string, 必填) - 股票代码

**查询参数**：
- `market` (string, 可选) - 市场类型（用于选择合适的数据源：A股、港股、美股）
- `preferred_provider` (string, 可选) - 首选数据源（akshare、yfinance、easyquotation等）

**数据源选择逻辑**：
- 如果指定了 `preferred_provider`，优先使用该数据源
- 如果指定了 `market`，会根据市场类型自动选择合适的数据源
  - A股：优先使用 akshare
  - 美股/港股：优先使用 yfinance
- 否则，按优先级自动选择数据源（自动容错）

**响应示例**：
```json
{
  "code": 200,
  "message": "股票 AAPL 更新成功",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "data_source": "yfinance",
    "last_updated": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**：
```bash
# 使用默认数据源（自动选择）
curl -X POST "http://localhost:8001/api/v1/stocks/AAPL/update"

# 指定市场类型
curl -X POST "http://localhost:8001/api/v1/stocks/000001/update?market=A股"

# 指定首选数据源
curl -X POST "http://localhost:8001/api/v1/stocks/AAPL/update?preferred_provider=yfinance"
```

### POST /api/v1/stocks/fetch-all

从数据源拉取全部股票列表并保存到数据库（SSE 实时推送进度，支持多数据源）。

**查询参数**：
- `market` (string, 可选) - 市场类型（用于选择合适的数据源：A股、港股、美股）
- `delay` (float, 可选) - 每次抓取之间的延迟（秒，默认 1.0 秒，范围 0.0-10.0）

**响应格式**：
使用 Server-Sent Events (SSE) 实时推送进度，客户端需要使用 EventSource API 接收。

**进度信息格式**：
```json
{
  "stage": "fetching",  // 阶段：init/fetching/saving/completed/error
  "message": "正在抓取股票信息... (10/100)",
  "progress": 5,  // 进度百分比（0-100）
  "total": 100,
  "current": 10,
  "fetch_success": 8,
  "fetch_failed": 2
}
```

**使用示例**：
```javascript
// JavaScript (EventSource)
const eventSource = new EventSource('/api/v1/stocks/fetch-all?market=A股&delay=1.0');

eventSource.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(progress.message);
  console.log(`进度: ${progress.progress}%`);
  
  if (progress.stage === 'completed') {
    console.log('完成！', progress.result);
    eventSource.close();
  } else if (progress.stage === 'error') {
    console.error('错误：', progress.message);
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('SSE 连接错误', error);
  eventSource.close();
};
```

### POST /api/v1/stocks/update-all

手动触发所有股票的更新。

**响应示例**：
```json
{
  "code": 200,
  "message": "批量更新完成：总数 100，成功 95，失败 5",
  "data": {
    "total": 100,
    "success": 95,
    "failed": 5,
    "results": [
      {"ticker": "AAPL", "status": "success"},
      {"ticker": "GOOGL", "status": "success"},
      {"ticker": "INVALID", "status": "failed"}
    ]
  }
}
```

### POST /api/v1/stocks/batch-update

批量手动更新指定股票。

**请求体**：
```json
{
  "tickers": ["AAPL", "GOOGL", "MSFT"]
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "批量更新完成：总数 3，成功 3，失败 0",
  "data": {
    "total": 3,
    "success": 3,
    "failed": 0,
    "results": [
      {"ticker": "AAPL", "status": "success"},
      {"ticker": "GOOGL", "status": "success"},
      {"ticker": "MSFT", "status": "success"}
    ]
  }
}
```

## 数据源管理接口

### GET /api/v1/providers/status

获取数据源状态信息。

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_providers": 3,
    "providers": {
      "akshare": {
        "name": "akshare",
        "supported_markets": ["A股", "港股", "美股"],
        "priority": 1
      },
      "yfinance": {
        "name": "yfinance",
        "supported_markets": ["美股", "港股"],
        "priority": 1
      },
      "easyquotation": {
        "name": "easyquotation",
        "supported_markets": ["A股"],
        "priority": 1
      }
    },
    "market_coverage": {
      "A股": ["akshare", "easyquotation"],
      "港股": ["yfinance", "akshare"],
      "美股": ["yfinance", "akshare"]
    }
  }
}
```

## 统一响应格式

所有 API 响应遵循以下格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

**错误响应**：
```json
{
  "code": 404,
  "message": "股票 AAPL 不存在",
  "data": null
}
```

## 数据模型

### Stock（股票）

```typescript
interface Stock {
  id: string;                    // 股票 ID
  ticker: string;                // 股票代码（必填）
  name: string;                  // 股票名称（必填）
  market?: string;               // 市场（可选）
  market_type?: string;          // 市场类型（可选：A股、港股、美股）
  sector?: string;               // 行业板块（可选）
  industry?: string;             // 细分行业（可选）
  currency?: string;             // 货币（可选）
  exchange?: string;             // 交易所代码（可选）
  country?: string;              // 国家（可选）
  market_cap?: number;           // 市值（可选）
  pe_ratio?: number;             // 市盈率（可选）
  pb_ratio?: number;             // 市净率（可选）
  dividend_yield?: number;        // 股息率（可选）
  listing_date?: string;         // 上市日期（可选，ISO 8601 格式）
  data_source: string;           // 数据来源（必填）
  last_updated: string;           // 最后更新时间（ISO 8601 格式）
  created_at: string;             // 创建时间（ISO 8601 格式）
  updated_at: string;             // 更新时间（ISO 8601 格式）
}
```

## 错误码

- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器内部错误

## 注意事项

1. **数据源选择**：
   - 系统会自动按市场类型选择合适的数据源
   - 主数据源失败时会自动切换到备用数据源
   - 可以通过 `preferred_provider` 参数手动指定数据源

2. **数据字段**：
   - 不同数据源返回的字段可能不同
   - 系统会自动映射和清洗字段，统一格式
   - 某些字段可能为 `null`（取决于数据源）

3. **请求频率**：
   - 建议控制请求频率，避免触发数据源限制
   - `fetch-all` 接口会自动添加延迟（默认 1 秒）

4. **实时进度**：
   - `fetch-all` 接口使用 SSE 推送实时进度
   - 客户端需要使用 EventSource API 接收

---

**最后更新**：2024年  
**文档版本**：v1.0
