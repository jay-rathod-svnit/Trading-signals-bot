#  Technical Indicator Engine
import pandas as pd
import ta
from config import (
    RSI_PERIOD,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    EMA_FAST,
    EMA_SLOW,
    BB_PERIOD,
    BB_STD,
)

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["Close"]

    #  RSI 
    df["RSI"] = ta.momentum.rsi(close, window=RSI_PERIOD)

    #  MACD 
    macd = ta.trend.MACD(
        close,
        window_slow=MACD_SLOW,
        window_fast=MACD_FAST,
        window_sign=MACD_SIGNAL,
    )
    df["MACD"]        = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"]   = macd.macd_diff()

    #  Exponential Moving Averages 
    df["EMA_Fast"] = ta.trend.ema_indicator(close, window=EMA_FAST)
    df["EMA_Slow"] = ta.trend.ema_indicator(close, window=EMA_SLOW)

    #  Bollinger Bands 
    bb = ta.volatility.BollingerBands(
        close, window=BB_PERIOD, window_dev=BB_STD,
    )
    df["BB_Upper"]  = bb.bollinger_hband()
    df["BB_Lower"]  = bb.bollinger_lband()
    df["BB_Middle"] = bb.bollinger_mavg()

    #  Volume SMA (for volume confirmation) 
    df["Vol_SMA"] = df["Volume"].rolling(window=20).mean()

    return df
