# ──────────────────────────────────────────────
#  CME Trading Signal Bot — Configuration
# ──────────────────────────────────────────────

# ── Telegram ──────────────────────────────────
TELEGRAM_BOT_TOKEN = "8232342634:AAFQhSzBxPubBF0mB8VoB7PYyG-KkZ-CLqk"
TELEGRAM_CHAT_ID   = "-1003974022501"

# ── Instruments ───────────────────────────────
#    ticker  →  { display name, emoji }
INSTRUMENTS = {
    "ES=F":    {"name": "S&P 500 E-mini Futures", "display": "S&P 500",    "emoji": "🇺🇸"},
    "CL=F":    {"name": "WTI Crude Oil Futures",  "display": "Crude Oil",  "emoji": "🛢️"},
    "GC=F":    {"name": "COMEX Gold Futures",     "display": "XAUUSD",     "emoji": "🥇"},
    "BTC-USD": {"name": "Bitcoin",                "display": "BTCUSD",     "emoji": "₿"},
}

# ── Technical Indicator Parameters ────────────
RSI_PERIOD   = 14
MACD_FAST    = 12
MACD_SLOW    = 26
MACD_SIGNAL  = 9
EMA_FAST     = 9
EMA_SLOW     = 21
BB_PERIOD    = 20
BB_STD       = 2

# ── Scan Settings ─────────────────────────────
SCAN_INTERVAL_SECONDS = 60        # Run scanner every 1 minute
CANDLE_INTERVAL       = "5m"      # 5-minute candles
YF_PERIOD             = "5d"      # Pull last 5 days of M5 data
COOLDOWN_MINUTES      = 15        # Min gap between same signal
MIN_SIGNAL_STRENGTH   = 3         # At least 3/5 indicators must agree
