# 🤖 CME Trading Signal Bot

A Python-based **automated trading signal bot** that monitors CME instruments in real-time, generates **multi-indicator confluence signals**, and delivers instant alerts to **Telegram**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📋 Table of Contents

- [Features](#-features)
- [Instruments Monitored](#-instruments-monitored)
- [Signal Strategy](#-signal-strategy)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Telegram Message Format](#-telegram-message-format)
- [Cloud Deployment (24/7)](#-cloud-deployment-247)
  - [Option 1 — Railway.app](#option-1--railwayapp--easiest)
  - [Option 2 — Oracle Cloud Always Free](#option-2--oracle-cloud-always-free--free-forever)
  - [Option 3 — VPS + Docker](#option-3--any-vps--docker)
- [Code Documentation](#-code-documentation)
  - [config.py](#configpy)
  - [data_fetcher.py](#data_fetcherpy)
  - [indicators.py](#indicatorspy)
  - [signal_engine.py](#signal_enginepy)
  - [telegram_bot.py](#telegram_botpy)
  - [main.py](#mainpy)
- [How It Works](#-how-it-works)
- [Customization](#-customization)
- [Disclaimer](#-disclaimer)

---

## ✨ Features

- 📡 **Real-time scanning** — scans every **1 minute** on **5-minute candles**
- 📊 **Multi-indicator confluence** — signals require ≥3/5 indicators to agree
- 🔔 **Instant Telegram alerts** — formatted messages with emojis, price, and indicator breakdown
- 🧊 **Smart cooldown** — prevents duplicate alerts (15-min cooldown per instrument per direction)
- 🛡️ **Error resilient** — retry logic, graceful error handling, Telegram error alerts
- 🐳 **Docker ready** — deploy anywhere with one command
- 📈 **5 Technical Indicators** — RSI, MACD, EMA Crossover, Bollinger Bands, Volume

---

## 📈 Instruments Monitored

| Instrument | Ticker | Exchange |
|:---|:---|:---|
| 🇺🇸 S&P 500 E-mini | `ES=F` | CME |
| 🛢️ WTI Crude Oil | `CL=F` | NYMEX |
| 🥇 Gold (XAUUSD) | `GC=F` | COMEX |
| ₿ Bitcoin (BTCUSD) | `BTC-USD` | Yahoo Finance |

Data is fetched via **yfinance** (free, no API key required).

---

## 🎯 Signal Strategy

The bot uses a **multi-indicator confluence** approach. A signal is only generated when **3 or more indicators agree** on the same direction.

### Indicators Used

| # | Indicator | BUY Condition | SELL Condition |
|:---|:---|:---|:---|
| 1 | **RSI (14)** | RSI < 40 (oversold zone) | RSI > 60 (overbought zone) |
| 2 | **MACD (12, 26, 9)** | MACD crosses above signal line | MACD crosses below signal line |
| 3 | **EMA Crossover (9/21)** | EMA 9 crosses above EMA 21 | EMA 9 crosses below EMA 21 |
| 4 | **Bollinger Bands (20, 2)** | Price near lower band (<30% range) | Price near upper band (<30% range) |
| 5 | **Volume** | Volume > 120% of 20-period SMA | Volume > 120% of 20-period SMA |

### Signal Strength

- Each confirmed indicator adds **+1** to the score (partial confirms add **+0.5**)
- **Minimum score of 3** required to trigger a signal
- Strength displayed as ⭐ stars (1–5)

### Cooldown Logic

- After a signal fires, the **same instrument + direction** is on a **15-minute cooldown**
- This prevents spam when scanning every 60 seconds

---

## 📁 Project Structure

```
trading_bot/
├── config.py            # All configuration constants
├── data_fetcher.py      # Fetches OHLCV data via yfinance
├── indicators.py        # Technical indicator calculations (RSI, MACD, EMA, BB)
├── signal_engine.py     # Signal evaluation & cooldown logic
├── telegram_bot.py      # Telegram message formatting & sending
├── main.py              # Entry point — scheduler & orchestration
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container for cloud deployment
├── Procfile             # For Railway / Render deployment
├── .dockerignore        # Docker build exclusions
└── README.md            # This file
```

---

## ⚙️ Prerequisites

- **Python 3.10+**
- A **Telegram Bot** (create one via [@BotFather](https://t.me/BotFather))
- Your **Telegram Chat ID** (use [@userinfobot](https://t.me/userinfobot) or group ID for groups)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/trading-signal-bot.git
cd trading-signal-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the bot

Edit `config.py` with your Telegram credentials:

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID   = "YOUR_CHAT_ID_HERE"
```

### 4. Run the bot

```bash
python main.py
```

---

## 🔧 Configuration

All settings are in **`config.py`**:

```python
# ── Telegram ──────────────────────────────────
TELEGRAM_BOT_TOKEN = "your-bot-token"
TELEGRAM_CHAT_ID   = "your-chat-id"

# ── Instruments ───────────────────────────────
INSTRUMENTS = {
    "ES=F":    {"name": "S&P 500 E-mini Futures", "display": "S&P 500",    "emoji": "🇺🇸"},
    "CL=F":    {"name": "WTI Crude Oil Futures",  "display": "Crude Oil",  "emoji": "🛢️"},
    "GC=F":    {"name": "COMEX Gold Futures",     "display": "XAUUSD",     "emoji": "🥇"},
    "BTC-USD": {"name": "Bitcoin",                "display": "BTCUSD",     "emoji": "₿"},
}

# ── Technical Indicator Parameters ────────────
RSI_PERIOD   = 14       # RSI lookback period
MACD_FAST    = 12       # MACD fast EMA
MACD_SLOW    = 26       # MACD slow EMA
MACD_SIGNAL  = 9        # MACD signal line
EMA_FAST     = 9        # Fast EMA period
EMA_SLOW     = 21       # Slow EMA period
BB_PERIOD    = 20       # Bollinger Bands period
BB_STD       = 2        # Bollinger Bands std deviation

# ── Scan Settings ─────────────────────────────
SCAN_INTERVAL_SECONDS = 60    # Scan every 1 minute
CANDLE_INTERVAL       = "5m"  # 5-minute candles
YF_PERIOD             = "5d"  # Fetch last 5 days of data
COOLDOWN_MINUTES      = 15    # Signal cooldown
MIN_SIGNAL_STRENGTH   = 3     # Minimum indicators to agree
```

---

## 💬 Telegram Message Format

When a signal triggers, you receive a message like this:

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

On startup, you also receive:

```
🤖 Trading Signal Bot — Online

📡 Scanning every 1 minute on M5 candles

📋 Instruments:
  • 🇺🇸 S&P 500 (ES=F)
  • 🛢️ Crude Oil (CL=F)
  • 🥇 XAUUSD (GC=F)
  • ₿ BTCUSD (BTC-USD)

📊 Strategy: Multi-indicator confluence
  RSI · MACD · EMA 9/21 · Bollinger Bands · Volume

🕐 Started at 2026-05-26 14:15 UTC
```

---

## ☁️ Cloud Deployment (24/7)

### Option 1 — Railway.app ⭐ Easiest

**Cost**: ~$5/month | **Setup**: 5 minutes

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → Sign in with GitHub
3. **New Project** → **Deploy from GitHub Repo** → Select your repo
4. Railway auto-detects the `Dockerfile` and deploys
5. Bot starts running — check Telegram for the startup message

---

### Option 2 — Oracle Cloud Always Free 🏆 Free Forever

**Cost**: **$0/month forever** | **Setup**: 20 minutes

1. Sign up at [cloud.oracle.com](https://cloud.oracle.com) (Always Free tier)
2. Create a **VM.Standard.E2.1.Micro** instance (Ubuntu 22.04)
3. SSH into the VM:
   ```bash
   ssh -i your_key.pem ubuntu@YOUR_VM_IP
   ```
4. Install dependencies:
   ```bash
   sudo apt update && sudo apt install -y python3 python3-pip git
   git clone https://github.com/YOUR_USERNAME/trading-signal-bot.git
   cd trading-signal-bot
   pip3 install -r requirements.txt
   ```
5. Create a systemd service for auto-restart:
   ```bash
   sudo nano /etc/systemd/system/trading-bot.service
   ```
   ```ini
   [Unit]
   Description=CME Trading Signal Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/trading-signal-bot
   ExecStart=/usr/bin/python3 main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl enable trading-bot
   sudo systemctl start trading-bot
   ```
6. Check status:
   ```bash
   sudo systemctl status trading-bot     # status
   sudo journalctl -u trading-bot -f     # live logs
   ```

---

### Option 3 — Any VPS + Docker

**Cost**: $3–6/month | **Setup**: 15 minutes

1. Get a VPS (Hetzner €3.29/mo, DigitalOcean $4/mo, Vultr $3.50/mo)
2. SSH in and install Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
3. Clone, build, and run:
   ```bash
   git clone https://github.com/YOUR_USERNAME/trading-signal-bot.git
   cd trading-signal-bot
   docker build -t trading-bot .
   docker run -d --restart always --name trading-bot trading-bot
   ```
4. View logs:
   ```bash
   docker logs -f trading-bot
   ```

### Deployment Comparison

| Platform | Cost | Setup | Auto-Restart | Best For |
|:---|:---|:---|:---|:---|
| Railway | ~$5/mo | 5 min | ✅ | Fastest setup |
| Oracle Cloud | **FREE** | 20 min | ✅ (systemd) | Zero cost, long-term |
| VPS + Docker | $3–6/mo | 15 min | ✅ (docker) | Full control |

---

## 📖 Code Documentation

### `config.py`

Central configuration file containing all tunable parameters.

```python
# Telegram credentials
TELEGRAM_BOT_TOKEN = "your-token"    # From @BotFather
TELEGRAM_CHAT_ID   = "your-chat-id"  # User or group chat ID

# Instruments dictionary maps Yahoo Finance tickers to display metadata
INSTRUMENTS = {
    "ES=F":    {"name": "...", "display": "S&P 500",   "emoji": "🇺🇸"},
    "CL=F":    {"name": "...", "display": "Crude Oil", "emoji": "🛢️"},
    "GC=F":    {"name": "...", "display": "XAUUSD",    "emoji": "🥇"},
    "BTC-USD": {"name": "...", "display": "BTCUSD",    "emoji": "₿"},
}

# Indicator parameters, scan interval, cooldown duration
```

**Key settings to customize:**
- `SCAN_INTERVAL_SECONDS` — how often to scan (default: 60s)
- `MIN_SIGNAL_STRENGTH` — minimum indicator agreement (default: 3/5)
- `COOLDOWN_MINUTES` — gap between repeat signals (default: 15 min)

---

### `data_fetcher.py`

Fetches 5-minute OHLCV (Open, High, Low, Close, Volume) candle data from Yahoo Finance.

**Key functions:**

| Function | Description |
|:---|:---|
| `fetch_candles(ticker)` | Fetches M5 candles for a single ticker with retry logic |
| `fetch_all_instruments()` | Fetches candles for all 4 instruments, returns dict of DataFrames |

**How it works:**
1. Uses `yf.Ticker(ticker).history()` for clean single-level column names
2. Pulls last 5 days of 5-minute data (~880+ candles per instrument)
3. Retries up to 2 times with exponential backoff on failure
4. Adds a 0.5s pause between instruments to avoid rate-limiting

```python
# Example usage
from data_fetcher import fetch_all_instruments

data = fetch_all_instruments()
# data = {
#     "ES=F":    <DataFrame with 881 rows>,
#     "CL=F":    <DataFrame with 884 rows>,
#     "GC=F":    <DataFrame with 884 rows>,
#     "BTC-USD": <DataFrame with 1330 rows>,
# }
```

---

### `indicators.py`

Computes all technical indicators using the [`ta`](https://github.com/bukosabino/ta) library.

**Function:** `compute_indicators(df)` → Returns enriched DataFrame

**Indicators added to DataFrame:**

| Column | Indicator | Parameters |
|:---|:---|:---|
| `RSI` | Relative Strength Index | period=14 |
| `MACD` | MACD line | fast=12, slow=26 |
| `MACD_Signal` | MACD signal line | signal=9 |
| `MACD_Hist` | MACD histogram | — |
| `EMA_Fast` | Fast EMA | period=9 |
| `EMA_Slow` | Slow EMA | period=21 |
| `BB_Upper` | Bollinger upper band | period=20, std=2 |
| `BB_Lower` | Bollinger lower band | period=20, std=2 |
| `BB_Middle` | Bollinger middle band | period=20 |
| `Vol_SMA` | Volume SMA | period=20 |

```python
# Example usage
from indicators import compute_indicators

df_enriched = compute_indicators(df)
print(df_enriched[["Close", "RSI", "MACD", "EMA_Fast", "EMA_Slow"]].tail())
```

---

### `signal_engine.py`

Core signal generation logic with confluence scoring and cooldown management.

**Class:** `SignalEngine`

| Method | Description |
|:---|:---|
| `evaluate(ticker, df)` | Main entry — evaluates latest candle, returns signal dict or None |
| `_score_buy(cur, prev)` | Scores BUY conditions across all 5 indicators |
| `_score_sell(cur, prev)` | Scores SELL conditions across all 5 indicators |
| `_is_on_cooldown(ticker, dir)` | Checks if a signal is within cooldown period |
| `_set_cooldown(ticker, dir)` | Records a signal timestamp for cooldown tracking |

**Signal dict structure:**
```python
{
    "ticker":     "GC=F",
    "direction":  "BUY",
    "strength":   4,               # 1-5
    "price":      2347.80,
    "reasons":    ["RSI(14): 28.3 — Oversold ✅", ...],
    "rsi":        28.3,
    "instrument": {"name": "...", "display": "XAUUSD", "emoji": "🥇"},
}
```

**Scoring logic:**
- **Full point (+1.0)**: Crossover detected (e.g., MACD just crossed, EMA just crossed)
- **Half point (+0.5)**: Indicator in favorable state but no fresh crossover
- **Threshold**: Signal fires only when `score ≥ 3` (configurable via `MIN_SIGNAL_STRENGTH`)

---

### `telegram_bot.py`

Handles all Telegram communication via the Bot API.

| Function | Description |
|:---|:---|
| `send_message(text)` | Low-level: sends any HTML message to the configured chat |
| `format_signal(signal)` | Formats a signal dict into a rich HTML message |
| `send_signal(signal)` | Formats + sends a trading signal |
| `send_startup_message()` | Sends "Bot Online" notification with instrument list |
| `send_error_alert(msg)` | Sends error notifications to Telegram |

**API endpoint used:** `POST https://api.telegram.org/bot{TOKEN}/sendMessage`

---

### `main.py`

Entry point that orchestrates everything.

**Flow:**
1. Configures logging with formatted output
2. Sends startup notification to Telegram
3. Runs an immediate first scan
4. Starts APScheduler with 60-second interval
5. Each scan cycle: `fetch data → compute indicators → evaluate signals → send alerts`
6. Handles graceful shutdown on `Ctrl+C`

```
╔══════════════════════════════════════════════╗
║     CME Trading Signal Bot  —  Starting      ║
╚══════════════════════════════════════════════╝

2026-05-26 20:19:00 │ INFO │ Sending startup message to Telegram...
2026-05-26 20:19:01 │ INFO │ Startup message delivered ✓
2026-05-26 20:19:01 │ INFO │ Running initial market scan...
2026-05-26 20:19:03 │ INFO │ [ES=F] Fetched 881 candles
2026-05-26 20:19:04 │ INFO │ [CL=F] Fetched 884 candles
2026-05-26 20:19:05 │ INFO │ [GC=F] Fetched 884 candles
2026-05-26 20:19:06 │ INFO │ [BTC-USD] Fetched 1330 candles
2026-05-26 20:19:07 │ INFO │ Scan complete — 4 instruments, 0 signal(s)
2026-05-26 20:19:07 │ INFO │ Scheduler active — scanning every 60s
```

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    EVERY 60 SECONDS                         │
│                                                             │
│  ┌──────────┐    ┌────────────┐    ┌───────────────────┐   │
│  │ yfinance │───▶│ indicators │───▶│  signal_engine    │   │
│  │ M5 OHLCV │    │ RSI, MACD  │    │  Score BUY/SELL   │   │
│  │ candles  │    │ EMA, BB    │    │  Check cooldown   │   │
│  └──────────┘    └────────────┘    └─────────┬─────────┘   │
│                                              │              │
│                                    ┌─────────▼─────────┐   │
│                                    │  Score ≥ 3/5 ?     │   │
│                                    └─────────┬─────────┘   │
│                                        YES   │   NO        │
│                                    ┌─────────▼───┐  │      │
│                                    │  Telegram   │  └─skip  │
│                                    │  Send Alert │         │
│                                    └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Customization

### Add a new instrument

Edit `INSTRUMENTS` in `config.py`:

```python
INSTRUMENTS = {
    # ... existing instruments ...
    "NQ=F": {"name": "Nasdaq 100 Futures", "display": "Nasdaq 100", "emoji": "📱"},
}
```

### Change signal sensitivity

```python
MIN_SIGNAL_STRENGTH = 2   # More signals (lower threshold)
MIN_SIGNAL_STRENGTH = 4   # Fewer, higher-quality signals
```

### Change scan frequency

```python
SCAN_INTERVAL_SECONDS = 30    # Scan every 30 seconds
SCAN_INTERVAL_SECONDS = 300   # Scan every 5 minutes
```

### Change candle timeframe

```python
CANDLE_INTERVAL = "1m"    # 1-minute candles (more noise)
CANDLE_INTERVAL = "15m"   # 15-minute candles (less noise)
CANDLE_INTERVAL = "1h"    # 1-hour candles (swing trading)
```

---

## ⚠️ Disclaimer

> **This bot is for educational and informational purposes only.**
>
> - This is **NOT financial advice**
> - Past performance does not guarantee future results
> - Always use proper **risk management** and **position sizing**
> - The authors are not responsible for any financial losses
> - **yfinance data may be delayed** (~15 minutes) — not suitable for scalping
> - Test thoroughly with a **demo account** before using real capital

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for traders who want automated signals without the noise.
</p>
