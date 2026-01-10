"""股票路由."""

import json
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from app.schemas.stock import (
    StockQueryParams,
    BatchUpdateRequest,
)
from app.schemas.response import success_response, error_response
from app.services.stock_service import get_stock_service
from app.database import get_database

router = APIRouter(prefix="/api/v1/stocks", tags=["stocks"])


@router.get("", response_model=dict)
async def get_stocks(
    ticker: str | None = Query(None, description="股票代码（精确匹配）"),
    name: str | None = Query(None, description="股票名称（模糊查询）"),
    market: str | None = Query(None, description="市场（精确匹配）"),
    market_type: str | None = Query(None, description="市场类型（精确匹配：A股、港股、美股）"),
    sector: str | None = Query(None, description="行业板块（精确匹配）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """获取股票列表（支持筛选和分页）."""
    try:
        params = StockQueryParams(
            ticker=ticker,
            name=name,
            market=market,
            market_type=market_type,
            sector=sector,
            page=page,
            page_size=page_size,
        )
        stock_service = get_stock_service(db=get_database())
        result = await stock_service.query_stocks(params)
        return success_response(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取股票列表失败: {str(e)}",
        )


@router.get("/{ticker}", response_model=dict)
async def get_stock(ticker: str):
    """获取单个股票的详细信息."""
    try:
        stock_service = get_stock_service(db=get_database())
        stock = await stock_service.get_stock_by_ticker(ticker)
        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"股票 {ticker} 不存在",
            )
        return success_response(data=stock)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取股票信息失败: {str(e)}",
        )


@router.post("/{ticker}/update", response_model=dict)
async def update_stock(
    ticker: str,
    market: str | None = Query(None, description="市场类型（可选，用于选择合适的数据源：A股、港股、美股）"),
    preferred_provider: str | None = Query(None, description="首选数据源（可选：akshare、yfinance、easyquotation等）"),
):
    """手动触发单个股票的更新（支持多数据源）.
    
    注意：如果股票不存在于数据库中，会先验证 ticker 是否有效。
    只有有效的股票数据（至少包含 name 字段）才会被保存到数据库。
    
    数据源选择逻辑：
    - 如果指定了 preferred_provider，优先使用该数据源
    - 如果指定了 market，会根据市场类型自动选择合适的数据源
    - 否则，按优先级自动选择数据源（自动容错）
    """
    try:
        stock_service = get_stock_service(db=get_database())
        
        # 检查数据库中是否已存在该股票
        existing_stock = await stock_service.get_stock_by_ticker(ticker)
        
        # 如果股票不存在，需要验证数据有效性
        # 如果股票已存在，允许更新（不需要额外验证）
        validate_if_new = existing_stock is None
        
        # 执行更新（使用多数据源方法）
        updated_stock = await stock_service.update_stock_from_provider(
            ticker=ticker,
            market=market,
            preferred_provider=preferred_provider,
            allow_create=True,
            validate_if_new=validate_if_new,
        )
        
        if updated_stock is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"股票 {ticker} 不存在或数据无效，无法更新",
            )
        return success_response(data=updated_stock, message=f"股票 {ticker} 更新成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新股票失败: {str(e)}",
        )


@router.post("/update-all", response_model=dict)
async def update_all_stocks():
    """手动触发所有股票的更新."""
    try:
        stock_service = get_stock_service(db=get_database())
        result = await stock_service.update_all_stocks()
        return success_response(
            data=result,
            message=f"批量更新完成：总数 {result['total']}，成功 {result['success']}，失败 {result['failed']}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量更新股票失败: {str(e)}",
        )


@router.post("/batch-update", response_model=dict)
async def batch_update_stocks(request: BatchUpdateRequest):
    """批量手动更新股票."""
    try:
        stock_service = get_stock_service(db=get_database())
        result = await stock_service.batch_update_stocks(request.tickers)
        return success_response(
            data=result,
            message=f"批量更新完成：总数 {result['total']}，成功 {result['success']}，失败 {result['failed']}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量更新股票失败: {str(e)}",
        )


@router.post("/fetch-all")
async def fetch_all_stocks(
    market: str | None = Query(None, description="市场类型（可选，用于选择合适的数据源：A股、港股、美股）"),
    delay: float = Query(1.0, ge=0.0, le=10.0, description="每次抓取之间的延迟（秒），默认 1.0 秒")
):
    """从数据源拉取全部股票列表并保存到数据库（SSE 实时推送进度，支持多数据源）.
    
    此接口使用 Server-Sent Events (SSE) 实时推送拉取进度，包括：
    1. 获取股票代码列表的进度
    2. 批量抓取股票信息的进度
    3. 保存股票数据到数据库的进度
    
    数据源选择逻辑：
    - 如果指定了 market，会根据市场类型自动选择合适的数据源
    - A股：优先使用 akshare
    - 美股/港股：优先使用 yfinance
    - 否则，按优先级自动选择数据源（自动容错）
    
    响应格式为 SSE 流，客户端可以通过 EventSource API 接收实时进度更新。
    
    注意：此操作可能需要较长时间，建议使用 SSE 客户端接收进度更新。
    """
    import asyncio
    
    async def event_generator():
        """SSE 事件生成器."""
        try:
            stock_service = get_stock_service(db=get_database())
            
            # 创建进度队列
            progress_queue = asyncio.Queue()
            task_done = False
            error_occurred = False
            
            async def progress_handler(progress_data: dict):
                """进度处理器，将数据添加到队列."""
                await progress_queue.put(progress_data)
            
            async def fetch_task():
                """异步拉取任务."""
                nonlocal task_done, error_occurred
                try:
                    # 使用新的多数据源方法
                    await stock_service.fetch_and_save_all_stocks_from_provider(
                        market=market,
                        delay=delay,
                        progress_callback=progress_handler
                    )
                except Exception as e:
                    error_occurred = True
                    error_data = {
                        "stage": "error",
                        "message": f"拉取失败: {str(e)}",
                        "progress": 0,
                    }
                    await progress_queue.put(error_data)
                finally:
                    task_done = True
                    # 发送结束标记
                    await progress_queue.put(None)
            
            # 启动拉取任务
            task = asyncio.create_task(fetch_task())
            
            # 持续发送进度更新
            while True:
                try:
                    # 从队列获取进度数据，设置超时避免阻塞
                    progress_data = await asyncio.wait_for(
                        progress_queue.get(), timeout=0.5
                    )
                    
                    # None 表示任务完成
                    if progress_data is None:
                        break
                    
                    # 发送 SSE 数据
                    data = json.dumps(progress_data, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                    
                except asyncio.TimeoutError:
                    # 超时检查任务是否完成
                    if task_done:
                        # 处理队列中剩余的数据
                        while not progress_queue.empty():
                            try:
                                progress_data = progress_queue.get_nowait()
                                if progress_data is not None:
                                    data = json.dumps(progress_data, ensure_ascii=False)
                                    yield f"data: {data}\n\n"
                            except asyncio.QueueEmpty:
                                break
                        break
                    continue
            
            # 等待任务完成
            await task
            
        except Exception as e:
            # 发送错误信息
            error_data = {
                "stage": "error",
                "message": f"拉取全部股票列表失败: {str(e)}",
                "progress": 0,
            }
            data = json.dumps(error_data, ensure_ascii=False)
            yield f"data: {data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


@router.delete("/all", response_model=dict)
async def delete_all_stocks():
    """删除所有股票."""
    try:
        stock_service = get_stock_service(db=get_database())
        result = await stock_service.delete_all_stocks()
        return success_response(
            data=result,
            message=f"已删除所有股票，共删除 {result['deleted_count']} 条记录",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除所有股票失败: {str(e)}",
        )


@router.delete("/{ticker}", response_model=dict)
async def delete_stock(ticker: str):
    """删除指定股票."""
    try:
        stock_service = get_stock_service(db=get_database())
        # 先检查股票是否存在
        stock = await stock_service.get_stock_by_ticker(ticker)
        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"股票 {ticker} 不存在",
            )
        # 删除股票
        deleted = await stock_service.delete_stock(ticker)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除股票 {ticker} 失败",
            )
        return success_response(
            data={"ticker": ticker},
            message=f"股票 {ticker} 删除成功",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除股票失败: {str(e)}",
        )
