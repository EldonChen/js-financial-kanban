"""股票数据业务逻辑服务."""

import logging
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from bson import ObjectId
from bson.regex import Regex
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.stock import stock_from_dict, prepare_stock_document
from app.services.yfinance_service import (
    fetch_stock_info_async,
    fetch_multiple_stocks,
    fetch_all_stocks_from_yahoo,
    get_all_tickers_from_yahoo,
)
from app.services.providers.router import StockDataRouter, get_stock_data_router
from app.schemas.stock import StockQueryParams

logger = logging.getLogger(__name__)


class StockService:
    """股票数据服务."""

    def __init__(
        self,
        db: Optional[AsyncIOMotorDatabase] = None,
        router: Optional[StockDataRouter] = None,
    ):
        """初始化服务.
        
        Args:
            db: 可选的数据库实例
            router: 可选的数据源路由器实例
        """
        self.db = db if db is not None else get_database()
        self.collection = self.db.stocks
        self.router = router or get_stock_data_router()

    async def get_stock_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """根据股票代码获取股票信息.

        Args:
            ticker: 股票代码

        Returns:
            股票信息字典，如果不存在返回 None
        """
        stock = await self.collection.find_one({"ticker": ticker.upper()})
        if stock:
            return stock_from_dict(stock)
        return None

    async def get_stocks_by_tickers(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """根据股票代码列表批量获取股票信息.

        Args:
            tickers: 股票代码列表

        Returns:
            股票信息列表
        """
        upper_tickers = [ticker.upper() for ticker in tickers]
        cursor = self.collection.find({"ticker": {"$in": upper_tickers}})
        stocks = []
        async for stock in cursor:
            stocks.append(stock_from_dict(stock))
        return stocks

    async def get_all_stocks(self) -> List[Dict[str, Any]]:
        """获取所有股票.

        Returns:
            股票信息列表
        """
        cursor = self.collection.find({})
        stocks = []
        async for stock in cursor:
            stocks.append(stock_from_dict(stock))
        return stocks

    async def query_stocks(
        self, params: StockQueryParams
    ) -> Dict[str, Any]:
        """查询股票列表（支持筛选和分页）.

        Args:
            params: 查询参数

        Returns:
            包含股票列表和分页信息的字典
        """
        # 构建查询条件
        query = {}

        if params.ticker:
            query["ticker"] = params.ticker.upper()

        if params.name:
            # 股票名称模糊查询（使用正则表达式，不区分大小写）
            query["name"] = Regex(params.name, "i")

        if params.market:
            query["market"] = params.market

        if params.market_type:
            query["market_type"] = params.market_type

        if params.sector:
            query["sector"] = params.sector

        # 计算跳过的文档数
        skip = (params.page - 1) * params.page_size

        # 查询总数
        total = await self.collection.count_documents(query)

        # 查询数据
        cursor = self.collection.find(query).skip(skip).limit(params.page_size)
        stocks = []
        async for stock in cursor:
            stocks.append(stock_from_dict(stock))

        return {
            "items": stocks,
            "total": total,
            "page": params.page,
            "page_size": params.page_size,
            "total_pages": (total + params.page_size - 1) // params.page_size,
        }

    async def upsert_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新或插入股票数据（upsert）.

        Args:
            stock_data: 股票数据字典

        Returns:
            更新后的股票信息
        """
        ticker = stock_data["ticker"].upper()
        now = datetime.now(UTC)

        # 准备文档
        document = prepare_stock_document(stock_data)
        document["ticker"] = ticker
        document["last_updated"] = now

        # 移除 created_at，因为它应该只通过 $setOnInsert 设置
        # 这样可以避免与 $setOnInsert 的冲突
        document.pop("created_at", None)

        # 使用 upsert 操作
        result = await self.collection.find_one_and_update(
            {"ticker": ticker},
            {
                "$set": document,
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
            return_document=True,
        )

        return stock_from_dict(result)

    async def update_stock_from_provider(
        self,
        ticker: str,
        market: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        allow_create: bool = True,
        validate_if_new: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """从数据源抓取并更新股票数据（支持多数据源）.

        Args:
            ticker: 股票代码
            market: 市场类型（可选，用于选择合适的数据源）
            preferred_provider: 首选数据源名称（可选）
            allow_create: 如果股票不存在于数据库中，是否允许创建新记录（默认 True）
            validate_if_new: 如果股票不存在于数据库中，是否验证数据有效性（默认 False）

        Returns:
            更新后的股票信息，如果抓取失败返回 None
        """
        # 检查数据库中是否已存在该股票
        existing_stock = await self.get_stock_by_ticker(ticker)

        # 使用数据源路由器获取股票信息（自动容错）
        stock_data = await self.router.fetch_stock_info(
            ticker, market=market, preferred_provider=preferred_provider
        )

        if not stock_data:
            logger.warning(
                f"股票 {ticker} 数据抓取失败（所有数据源都失败，市场: {market}）"
            )
            return None

        # 如果股票不存在于数据库中
        if existing_stock is None:
            # 如果不允许创建，直接返回 None
            if not allow_create:
                logger.warning(
                    f"股票 {ticker} 不存在于数据库中，且不允许创建新记录"
                )
                return None

            # 如果需要验证数据有效性
            if validate_if_new:
                # 验证数据有效性：至少要有 name 字段
                if not stock_data.get("name"):
                    logger.warning(
                        f"股票 {ticker} 数据无效（缺少 name 字段），拒绝创建新记录"
                    )
                    return None

        # 更新到数据库
        updated_stock = await self.upsert_stock(stock_data)
        data_source = stock_data.get("data_source", "unknown")
        logger.info(f"股票 {ticker} 更新成功（数据源: {data_source}）")
        return updated_stock

    async def update_stock_from_yfinance(
        self, ticker: str, allow_create: bool = True, validate_if_new: bool = False
    ) -> Optional[Dict[str, Any]]:
        """从 yfinance 抓取并更新股票数据（向后兼容方法）.

        此方法保留用于向后兼容，实际调用 update_stock_from_provider。

        Args:
            ticker: 股票代码
            allow_create: 如果股票不存在于数据库中，是否允许创建新记录（默认 True）
            validate_if_new: 如果股票不存在于数据库中，是否验证数据有效性（默认 False）

        Returns:
            更新后的股票信息，如果抓取失败返回 None
        """
        # 调用新的多数据源方法，指定首选数据源为 yfinance
        return await self.update_stock_from_provider(
            ticker=ticker,
            preferred_provider="yfinance",
            allow_create=allow_create,
            validate_if_new=validate_if_new,
        )

    async def update_all_stocks(self) -> Dict[str, Any]:
        """更新所有股票数据.

        Returns:
            更新结果统计
        """
        # 获取所有股票代码
        tickers = []
        async for stock in self.collection.find({}, {"ticker": 1}):
            tickers.append(stock["ticker"])

        if not tickers:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "results": [],
            }

        # 使用数据源路由器批量获取股票信息
        success_count = 0
        failed_count = 0
        update_results = []

        for ticker in tickers:
            # 使用多数据源方法更新
            stock_data = await self.router.fetch_stock_info(ticker)
            if stock_data:
                # 更新到数据库
                updated_stock = await self.upsert_stock(stock_data)
                success_count += 1
                update_results.append({"ticker": ticker, "status": "success"})
            else:
                failed_count += 1
                update_results.append({"ticker": ticker, "status": "failed"})

        logger.info(
            f"批量更新完成：总数 {len(tickers)}，成功 {success_count}，失败 {failed_count}"
        )

        return {
            "total": len(tickers),
            "success": success_count,
            "failed": failed_count,
            "results": update_results,
        }

    async def batch_update_stocks(self, tickers: List[str]) -> Dict[str, Any]:
        """批量更新指定股票数据.

        Args:
            tickers: 股票代码列表

        Returns:
            更新结果统计
        """
        if not tickers:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "results": [],
            }

        # 使用数据源路由器批量获取股票信息
        success_count = 0
        failed_count = 0
        update_results = []

        for ticker in tickers:
            # 使用多数据源方法更新
            stock_data = await self.router.fetch_stock_info(ticker)
            if stock_data:
                # 更新到数据库
                updated_stock = await self.upsert_stock(stock_data)
                success_count += 1
                update_results.append({"ticker": ticker, "status": "success"})
            else:
                failed_count += 1
                update_results.append({"ticker": ticker, "status": "failed"})

        logger.info(
            f"批量更新完成：总数 {len(tickers)}，成功 {success_count}，失败 {failed_count}"
        )

        return {
            "total": len(tickers),
            "success": success_count,
            "failed": failed_count,
            "results": update_results,
        }

    async def delete_stock(self, ticker: str) -> bool:
        """删除股票数据.

        Args:
            ticker: 股票代码

        Returns:
            是否删除成功
        """
        result = await self.collection.delete_one({"ticker": ticker.upper()})
        return result.deleted_count > 0

    async def delete_all_stocks(self) -> Dict[str, Any]:
        """删除所有股票数据.

        Returns:
            删除结果统计
        """
        result = await self.collection.delete_many({})
        deleted_count = result.deleted_count
        logger.info(f"删除所有股票完成，共删除 {deleted_count} 条记录")
        return {
            "deleted_count": deleted_count,
        }

    async def fetch_and_save_all_stocks_from_provider(
        self,
        market: Optional[str] = None,
        delay: float = 1.0,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """从数据源抓取所有股票并保存到数据库（支持多数据源）.

        Args:
            market: 市场类型（可选，用于选择合适的数据源）
            delay: 每次抓取之间的延迟（秒）
            progress_callback: 进度回调函数，接收进度信息字典

        Returns:
            抓取和保存结果统计
        """
        import asyncio
        import time

        start_time = time.time()
        logger.info("=" * 80)
        logger.info("开始执行 fetch_and_save_all_stocks_from_provider 操作")
        logger.info(
            f"参数: market={market}, delay={delay}, "
            f"progress_callback={'已设置' if progress_callback else '未设置'}"
        )

        # 发送初始进度
        if progress_callback:
            await progress_callback({
                "stage": "init",
                "message": "开始获取股票代码列表...",
                "progress": 0,
            })

        logger.info("步骤1: 开始获取股票代码列表...")
        ticker_start_time = time.time()

        # 使用数据源路由器获取股票代码列表（自动容错）
        all_tickers = await self.router.fetch_all_tickers(market=market)

        ticker_elapsed = time.time() - ticker_start_time
        logger.info(f"步骤1完成: 获取股票代码列表耗时 {ticker_elapsed:.2f} 秒")

        if not all_tickers:
            logger.error("步骤1失败: 未获取到任何股票代码")
            if progress_callback:
                await progress_callback({
                    "stage": "error",
                    "message": "未获取到任何股票代码",
                    "progress": 0,
                })
            logger.info("=" * 80)
            return {
                "total": 0,
                "fetch_success": 0,
                "fetch_failed": 0,
                "save_success": 0,
                "save_failed": 0,
                "results": [],
            }

        total = len(all_tickers)
        logger.info(f"步骤1成功: 共获取到 {total} 只股票代码")
        logger.info(f"股票代码示例（前10只）: {all_tickers[:10]}")

        if progress_callback:
            await progress_callback({
                "stage": "fetching",
                "message": f"开始抓取 {total} 只股票的信息...",
                "progress": 0,
                "total": total,
                "current": 0,
            })

        logger.info("=" * 80)
        logger.info("步骤2: 开始批量抓取股票信息...")
        logger.info(f"批量抓取参数: delay={delay}秒, 总数={total}只")
        fetch_start_time = time.time()

        # 优先尝试批量查询（如果数据源支持）
        fetch_success = 0
        fetch_failed = 0
        fetch_results = {}
        failed_tickers = []

        # 尝试使用批量查询（优先使用 akshare 的批量查询功能）
        logger.info("尝试使用批量查询模式（如果数据源支持）...")
        batch_query_success = False
        
        try:
            batch_results = await self.router.fetch_multiple_stocks(
                all_tickers, market=market
            )
            
            # 检查批量查询结果
            batch_success_count = sum(1 for v in batch_results.values() if v is not None)
            
            if batch_success_count > 0:
                # 批量查询成功，使用批量结果
                fetch_elapsed = time.time() - fetch_start_time
                logger.info(
                    f"✅ 批量查询成功: 获取到 {batch_success_count}/{total} 只股票信息 "
                    f"(耗时 {fetch_elapsed:.2f}秒)"
                )
                fetch_results = batch_results
                fetch_success = batch_success_count
                fetch_failed = total - batch_success_count
                batch_query_success = True
                
                # 记录失败的股票
                for ticker, stock_data in batch_results.items():
                    if stock_data is None:
                        failed_tickers.append(ticker)
                
                # 发送批量查询完成的进度
                if progress_callback:
                    await progress_callback({
                        "stage": "fetching",
                        "message": f"批量查询完成: 成功 {fetch_success}，失败 {fetch_failed}",
                        "progress": 50,  # 批量查询完成，进入保存阶段
                        "total": total,
                        "current": total,
                        "fetch_success": fetch_success,
                        "fetch_failed": fetch_failed,
                    })
                
                # 记录批量查询统计（批量查询成功时）
                logger.info("=" * 80)
                logger.info(f"步骤2完成: 批量查询股票信息耗时 {fetch_elapsed:.2f} 秒")
                logger.info(f"抓取统计: 成功 {fetch_success} 只, 失败 {fetch_failed} 只")
                if failed_tickers:
                    logger.warning(f"抓取失败的股票代码（前20只）: {failed_tickers[:20]}")
            else:
                # 批量查询失败，回退到逐个查询
                logger.warning("批量查询未获取到任何数据，回退到逐个查询模式")
                batch_query_success = False
                
        except Exception as e:
            logger.warning(f"批量查询失败: {e}，回退到逐个查询模式")
            batch_query_success = False
        
        # 如果批量查询失败，回退到逐个查询
        if not batch_query_success:
            for idx, ticker in enumerate(all_tickers):
                ticker_fetch_start = time.time()
                # 使用数据源路由器获取股票信息（自动容错）
                stock_data = await self.router.fetch_stock_info(ticker, market=market)
                ticker_fetch_elapsed = time.time() - ticker_fetch_start
                fetch_results[ticker] = stock_data

                if stock_data:
                    fetch_success += 1
                    logger.debug(
                        f"[{idx + 1}/{total}] 抓取成功: {ticker} "
                        f"(耗时 {ticker_fetch_elapsed:.2f}秒, "
                        f"数据源: {stock_data.get('data_source', 'unknown')})"
                    )
                else:
                    fetch_failed += 1
                    failed_tickers.append(ticker)
                    logger.warning(
                        f"[{idx + 1}/{total}] 抓取失败: {ticker} "
                        f"(耗时 {ticker_fetch_elapsed:.2f}秒)"
                    )

                # 每10只股票记录一次进度
                if (idx + 1) % 10 == 0 or idx == total - 1:
                    elapsed = time.time() - fetch_start_time
                    avg_time = elapsed / (idx + 1)
                    remaining = avg_time * (total - idx - 1)
                    logger.info(
                        f"抓取进度: {idx + 1}/{total} ({int((idx + 1) / total * 100)}%) | "
                        f"成功: {fetch_success} | 失败: {fetch_failed} | "
                        f"已耗时: {elapsed:.1f}秒 | 预计剩余: {remaining:.1f}秒"
                    )

                # 发送抓取进度
                if progress_callback:
                    await progress_callback({
                        "stage": "fetching",
                        "message": f"正在抓取股票信息... ({idx + 1}/{total})",
                        "progress": int((idx + 1) / total * 50),  # 抓取阶段占 50%
                        "total": total,
                        "current": idx + 1,
                        "fetch_success": fetch_success,
                        "fetch_failed": fetch_failed,
                    })

                # 添加延迟
                if delay > 0 and idx < total - 1:
                    await asyncio.sleep(delay)
            
            # 逐个查询完成后的统计（仅在批量查询失败时执行）
            fetch_elapsed = time.time() - fetch_start_time
            logger.info("=" * 80)
            logger.info(f"步骤2完成: 批量抓取股票信息耗时 {fetch_elapsed:.2f} 秒")
            logger.info(f"抓取统计: 成功 {fetch_success} 只, 失败 {fetch_failed} 只")
            if failed_tickers:
                logger.warning(f"抓取失败的股票代码（前20只）: {failed_tickers[:20]}")

        if progress_callback:
            await progress_callback({
                "stage": "saving",
                "message": f"开始保存股票数据到数据库...",
                "progress": 50,
                "total": total,
                "current": 0,
            })

        logger.info("=" * 80)
        logger.info("步骤3: 开始保存股票数据到数据库...")
        logger.info(f"待保存股票数量: {fetch_success} 只（有数据的股票）")
        save_start_time = time.time()

        # 保存到数据库
        save_success = 0
        save_failed = 0
        save_results = []
        save_failed_tickers = []

        for idx, (ticker, stock_data) in enumerate(fetch_results.items()):
            if stock_data:
                try:
                    ticker_save_start = time.time()
                    await self.upsert_stock(stock_data)
                    ticker_save_elapsed = time.time() - ticker_save_start
                    save_success += 1
                    save_results.append({"ticker": ticker, "status": "success"})
                    logger.debug(
                        f"[{idx + 1}/{total}] 保存成功: {ticker} "
                        f"(耗时 {ticker_save_elapsed:.3f}秒)"
                    )
                except Exception as e:
                    logger.error(f"[{idx + 1}/{total}] 保存股票 {ticker} 失败: {str(e)}")
                    save_failed += 1
                    save_failed_tickers.append(ticker)
                    save_results.append({"ticker": ticker, "status": "failed"})
            else:
                save_failed += 1
                save_results.append({"ticker": ticker, "status": "failed"})

            # 每10只股票记录一次进度
            if (idx + 1) % 10 == 0 or idx == total - 1:
                elapsed = time.time() - save_start_time
                avg_time = elapsed / (idx + 1) if idx > 0 else 0
                remaining = avg_time * (total - idx - 1) if idx > 0 else 0
                logger.info(
                    f"保存进度: {idx + 1}/{total} ({int((idx + 1) / total * 100)}%) | "
                    f"成功: {save_success} | 失败: {save_failed} | "
                    f"已耗时: {elapsed:.1f}秒 | 预计剩余: {remaining:.1f}秒"
                )

            # 发送保存进度
            if progress_callback:
                await progress_callback({
                    "stage": "saving",
                    "message": f"正在保存股票数据... ({idx + 1}/{total})",
                    "progress": 50 + int((idx + 1) / total * 50),  # 保存阶段占 50%
                    "total": total,
                    "current": idx + 1,
                    "save_success": save_success,
                    "save_failed": save_failed,
                })

        save_elapsed = time.time() - save_start_time
        logger.info("=" * 80)
        logger.info(f"步骤3完成: 保存股票数据耗时 {save_elapsed:.2f} 秒")
        logger.info(f"保存统计: 成功 {save_success} 只, 失败 {save_failed} 只")
        if save_failed_tickers:
            logger.warning(f"保存失败的股票代码（前20只）: {save_failed_tickers[:20]}")

        total_elapsed = time.time() - start_time
        logger.info("=" * 80)
        logger.info(
            f"操作完成总结: "
            f"总耗时 {total_elapsed:.2f} 秒 | "
            f"股票总数 {total} | "
            f"抓取成功 {fetch_success} | 抓取失败 {fetch_failed} | "
            f"保存成功 {save_success} | 保存失败 {save_failed}"
        )
        logger.info("=" * 80)

        result = {
            "total": total,
            "fetch_success": fetch_success,
            "fetch_failed": fetch_failed,
            "save_success": save_success,
            "save_failed": save_failed,
            "results": save_results,
        }

        # 发送完成进度
        if progress_callback:
            await progress_callback({
                "stage": "completed",
                "message": f"拉取完成：总数 {total}，抓取成功 {fetch_success}，抓取失败 {fetch_failed}，保存成功 {save_success}，保存失败 {save_failed}",
                "progress": 100,
                "total": total,
                "current": total,
                "fetch_success": fetch_success,
                "fetch_failed": fetch_failed,
                "save_success": save_success,
                "save_failed": save_failed,
                "result": result,
            })

        return result

    async def fetch_and_save_all_stocks_from_yahoo(
        self, delay: float = 1.0, progress_callback=None
    ) -> Dict[str, Any]:
        """从 Yahoo Finance 抓取所有股票并保存到数据库（向后兼容方法）.

        此方法保留用于向后兼容，实际调用 fetch_and_save_all_stocks_from_provider。

        Args:
            delay: 每次抓取之间的延迟（秒）
            progress_callback: 进度回调函数，接收进度信息字典

        Returns:
            抓取和保存结果统计
        """
        # 调用新的多数据源方法，优先使用 yfinance
        return await self.fetch_and_save_all_stocks_from_provider(
            market=None,  # 不指定市场，让路由器自动选择
            delay=delay,
            progress_callback=progress_callback,
        )


# 创建全局服务实例（延迟初始化，避免导入时数据库未初始化）
stock_service: StockService | None = None


def get_stock_service(db=None, router=None) -> StockService:
    """获取股票服务实例（延迟初始化）.
    
    Args:
        db: 可选的数据库实例，如果提供则使用该实例
        router: 可选的数据源路由器实例
    """
    global stock_service
    if db is not None or router is not None:
        # 如果提供了数据库实例或路由器，创建新服务实例
        return StockService(db=db, router=router)
    if stock_service is None:
        stock_service = StockService()
    return stock_service
