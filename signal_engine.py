#  Signal Generation Engine
import logging
from datetime import datetime, timedelta

import pandas as pd

from config import INSTRUMENTS, MIN_SIGNAL_STRENGTH, COOLDOWN_MINUTES

logger = logging.getLogger(__name__)


class SignalEngine:

    def __init__(self):
        # key = "TICKER_DIRECTION" → datetime of last signal
        self._cooldowns: dict[str, datetime] = {}

    #  cooldown helpers 

    def _is_on_cooldown(self, ticker: str, direction: str) -> bool:
        key = f"{ticker}_{direction}"
        last = self._cooldowns.get(key)
        if last and (datetime.now() - last) < timedelta(minutes=COOLDOWN_MINUTES):
            return True
        return False

    def _set_cooldown(self, ticker: str, direction: str):
        self._cooldowns[f"{ticker}_{direction}"] = datetime.now()

    #  core evaluation 

    def evaluate(self, ticker: str, df: pd.DataFrame) -> dict | None:
        if len(df) < 2:
            return None

        cur  = df.iloc[-1]
        prev = df.iloc[-2]

        buy_score,  buy_reasons  = self._score_buy(cur, prev)
        sell_score, sell_reasons = self._score_sell(cur, prev)

        buy_str  = int(round(buy_score))
        sell_str = int(round(sell_score))

        # Pick the stronger direction (if it meets the threshold)
        if buy_str >= MIN_SIGNAL_STRENGTH and buy_str > sell_str:
            return self._build_signal(
                ticker, "BUY", buy_str, cur["Close"], buy_reasons, cur,
            )

        if sell_str >= MIN_SIGNAL_STRENGTH and sell_str > buy_str:
            return self._build_signal(
                ticker, "SELL", sell_str, cur["Close"], sell_reasons, cur,
            )

        return None

    #  BUY scoring 

    @staticmethod
    def _score_buy(cur: pd.Series, prev: pd.Series) -> tuple[float, list[str]]:
        score   = 0.0
        reasons: list[str] = []

        # 1. RSI — approaching oversold
        rsi = cur.get("RSI")
        if pd.notna(rsi) and rsi < 40:
            score += 1
            reasons.append(f"RSI(14): {rsi:.1f} — Oversold ✅")

        # 2. MACD — bullish crossover or bullish state
        macd, macd_s = cur.get("MACD"), cur.get("MACD_Signal")
        p_macd, p_macd_s = prev.get("MACD"), prev.get("MACD_Signal")
        if all(pd.notna(v) for v in [macd, macd_s, p_macd, p_macd_s]):
            if macd > macd_s and p_macd <= p_macd_s:
                score += 1
                reasons.append("MACD: Bullish Crossover ✅")
            elif macd > macd_s:
                score += 0.5
                reasons.append("MACD: Bullish ✅")

        # 3. EMA 9/21 — bullish cross or bullish alignment
        ema_f, ema_s = cur.get("EMA_Fast"), cur.get("EMA_Slow")
        p_ema_f, p_ema_s = prev.get("EMA_Fast"), prev.get("EMA_Slow")
        if all(pd.notna(v) for v in [ema_f, ema_s, p_ema_f, p_ema_s]):
            if ema_f > ema_s and p_ema_f <= p_ema_s:
                score += 1
                reasons.append("EMA 9/21: Bullish Cross ✅")
            elif ema_f > ema_s:
                score += 0.5
                reasons.append("EMA 9/21: Bullish ✅")

        # 4. Bollinger Bands — price near lower band
        bb_lo, bb_mid = cur.get("BB_Lower"), cur.get("BB_Middle")
        if pd.notna(bb_lo) and pd.notna(bb_mid):
            bb_range = bb_mid - bb_lo
            if bb_range > 0:
                position = (cur["Close"] - bb_lo) / bb_range
                if position < 0.3:
                    score += 1
                    reasons.append("Bollinger: Near Lower Band ✅")

        # 5. Volume spike
        vol, vol_sma = cur.get("Volume"), cur.get("Vol_SMA")
        if pd.notna(vol) and pd.notna(vol_sma) and vol_sma > 0:
            if vol > vol_sma * 1.2:
                score += 1
                reasons.append("Volume: Above Average ✅")

        return score, reasons
    #   print("signal triggered!")
    
    #  SELL scoring 

    @staticmethod
    def _score_sell(cur: pd.Series, prev: pd.Series) -> tuple[float, list[str]]:
        score   = 0.0
        reasons: list[str] = []

        # 1. RSI — approaching overbought
        rsi = cur.get("RSI")
        if pd.notna(rsi) and rsi > 60:
            score += 1
            reasons.append(f"RSI(14): {rsi:.1f} — Overbought ✅")

        # 2. MACD — bearish crossover or bearish state
        macd, macd_s = cur.get("MACD"), cur.get("MACD_Signal")
        p_macd, p_macd_s = prev.get("MACD"), prev.get("MACD_Signal")
        if all(pd.notna(v) for v in [macd, macd_s, p_macd, p_macd_s]):
            if macd < macd_s and p_macd >= p_macd_s:
                score += 1
                reasons.append("MACD: Bearish Crossover ✅")
            elif macd < macd_s:
                score += 0.5
                reasons.append("MACD: Bearish ✅")

        # 3. EMA 9/21 — bearish cross or bearish alignment
        ema_f, ema_s = cur.get("EMA_Fast"), cur.get("EMA_Slow")
        p_ema_f, p_ema_s = prev.get("EMA_Fast"), prev.get("EMA_Slow")
        if all(pd.notna(v) for v in [ema_f, ema_s, p_ema_f, p_ema_s]):
            if ema_f < ema_s and p_ema_f >= p_ema_s:
                score += 1
                reasons.append("EMA 9/21: Bearish Cross ✅")
            elif ema_f < ema_s:
                score += 0.5
                reasons.append("EMA 9/21: Bearish ✅")

        # 4. Bollinger Bands — price near upper band
        bb_up, bb_mid = cur.get("BB_Upper"), cur.get("BB_Middle")
        if pd.notna(bb_up) and pd.notna(bb_mid):
            bb_range = bb_up - bb_mid
            if bb_range > 0:
                position = (bb_up - cur["Close"]) / bb_range
                if position < 0.3:
                    score += 1
                    reasons.append("Bollinger: Near Upper Band ✅")

        # 5. Volume spike
        vol, vol_sma = cur.get("Volume"), cur.get("Vol_SMA")
        if pd.notna(vol) and pd.notna(vol_sma) and vol_sma > 0:
            if vol > vol_sma * 1.2:
                score += 1
                reasons.append("Volume: Above Average ✅")

        return score, reasons

    #  signal builder 

    def _build_signal(
        self,
        ticker: str,
        direction: str,
        strength: int,
        price: float,
        reasons: list[str],
        cur: pd.Series,
    ) -> dict | None:
        if self._is_on_cooldown(ticker, direction):
            logger.debug(f"[{ticker}] {direction} signal on cooldown — skipped")
            return None

        self._set_cooldown(ticker, direction)

        signal = {
            "ticker":     ticker,
            "direction":  direction,
            "strength":   min(strength, 5),
            "price":      float(price),
            "reasons":    reasons,
            "rsi":        cur.get("RSI"),
            "instrument": INSTRUMENTS[ticker],
        }
        logger.info(
            f"✨ SIGNAL  {direction}  {INSTRUMENTS[ticker]['display']} "
            f"({ticker})  strength={signal['strength']}/5  price={price:.2f}"
        )
        return signal
