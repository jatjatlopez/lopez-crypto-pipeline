# ============================================================
# fetch_prices.py
# ============================================================
# WHAT THIS FILE DOES (one sentence):
#   Downloads live crypto PRICES from CoinGecko and saves them
#   as raw JSON files on your computer.
#
# HOW TO RUN:
#   python ingestion/fetch_prices.py
#
# WHERE DATA GOES:
#   data/prices/YYYYMMDD_HHMMSS.json
#
# WHERE STATE GOES:
#   ingestion/state.json  (remembers last successful run)
# ============================================================


# ------------------------------------------------------------
# IMPORTS — bring in tools other people already built
# ------------------------------------------------------------
import json          # read/write JSON files (API data format)
import os            # talk to the operating system (env variables)
from datetime import datetime, timezone  # timestamps for "when did we fetch?"
from pathlib import Path                 # clean way to build file paths

import requests      # send HTTP requests to APIs (like a browser, but in code)
from dotenv import load_dotenv  # read secrets from your .env file

from s3_upload import upload_to_s3


# ------------------------------------------------------------
# STEP 1: LOAD SECRETS FROM .env
# ------------------------------------------------------------
# WHY: Never hardcode API keys in code — they could leak to GitHub.
# .env lives in project root and is listed in .gitignore.
load_dotenv()  # reads .env and loads keys into the environment

API_KEY = os.getenv("COINGECKO_API_KEY")  # grab the key by name

if not API_KEY:
    # Fail fast with a helpful message instead of a cryptic 401 error later
    raise ValueError("Missing COINGECKO_API_KEY in .env file")


# ------------------------------------------------------------
# STEP 2: CONFIG — things you might change often
# ------------------------------------------------------------
# WHY a string with commas: CoinGecko accepts multiple coin IDs in one API call.
# That saves API credits (1 call instead of 5).
#
# IMPORTANT: CoinGecko uses internal IDs, NOT ticker symbols:
#   BTC  → "bitcoin"
#   ETH  → "ethereum"
#   SOL  → "solana"
#   XRP  → "ripple"       ← NOT "xrp"
#   HYPE → "hyperliquid"
COIN_IDS = "bitcoin,ethereum,solana,ripple,hyperliquid"


# ------------------------------------------------------------
# STEP 3: PATHS — where files live on disk
# ------------------------------------------------------------
# __file__           = full path to THIS script (.../ingestion/fetch_prices.py)
# .parent            = ingestion/
# .parent.parent     = crypto-pipeline/  (project root)
#
# WHY Path instead of strings: works on Windows AND Mac/Linux without "\" vs "/" bugs.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "prices"          # where price JSON files go
STATE_FILE = PROJECT_ROOT / "ingestion" / "state.json"  # shared with sentiment script
print(STATE_FILE)

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
# STATE HELPERS — read/write ingestion/state.json
# ------------------------------------------------------------
# WHY state.json exists:
#   Later, Airflow runs this hourly. State tells the pipeline
#   "last time I succeeded" so reruns don't duplicate or skip data.
#
# Both fetch_prices.py and fetch_sentiment.py share this ONE file.
# Each script only updates ITS OWN keys (prices_last_run, etc.).

def load_state():
    """Read state.json into a Python dict. Returns {} if file missing."""
    if not STATE_FILE.exists():
        return {}  # first run ever — empty state is fine
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)  # parse JSON text → Python dict


def save_state(state):
    """Write the dict back to state.json (overwrites whole file)."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)  # indent=2 makes it human-readable


# ------------------------------------------------------------
# FETCH — call the CoinGecko API
# ------------------------------------------------------------
def fetch_prices():
    """
    HTTP GET to CoinGecko /coins/markets endpoint.
    Returns a Python LIST of coin dicts (price, volume, market cap, etc.)
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"

    # params = query string values appended to the URL after "?"
    params = {
        "vs_currency": "usd",              # prices in US dollars
        "ids": COIN_IDS,                   # which coins to fetch
        "order": "market_cap_desc",        # biggest coins first
        "x_cg_demo_api_key": API_KEY,      # your free demo key
    }

    # timeout=30 → give up after 30 seconds (don't hang forever)
    response = requests.get(url, params=params, timeout=30)

    # raise_for_status() → if API returns 401/429/500, STOP with an error.
    # WHY: we don't want to save empty/broken data and think it succeeded.
    response.raise_for_status()

    # .json() converts the response body (JSON text) into Python objects
    return response.json()


# ------------------------------------------------------------
# SAVE — write raw API response to disk
# ------------------------------------------------------------
def save_raw_json(records, run_time):
    """
    Save the API response as a JSON file.

    WHY wrap raw data in a 'payload' dict?
      Later (Spark/dbt) we need to know:
        - WHEN our pipeline fetched it  → ingested_at
        - WHERE it came from            → source
        - the actual API response       → records
      This is a data-engineering best practice called "raw landing with metadata."
    """
    
    # Phase 2: hive-style path instead of flat timestamp filename
    filepath = build_partition_path(DATA_DIR, run_time)

    payload = {
        "ingested_at": run_time.isoformat(),  # ISO format: 2026-06-16T03:48:55+00:00
        "source": "coingecko",                # label for downstream tools
        "records": records,                   # raw API list — we do NOT reshape it here
    }

    # "with open(...) as f" → file auto-closes even if something crashes mid-write
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)  # write Python dict as formatted JSON

    return filepath  # so main() can print where the file went


# ------------------------------------------------------------
# MAIN — the workflow: fetch → save → update state
# ------------------------------------------------------------
def main():
    # UTC = Coordinated Universal Time. Industry standard for pipelines.
    # Using one timezone everywhere avoids "which timezone is this?" bugs.
    run_time = datetime.now(timezone.utc)
    print(f"Fetching prices at {run_time.isoformat()}...")

    # --- Step A: call API ---
    records = fetch_prices()

    # --- Step B: save to disk ---
    filepath = save_raw_json(records, run_time)
    print(f"Saved {len(records)} coins to {filepath}")

    # Upload same file to S3 (same hive path, different destination)
    upload_to_s3(filepath, s3_prefix="prices")

    # --- Step C: update state ONLY after save succeeded ---
    # CRITICAL: this block MUST stay INSIDE main().
    # run_time is created above — it does NOT exist outside this function.
    # (Putting state update below main() caused your NameError bug earlier.)
    state = load_state()                        # read current state (or {})
    state["prices_last_run"] = run_time.isoformat()  # update ONLY our key
    save_state(state)                           # write back to disk
    print("Updated state.json")


# ------------------------------------------------------------
# ENTRY POINT — only runs when YOU execute this file directly
# ------------------------------------------------------------
# WHY this guard exists:
#   If another script does "from fetch_prices import fetch_prices",
#   we don't want main() to auto-run. Only run when called as:
#   python ingestion/fetch_prices.py
#
# IMPORTANT: keep this block clean — ONLY call main(), nothing else below it.
if __name__ == "__main__":
    main()
