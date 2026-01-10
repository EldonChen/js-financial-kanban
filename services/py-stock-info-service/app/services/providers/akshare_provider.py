"""akshare 数据源提供者."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import akshare as ak
from app.services.providers.base import StockDataProvider
from app.services.providers.field_mapper import FieldMapper

logger = logging.getLogger(__name__)


class AkshareProvider(StockDataProvider):
    """akshare 数据源提供者.
    
    支持 A 股、港股、美股市场。
    第一优先级：免费优先、无需认证。
    """

    @property
    def name(self) -> str:
        """数据源名称."""
        return "akshare"

    @property
    def supported_markets(self) -> List[str]:
        """支持的市场列表."""
        return ["A股", "港股", "美股"]

    @property
    def priority(self) -> int:
        """数据源优先级：第一优先级."""
        return 1

    async def fetch_stock_info(
        self, ticker: str, market: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """获取单个股票信息.
        
        Args:
            ticker: 股票代码
            market: 市场类型（可选）
        
        Returns:
            股票信息字典，如果失败返回 None
        """
        try:
            # 在线程池中执行同步的 akshare 调用
            loop = asyncio.get_event_loop()
            
            # 根据市场类型选择不同的接口
            if market == "A股" or (market is None and self._is_a_stock(ticker)):
                stock_data = await loop.run_in_executor(
                    None, self._fetch_a_stock_info, ticker
                )
            elif market == "港股" or (market is None and self._is_hk_stock(ticker)):
                stock_data = await loop.run_in_executor(
                    None, self._fetch_hk_stock_info, ticker
                )
            else:
                # 默认尝试 A 股
                stock_data = await loop.run_in_executor(
                    None, self._fetch_a_stock_info, ticker
                )

            if stock_data:
                # 使用字段映射器统一格式
                mapped_data = FieldMapper.map_akshare(stock_data)
                # 清洗字段
                cleaned_data = FieldMapper.clean_fields(mapped_data)
                return cleaned_data

            return None

        except Exception as e:
            logger.error(f"akshare 获取股票 {ticker} 信息失败: {e}")
            return None

    async def fetch_all_tickers(
        self, market: Optional[str] = None
    ) -> List[str]:
        """获取所有股票代码列表.
        
        Args:
            market: 市场类型（可选）
        
        Returns:
            股票代码列表
        """
        try:
            loop = asyncio.get_event_loop()

            if market == "A股" or market is None:
                # 获取 A 股股票列表
                tickers = await loop.run_in_executor(
                    None, self._get_a_stock_tickers
                )
                return tickers
            elif market == "港股":
                # 获取港股股票列表
                tickers = await loop.run_in_executor(
                    None, self._get_hk_stock_tickers
                )
                return tickers
            else:
                # 默认返回 A 股列表
                tickers = await loop.run_in_executor(
                    None, self._get_a_stock_tickers
                )
                return tickers

        except Exception as e:
            logger.error(f"akshare 获取股票列表失败: {e}")
            return []

    async def is_available(self) -> bool:
        """检查数据源是否可用."""
        try:
            # 尝试获取 A 股股票列表，如果能成功则说明可用
            loop = asyncio.get_event_loop()
            tickers = await loop.run_in_executor(
                None, self._get_a_stock_tickers
            )
            return len(tickers) > 0
        except Exception as e:
            logger.warning(f"akshare 可用性检查失败: {e}")
            return False

    def _fetch_a_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """获取 A 股股票信息（同步方法）.
        
        Args:
            ticker: 股票代码
        
        Returns:
            股票信息字典
        """
        try:
            # 使用 akshare 获取股票基本信息
            # 注意：akshare 的接口可能会变化，这里使用较稳定的接口
            df = ak.stock_individual_info_em(symbol=ticker)
            
            if df is None or df.empty:
                return None

            # 转换为字典
            stock_info = {}
            for _, row in df.iterrows():
                key = row.iloc[0] if len(row) > 0 else None
                value = row.iloc[1] if len(row) > 1 else None
                if key and value:
                    stock_info[key] = value

            # 获取股票代码和名称
            stock_info["code"] = ticker
            stock_info["name"] = stock_info.get("股票简称") or stock_info.get("名称")

            return stock_info

        except Exception as e:
            logger.error(f"akshare 获取 A 股股票 {ticker} 信息失败: {e}")
            return None

    def _fetch_hk_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """获取港股股票信息（同步方法）.
        
        Args:
            ticker: 股票代码
        
        Returns:
            股票信息字典
        """
        try:
            # akshare 港股接口
            df = ak.stock_hk_spot_em()
            
            if df is None or df.empty:
                return None

            # 查找指定股票代码
            stock_row = df[df["代码"] == ticker]
            if stock_row.empty:
                return None

            # 转换为字典
            stock_info = stock_row.iloc[0].to_dict()
            stock_info["code"] = ticker

            return stock_info

        except Exception as e:
            logger.error(f"akshare 获取港股股票 {ticker} 信息失败: {e}")
            return None

    def _get_a_stock_tickers(self) -> List[str]:
        """获取 A 股股票代码列表（同步方法）.
        
        Returns:
            股票代码列表
        """
        try:
            # 获取 A 股股票列表
            df = ak.stock_info_a_code_name()
            
            if df is None or df.empty:
                return []

            # 提取股票代码
            tickers = df["code"].tolist()
            return [str(ticker).strip() for ticker in tickers if ticker]

        except Exception as e:
            logger.error(f"akshare 获取 A 股股票列表失败: {e}")
            return []

    def _get_hk_stock_tickers(self) -> List[str]:
        """获取港股股票代码列表（同步方法）.
        
        Returns:
            股票代码列表
        """
        try:
            # 获取港股股票列表
            df = ak.stock_hk_spot_em()
            
            if df is None or df.empty:
                return []

            # 提取股票代码
            tickers = df["代码"].tolist()
            return [str(ticker).strip() for ticker in tickers if ticker]

        except Exception as e:
            logger.error(f"akshare 获取港股股票列表失败: {e}")
            return []

    def _is_a_stock(self, ticker: str) -> bool:
        """判断是否为 A 股股票代码.
        
        Args:
            ticker: 股票代码
        
        Returns:
            是否为 A 股
        """
        # A 股代码通常是 6 位数字
        return ticker.isdigit() and len(ticker) == 6

    def _is_hk_stock(self, ticker: str) -> bool:
        """判断是否为港股股票代码.
        
        Args:
            ticker: 股票代码
        
        Returns:
            是否为港股
        """
        # 港股代码通常是 5 位数字，或以 0 开头
        return ticker.isdigit() and (len(ticker) == 5 or ticker.startswith("0"))

    async def fetch_multiple_stocks(
        self, tickers: List[str], market: Optional[str] = None
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """批量获取多个股票信息（使用 akshare 批量查询）.
        
        akshare 支持批量查询，可以一次性获取多个股票的信息，比逐个查询快得多。
        
        Args:
            tickers: 股票代码列表
            market: 市场类型（可选）
        
        Returns:
            字典，key 为 ticker，value 为股票信息或 None
        """
        if not tickers:
            return {}

        try:
            loop = asyncio.get_event_loop()

            # 根据市场类型选择批量查询方法
            if market == "A股" or (market is None and all(self._is_a_stock(t) for t in tickers)):
                # 使用 A 股批量查询
                stock_data_dict = await loop.run_in_executor(
                    None, self._fetch_multiple_a_stocks, tickers
                )
            elif market == "港股" or (market is None and all(self._is_hk_stock(t) for t in tickers)):
                # 使用港股批量查询
                stock_data_dict = await loop.run_in_executor(
                    None, self._fetch_multiple_hk_stocks, tickers
                )
            else:
                # 混合市场或不确定，回退到逐个查询
                logger.warning("混合市场或不确定市场类型，回退到逐个查询")
                return await super().fetch_multiple_stocks(tickers, market)

            # 映射和清洗字段
            results = {}
            for ticker, stock_data in stock_data_dict.items():
                if stock_data:
                    mapped_data = FieldMapper.map_akshare(stock_data)
                    cleaned_data = FieldMapper.clean_fields(mapped_data)
                    results[ticker] = cleaned_data
                else:
                    results[ticker] = None

            return results

        except Exception as e:
            logger.error(f"akshare 批量获取股票信息失败: {e}")
            # 回退到逐个查询
            logger.info("回退到逐个查询模式")
            return await super().fetch_multiple_stocks(tickers, market)

    def _fetch_multiple_a_stocks(self, tickers: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """批量获取 A 股股票信息（同步方法）.
        
        使用 akshare 的批量接口一次性获取多个股票信息。
        如果请求的股票数量较多（>50），直接获取所有 A 股数据然后过滤，比逐个查询快得多。
        
        Args:
            tickers: 股票代码列表
        
        Returns:
            字典，key 为 ticker，value 为股票信息或 None
        """
        results = {}
        tickers_set = set(tickers)  # 使用 set 提高查找效率
        
        try:
            # 如果请求的股票数量较多，直接获取所有 A 股数据然后过滤
            # 这样可以避免多次网络请求，大幅提升性能
            if len(tickers) > 50:
                logger.info(f"请求股票数量较多（{len(tickers)} 只），使用全量数据过滤模式")
                # 使用 stock_zh_a_spot_em 获取所有 A 股实时行情（包含基本信息）
                df_all = ak.stock_zh_a_spot_em()
                
                if df_all is not None and not df_all.empty:
                    logger.info(f"获取到 {len(df_all)} 只 A 股数据，开始过滤...")
                    # 将 DataFrame 转换为字典，以股票代码为 key
                    for _, row in df_all.iterrows():
                        code = str(row.get("代码", "")).strip()
                        if code in tickers_set:
                            # 转换为字典
                            stock_info = row.to_dict()
                            stock_info["code"] = code
                            stock_info["name"] = stock_info.get("名称") or stock_info.get("name")
                            results[code] = stock_info
                    
                    logger.info(f"批量查询成功: 找到 {len(results)}/{len(tickers)} 只股票")
                else:
                    logger.warning("批量查询返回空结果，回退到逐个查询")
                    raise Exception("批量查询返回空结果")
            else:
                # 如果请求的股票数量较少，仍然使用全量数据过滤（因为 akshare 的接口就是返回全量）
                logger.debug(f"请求股票数量较少（{len(tickers)} 只），使用全量数据过滤模式")
                df_all = ak.stock_zh_a_spot_em()
                
                if df_all is not None and not df_all.empty:
                    for _, row in df_all.iterrows():
                        code = str(row.get("代码", "")).strip()
                        if code in tickers_set:
                            stock_info = row.to_dict()
                            stock_info["code"] = code
                            stock_info["name"] = stock_info.get("名称") or stock_info.get("name")
                            results[code] = stock_info
                else:
                    raise Exception("批量查询返回空结果")
            
            # 对于没有在批量结果中找到的股票，尝试单独查询
            missing_tickers = [t for t in tickers if t not in results]
            if missing_tickers:
                logger.debug(f"批量查询未找到 {len(missing_tickers)} 只股票，尝试单独查询")
                for ticker in missing_tickers:
                    try:
                        stock_info = self._fetch_a_stock_info(ticker)
                        if stock_info:
                            results[ticker] = stock_info
                        else:
                            results[ticker] = None
                    except Exception as e:
                        logger.warning(f"单独查询股票 {ticker} 失败: {e}")
                        results[ticker] = None
            
            # 确保所有 tickers 都在结果中
            for ticker in tickers:
                if ticker not in results:
                    results[ticker] = None
            
            return results

        except Exception as e:
            logger.error(f"akshare 批量获取 A 股股票信息失败: {e}")
            # 回退到逐个查询
            logger.info("回退到逐个查询模式")
            for ticker in tickers:
                try:
                    stock_info = self._fetch_a_stock_info(ticker)
                    results[ticker] = stock_info
                except Exception:
                    results[ticker] = None
            return results

    def _fetch_multiple_hk_stocks(self, tickers: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """批量获取港股股票信息（同步方法）.
        
        使用 akshare 的批量接口一次性获取多个港股信息。
        直接获取所有港股数据然后过滤，比逐个查询快得多。
        
        Args:
            tickers: 股票代码列表
        
        Returns:
            字典，key 为 ticker，value 为股票信息或 None
        """
        results = {}
        tickers_set = set(tickers)  # 使用 set 提高查找效率
        
        try:
            # 使用 stock_hk_spot_em 获取所有港股实时行情（包含基本信息）
            logger.info(f"批量获取港股信息: 请求 {len(tickers)} 只股票")
            df_all = ak.stock_hk_spot_em()
            
            if df_all is not None and not df_all.empty:
                logger.info(f"获取到 {len(df_all)} 只港股数据，开始过滤...")
                # 将 DataFrame 转换为字典，以股票代码为 key
                for _, row in df_all.iterrows():
                    code = str(row.get("代码", "")).strip()
                    if code in tickers_set:
                        # 转换为字典
                        stock_info = row.to_dict()
                        stock_info["code"] = code
                        results[code] = stock_info
                
                logger.info(f"批量查询成功: 找到 {len(results)}/{len(tickers)} 只股票")
                
                # 确保所有 tickers 都在结果中
                for ticker in tickers:
                    if ticker not in results:
                        results[ticker] = None
                
                return results
            else:
                # 如果批量查询失败，回退到逐个查询
                logger.warning("批量查询返回空结果，回退到逐个查询")
                raise Exception("批量查询返回空结果")

        except Exception as e:
            logger.error(f"akshare 批量获取港股股票信息失败: {e}")
            # 回退到逐个查询
            logger.info("回退到逐个查询模式")
            for ticker in tickers:
                try:
                    stock_info = self._fetch_hk_stock_info(ticker)
                    results[ticker] = stock_info
                except Exception:
                    results[ticker] = None
            return results
