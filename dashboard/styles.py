"""Dashboard design system — Arctic Glass theme."""

FONT_DISPLAY = "Outfit"
FONT_BODY = "DM Sans"

PLOTLY_FONT = f"{FONT_BODY}, system-ui, sans-serif"

COIN_ACCENTS = {
    "BTC": "#f7931a",
    "ETH": "#627eea",
    "SOL": "#14f195",
    "XRP": "#00aae4",
    "HYPE": "#a78bfa",
}


def inject_styles() -> str:
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Outfit:wght@300;400;500;600;700;800&display=swap');

    :root {{
        --ice-50: #e8f4ff;
        --ice-100: #b8dcff;
        --ice-200: #7ec8ff;
        --ice-300: #4db5ff;
        --ice-glow: rgba(77, 181, 255, 0.35);
        --glass-bg: rgba(255, 255, 255, 0.045);
        --glass-border: rgba(140, 210, 255, 0.18);
        --glass-highlight: rgba(255, 255, 255, 0.09);
        --glass-shadow: 0 8px 40px rgba(0, 60, 120, 0.22), inset 0 1px 0 var(--glass-highlight);
        --navy-900: #050a14;
        --navy-800: #0a1224;
        --navy-700: #0f1a33;
        --text-primary: rgba(255, 255, 255, 0.94);
        --text-secondary: rgba(200, 225, 255, 0.55);
        --text-muted: rgba(160, 195, 230, 0.38);
        --positive: #2ee8a5;
        --negative: #ff6b7a;
        --radius-lg: 22px;
        --radius-md: 16px;
        --radius-sm: 10px;
    }}

    html, body, [class*="css"] {{
        font-family: '{FONT_BODY}', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(56, 149, 255, 0.18) 0%, transparent 55%),
            radial-gradient(ellipse 60% 40% at 85% 5%, rgba(100, 200, 255, 0.12) 0%, transparent 50%),
            radial-gradient(ellipse 50% 60% at 50% 100%, rgba(30, 80, 160, 0.15) 0%, transparent 60%),
            linear-gradient(165deg, var(--navy-900) 0%, var(--navy-800) 38%, var(--navy-700) 100%);
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        top: 10%;
        right: -5%;
        width: 420px;
        height: 420px;
        background: radial-gradient(circle, rgba(77, 181, 255, 0.12) 0%, transparent 68%);
        filter: blur(40px);
        animation: orbDrift 22s ease-in-out infinite alternate;
        pointer-events: none;
        z-index: 0;
    }}

    .stApp::after {{
        content: "";
        position: fixed;
        bottom: 5%;
        left: -8%;
        width: 360px;
        height: 360px;
        background: radial-gradient(circle, rgba(46, 232, 165, 0.06) 0%, transparent 70%);
        filter: blur(50px);
        animation: orbDrift 28s ease-in-out infinite alternate-reverse;
        pointer-events: none;
        z-index: 0;
    }}

    @keyframes orbDrift {{
        0% {{ transform: translate(0, 0) scale(1); }}
        100% {{ transform: translate(30px, -20px) scale(1.08); }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.45; transform: scale(0.85); }}
    }}

    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
        border-bottom: none;
    }}
    div[data-testid="stDecoration"] {{ display: none; }}
    div[data-testid="stToolbar"] {{
        background: transparent !important;
        right: 1.25rem;
    }}
    .stApp [data-testid="stAppViewContainer"] > section.main > div.block-container {{
        padding: 0.35rem 1.75rem 1.5rem;
        max-width: 1320px;
        position: relative;
        z-index: 1;
        animation: fadeUp 0.5s ease-out;
    }}

    /* Tighter Streamlit vertical rhythm */
    .stApp [data-testid="stVerticalBlock"] {{
        gap: 0.35rem !important;
    }}
    .stApp [data-testid="stVerticalBlock"] > div {{
        gap: 0.35rem !important;
    }}
    div[data-testid="element-container"] {{
        margin-bottom: 0.15rem !important;
    }}
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2 {{
        margin-bottom: 0 !important;
    }}

    /* ── Hero ── */
    .hero {{
        position: relative;
        padding: 0.9rem 1.25rem 0.75rem;
        margin-bottom: 0.85rem;
        border-radius: var(--radius-lg);
        background: linear-gradient(135deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.02) 100%);
        backdrop-filter: blur(28px) saturate(160%);
        -webkit-backdrop-filter: blur(28px) saturate(160%);
        border: 1px solid var(--glass-border);
        box-shadow: var(--glass-shadow);
        overflow: hidden;
    }}
    .hero::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(180, 230, 255, 0.5), transparent);
    }}
    .hero-badge-row {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.45rem;
    }}
    .live-pill {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 5px 12px;
        border-radius: 999px;
        background: rgba(46, 232, 165, 0.1);
        border: 1px solid rgba(46, 232, 165, 0.28);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.8px;
        color: var(--positive);
        text-transform: uppercase;
    }}
    .live-dot {{
        width: 7px; height: 7px;
        border-radius: 50%;
        background: var(--positive);
        box-shadow: 0 0 10px var(--positive);
        animation: pulse 2s ease-in-out infinite;
    }}
    .hero-chip {{
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.6px;
        color: var(--text-muted);
        padding: 5px 10px;
        border-radius: 999px;
        border: 1px solid rgba(140, 210, 255, 0.12);
        background: rgba(255,255,255,0.03);
    }}
    .hero-title {{
        font-family: '{FONT_DISPLAY}', sans-serif;
        font-size: clamp(1.65rem, 3.2vw, 2.15rem);
        font-weight: 700;
        letter-spacing: -1.2px;
        line-height: 1.08;
        margin: 0 0 0.3rem 0;
        background: linear-gradient(120deg, #ffffff 0%, var(--ice-100) 45%, var(--ice-300) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .hero-sub {{
        font-size: 12px;
        font-weight: 400;
        color: var(--text-secondary);
        letter-spacing: 0.2px;
        margin: 0;
    }}
    .hero-sub span {{
        color: var(--ice-200);
        font-weight: 500;
    }}

    /* ── Section headers ── */
    .section-wrap {{
        margin: 1.15rem 0 0.7rem;
        padding-bottom: 0.15rem;
    }}
    .section-header {{
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 0;
    }}
    .section-accent {{
        width: 3px;
        height: 18px;
        border-radius: 4px;
        background: linear-gradient(180deg, var(--ice-200), var(--ice-300));
        box-shadow: 0 0 14px var(--ice-glow);
        flex-shrink: 0;
    }}
    .section-title {{
        font-family: '{FONT_DISPLAY}', sans-serif;
        font-size: 1.02rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.4px;
        margin: 0;
    }}
    .section-desc {{
        font-size: 11px;
        color: var(--text-muted);
        margin: 4px 0 0 0;
        line-height: 1.35;
    }}

    /* ── Aligned card rows ── */
    .chart-caption {{
        font-size: 10px;
        color: var(--text-muted);
        margin: 0 0 12px 0;
        padding: 2px 4px 0;
        letter-spacing: 0.35px;
        text-transform: uppercase;
        font-weight: 600;
        line-height: 1.3;
        display: block;
    }}
    .card-footer-stats {{
        display: flex;
        justify-content: space-around;
        padding: 8px 4px 4px;
        margin-top: auto;
        border-top: 1px solid rgba(255,255,255,0.06);
        min-height: 52px;
        box-sizing: border-box;
    }}
    div[data-testid="stHorizontalBlock"].card-row {{
        align-items: stretch !important;
        gap: 12px !important;
    }}
    div[data-testid="element-container"]:has(.section-wrap) + div[data-testid="element-container"] {{
        margin-top: 0.15rem;
    }}
    div[data-testid="element-container"]:has(.section-wrap) + div[data-testid="element-container"] [data-testid="stHorizontalBlock"] {{
        align-items: stretch !important;
        gap: 12px !important;
    }}
    div[data-testid="element-container"]:has(.section-wrap) + div[data-testid="element-container"] [data-testid="column"] {{
        display: flex;
        flex-direction: column;
    }}
    div[data-testid="element-container"]:has(.section-wrap) + div[data-testid="element-container"] [data-testid="column"] > div {{
        flex: 1;
        width: 100%;
    }}
    div[data-testid="element-container"]:has(.section-wrap) + div[data-testid="element-container"] [data-testid="stVerticalBlockBorderWrapper"] {{
        height: 100%;
        min-height: 292px;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    }}
    div[data-testid="element-container"]:has(.section-wrap) + div[data-testid="element-container"] [data-testid="stPlotlyChart"] {{
        flex: 1;
        margin-top: 4px !important;
        padding-top: 2px;
    }}

    /* ── Glass surfaces ── */
    .glass-card, .glass-panel {{
        background: var(--glass-bg);
        backdrop-filter: blur(24px) saturate(150%);
        -webkit-backdrop-filter: blur(24px) saturate(150%);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        box-shadow: var(--glass-shadow);
        position: relative;
        overflow: hidden;
    }}
    .glass-panel {{
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.25rem;
    }}
    .glass-panel::before {{
        content: "";
        position: absolute;
        top: 0; left: 12%; right: 12%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(200, 235, 255, 0.35), transparent);
    }}

    /* ── KPI cards ── */
    .kpi-card {{
        background: linear-gradient(160deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.025) 100%);
        backdrop-filter: blur(22px) saturate(140%);
        -webkit-backdrop-filter: blur(22px) saturate(140%);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: 0.85rem 0.75rem 0.75rem;
        text-align: center;
        box-shadow: var(--glass-shadow);
        transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.25s ease, box-shadow 0.25s ease;
        min-height: 168px;
        box-sizing: border-box;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::after {{
        content: "";
        position: absolute;
        top: -40%;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        height: 60%;
        background: radial-gradient(ellipse, var(--coin-glow, rgba(77,181,255,0.12)) 0%, transparent 70%);
        pointer-events: none;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        border-color: rgba(140, 210, 255, 0.38);
        box-shadow: 0 16px 48px rgba(0, 80, 160, 0.28), inset 0 1px 0 var(--glass-highlight);
    }}
    .coin-avatar {{
        width: 36px; height: 36px;
        margin: 0 auto 6px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255,255,255,0.18);
        box-shadow: 0 4px 16px var(--coin-glow, rgba(77,181,255,0.25));
        position: relative;
        z-index: 1;
        overflow: hidden;
        padding: 3px;
        box-sizing: border-box;
    }}
    .coin-avatar img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 50%;
        display: block;
    }}
    .coin-avatar-fallback {{
        font-family: '{FONT_DISPLAY}', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: white;
        background: linear-gradient(135deg, var(--coin-color, #4db5ff), rgba(0,0,0,0.2));
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
    }}
    .coin-symbol {{
        font-size: 10px;
        font-weight: 700;
        color: var(--ice-200);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 2px;
        position: relative;
        z-index: 1;
    }}
    .coin-name {{
        font-size: 12px;
        color: var(--text-muted);
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }}
    .coin-price {{
        font-family: '{FONT_DISPLAY}', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.6px;
        margin-bottom: 6px;
        position: relative;
        z-index: 1;
    }}
    .coin-change-positive, .coin-change-negative {{
        font-size: 12px;
        font-weight: 600;
        border-radius: var(--radius-sm);
        padding: 4px 14px;
        display: inline-block;
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }}
    .coin-change-positive {{
        color: var(--positive);
        background: rgba(46, 232, 165, 0.12);
        border: 1px solid rgba(46, 232, 165, 0.2);
    }}
    .coin-change-negative {{
        color: var(--negative);
        background: rgba(255, 107, 122, 0.12);
        border: 1px solid rgba(255, 107, 122, 0.2);
    }}
    .stat-row {{
        display: flex;
        justify-content: space-between;
        border-top: 1px solid rgba(255,255,255,0.06);
        padding-top: 10px;
        position: relative;
        z-index: 1;
    }}
    .stat-item {{ text-align: center; flex: 1; }}
    .stat-label {{
        font-size: 9px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }}
    .stat-value {{
        font-size: 11px;
        font-weight: 600;
        color: rgba(220, 240, 255, 0.75);
        margin-top: 4px;
    }}

    /* ── Fear & Greed ── */
    .fg-card-label {{
        font-size: 10px;
        font-weight: 600;
        color: var(--text-muted);
        letter-spacing: 1.6px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 4px;
    }}
    .fg-stat {{ text-align: center; padding: 0 10px; }}
    .fg-stat-label {{
        font-size: 9px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }}
    .fg-stat-value {{
        font-family: '{FONT_DISPLAY}', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
    }}

    /* ── Trading controls ── */
    .tv-toolbar {{
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        padding: 0.85rem 1rem;
        margin-bottom: 0.75rem;
        border-radius: var(--radius-md);
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(140, 210, 255, 0.12);
    }}
    .tv-toolbar-label {{
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--text-muted);
        margin: 0 0 0.35rem 0;
    }}
    div[data-testid="stPopover"] button {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(140, 210, 255, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        min-height: 38px !important;
    }}
    div[data-testid="stPopoverBody"] button {{
        margin-bottom: 0.25rem !important;
    }}

    /* ── Streamlit widgets ── */
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stMultiSelect"] > div > div {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(140, 210, 255, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        backdrop-filter: blur(12px);
    }}
    div[data-testid="stCheckbox"] label span {{
        color: var(--text-secondary) !important;
        font-size: 13px !important;
    }}
    div[data-testid="stCheckbox"] label {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(140, 210, 255, 0.14);
        border-radius: var(--radius-sm);
        padding: 6px 12px !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="element-container"]:has(.chart-caption) {{
        margin-bottom: 0 !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="element-container"]:has(.chart-caption) + [data-testid="element-container"] {{
        margin-top: 0.5rem !important;
        padding-top: 2px !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="element-container"]:has(.chart-caption) + [data-testid="element-container"] [data-testid="stPlotlyChart"] {{
        margin-top: 0 !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(24px) saturate(150%);
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--glass-shadow) !important;
        padding: 0.75rem 0.7rem 0.5rem !important;
        margin-bottom: 0.25rem !important;
    }}

    /* ── News ── */
    .news-card {{
        padding: 0.7rem 0.9rem;
        margin-bottom: 0.4rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }}
    .news-card:hover {{
        border-color: rgba(140, 210, 255, 0.32);
        transform: translateX(3px);
    }}
    .news-title {{
        font-size: 13px;
        font-weight: 500;
        color: rgba(235, 248, 255, 0.9);
        line-height: 1.45;
        margin-bottom: 6px;
    }}
    .news-meta {{
        font-size: 10px;
        color: var(--text-muted);
        letter-spacing: 0.4px;
    }}
    .news-source-dot {{
        display: inline-block;
        width: 5px; height: 5px;
        border-radius: 50%;
        background: var(--ice-300);
        margin-right: 6px;
        vertical-align: middle;
    }}

    /* ── Expandable news ── */
    div[data-testid="stExpander"] {{
        background: var(--glass-bg);
        backdrop-filter: blur(20px) saturate(140%);
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-md) !important;
        margin-bottom: 0.35rem;
        box-shadow: 0 4px 20px rgba(0, 60, 120, 0.12);
    }}
    div[data-testid="stExpander"] details {{
        border: none;
    }}
    div[data-testid="stExpander"] summary {{
        padding: 0.6rem 0.8rem;
        font-size: 12.5px;
        font-weight: 500;
        color: rgba(235, 248, 255, 0.88);
        line-height: 1.35;
    }}
    div[data-testid="stExpander"] summary:hover {{
        color: var(--ice-100);
    }}
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        padding: 0 0.8rem 0.7rem;
        border-top: 1px solid rgba(140, 210, 255, 0.1);
    }}
    .news-meta-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 0.35rem 0 0.65rem;
    }}
    .news-chip {{
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.4px;
        padding: 3px 8px;
        border-radius: 999px;
        border: 1px solid rgba(140, 210, 255, 0.15);
        background: rgba(255,255,255,0.04);
        color: var(--text-muted);
        text-transform: capitalize;
    }}
    .news-chip-sentiment {{
        font-weight: 600;
        background: rgba(255,255,255,0.03);
    }}
    .news-tldr {{
        font-size: 13px;
        line-height: 1.55;
        color: rgba(220, 240, 255, 0.82);
        padding: 0.65rem 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: var(--radius-sm);
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(140, 210, 255, 0.1);
    }}
    .news-tags {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 0.5rem 0 0.65rem;
    }}
    .news-tag {{
        font-size: 10px;
        padding: 3px 9px;
        border-radius: 6px;
        background: rgba(77, 181, 255, 0.1);
        border: 1px solid rgba(77, 181, 255, 0.2);
        color: var(--ice-200);
    }}

    /* ── Footer ── */
    .footer {{
        text-align: center;
        margin-top: 1.5rem;
        padding: 0.85rem 0 0.25rem;
        border-top: 1px solid rgba(140, 210, 255, 0.08);
    }}
    .footer-text {{
        font-size: 10px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text-muted);
    }}
    .footer-stack {{
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 6px 16px;
        margin-top: 8px;
    }}
    .footer-stack span {{
        font-size: 10px;
        color: rgba(140, 195, 230, 0.35);
        letter-spacing: 0.8px;
    }}

    div[data-testid="stHorizontalBlock"] {{ gap: 10px; }}
    .stSpinner > div {{ border-top-color: var(--ice-300) !important; }}
    [data-testid="stPlotlyChart"] {{
        border-radius: 12px;
        overflow: hidden;
        margin-top: 0;
        margin-bottom: 0;
    }}
</style>
"""


def section_header(title: str, subtitle: str = "") -> str:
    sub = f'<p class="section-desc">{subtitle}</p>' if subtitle else ""
    return f"""
    <div class="section-wrap">
        <div class="section-header">
            <div class="section-accent"></div>
            <div>
                <h2 class="section-title">{title}</h2>
                {sub}
            </div>
        </div>
    </div>
    """
