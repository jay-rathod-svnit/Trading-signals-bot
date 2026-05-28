#  Market Data Fetcher  —  yfinance
import time
import logging
import yfinance as yf
import pandas as pd
from config import INSTRUMENTS, YF_PERIOD, CANDLE_INTERVAL

logger = logging.getLogger(__name__)


def fetch_candles(ticker: str, retries: int = 2) -> pd.DataFrame | None:
    """
    Fetch 5-minute OHLCV candles for *ticker*.

    Uses ``yf.Ticker().history()`` so the returned DataFrame always has
    flat, single-level column names (Open, High, Low, Close, Volume).
    """
    for attempt in range(1, retries + 1):
        try:
            t = yf.Ticker(ticker)
            data = t.history(period=YF_PERIOD, interval=CANDLE_INTERVAL)

            if data is None or data.empty:
                logger.warning(f"[{ticker}] No data returned (attempt {attempt})")
                time.sleep(1)
                continue

            # Keep only the columns we need
            required = ["Open", "High", "Low", "Close", "Volume"]
            missing = [c for c in required if c not in data.columns]
            if missing:
                logger.warning(f"[{ticker}] Missing columns: {missing}")
                return None

            data = data[required].copy()
            data.dropna(inplace=True)

            logger.info(f"[{ticker}] Fetched {len(data)} candles")
            return data

        except Exception as exc:
            logger.error(f"[{ticker}] Fetch error (attempt {attempt}): {exc}")
            if attempt < retries:
                time.sleep(2 * attempt)  # exponential back-off

    return None


def fetch_all_instruments() -> dict[str, pd.DataFrame]:
    """
    Fetch candles for every instrument in ``config.INSTRUMENTS``.

    Returns a dict  ``{ticker: DataFrame}``  — only instruments with
    enough rows for indicator calculation are included.
    """
    results: dict[str, pd.DataFrame] = {}
    for ticker in INSTRUMENTS:
        df = fetch_candles(ticker)
        if df is not None and len(df) >= 30:
            results[ticker] = df
        else:
            logger.warning(f"[{ticker}] Insufficient data — skipped")
        time.sleep(0.5)  # small pause to avoid rate-limits
    return results
