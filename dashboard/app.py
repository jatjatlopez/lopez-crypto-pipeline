import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import databricks.sql

from charts import COINS, MIN_CANDLES, fetch_ohlc, build_trading_chart
from coin_ui import coins_by_mcap, logo_data_uri, render_coin_selector
from news_ui import render_news_feed
from styles import COIN_ACCENTS, PLOTLY_FONT, inject_styles, section_header

st.set_page_config(
    page_title="Crypto Market Intelligence",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed",
)

st.markdown(inject_styles(), unsafe_allow_html=True)

DATABRICKS_HOST = "dbc-758c2345-970f.cloud.databricks.com"
DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/67040879cf9bb833"
DATABRICKS_TOKEN = st.secrets["DATABRICKS_TOKEN"]
COINGECKO_API_KEY = st.secrets.get("COINGECKO_API_KEY")

@st.cache_data(ttl=600)
def get_chart_data(coin_id: str, timeframe: str, api_key: str | None):
    return fetch_ohlc(coin_id, timeframe, api_key)

@st.cache_data(ttl=3600)
def get_data(query):
    with databricks.sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_TOKEN,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])

PLOTLY_UI = {"displayModeBar": False}
SENTIMENT_CHART_H = 218

def fmt_price(v):
    if v is None: return "—"
    return f"${v:,.0f}" if v >= 1000 else f"${v:,.2f}"

def fmt_large(v):
    if v is None: return "—"
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9: return f"${v/1e9:.2f}B"
    if v >= 1e6: return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"

df = get_data("SELECT * FROM workspace.default.gold_price_sentiment ORDER BY last_updated DESC")
latest = df.sort_values("last_updated").drop_duplicates("coin_id", keep="last")
coins_ordered = coins_by_mcap(latest, valid=set(COINS.keys()))

fg_df = get_data("""
    SELECT DATE(last_updated) AS date, AVG(fear_greed_value) AS avg_fg, MAX(value_classification) AS classification
    FROM workspace.default.gold_price_sentiment
    WHERE fear_greed_value IS NOT NULL
    GROUP BY DATE(last_updated) ORDER BY date ASC
""")

news_df = get_data("""
    SELECT ingested_at, data FROM workspace.default.bronze_news
    ORDER BY ingested_at DESC LIMIT 10
""")

st.markdown(f"""
<div class="hero">
    <div class="hero-badge-row">
        <div class="live-pill"><span class="live-dot"></span> Live</div>
        <span class="hero-chip">Delta Lake</span>
        <span class="hero-chip">5 Assets</span>
        <span class="hero-chip">24/7 Pipeline</span>
    </div>
    <h1 class="hero-title">Crypto Market Intelligence</h1>
    <p class="hero-sub">
        Real-time prices · sentiment · technicals &nbsp;·&nbsp;
        <span>{pd.Timestamp.now().strftime("%b %d, %Y · %H:%M")} UTC+8</span>
    </p>
</div>
""", unsafe_allow_html=True)

# ── FEAR & GREED ROW ──────────────────────────────────────────────
sent = get_data("""
    SELECT value_classification, ROUND(AVG(price_change_percentage_24h),2) AS avg_pct
    FROM workspace.default.gold_price_sentiment
    WHERE value_classification IS NOT NULL
    GROUP BY value_classification ORDER BY avg_pct DESC
""")

if not fg_df.empty:
    latest_fg_val = int(fg_df.iloc[-1]["avg_fg"])
    latest_fg_label = fg_df.iloc[-1]["classification"] or ""
    prev_fg_val = int(fg_df.iloc[-2]["avg_fg"]) if len(fg_df) > 1 else latest_fg_val
    trend = latest_fg_val - prev_fg_val
    avg_7d = int(fg_df.tail(7)["avg_fg"].mean())

    if latest_fg_val < 25: fg_color = "#f87171"
    elif latest_fg_val < 45: fg_color = "#fb923c"
    elif latest_fg_val < 55: fg_color = "#facc15"
    elif latest_fg_val < 75: fg_color = "#34d399"
    else: fg_color = "#4ade80"

    st.markdown(section_header("Market Sentiment", "Fear & Greed index with historical zones"), unsafe_allow_html=True)

    fg_col1, fg_col2, fg_col3 = st.columns(3)

    with fg_col1:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_fg_val,
            number={"font": {"size": 40, "color": fg_color, "family": PLOTLY_FONT}, "suffix": ""},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "rgba(255,255,255,0.2)",
                         "tickfont": {"color": "rgba(255,255,255,0.4)", "size": 9}},
                "bar": {"color": fg_color, "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 25], "color": "rgba(248,113,113,0.15)"},
                    {"range": [25, 45], "color": "rgba(251,146,60,0.15)"},
                    {"range": [45, 55], "color": "rgba(250,204,21,0.15)"},
                    {"range": [55, 75], "color": "rgba(52,211,153,0.15)"},
                    {"range": [75, 100], "color": "rgba(74,222,128,0.15)"},
                ],
                "threshold": {"line": {"color": fg_color, "width": 3}, "thickness": 0.8, "value": latest_fg_val}
            },
            title={"text": f"<b>{latest_fg_label}</b>", "font": {"size": 12, "color": fg_color, "family": PLOTLY_FONT}},
        ))
        gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=8, r=8, t=16, b=0),
            height=SENTIMENT_CHART_H,
        )
        trend_arrow = "▲" if trend >= 0 else "▼"
        trend_color = "#34d399" if trend >= 0 else "#f87171"
        with st.container(border=True):
            st.markdown('<p class="chart-caption">Fear &amp; Greed Index</p>', unsafe_allow_html=True)
            st.plotly_chart(gauge, use_container_width=True, config=PLOTLY_UI)
            st.markdown(f"""
                <div class="card-footer-stats">
                    <div class="fg-stat">
                        <div class="fg-stat-label">7-Day Avg</div>
                        <div class="fg-stat-value">{avg_7d}</div>
                    </div>
                    <div class="fg-stat" style="border-left:1px solid rgba(255,255,255,0.08); border-right:1px solid rgba(255,255,255,0.08);">
                        <div class="fg-stat-label">vs Yesterday</div>
                        <div class="fg-stat-value" style="color:{trend_color};">{trend_arrow} {abs(trend)}</div>
                    </div>
                    <div class="fg-stat">
                        <div class="fg-stat-label">Points</div>
                        <div class="fg-stat-value">{len(fg_df)}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with fg_col2:
        fig_fg = go.Figure()
        fig_fg.add_hrect(y0=0, y1=25, fillcolor="rgba(248,113,113,0.05)", line_width=0, annotation_text="Extreme Fear", annotation_position="inside bottom left", annotation_font_color="rgba(248,113,113,0.4)", annotation_font_size=9)
        fig_fg.add_hrect(y0=25, y1=45, fillcolor="rgba(251,146,60,0.05)", line_width=0, annotation_text="Fear", annotation_position="inside bottom left", annotation_font_color="rgba(251,146,60,0.4)", annotation_font_size=9)
        fig_fg.add_hrect(y0=45, y1=55, fillcolor="rgba(250,204,21,0.05)", line_width=0, annotation_text="Neutral", annotation_position="inside bottom left", annotation_font_color="rgba(250,204,21,0.4)", annotation_font_size=9)
        fig_fg.add_hrect(y0=55, y1=100, fillcolor="rgba(52,211,153,0.05)", line_width=0, annotation_text="Greed", annotation_position="inside top left", annotation_font_color="rgba(52,211,153,0.4)", annotation_font_size=9)
        fig_fg.add_trace(go.Scatter(
            x=fg_df["date"], y=fg_df["avg_fg"],
            mode="lines+markers",
            line=dict(color=fg_color, width=2.5),
            marker=dict(size=7, color=fg_color, line=dict(color="white", width=1.5)),
            fill="tozeroy", fillcolor="rgba(100,180,255,0.06)",
            name="Fear & Greed",
        ))
        fig_fg.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(200,225,255,0.5)", family=PLOTLY_FONT),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", range=[0, 100]),
            margin=dict(l=0, r=0, t=24, b=0), height=SENTIMENT_CHART_H,
            showlegend=False,
        )
        with st.container(border=True):
            st.markdown('<p class="chart-caption">Historical trend · sentiment zones</p>', unsafe_allow_html=True)
            st.plotly_chart(fig_fg, use_container_width=True, config=PLOTLY_UI)
            st.markdown('<div class="card-footer-stats" style="visibility:hidden; min-height:52px;"></div>', unsafe_allow_html=True)

    with fg_col3:
        with st.container(border=True):
            st.markdown('<p class="chart-caption">Avg price change by sentiment</p>', unsafe_allow_html=True)
            bar_colors = ["#2ee8a5" if v >= 0 else "#ff6b7a" for v in sent["avg_pct"]]
            fig_sent = go.Figure(go.Bar(
                x=sent["value_classification"], y=sent["avg_pct"],
                marker_color=bar_colors,
                text=[f"{v:+.2f}%" for v in sent["avg_pct"]], textposition="outside",
                textfont=dict(color="rgba(255,255,255,0.65)", size=10),
            ))
            fig_sent.add_hline(y=0, line_color="rgba(255,255,255,0.12)")
            fig_sent.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="rgba(200,225,255,0.5)", family=PLOTLY_FONT),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickangle=-25),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                margin=dict(l=0, r=0, t=24, b=0), height=SENTIMENT_CHART_H, showlegend=False,
            )
            st.plotly_chart(fig_sent, use_container_width=True, config=PLOTLY_UI)
            st.markdown('<div class="card-footer-stats" style="visibility:hidden; min-height:52px;"></div>', unsafe_allow_html=True)

# ── COIN KPI CARDS ──────────────────────────────────────────────
st.markdown(section_header("Live Coin Prices", "Spot prices across tracked assets"), unsafe_allow_html=True)
coin_cols = st.columns(5)
latest_by_mcap = latest.sort_values("market_cap", ascending=False)
for i, row in enumerate(latest_by_mcap.itertuples()):
    change = row.price_change_percentage_24h or 0
    change_class = "coin-change-positive" if change >= 0 else "coin-change-negative"
    arrow = "▲" if change >= 0 else "▼"
    sym = (row.symbol or "").upper()
    accent = COIN_ACCENTS.get(sym, "#4db5ff")
    logo_url = logo_data_uri(sym)
    avatar_html = (
        f'<img src="{logo_url}" alt="{sym}" loading="lazy" />'
        if logo_url
        else f'<span class="coin-avatar-fallback">{sym[:1]}</span>'
    )
    with coin_cols[i % 5]:
        st.markdown(f"""
        <div class="kpi-card" style="--coin-color: {accent}; --coin-glow: {accent}33;">
            <div class="coin-avatar">{avatar_html}</div>
            <div class="coin-symbol">{sym}</div>
            <div class="coin-name">{row.name}</div>
            <div class="coin-price">{fmt_price(row.current_price)}</div>
            <div class="{change_class}">{arrow} {abs(change):.2f}%</div>
            <div class="stat-row">
                <div class="stat-item">
                    <div class="stat-label">Mkt Cap</div>
                    <div class="stat-value">{fmt_large(row.market_cap)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Volume</div>
                    <div class="stat-value">{fmt_large(row.total_volume)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">24h High</div>
                    <div class="stat-value">{fmt_price(row.high_24h)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── TRADING VIEW + SIDE ANALYTICS ────────────────────────────────
st.markdown(section_header("Trading View", "Exchange-style OHLC · RSI · MACD · EMA overlays"), unsafe_allow_html=True)

mc = latest.sort_values("market_cap", ascending=False)
top = latest.sort_values("price_change_percentage_24h", ascending=True)
vol = get_data("""
    SELECT volatility_category, COUNT(*) AS count
    FROM workspace.default.gold_price_sentiment
    WHERE volatility_category IS NOT NULL
    GROUP BY volatility_category
""")

tv_left, tv_right = st.columns([1.55, 1])

with tv_left:
    with st.container(border=True):
        st.markdown('<div class="tv-toolbar-label">Chart Controls</div>', unsafe_allow_html=True)
        tv_col1, tv_col2, tv_col3, tv_col4 = st.columns([1.2, 1, 1, 1])
        with tv_col1:
            selected_symbol = render_coin_selector(coins_ordered, key="tv_coin")
        with tv_col2:
            selected_timeframe = st.selectbox("Timeframe", ["1H", "4H", "1D"], index=0, label_visibility="collapsed")
        with tv_col3:
            show_ema_9 = st.checkbox("EMA 9", value=True)
        with tv_col4:
            show_ema_21 = st.checkbox("EMA 21", value=True)

        coin_id = COINS[selected_symbol]

        with st.spinner(f"Loading {selected_symbol} · {selected_timeframe} chart..."):
            try:
                chart_df = get_chart_data(coin_id, selected_timeframe, COINGECKO_API_KEY)
                if len(chart_df) < MIN_CANDLES:
                    st.warning(
                        f"Not enough candle data yet ({len(chart_df)} candles). "
                        f"Need at least {MIN_CANDLES} for reliable RSI/MACD."
                    )
                else:
                    fig_tv = build_trading_chart(
                        chart_df,
                        selected_symbol,
                        selected_timeframe,
                        show_ema_9=show_ema_9,
                        show_ema_21=show_ema_21,
                    )
                    st.plotly_chart(fig_tv, use_container_width=True)
            except Exception as e:
                st.error(f"Could not load chart data: {e}")

with tv_right:
    with st.container(border=True):
        st.markdown('<p class="chart-caption">Market cap distribution</p>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=mc["name"], y=mc["market_cap"],
            marker=dict(color=mc["market_cap"], colorscale=[[0, "rgba(77,181,255,0.25)"], [1, "rgba(126,200,255,0.95)"]], line=dict(color="rgba(126,200,255,0.25)", width=1)),
            text=[fmt_large(v) for v in mc["market_cap"]], textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.65)", size=10),
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(200,225,255,0.5)", family=PLOTLY_FONT),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showticklabels=False),
            margin=dict(l=0, r=0, t=6, b=0), height=185, showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with st.container(border=True):
        st.markdown('<p class="chart-caption">24h price change leaderboard</p>', unsafe_allow_html=True)
        fig5 = go.Figure(go.Bar(
            x=top["price_change_percentage_24h"], y=top["name"], orientation="h",
            marker_color=["#2ee8a5" if v >= 0 else "#ff6b7a" for v in top["price_change_percentage_24h"]],
            text=[f"{v:+.2f}%" for v in top["price_change_percentage_24h"]],
            textposition="outside", textfont=dict(color="rgba(255,255,255,0.65)", size=10),
        ))
        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(200,225,255,0.5)", family=PLOTLY_FONT),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=True, zerolinecolor="rgba(255,255,255,0.12)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            margin=dict(l=0, r=40, t=6, b=0), height=185, showlegend=False,
        )
        st.plotly_chart(fig5, use_container_width=True)

    with st.container(border=True):
        st.markdown('<p class="chart-caption">Volatility breakdown</p>', unsafe_allow_html=True)
        fig4 = go.Figure(go.Pie(
            labels=vol["volatility_category"], values=vol["count"], hole=0.55,
            marker=dict(colors=["#7ec8ff", "#2ee8a5", "#ffb86b", "#ff6b7a", "#c4b5fd"], line=dict(color="rgba(0,0,0,0.25)", width=2)),
            textfont=dict(color="white", size=10),
        ))
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(200,225,255,0.5)", family=PLOTLY_FONT),
            margin=dict(l=0, r=0, t=6, b=0), height=185,
            legend=dict(font=dict(color="rgba(255,255,255,0.55)", size=9), bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(text="Volatility", x=0.5, y=0.5, font_size=11, font_color="rgba(255,255,255,0.4)", showarrow=False)],
        )
        st.plotly_chart(fig4, use_container_width=True)

# ── NEWS FEED ──────────────────────────────────────────────────
st.markdown(section_header("Latest Crypto News", "Click any headline to expand TL;DR & details"), unsafe_allow_html=True)

articles_shown = render_news_feed(news_df, max_articles=8)

if articles_shown == 0:
    st.markdown("""
    <div class="glass-panel" style="text-align:center; padding: 2rem; color: rgba(160,195,230,0.4);">
        No news articles yet — cryptocurrency.cv will populate this once articles are fetched.
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <div class="footer-text">Crypto Market Intelligence</div>
    <div class="footer-stack">
        <span>Databricks Delta Lake</span>
        <span>Apache Airflow</span>
        <span>dbt Core</span>
        <span>GitHub Actions</span>
        <span>Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)
