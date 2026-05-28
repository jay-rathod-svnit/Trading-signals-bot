# 🤖 CME Trading Signal Bot

Hey! This is a Python bot I built that watches CME futures markets and pings me on Telegram whenever it spots a good trading opportunity. It scans **every minute** on **5-minute candles** and only alerts when multiple indicators line up — so you're not drowning in noise.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## What does it do?

In short — it watches 4 markets, crunches the numbers every 60 seconds, and sends you a Telegram message when things look interesting.

- 🇺🇸 **S&P 500** (ES=F)
- 🛢️ **Crude Oil** (CL=F)
- 🥇 **Gold / XAUUSD** (GC=F)
- ₿ **Bitcoin / BTCUSD** (BTC-USD)

Data comes from **yfinance** — it's free, no API key needed. The tradeoff is data can be ~15 min delayed, but for M5 swing signals that's totally fine.

---

## How signals work

I didn't want a bot that cries wolf every 5 minutes. So it uses a **confluence approach** — a signal only fires when **at least 3 out of 5** indicators agree on the same direction.

### The 5 indicators

| Indicator | What it checks |
|:---|:---|
| **RSI (14)** | Is the market oversold (<40) or overbought (>60)? |
| **MACD (12/26/9)** | Did the MACD just cross its signal line? |
| **EMA 9/21** | Did the fast EMA cross the slow one? |
| **Bollinger Bands** | Is price hugging the upper or lower band? |
| **Volume** | Is volume 20%+ above average? (confirms the move is real) |

### When you get a BUY alert
RSI is low + MACD crossed up + EMAs are bullish + price is near the lower Bollinger Band. Basically, "this thing looks oversold and momentum is shifting up."

### When you get a SELL alert
The opposite — RSI is high, MACD crossed down, EMAs bearish, price near the upper band.

### Cooldowns
Once a signal fires for an instrument, the bot won't send another one in the **same direction for 15 minutes**. This keeps your Telegram from blowing up when the market is choppy.

---

## What the Telegram alerts look like

```
🟢 BUY SIGNAL — XAUUSD 🥇

💰 Price: $2,347.80
📊 Strength: ⭐⭐⭐⭐ (4/5)
⏰ Timeframe: M5

📈 Indicators:
  • RSI(14): 28.3 — Oversold ✅
  • MACD: Bullish Crossover ✅
  • EMA 9/21: Bullish Cross ✅
  • Bollinger: Near Lower Band ✅
  • Volume: Above Average ✅

⚠️ Not financial advice. Use proper risk management.
🕐 2026-05-26 14:15 UTC
```

When the bot starts up, it also sends a "I'm online" message so you know it's running.

---

## Project structure

Nothing fancy — just 6 Python files and a requirements file:

```
trading_bot/
├── config.py          ← settings (Telegram token, tickers, indicator params)
├── data_fetcher.py    ← pulls candle data from Yahoo Finance
├── indicators.py      ← calculates RSI, MACD, EMAs, Bollinger Bands
├── signal_engine.py   ← decides if a signal should fire
├── telegram_bot.py    ← formats and sends Telegram messages
├── main.py            ← runs the whole thing on a 60-second loop
└── requirements.txt   ← pip dependencies
```

---

## Getting started

### 1. Clone it

```bash
git clone https://github.com/YOUR_USERNAME/trading-signal-bot.git
cd trading-signal-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your Telegram bot

If you haven't already:
1. Open Telegram, search for **@BotFather**
2. Send `/newbot`, follow the prompts, get your **bot token**
3. Get your **chat ID** (send a message to your bot, then check `https://api.telegram.org/bot<TOKEN>/getUpdates`)

### 4. Configure

Open `config.py` and plug in your credentials:

```python
TELEGRAM_BOT_TOKEN = "your-bot-token-here"
TELEGRAM_CHAT_ID   = "your-chat-id-here"
```

### 5. Run it

```bash
python main.py
```

You should see something like:

```
╔══════════════════════════════════════════════╗
║     CME Trading Signal Bot  —  Starting      ║
╚══════════════════════════════════════════════╝

2026-05-26 20:19:00 │ INFO │ Sending startup message to Telegram...
2026-05-26 20:19:01 │ INFO │ Startup message delivered ✓
2026-05-26 20:19:03 │ INFO │ [ES=F] Fetched 881 candles
2026-05-26 20:19:04 │ INFO │ [CL=F] Fetched 884 candles
2026-05-26 20:19:05 │ INFO │ [GC=F] Fetched 884 candles
2026-05-26 20:19:06 │ INFO │ [BTC-USD] Fetched 1330 candles
2026-05-26 20:19:07 │ INFO │ Scan complete — 4 instruments, 0 signal(s)
2026-05-26 20:19:07 │ INFO │ Scheduler active — scanning every 60s
```

Hit `Ctrl+C` to stop.

---

## Tweaking it

Everything's in `config.py`. Here's some stuff you might want to change:

**Want more signals?** Lower the threshold:
```python
MIN_SIGNAL_STRENGTH = 2   # fires when just 2 indicators agree
```

**Want fewer, higher-quality signals?** Raise it:
```python
MIN_SIGNAL_STRENGTH = 4   # needs 4 out of 5 to agree
```

**Want to scan less often?**
```python
SCAN_INTERVAL_SECONDS = 300   # every 5 minutes instead of every 1
```

**Want to track more instruments?** Just add them:
```python
INSTRUMENTS = {
    # ... existing ones ...
    "NQ=F": {"name": "Nasdaq 100 Futures", "display": "Nasdaq 100", "emoji": "📱"},
    "SI=F": {"name": "Silver Futures",     "display": "XAGUSD",     "emoji": "🥈"},
}
```

**Want a different timeframe?**
```python
CANDLE_INTERVAL = "15m"   # 15-minute candles
CANDLE_INTERVAL = "1h"    # hourly candles
```

---

## How it works under the hood

Pretty straightforward loop:

```
Every 60 seconds:
  1. Pull 5-min candles for all 4 instruments (yfinance)
  2. Calculate RSI, MACD, EMA, Bollinger Bands, Volume SMA
  3. Score BUY and SELL conditions (0–5 each)
  4. If score ≥ 3 and not on cooldown → send Telegram alert
  5. Log results, wait for next cycle
```

The bot is resilient — if yfinance fails for one instrument, it skips it and continues with the rest. If Telegram is down, it logs the error and retries next cycle. No crashes.

---

## Dependencies

Just 5 packages, nothing exotic:

| Package | What for |
|:---|:---|
| `yfinance` | Market data from Yahoo Finance |
| `pandas` | Data manipulation |
| `ta` | Technical indicator calculations |
| `requests` | Talking to Telegram API |
| `apscheduler` | Running the scan loop on a timer |

---

## Disclaimer

This is a personal project. **It's not financial advice.** Markets are unpredictable and signals are just signals — they're not guarantees. Always use proper risk management, never risk money you can't afford to lose, and test with a paper trading account first.

The yfinance data can be delayed (~15 min), so don't use this for scalping.

---

## License

MIT — do whatever you want with it.

---

*Built because I got tired of staring at charts all day. Now the bot does it for me.*
