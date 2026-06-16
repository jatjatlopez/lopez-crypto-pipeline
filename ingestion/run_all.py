# ============================================================
# run_all.py
# ============================================================
# WHAT THIS FILE DOES:
#   Runs ALL ingestion scripts in order with ONE command.
#
# HOW TO RUN (from project root):
#   python ingestion/run_all.py
#
# ORDER:
#   1) prices   → CoinGecko
#   2) sentiment → Fear/Greed + news
#
# WHY ORDER MATTERS:
#   Later in Airflow, each step is a separate task with retries.
#   Prices failing shouldn't block you from debugging sentiment separately,
#   but for a simple "run everything" entry point, this order is fine.
# ============================================================

from fetch_prices import main as run_prices
from fetch_sentiment import main as run_sentiment


if __name__ == "__main__":
    print("=== Starting full ingestion ===\n")

    run_prices()
    print()

    run_sentiment()
    print()

    print("=== All ingestion complete ===")