"""历史数据路由."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.database import get_database
from app.schemas.historical_data import (
    DeleteKlineDataResponse,
    HistoricalDataListResponse,
    HistoricalDataPageResponse,
    KlineDataResponse,
    StatisticsResponse,
    UpdateKlineDataResponse,
)
from app.schemas.response import error_response, success_response
from app.services.historical_data.historical_data_service import (
    HistoricalDataService,
)
from app.services.stock_service import get_stock_service

router = APIRouter(prefix="/api/v1/historical-data", tags=["historical-data"])
logger = logging.getLogger(__name__)


def get_historical_data_service():
    """获取历史数据服务实例."""
    return HistoricalDataService(db=get_database())


@router.get("/{ticker}", response_model=dict)
async def get_kline_data(
    ticker: str,
    period: str = Query("1d", description="时间周期（1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M）"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="返回数量限制"),
    page: Optional[int] = Query(None, ge=1, description="页码（分页模式）"),
    page_size: Optional[int] = Query(None, ge=1, le=1000, description="每页条数（分页模式）"),
):
    """获取历史K线数据.

    支持两种模式：
    1. 列表模式：不传 page/page_size 参数，返回列表格式
    2. 分页模式：传 page/page_size 参数，返回分页格式
    """
    try:
        service = get_historical_data_service()

        # 解析日期
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # 查询数据
        kline_data = await service.query_kline_data(
            ticker=ticker,
            period=period,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
        )

        # 判断是分页模式还是列表模式
        if page is not None or page_size is not None:
            # 分页模式
            page = page or 1
            page_size = page_size or 100

            total = len(kline_data)
            total_pages = (total + page_size - 1) // page_size

            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            items = kline_data[start_idx:end_idx]

            response_data = HistoricalDataPageResponse(
                items=[KlineDataResponse(**item) for item in items],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )
        else:
            # 列表模式
            response_data = HistoricalDataListResponse(
                ticker=ticker,
                period=period,
                count=len(kline_data),
                data=[KlineDataResponse(**item) for item in kline_data],
            )

        return success_response(data=response_data.model_dump())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数错误: {str(e)}",
        )
    except Exception as e:
        logger.error(f"获取历史K线数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史K线数据失败: {str(e)}",
        )


@router.get("/{ticker}/statistics", response_model=dict)
async def get_kline_data_statistics(
    ticker: str,
    period: str = Query("1d", description="时间周期"),
):
    """获取历史K线数据统计信息."""
    try:
        service = get_historical_data_service()
        statistics = await service.get_kline_data_statistics(ticker=ticker, period=period)

        response_data = StatisticsResponse(**statistics)
        return success_response(data=response_data.model_dump())

    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}",
        )


@router.post("/{ticker}/update", response_model=dict)
async def update_kline_data(
    ticker: str,
    period: str = Query("1d", description="时间周期"),
    incremental: bool = Query(True, description="是否增量更新（True: 只更新缺失数据，False: 全量更新）"),
    data_source: Optional[str] = Query(None, description="数据源（可选，自动选择）"),
):
    """更新历史K线数据.

    - incremental=True: 增量更新，只获取缺失的数据
    - incremental=False: 全量更新，获取最近1年的数据
    """
    try:
        # 获取股票市场信息
        stock_service = get_stock_service(db=get_database())
        stock = await stock_service.get_stock_by_ticker(ticker)
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"股票 {ticker} 不存在",
            )

        market = stock.get("market", "NASDAQ")
        service = get_historical_data_service()

        # 执行更新
        if incremental:
            result = await service.update_kline_data_incremental(
                ticker=ticker,
                market=market,
                period=period,
                data_source=data_source,
            )
        else:
            result = await service.fetch_and_save_kline_data(
                ticker=ticker,
                market=market,
                period=period,
                data_source=data_source,
            )

        response_data = UpdateKlineDataResponse(
            ticker=result["ticker"],
            period=period,
            updated=result.get("updated", 0),
            inserted=result.get("inserted", 0),
        )

        return success_response(
            data=response_data.model_dump(),
            message=f"更新完成：新增 {response_data.new_count} 条，更新 {response_data.updated_count} 条",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新历史K线数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}",
        )


@router.get("/batch")
async def batch_update_kline_data(
    tickers: str = Query(..., description="股票代码列表（逗号分隔）"),
    period: str = Query("1d", description="时间周期"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
):
    """批量更新历史K线数据（SSE 实时推送进度）.

    ⚠️ 注意：此接口使用 GET 方法，因为 EventSource API 只支持 GET 请求。

    响应格式为 SSE 流，进度消息格式：
    {
        "stage": "init|fetching|saving|completed|error",
        "message": "进度描述",
        "progress": 0-100,
        "total": 总数,
        "current": 当前进度,
        "success_count": 成功数,
        "failed_count": 失败数
    }
    """

    async def event_generator():
        """SSE 事件生成器."""
        try:
            # 解析股票代码列表
            ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
            if not ticker_list:
                yield f"data: {json.dumps({'stage': 'error', 'message': '股票代码列表为空'})}\n\n"
                return

            # 获取股票市场信息
            stock_service = get_stock_service(db=get_database())
            stocks = await stock_service.get_stocks_by_tickers(ticker_list)
            markets = {stock["ticker"]: stock.get("market", "NASDAQ") for stock in stocks}

            # 解析日期
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None

            # 创建进度队列
            progress_queue = asyncio.Queue()

            async def progress_handler(progress_data: dict):
                """进度处理器，将数据添加到队列."""
                await progress_queue.put(progress_data)

            async def batch_task():
                """异步批量任务."""
                try:
                    service = get_historical_data_service()
                    await service.fetch_batch_kline_data(
                        tickers=ticker_list,
                        markets=markets,
                        period=period,
                        start_date=start_dt,
                        end_date=end_dt,
                        progress_callback=progress_handler,
                    )
                except Exception as e:
                    logger.error(f"批量更新失败: {str(e)}")
                    await progress_queue.put(
                        {"stage": "error", "message": f"批量更新失败: {str(e)}"}
                    )
                finally:
                    # 发送结束标记
                    await progress_queue.put(None)

            # 启动批量任务
            task = asyncio.create_task(batch_task())

            # 持续发送进度更新
            while True:
                try:
                    # 从队列获取进度数据，设置超时避免阻塞
                    progress_data = await asyncio.wait_for(
                        progress_queue.get(), timeout=0.5
                    )

                    # None 表示任务结束
                    if progress_data is None:
                        break

                    # 发送 SSE 消息
                    yield f"data: {json.dumps(progress_data)}\n\n"

                except asyncio.TimeoutError:
                    # 超时则发送心跳
                    yield ": heartbeat\n\n"

            # 等待任务完成
            await task

        except Exception as e:
            logger.error(f"SSE 事件生成器错误: {str(e)}")
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/full-update")
async def full_update_kline_data(
    period: str = Query("1d", description="时间周期"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
):
    """全量更新所有股票的历史K线数据（SSE 实时推送进度）.

    ⚠️ 注意：此接口使用 GET 方法，因为 EventSource API 只支持 GET 请求。
    """

    async def event_generator():
        """SSE 事件生成器."""
        try:
            # 获取所有股票
            stock_service = get_stock_service(db=get_database())
            all_stocks = await stock_service.get_all_stocks()

            if not all_stocks:
                yield f"data: {json.dumps({'stage': 'error', 'message': '没有找到股票数据'})}\n\n"
                return

            ticker_list = [stock["ticker"] for stock in all_stocks]
            markets = {
                stock["ticker"]: stock.get("market", "NASDAQ") for stock in all_stocks
            }

            # 解析日期
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None

            # 创建进度队列
            progress_queue = asyncio.Queue()

            async def progress_handler(progress_data: dict):
                """进度处理器."""
                await progress_queue.put(progress_data)

            async def batch_task():
                """异步批量任务."""
                try:
                    service = get_historical_data_service()
                    await service.fetch_batch_kline_data(
                        tickers=ticker_list,
                        markets=markets,
                        period=period,
                        start_date=start_dt,
                        end_date=end_dt,
                        progress_callback=progress_handler,
                    )
                except Exception as e:
                    logger.error(f"全量更新失败: {str(e)}")
                    await progress_queue.put(
                        {"stage": "error", "message": f"全量更新失败: {str(e)}"}
                    )
                finally:
                    await progress_queue.put(None)

            # 启动批量任务
            task = asyncio.create_task(batch_task())

            # 持续发送进度更新
            while True:
                try:
                    progress_data = await asyncio.wait_for(
                        progress_queue.get(), timeout=0.5
                    )

                    if progress_data is None:
                        break

                    yield f"data: {json.dumps(progress_data)}\n\n"

                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"

            await task

        except Exception as e:
            logger.error(f"SSE 事件生成器错误: {str(e)}")
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/{ticker}", response_model=dict)
async def delete_kline_data(
    ticker: str,
    period: Optional[str] = Query(None, description="时间周期（可选）"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
):
    """删除历史K线数据.

    - 如果指定了 period，只删除该周期的数据
    - 如果指定了日期范围，只删除该日期范围内的数据
    - 如果都不指定，删除该股票的所有数据
    """
    try:
        service = get_historical_data_service()

        # 解析日期
        before_date = datetime.fromisoformat(end_date) if end_date else None

        deleted_count = await service.delete_kline_data(
            ticker=ticker, period=period, before_date=before_date
        )

        response_data = DeleteKlineDataResponse(deleted_count=deleted_count)

        return success_response(
            data=response_data.model_dump(), message=f"删除完成：共删除 {deleted_count} 条数据"
        )

    except Exception as e:
        logger.error(f"删除历史K线数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}",
        )
