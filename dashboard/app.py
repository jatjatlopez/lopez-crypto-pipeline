import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import databricks.sql
import json

st.set_page_config(
    page_title="Crypto Market Intelligence",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0f1e 0%, #0d1b3e 40%, #0a1628 100%); }

    .glass-card {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(100,180,255,0.15);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0,100,255,0.08), inset 0 1px 0 rgba(255,255,255,0.06);
        height: 100%;
        box-sizing: border-box;
    }
    .kpi-card {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(100,180,255,0.15);
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,100,255,0.08), inset 0 1px 0 rgba(255,255,255,0.06);
        transition: transform 0.2s ease;
        min-height: 180px;
        box-sizing: border-box;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: rgba(100,180,255,0.35); }
    .coin-symbol { font-size: 11px; font-weight: 600; color: #64b4ff; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; }
    .coin-name { font-size: 13px; color: rgba(255,255,255,0.45); margin-bottom: 10px; }
    .coin-price { font-size: 24px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; margin-bottom: 8px; }
    .coin-change-positive { font-size: 13px; font-weight: 600; color: #34d399; background: rgba(52,211,153,0.12); border-radius: 8px; padding: 4px 12px; display: inline-block; margin-bottom: 12px; }
    .coin-change-negative { font-size: 13px; font-weight: 600; color: #f87171; background: rgba(248,113,113,0.12); border-radius: 8px; padding: 4px 12px; display: inline-block; margin-bottom: 12px; }
    .stat-row { display: flex; justify-content: space-between; margin-top: 0; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; }
    .stat-item { text-align: center; flex: 1; }
    .stat-label { font-size: 10px; color: rgba(255,255,255,0.28); text-transform: uppercase; letter-spacing: 0.8px; }
    .stat-value { font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.7); margin-top: 3px; }
    .section-title { font-size: 18px; font-weight: 600; color: rgba(255,255,255,0.9); margin-bottom: 16px; letter-spacing: -0.3px; }
    .header-title { font-size: 32px; font-weight: 700; background: linear-gradient(90deg, #ffffff, #64b4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; margin-bottom: 4px; }
    .header-sub { font-size: 13px; color: rgba(255,255,255,0.4); margin-bottom: 24px; }
    .news-item { padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
    .news-title { font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.85); line-height: 1.4; margin-bottom: 4px; }
    .news-meta { font-size: 11px; color: rgba(255,255,255,0.3); }
    .fg-stat { text-align: center; padding: 0 12px; }
    .fg-stat-label { font-size: 10px; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
    .fg-stat-value { font-size: 16px; font-weight: 700; color: rgba(255,255,255,0.85); }
    .block-container { padding: 2rem 2.5rem; }
    div[data-testid="stHorizontalBlock"] { gap: 16px; }
</style>
""", unsafe_allow_html=True)

DATABRICKS_HOST = "dbc-758c2345-970f.cloud.databricks.com"
DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/67040879cf9bb833"
DATABRICKS_TOKEN = st.secrets["DATABRICKS_TOKEN"]

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

fg_df = get_data("""
    SELECT DATE(last_updated) AS date, AVG(fear_greed_value) AS avg_fg, MAX(value_classification) AS classification
    FROM workspace.default.gold_price_sentiment
    WHERE fear_greed_value IS NOT NULL
    GROUP BY DATE(last_updated) ORDER BY date ASC
""")

news_df = get_data("""
    SELECT ingested_at, data FROM workspace.default.bronze_news
    ORDER BY ingested_at DESC LIMIT 5
""")

st.markdown('<div class="header-title">📈 Crypto Market Intelligence</div>', unsafe_allow_html=True)
st.markdown(f'<div class="header-sub">Live data · CoinGecko · Alternative.me · Databricks Delta Lake · {pd.Timestamp.now().strftime("%b %d, %Y %H:%M")} UTC+8</div>', unsafe_allow_html=True)

# ── FEAR & GREED ROW ──────────────────────────────────────────────
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

    st.markdown('<div class="section-title">Market Sentiment</div>', unsafe_allow_html=True)

    fg_col1, fg_col2 = st.columns([1, 2])

    with fg_col1:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_fg_val,
            number={"font": {"size": 48, "color": fg_color, "family": "Inter"}, "suffix": ""},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "rgba(255,255,255,0.2)",
                         "tickfont": {"color": "rgba(255,255,255,0.4)", "size": 10}},
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
            title={"text": f"<b>{latest_fg_label}</b>", "font": {"size": 14, "color": fg_color, "family": "Inter"}},
        ))
        gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=10),
            height=220,
        )
        trend_arrow = "▲" if trend >= 0 else "▼"
        trend_color = "#34d399" if trend >= 0 else "#f87171"
        st.markdown(f"""
        <div class="glass-card" style="padding: 16px 20px; text-align: center;">
            <div style="font-size:11px; color:rgba(255,255,255,0.35); letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px;">Fear & Greed Index</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(gauge, use_container_width=True)
        st.markdown(f"""
            <div style="display:flex; justify-content:space-around; padding: 4px 8px 8px 8px; border-top: 1px solid rgba(255,255,255,0.06); margin-top: -8px;">
                <div class="fg-stat">
                    <div class="fg-stat-label">7-Day Avg</div>
                    <div class="fg-stat-value">{avg_7d}</div>
                </div>
                <div class="fg-stat" style="border-left:1px solid rgba(255,255,255,0.08); border-right:1px solid rgba(255,255,255,0.08);">
                    <div class="fg-stat-label">vs Yesterday</div>
                    <div class="fg-stat-value" style="color:{trend_color};">{trend_arrow} {abs(trend)}</div>
                </div>
                <div class="fg-stat">
                    <div class="fg-stat-label">Data Points</div>
                    <div class="fg-stat-value">{len(fg_df)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with fg_col2:
        fig_fg = go.Figure()
        fig_fg.add_hrect(y0=0, y1=25, fillcolor="rgba(248,113,113,0.05)", line_width=0, annotation_text="Extreme Fear", annotation_position="top left", annotation_font_color="rgba(248,113,113,0.4)", annotation_font_size=10)
        fig_fg.add_hrect(y0=25, y1=45, fillcolor="rgba(251,146,60,0.05)", line_width=0, annotation_text="Fear", annotation_position="top left", annotation_font_color="rgba(251,146,60,0.4)", annotation_font_size=10)
        fig_fg.add_hrect(y0=45, y1=55, fillcolor="rgba(250,204,21,0.05)", line_width=0, annotation_text="Neutral", annotation_position="top left", annotation_font_color="rgba(250,204,21,0.4)", annotation_font_size=10)
        fig_fg.add_hrect(y0=55, y1=100, fillcolor="rgba(52,211,153,0.05)", line_width=0, annotation_text="Greed", annotation_position="top left", annotation_font_color="rgba(52,211,153,0.4)", annotation_font_size=10)
        fig_fg.add_trace(go.Scatter(
            x=fg_df["date"], y=fg_df["avg_fg"],
            mode="lines+markers",
            line=dict(color=fg_color, width=2.5),
            marker=dict(size=8, color=fg_color, line=dict(color="white", width=1.5)),
            fill="tozeroy", fillcolor=f"rgba(100,180,255,0.06)",
            name="Fear & Greed"
        ))
        fig_fg.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.5)", family="Inter"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", range=[0, 100]),
            margin=dict(l=0, r=0, t=10, b=0), height=220,
            showlegend=False,
        )
        st.markdown('<div style="font-size:12px; color:rgba(255,255,255,0.4); margin-bottom:8px; padding-left:4px;">Fear & Greed Index · Historical Trend with Sentiment Zones</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_fg, use_container_width=True)

# ── COIN KPI CARDS ──────────────────────────────────────────────
st.markdown('<div class="section-title">Live Coin Prices</div>', unsafe_allow_html=True)
coin_cols = st.columns(5)
for i, row in enumerate(latest.itertuples()):
    change = row.price_change_percentage_24h or 0
    change_class = "coin-change-positive" if change >= 0 else "coin-change-negative"
    arrow = "▲" if change >= 0 else "▼"
    with coin_cols[i % 5]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="coin-symbol">{(row.symbol or '').upper()}</div>
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

st.markdown("<br>", unsafe_allow_html=True)

# ── CHARTS ROW ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Market Cap Distribution</div>', unsafe_allow_html=True)
    mc = latest.sort_values("market_cap", ascending=False)
    fig2 = go.Figure(go.Bar(
        x=mc["name"], y=mc["market_cap"],
        marker=dict(color=mc["market_cap"], colorscale=[[0,"rgba(100,180,255,0.35)"],[1,"rgba(100,180,255,1)"]], line=dict(color="rgba(100,180,255,0.2)", width=1)),
        text=[fmt_large(v) for v in mc["market_cap"]], textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.65)", size=11),
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.5)", family="Inter"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showticklabels=False),
        margin=dict(l=0, r=0, t=10, b=0), height=280, showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">Avg Price Change % by Sentiment</div>', unsafe_allow_html=True)
    sent = get_data("""
        SELECT value_classification, ROUND(AVG(price_change_percentage_24h),2) AS avg_pct
        FROM workspace.default.gold_price_sentiment
        WHERE value_classification IS NOT NULL
        GROUP BY value_classification ORDER BY avg_pct DESC
    """)
    bar_colors = ["#34d399" if v >= 0 else "#f87171" for v in sent["avg_pct"]]
    fig3 = go.Figure(go.Bar(
        x=sent["value_classification"], y=sent["avg_pct"],
        marker_color=bar_colors,
        text=[f"{v:+.2f}%" for v in sent["avg_pct"]], textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.65)", size=11),
    ))
    fig3.add_hline(y=0, line_color="rgba(255,255,255,0.12)")
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.5)", family="Inter"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        margin=dict(l=0, r=0, t=30, b=0), height=280, showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-title">24h Price Change Leaderboard</div>', unsafe_allow_html=True)
    top = latest.sort_values("price_change_percentage_24h", ascending=True)
    fig5 = go.Figure(go.Bar(
        x=top["price_change_percentage_24h"], y=top["name"], orientation="h",
        marker_color=["#34d399" if v >= 0 else "#f87171" for v in top["price_change_percentage_24h"]],
        text=[f"{v:+.2f}%" for v in top["price_change_percentage_24h"]],
        textposition="outside", textfont=dict(color="rgba(255,255,255,0.65)", size=12),
    ))
    fig5.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.5)", family="Inter"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=True, zerolinecolor="rgba(255,255,255,0.12)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        margin=dict(l=0, r=60, t=10, b=0), height=280, showlegend=False,
    )
    st.plotly_chart(fig5, use_container_width=True)

with col4:
    st.markdown('<div class="section-title">Volatility Breakdown</div>', unsafe_allow_html=True)
    vol = get_data("""
        SELECT volatility_category, COUNT(*) AS count
        FROM workspace.default.gold_price_sentiment
        WHERE volatility_category IS NOT NULL
        GROUP BY volatility_category
    """)
    fig4 = go.Figure(go.Pie(
        labels=vol["volatility_category"], values=vol["count"], hole=0.55,
        marker=dict(colors=["#64b4ff","#34d399","#fb923c","#f87171","#a78bfa"], line=dict(color="rgba(0,0,0,0.3)", width=2)),
        textfont=dict(color="white", size=12),
    ))
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.5)", family="Inter"),
        margin=dict(l=0, r=0, t=10, b=0), height=280,
        legend=dict(font=dict(color="rgba(255,255,255,0.55)"), bgcolor="rgba(0,0,0,0)"),
        annotations=[dict(text="Volatility", x=0.5, y=0.5, font_size=13, font_color="rgba(255,255,255,0.4)", showarrow=False)]
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── NEWS FEED ──────────────────────────────────────────────────
st.markdown('<div class="section-title">📰 Latest Crypto News</div>', unsafe_allow_html=True)

news_col1, news_col2 = st.columns(2)
articles_shown = 0

for _, news_row in news_df.iterrows():
    try:
        raw = news_row["data"]
        if isinstance(raw, str):
            raw = json.loads(raw)
        articles = raw.get("articles", [])
        fetched_at = news_row["ingested_at"]

        for article in articles[:6]:
            title = article.get("title", "")
            source = article.get("source", {})
            source_name = source.get("name", "") if isinstance(source, dict) else str(source)
            published = article.get("publishedAt", "")[:10] if article.get("publishedAt") else ""
            url = article.get("url", "#")

            if title:
                col = news_col1 if articles_shown % 2 == 0 else news_col2
                with col:
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 14px 18px; margin-bottom: 10px;">
                        <div class="news-title">{title}</div>
                        <div class="news-meta">{source_name} · {published}</div>
                    </div>
                    """, unsafe_allow_html=True)
                articles_shown += 1
                if articles_shown >= 8:
                    break
    except Exception:
        pass

if articles_shown == 0:
    st.markdown("""
    <div class="glass-card" style="text-align:center; padding: 24px; color: rgba(255,255,255,0.3);">
        No news articles yet — cryptocurrency.cv will populate this once articles are fetched.
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; color:rgba(255,255,255,0.15); font-size:11px; margin-top:32px; padding-bottom:16px;">Crypto Market Intelligence · Databricks Delta Lake · Apache Airflow · dbt · GitHub Actions · Streamlit</div>', unsafe_allow_html=True)
