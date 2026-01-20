"""技术指标路由."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.database import get_database
from app.schemas.indicators import (
    CalculateIndicatorRequest,
    IndicatorDataResponse,
    IndicatorListResponse,
    IndicatorPageResponse,
    SupportedIndicator,
)
from app.schemas.response import success_response
from app.services.indicators.indicator_service import IndicatorService

router = APIRouter(prefix="/api/v1/indicators", tags=["indicators"])
logger = logging.getLogger(__name__)


def get_indicator_service():
    """获取技术指标服务实例."""
    return IndicatorService(db=get_database())


@router.get("/supported", response_model=dict)
async def get_supported_indicators():
    """获取支持的技术指标列表."""
    try:
        service = get_indicator_service()
        indicators = service.get_supported_indicators()

        response_data = [SupportedIndicator(**ind) for ind in indicators]

        return success_response(data=[ind.model_dump() for ind in response_data])

    except Exception as e:
        logger.error(f"获取支持的指标列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取支持的指标列表失败: {str(e)}",
        )


@router.post("/{ticker}/calculate", response_model=dict)
async def calculate_indicator(
    ticker: str,
    indicator_name: str = Query(..., description="指标名称（如 MA5, RSI14, MACD_DIF）"),
    period: str = Query("1d", description="时间周期"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    request: CalculateIndicatorRequest = Body(default=None),
):
    """计算技术指标.

    请求体（可选）：
    {
        "indicator_params": {
            "period": 5,  // 示例参数
            ...
        }
    }
    """
    try:
        service = get_indicator_service()

        # 解析指标名称（获取指标类型和默认参数）
        indicator_info = service._parse_indicator_name(indicator_name)
        if not indicator_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的指标名称: {indicator_name}",
            )

        # 合并默认参数和用户提供的参数
        params = indicator_info["params"].copy()
        if request and request.indicator_params:
            params.update(request.indicator_params)

        # 解析日期
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # 计算指标
        indicator_data = await service.calculate_indicator(
            ticker=ticker,
            indicator_type=indicator_info["type"],
            indicator_name=indicator_name,
            period=period,
            params=params,
            start_date=start_dt,
            end_date=end_dt,
            use_cache=False,  # 手动计算不使用缓存
        )

        response_data = [IndicatorDataResponse(**item) for item in indicator_data]

        return success_response(
            data=[item.model_dump() for item in response_data],
            message=f"计算完成：共 {len(indicator_data)} 条数据",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"计算技术指标失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计算失败: {str(e)}",
        )


@router.get("/{ticker}", response_model=dict)
async def get_indicator_data(
    ticker: str,
    indicator_name: str = Query(..., description="指标名称（如 MA5, RSI14）"),
    period: str = Query("1d", description="时间周期"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    page: Optional[int] = Query(None, ge=1, description="页码（分页模式）"),
    page_size: Optional[int] = Query(None, ge=1, le=1000, description="每页条数（分页模式）"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="返回数量限制"),
):
    """查询技术指标数据.

    支持两种模式：
    1. 列表模式：不传 page/page_size 参数，返回列表格式
    2. 分页模式：传 page/page_size 参数，返回分页格式
    """
    try:
        service = get_indicator_service()

        # 解析日期
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # 查询指标数据
        indicator_data = await service.query_indicator_data(
            ticker=ticker,
            indicator_name=indicator_name,
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

            total = len(indicator_data)
            total_pages = (total + page_size - 1) // page_size

            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            items = indicator_data[start_idx:end_idx]

            response_data = IndicatorPageResponse(
                items=[IndicatorDataResponse(**item) for item in items],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )
        else:
            # 列表模式
            response_data = IndicatorListResponse(
                ticker=ticker,
                indicator_name=indicator_name,
                period=period,
                count=len(indicator_data),
                data=[IndicatorDataResponse(**item) for item in indicator_data],
            )

        return success_response(data=response_data.model_dump())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数错误: {str(e)}",
        )
    except Exception as e:
        logger.error(f"查询技术指标数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}",
        )


@router.get("/batch-calculate")
async def batch_calculate_indicators(
    tickers: str = Query(..., description="股票代码列表（逗号分隔）"),
    indicator_names: str = Query(..., description="指标名称列表（逗号分隔）"),
    period: str = Query("1d", description="时间周期"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
):
    """批量计算技术指标（SSE 实时推送进度）.

    ⚠️ 注意：此接口使用 GET 方法，因为 EventSource API 只支持 GET 请求。

    响应格式为 SSE 流，进度消息格式：
    {
        "stage": "init|calculating|completed|error",
        "message": "进度描述",
        "progress": 0-100,
        "total": 总数,
        "current": 当前进度,
        "success": 成功数,
        "failed": 失败数,
        "current_indicator": "当前正在计算的指标"
    }
    """

    async def event_generator():
        """SSE 事件生成器."""
        try:
            # 解析参数
            ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
            indicator_list = [i.strip() for i in indicator_names.split(",") if i.strip()]

            if not ticker_list:
                yield f"data: {json.dumps({'stage': 'error', 'message': '股票代码列表为空'})}\n\n"
                return

            if not indicator_list:
                yield f"data: {json.dumps({'stage': 'error', 'message': '指标名称列表为空'})}\n\n"
                return

            # 解析日期
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None

            # 发送初始化进度
            yield f"data: {json.dumps({'stage': 'init', 'message': '开始批量计算指标...', 'progress': 0, 'total': len(ticker_list)})}\n\n"

            service = get_indicator_service()
            total_success = 0
            total_failed = 0

            # 遍历股票列表
            for idx, ticker in enumerate(ticker_list):
                try:
                    # 创建进度队列
                    progress_queue = asyncio.Queue()

                    async def progress_handler(progress_data: dict):
                        """进度处理器."""
                        await progress_queue.put(progress_data)

                    async def calculate_task():
                        """异步计算任务."""
                        try:
                            await service.calculate_batch_indicators(
                                ticker=ticker,
                                indicator_names=indicator_list,
                                period=period,
                                start_date=start_dt,
                                end_date=end_dt,
                                progress_callback=progress_handler,
                            )
                        except Exception as e:
                            logger.error(f"计算 {ticker} 指标失败: {str(e)}")
                            await progress_queue.put(
                                {"stage": "error", "message": f"计算 {ticker} 失败: {str(e)}"}
                            )
                        finally:
                            await progress_queue.put(None)

                    # 启动计算任务
                    task = asyncio.create_task(calculate_task())

                    # 持续发送进度更新
                    while True:
                        try:
                            progress_data = await asyncio.wait_for(
                                progress_queue.get(), timeout=0.5
                            )

                            if progress_data is None:
                                break

                            # 添加全局进度信息
                            progress_data["ticker"] = ticker
                            progress_data["global_progress"] = int((idx + 1) / len(ticker_list) * 100)
                            progress_data["global_current"] = idx + 1
                            progress_data["global_total"] = len(ticker_list)

                            yield f"data: {json.dumps(progress_data)}\n\n"

                            # 统计成功/失败数
                            if progress_data.get("stage") == "completed":
                                result = progress_data.get("result", {})
                                total_success += result.get("success", 0)
                                total_failed += result.get("failed", 0)

                        except asyncio.TimeoutError:
                            yield ": heartbeat\n\n"

                    await task

                except Exception as e:
                    logger.error(f"处理 {ticker} 时出错: {str(e)}")
                    total_failed += len(indicator_list)
                    yield f"data: {json.dumps({'stage': 'error', 'message': f'处理 {ticker} 时出错: {str(e)}', 'ticker': ticker})}\n\n"

            # 发送最终完成通知
            yield f"data: {json.dumps({'stage': 'completed', 'message': f'批量计算完成：总数 {len(ticker_list)} 只股票，成功 {total_success} 个指标，失败 {total_failed} 个指标', 'progress': 100, 'total_success': total_success, 'total_failed': total_failed})}\n\n"

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
