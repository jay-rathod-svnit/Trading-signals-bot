#  CME Trading Signal Bot — Entry Point
import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

from config import SCAN_INTERVAL_SECONDS, INSTRUMENTS
from data_fetcher import fetch_all_instruments
from indicators import compute_indicators
from signal_engine import SignalEngine
from telegram_bot import (
    send_signal,
    send_startup_message,
    send_error_alert,
)

#  Logging setup 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("TradingBot")

#  Global signal engine (keeps cooldown state) 
engine = SignalEngine()


#  Scanner 
def scan_markets():
    """Fetch data → compute indicators → evaluate signals → notify."""
    logger.info("── Scanning markets ─────────────────────────")

    try:
        data = fetch_all_instruments()

        if not data:
            logger.warning("No data fetched for any instrument this cycle")
            return

        signals_found = 0

        for ticker, df in data.items():
            try:
                df_ind = compute_indicators(df)
                signal = engine.evaluate(ticker, df_ind)

                if signal:
                    signals_found += 1
                    ok = send_signal(signal)
                    if ok:
                        logger.info(f"Signal sent → {signal['direction']} {ticker}")
                    else:
                        logger.error(f"Failed to send signal for {ticker}")
            except Exception as exc:
                logger.error(f"Error processing {ticker}: {exc}", exc_info=True)

        logger.info(f"Scan complete — {len(data)} instruments, {signals_found} signal(s)")

    except Exception as exc:
        logger.error(f"Scan cycle error: {exc}", exc_info=True)
        try:
            send_error_alert(str(exc))
        except Exception:
            pass


#  Main 

def main():
    banner = (
        "\n"
        "     CME Trading Signal Bot  —  Starting      \n"
    )
    logger.info(banner)

    # Show configured instruments
    for ticker, info in INSTRUMENTS.items():
        logger.info(f"  {info['emoji']}  {info['display']:12s}  →  {ticker}")

    # Telegram startup notification
    logger.info("Sending startup message to Telegram...")
    if send_startup_message():
        logger.info("Startup message delivered ✓")
    else:
        logger.warning("Could not send startup message — check token / chat ID")

    # Run an immediate first scan
    logger.info("Running initial market scan...")
    scan_markets()

    # Schedule recurring scans
    scheduler = BlockingScheduler()
    scheduler.add_job(
        scan_markets,
        "interval",
        seconds=SCAN_INTERVAL_SECONDS,
        id="market_scanner",
        max_instances=1,
        coalesce=True,
    )

    logger.info(
        f"Scheduler active — scanning every {SCAN_INTERVAL_SECONDS}s  "
        f"(Ctrl+C to stop)"
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
