"""yfinance 数据抓取服务."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import yfinance as yf
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def _get_wikipedia_headers() -> dict:
    """获取 Wikipedia 请求的请求头.
    
    Returns:
        包含 User-Agent 等请求头的字典
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


def fetch_stock_info(ticker: str) -> Optional[Dict[str, Any]]:
    """从 Yahoo Finance 抓取股票信息.

    Args:
        ticker: 股票代码

    Returns:
        股票信息字典，如果抓取失败返回 None
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or "symbol" not in info:
            logger.warning(f"股票 {ticker} 信息不完整或不存在")
            return None

        # 数据转换和清洗
        stock_data = transform_stock_info(info)
        return stock_data

    except Exception as e:
        logger.error(f"抓取股票 {ticker} 信息失败: {str(e)}")
        return None


def transform_stock_info(info: Dict[str, Any]) -> Dict[str, Any]:
    """转换 yfinance 返回的数据为标准化格式.

    Args:
        info: yfinance 返回的股票信息字典

    Returns:
        转换后的股票数据字典
    """
    # 字段映射：只映射基本信息字段
    stock_data = {
        "ticker": info.get("symbol", "").strip().upper(),
        "name": (info.get("longName") or info.get("shortName") or "").strip(),
        "market": (info.get("exchange") or "").strip(),
        "sector": (info.get("sector") or "").strip(),
        "industry": (info.get("industry") or "").strip(),
        "currency": (info.get("currency") or "").strip().upper(),
        "exchange": (info.get("exchange") or "").strip(),
        "country": (info.get("country") or "").strip(),
        "data_source": "yfinance",
    }

    # 数据清洗：处理空字符串和 None
    for key, value in stock_data.items():
        if value == "":
            stock_data[key] = None

    return stock_data


async def fetch_stock_info_async(ticker: str, retry_count: int = 3) -> Optional[Dict[str, Any]]:
    """异步抓取股票信息（带重试机制）.

    Args:
        ticker: 股票代码
        retry_count: 重试次数

    Returns:
        股票信息字典，如果抓取失败返回 None
    """
    for attempt in range(retry_count):
        try:
            # 在线程池中执行同步的 yfinance 调用
            loop = asyncio.get_event_loop()
            stock_data = await loop.run_in_executor(None, fetch_stock_info, ticker)

            if stock_data:
                return stock_data

            # 如果返回 None，等待后重试
            if attempt < retry_count - 1:
                wait_time = 2 ** attempt  # 指数退避：1s, 2s, 4s
                logger.info(f"股票 {ticker} 抓取失败，{wait_time} 秒后重试 (尝试 {attempt + 1}/{retry_count})")
                await asyncio.sleep(wait_time)

        except Exception as e:
            logger.error(f"异步抓取股票 {ticker} 信息异常: {str(e)}")
            if attempt < retry_count - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

    logger.error(f"股票 {ticker} 抓取失败，已重试 {retry_count} 次")
    return None


async def fetch_multiple_stocks(tickers: list[str], delay: float = 1.0, batch_size: int = 50) -> Dict[str, Optional[Dict[str, Any]]]:
    """批量抓取多个股票信息.

    使用 yfinance 的 Tickers 类批量获取股票信息，比逐个获取更高效。
    如果股票数量较多，会自动分批处理。

    Args:
        tickers: 股票代码列表
        delay: 批量之间的延迟（秒），避免请求过快（仅在批量之间延迟，不在每个股票之间）
        batch_size: 每批处理的股票数量（默认 50）

    Returns:
        字典，key 为 ticker，value 为股票信息或 None
    """
    if not tickers:
        return {}
    
    results = {}
    
    # 将股票列表分批处理
    batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
    
    for batch_idx, batch_tickers in enumerate(batches):
        try:
            # 使用 yfinance 的 Tickers 类批量获取
            # 将股票代码列表转换为空格分隔的字符串
            ticker_string = " ".join(batch_tickers)
            
            # 在线程池中执行同步的 yfinance 批量调用
            loop = asyncio.get_event_loop()
            
            def fetch_batch():
                """批量获取股票信息."""
                batch_results = {}
                try:
                    # 使用 Tickers 批量创建 Ticker 对象
                    tickers_obj = yf.Tickers(ticker_string)
                    
                    # 遍历每个 Ticker 对象获取信息
                    for symbol, ticker_obj in tickers_obj.tickers.items():
                        try:
                            info = ticker_obj.info
                            if info and "symbol" in info:
                                stock_data = transform_stock_info(info)
                                batch_results[symbol] = stock_data
                            else:
                                logger.warning(f"股票 {symbol} 信息不完整或不存在")
                                batch_results[symbol] = None
                        except Exception as e:
                            logger.error(f"获取股票 {symbol} 信息失败: {str(e)}")
                            batch_results[symbol] = None
                    
                except Exception as e:
                    logger.error(f"批量获取股票信息失败: {str(e)}")
                    # 如果批量获取失败，返回空字典，后续可以回退到逐个获取
                
                return batch_results
            
            # 执行批量获取
            batch_results = await loop.run_in_executor(None, fetch_batch)
            results.update(batch_results)
            
            # 检查是否有失败的股票（不在结果中的）
            for ticker in batch_tickers:
                if ticker not in results:
                    results[ticker] = None
            
            # 批量之间添加延迟（除了最后一批）
            if delay > 0 and batch_idx < len(batches) - 1:
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.error(f"批量抓取股票信息异常: {str(e)}")
            # 如果批量获取失败，回退到逐个获取
            logger.info(f"批次 {batch_idx + 1} 批量获取失败，回退到逐个获取模式...")
            for ticker in batch_tickers:
                if ticker not in results:
                    stock_data = await fetch_stock_info_async(ticker)
                    results[ticker] = stock_data
                    if delay > 0:
                        await asyncio.sleep(delay)

    return results


def _get_predefined_tickers() -> List[str]:
    """获取预定义的常见股票代码列表.
    
    包含主要指数的股票代码，作为备用数据源。
    这些是市场上最活跃和最重要的股票，确保即使外部数据源失败也能获取到股票列表。
    
    Returns:
        股票代码列表
    """
    # S&P 500 主要股票（市值最大的前 100 只左右）
    sp500_major = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B",
        "V", "UNH", "JNJ", "WMT", "JPM", "MA", "PG", "HD", "DIS", "BAC",
        "AVGO", "ADBE", "NFLX", "CRM", "COST", "XOM", "PEP", "TMO", "ABT",
        "CSCO", "ACN", "NKE", "MRK", "LIN", "DHR", "VZ", "CMCSA", "PM",
        "TXN", "NEE", "RTX", "HON", "UPS", "QCOM", "AMGN", "INTU", "AMAT",
        "DE", "LOW", "SPGI", "BKNG", "ADP", "GE", "SBUX", "GILD", "MDT",
        "C", "AXP", "TJX", "ZTS", "ISRG", "SYK", "BLK", "ADI", "MMC",
        "REGN", "CI", "CDNS", "PNC", "WM", "KLAC", "AON", "SHW", "SNPS",
        "FTNT", "ITW", "ICE", "ETN", "CME", "EQIX", "HCA", "CTSH", "MCO",
        "FAST", "APH", "EMR", "TT", "LRCX", "NXPI", "WDAY", "ANSS", "PAYX",
    ]
    
    # NASDAQ 100 主要股票
    nasdaq_major = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO",
        "COST", "NFLX", "ADBE", "PEP", "CSCO", "CMCSA", "QCOM", "INTU",
        "AMGN", "TXN", "ISRG", "REGN", "ADI", "KLAC", "SNPS", "FTNT",
        "CDNS", "CTSH", "FAST", "MELI", "TEAM", "ZS", "CRWD", "PANW",
        "OKTA", "NET", "DDOG", "DOCN", "FROG", "ESTC", "MDB", "NOW",
    ]
    
    # Dow Jones 30
    dow30 = [
        "AAPL", "MSFT", "UNH", "GS", "HD", "CAT", "MCD", "AMGN", "V",
        "HON", "TRV", "AXP", "IBM", "JPM", "WMT", "PG", "JNJ", "MRK",
        "CVX", "BA", "DIS", "DOW", "AMZN", "CRM", "CSCO", "INTC", "NKE",
        "VZ", "WBA", "MMM",
    ]
    
    # 合并所有列表并去重
    all_tickers = set(sp500_major + nasdaq_major + dow30)
    return sorted(list(all_tickers))


def _get_tickers_from_yahoo_finance_api() -> List[str]:
    """从 Yahoo Finance API 获取股票列表.
    
    使用多种策略从 Yahoo Finance 的公开 API 获取股票列表：
    1. 按行业关键词搜索
    2. 按字母搜索（A-Z）
    3. 搜索热门股票关键词
    
    Returns:
        股票代码列表
    """
    tickers = set()
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        
        # 策略1: 按行业关键词搜索
        search_terms = [
            "technology", "finance", "healthcare", "energy", "consumer",
            "industrial", "communication", "utilities", "real estate",
            "biotech", "pharmaceutical", "retail", "manufacturing",
            "aerospace", "defense", "automotive", "semiconductor",
        ]
        
        for term in search_terms:
            try:
                params = {
                    "q": term,
                    "lang": "en-US",
                    "region": "US",
                    "quotesCount": 100,  # 增加每个关键词的获取数量
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for quote in data.get("quotes", []):
                        symbol = quote.get("symbol", "").upper()
                        quote_type = quote.get("quoteType", "").upper()
                        # 只保留股票代码（排除期权、期货、ETF等）
                        if (symbol and len(symbol) <= 5 and "." not in symbol and 
                            quote_type in ["EQUITY", "STOCK", ""]):
                            tickers.add(symbol)
                
                # 添加延迟，避免请求过快
                import time
                time.sleep(0.3)
                
            except Exception as e:
                logger.warning(f"从 Yahoo Finance API 搜索 '{term}' 失败: {str(e)}")
                continue
        
        # 策略2: 按字母搜索（仅在股票数量不足时使用，获取更多股票）
        # 只搜索常见字母，避免耗时过长
        if len(tickers) < 300:  # 如果通过行业搜索获取的股票数量不足，才按字母搜索
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            # 只搜索前10个常见字母，避免耗时过长
            common_letters = letters[:10]
            for letter in common_letters:
                try:
                    params = {
                        "q": letter,
                        "lang": "en-US",
                        "region": "US",
                        "quotesCount": 50,  # 每个字母获取50个结果
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for quote in data.get("quotes", []):
                            symbol = quote.get("symbol", "").upper()
                            quote_type = quote.get("quoteType", "").upper()
                            # 只保留股票代码
                            if (symbol and len(symbol) <= 5 and "." not in symbol and
                                quote_type in ["EQUITY", "STOCK", ""] and
                                symbol.startswith(letter)):
                                tickers.add(symbol)
                    
                    # 添加延迟
                    import time
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.warning(f"按字母 '{letter}' 搜索失败: {str(e)}")
                    continue
        
        # 策略3: 搜索热门关键词
        popular_terms = [
            "stock", "shares", "company", "corporation", "inc", "ltd",
            "top stocks", "most active", "gainers", "losers",
        ]
        
        for term in popular_terms:
            try:
                params = {
                    "q": term,
                    "lang": "en-US",
                    "region": "US",
                    "quotesCount": 50,
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for quote in data.get("quotes", []):
                        symbol = quote.get("symbol", "").upper()
                        quote_type = quote.get("quoteType", "").upper()
                        if (symbol and len(symbol) <= 5 and "." not in symbol and
                            quote_type in ["EQUITY", "STOCK", ""]):
                            tickers.add(symbol)
                
                import time
                time.sleep(0.3)
                
            except Exception as e:
                logger.warning(f"搜索热门关键词 '{term}' 失败: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"从 Yahoo Finance API 获取股票列表失败: {str(e)}")
    
    logger.info(f"从 Yahoo Finance API 总共获取到 {len(tickers)} 只股票")
    return sorted(list(tickers))


def get_all_tickers_from_yahoo() -> List[str]:
    """从多个数据源获取股票代码列表.

    优先使用动态数据源获取股票列表，预定义列表仅作为兜底。
    数据源优先级：
    1. Yahoo Finance API（通过多种搜索策略获取，动态）
    2. Yahoo Finance 页面抓取（动态）
    3. Wikipedia（如果动态获取失败）
    4. 预定义的常见股票列表（兜底，确保至少有一些股票）

    Returns:
        股票代码列表
    """
    import time
    
    start_time = time.time()
    logger.info("开始获取股票代码列表（多数据源）...")
    tickers = set()
    data_source_stats = {}  # 记录每个数据源的统计信息

    try:
        # 方法1: 从 Yahoo Finance API 获取（通过多种搜索策略，动态获取）
        # 这是最主要的动态数据源
        logger.info("数据源1: 尝试从 Yahoo Finance API 获取股票列表...")
        api_start_time = time.time()
        try:
            api_tickers = _get_tickers_from_yahoo_finance_api()
            api_elapsed = time.time() - api_start_time
            if api_tickers:
                before_count = len(tickers)
                tickers.update(api_tickers)
                added_count = len(tickers) - before_count
                data_source_stats["Yahoo Finance API"] = {
                    "success": True,
                    "count": len(api_tickers),
                    "added": added_count,
                    "elapsed": api_elapsed,
                }
                logger.info(
                    f"数据源1成功: 从 Yahoo Finance API 获取到 {len(api_tickers)} 只股票, "
                    f"新增 {added_count} 只, 耗时 {api_elapsed:.2f} 秒"
                )
            else:
                data_source_stats["Yahoo Finance API"] = {
                    "success": False,
                    "count": 0,
                    "elapsed": api_elapsed,
                }
                logger.warning(f"数据源1失败: Yahoo Finance API 未返回任何股票, 耗时 {api_elapsed:.2f} 秒")
        except Exception as e:
            api_elapsed = time.time() - api_start_time
            data_source_stats["Yahoo Finance API"] = {
                "success": False,
                "error": str(e),
                "elapsed": api_elapsed,
            }
            logger.warning(f"数据源1异常: 从 Yahoo Finance API 获取股票列表失败: {str(e)}, 耗时 {api_elapsed:.2f} 秒")

        # 方法2: 从 Yahoo Finance 页面抓取（动态）
        logger.info(f"数据源2: 尝试从 Yahoo Finance 页面抓取股票列表（当前已有 {len(tickers)} 只）...")
        yahoo_start_time = time.time()
        try:
            yahoo_tickers = _scrape_yahoo_tickers()
            yahoo_elapsed = time.time() - yahoo_start_time
            if yahoo_tickers:
                before_count = len(tickers)
                tickers.update(yahoo_tickers)
                added_count = len(tickers) - before_count
                data_source_stats["Yahoo Finance 页面"] = {
                    "success": True,
                    "count": len(yahoo_tickers),
                    "added": added_count,
                    "elapsed": yahoo_elapsed,
                }
                logger.info(
                    f"数据源2成功: 从 Yahoo Finance 页面抓取到 {len(yahoo_tickers)} 只股票, "
                    f"新增 {added_count} 只, 耗时 {yahoo_elapsed:.2f} 秒"
                )
            else:
                data_source_stats["Yahoo Finance 页面"] = {
                    "success": False,
                    "count": 0,
                    "elapsed": yahoo_elapsed,
                }
                logger.warning(f"数据源2失败: Yahoo Finance 页面未抓取到任何股票, 耗时 {yahoo_elapsed:.2f} 秒")
        except Exception as e:
            yahoo_elapsed = time.time() - yahoo_start_time
            data_source_stats["Yahoo Finance 页面"] = {
                "success": False,
                "error": str(e),
                "elapsed": yahoo_elapsed,
            }
            logger.warning(f"数据源2异常: 从 Yahoo Finance 页面抓取股票列表失败: {str(e)}, 耗时 {yahoo_elapsed:.2f} 秒")

        # 方法3: 尝试从 Wikipedia 获取（如果动态获取的股票数量不足）
        if len(tickers) < 200:  # 如果动态获取的股票数量少于200，尝试 Wikipedia
            logger.info(f"数据源3: 当前股票数量 {len(tickers)} < 200, 尝试从 Wikipedia 获取...")
            wiki_start_time = time.time()
            
            try:
                sp500_tickers = _get_sp500_tickers()
                if sp500_tickers:
                    before_count = len(tickers)
                    tickers.update(sp500_tickers)
                    added_count = len(tickers) - before_count
                    logger.info(
                        f"数据源3-1成功: 从 Wikipedia 获取到 S&P 500 股票 {len(sp500_tickers)} 只, "
                        f"新增 {added_count} 只"
                    )
                else:
                    logger.warning("数据源3-1失败: 从 Wikipedia 获取 S&P 500 股票列表为空")
            except Exception as e:
                logger.warning(f"数据源3-1异常: 从 Wikipedia 获取 S&P 500 股票列表失败: {str(e)}")

            try:
                nasdaq_tickers = _get_nasdaq_tickers()
                if nasdaq_tickers:
                    before_count = len(tickers)
                    tickers.update(nasdaq_tickers)
                    added_count = len(tickers) - before_count
                    logger.info(
                        f"数据源3-2成功: 从 Wikipedia 获取到 NASDAQ 股票 {len(nasdaq_tickers)} 只, "
                        f"新增 {added_count} 只"
                    )
                else:
                    logger.warning("数据源3-2失败: 从 Wikipedia 获取 NASDAQ 股票列表为空")
            except Exception as e:
                logger.warning(f"数据源3-2异常: 从 Wikipedia 获取 NASDAQ 股票列表失败: {str(e)}")
            
            wiki_elapsed = time.time() - wiki_start_time
            logger.info(f"数据源3完成: Wikipedia 获取耗时 {wiki_elapsed:.2f} 秒, 当前股票总数 {len(tickers)}")

        # 方法4: 使用预定义的股票列表（兜底，确保至少有一些股票）
        # 只有在动态获取的股票数量非常少时才使用
        if len(tickers) < 100:
            logger.info(f"数据源4: 当前股票数量 {len(tickers)} < 100, 使用预定义列表作为兜底...")
            predefined_start_time = time.time()
            try:
                predefined_tickers = _get_predefined_tickers()
                before_count = len(tickers)
                tickers.update(predefined_tickers)
                added_count = len(tickers) - before_count
                predefined_elapsed = time.time() - predefined_start_time
                data_source_stats["预定义列表"] = {
                    "success": True,
                    "count": len(predefined_tickers),
                    "added": added_count,
                    "elapsed": predefined_elapsed,
                }
                logger.info(
                    f"数据源4成功: 从预定义列表获取到 {len(predefined_tickers)} 只股票, "
                    f"新增 {added_count} 只, 耗时 {predefined_elapsed:.3f} 秒（兜底）"
                )
            except Exception as e:
                predefined_elapsed = time.time() - predefined_start_time
                data_source_stats["预定义列表"] = {
                    "success": False,
                    "error": str(e),
                    "elapsed": predefined_elapsed,
                }
                logger.warning(f"数据源4异常: 获取预定义股票列表失败: {str(e)}, 耗时 {predefined_elapsed:.3f} 秒")

    except Exception as e:
        logger.error(f"获取所有股票代码过程中发生异常: {str(e)}")
        # 如果所有方法都失败，至少返回预定义列表
        logger.info("尝试使用预定义列表作为最后的兜底方案...")
        try:
            predefined_tickers = _get_predefined_tickers()
            tickers.update(predefined_tickers)
            logger.info(f"兜底成功: 使用预定义列表获取到 {len(predefined_tickers)} 只股票")
        except Exception as e2:
            logger.error(f"兜底失败: 连预定义列表也获取失败: {str(e2)}")

    ticker_list = sorted(list(tickers))
    total_elapsed = time.time() - start_time
    
    # 输出数据源统计信息
    logger.info("=" * 80)
    logger.info("数据源统计信息:")
    for source, stats in data_source_stats.items():
        if stats.get("success"):
            logger.info(
                f"  {source}: 成功 | "
                f"获取 {stats.get('count', 0)} 只 | "
                f"新增 {stats.get('added', 0)} 只 | "
                f"耗时 {stats.get('elapsed', 0):.2f}秒"
            )
        else:
            error_msg = stats.get("error", "未知错误")
            logger.warning(
                f"  {source}: 失败 | "
                f"错误: {error_msg[:50]} | "
                f"耗时 {stats.get('elapsed', 0):.2f}秒"
            )
    
    logger.info("=" * 80)
    logger.info(
        f"获取股票代码列表完成: "
        f"总共 {len(ticker_list)} 只 | "
        f"耗时 {total_elapsed:.2f} 秒 | "
        f"动态获取: {'是' if len(ticker_list) > 150 else '否（使用兜底）'}"
    )
    logger.info(f"股票代码示例（前20只）: {ticker_list[:20]}")
    logger.info("=" * 80)
    
    return ticker_list


def _get_sp500_tickers() -> List[str]:
    """获取 S&P 500 股票列表.

    Returns:
        S&P 500 股票代码列表
    """
    try:
        # 使用 Wikipedia 的 S&P 500 列表
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url, timeout=10, headers=_get_wikipedia_headers())
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "constituents"})

        if not table:
            # 尝试备用表格 ID
            table = soup.find("table", {"class": "wikitable"})

        tickers = []
        if table:
            rows = table.find_all("tr")[1:]  # 跳过表头
            for row in rows:
                cells = row.find_all("td")
                if cells:
                    ticker = cells[0].text.strip()
                    if ticker:
                        tickers.append(ticker)

        return tickers
    except Exception as e:
        logger.error(f"获取 S&P 500 股票列表失败: {str(e)}")
        return []


def _get_nasdaq_tickers() -> List[str]:
    """获取 NASDAQ 100 股票列表.

    Returns:
        NASDAQ 100 股票代码列表
    """
    try:
        # 使用 Wikipedia 的 NASDAQ 100 列表
        url = "https://en.wikipedia.org/wiki/NASDAQ-100"
        response = requests.get(url, timeout=10, headers=_get_wikipedia_headers())
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        # 查找包含股票代码的表格
        tables = soup.find_all("table", {"class": "wikitable"})

        tickers = []
        for table in tables:
            rows = table.find_all("tr")[1:]  # 跳过表头
            for row in rows:
                cells = row.find_all("td")
                if cells:
                    # NASDAQ 100 表格中，股票代码通常在第一个或第二个单元格
                    ticker = None
                    for cell in cells[:2]:
                        text = cell.text.strip()
                        # 检查是否是有效的股票代码格式（通常是大写字母，3-5个字符）
                        if text and text.isupper() and 2 <= len(text) <= 5:
                            ticker = text
                            break
                    if ticker:
                        tickers.append(ticker)

        return list(set(tickers))  # 去重
    except Exception as e:
        logger.error(f"获取 NASDAQ 股票列表失败: {str(e)}")
        return []


def _scrape_yahoo_tickers() -> List[str]:
    """从 Yahoo Finance 抓取股票代码列表.

    注意：这个方法可能较慢，因为需要抓取多个页面。

    Returns:
        股票代码列表
    """
    tickers = set()

    try:
        # Yahoo Finance 的股票列表页面（按字母顺序）
        base_url = "https://finance.yahoo.com/screener/predefined/most_actives"
        
        # 尝试获取活跃股票列表
        response = requests.get(base_url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        
        # 查找包含股票代码的元素（Yahoo Finance 使用特定的数据属性）
        # 注意：Yahoo Finance 的页面结构可能变化，这个方法可能需要调整
        ticker_elements = soup.find_all("a", {"data-test": "quoteLink"})
        
        for element in ticker_elements:
            href = element.get("href", "")
            # 从 URL 中提取股票代码，格式通常是 /quote/TICKER
            if "/quote/" in href:
                ticker = href.split("/quote/")[-1].split("?")[0].upper()
                if ticker and 1 <= len(ticker) <= 5:
                    tickers.add(ticker)

    except Exception as e:
        logger.warning(f"从 Yahoo Finance 抓取股票代码失败: {str(e)}")

    return list(tickers)


async def fetch_all_stocks_from_yahoo(delay: float = 1.0) -> Dict[str, Any]:
    """抓取 Yahoo Finance 上的所有股票信息.

    这个方法会：
    1. 获取所有可用的股票代码列表
    2. 批量抓取这些股票的信息
    3. 返回结果统计

    Args:
        delay: 每次抓取之间的延迟（秒），避免请求过快

    Returns:
        包含抓取结果的字典
    """
    logger.info("开始获取所有股票代码列表...")
    
    # 获取所有股票代码
    loop = asyncio.get_event_loop()
    all_tickers = await loop.run_in_executor(None, get_all_tickers_from_yahoo)

    if not all_tickers:
        logger.warning("未获取到任何股票代码")
        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "results": [],
        }

    logger.info(f"开始批量抓取 {len(all_tickers)} 只股票的信息...")

    # 批量抓取股票信息
    results = await fetch_multiple_stocks(all_tickers, delay=delay)

    # 统计结果
    success_count = sum(1 for v in results.values() if v is not None)
    failed_count = len(results) - success_count

    logger.info(
        f"批量抓取完成：总数 {len(all_tickers)}，成功 {success_count}，失败 {failed_count}"
    )

    return {
        "total": len(all_tickers),
        "success": success_count,
        "failed": failed_count,
        "tickers": all_tickers,
        "results": results,
    }
