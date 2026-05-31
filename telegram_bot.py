#  Telegram Bot — Message Formatting & Sending
import logging
from datetime import datetime, timezone

import requests as _requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, INSTRUMENTS

logger = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


#  low-level send 

def send_message(text: str, parse_mode: str = "HTML") -> bool:
    try:
        resp = _requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id":                  TELEGRAM_CHAT_ID,
                "text":                     text,
                "parse_mode":               parse_mode,
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if resp.status_code == 200 and resp.json().get("ok"):
            logger.info("Telegram message sent ✓")
            return True
        else:
            logger.error(f"Telegram API error: {resp.status_code} — {resp.text}")
            return False
    except Exception as exc:
        logger.error(f"Telegram send failed: {exc}")
        return False


#  signal formatter 

def format_signal(signal: dict) -> str:
    info      = signal["instrument"]
    direction = signal["direction"]

    dir_emoji = "🟢" if direction == "BUY" else "🔴"
    stars     = "⭐" * signal["strength"]

    price = signal["price"]
    price_str = f"${price:,.2f}" if price >= 100 else f"${price:.2f}"

    reasons_block = "\n".join(f"  • {r}" for r in signal["reasons"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return (
        f"{dir_emoji} <b>{direction} SIGNAL — {info['display']}</b> {info['emoji']}\n"
        f"\n"
        f"💰 Price: <code>{price_str}</code>\n"
        f"📊 Strength: {stars} ({signal['strength']}/5)\n"
        f"⏰ Timeframe: M5\n"
        f"\n"
        f"📈 <b>Indicators:</b>\n"
        f"{reasons_block}\n"
        f"\n"
        f"⚠️ <i>Not financial advice. Use proper risk management.</i>\n"
        f"🕐 {now}"
    )


def send_signal(signal: dict) -> bool:
    return send_message(format_signal(signal))


#  utility messages 

def send_startup_message() -> bool:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    instruments_lines = "\n".join(
        f"  • {v['emoji']} {v['display']} ({k})"
        for k, v in INSTRUMENTS.items()
    )
    msg = (
        "🤖 <b>Trading Signal Bot — Online</b>\n"
        "\n"
        "📡 Scanning every <b>1 minute</b> on <b>M75</b> candles\n"
        "\n"
        "📋 <b>Instruments:</b>\n"
        f"{instruments_lines}\n"
        "\n"
        "📊 <b>Strategy:</b> Multi-indicator confluence\n"
        "  RSI · MACD · EMA 9/21 · Bollinger Bands · Volume\n"
        "\n"
        f"🕐 Started at {now}"
    )
    return send_message(msg)


def send_scan_summary(scanned: int, signals_found: int) -> None:
    logger.info(f"Scan done — {scanned} instruments, {signals_found} signal(s)")


def send_error_alert(error_msg: str) -> bool:
    return send_message(
        f"❌ <b>Bot Error</b>\n\n<code>{error_msg[:1000]}</code>"
    )
