"""Coin logos and market-cap-ordered picker."""

import base64
from pathlib import Path

import streamlit as st

LOGO_DIR = Path(__file__).parent / "assets" / "logos"
LOGO_FILES = {
    "BTC": "btc.png",
    "ETH": "eth.png",
    "SOL": "sol.png",
    "XRP": "xrp.png",
    "HYPE": "hype.jpg",
}


def logo_path(symbol: str) -> Path | None:
    fname = LOGO_FILES.get((symbol or "").upper())
    if not fname:
        return None
    path = LOGO_DIR / fname
    return path if path.exists() else None


def logo_data_uri(symbol: str) -> str:
    path = logo_path(symbol)
    if not path:
        return ""
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{encoded}"


def coins_by_mcap(latest_df, valid: set[str] | None = None) -> list[str]:
    ordered = latest_df.sort_values("market_cap", ascending=False)
    symbols: list[str] = []
    for raw in ordered["symbol"]:
        sym = (raw or "").upper()
        if valid and sym not in valid:
            continue
        if sym and sym not in symbols:
            symbols.append(sym)
    return symbols


def render_coin_selector(symbols: list[str], key: str = "tv_coin") -> str:
    state_key = f"{key}_sel"
    if state_key not in st.session_state:
        st.session_state[state_key] = symbols[0] if symbols else "BTC"
    if st.session_state[state_key] not in symbols and symbols:
        st.session_state[state_key] = symbols[0]

    current = st.session_state[state_key]
    logo_col, menu_col = st.columns([0.32, 1], gap="small")

    with logo_col:
        path = logo_path(current)
        if path:
            st.image(str(path), width=32)

    with menu_col:
        with st.popover(f"{current}  ▾", use_container_width=True):
            for sym in symbols:
                opt_logo, opt_btn = st.columns([0.2, 1], gap="small")
                with opt_logo:
                    sym_path = logo_path(sym)
                    if sym_path:
                        st.image(str(sym_path), width=24)
                with opt_btn:
                    if st.button(
                        sym,
                        key=f"{key}_opt_{sym}",
                        use_container_width=True,
                        type="primary" if sym == current else "secondary",
                    ):
                        st.session_state[state_key] = sym
                        st.rerun()

    return st.session_state[state_key]
