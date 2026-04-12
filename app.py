import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import calendar

st.set_page_config(
    page_title="CRZ Kaizen Journal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #080c14; }

/* Hide streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem; max-width: 1400px; }

/* Header */
.crz-header {
    background: linear-gradient(135deg, #0d1117 0%, #0a1628 100%);
    border-bottom: 1px solid #1e2a3a;
    padding: 16px 32px;
    margin: -1rem -2rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.crz-logo {
    font-size: 20px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: 0.05em;
}
.crz-logo span { color: #2dd4bf; }
.crz-tagline { font-size: 11px; color: #475569; letter-spacing: 0.1em; text-transform: uppercase; }

/* Metric cards */
.metric-card {
    background: #0d1117;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.green::before { background: #22c55e; }
.metric-card.red::before   { background: #ef4444; }
.metric-card.blue::before  { background: #3b82f6; }
.metric-card.teal::before  { background: #2dd4bf; }
.metric-card.amber::before { background: #f59e0b; }
.metric-card.purple::before{ background: #8b5cf6; }

.metric-label {
    font-size: 10px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 600;
    color: #f1f5f9;
    line-height: 1;
}
.metric-sub {
    font-size: 11px;
    color: #64748b;
    margin-top: 6px;
}

/* Nav tabs — button style */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #0f1923;
    gap: 4px;
    padding: 0 0 0 0;
}
.stTabs [data-baseweb="tab"] {
    color: #475569;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 8px 16px;
    border-radius: 6px 6px 0 0;
    text-transform: uppercase;
    background: transparent;
    border: 1px solid transparent;
    border-bottom: none;
    transition: all 0.15s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: #0d1117 !important;
}
.stTabs [aria-selected="true"] {
    background: #0d1117 !important;
    color: #2dd4bf !important;
    border: 1px solid #1e2a3a !important;
    border-bottom: 2px solid #2dd4bf !important;
}

/* Upload zone */
.upload-zone {
    background: #0d1117;
    border: 1.5px dashed #1e2a3a;
    border-radius: 12px;
    padding: 60px 40px;
    text-align: center;
    margin: 40px auto;
    max-width: 600px;
}

/* Calendar */
.cal-day {
    background: #0d1117;
    border: 1px solid #1e2a3a;
    border-radius: 4px;
    padding: 6px;
    text-align: center;
    font-size: 11px;
    min-height: 52px;
}
.cal-day.win  { border-color: #166534; background: #052e16; }
.cal-day.loss { border-color: #991b1b; background: #2d0a0a; }
.cal-day.empty{ opacity: 0.2; }

/* Kaizen score */
.kaizen-score {
    background: linear-gradient(135deg, #0d1117, #0a1628);
    border: 1px solid #2dd4bf33;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
}

/* Selectbox */
.stSelectbox label { color: #94a3b8 !important; font-size: 11px !important; }
.stSelectbox div[data-baseweb="select"] { background: #0d1117 !important; border-color: #1e2a3a !important; }
.stSelectbox div[data-baseweb="select"] * { color: #e2e8f0 !important; }
.stSelectbox [data-baseweb="popover"] * { color: #e2e8f0 !important; background: #0d1117 !important; }

/* Dataframe text */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrame"] * { 
    font-size: 12px !important; 
    font-family: 'JetBrains Mono', monospace !important;
    color: #e2e8f0 !important;
}
[data-testid="stDataFrame"] th { 
    color: #94a3b8 !important; 
    background: #0d1117 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
}

/* General text */
p, span, label { color: #e2e8f0 !important; }
h4 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

# ── Parser MT5 ─────────────────────────────────────────────────────────────────
def parse_mt5(file) -> dict:
    df_raw = pd.read_excel(file, header=None, dtype=str)
    rows = df_raw.values.tolist()
    meta = {"trader": "", "cuenta": "", "empresa": "", "fecha": ""}
    header_row = -1
    for i, r in enumerate(rows[:25]):
        c0 = str(r[0] or "")
        if "ombre" in c0:  meta["trader"]  = str(r[3] or r[1] or "").strip()
        if "uenta" in c0:  meta["cuenta"]  = str(r[3] or r[1] or "").strip()
        if "mpresa" in c0: meta["empresa"] = str(r[3] or r[1] or "").strip()
        if "echa" in c0 and str(r[3] or "").strip()[:4].isdigit():
            meta["fecha"] = str(r[3] or "").strip()
        if "osici" in str(r[1] or "") and "echa" in str(r[0] or ""):
            header_row = i
    if header_row < 0:
        raise ValueError("No se encontró la sección de Posiciones")
    trades = []
    for r in rows[header_row + 1:]:
        c0 = str(r[0] or "")
        if any(x in c0 for x in ["rdene", "ransacc", "Balance:", "Resultado"]):
            break
        try:
            float(str(r[1]).replace(",", "."))
            profit = float(str(r[12]).replace(",", "."))
        except:
            continue
        def n(v):
            try: return float(str(v).replace(",", "."))
            except: return 0.0
        trades.append({
            "open": str(r[0]), "symbol": str(r[2]).strip(),
            "type": str(r[3]).strip().lower(), "volume": n(r[4]),
            "p_in": n(r[5]), "sl": n(r[6]), "tp": n(r[7]),
            "close": str(r[8]), "p_out": n(r[9]),
            "comm": n(r[10]), "swap": n(r[11]),
            "profit": profit, "pnl_net": profit + n(r[10]) + n(r[11]),
        })
    if not trades:
        raise ValueError("No se encontraron operaciones")
    df = pd.DataFrame(trades)
    df["open_dt"]   = pd.to_datetime(df["open"],  format="%Y.%m.%d %H:%M:%S", errors="coerce")
    df["close_dt"]  = pd.to_datetime(df["close"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    df["close_date"]= df["close_dt"].dt.date
    df["month"]     = df["close_dt"].dt.to_period("M").astype(str)
    df["hour"]      = df["close_dt"].dt.hour
    df["weekday"]   = df["close_dt"].dt.day_name()
    df["win"]       = df["profit"] > 0
    df["duration"]  = (df["close_dt"] - df["open_dt"]).dt.total_seconds() / 3600

    stats = {}
    stats["total_ops"]  = len(df)
    stats["winners"]    = int(df["win"].sum())
    stats["losers"]     = stats["total_ops"] - stats["winners"]
    stats["win_rate"]   = stats["winners"] / stats["total_ops"] * 100 if stats["total_ops"] else 0
    stats["pnl_net"]    = df["pnl_net"].sum()
    stats["gross_win"]  = df[df.profit > 0]["profit"].sum()
    stats["gross_loss"] = df[df.profit < 0]["profit"].sum()
    stats["pfactor"]    = stats["gross_win"] / abs(stats["gross_loss"]) if stats["gross_loss"] else 0
    stats["avg_win"]    = df[df.win]["profit"].mean() if df["win"].any() else 0
    stats["avg_loss"]   = df[~df["win"]]["profit"].mean() if (~df["win"]).any() else 0
    stats["best"]       = df["profit"].max()
    stats["worst"]      = df["profit"].min()
    stats["avg_duration"]= df["duration"].mean()

    # Equity curve
    df_sorted = df.sort_values("close_dt")
    df_sorted["equity"] = df_sorted["pnl_net"].cumsum()
    peak = df_sorted["equity"].cummax()
    dd   = (df_sorted["equity"] - peak) / peak.replace(0, np.nan) * 100
    stats["max_dd"] = dd.min() if not dd.isna().all() else 0
    stats["df_sorted"] = df_sorted

    # Kaizen score (0-100)
    wr_score  = min(stats["win_rate"] / 60 * 30, 30)
    pf_score  = min(stats["pfactor"] / 2 * 30, 30)
    rr_ratio  = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
    rr_score  = min(rr_ratio / 2 * 20, 20)
    dd_score  = max(20 + stats["max_dd"] / 5, 0)
    stats["kaizen_score"] = int(wr_score + pf_score + rr_score + dd_score)

    return {"meta": meta, "df": df, "stats": stats}

# ── Chart theme ────────────────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="#080c14", plot_bgcolor="#080c14",
    font=dict(color="#64748b", family="Inter, sans-serif", size=11),
    margin=dict(l=16, r=16, t=32, b=16),
    xaxis=dict(gridcolor="#0f1923", showgrid=True, zeroline=False,
               linecolor="#1e2a3a", tickcolor="#1e2a3a"),
    yaxis=dict(gridcolor="#0f1923", showgrid=True, zeroline=False,
               linecolor="#1e2a3a", tickcolor="#1e2a3a"),
)
GREEN  = "#10b981"
RED    = "#f43f5e"
TEAL   = "#2dd4bf"
BLUE   = "#6366f1"
AMBER  = "#f59e0b"
PURPLE = "#a78bfa"
MUTED  = "#334155"

# ── Global theme toggle ────────────────────────────────────────────────────────
if "light_mode" not in st.session_state:
    st.session_state.light_mode = False

# ── Header ─────────────────────────────────────────────────────────────────────
col_hd, col_toggle = st.columns([5, 1])
with col_hd:
    st.markdown("""
<div class="crz-header">
  <div>
    <div class="crz-logo">CRZ <span>Kaizen</span> Journal</div>
    <div class="crz-tagline">Mejora continua · Trading consciente</div>
  </div>
  <div style="font-size:11px;color:#475569;">改善 · 1% mejor cada día</div>
</div>
""", unsafe_allow_html=True)
with col_toggle:
    st.markdown("<div style='padding-top:12px;'>", unsafe_allow_html=True)
    light_mode = st.toggle("☀️", value=st.session_state.light_mode, help="Modo claro / oscuro")
    st.session_state.light_mode = light_mode
    st.markdown("</div>", unsafe_allow_html=True)

# Apply light mode CSS globally
if light_mode:
    st.markdown("""<style>
    .stApp { background: #f8fafc !important; }
    .crz-header { background: #ffffff !important; border-color: #e2e8f0 !important; }
    .crz-logo { color: #0f172a !important; }
    .crz-tagline { color: #64748b !important; }
    .metric-card { background: #ffffff !important; border-color: #e2e8f0 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important; }
    .metric-value { color: #0f172a !important; }
    .metric-sub { color: #64748b !important; }
    .stTabs [data-baseweb="tab-list"] { border-color: #e2e8f0 !important; }
    .stTabs [data-baseweb="tab"] { color: #64748b !important; }
    .stTabs [aria-selected="true"] { color: #0f172a !important; border-color: #2dd4bf !important; }
    p, span, div, label, h1, h2, h3, h4 { color: #0f172a !important; }
    [data-testid="stDataFrame"] * { color: #0f172a !important; }
    [data-testid="stDataFrame"] th { color: #0f172a !important; background: #f1f5f9 !important; }
    [data-testid="stDataFrame"] td { color: #0f172a !important; background: #ffffff !important; }
    .stSelectbox div[data-baseweb="select"] { background: #ffffff !important; border-color: #e2e8f0 !important; }
    .stSelectbox div[data-baseweb="select"] * { color: #0f172a !important; background: #ffffff !important; }
    .stSelectbox [data-baseweb="popover"] { background: #ffffff !important; }
    .stSelectbox [data-baseweb="popover"] * { color: #0f172a !important; background: #ffffff !important; }
    [data-baseweb="select"] * { color: #0f172a !important; }
    [data-baseweb="popover"] * { color: #0f172a !important; background: #ffffff !important; }
    [role="option"] { color: #0f172a !important; background: #ffffff !important; }
    [role="option"]:hover { background: #f1f5f9 !important; }
    hr { border-color: #e2e8f0 !important; }
    </style>""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Sube tu historial MT5",
    type=["xlsx", "xls"],
    label_visibility="collapsed"
)

if not uploaded:
    _lm = st.session_state.light_mode
    _bg = "#ffffff" if _lm else "#0d1117"
    _border = "#e2e8f0" if _lm else "#1e2a3a"
    _title = "#0f172a" if _lm else "#f1f5f9"
    _sub = "#64748b" if _lm else "#64748b"
    _sub2 = "#94a3b8" if _lm else "#334155"
    st.markdown(f"""
<div style="background:{_bg};border:1.5px dashed {_border};border-radius:12px;
     padding:60px 40px;text-align:center;margin:40px auto;max-width:600px;">
  <div style="font-size:48px;margin-bottom:16px;">📊</div>
  <div style="font-size:20px;font-weight:600;color:{_title};margin-bottom:8px;">Analiza tu trading</div>
  <div style="font-size:14px;color:{_sub};margin-bottom:4px;">Sube tu historial exportado desde MetaTrader 5</div>
  <div style="font-size:12px;color:{_sub2};">MT5 → Historial → Click derecho → Guardar como informe (.xlsx)</div>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ── Parse ──────────────────────────────────────────────────────────────────────
with st.spinner("Analizando tu historial..."):
    try:
        data = parse_mt5(uploaded)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.stop()

df    = data["df"]
stats = data["stats"]
meta  = data["meta"]
df_s  = stats["df_sorted"]

# ── Trader bar ─────────────────────────────────────────────────────────────────
pnl_color = GREEN if stats["pnl_net"] >= 0 else RED
_lm = st.session_state.light_mode
_bar_bg = "#ffffff" if _lm else "#0d1117"
_bar_border = "#e2e8f0" if _lm else "#1e2a3a"
_bar_title = "#0f172a" if _lm else "#f1f5f9"
_bar_sub = "#64748b"
st.markdown(f"""
<div style="background:{_bar_bg};border:1px solid {_bar_border};border-left:4px solid {TEAL};
     border-radius:8px;padding:14px 20px;margin-bottom:24px;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-size:16px;font-weight:600;color:{_bar_title};">{meta['trader'] or 'Mi Cuenta'}</div>
    <div style="font-size:11px;color:{_bar_sub};margin-top:2px;">{meta['cuenta']} · {meta['empresa']} · {meta['fecha']}</div>
  </div>
  <div style="display:flex;gap:24px;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-size:10px;color:{_bar_sub};text-transform:uppercase;letter-spacing:0.1em;">PnL Total</div>
      <div style="font-family:'JetBrains Mono';font-size:18px;font-weight:600;color:{pnl_color};">{stats['pnl_net']:+,.2f}$</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">Win Rate</div>
      <div style="font-family:'JetBrains Mono';font-size:18px;font-weight:600;color:#f1f5f9;">{stats['win_rate']:.1f}%</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">Operaciones</div>
      <div style="font-family:'JetBrains Mono';font-size:18px;font-weight:600;color:#f1f5f9;">{stats['total_ops']}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">Kaizen Score</div>
      <div style="font-family:'JetBrains Mono';font-size:18px;font-weight:600;color:{TEAL};">{stats['kaizen_score']}/100</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_dash, tab_cal, tab_ops, tab_sym, tab_hora, tab_kaizen = st.tabs([
    "◈ Dashboard", "⬚ Calendario", "≡ Operaciones",
    "◎ Símbolo", "◷ Horario", "△ Kaizen"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    # KPI cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    cards = [
        (c1, "PnL Neto", f"{stats['pnl_net']:+,.2f}$", "green" if stats['pnl_net'] >= 0 else "red",
         f"{stats['gross_win']:+,.0f} / {stats['gross_loss']:+,.0f}"),
        (c2, "Win Rate", f"{stats['win_rate']:.1f}%", "blue",
         f"{stats['winners']}G · {stats['losers']}P"),
        (c3, "Factor Beneficio", f"{stats['pfactor']:.2f}", "teal",
         "Objetivo > 1.5"),
        (c4, "Max Drawdown", f"{stats['max_dd']:.1f}%", "red",
         "Pérdida máx. acumulada"),
        (c5, "Mejor Trade", f"{stats['best']:+,.2f}$", "green",
         f"Peor: {stats['worst']:+,.2f}$"),
        (c6, "Duración Media", f"{stats['avg_duration']:.1f}h", "purple",
         "Por operación"),
    ]
    for col, label, val, color, sub in cards:
        col.markdown(f"""
<div class="metric-card {color}">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{val}</div>
  <div class="metric-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Equity curve + Daily PnL
    col_eq, col_daily = st.columns([3, 2])

    with col_eq:
        peak    = df_s["equity"].cummax()
        idx_max = df_s["equity"].idxmax()
        idx_min = df_s["equity"].idxmin()
        dd_pct  = ((df_s["equity"] - peak) / peak.replace(0, np.nan) * 100).fillna(0)

        HUD_LAYOUT = dict(
            paper_bgcolor="#020408",
            plot_bgcolor="#020408",
            font=dict(color="#334155", family="JetBrains Mono", size=10),
            margin=dict(l=48, r=16, t=36, b=36),
            xaxis=dict(
                gridcolor="#0a0f1a", showgrid=True, zeroline=False,
                linecolor="#0f1923", tickcolor="#0f1923",
                tickfont=dict(color="#334155", size=9),
            ),
            yaxis=dict(
                gridcolor="#0a0f1a", showgrid=True, zeroline=False,
                linecolor="#0f1923", tickcolor="#0f1923",
                tickfont=dict(color="#334155", size=9),
                tickprefix="$",
            ),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                bordercolor="#0f1923",
                font=dict(color="#475569", size=9),
                x=0.01, y=0.99
            )
        )

        fig_eq = go.Figure()

        # Drawdown fill (peak → equity)
        fig_eq.add_trace(go.Scatter(
            x=df_s["close_dt"], y=peak,
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip"
        ))
        fig_eq.add_trace(go.Scatter(
            x=df_s["close_dt"], y=df_s["equity"],
            mode="lines", line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(244,63,94,0.07)",
            showlegend=False, hoverinfo="skip", name="Drawdown"
        ))

        # Peak dotted line
        fig_eq.add_trace(go.Scatter(
            x=df_s["close_dt"], y=peak,
            mode="lines", name="Peak",
            line=dict(color="#1e3a2a", width=1, dash="dot"),
            showlegend=True,
            hoverinfo="skip"
        ))

        # Zero line fill
        fig_eq.add_trace(go.Scatter(
            x=df_s["close_dt"], y=df_s["equity"],
            mode="none", fill="tozeroy",
            fillcolor="rgba(45,212,191,0.03)",
            showlegend=False, hoverinfo="skip"
        ))

        # Main equity line — thin & sharp
        fig_eq.add_trace(go.Scatter(
            x=df_s["close_dt"], y=df_s["equity"],
            mode="lines", name="Equity",
            line=dict(color=TEAL, width=1.2),
            hovertemplate="<b>%{x|%d %b %Y %H:%M}</b><br>Equity: <b>$%{y:+,.2f}</b><extra></extra>"
        ))

        # Horizontal grid helper lines
        eq_range = df_s["equity"]
        for level in [eq_range.max()*0.75, eq_range.max()*0.5, eq_range.max()*0.25]:
            if abs(level) > 1:
                fig_eq.add_hline(
                    y=level, line_color="#0a0f1a",
                    line_width=1, opacity=1
                )

        # Zero line
        fig_eq.add_hline(y=0, line_color="#1e2a3a", line_width=1, opacity=0.8)

        # Max marker
        fig_eq.add_trace(go.Scatter(
            x=[df_s.loc[idx_max, "close_dt"]],
            y=[df_s.loc[idx_max, "equity"]],
            mode="markers+text",
            marker=dict(color=GREEN, size=6, symbol="circle",
                       line=dict(color="#020408", width=1)),
            text=[f"▲ ${df_s.loc[idx_max,'equity']:+,.0f}"],
            textposition="top right",
            textfont=dict(size=9, color=GREEN, family="JetBrains Mono"),
            showlegend=False, hoverinfo="skip"
        ))

        # Min marker
        fig_eq.add_trace(go.Scatter(
            x=[df_s.loc[idx_min, "close_dt"]],
            y=[df_s.loc[idx_min, "equity"]],
            mode="markers+text",
            marker=dict(color=RED, size=6, symbol="circle",
                       line=dict(color="#020408", width=1)),
            text=[f"▼ ${df_s.loc[idx_min,'equity']:+,.0f}"],
            textposition="bottom right",
            textfont=dict(size=9, color=RED, family="JetBrains Mono"),
            showlegend=False, hoverinfo="skip"
        ))

        # Title annotation HUD style
        fig_eq.add_annotation(
            x=0, y=1.06, xref="paper", yref="paper",
            text="◈ EQUITY CURVE",
            font=dict(size=10, color="#2dd4bf", family="JetBrains Mono"),
            showarrow=False, align="left"
        )
        fig_eq.add_annotation(
            x=1, y=1.06, xref="paper", yref="paper",
            text=f"MAX DD: {dd_pct.min():.1f}%",
            font=dict(size=10, color="#f43f5e", family="JetBrains Mono"),
            showarrow=False, align="right"
        )

        fig_eq.update_layout(**HUD_LAYOUT, height=300,
            shapes=[dict(
                type="rect", xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color="#0f1923", width=1),
                fillcolor="rgba(0,0,0,0)"
            )]
        )
        st.plotly_chart(fig_eq, use_container_width=True)

    with col_daily:
        st.markdown("#### PnL Diario + Tendencia")
        daily = df_s.groupby("close_date")["pnl_net"].sum().reset_index()
        daily.columns = ["fecha", "pnl"]
        daily["ma7"] = daily["pnl"].rolling(7, min_periods=1).mean()
        colors_bar = [GREEN if v >= 0 else RED for v in daily["pnl"]]
        fig_daily = go.Figure()
        fig_daily.add_trace(go.Bar(
            x=daily["fecha"], y=daily["pnl"],
            marker_color=colors_bar,
            marker_line_width=0,
            opacity=0.7,
            name="PnL",
            hovertemplate="%{x}<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        fig_daily.add_trace(go.Scatter(
            x=daily["fecha"], y=daily["ma7"],
            mode="lines", name="Media 7d",
            line=dict(color=AMBER, width=1.5, dash="dot"),
            hovertemplate="Media 7d: $%{y:+,.2f}<extra></extra>"
        ))
        fig_daily.add_hline(y=0, line_color=MUTED, opacity=0.3, line_width=1)
        fig_daily.update_layout(**LAYOUT, height=280,
            title=dict(text="PnL Diario", font=dict(size=12, color="#94a3b8")))
        st.plotly_chart(fig_daily, use_container_width=True)

    # Win/Loss distribution + RR ratio
    col_wl, col_rr = st.columns(2)

    with col_wl:
        st.markdown("#### Distribución de Resultados")
        wins   = df[df.profit > 0]["profit"].tolist()
        losses = df[df.profit < 0]["profit"].tolist()
        fig_wl = go.Figure()
        fig_wl.add_trace(go.Histogram(
            x=wins, name="Ganadoras",
            marker_color=GREEN, opacity=0.6,
            nbinsx=20, marker_line_width=0
        ))
        fig_wl.add_trace(go.Histogram(
            x=losses, name="Perdedoras",
            marker_color=RED, opacity=0.6,
            nbinsx=20, marker_line_width=0
        ))
        # Add vertical lines for averages
        fig_wl.add_vline(x=stats["avg_win"], line_color=GREEN,
            line_dash="dash", opacity=0.8, line_width=1.5,
            annotation_text=f"Media G: ${stats['avg_win']:,.0f}",
            annotation_font_color=GREEN, annotation_font_size=9)
        fig_wl.add_vline(x=stats["avg_loss"], line_color=RED,
            line_dash="dash", opacity=0.8, line_width=1.5,
            annotation_text=f"Media P: ${stats['avg_loss']:,.0f}",
            annotation_font_color=RED, annotation_font_size=9)
        fig_wl.update_layout(**LAYOUT, height=240, barmode="overlay",
            title=dict(text="Distribución Resultados", font=dict(size=12, color="#94a3b8")))
        st.plotly_chart(fig_wl, use_container_width=True)

    with col_rr:
        st.markdown("#### Win vs Loss — Comparativa")
        rr = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
        fig_rr = go.Figure()
        # Horizontal bars
        fig_rr.add_trace(go.Bar(
            y=["Ganancia Media", "Pérdida Media"],
            x=[stats["avg_win"], abs(stats["avg_loss"])],
            orientation="h",
            marker_color=[GREEN, RED],
            marker_line_width=0,
            opacity=0.85,
            text=[f"${stats['avg_win']:,.2f}", f"${abs(stats['avg_loss']):,.2f}"],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
            hovertemplate="%{y}: $%{x:,.2f}<extra></extra>"
        ))
        fig_rr.add_annotation(
            x=0.98, y=0.05, xref="paper", yref="paper",
            text=f"RR: {rr:.2f}x",
            font=dict(size=16, color=TEAL, family="JetBrains Mono"),
            showarrow=False, align="right"
        )
        fig_rr.update_layout(**LAYOUT, height=240, showlegend=False,
            title=dict(text="Avg Win vs Avg Loss", font=dict(size=12, color="#94a3b8")))
        st.plotly_chart(fig_rr, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB CALENDARIO
# ══════════════════════════════════════════════════════════════════════════════
with tab_cal:
    st.markdown("#### Rendimiento por Día")

    daily_cal = df_s.groupby("close_date").agg(
        pnl=("pnl_net", "sum"),
        ops=("pnl_net", "count")
    ).reset_index()
    daily_cal["close_date"] = pd.to_datetime(daily_cal["close_date"])

    months = sorted(daily_cal["close_date"].dt.to_period("M").unique())
    months_str = [str(m) for m in months]

    # Session state for calendar navigation and theme
    if "cal_idx" not in st.session_state:
        st.session_state.cal_idx = len(months_str) - 1
    if "cal_light" not in st.session_state:
        st.session_state.cal_light = False

    # Navigation bar
    nav1, nav2, nav3, nav4, nav5 = st.columns([1, 1, 3, 1, 1])
    with nav1:
        if st.button("◀◀", help="Primer mes"):
            st.session_state.cal_idx = 0
    with nav2:
        if st.button("◀", help="Mes anterior"):
            st.session_state.cal_idx = max(0, st.session_state.cal_idx - 1)
    with nav3:
        sel_month = st.selectbox("Mes", months_str,
            index=st.session_state.cal_idx, label_visibility="collapsed")
        st.session_state.cal_idx = months_str.index(sel_month)
    with nav4:
        if st.button("▶", help="Mes siguiente"):
            st.session_state.cal_idx = min(len(months_str)-1, st.session_state.cal_idx + 1)
    with nav5:
        if st.button("▶▶", help="Último mes"):
            st.session_state.cal_idx = len(months_str) - 1

    # Light/dark toggle uses global setting
    light_mode = st.session_state.light_mode

    sel_month = months_str[st.session_state.cal_idx]

    # Calendar colors based on mode
    if light_mode:
        bg_main    = "#ffffff"
        bg_win     = "#dcfce7"
        bg_loss    = "#fee2e2"
        border_win = "#16a34a"
        border_loss= "#dc2626"
        text_day   = "#374151"
        text_empty = "#d1d5db"
        text_ops   = "#6b7280"
        header_col = "#374151"
    else:
        bg_main    = "#0d1117"
        bg_win     = "#052e16"
        bg_loss    = "#2d0a0a"
        border_win = "#166534"
        border_loss= "#991b1b"
        text_day   = "#94a3b8"
        text_empty = "#1e2a3a"
        text_ops   = "#475569"
        header_col = "#475569"

    y, m = int(sel_month[:4]), int(sel_month[5:7])
    month_names = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
                   7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
    st.markdown(f"<div style='text-align:center;font-size:16px;font-weight:700;color:#f1f5f9;margin:8px 0;'>{month_names[m]} {y}</div>", unsafe_allow_html=True)

    month_data = daily_cal[daily_cal["close_date"].dt.to_period("M") == sel_month]
    day_map = {row["close_date"].day: row for _, row in month_data.iterrows()}

    days_in_month = calendar.monthrange(y, m)[1]
    first_weekday = calendar.monthrange(y, m)[0]
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    # Header days
    cols_h = st.columns(7)
    for i, d in enumerate(day_names):
        cols_h[i].markdown(f"<div style='text-align:center;font-size:11px;color:{header_col};font-weight:600;padding:6px 0;'>{d}</div>", unsafe_allow_html=True)

    # Grid
    total_cells = first_weekday + days_in_month
    rows_needed = (total_cells + 6) // 7
    cell = 0

    for week in range(rows_needed):
        cols = st.columns(7)
        for wd in range(7):
            day_num = cell - first_weekday + 1
            if cell < first_weekday or day_num > days_in_month:
                cols[wd].markdown(f"<div style='background:{bg_main};border:1px solid {text_empty};border-radius:4px;padding:6px;min-height:52px;opacity:0.2;text-align:center;'>·</div>", unsafe_allow_html=True)
            else:
                if day_num in day_map:
                    row = day_map[day_num]
                    pnl = row["pnl"]
                    ops = row["ops"]
                    bg    = bg_win if pnl >= 0 else bg_loss
                    bord  = border_win if pnl >= 0 else border_loss
                    color = GREEN if pnl >= 0 else RED
                    cols[wd].markdown(f"""
<div style='background:{bg};border:1px solid {bord};border-radius:4px;padding:6px;min-height:52px;text-align:center;'>
  <div style='font-size:11px;color:{text_day};font-weight:600;'>{day_num}</div>
  <div style='font-family:JetBrains Mono;font-size:11px;color:{color};font-weight:700;'>{pnl:+,.0f}$</div>
  <div style='font-size:9px;color:{text_ops};'>{ops} ops</div>
</div>""", unsafe_allow_html=True)
                else:
                    cols[wd].markdown(f"""
<div style='background:{bg_main};border:1px solid {text_empty};border-radius:4px;padding:6px;min-height:52px;text-align:center;'>
  <div style='font-size:11px;color:{text_day};'>{day_num}</div>
</div>""", unsafe_allow_html=True)
            cell += 1

    # Monthly summary
    st.markdown("<br>", unsafe_allow_html=True)
    m_pnl  = month_data["pnl"].sum()
    m_dias = len(month_data)
    m_win  = len(month_data[month_data["pnl"] > 0])
    m_color= GREEN if m_pnl >= 0 else RED

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card {'green' if m_pnl>=0 else 'red'}'><div class='metric-label'>PnL del Mes</div><div class='metric-value' style='color:{m_color};font-size:22px;'>{m_pnl:+,.2f}$</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card blue'><div class='metric-label'>Días Activos</div><div class='metric-value' style='font-size:22px;'>{m_dias}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card teal'><div class='metric-label'>Días Ganadores</div><div class='metric-value' style='font-size:22px;'>{m_win}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card amber'><div class='metric-label'>% Días Positivos</div><div class='metric-value' style='font-size:22px;'>{m_win/m_dias*100:.0f}%</div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB OPERACIONES
# ══════════════════════════════════════════════════════════════════════════════
with tab_ops:
    st.markdown("#### Historial de Operaciones")

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        syms = ["Todos"] + sorted(df["symbol"].unique().tolist())
        sel_sym = st.selectbox("Símbolo", syms)
    with fc2:
        types = ["Todos", "buy", "sell"]
        sel_type = st.selectbox("Tipo", types)
    with fc3:
        results = ["Todos", "Ganadoras", "Perdedoras"]
        sel_res = st.selectbox("Resultado", results)

    df_view = df.copy()
    if sel_sym != "Todos":  df_view = df_view[df_view["symbol"] == sel_sym]
    if sel_type != "Todos": df_view = df_view[df_view["type"] == sel_type.lower()]
    if sel_res == "Ganadoras": df_view = df_view[df_view["win"]]
    if sel_res == "Perdedoras":df_view = df_view[~df_view["win"]]

    display = df_view[["open","symbol","type","volume","p_in","close","p_out","comm","swap","profit","pnl_net"]].copy()
    display.columns = ["Apertura","Símbolo","Tipo","Vol","Entrada","Cierre","Salida","Comisión","Swap","Beneficio","PnL Neto"]

    def color_profit(val):
        if isinstance(val, (int, float)):
            if val > 0: return "color: #16a34a; font-weight: 600"
            if val < 0: return "color: #dc2626; font-weight: 600"
        return ""

    st.dataframe(
        display.style
            .map(color_profit, subset=["Beneficio", "PnL Neto"])
            .format({
                "Entrada": "{:.2f}", "Salida": "{:.2f}",
                "Comisión": "{:.2f}", "Swap": "{:.2f}",
                "Beneficio": "{:+.2f}", "PnL Neto": "{:+.2f}"
            }),
        use_container_width=True,
        height=420
    )

    # Download
    csv = display.to_csv(index=False)
    st.download_button(
        "⬇ Descargar CSV",
        data=csv,
        file_name=f"CRZ_Journal_{meta['trader'].replace(' ','_')}.csv",
        mime="text/csv"
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB POR SÍMBOLO
# ══════════════════════════════════════════════════════════════════════════════
with tab_sym:
    st.markdown("#### Análisis por Símbolo")

    sym_g = df.groupby("symbol").agg(
        Ops=("profit","count"),
        Ganadoras=("win","sum"),
        PnL=("pnl_net","sum"),
        Mejor=("profit","max"),
        Peor=("profit","min"),
        Gan_bruta=("profit", lambda x: x[x>0].sum()),
        Perd_bruta=("profit", lambda x: x[x<0].sum()),
    ).reset_index()
    sym_g["Win_Rate"] = sym_g["Ganadoras"] / sym_g["Ops"] * 100
    sym_g["Factor"]   = sym_g["Gan_bruta"] / sym_g["Perd_bruta"].abs().replace(0, np.nan)
    sym_g = sym_g.sort_values("PnL", ascending=False)

    col_bar, col_wr = st.columns(2)

    with col_bar:
        # Bar + scatter win rate overlay
        fig_sym = go.Figure()
        fig_sym.add_trace(go.Bar(
            x=sym_g["symbol"], y=sym_g["PnL"],
            marker_color=[GREEN if v >= 0 else RED for v in sym_g["PnL"]],
            marker_line_width=0, opacity=0.8,
            name="PnL",
            hovertemplate="%{x}<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        fig_sym.add_trace(go.Scatter(
            x=sym_g["symbol"], y=sym_g["Win_Rate"],
            mode="markers+text",
            marker=dict(color=AMBER, size=10, symbol="diamond"),
            text=[f"{v:.0f}%" for v in sym_g["Win_Rate"]],
            textposition="top center",
            textfont=dict(size=9, color=AMBER),
            name="Win Rate",
            yaxis="y2",
            hovertemplate="%{x}<br>Win Rate: %{y:.1f}%<extra></extra>"
        ))
        fig_sym.update_layout(**LAYOUT, height=300,
            title=dict(text="PnL + Win Rate por Símbolo", font=dict(size=12, color="#94a3b8")),
            yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                       showgrid=False, tickfont=dict(color=AMBER, size=10))
        )
        st.plotly_chart(fig_sym, use_container_width=True)

    with col_wr:
        # Radar chart
        if len(sym_g) >= 3:
            fig_radar = go.Figure(go.Scatterpolar(
                r=sym_g["Win_Rate"].tolist(),
                theta=sym_g["symbol"].tolist(),
                fill="toself",
                fillcolor=f"rgba(99,102,241,0.15)",
                line=dict(color=BLUE, width=2),
                marker=dict(color=BLUE, size=6),
                name="Win Rate"
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#080c14",
                    radialaxis=dict(visible=True, range=[0, 100],
                                   gridcolor="#1e2a3a", tickcolor="#1e2a3a",
                                   tickfont=dict(color="#475569", size=9)),
                    angularaxis=dict(gridcolor="#1e2a3a",
                                    tickfont=dict(color="#94a3b8", size=10))
                ),
                paper_bgcolor="#080c14",
                plot_bgcolor="#080c14",
                margin=dict(l=40, r=40, t=40, b=40),
                height=300,
                showlegend=False,
                title=dict(text="Win Rate por Símbolo", font=dict(size=12, color="#94a3b8"))
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            fig_wr = go.Figure(go.Bar(
                x=sym_g["symbol"], y=sym_g["Win_Rate"],
                marker_color=BLUE, marker_line_width=0, opacity=0.8,
                text=[f"{v:.0f}%" for v in sym_g["Win_Rate"]],
                textposition="outside",
                textfont=dict(color="#f1f5f9", size=11),
            ))
            fig_wr.add_hline(y=50, line_dash="dash", line_color=MUTED, opacity=0.5)
            fig_wr.update_layout(**LAYOUT, height=300,
                title=dict(text="Win Rate por Símbolo", font=dict(size=12, color="#94a3b8")))
            fig_wr.update_yaxes(range=[0, 105], ticksuffix="%")
            st.plotly_chart(fig_wr, use_container_width=True)

    st.dataframe(
        sym_g[["symbol","Ops","Ganadoras","Win_Rate","PnL","Factor","Mejor","Peor"]]
        .rename(columns={"symbol":"Símbolo","Win_Rate":"Win Rate %","Factor":"Factor Ben."})
        .style
        .set_properties(**{"color": "#e2e8f0"})
        .map(color_profit, subset=["PnL","Mejor","Peor"])
        .format({"Win Rate %":"{:.1f}%","PnL":"{:+.2f}","Factor Ben.":"{:.2f}",
                 "Mejor":"{:+.2f}","Peor":"{:.2f}"}),
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB POR HORARIO
# ══════════════════════════════════════════════════════════════════════════════
with tab_hora:
    st.markdown("#### Análisis por Horario y Día de Semana")

    hr_g = df.groupby("hour").agg(
        ops=("profit","count"),
        pnl=("pnl_net","sum"),
        wins=("win","sum")
    ).reset_index()
    hr_g["win_rate"] = hr_g["wins"] / hr_g["ops"] * 100

    wd_g = df.groupby("weekday").agg(
        ops=("profit","count"),
        pnl=("pnl_net","sum"),
        wins=("win","sum")
    ).reset_index()
    wd_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    wd_names = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
                "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
    wd_g["weekday"] = pd.Categorical(wd_g["weekday"], categories=wd_order, ordered=True)
    wd_g = wd_g.sort_values("weekday")
    wd_g["weekday"] = wd_g["weekday"].map(wd_names)
    wd_g["win_rate"] = wd_g["wins"] / wd_g["ops"] * 100

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        fig_hr = go.Figure()
        # Area for win rate
        fig_hr.add_trace(go.Scatter(
            x=hr_g["hour"], y=hr_g["win_rate"],
            mode="lines", name="Win Rate",
            line=dict(color=TEAL, width=0),
            fill="tozeroy",
            fillcolor="rgba(45,212,191,0.08)",
            hoverinfo="skip", showlegend=False
        ))
        # Bars for PnL
        fig_hr.add_trace(go.Bar(
            x=hr_g["hour"], y=hr_g["pnl"],
            marker_color=[GREEN if v >= 0 else RED for v in hr_g["pnl"]],
            marker_line_width=0, opacity=0.8,
            name="PnL",
            hovertemplate="Hora %{x}:00<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        # Win rate line
        fig_hr.add_trace(go.Scatter(
            x=hr_g["hour"], y=hr_g["win_rate"],
            mode="lines+markers", name="Win Rate %",
            line=dict(color=TEAL, width=1.5),
            marker=dict(size=4, color=TEAL),
            hovertemplate="Hora %{x}:00<br>Win Rate: %{y:.1f}%<extra></extra>"
        ))
        fig_hr.add_hline(y=0, line_color=MUTED, opacity=0.3, line_width=1)
        fig_hr.update_layout(**LAYOUT, height=300,
            title=dict(text="PnL + Win Rate por Hora", font=dict(size=12, color="#94a3b8")))
        st.plotly_chart(fig_hr, use_container_width=True)

    with col_h2:
        # Polar/radial chart for weekday
        fig_wd = go.Figure()
        fig_wd.add_trace(go.Barpolar(
            r=wd_g["pnl"].abs().tolist(),
            theta=wd_g["weekday"].tolist(),
            marker_color=[GREEN if v >= 0 else RED for v in wd_g["pnl"]],
            marker_line_width=0,
            opacity=0.8,
            name="PnL",
            hovertemplate="%{theta}<br>PnL: $%{customdata:+,.2f}<extra></extra>",
            customdata=wd_g["pnl"].tolist()
        ))
        fig_wd.update_layout(
            polar=dict(
                bgcolor="#080c14",
                radialaxis=dict(visible=True, gridcolor="#1e2a3a",
                               tickfont=dict(color="#475569", size=8)),
                angularaxis=dict(gridcolor="#1e2a3a",
                                tickfont=dict(color="#94a3b8", size=10))
            ),
            paper_bgcolor="#080c14",
            margin=dict(l=40, r=40, t=40, b=40),
            height=300, showlegend=False,
            title=dict(text="PnL por Día de Semana", font=dict(size=12, color="#94a3b8"))
        )
        st.plotly_chart(fig_wd, use_container_width=True)

    # Heatmap hora x día
    st.markdown("#### Mapa de Calor — Hora × Día")
    df_heat = df.copy()
    df_heat["weekday_es"] = df_heat["weekday"].map(wd_names)
    heat = df_heat.groupby(["weekday_es","hour"])["pnl_net"].sum().reset_index()
    heat_pivot = heat.pivot(index="weekday_es", columns="hour", values="pnl_net").fillna(0)

    day_order_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    heat_pivot = heat_pivot.reindex([d for d in day_order_es if d in heat_pivot.index])

    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=[f"{h}:00" for h in heat_pivot.columns],
        y=heat_pivot.index.tolist(),
        colorscale=[[0,"#7f1d1d"],[0.5,"#0d1117"],[1,"#14532d"]],
        zmid=0,
        hovertemplate="Hora: %{x}<br>Día: %{y}<br>PnL: $%{z:+,.2f}<extra></extra>"
    ))
    fig_heat.update_layout(**LAYOUT, height=280)
    st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB KAIZEN SCORE — HUD COCKPIT STYLE
# ══════════════════════════════════════════════════════════════════════════════
with tab_kaizen:

    score = stats["kaizen_score"]
    wr_score  = min(stats["win_rate"] / 60 * 30, 30)
    pf_score  = min(stats["pfactor"] / 2 * 30, 30)
    rr_ratio  = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
    rr_score  = min(rr_ratio / 2 * 20, 20)
    dd_score  = max(20 + stats["max_dd"] / 5, 0)

    if score >= 80:   lvl_name, lvl_color, lvl_emoji = "MASTER",    "#10b981", "🏆"
    elif score >= 60: lvl_name, lvl_color, lvl_emoji = "PRO",       "#2dd4bf", "⚡"
    elif score >= 40: lvl_name, lvl_color, lvl_emoji = "PROGRESS",  "#f59e0b", "📈"
    else:             lvl_name, lvl_color, lvl_emoji = "TRAINING",  "#f43f5e", "🎯"

    best_hour  = hr_g.loc[hr_g["pnl"].idxmax(), "hour"] if len(hr_g) else 0
    worst_hour = hr_g.loc[hr_g["pnl"].idxmin(), "hour"] if len(hr_g) else 0
    best_sym   = sym_g.iloc[0]["symbol"] if len(sym_g) else "—"
    worst_sym  = sym_g.iloc[-1]["symbol"] if len(sym_g) else "—"

    def hud_circle(pct, color, size, stroke, label, value):
        r   = (size - stroke) / 2
        cx  = size / 2
        cir = 2 * 3.14159 * r
        dash= cir * min(pct / 100, 1)
        gap = cir - dash
        return f"""
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow_{label.replace(' ','')}">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- Background track -->
  <circle cx="{cx}" cy="{cx}" r="{r}" fill="none"
    stroke="#0f1923" stroke-width="{stroke}"/>
  <!-- Tick marks -->
  {"".join([
    f'<line x1="{cx}" y1="{stroke+2}" x2="{cx}" y2="{stroke+6}" stroke="#1e2a3a" stroke-width="1.5"'
    f' transform="rotate({i*30} {cx} {cx})"/>'
    for i in range(12)
  ])}
  <!-- Progress arc -->
  <circle cx="{cx}" cy="{cx}" r="{r}" fill="none"
    stroke="{color}" stroke-width="{stroke}"
    stroke-dasharray="{dash:.1f} {gap:.1f}"
    stroke-linecap="round"
    transform="rotate(-90 {cx} {cx})"
    filter="url(#glow_{label.replace(' ','')})"
    opacity="0.95"/>
  <!-- Center value -->
  <text x="{cx}" y="{cx - 8}" text-anchor="middle"
    font-family="JetBrains Mono" font-size="{int(size*0.14)}"
    font-weight="700" fill="{color}">{value}</text>
  <!-- Center label -->
  <text x="{cx}" y="{cx + 10}" text-anchor="middle"
    font-family="Inter" font-size="{int(size*0.075)}"
    font-weight="500" fill="#475569" letter-spacing="1">{label.upper()}</text>
  <!-- Percentage -->
  <text x="{cx}" y="{cx + 22}" text-anchor="middle"
    font-family="JetBrains Mono" font-size="{int(size*0.07)}"
    fill="#334155">{pct:.0f}%</text>
</svg>"""

    # ── HUD CSS ───────────────────────────────────────────────────────────────
    st.markdown("""
<style>
@keyframes scanline {
  0%   { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.3; }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
.hud-container {
  background: radial-gradient(ellipse at center, #050810 0%, #020408 100%);
  border: 1px solid #0f1923;
  border-radius: 16px;
  padding: 28px;
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.6s ease;
}
.hud-container::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #2dd4bf44, #2dd4bf, #2dd4bf44, transparent);
}
.hud-container::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #2dd4bf22, #2dd4bf44, #2dd4bf22, transparent);
}
.hud-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-top: 16px;
}
.hud-stat {
  background: #0a0f1a;
  border: 1px solid #1e2a3a;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hud-label {
  font-size: 9px;
  color: #334155;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 600;
}
.hud-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 700;
}
.hud-online {
  display: inline-block;
  width: 6px; height: 6px;
  background: #10b981;
  border-radius: 50%;
  animation: blink 2s infinite;
  margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

    # ── Main HUD panel ────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="hud-container">
  <!-- Header bar -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
    <div>
      <div style="font-size:9px;color:#334155;letter-spacing:0.2em;text-transform:uppercase;">CRZ KAIZEN JOURNAL · PERFORMANCE HUD</div>
      <div style="font-size:14px;font-weight:700;color:#e2e8f0;margin-top:2px;">{meta['trader'] or 'Mi Cuenta'}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:9px;color:#334155;"><span class="hud-online"></span>SISTEMA ACTIVO</div>
      <div style="font-size:11px;color:{lvl_color};font-weight:700;margin-top:2px;">{lvl_emoji} NIVEL {lvl_name}</div>
    </div>
  </div>

  <!-- Divider -->
  <div style="height:1px;background:linear-gradient(90deg,transparent,#1e2a3a,transparent);margin-bottom:20px;"></div>

  <!-- Corner decorations -->
  <div style="position:absolute;top:16px;left:16px;width:16px;height:16px;border-top:2px solid {lvl_color}66;border-left:2px solid {lvl_color}66;"></div>
  <div style="position:absolute;top:16px;right:16px;width:16px;height:16px;border-top:2px solid {lvl_color}66;border-right:2px solid {lvl_color}66;"></div>
  <div style="position:absolute;bottom:16px;left:16px;width:16px;height:16px;border-bottom:2px solid {lvl_color}66;border-left:2px solid {lvl_color}66;"></div>
  <div style="position:absolute;bottom:16px;right:16px;width:16px;height:16px;border-bottom:2px solid {lvl_color}66;border-right:2px solid {lvl_color}66;"></div>

</div>
""", unsafe_allow_html=True)

    # ── Circles row ───────────────────────────────────────────────────────────
    circles = [
        (score,              lvl_color, 180, 14, "Score",    str(score)),
        (wr_score/30*100,    BLUE,      140, 11, "Win Rate", f"{stats['win_rate']:.0f}%"),
        (pf_score/30*100,    TEAL,      140, 11, "Factor",   f"{stats['pfactor']:.1f}x"),
        (rr_score/20*100,    PURPLE,    140, 11, "R/R",      f"{rr_ratio:.1f}x"),
        (dd_score/20*100,    AMBER,     140, 11, "DD Ctrl",  f"{abs(stats['max_dd']):.0f}%"),
    ]

    c_main, c1, c2, c3, c4 = st.columns([1.4, 1, 1, 1, 1])
    for col_w, (pct, color, size, stroke, label, val) in zip(
        [c_main, c1, c2, c3, c4], circles
    ):
        svg = hud_circle(pct, color, size, stroke, label, val)
        col_w.markdown(
            f"<div style='display:flex;justify-content:center;align-items:center;"
            f"background:#050810;border:1px solid #0f1923;border-radius:12px;"
            f"padding:12px;margin:4px;'>{svg}</div>",
            unsafe_allow_html=True
        )

    # ── Stats grid ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    stats_grid = [
        ("PnL Total",      f"{stats['pnl_net']:+,.2f}$",    GREEN if stats["pnl_net"] >= 0 else RED),
        ("Operaciones",    str(stats["total_ops"]),           "#e2e8f0"),
        ("Mejor Trade",    f"{stats['best']:+,.2f}$",        GREEN),
        ("Peor Trade",     f"{stats['worst']:+,.2f}$",       RED),
        ("Mejor Hora",     f"{best_hour}:00",                TEAL),
        ("Peor Hora",      f"{worst_hour}:00",               "#f43f5e"),
        ("Mejor Símbolo",  best_sym,                         GREEN),
        ("Evitar",         worst_sym,                        RED),
        ("Ganadoras",      str(stats["winners"]),            GREEN),
        ("Perdedoras",     str(stats["losers"]),             RED),
        ("Avg Ganadora",   f"{stats['avg_win']:+,.2f}$",    GREEN),
        ("Avg Perdedora",  f"{stats['avg_loss']:+,.2f}$",   RED),
    ]

    rows = [stats_grid[i:i+4] for i in range(0, len(stats_grid), 4)]
    for row in rows:
        cols_r = st.columns(4)
        for col_w, (label, val, color) in zip(cols_r, row):
            col_w.markdown(f"""
<div class="hud-stat">
  <div class="hud-label">{label}</div>
  <div class="hud-val" style="color:{color};">{val}</div>
</div>""", unsafe_allow_html=True)

    # ── Mission log ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:9px;color:#334155;letter-spacing:0.2em;"
        "text-transform:uppercase;margin-bottom:12px;'>"
        "▸ MISIONES ACTIVAS</div>",
        unsafe_allow_html=True
    )

    missions = []
    if stats["win_rate"] < 60:
        missions.append((BLUE,   "WIN RATE",   f"{stats['win_rate']:.1f}% → 60%",   "Menos trades, más calidad en las entradas"))
    if stats["pfactor"] < 2.0:
        missions.append((TEAL,   "FACTOR",     f"{stats['pfactor']:.2f} → 2.0",     "Deja correr ganadoras, corta perdedoras antes"))
    if rr_ratio < 2.0:
        missions.append((PURPLE, "R/R RATIO",  f"{rr_ratio:.2f} → 2.0",            "TP mínimo el doble que el SL en cada trade"))
    if stats["max_dd"] < -10:
        missions.append((AMBER,  "DRAWDOWN",   f"{stats['max_dd']:.1f}% → -10%",   "Reduce tamaño de posición hasta estabilizar"))
    missions.append((TEAL,  "HORARIO",    f"Opera más a las {best_hour}:00",       f"Evita las {worst_hour}:00 — menor rendimiento"))
    missions.append((BLUE,  "SÍMBOLO",    f"Especialízate en {best_sym}",          f"Reduce exposición en {worst_sym}"))

    for col, tag, stat_txt, advice in missions[:5]:
        st.markdown(f"""
<div style="background:#050810;border:1px solid #0f1923;border-left:2px solid {col};
     border-radius:6px;padding:10px 14px;margin-bottom:6px;
     display:flex;align-items:center;gap:16px;">
  <div style="font-size:9px;font-weight:700;color:{col};letter-spacing:0.12em;
       min-width:80px;text-transform:uppercase;">{tag}</div>
  <div style="font-family:'JetBrains Mono';font-size:11px;color:#e2e8f0;min-width:140px;">{stat_txt}</div>
  <div style="font-size:10px;color:#475569;">▸ {advice}</div>
</div>""", unsafe_allow_html=True)
