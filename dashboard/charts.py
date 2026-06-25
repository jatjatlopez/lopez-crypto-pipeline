"""Trading View chart helpers — OHLC, volume, RSI, MACD via CoinGecko."""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from styles import PLOTLY_FONT

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "HYPE": "hyperliquid",
}

COIN_LOGOS = {
    "BTC": "https://coin-images.coingecko.com/coins/images/1/small/bitcoin.png",
    "ETH": "https://coin-images.coingecko.com/coins/images/279/small/ethereum.png",
    "SOL": "https://coin-images.coingecko.com/coins/images/4128/small/solana.png",
    "XRP": "https://coin-images.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png",
    "HYPE": "https://coin-images.coingecko.com/coins/images/50882/small/hyperliquid.jpg",
}

TIMEFRAME_CONFIG = {
    "1H": {"days": 30, "rule": "1h"},
    "4H": {"days": 90, "rule": "4h"},
    "1D": {"days": 180, "rule": "1D"},
}

MIN_CANDLES = 30
CACHE_TTL = 600

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(200,225,255,0.55)", family=PLOTLY_FONT, size=11),
    xaxis=dict(gridcolor="rgba(140,210,255,0.06)", showline=False, rangeslider_visible=False),
    margin=dict(l=0, r=8, t=28, b=0),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="rgba(10,18,36,0.92)",
        bordercolor="rgba(140,210,255,0.25)",
        font=dict(family=PLOTLY_FONT, size=11, color="rgba(235,248,255,0.9)"),
    ),
)


def fetch_market_chart(coin_id: str, days: int, api_key: str | None = None) -> pd.DataFrame:
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key.strip()

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
    prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms", utc=True)
    volumes["timestamp"] = pd.to_datetime(volumes["timestamp"], unit="ms", utc=True)

    df = prices.merge(volumes, on="timestamp", how="outer").sort_values("timestamp")
    return df.set_index("timestamp")


def fetch_ohlc(coin_id: str, timeframe: str, api_key: str | None = None) -> pd.DataFrame:
    cfg = TIMEFRAME_CONFIG[timeframe]
    raw = fetch_market_chart(coin_id, cfg["days"], api_key)

    ohlc = raw["price"].resample(cfg["rule"]).ohlc()
    volume = raw["volume"].resample(cfg["rule"]).sum()
    df = ohlc.join(volume).dropna(subset=["open", "close"])
    df.columns = ["open", "high", "low", "close", "volume"]
    return df.reset_index().rename(columns={"timestamp": "date"})


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def compute_macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def build_trading_chart(
    df: pd.DataFrame,
    coin_label: str,
    timeframe: str,
    show_ema_9: bool = True,
    show_ema_21: bool = True,
    height: int = 580,
) -> go.Figure:
    close = df["close"]
    rsi = compute_rsi(close)
    macd_line, signal_line, histogram = compute_macd(close)

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.48, 0.14, 0.19, 0.19],
        subplot_titles=(
            f"{coin_label} · {timeframe}",
            "Volume",
            "RSI (14)",
            "MACD (12, 26, 9)",
        ),
    )

    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="OHLC",
            increasing_line_color="#2ee8a5",
            increasing_fillcolor="rgba(46,232,165,0.85)",
            decreasing_line_color="#ff6b7a",
            decreasing_fillcolor="rgba(255,107,122,0.85)",
        ),
        row=1,
        col=1,
    )

    if show_ema_9:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=compute_ema(close, 9),
                name="EMA 9",
                line=dict(color="#7ec8ff", width=1.4),
            ),
            row=1,
            col=1,
        )
    if show_ema_21:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=compute_ema(close, 21),
                name="EMA 21",
                line=dict(color="#a78bfa", width=1.2),
            ),
            row=1,
            col=1,
        )

    vol_colors = [
        "rgba(52,211,153,0.55)" if c >= o else "rgba(248,113,113,0.55)"
        for o, c in zip(df["open"], df["close"])
    ]
    fig.add_trace(
        go.Bar(x=df["date"], y=df["volume"], name="Volume", marker_color=vol_colors),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(x=df["date"], y=rsi, name="RSI", line=dict(color="#64b4ff", width=1.5)),
        row=3,
        col=1,
    )
    fig.add_hline(y=70, line_dash="dot", line_color="rgba(248,113,113,0.4)", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="rgba(52,211,153,0.4)", row=3, col=1)

    hist_colors = [
        "rgba(52,211,153,0.7)" if v >= 0 else "rgba(248,113,113,0.7)" for v in histogram
    ]
    fig.add_trace(
        go.Bar(x=df["date"], y=histogram, name="Histogram", marker_color=hist_colors, showlegend=False),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=macd_line, name="MACD", line=dict(color="#64b4ff", width=1.2)
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=signal_line,
            name="Signal",
            line=dict(color="#fb923c", width=1.2),
        ),
        row=4,
        col=1,
    )

    fig.update_layout(
        **CHART_LAYOUT,
        height=height,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="rgba(200,225,255,0.6)", family=PLOTLY_FONT),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=2, col=1)
    fig.update_xaxes(showticklabels=False, row=3, col=1)
    fig.update_yaxes(gridcolor="rgba(140,210,255,0.06)", row=1, col=1)
    fig.update_yaxes(gridcolor="rgba(140,210,255,0.06)", row=2, col=1)
    fig.update_yaxes(gridcolor="rgba(140,210,255,0.06)", range=[0, 100], row=3, col=1)
    fig.update_yaxes(gridcolor="rgba(140,210,255,0.06)", row=4, col=1)
    fig.update_annotations(font=dict(family=PLOTLY_FONT, size=11, color="rgba(200,225,255,0.45)"))
    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig
