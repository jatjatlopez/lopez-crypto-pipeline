# ============================================================
# fetch_sentiment.py
# ============================================================
# WHAT THIS FILE DOES (one sentence):
#   Downloads SENTIMENT signals from two free APIs and saves them
#   as raw JSON files on your computer.
#
# TWO DATA SOURCES:
#   1) Fear & Greed Index  → overall market mood (one number 0–100)
#   2) Crypto news         → headlines (for hype/panic + Time-Travel Ledger later)
#
# HOW TO RUN:
#   python ingestion/fetch_sentiment.py
#
# WHERE DATA GOES:
#   data/fear_greed/YYYYMMDD_HHMMSS.json
#   data/news/YYYYMMDD_HHMMSS.json
#
# WHERE STATE GOES:
#   ingestion/state.json  (updates news_last_run + fear_greed_last_run)
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
import json          # read/write JSON files
from datetime import datetime, timezone  # timestamps
from pathlib import Path                 # file paths

import requests      # HTTP calls to APIs

from s3_upload import upload_to_s3

# NOTE: no dotenv here — both sentiment APIs are free with NO API key needed.


# ------------------------------------------------------------
# PATHS — same pattern as fetch_prices.py
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = PROJECT_ROOT / "data" / "news"              # headline JSON files
FEAR_GREED_DIR = PROJECT_ROOT / "data" / "fear_greed"  # mood score JSON files
STATE_FILE = PROJECT_ROOT / "ingestion" / "state.json"  # shared with prices script


# ------------------------------------------------------------
# PHASE 2: HIVE PARTITIONS — folder path by year/month/day/hour
# ------------------------------------------------------------
# WHY "year=2026" and not just "2026"?
#   Spark, Databricks, and AWS Athena recognize key=value folders as PARTITIONS.
#   Query "hour=04" → they skip all other hours (fast + cheap).
#
# WHY always "data.json" as the filename?
#   The FOLDER path carries the time. Filename stays constant.
#   Running twice in the same hour OVERWRITES that hour's snapshot (correct for hourly jobs).

def build_partition_path(base_dir, run_time):
    """
    Build: base_dir/year=YYYY/month=MM/day=DD/hour=HH/data.json

    base_dir  → DATA_DIR, NEWS_DIR, or FEAR_GREED_DIR
    run_time  → UTC datetime from main()
    """
    partition_dir = (
        base_dir
        / f"year={run_time.year}"
        / f"month={run_time.month:02d}"   # :02d pads 6 → "06" (sorts correctly)
        / f"day={run_time.day:02d}"
        / f"hour={run_time.hour:02d}"
    )
    partition_dir.mkdir(parents=True, exist_ok=True)  # create folders if missing
    return partition_dir / "data.json"


# ------------------------------------------------------------
# STATE HELPERS — identical idea to fetch_prices.py
# ------------------------------------------------------------
# This script updates TWO keys in state.json:
#   - news_last_run
#   - fear_greed_last_run
# It does NOT touch prices_last_run (that's fetch_prices.py's job).

def load_state():
    """Read state.json into a Python dict."""
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    """Write dict back to state.json."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# ------------------------------------------------------------
# FETCH #1 — Fear & Greed Index (macro sentiment)
# ------------------------------------------------------------
def fetch_fear_greed():
    """
    Calls alternative.me — a free Fear & Greed Index.

    Scale:
      0–24   = Extreme Fear   (panic selling)
      25–49  = Fear
      50–74  = Greed
      75–100 = Extreme Greed  (hype / FOMO)

    Used later for: Sentiment Heatmap, Hype-to-Volume Matrix overlay.
    """
    url = "https://api.alternative.me/fng/"
    params = {"limit": 1}  # only the latest reading (not historical)

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()  # stop if API fails
    return response.json()


# ------------------------------------------------------------
# FETCH #2 — Crypto news headlines
# ------------------------------------------------------------
def fetch_news(limit=20):
    """
    Calls cryptocurrency.cv — free crypto news aggregator.
    Replaces CryptoPanic (which is paid now).

    Returns recent headlines with titles, links, timestamps.
    Used later for: Time-Travel Ledger (headlines during a crash).
    """
    url = "https://cryptocurrency.cv/api/news"
    params = {"limit": limit}  # max articles per request (keep modest)

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


# ------------------------------------------------------------
# SAVE — one reusable function for BOTH sentiment sources
# ------------------------------------------------------------
def save_payload(folder, source_name, api_response, run_time):
    """
    Generic save function — works for fear/greed AND news.

    Parameters:
      folder        → which data/ subfolder (NEWS_DIR or FEAR_GREED_DIR)
      source_name   → label stored in JSON ("alternative.me_fng", etc.)
      api_response  → raw dict/list from the API (unchanged)
      run_time      → when OUR script ran (UTC)

    WHY one function for both?
      Same save logic — only folder name and source label differ.
      DRY = Don't Repeat Yourself.
    """
        # Phase 2: hive-style path (build_partition_path creates folders for us)
    filepath = build_partition_path(folder, run_time)

    payload = {
        "ingested_at": run_time.isoformat(),
        "source": source_name,
        "data": api_response,  # note: key is "data" here (prices script uses "records")
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return filepath


# ------------------------------------------------------------
# MAIN — fetch both sources → save both → update state
# ------------------------------------------------------------
def main():
    run_time = datetime.now(timezone.utc)
    print(f"Fetching sentiment at {run_time.isoformat()}...")

    # --- Step A: call both APIs ---
    # If fear_greed fails, we never reach news (script stops — state NOT updated).
    # That's correct: only mark success when everything worked.
    fear_greed = fetch_fear_greed()
    news = fetch_news(limit=20)

    # --- Step B: save to separate folders ---
    fg_path = save_payload(
        FEAR_GREED_DIR,
        "alternative.me_fng",   # source label for Spark/dbt later
        fear_greed,
        run_time,
    )
    news_path = save_payload(
        NEWS_DIR,
        "cryptocurrency.cv_news",
        news,
        run_time,
    )

    print(f"Saved fear/greed to {fg_path}")
    print(f"Saved news to {news_path}")

    # Upload both to S3
    upload_to_s3(fg_path, s3_prefix="fear_greed")
    upload_to_s3(news_path, s3_prefix="news")

    # --- Step C: update state AFTER both saves succeeded ---
    # MUST stay INSIDE main() — run_time only exists in this function.
    # MUST use news_last_run / fear_greed_last_run — NOT prices_last_run.
    state = load_state()
    state["news_last_run"] = run_time.isoformat()
    state["fear_greed_last_run"] = run_time.isoformat()
    save_state(state)
    print("Updated state.json")


# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------
# Only call main() here. Do NOT put state update code below main().
# (That was the bug: run_time doesn't exist outside main().)
if __name__ == "__main__":
    main()
