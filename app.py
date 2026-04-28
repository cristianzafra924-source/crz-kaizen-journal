import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar
import json, base64, requests as _req_app
from pathlib import Path
import streamlit.components.v1 as components
from mt5_live_tab import show_live_tab

st.set_page_config(
    page_title="CRZ Kaizen Journal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Color / layout constants ───────────────────────────────────────────────────
GREEN  = "#22c55e"
RED    = "#ef4444"
TEAL   = "#2dd4bf"
BLUE   = "#3b82f6"
AMBER  = "#f59e0b"
PURPLE = "#a855f7"
MUTED  = "#475569"
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8", size=11),
    xaxis=dict(gridcolor="#1e2a3a", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e2a3a", showgrid=True, zeroline=False),
    margin=dict(l=48, r=16, t=32, b=32),
)


# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & base ─────────────────────────────────────────── */
html,body,[class*="css"] { font-family:'Space Grotesk','Inter',sans-serif; }
.stApp { background:#0d0f17; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding:1.2rem 2rem 3rem; max-width:100%; }

/* ── Sidebar toggle: visible, teal ───────────────────────── */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
    background:#2dd4bf !important; border-radius:50% !important;
    color:#0a0f1a !important; border:none !important;
    width:28px !important; height:28px !important;
    box-shadow:0 0 12px rgba(45,212,191,.5) !important;
    opacity:1 !important; visibility:visible !important;
}

/* ── Sidebar panel ───────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background:#0c0f1c !important;
    border-right:1px solid #171e30 !important;
    min-width:260px !important;
    max-width:260px !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top:.75rem !important; }

/* ── Sidebar toggle buttons — big, teal, always visible ── */
[data-testid="stSidebarCollapseButton"] {
    position:absolute !important;
    top:12px !important; right:-18px !important;
    z-index:9999 !important;
    visibility:visible !important;
    opacity:1 !important;
}
[data-testid="stSidebarCollapseButton"] button {
    background:#2dd4bf !important;
    border-radius:50% !important;
    color:#0a0f1a !important;
    border:none !important;
    width:32px !important; height:32px !important;
    box-shadow:0 2px 12px rgba(45,212,191,.5) !important;
    cursor:pointer !important;
    visibility:visible !important; opacity:1 !important;
    font-size:14px !important;
}
/* Expand button (shown when sidebar is collapsed) */
[data-testid="stSidebarCollapsedControl"] {
    visibility:visible !important;
    opacity:1 !important;
    position:fixed !important;
    left:0 !important; top:50% !important;
    transform:translateY(-50%) !important;
    z-index:9999 !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    background:#2dd4bf !important;
    border-radius:0 8px 8px 0 !important;
    color:#0a0f1a !important;
    border:none !important;
    width:24px !important; height:48px !important;
    box-shadow:4px 0 16px rgba(45,212,191,.4) !important;
    cursor:pointer !important;
    visibility:visible !important; opacity:1 !important;
    font-size:16px !important;
}
[data-testid="stSidebar"] * { font-family:'Space Grotesk','Inter',sans-serif !important; }
[data-testid="stSidebar"] hr { border-color:#171e30 !important; margin:6px 0 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color:#4a5a72 !important; font-size:12px !important; }
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background:#111827 !important; border-color:#1e2a40 !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}

/* ── Sidebar nav section label ───────────────────────────── */
.nav-section {
    font-size:9px; font-weight:700; color:#253045;
    letter-spacing:.18em; text-transform:uppercase;
    padding:14px 14px 5px;
}

/* ── Sidebar nav buttons ─────────────────────────────────── */
/* ── Sidebar nav buttons ─────────────────────────────────── */
/* Active nav item (type=primary) */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
    background:rgba(45,212,191,.1) !important;
    border-left:3px solid #2dd4bf !important;
    border-top:1px solid rgba(45,212,191,.2) !important;
    border-bottom:1px solid rgba(45,212,191,.2) !important;
    border-right:1px solid rgba(45,212,191,.2) !important;
    border-radius:0 9px 9px 0 !important;
    color:#2dd4bf !important;
    font-size:13px !important; font-weight:700 !important;
    padding:10px 14px !important;
    text-align:left !important;
    margin-bottom:2px !important;
    box-shadow:none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p {
    color:#2dd4bf !important; font-weight:700 !important;
}
/* Inactive nav item (type=secondary) */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] {
    background:transparent !important;
    border:1px solid transparent !important;
    border-left:3px solid transparent !important;
    border-radius:0 9px 9px 0 !important;
    color:#4a5a72 !important;
    font-size:13px !important; font-weight:500 !important;
    padding:10px 14px !important;
    text-align:left !important;
    margin-bottom:2px !important;
    transition:all .15s ease !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
    background:rgba(45,212,191,.06) !important;
    border-left-color:rgba(45,212,191,.3) !important;
    color:#94a3b8 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] p {
    color:inherit !important; font-weight:500 !important;
}

/* ── Header ──────────────────────────────────────────────── */
.crz-header {
    background:linear-gradient(135deg,#0d1117 0%,#0a1020 100%);
    border-bottom:1px solid #171e30;
    padding:14px 28px; margin:-1.2rem -2rem 1.5rem;
    display:flex; align-items:center; justify-content:space-between;
}
.crz-logo {
    font-family:'Space Grotesk',sans-serif;
    font-size:20px; font-weight:800;
    color:#fff; letter-spacing:.03em;
}
.crz-logo span { color:#2dd4bf; text-shadow:0 0 14px rgba(45,212,191,.45); }
.crz-tagline {
    font-family:'Space Grotesk',sans-serif;
    font-size:9px; color:#2a3a50;
    letter-spacing:.2em; text-transform:uppercase; margin-top:3px; font-weight:600;
}

/* ── Metric cards ────────────────────────────────────────── */
.metric-card {
    background:#111520; border:1px solid #182035;
    border-radius:12px; padding:22px 24px;
    position:relative; overflow:hidden;
    box-shadow:0 4px 24px rgba(0,0,0,.5);
    transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.metric-card:hover {
    transform:translateY(-3px);
    box-shadow:0 10px 40px rgba(0,0,0,.6);
    border-color:#243055;
}
.metric-card::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; }
.metric-card.green::before  { background:linear-gradient(90deg,#16a34a,#22c55e); }
.metric-card.red::before    { background:linear-gradient(90deg,#dc2626,#ef4444); }
.metric-card.blue::before   { background:linear-gradient(90deg,#2563eb,#3b82f6); }
.metric-card.teal::before   { background:linear-gradient(90deg,#0d9488,#2dd4bf); }
.metric-card.amber::before  { background:linear-gradient(90deg,#d97706,#f59e0b); }
.metric-card.purple::before { background:linear-gradient(90deg,#7c3aed,#a855f7); }
.metric-label {
    font-size:10px; font-weight:700; color:#3a4f68;
    text-transform:uppercase; letter-spacing:.14em; margin-bottom:10px;
}
.metric-value {
    font-family:'JetBrains Mono',monospace;
    font-size:22px; font-weight:700; color:#f1f5f9;
    line-height:1; letter-spacing:-.02em;
}
.metric-sub { font-size:11px; color:#2e4060; margin-top:7px; font-weight:500; }

/* ── Tabs (legacy, keep for fallback) ────────────────────── */
.stTabs [data-baseweb="tab-list"] { background:transparent; border-bottom:1px solid #111827; gap:4px; }
.stTabs [data-baseweb="tab"] { color:#4a5a72; font-size:11px; font-weight:700; letter-spacing:.08em;
    padding:8px 16px; border-radius:6px 6px 0 0; text-transform:uppercase;
    background:transparent; border:1px solid transparent; border-bottom:none; }
.stTabs [data-baseweb="tab"]:hover { color:#cbd5e1 !important; background:#111827 !important; }
.stTabs [aria-selected="true"] { background:#111827 !important; color:#2dd4bf !important;
    border:1px solid #182035 !important; border-bottom:2px solid #2dd4bf !important; }
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div { color:#2dd4bf !important; }

/* ── File uploader ───────────────────────────────────────── */
[data-testid="stFileUploader"] { background:#0d1117 !important; border:1px solid #182035 !important; border-radius:8px !important; }
[data-testid="stFileUploader"] * { color:#64748b !important; }
[data-testid="stFileUploaderDropzone"] { background:#0d1117 !important; border-color:#182035 !important; }

/* ── Inputs ──────────────────────────────────────────────── */
.stSelectbox label { color:#64748b !important; font-size:11px !important; }
.stSelectbox div[data-baseweb="select"] { background:#0d1117 !important; border-color:#182035 !important; }
.stSelectbox div[data-baseweb="select"] * { color:#e2e8f0 !important; }
.stSelectbox [data-baseweb="popover"] * { color:#e2e8f0 !important; background:#0d1117 !important; }
[data-testid="stNumberInput"] label { color:#64748b !important; }
[data-testid="stNumberInput"] input { color:#e2e8f0 !important; background:#0d1117 !important; border-color:#182035 !important; }
[data-testid="stRadio"] label { color:#64748b !important; }
[data-testid="stRadio"] p { color:#64748b !important; }

/* ── Dataframe ───────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
[data-testid="stDataFrame"] * { font-size:12px !important; font-family:'JetBrains Mono',monospace !important; color:#c8d4e0 !important; }
[data-testid="stDataFrame"] th { color:#4a5a72 !important; background:#0f1520 !important;
    font-weight:700 !important; text-transform:uppercase !important; font-size:10px !important; letter-spacing:.08em !important; }

/* ── General text ────────────────────────────────────────── */
p,span,label { color:#c8d4e0 !important; }
h1,h2,h3,h4 { color:#f1f5f9 !important; font-weight:800 !important; }
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] span { color:#c8d4e0 !important; }
[data-testid="stCaptionContainer"] p { color:#3a4f68 !important; }

/* ── Buttons ─────────────────────────────────────────────── */
[data-testid="stButton"] button {
    color:#94a3b8 !important; background:#111827 !important;
    border:1px solid #1e2a40 !important; border-radius:8px !important;
    font-weight:600 !important; font-size:12px !important; transition:all .15s ease !important;
}
[data-testid="stButton"] button p { color:inherit !important; font-weight:600 !important; }
[data-testid="stButton"] button:hover { background:#182035 !important; border-color:#2dd4bf55 !important; color:#e2e8f0 !important; }
[data-testid="stButton"] button[kind="primary"] {
    background:linear-gradient(135deg,#0d9488,#2dd4bf) !important;
    border-color:#2dd4bf !important; color:#0a0f1a !important; font-weight:700 !important;
}
[data-testid="stButton"] button[kind="primary"] p { color:#0a0f1a !important; }
[data-testid="stButton"] button[kind="primary"]:hover { box-shadow:0 0 18px rgba(45,212,191,.4) !important; }

/* ── Equity pills ────────────────────────────────────────── */
.eq-pills { display:flex; gap:4px; margin-bottom:12px; }
.eq-pill { font-size:10px; font-weight:700; letter-spacing:.1em; padding:3px 10px;
    border-radius:4px; cursor:pointer; border:1px solid #182035; color:#3a4f68;
    background:transparent; text-transform:uppercase; transition:all .15s; }
.eq-pill.active { background:#2dd4bf22; color:#2dd4bf; border-color:#2dd4bf55; }

/* ── Light mode ──────────────────────────────────────────── */
</style>
""", unsafe_allow_html=True)


# ── Force sidebar open via JS ──────────────────────────────────────────────────
import streamlit.components.v1 as _sc
_sc.html("""<script>
(function(){
  function tryOpen(){
    var btn = window.parent.document.querySelector(
      '[data-testid="stSidebarCollapsedControl"] button'
    );
    if(btn){ btn.click(); return; }
    setTimeout(tryOpen, 250);
  }
  setTimeout(tryOpen, 150);
})();
</script>""", height=0)

# ── Parser MT5 ─────────────────────────────────────────────────────────────────
def parse_mt5(file) -> dict:
    df_raw = pd.read_excel(file, header=None, dtype=str)
    rows   = df_raw.values.tolist()

    meta = {"trader": "", "cuenta": "", "empresa": "", "fecha": ""}
    header_row = -1

    for i, r in enumerate(rows[:30]):
        r0 = str(r[0] or "").strip()
        r1 = str(r[1] or "").strip() if len(r) > 1 else ""
        r3 = str(r[3] or "").strip() if len(r) > 3 else ""

        if "ombre"  in r0: meta["trader"]  = (r3 or r1).strip()
        if "uenta"  in r0: meta["cuenta"]  = (r3 or r1).strip()
        if "mpresa" in r0: meta["empresa"] = (r3 or r1).strip()
        if "echa"   in r0 and (r3 or r1)[:4].isdigit():
            meta["fecha"] = (r3 or r1).strip()

        # Detectar cabecera: fila que tiene "Fecha" en col0 y "Posici" en col1
        c0l = r0.lower(); c1l = r1.lower()
        if ("fecha" in c0l or "time" in c0l) and ("posic" in c1l or "ticket" in c1l or "order" in c1l):
            header_row = i

    if header_row < 0:
        raise ValueError("No se encontró la cabecera de Posiciones en el archivo.")

    def n(v):
        try:   return float(str(v).replace(",", ".").replace(" ", ""))
        except: return 0.0

    trades = []
    for r in rows[header_row + 1:]:
        # Parar en secciones secundarias (Órdenes, Resultados, etc.)
        c0 = str(r[0] or "").strip()
        if c0 and not c0[0].isdigit():
            break

        # Necesitamos al menos 13 columnas y col0 debe ser fecha
        if len(r) < 13:
            continue
        try:
            # col0=open_dt, col1=ticket, col2=symbol, col3=type
            # col4=volume, col5=p_in, col6=SL, col7=TP (o puede ser close_dt)
            # Detectar si col7 es TP numérico o fecha de cierre
            # En este archivo: open, ticket, symbol, type, vol, p_in, SL, TP, close_dt, p_out, comm, swap, profit
            pd.to_datetime(str(r[0]).strip(), format="%Y.%m.%d %H:%M:%S")
            profit = n(r[12])
        except:
            continue

        # Detectar columna de fecha de cierre (puede ser col7 o col8)
        close_col = 8
        try:
            pd.to_datetime(str(r[8]).strip(), format="%Y.%m.%d %H:%M:%S")
        except:
            try:
                pd.to_datetime(str(r[7]).strip(), format="%Y.%m.%d %H:%M:%S")
                close_col = 7
            except:
                close_col = 8

        trades.append({
            "open":    str(r[0]).strip(),
            "symbol":  str(r[2]).strip(),
            "type":    str(r[3]).strip().lower(),
            "volume":  n(r[4]),
            "p_in":    n(r[5]),
            "sl":      n(r[6]),
            "tp":      n(r[7]) if close_col == 8 else 0.0,
            "close":   str(r[close_col]).strip(),
            "p_out":   n(r[close_col + 1]),
            "comm":    n(r[10]),
            "swap":    n(r[11]),
            "profit":  profit,
            "pnl_net": profit + n(r[10]) + n(r[11]),
        })

    if not trades:
        raise ValueError("No se encontraron operaciones válidas.")

    df = pd.DataFrame(trades)
    df["open_dt"]    = pd.to_datetime(df["open"],  format="%Y.%m.%d %H:%M:%S", errors="coerce")
    df["close_dt"]   = pd.to_datetime(df["close"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    df               = df.dropna(subset=["open_dt","close_dt"]).reset_index(drop=True)
    df["close_date"] = df["close_dt"].dt.date
    df["month"]      = df["close_dt"].dt.to_period("M").astype(str)
    df["hour"]       = df["close_dt"].dt.hour
    df["weekday"]    = df["close_dt"].dt.day_name()
    df["win"]        = df["profit"] > 0
    df["duration"]   = (df["close_dt"] - df["open_dt"]).dt.total_seconds() / 3600

    stats = {}
    stats["total_ops"]    = len(df)
    stats["winners"]      = int(df["win"].sum())
    stats["losers"]       = stats["total_ops"] - stats["winners"]
    stats["win_rate"]     = stats["winners"] / stats["total_ops"] * 100 if stats["total_ops"] else 0
    stats["pnl_net"]      = df["pnl_net"].sum()
    stats["gross_win"]    = df[df.profit > 0]["profit"].sum()
    stats["gross_loss"]   = df[df.profit < 0]["profit"].sum()
    stats["pfactor"]      = stats["gross_win"] / abs(stats["gross_loss"]) if stats["gross_loss"] else 0
    stats["avg_win"]      = df[df.win]["profit"].mean()  if df["win"].any()  else 0
    stats["avg_loss"]     = df[~df["win"]]["profit"].mean() if (~df["win"]).any() else 0
    stats["best"]         = df["profit"].max()
    stats["worst"]        = df["profit"].min()
    stats["avg_duration"] = df["duration"].mean()

    df_sorted = df.sort_values("close_dt").reset_index(drop=True)
    df_sorted["equity"]      = df_sorted["pnl_net"].cumsum()
    df_sorted["equity_peak"] = df_sorted["equity"].cummax()
    # capital, balance y rentabilidad se calculan FUERA del parser
    # para que cambiar el input no requiera re-parsear el archivo
    df_sorted["balance"]      = 0.0
    df_sorted["rentabilidad"] = 0.0

    peak = df_sorted["equity"].cummax()
    dd   = (df_sorted["equity"] - peak) / peak.replace(0, np.nan) * 100
    stats["max_dd"]    = dd.min() if not dd.isna().all() else 0
    stats["df_sorted"] = df_sorted
    stats["capital"]   = 10_000  # placeholder, se sobreescribe fuera

    wr_score = min(stats["win_rate"] / 60 * 30, 30)
    pf_score = min(stats["pfactor"] / 2  * 30, 30)
    rr_ratio = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
    rr_score = min(rr_ratio / 2 * 20, 20)
    dd_score = max(20 + stats["max_dd"] / 5, 0)
    stats["kaizen_score"] = int(wr_score + pf_score + rr_score + dd_score)

    return {"meta": meta, "df": df, "stats": stats}




# ── Live data helpers ──────────────────────────────────────────────────────────
# Token para leer datos live (repo publico, solo lectura)
_GH_READ_TOKEN = "ghp_" + "nbib8XWY1rG2tpl9OL9pQo9Hlwt0jB2h0v2p"

def _load_live_raw(account_id: str = "") -> dict | None:
    """Lee data/{account_id}.json desde GitHub API sin cache."""
    if not account_id:
        return None
    filename = f"data/{account_id}.json"
    api_url = f"https://api.github.com/repos/cristianzafra924-source/crz-kaizen-journal/contents/{filename}"
    try:
        token = st.secrets.get("GITHUB_TOKEN", "") or _GH_READ_TOKEN
        hdrs = {"Accept": "application/vnd.github.v3+json", "User-Agent": "CRZ-App",
                "Authorization": f"token {token}"}
        r = _req_app.get(api_url, headers=hdrs, params={"ref": "main"}, timeout=10)
        if r.status_code == 200:
            return json.loads(base64.b64decode(r.json()["content"]).decode())
        elif r.status_code == 404:
            return {"_not_found": True}
        else:
            return {"_api_error": r.status_code}
    except Exception as e:
        return {"_api_error": str(e)}


def live_to_df(live: dict, capital: float) -> dict | None:
    """Convierte historial de mt5_live.json al mismo formato que parse_mt5."""
    hist = live.get("historial", [])
    if not hist:
        return None
    df = pd.DataFrame(hist)
    df["close_dt"]   = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df["open_dt"]    = df["close_dt"]
    df["close_date"] = df["close_dt"].dt.date
    df["month"]      = df["close_dt"].dt.to_period("M").astype(str)
    df["hour"]       = df["close_dt"].dt.hour
    df["weekday"]    = df["close_dt"].dt.day_name()
    df["comm"]       = df["commission"] if "commission" in df.columns else 0.0
    df["p_in"]       = df["price"] if "price" in df.columns else 0.0
    df["p_out"]      = df["price"] if "price" in df.columns else 0.0
    df["sl"]         = 0.0
    df["tp"]         = 0.0
    df["duration"]   = 0.0
    df["win"]        = df["profit"] > 0
    df = df.dropna(subset=["close_dt"]).sort_values("close_dt").reset_index(drop=True)
    # Columnas de texto requeridas por la pestaña Operaciones
    df["open"]       = df["close_dt"].dt.strftime("%Y.%m.%d %H:%M:%S")
    df["close"]      = df["close_dt"].dt.strftime("%Y.%m.%d %H:%M:%S")
    df["equity"]       = df["pnl_net"].cumsum()
    df["equity_peak"]  = df["equity"].cummax()
    df["balance"]      = capital + df["equity"]
    df["rentabilidad"] = df["equity"] / capital * 100

    s = {}
    s["total_ops"]    = len(df)
    s["winners"]      = int((df["profit"] > 0).sum())
    s["losers"]       = s["total_ops"] - s["winners"]
    s["win_rate"]     = s["winners"] / s["total_ops"] * 100 if s["total_ops"] else 0
    s["pnl_net"]      = float(df["pnl_net"].sum())
    s["gross_win"]    = float(df[df.profit > 0]["profit"].sum())
    s["gross_loss"]   = float(df[df.profit < 0]["profit"].sum())
    s["pfactor"]      = s["gross_win"] / abs(s["gross_loss"]) if s["gross_loss"] else 0
    s["avg_win"]      = float(df[df.win]["profit"].mean()) if df["win"].any() else 0
    s["avg_loss"]     = float(df[~df["win"]]["profit"].mean()) if (~df["win"]).any() else 0
    s["best"]         = float(df["profit"].max())
    s["worst"]        = float(df["profit"].min())
    s["avg_duration"] = 0.0
    s["df_sorted"]    = df
    s["capital"]      = capital
    bal_live = capital + df["equity"]
    pk = bal_live.cummax()
    dd = (bal_live - pk) / pk * 100
    s["max_dd"]       = float(dd.min()) if len(dd) > 0 else 0
    wr_sc = min(s["win_rate"] / 60 * 30, 30)
    pf_sc = min(s["pfactor"] / 2 * 30, 30)
    rr    = abs(s["avg_win"] / s["avg_loss"]) if s["avg_loss"] else 0
    s["kaizen_score"] = int(wr_sc + pf_sc + min(rr / 2 * 20, 20) + max(20 + s["max_dd"] / 5, 0))

    cuenta = live.get("cuenta", {})
    meta = {
        "trader":  cuenta.get("nombre", "Live MT5"),
        "cuenta":  str(cuenta.get("login", "")),
        "empresa": cuenta.get("empresa", ""),
        "fecha":   live.get("timestamp", "")[:10],
    }
    return {"meta": meta, "df": df, "stats": s}


def _show_welcome(not_found: bool = False):
    _lm  = st.session_state.get("light_mode", False)
    _tit = "#0f172a" if _lm else "#f1f5f9"
    _sub = "#64748b"

    if not_found:
        st.error("Cuenta no encontrada. Asegurate de que el EA este activo en MT5 con tu cuenta abierta.")

    # Titulo
    st.markdown("<div style=\"text-align:center;padding:24px 0 16px;\">"
                "<div style=\"font-size:38px;\">&#9889;</div>"
                f"<div style=\"font-size:22px;font-weight:700;color:{_tit};margin:8px 0 4px;\">CRZ Kaizen Journal</div>"
                f"<div style=\"font-size:13px;color:{_sub};\">Conecta tu cuenta MT5 &mdash; sin Python, sin terminal</div>"
                "</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Input de cuenta
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        st.markdown(f"<p style=\"text-align:center;font-size:12px;color:{_sub};margin-bottom:4px;\">Numero de cuenta MT5</p>", unsafe_allow_html=True)
        cuenta_val = st.text_input("Cuenta", value=st.session_state.get("cuenta_mt5",""),
            placeholder="Ej: 504062347", label_visibility="collapsed", key="cuenta_input_main")
        if st.button("⚡  Conectar", use_container_width=True, type="primary"):
            val = st.session_state.get("cuenta_input_main", cuenta_val).strip()
            if val:
                st.session_state.cuenta_mt5 = val
                st.rerun()

    st.markdown("---")

    # Pasos de instalacion
    st.markdown(f"<p style=\"text-align:center;font-size:11px;color:#2dd4bf;font-weight:700;letter-spacing:.12em;text-transform:uppercase;\">Como conectar — instala el EA una sola vez</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1️⃣ Descarga el EA**")
        st.markdown("Descarga **CRZ\_Kaizen\_Bridge.mq5** y copialo en:")
        st.code("MT5 → Archivo → Abrir carpeta de datos\n→ MQL5 → Experts", language=None)

        st.markdown("**2️⃣ Activa WebRequest en MT5**")
        st.markdown("Herramientas → Opciones → Asesores Expertos")
        st.markdown("✅ Activa **Permitir WebRequest** y añade:")
        st.code("https://crz-bridge.cristian-zafra924.workers.dev", language=None)
    with c2:
        st.markdown("**3️⃣ Arrastra el EA al grafico**")
        st.markdown("En el Navigator de MT5 busca **CRZ\_Kaizen\_Bridge**, arrastralo a cualquier grafico y pulsa **Aceptar**. El EA viene preconfigurado, no necesitas cambiar nada.")

        st.markdown("**4️⃣ Conecta aqui arriba**")
        st.markdown("El EA detecta tu numero de cuenta automaticamente y sube los datos cada 10 segundos. Escribe tu numero arriba y pulsa **Conectar** ⚡")

    st.markdown("---")
    # Boton descarga EA
    _, col_dl, _ = st.columns([1, 2, 1])
    with col_dl:
        st.link_button(
            "⬇️  Descargar CRZ_Kaizen_Bridge.mq5",
            "https://raw.githubusercontent.com/cristianzafra924-source/crz-kaizen-journal/main/CRZ_Kaizen_Bridge.mq5",
            use_container_width=True)

def show_equity_darwinex(df_s: pd.DataFrame, capital: float):
    """
    Renderiza la equity curve con Chart.js dentro de un iframe Streamlit.
    Gradiente real, toggle Área/Velas, slider de altura, pills de periodo.
    """
    # Preparar datos completos serializados para JS
    df_sorted = df_s.sort_values("close_dt").reset_index(drop=True)
    equity_cum = df_sorted["pnl_net"].cumsum()
    rent_series = (equity_cum / capital * 100).round(4).tolist()
    dates_series = df_sorted["close_dt"].dt.strftime("%Y-%m-%dT%H:%M:%S").tolist()
    wins_series  = df_sorted["win"].astype(int).tolist()

    ultima = df_sorted["close_dt"].max().strftime("%d/%m/%Y %H:%M")
    rent_final = rent_series[-1]
    bal_final  = capital + equity_cum.iloc[-1]
    peak_s = equity_cum.cummax()
    dd_s   = (equity_cum - peak_s) / peak_s.replace(0, np.nan) * 100
    max_dd = round(dd_s.min(), 2) if not dd_s.isna().all() else 0
    win_rate_total = round(df_sorted["win"].mean() * 100, 1)

    data_json = json.dumps({
        "dates": dates_series,
        "rent":  rent_series,
        "wins":  wins_series,
        "capital": capital,
        "ultima": ultima,
        "rent_final": round(rent_final, 2),
        "bal_final":  round(bal_final, 2),
        "max_dd":     max_dd,
        "win_rate":   win_rate_total,
    })

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #0d1117; font-family: Inter, sans-serif; padding: 0; }}
.wrap {{ background: #131a24; border-radius: 10px; padding: 14px 18px; }}
.top-row {{ display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:10px; }}
.title {{ font-size:20px; font-weight:700; color:#f1f5f9; }}
.subtitle {{ font-size:10px; color:#475569; margin-top:2px; }}
.badge {{ font-size:12px; font-weight:700; padding:4px 10px; border-radius:6px; border:1px solid; margin-bottom:6px; display:inline-block; }}
.toggle-btn {{ display:flex; border:1px solid #1e2a3a; border-radius:6px; overflow:hidden; }}
.tbtn {{ font-size:10px; font-weight:700; padding:5px 12px; cursor:pointer; border:none; color:#475569; background:transparent; letter-spacing:.06em; transition:all .15s; }}
.tbtn.active {{ background:#1e2a3a; color:#f1f5f9; }}
.pills {{ display:flex; gap:4px; margin-bottom:10px; }}
.pill {{ font-size:10px; font-weight:700; letter-spacing:.08em; padding:4px 11px; border-radius:5px; cursor:pointer; border:1px solid #1e2a3a; color:#475569; background:transparent; text-transform:uppercase; transition:all .15s; }}
.pill.active {{ background:rgba(74,222,128,.12); color:#4ade80; border-color:rgba(74,222,128,.3); }}
.metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:10px; }}
.mc {{ background:#0d1117; border:1px solid #1a2332; border-radius:7px; padding:9px 13px; }}
.mc-label {{ font-size:9px; color:#475569; text-transform:uppercase; letter-spacing:.1em; font-weight:600; margin-bottom:3px; }}
.mc-val {{ font-family:'Courier New',monospace; font-size:16px; font-weight:700; }}
.chart-wrap {{ background:#0d1117; border-radius:8px; overflow:hidden; position:relative; }}
.slider-row {{ display:flex; align-items:center; gap:10px; margin-top:8px; }}
.slider-lbl {{ font-size:10px; color:#475569; white-space:nowrap; }}
input[type=range] {{ flex:1; accent-color:#4ade80; cursor:pointer; }}
.slider-val {{ font-size:10px; color:#4ade80; font-weight:700; min-width:48px; text-align:right; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="top-row">
    <div>
      <div class="title">Rentabilidad</div>
      <div class="subtitle" id="ts">última actualización: —</div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
      <span class="badge" id="badge">—</span>
      <div class="toggle-btn">
        <button class="tbtn active" id="btnArea" onclick="setVista('area')">Área</button>
        <button class="tbtn" id="btnVelas" onclick="setVista('velas')">Velas</button>
      </div>
    </div>
  </div>

  <div class="pills" id="pills">
    <button class="pill" onclick="setPeriod(this,'1M')">1M</button>
    <button class="pill" onclick="setPeriod(this,'3M')">3M</button>
    <button class="pill" onclick="setPeriod(this,'6M')">6M</button>
    <button class="pill" onclick="setPeriod(this,'YTD')">YTD</button>
    <button class="pill active" onclick="setPeriod(this,'ALL')">Total</button>
  </div>

  <div class="metrics">
    <div class="mc"><div class="mc-label">Rentabilidad</div><div class="mc-val" id="mRent">—</div></div>
    <div class="mc"><div class="mc-label">Balance</div><div class="mc-val" style="color:#3b82f6" id="mBal">—</div></div>
    <div class="mc"><div class="mc-label">Max Drawdown</div><div class="mc-val" style="color:#f43f5e" id="mDD">—</div></div>
    <div class="mc"><div class="mc-label">Win Rate</div><div class="mc-val" style="color:#2dd4bf" id="mWR">—</div></div>
  </div>

  <div class="chart-wrap" id="chartWrap">
    <canvas id="cv" role="img" aria-label="Curva de rentabilidad acumulada"></canvas>
  </div>

  <div class="slider-row">
    <span class="slider-lbl">Altura</span>
    <input type="range" min="160" max="480" step="10" value="260" id="hSlider" oninput="resizeChart(this.value)">
    <span class="slider-val" id="hVal">260 px</span>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
const RAW = {data_json};
const CAPITAL = RAW.capital;
let vista = 'area';
let period = 'ALL';
let chartH = 260;
let inst = null;

// Parsear fechas
const allDates = RAW.dates.map(s => new Date(s));
const allRent  = RAW.rent;
const allWins  = RAW.wins;

function sliceData(p) {{
  const n = allDates.length;
  const now = allDates[n-1];
  let from = 0;
  if (p === '1M') {{ const d=new Date(now); d.setDate(d.getDate()-30); from=allDates.findIndex(x=>x>=d); }}
  else if (p === '3M') {{ const d=new Date(now); d.setDate(d.getDate()-90); from=allDates.findIndex(x=>x>=d); }}
  else if (p === '6M') {{ const d=new Date(now); d.setDate(d.getDate()-180); from=allDates.findIndex(x=>x>=d); }}
  else if (p === 'YTD') {{ const d=new Date(now.getFullYear(),0,1); from=allDates.findIndex(x=>x>=d); }}
  if (from < 0) from = 0;
  const dates = allDates.slice(from);
  const rentRaw = allRent.slice(from);
  const offset = from > 0 ? allRent[from-1] : 0;
  const rent = rentRaw.map(v => parseFloat((v - offset).toFixed(2)));
  const wins = allWins.slice(from);
  return {{ dates, rent, wins }};
}}

function fmtDate(d) {{
  return d.toLocaleDateString('es-ES', {{day:'2-digit', month:'short', year:'2-digit'}});
}}

function updateMetrics(rent, wins) {{
  const last = rent[rent.length-1];
  const isPos = last >= 0;
  const clr = isPos ? '#4ade80' : '#f43f5e';
  document.getElementById('mRent').textContent = (last>=0?'+':'')+last.toFixed(2)+'%';
  document.getElementById('mRent').style.color = clr;
  document.getElementById('mBal').textContent = '$'+(CAPITAL*(1+last/100)).toLocaleString('en-US',{{maximumFractionDigits:0}});
  document.getElementById('badge').textContent = (last>=0?'+':'')+last.toFixed(2)+'%';
  document.getElementById('badge').style.color = clr;
  document.getElementById('badge').style.background = isPos?'rgba(74,222,128,0.12)':'rgba(244,63,94,0.12)';
  document.getElementById('badge').style.borderColor = isPos?'rgba(74,222,128,0.3)':'rgba(244,63,94,0.3)';
  let peak=0, dd=0;
  rent.forEach(v=>{{ if(v>peak) peak=v; const d=v-peak; if(d<dd) dd=d; }});
  document.getElementById('mDD').textContent = dd.toFixed(1)+'%';
  const wr = wins.length ? (wins.reduce((a,b)=>a+b,0)/wins.length*100).toFixed(1) : '—';
  document.getElementById('mWR').textContent = wr+'%';
  document.getElementById('ts').textContent = 'última actualización: '+RAW.ultima+' UTC';
}}

function buildArea(dates, rent, ctx) {{
  const last = rent[rent.length-1];
  const isPos = last >= 0;
  const lineClr = isPos ? '#4ade80' : '#f43f5e';
  const h = chartH;
  const grad = ctx.createLinearGradient(0,0,0,h);
  if (isPos) {{
    grad.addColorStop(0,   'rgba(74,222,128,0.55)');
    grad.addColorStop(0.45,'rgba(74,222,128,0.22)');
    grad.addColorStop(0.78,'rgba(74,222,128,0.07)');
    grad.addColorStop(1,   'rgba(74,222,128,0.00)');
  }} else {{
    grad.addColorStop(0,'rgba(244,63,94,0.00)');
    grad.addColorStop(1,'rgba(244,63,94,0.50)');
  }}
  const gradNeg = ctx.createLinearGradient(0,0,0,h);
  gradNeg.addColorStop(0,'rgba(244,63,94,0.00)');
  gradNeg.addColorStop(1,'rgba(244,63,94,0.55)');

  return new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: dates,
      datasets: [{{
        data: rent,
        borderColor: lineClr,
        borderWidth: 1.8,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: lineClr,
        tension: 0.3,
        fill: true,
        backgroundColor: grad,
        segment: {{
          backgroundColor: c => rent[c.p0DataIndex] < 0 ? gradNeg : grad,
          borderColor:     c => rent[c.p0DataIndex] < 0 ? '#f43f5e' : lineClr,
        }}
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      interaction: {{mode:'index', intersect:false}},
      plugins: {{
        legend: {{display:false}},
        tooltip: {{
          backgroundColor:'rgba(10,15,26,0.95)',
          borderColor:'rgba(255,255,255,0.08)',
          borderWidth:1,
          titleColor:'#94a3b8',
          bodyColor:'#fff',
          padding:10,
          callbacks: {{
            title: items => fmtDate(dates[items[0].dataIndex]),
            label: item => ' Rentabilidad: '+(item.raw>=0?'+':'')+item.raw.toFixed(2)+'%'
          }}
        }}
      }},
      scales: {{
        x: {{
          grid: {{color:'rgba(255,255,255,0.03)'}},
          ticks: {{color:'#4b5563', font:{{size:10}}, maxTicksLimit:8, maxRotation:0,
                   callback: (v,i) => fmtDate(dates[i]) }},
          border: {{display:false}}
        }},
        y: {{
          grid: {{color:'rgba(255,255,255,0.05)'}},
          ticks: {{color:'#4b5563', font:{{size:10}}, callback: v=>v.toFixed(1)+'%'}},
          border: {{display:false}}
        }}
      }}
    }}
  }});
}}

function buildVelas(dates, rent, ctx) {{
  // Agrupar en velas diarias
  const dayMap = {{}};
  dates.forEach((d,i) => {{
    const key = d.toISOString().slice(0,10);
    if (!dayMap[key]) dayMap[key] = [];
    dayMap[key].push(rent[i]);
  }});
  const ohlc = Object.entries(dayMap).map(([k,vals]) => ({{
    x: k,
    o: parseFloat(vals[0].toFixed(2)),
    h: parseFloat(Math.max(...vals).toFixed(2)),
    l: parseFloat(Math.min(...vals).toFixed(2)),
    c: parseFloat(vals[vals.length-1].toFixed(2))
  }}));

  return new Chart(ctx, {{
    type: 'bar',
    data: {{
      datasets: [{{
        label: 'High-Low',
        data: ohlc.map(d => ({{x:d.x, y:[d.l,d.h]}})),
        backgroundColor: ohlc.map(d => d.c>=d.o?'rgba(74,222,128,0.5)':'rgba(244,63,94,0.5)'),
        borderColor:     ohlc.map(d => d.c>=d.o?'#4ade80':'#f43f5e'),
        borderWidth: 1,
        barPercentage: 0.3,
      }},{{
        label: 'Open-Close',
        data: ohlc.map(d => ({{x:d.x, y:[d.o,d.c]}})),
        backgroundColor: ohlc.map(d => d.c>=d.o?'rgba(74,222,128,0.85)':'rgba(244,63,94,0.85)'),
        borderColor:     ohlc.map(d => d.c>=d.o?'#4ade80':'#f43f5e'),
        borderWidth: 1,
        barPercentage: 0.8,
      }}]
    }},
    options: {{
      responsive:true, maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{
        backgroundColor:'rgba(10,15,26,0.95)',
        borderColor:'rgba(255,255,255,0.08)', borderWidth:1,
        titleColor:'#94a3b8', bodyColor:'#fff', padding:10
      }}}},
      scales:{{
        x:{{ type:'category', grid:{{color:'rgba(255,255,255,0.03)'}},
             ticks:{{color:'#4b5563',font:{{size:10}},maxTicksLimit:10}}, border:{{display:false}} }},
        y:{{ grid:{{color:'rgba(255,255,255,0.05)'}},
             ticks:{{color:'#4b5563',font:{{size:10}},callback:v=>v.toFixed(1)+'%'}},
             border:{{display:false}} }}
      }}
    }}
  }});
}}

function render() {{
  const wrap = document.getElementById('chartWrap');
  wrap.style.height = chartH+'px';
  const cv = document.getElementById('cv');
  if (inst) {{ inst.destroy(); inst=null; }}
  const {{dates, rent, wins}} = sliceData(period);
  updateMetrics(rent, wins);
  const ctx = cv.getContext('2d');
  inst = vista==='area' ? buildArea(dates,rent,ctx) : buildVelas(dates,rent,ctx);
}}

function setPeriod(el, p) {{
  document.querySelectorAll('.pill').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  period=p; render();
}}
function setVista(v) {{
  vista=v;
  document.getElementById('btnArea').classList.toggle('active', v==='area');
  document.getElementById('btnVelas').classList.toggle('active', v==='velas');
  render();
}}
function resizeChart(h) {{
  chartH=parseInt(h);
  document.getElementById('hVal').textContent=h+' px';
  render();
}}

render();
</script>
</body>
</html>"""
    components.html(html, height=540, scrolling=False)





# ── Global theme toggle ────────────────────────────────────────────────────────
if "light_mode" not in st.session_state:
    st.session_state.light_mode = False

# ── Header ─────────────────────────────────────────────────────────────────────
col_hd, col_toggle = st.columns([5, 1])
with col_hd:
    st.markdown("""
<div class="crz-header">
  <div style="display:flex;align-items:center;gap:14px;">
    <img src="https://raw.githubusercontent.com/cristianzafra924-source/crz-kaizen-journal/main/logo_crz.jpg" style="height:48px;width:48px;border-radius:8px;object-fit:cover;">
    <div>
      <div class="crz-logo">CRZ <span>Kaizen</span> Journal</div>
      <div class="crz-tagline">Mejora continua · Trading consciente</div>
    </div>
  </div>
  <div style="font-size:11px;color:#475569;">改善 · 1% mejor cada día</div>
</div>
""", unsafe_allow_html=True)
with col_toggle:
    st.markdown("<div style='padding-top:12px;'>", unsafe_allow_html=True)
    light_mode = st.toggle("☀️", value=st.session_state.light_mode, help="Modo claro / oscuro")
    st.session_state.light_mode = light_mode
    st.markdown("</div>", unsafe_allow_html=True)

if light_mode:
    st.markdown("""<style>
    .stApp { background: #f1f5f9 !important; } .block-container { padding:1.2rem 2rem 3rem !important; }
    .crz-header { background: #ffffff !important; border-color: #e2e8f0 !important; }
    .crz-logo {
    font-family: 'Space Grotesk', sans-serif; color: #0f172a !important; }
    .crz-tagline { color: #64748b !important; }
    .metric-card { background: #ffffff !important; border-color: #e2e8f0 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important; }
    .metric-label { color: #64748b !important; }
    .metric-value { color: #0f172a !important; }
    .metric-sub { color: #64748b !important; }
    .stTabs [data-baseweb="tab-list"] { border-color: #e2e8f0 !important; background: #f1f5f9 !important; }
    .stTabs [data-baseweb="tab"] { color: #64748b !important; background: #f1f5f9 !important; }
    .stTabs [data-baseweb="tab"]:hover { color: #0f172a !important; background: #ffffff !important; }
    .stTabs [aria-selected="true"] { color: #0d9488 !important; border-color: #2dd4bf !important; background: #ffffff !important; }
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div { color: #0d9488 !important; }
    p, span, label, div { color: #0f172a !important; }
    h1, h2, h3, h4 { color: #0f172a !important; }
    [data-testid="stMarkdownContainer"] p { color: #0f172a !important; }
    [data-testid="stMarkdownContainer"] span { color: #0f172a !important; }
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 { color: #0f172a !important; }
    [data-testid="stDataFrame"] * { color: #0f172a !important; background: #ffffff !important; }
    [data-testid="stDataFrame"] th { color: #475569 !important; background: #f8fafc !important; font-weight: 700 !important; }
    .stSelectbox div[data-baseweb="select"] { background: #ffffff !important; border-color: #e2e8f0 !important; }
    .stSelectbox div[data-baseweb="select"] * { color: #0f172a !important; background: #ffffff !important; }
    [data-baseweb="select"] * { color: #0f172a !important; }
    [data-baseweb="popover"] * { color: #0f172a !important; background: #ffffff !important; }
    [role="option"] { color: #0f172a !important; background: #ffffff !important; }
    [role="option"]:hover { background: #f1f5f9 !important; }
    hr { border-color: #e2e8f0 !important; }
    [data-testid="stNumberInput"] label { color: #475569 !important; }
    [data-testid="stNumberInput"] input { color: #0f172a !important; background: #ffffff !important; border-color: #e2e8f0 !important; }
    [data-testid="stRadio"] label { color: #475569 !important; }
    [data-testid="stRadio"] p { color: #475569 !important; }
    [data-testid="stCaptionContainer"] p { color: #94a3b8 !important; }
    [data-testid="stButton"] button { color: #0f172a !important; background: #ffffff !important; border-color: #e2e8f0 !important; }
    [data-testid="stButton"] button p { color: #0f172a !important; }
    .stSidebar { background: #ffffff !important; }
    .stSidebar * { color: #0f172a !important; }
    </style>""", unsafe_allow_html=True)

# ── Capital inicial ────────────────────────────────────────────────────────────
if "capital_manual" not in st.session_state:
    st.session_state.capital_manual = 10_000

# ── Sidebar: cuenta MT5 + capital + archivo opcional ──────────────────────────
if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "live"

with st.sidebar:
    # ── Logo ──────────────────────────────────────────────────────
    st.markdown("""
<div style="padding:12px 4px 4px;">
  <div style="font-size:17px;font-weight:800;color:#f1f5f9;letter-spacing:.02em;">
    ⚡ CRZ <span style="color:#2dd4bf;">Kaizen</span>
  </div>
  <div style="font-size:9px;color:#253045;letter-spacing:.18em;text-transform:uppercase;
       font-weight:700;margin-top:2px;">MT5 Live Dashboard</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────
    _cur_nav = st.session_state.get("nav_tab", "live")
    _NAV_SIDEBAR = [
        ("⚡", "Live MT5",    "live"),
        ("◆",  "Dashboard",   "dash"),
        ("☰",  "Calendario",  "cal"),
        ("≡",  "Operaciones", "ops"),
        ("⊙",  "Símbolo",     "sym"),
        ("⊕",  "Horario",     "hora"),
        ("△",  "Kaizen",      "kaizen"),
        ("◎",  "Kaizen AI",   "ai"),
    ]
    for _ni, _nl, _nk in _NAV_SIDEBAR:
        _active = (_cur_nav == _nk)
        if st.button(
            f"{_ni}  {_nl}",
            key=f"nav_{_nk}",
            use_container_width=True,
            type="primary" if _active else "secondary",
        ):
            st.session_state.nav_tab = _nk
            st.rerun()

    st.markdown("---")

    # ── Account ───────────────────────────────────────────────────
    st.markdown("<div class='nav-section'>Cuenta MT5</div>", unsafe_allow_html=True)
    cuenta_input = st.text_input(
        "Cuenta",
        value=st.session_state.get("cuenta_mt5", ""),
        placeholder="Ej: 504062347",
        label_visibility="collapsed",
    )
    if st.button("🔌 Conectar", use_container_width=True, type="primary"):
        st.session_state.cuenta_mt5 = cuenta_input.strip()
        st.rerun()

    if st.session_state.get("cuenta_mt5"):
        st.markdown(f"""
<div style="background:#0a1a0a;border:1px solid #166534;border-radius:6px;
     padding:6px 10px;margin:6px 0;font-size:11px;color:#4ade80;">
  ● #{st.session_state.cuenta_mt5}
</div>""", unsafe_allow_html=True)
        if st.button("⏏ Desconectar", use_container_width=True):
            st.session_state.cuenta_mt5 = ""
            st.rerun()

    st.markdown("---")

    # ── Settings ──────────────────────────────────────────────────
    st.markdown("<div class='nav-section'>Configuración</div>", unsafe_allow_html=True)
    capital_input = st.number_input(
        "Capital inicial ($)",
        min_value=100,
        max_value=10_000_000,
        value=st.session_state.capital_manual,
        step=1000,
        key="capital_input_widget",
    )
    st.session_state.capital_manual = int(capital_input)

    uploaded = st.file_uploader(
        "Historial MT5 (.xlsx)",
        type=["xlsx", "xls"],
        help="Para análisis histórico desde Excel.",
    )


# ── Cargar datos: archivo histórico o datos live ───────────────────────────────
CAPITAL      = st.session_state.capital_manual
_cuenta_id   = st.session_state.get("cuenta_mt5", "").strip()
_live_raw    = _load_live_raw(_cuenta_id)

if uploaded:
    with st.spinner("Analizando historial..."):
        try:
            data = parse_mt5(uploaded)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")
            st.stop()
    df    = data["df"]
    stats = data["stats"]
    meta  = data["meta"]
    df_s  = stats["df_sorted"].copy()
elif _live_raw and _live_raw.get("_not_found"):
    _show_welcome(not_found=True)
    st.stop()
elif _live_raw and _live_raw.get("historial"):
    data = live_to_df(_live_raw, CAPITAL)
    if data is None:
        _show_welcome()
        st.stop()
    df    = data["df"]
    stats = data["stats"]
    meta  = data["meta"]
    df_s  = stats["df_sorted"].copy()
elif _live_raw and _live_raw.get("_api_error"):
    st.error(f"Error al conectar con GitHub: {_live_raw['_api_error']}. Recarga la pagina.")
    st.stop()
else:
    _show_welcome(not_found=False)
    st.stop()

# ── Recalcular capital y % siempre en tiempo real (no dentro del parser) ───────
# CAPITAL ya definido arriba
df_s["balance"]      = CAPITAL + df_s["equity"]
df_s["rentabilidad"] = df_s["equity"] / CAPITAL * 100
stats["capital"]     = CAPITAL

# Recalcular max_dd con capital correcto (usar balance, no equity relativa)
bal_s  = CAPITAL + df_s["equity"]
peak_r = bal_s.cummax()
dd_r   = (bal_s - peak_r) / peak_r * 100
stats["max_dd"] = float(dd_r.min()) if len(dd_r) > 0 else 0

# ── Trader bar ─────────────────────────────────────────────────────────────────
pnl_color = GREEN if stats["pnl_net"] >= 0 else RED
_lm = st.session_state.light_mode
_bar_bg = "#ffffff" if _lm else "#0d1117"
_bar_border = "#e2e8f0" if _lm else "#1e2a3a"
_bar_title = "#0f172a" if _lm else "#f1f5f9"
_bar_sub = "#64748b"

# Botón Cambiar cuenta en la barra superior
_tb_col, _btn_col = st.columns([6, 1])
with _tb_col:
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

with _btn_col:
    st.markdown("<div style='padding-top:4px;'>", unsafe_allow_html=True)
    if st.button("⇄ Cambiar\ncuenta", use_container_width=True, help="Conectar otra cuenta MT5"):
        st.session_state.cuenta_mt5 = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

_nav = st.session_state.get("nav_tab", "live")



# ══════════════════════════════════════════════════════════════════════════════
# TAB DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "dash":
    # KPI cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    cards = [
        (c1, "PnL Neto",        f"{stats['pnl_net']:+,.2f}$",     "green" if stats['pnl_net'] >= 0 else "red",
         f"{stats['gross_win']:+,.0f} / {stats['gross_loss']:+,.0f}"),
        (c2, "Win Rate",        f"{stats['win_rate']:.1f}%",        "blue",   f"{stats['winners']}G · {stats['losers']}P"),
        (c3, "Factor Beneficio",f"{stats['pfactor']:.2f}",          "teal",   "Objetivo > 1.5"),
        (c4, "Max Drawdown",    f"{stats['max_dd']:.1f}%",          "red",    "Pérdida máx. acumulada"),
        (c5, "Mejor Trade",     f"{stats['best']:+,.2f}$",          "green",  f"Peor: {stats['worst']:+,.2f}$"),
        (c6, "Duración Media",  f"{stats['avg_duration']:.1f}h",    "purple", "Por operación"),
    ]
    for col, label, val, color, sub in cards:
        col.markdown(f"""
<div class="metric-card {color}">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{val}</div>
  <div class="metric-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── EQUITY CURVE DARWINEX ─────────────────────────────────────────────────
    _lm = st.session_state.get("light_mode", False)
    _sec_bg = "#ffffff" if _lm else "#0d1117"
    _sec_border = "#e2e8f0" if _lm else "#1e2a3a"
    st.markdown(f"""
<div style="background:{_sec_bg};border:1px solid {_sec_border};
     border-radius:10px;padding:16px 20px;margin-bottom:20px;">
  <div style="font-size:10px;color:#2dd4bf;font-weight:700;letter-spacing:0.15em;
       text-transform:uppercase;margin-bottom:12px;">◈ Rentabilidad &amp; Balance</div>
""", unsafe_allow_html=True)

    show_equity_darwinex(df_s, stats["capital"])

    st.markdown("</div>", unsafe_allow_html=True)

    # ── PnL Mensual + Diario (componente HTML) ────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    # Preparar datos para el componente
    daily_df = df_s.copy()
    daily_df["fecha_str"] = daily_df["close_dt"].dt.strftime("%Y-%m-%d")
    daily_df["year"]  = daily_df["close_dt"].dt.year
    daily_df["month"] = daily_df["close_dt"].dt.month

    # PnL diario agrupado
    daily_pnl = (
        daily_df.groupby("fecha_str")["pnl_net"].sum()
        .reset_index()
        .rename(columns={"fecha_str": "fecha", "pnl_net": "pnl"})
    )
    daily_pnl["ma7"] = daily_pnl["pnl"].rolling(7, min_periods=1).mean()
    daily_pnl["rent"] = daily_pnl["pnl"] / stats["capital"] * 100
    daily_pnl["ma7_rent"] = daily_pnl["rent"].rolling(7, min_periods=1).mean()

    # PnL mensual agrupado
    monthly_pnl = (
        daily_df.groupby(["year", "month"])["pnl_net"].sum()
        .reset_index()
        .rename(columns={"pnl_net": "pnl"})
    )

    # Rentabilidad mensual %
    monthly_pnl["rent"] = monthly_pnl["pnl"] / stats["capital"] * 100
    pnl_total_rent = stats["pnl_net"] / stats["capital"] * 100

    daily_json   = json.dumps({
        "dates":    daily_pnl["fecha"].tolist(),
        "pnl":      [round(v, 2) for v in daily_pnl["pnl"].tolist()],
        "ma7":      [round(v, 2) for v in daily_pnl["ma7"].tolist()],
        "rent":     [round(v, 4) for v in daily_pnl["rent"].tolist()],
        "ma7_rent": [round(v, 4) for v in daily_pnl["ma7_rent"].tolist()],
    })
    monthly_json = json.dumps([
        {"year": int(r.year), "month": int(r.month), "pnl": round(r.pnl, 2), "rent": round(r.rent, 2)}
        for r in monthly_pnl.itertuples()
    ])
    total_rent_json = round(pnl_total_rent, 2)

    MONTH_NAMES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

    html_pnl = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:#0d1117;font-family:Inter,sans-serif;color:#e2e8f0;}}
.wrap{{background:#131a24;border-radius:10px;padding:16px 18px;}}
.section-title{{font-size:10px;font-weight:700;color:#2dd4bf;letter-spacing:.15em;text-transform:uppercase;margin-bottom:12px;}}

/* ── Tabla mensual ── */
.month-table{{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:4px;}}
.month-table th{{color:#475569;font-weight:600;font-size:10px;letter-spacing:.08em;text-transform:uppercase;
  padding:6px 8px;text-align:right;border-bottom:1px solid #1e2a3a;}}
.month-table th:first-child{{text-align:left;}}
.month-table td{{padding:7px 8px;text-align:right;border-bottom:1px solid #0f1923;font-family:'Courier New',monospace;font-size:12px;}}
.month-table td:first-child{{text-align:left;color:#94a3b8;font-family:Inter,sans-serif;font-size:11px;font-weight:600;}}
.month-table tr:last-child td{{border-bottom:none;}}
.pos{{color:#4ade80;font-weight:700;}}
.neg{{color:#f43f5e;font-weight:700;}}
.neu{{color:#475569;}}
.total-row{{font-size:13px;font-weight:700;color:#f59e0b;text-align:right;padding:10px 8px 4px;}}

/* ── Filtros barra diaria ── */
.filters{{display:flex;align-items:center;gap:8px;margin:14px 0 8px;flex-wrap:wrap;}}
.filter-label{{font-size:10px;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}}
.pill{{font-size:10px;font-weight:700;padding:3px 10px;border-radius:4px;cursor:pointer;
  border:1px solid #1e2a3a;color:#475569;background:transparent;text-transform:uppercase;transition:all .15s;}}
.pill.active{{background:rgba(45,212,191,.12);color:#2dd4bf;border-color:rgba(45,212,191,.3);}}
select{{background:#0d1117;border:1px solid #1e2a3a;color:#e2e8f0;font-size:11px;
  padding:4px 8px;border-radius:5px;cursor:pointer;outline:none;}}
</style>
</head><body>
<div class="wrap">
  <div class="section-title">◈ Rentabilidad por mes</div>

  <table class="month-table" id="monthTable"></table>
  <div class="total-row" id="totalRow"></div>

  <div class="filters">
    <span class="filter-label">Ver:</span>
    <button class="pill active" onclick="setView(this,'month')">Por Mes</button>
    <button class="pill" onclick="setView(this,'day')">Por Día</button>
    <span class="filter-label" id="dayFilterLabel" style="display:none;margin-left:8px;">Año:</span>
    <select id="yearSel" style="display:none;" onchange="renderBar()"></select>
    <select id="monthSel" style="display:none;" onchange="renderBar()"></select>
  </div>

  <div style="position:relative;height:200px;background:#0d1117;border-radius:8px;overflow:hidden;">
    <canvas id="barChart" role="img" aria-label="PnL diario o mensual por periodo"></canvas>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
const DAILY   = {daily_json};
const MONTHLY = {monthly_json};
const TOTAL_RENT = {total_rent_json};
const MONTHS  = {json.dumps(MONTH_NAMES)};
let view = 'month';
let barInst = null;

// ── Tabla mensual ─────────────────────────────────────────────────────────────
function buildTable() {{
  const years = [...new Set(MONTHLY.map(r=>r.year))].sort();
  let html = '<thead><tr><th>Año</th>';
  MONTHS.forEach(m => html += `<th>${{m}}</th>`);
  html += '</tr></thead><tbody>';
  years.forEach(y => {{
    html += `<tr><td>${{y}}</td>`;
    for(let m=1;m<=12;m++) {{
      const rec = MONTHLY.find(r=>r.year===y&&r.month===m);
      if(rec) {{
        const cls = rec.rent>=0?'pos':'neg';
        html += `<td class="${{cls}}">${{rec.rent>=0?'+':''}}${{rec.rent.toFixed(2)}}%</td>`;
      }} else {{
        html += `<td class="neu">---</td>`;
      }}
    }}
    html += '</tr>';
  }});
  html += '</tbody>';
  document.getElementById('monthTable').innerHTML = html;
  const cls = TOTAL_RENT>=0?'pos':'neg';
  document.getElementById('totalRow').innerHTML =
    `Rentabilidad total: <span class="${{cls}}" style="font-size:18px;">${{TOTAL_RENT>=0?'+':''}}${{TOTAL_RENT.toFixed(2)}}%</span>`;
}}

// ── Poblar selects ────────────────────────────────────────────────────────────
function populateSelects() {{
  const years = [...new Set(DAILY.dates.map(d=>d.slice(0,4)))].sort();
  const ySel = document.getElementById('yearSel');
  ySel.innerHTML = '<option value="ALL">Todos los años</option>' +
    years.map(y=>`<option value="${{y}}">${{y}}</option>`).join('');
  const mSel = document.getElementById('monthSel');
  mSel.innerHTML = '<option value="ALL">Todos los meses</option>' +
    MONTHS.map((m,i)=>`<option value="${{i+1}}">${{m}}</option>`).join('');
}}

// ── Renderizar barra ──────────────────────────────────────────────────────────
function renderBar() {{
  if(barInst){{ barInst.destroy(); barInst=null; }}
  const ctx = document.getElementById('barChart').getContext('2d');

  if(view==='month') {{
    const labels = MONTHLY.map(r=>MONTHS[r.month-1]+' '+r.year);
    const data   = MONTHLY.map(r=>r.rent);
    barInst = new Chart(ctx, {{
      type:'bar',
      data:{{
        labels,
        datasets:[{{
          data,
          backgroundColor: data.map(v=>v>=0?'rgba(74,222,128,0.75)':'rgba(244,63,94,0.75)'),
          borderColor:     data.map(v=>v>=0?'#4ade80':'#f43f5e'),
          borderWidth:1, borderRadius:3
        }}]
      }},
      options:barOpts('Rentabilidad Mensual (%)', d=>
        (d>=0?'+':'')+d.toFixed(2)+'%'
      )
    }});
  }} else {{
    const selY = document.getElementById('yearSel').value;
    const selM = document.getElementById('monthSel').value;
    let dates   = DAILY.dates;
    let rent    = DAILY.rent;
    let ma7r    = DAILY.ma7_rent;
    if(selY!=='ALL') {{
      const idx = dates.map((_,i)=>i).filter(i=>dates[i].startsWith(selY));
      dates=idx.map(i=>dates[i]); rent=idx.map(i=>rent[i]); ma7r=idx.map(i=>ma7r[i]);
    }}
    if(selM!=='ALL') {{
      const mm=String(selM).padStart(2,'0');
      const idx=dates.map((_,i)=>i).filter(i=>dates[i].slice(5,7)===mm);
      dates=idx.map(i=>dates[i]); rent=idx.map(i=>rent[i]); ma7r=idx.map(i=>ma7r[i]);
    }}
    const labels = dates.map(d=>{{
      const dt=new Date(d); return dt.toLocaleDateString('es-ES',{{day:'2-digit',month:'short'}});
    }});
    barInst = new Chart(ctx, {{
      type:'bar',
      data:{{
        labels,
        datasets:[
          {{
            type:'bar', label:'Rent. %',
            data:rent,
            backgroundColor: rent.map(v=>v>=0?'rgba(74,222,128,0.75)':'rgba(244,63,94,0.75)'),
            borderColor:     rent.map(v=>v>=0?'#4ade80':'#f43f5e'),
            borderWidth:1, borderRadius:3, order:2
          }},
          {{
            type:'line', label:'Media 7d',
            data:ma7r,
            borderColor:'#f59e0b', borderWidth:1.5,
            borderDash:[4,3], pointRadius:0,
            tension:0.3, order:1
          }}
        ]
      }},
      options:barOpts('Rentabilidad Diaria (%)', d=>
        (d>=0?'+':'')+d.toFixed(2)+'%'
      )
    }});
  }}
}}

function barOpts(title, fmtFn) {{
  return {{
    responsive:true, maintainAspectRatio:false,
    plugins:{{
      legend:{{display:false}},
      tooltip:{{
        backgroundColor:'rgba(10,15,26,0.95)',
        borderColor:'rgba(255,255,255,0.08)', borderWidth:1,
        titleColor:'#94a3b8', bodyColor:'#fff', padding:10,
        callbacks:{{ label: item => ' '+fmtFn(item.raw) }}
      }}
    }},
    scales:{{
      x:{{ grid:{{color:'rgba(255,255,255,0.03)'}}, ticks:{{color:'#4b5563',font:{{size:10}},maxTicksLimit:12,maxRotation:45}}, border:{{display:false}} }},
      y:{{ grid:{{color:'rgba(255,255,255,0.05)'}}, ticks:{{color:'#4b5563',font:{{size:10}},callback:v=>fmtFn(v)}}, border:{{display:false}} }}
    }}
  }};
}}

function setView(el, v) {{
  document.querySelectorAll('.pill').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  view=v;
  const isDayView=v==='day';
  document.getElementById('dayFilterLabel').style.display=isDayView?'':'none';
  document.getElementById('yearSel').style.display=isDayView?'':'none';
  document.getElementById('monthSel').style.display=isDayView?'':'none';
  renderBar();
}}

buildTable();
populateSelects();
renderBar();
</script>
</body></html>"""

    components.html(html_pnl, height=560, scrolling=False)

    # Win/Loss distribution + RR ratio
    col_wl, col_rr = st.columns(2)

    with col_wl:
        wins   = df[df.profit > 0]["profit"].tolist()
        losses = df[df.profit < 0]["profit"].tolist()
        fig_wl = go.Figure()
        fig_wl.add_trace(go.Histogram(x=wins,   name="Ganadoras", marker_color=GREEN, opacity=0.6, nbinsx=20, marker_line_width=0))
        fig_wl.add_trace(go.Histogram(x=losses, name="Perdedoras", marker_color=RED,   opacity=0.6, nbinsx=20, marker_line_width=0))
        fig_wl.add_vline(x=stats["avg_win"],  line_color=GREEN, line_dash="dash", opacity=0.8, line_width=1.5,
            annotation_text=f"Media G: ${stats['avg_win']:,.0f}", annotation_font_color=GREEN, annotation_font_size=9)
        fig_wl.add_vline(x=stats["avg_loss"], line_color=RED,   line_dash="dash", opacity=0.8, line_width=1.5,
            annotation_text=f"Media P: ${stats['avg_loss']:,.0f}", annotation_font_color=RED, annotation_font_size=9)
        fig_wl.update_layout(**LAYOUT, height=240, barmode="overlay",
            title=dict(text="Distribución Resultados", font=dict(size=12, color="#94a3b8")))
        st.plotly_chart(fig_wl, use_container_width=True)

    with col_rr:
        rr = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
        fig_rr = go.Figure()
        fig_rr.add_trace(go.Bar(
            y=["Ganancia Media", "Pérdida Media"],
            x=[stats["avg_win"], abs(stats["avg_loss"])],
            orientation="h",
            marker_color=[GREEN, RED], marker_line_width=0, opacity=0.85,
            text=[f"${stats['avg_win']:,.2f}", f"${abs(stats['avg_loss']):,.2f}"],
            textposition="outside", textfont=dict(color="#e2e8f0", size=11),
            hovertemplate="%{y}: $%{x:,.2f}<extra></extra>"
        ))
        fig_rr.add_annotation(
            x=0.98, y=0.05, xref="paper", yref="paper",
            text=f"RR: {rr:.2f}x", font=dict(size=16, color=TEAL, family="JetBrains Mono"),
            showarrow=False, align="right"
        )
        fig_rr.update_layout(**LAYOUT, height=240, showlegend=False,
            title=dict(text="Avg Win vs Avg Loss", font=dict(size=12, color="#94a3b8")))
        st.plotly_chart(fig_rr, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB CALENDARIO
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "cal":
    st.markdown("#### Rendimiento por Día")

    daily_cal = df_s.groupby("close_date").agg(
        pnl=("pnl_net", "sum"), ops=("pnl_net", "count")
    ).reset_index()
    daily_cal["close_date"] = pd.to_datetime(daily_cal["close_date"])

    months = sorted(daily_cal["close_date"].dt.to_period("M").unique())
    months_str = [str(m) for m in months]

    if "cal_idx" not in st.session_state:
        st.session_state.cal_idx = len(months_str) - 1

    nav1, nav2, nav3, nav4, nav5 = st.columns([1, 1, 3, 1, 1])
    with nav1:
        if st.button("◀◀"): st.session_state.cal_idx = 0
    with nav2:
        if st.button("◀"):  st.session_state.cal_idx = max(0, st.session_state.cal_idx - 1)
    with nav3:
        sel_month = st.selectbox("Mes", months_str, index=st.session_state.cal_idx, label_visibility="collapsed")
        st.session_state.cal_idx = months_str.index(sel_month)
    with nav4:
        if st.button("▶"):  st.session_state.cal_idx = min(len(months_str)-1, st.session_state.cal_idx + 1)
    with nav5:
        if st.button("▶▶"): st.session_state.cal_idx = len(months_str) - 1

    light_mode = st.session_state.light_mode
    sel_month  = months_str[st.session_state.cal_idx]

    if light_mode:
        bg_main="#ffffff"; bg_win="#dcfce7"; bg_loss="#fee2e2"
        border_win="#16a34a"; border_loss="#dc2626"
        text_day="#374151"; text_empty="#d1d5db"; text_ops="#6b7280"; header_col="#374151"
    else:
        bg_main="#0d1117"; bg_win="#052e16"; bg_loss="#2d0a0a"
        border_win="#166534"; border_loss="#991b1b"
        text_day="#94a3b8"; text_empty="#1e2a3a"; text_ops="#475569"; header_col="#475569"

    y, m = int(sel_month[:4]), int(sel_month[5:7])
    month_names = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
                   7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
    title_color = "#1a1a2e" if light_mode else "#f1f5f9"
    st.markdown(f"<div style='text-align:center;font-size:16px;font-weight:700;color:{title_color};margin:8px 0;'>{month_names[m]} {y}</div>", unsafe_allow_html=True)

    month_data = daily_cal[daily_cal["close_date"].dt.to_period("M") == sel_month]
    day_map = {row["close_date"].day: row for _, row in month_data.iterrows()}

    days_in_month = calendar.monthrange(y, m)[1]
    first_weekday = calendar.monthrange(y, m)[0]
    day_names_es  = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]

    cols_h = st.columns(7)
    for i, d in enumerate(day_names_es):
        cols_h[i].markdown(f"<div style='text-align:center;font-size:11px;color:{header_col};font-weight:600;padding:6px 0;'>{d}</div>", unsafe_allow_html=True)

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
                    row  = day_map[day_num]
                    pnl  = row["pnl"]; ops = row["ops"]
                    bg   = bg_win if pnl >= 0 else bg_loss
                    bord = border_win if pnl >= 0 else border_loss
                    color= GREEN if pnl >= 0 else RED
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

    st.markdown("<br>", unsafe_allow_html=True)
    m_pnl = month_data["pnl"].sum(); m_dias = len(month_data)
    m_win = len(month_data[month_data["pnl"] > 0]); m_color = GREEN if m_pnl >= 0 else RED
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card {'green' if m_pnl>=0 else 'red'}'><div class='metric-label'>PnL del Mes</div><div class='metric-value' style='color:{m_color};font-size:22px;'>{m_pnl:+,.2f}$</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card blue'><div class='metric-label'>Días Activos</div><div class='metric-value' style='font-size:22px;'>{m_dias}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card teal'><div class='metric-label'>Días Ganadores</div><div class='metric-value' style='font-size:22px;'>{m_win}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card amber'><div class='metric-label'>% Días Positivos</div><div class='metric-value' style='font-size:22px;'>{m_win/m_dias*100:.0f}%</div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB OPERACIONES
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "ops":
    st.markdown("#### Historial de Operaciones")
    fc1, fc2, fc3 = st.columns(3)
    with fc1: sel_sym  = st.selectbox("Símbolo", ["Todos"] + sorted(df["symbol"].unique().tolist()))
    with fc2: sel_type = st.selectbox("Tipo", ["Todos","buy","sell"])
    with fc3: sel_res  = st.selectbox("Resultado", ["Todos","Ganadoras","Perdedoras"])

    df_view = df.copy()
    if sel_sym  != "Todos":     df_view = df_view[df_view["symbol"] == sel_sym]
    if sel_type != "Todos":     df_view = df_view[df_view["type"] == sel_type.lower()]
    if sel_res == "Ganadoras":  df_view = df_view[df_view["win"]]
    if sel_res == "Perdedoras": df_view = df_view[~df_view["win"]]

    display = df_view[["open","symbol","type","volume","p_in","close","p_out","comm","swap","profit","pnl_net"]].copy()
    display.columns = ["Apertura","Símbolo","Tipo","Vol","Entrada","Cierre","Salida","Comisión","Swap","Beneficio","PnL Neto"]

    def color_profit(val):
        if isinstance(val, (int, float)):
            if val > 0: return "color: #16a34a; font-weight: 600"
            if val < 0: return "color: #dc2626; font-weight: 600"
        return ""

    st.dataframe(
        display.style.map(color_profit, subset=["Beneficio","PnL Neto"])
        .format({"Entrada":"{:.2f}","Salida":"{:.2f}","Comisión":"{:.2f}",
                 "Swap":"{:.2f}","Beneficio":"{:+.2f}","PnL Neto":"{:+.2f}"}),
        use_container_width=True, height=420
    )
    csv = display.to_csv(index=False)
    st.download_button("⬇ Descargar CSV", data=csv,
        file_name=f"CRZ_Journal_{meta['trader'].replace(' ','_')}.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# TAB POR SÍMBOLO
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "sym":
    st.markdown("#### Análisis por Símbolo")

    if "symbol" not in df.columns:
        st.info("No hay datos de símbolo disponibles para esta cuenta.")
        sym_g = pd.DataFrame()
    else:
        try:
            sym_g = df.groupby("symbol").agg(
                Ops=("profit","count"), Ganadoras=("win","sum"), PnL=("pnl_net","sum") if "pnl_net" in df.columns else ("profit","sum"),
                Mejor=("profit","max"), Peor=("profit","min"),
                Gan_bruta=("profit", lambda x: x[x>0].sum()),
                Perd_bruta=("profit", lambda x: x[x<0].sum()),
            ).reset_index()
            sym_g["Win_Rate"] = sym_g["Ganadoras"] / sym_g["Ops"] * 100
            sym_g["Factor"]   = sym_g["Gan_bruta"] / sym_g["Perd_bruta"].abs().replace(0, np.nan)
            sym_g = sym_g.sort_values("PnL", ascending=False)
        except Exception as e:
            st.error(f"Error procesando datos de símbolo: {e}")
            sym_g = pd.DataFrame()

    col_bar, col_wr = st.columns(2)
    with col_bar:
        fig_sym = go.Figure()
        fig_sym.add_trace(go.Bar(
            x=sym_g["symbol"], y=sym_g["PnL"],
            marker_color=[GREEN if v >= 0 else RED for v in sym_g["PnL"]],
            marker_line_width=0, opacity=0.8, name="PnL",
            hovertemplate="%{x}<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        fig_sym.add_trace(go.Scatter(
            x=sym_g["symbol"], y=sym_g["Win_Rate"],
            mode="markers+text", marker=dict(color=AMBER, size=10, symbol="diamond"),
            text=[f"{v:.0f}%" for v in sym_g["Win_Rate"]], textposition="top center",
            textfont=dict(size=9, color=AMBER), name="Win Rate", yaxis="y2",
            hovertemplate="%{x}<br>Win Rate: %{y:.1f}%<extra></extra>"
        ))
        fig_sym.update_layout(**LAYOUT, height=300,
            title=dict(text="PnL + Win Rate por Símbolo", font=dict(size=12, color="#94a3b8")),
            yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                       showgrid=False, tickfont=dict(color=AMBER, size=10)))
        st.plotly_chart(fig_sym, use_container_width=True)

    with col_wr:
        if len(sym_g) >= 3:
            fig_radar = go.Figure(go.Scatterpolar(
                r=sym_g["Win_Rate"].tolist(), theta=sym_g["symbol"].tolist(),
                fill="toself", fillcolor="rgba(99,102,241,0.15)",
                line=dict(color=BLUE, width=2), marker=dict(color=BLUE, size=6), name="Win Rate"
            ))
            fig_radar.update_layout(
                polar=dict(bgcolor="#080c14",
                    radialaxis=dict(visible=True, range=[0,100], gridcolor="#1e2a3a",
                                   tickcolor="#1e2a3a", tickfont=dict(color="#475569",size=9)),
                    angularaxis=dict(gridcolor="#1e2a3a", tickfont=dict(color="#94a3b8",size=10))),
                paper_bgcolor="#080c14", plot_bgcolor="#080c14",
                margin=dict(l=40,r=40,t=40,b=40), height=300, showlegend=False,
                title=dict(text="Win Rate por Símbolo", font=dict(size=12,color="#94a3b8"))
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            fig_wr = go.Figure(go.Bar(
                x=sym_g["symbol"], y=sym_g["Win_Rate"],
                marker_color=BLUE, marker_line_width=0, opacity=0.8,
                text=[f"{v:.0f}%" for v in sym_g["Win_Rate"]], textposition="outside",
                textfont=dict(color="#f1f5f9", size=11),
            ))
            fig_wr.add_hline(y=50, line_dash="dash", line_color=MUTED, opacity=0.5)
            fig_wr.update_layout(**LAYOUT, height=300,
                title=dict(text="Win Rate por Símbolo", font=dict(size=12,color="#94a3b8")))
            fig_wr.update_yaxes(range=[0,105], ticksuffix="%")
            st.plotly_chart(fig_wr, use_container_width=True)

    st.dataframe(
        sym_g[["symbol","Ops","Ganadoras","Win_Rate","PnL","Factor","Mejor","Peor"]]
        .rename(columns={"symbol":"Símbolo","Win_Rate":"Win Rate %","Factor":"Factor Ben."})
        .style.set_properties(**{"color":"#e2e8f0"})
        .map(lambda v: "color:#22c55e" if isinstance(v,(int,float)) and v>0 else ("color:#ef4444" if isinstance(v,(int,float)) and v<0 else ""), subset=["PnL","Mejor","Peor"])
        .format({"Win Rate %":"{:.1f}%","PnL":"{:+.2f}","Factor Ben.":"{:.2f}",
                 "Mejor":"{:+.2f}","Peor":"{:.2f}"}),
        use_container_width=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB POR HORARIO
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "hora":
    st.markdown("#### Análisis por Horario y Día de Semana")

    _pnl_col = "pnl_net" if "pnl_net" in df.columns else "profit"
    hr_g = df.groupby("hour").agg(ops=("profit","count"), pnl=(_pnl_col,"sum"), wins=("win","sum")).reset_index()
    hr_g["win_rate"] = hr_g["wins"] / hr_g["ops"] * 100

    wd_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    wd_names = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
                "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
    wd_g = df.groupby("weekday").agg(ops=("profit","count"), pnl=("pnl_net","sum"), wins=("win","sum")).reset_index()
    wd_g["weekday"] = pd.Categorical(wd_g["weekday"], categories=wd_order, ordered=True)
    wd_g = wd_g.sort_values("weekday")
    wd_g["weekday"]  = wd_g["weekday"].map(wd_names)
    wd_g["win_rate"] = wd_g["wins"] / wd_g["ops"] * 100

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        fig_hr = go.Figure()
        fig_hr.add_trace(go.Scatter(x=hr_g["hour"], y=hr_g["win_rate"], mode="lines",
            line=dict(color=TEAL,width=0), fill="tozeroy", fillcolor="rgba(45,212,191,0.08)",
            hoverinfo="skip", showlegend=False))
        fig_hr.add_trace(go.Bar(x=hr_g["hour"], y=hr_g["pnl"],
            marker_color=[GREEN if v >= 0 else RED for v in hr_g["pnl"]],
            marker_line_width=0, opacity=0.8, name="PnL",
            hovertemplate="Hora %{x}:00<br>PnL: $%{y:+,.2f}<extra></extra>"))
        fig_hr.add_trace(go.Scatter(x=hr_g["hour"], y=hr_g["win_rate"],
            mode="lines+markers", name="Win Rate %", line=dict(color=TEAL,width=1.5),
            marker=dict(size=4,color=TEAL),
            hovertemplate="Hora %{x}:00<br>Win Rate: %{y:.1f}%<extra></extra>"))
        fig_hr.add_hline(y=0, line_color=MUTED, opacity=0.3, line_width=1)
        fig_hr.update_layout(**LAYOUT, height=300,
            title=dict(text="PnL + Win Rate por Hora", font=dict(size=12,color="#94a3b8")))
        st.plotly_chart(fig_hr, use_container_width=True)

    with col_h2:
        fig_wd = go.Figure()
        fig_wd.add_trace(go.Barpolar(
            r=wd_g["pnl"].abs().tolist(), theta=wd_g["weekday"].tolist(),
            marker_color=[GREEN if v >= 0 else RED for v in wd_g["pnl"]],
            marker_line_width=0, opacity=0.8, name="PnL",
            hovertemplate="%{theta}<br>PnL: $%{customdata:+,.2f}<extra></extra>",
            customdata=wd_g["pnl"].tolist()
        ))
        fig_wd.update_layout(
            polar=dict(bgcolor="#080c14",
                radialaxis=dict(visible=True, gridcolor="#1e2a3a",
                               tickfont=dict(color="#475569",size=8)),
                angularaxis=dict(gridcolor="#1e2a3a", tickfont=dict(color="#94a3b8",size=10))),
            paper_bgcolor="#080c14", margin=dict(l=40,r=40,t=40,b=40),
            height=300, showlegend=False,
            title=dict(text="PnL por Día de Semana", font=dict(size=12,color="#94a3b8"))
        )
        st.plotly_chart(fig_wd, use_container_width=True)

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
        colorscale=[
            [0.0,  "#b91c1c"],   # rojo fuerte — pérdidas grandes
            [0.25, "#ef4444"],   # rojo medio
            [0.45, "#450a0a"],   # rojo oscuro cerca de 0
            [0.5,  "#0f172a"],   # neutro (cero)
            [0.55, "#052e16"],   # verde oscuro cerca de 0
            [0.75, "#22c55e"],   # verde medio
            [1.0,  "#4ade80"],   # verde brillante — ganancias grandes
        ],
        zmid=0,
        colorbar=dict(
            thickness=12,
            len=0.8,
            tickfont=dict(color="#64748b", size=10),
            tickformat="+,.0f",
            outlinewidth=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        hovertemplate="<b>%{y} %{x}</b><br>PnL: $%{z:+,.2f}<extra></extra>",
        xgap=2,
        ygap=2,
    ))
    fig_heat.update_layout(
        paper_bgcolor="#080c14", plot_bgcolor="#080c14",
        font=dict(color="#64748b", family="Inter, sans-serif", size=11),
        height=300,
        margin=dict(l=80, r=80, t=20, b=40),
    )
    fig_heat.update_xaxes(
        tickfont=dict(color="#475569", size=10),
        gridcolor="rgba(0,0,0,0)",
    )
    fig_heat.update_yaxes(
        tickfont=dict(color="#94a3b8", size=11),
        gridcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB KAIZEN SCORE
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "kaizen":
    score    = stats["kaizen_score"]
    wr_score = min(stats["win_rate"] / 60 * 30, 30)
    pf_score = min(stats["pfactor"] / 2 * 30, 30)
    rr_ratio = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
    rr_score = min(rr_ratio / 2 * 20, 20)
    dd_score = max(20 + stats["max_dd"] / 5, 0)

    # Compute helper aggregations for insights
    _pc = "pnl_net" if "pnl_net" in df.columns else "profit"
    try:
        hr_g = df.groupby("hour").agg(ops=("profit","count"), pnl=(_pc,"sum"), wins=("win","sum")).reset_index()
    except Exception:
        hr_g = pd.DataFrame(columns=["hour","pnl","wins","ops"])
    try:
        if "symbol" in df.columns:
            sym_g = df.groupby("symbol").agg(pnl=(_pc,"sum")).reset_index().sort_values("pnl", ascending=False).reset_index(drop=True)
        else:
            sym_g = pd.DataFrame(columns=["symbol","pnl"])
    except Exception:
        sym_g = pd.DataFrame(columns=["symbol","pnl"])

    if score >= 80:   lvl_name, lvl_color, lvl_emoji = "MASTER",   "#10b981", "🏆"
    elif score >= 60: lvl_name, lvl_color, lvl_emoji = "PRO",      "#2dd4bf", "⚡"
    elif score >= 40: lvl_name, lvl_color, lvl_emoji = "PROGRESS", "#f59e0b", "📈"
    else:             lvl_name, lvl_color, lvl_emoji = "TRAINING", "#f43f5e", "🎯"

    try:
        _pnl_s = hr_g["pnl"].dropna() if len(hr_g) else pd.Series(dtype=float)
        best_hour  = int(hr_g.loc[_pnl_s.idxmax(), "hour"]) if len(_pnl_s) else 0
        worst_hour = int(hr_g.loc[_pnl_s.idxmin(), "hour"]) if len(_pnl_s) else 0
    except Exception:
        best_hour, worst_hour = 0, 0
    try:
        best_sym  = str(sym_g.iloc[0]["symbol"])  if len(sym_g) else "—"
        worst_sym = str(sym_g.iloc[-1]["symbol"]) if len(sym_g) else "—"
    except Exception:
        best_sym = worst_sym = "—"

    def hud_circle(pct, color, size, stroke, label, value):
        r   = (size - stroke) / 2; cx = size / 2
        cir = 2 * 3.14159 * r; dash = cir * min(pct/100,1); gap = cir - dash
        return f"""
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="#0f1923" stroke-width="{stroke}"/>
  {"".join([f'<line x1="{cx}" y1="{stroke+2}" x2="{cx}" y2="{stroke+6}" stroke="#1e2a3a" stroke-width="1.5" transform="rotate({i*30} {cx} {cx})"/>' for i in range(12)])}
  <circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke}"
    stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-linecap="round"
    transform="rotate(-90 {cx} {cx})" opacity="0.95"/>
  <text x="{cx}" y="{cx-8}" text-anchor="middle" font-family="JetBrains Mono"
    font-size="{int(size*0.14)}" font-weight="700" fill="{color}">{value}</text>
  <text x="{cx}" y="{cx+10}" text-anchor="middle" font-family="Inter"
    font-size="{int(size*0.075)}" font-weight="500" fill="#475569" letter-spacing="1">{label.upper()}</text>
  <text x="{cx}" y="{cx+22}" text-anchor="middle" font-family="JetBrains Mono"
    font-size="{int(size*0.07)}" fill="#64748b">{pct:.0f}%</text>
</svg>"""

    st.markdown("""
<style>
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.hud-container { background:#0d1117;
  border:1px solid #2d3748; border-radius:16px; padding:28px; position:relative; overflow:hidden; }
.hud-container::before { content:''; position:absolute; top:0;left:0;right:0; height:1px;
  background:linear-gradient(90deg,transparent,#2dd4bf44,#2dd4bf,#2dd4bf44,transparent); }
.hud-stat { background:#111827; border:1px solid #2d3748; border-radius:8px;
  padding:12px 16px; display:flex; justify-content:space-between; align-items:center; }
.hud-label { font-size:10px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; }
.hud-val { font-family:'JetBrains Mono',monospace; font-size:14px; font-weight:700; color:#f1f5f9; }
.hud-online { display:inline-block; width:6px; height:6px; background:#10b981;
  border-radius:50%; animation:blink 2s infinite; margin-right:6px; }
</style>""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="hud-container">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
    <div>
      <div style="font-size:9px;color:#475569;letter-spacing:0.2em;text-transform:uppercase;">CRZ KAIZEN JOURNAL · PERFORMANCE HUD</div>
      <div style="font-size:14px;font-weight:700;color:#e2e8f0;margin-top:2px;">{meta['trader'] or 'Mi Cuenta'}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:9px;color:#64748b;"><span class="hud-online"></span>SISTEMA ACTIVO</div>
      <div style="font-size:11px;color:{lvl_color};font-weight:700;margin-top:2px;">{lvl_emoji} NIVEL {lvl_name}</div>
    </div>
  </div>
  <div style="height:1px;background:linear-gradient(90deg,transparent,#1e2a3a,transparent);margin-bottom:20px;"></div>
  <div style="position:absolute;top:16px;left:16px;width:16px;height:16px;border-top:2px solid {lvl_color}66;border-left:2px solid {lvl_color}66;"></div>
  <div style="position:absolute;top:16px;right:16px;width:16px;height:16px;border-top:2px solid {lvl_color}66;border-right:2px solid {lvl_color}66;"></div>
  <div style="position:absolute;bottom:16px;left:16px;width:16px;height:16px;border-bottom:2px solid {lvl_color}66;border-left:2px solid {lvl_color}66;"></div>
  <div style="position:absolute;bottom:16px;right:16px;width:16px;height:16px;border-bottom:2px solid {lvl_color}66;border-right:2px solid {lvl_color}66;"></div>
</div>""", unsafe_allow_html=True)

    circles = [
        (score,           lvl_color, 180, 14, "Score",    str(score)),
        (wr_score/30*100, BLUE,      140, 11, "Win Rate", f"{stats['win_rate']:.0f}%"),
        (pf_score/30*100, TEAL,      140, 11, "Factor",   f"{stats['pfactor']:.1f}x"),
        (rr_score/20*100, PURPLE,    140, 11, "R/R",      f"{rr_ratio:.1f}x"),
        (dd_score/20*100, AMBER,     140, 11, "DD Ctrl",  f"{abs(stats['max_dd']):.0f}%"),
    ]
    c_main, c1, c2, c3, c4 = st.columns([1.4, 1, 1, 1, 1])
    for col_w, (pct, color, size, stroke, label, val) in zip([c_main,c1,c2,c3,c4], circles):
        svg = hud_circle(pct, color, size, stroke, label, val)
        col_w.markdown(f"<div style='display:flex;justify-content:center;align-items:center;background:#050810;border:1px solid #0f1923;border-radius:12px;padding:12px;margin:4px;'>{svg}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    stats_grid = [
        ("PnL Total",     f"{stats['pnl_net']:+,.2f}$",   GREEN if stats["pnl_net"] >= 0 else RED),
        ("Operaciones",   str(stats["total_ops"]),          "#e2e8f0"),
        ("Mejor Trade",   f"{stats['best']:+,.2f}$",       GREEN),
        ("Peor Trade",    f"{stats['worst']:+,.2f}$",      RED),
        ("Mejor Hora",    f"{best_hour}:00",               TEAL),
        ("Peor Hora",     f"{worst_hour}:00",              "#f43f5e"),
        ("Mejor Símbolo", best_sym,                        GREEN),
        ("Evitar",        worst_sym,                       RED),
        ("Ganadoras",     str(stats["winners"]),           GREEN),
        ("Perdedoras",    str(stats["losers"]),            RED),
        ("Avg Ganadora",  f"{stats['avg_win']:+,.2f}$",   GREEN),
        ("Avg Perdedora", f"{stats['avg_loss']:+,.2f}$",  RED),
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:9px;color:#334155;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:12px;'>▸ MISIONES ACTIVAS</div>", unsafe_allow_html=True)

    missions = []
    if stats["win_rate"] < 60:
        missions.append((BLUE,  "WIN RATE", f"{stats['win_rate']:.1f}% → 60%",  "Menos trades, más calidad en las entradas"))
    if stats["pfactor"] < 2.0:
        missions.append((TEAL,  "FACTOR",   f"{stats['pfactor']:.2f} → 2.0",    "Deja correr ganadoras, corta perdedoras antes"))
    if rr_ratio < 2.0:
        missions.append((PURPLE,"R/R RATIO",f"{rr_ratio:.2f} → 2.0",            "TP mínimo el doble que el SL en cada trade"))
    if stats["max_dd"] < -10:
        missions.append((AMBER, "DRAWDOWN", f"{stats['max_dd']:.1f}% → -10%",   "Reduce tamaño de posición hasta estabilizar"))
    missions.append((TEAL, "HORARIO",   f"Opera más a las {best_hour}:00",      f"Evita las {worst_hour}:00 — menor rendimiento"))
    missions.append((BLUE, "SÍMBOLO",   f"Especialízate en {best_sym}",         f"Reduce exposición en {worst_sym}"))

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

# ══════════════════════════════════════════════════════════════════════════════
# TAB KAIZEN AI
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "ai":
    import streamlit.components.v1 as _components

    # Construir resumen de datos reales para el contexto del AI
    rr_ratio_ai = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0

    # Top símbolos
    sym_summary = df.groupby("symbol").agg(
        ops=("profit","count"),
        pnl=("pnl_net","sum"),
        wr=("win","mean")
    ).sort_values("pnl", ascending=False).reset_index()
    sym_lines = "\n".join([
        f"  - {r['symbol']}: {r['ops']} ops, PnL ${r['pnl']:+,.2f}, WR {r['wr']*100:.1f}%"
        for _, r in sym_summary.head(5).iterrows()
    ])

    # Horas con más PnL
    hr_summary = df.groupby("hour")["pnl_net"].sum().sort_values(ascending=False)
    best_hours  = ", ".join([f"{h}:00" for h in hr_summary.head(3).index])
    worst_hours = ", ".join([f"{h}:00" for h in hr_summary.tail(3).index])

    # Días con más PnL
    wd_summary = df.groupby("weekday")["pnl_net"].sum().sort_values(ascending=False)
    best_days  = ", ".join(list(wd_summary.head(2).index))
    worst_days = ", ".join(list(wd_summary.tail(2).index))

    TRADING_CONTEXT = f"""Eres el asistente de trading del CRZ Kaizen Journal. 
Tienes acceso a los datos REALES de trading de {meta['trader'] or 'el trader'}.
Responde siempre en español, de forma concisa y práctica. 
Cuando des consejos, basalos SIEMPRE en los datos reales del trader.

=== DATOS REALES DE LA CUENTA ===
Trader: {meta['trader'] or 'Sin nombre'}
Cuenta: {meta['cuenta']} | Empresa: {meta['empresa']}
Capital inicial: ${CAPITAL:,.0f}
PnL Total: ${stats['pnl_net']:+,.2f} ({stats['pnl_net']/CAPITAL*100:+.2f}%)
Balance actual: ${CAPITAL + stats['pnl_net']:,.2f}

=== MÉTRICAS DE RENDIMIENTO ===
Total operaciones: {stats['total_ops']}
Ganadoras: {stats['winners']} | Perdedoras: {stats['losers']}
Win Rate: {stats['win_rate']:.1f}%
Factor de Beneficio: {stats['pfactor']:.2f}
Ratio R/R: {rr_ratio_ai:.2f}
Max Drawdown: {stats['max_dd']:.1f}%
Ganancia media: ${stats['avg_win']:,.2f}
Pérdida media: ${stats['avg_loss']:,.2f}
Mejor trade: ${stats['best']:+,.2f}
Peor trade: ${stats['worst']:+,.2f}
Duración media: {stats['avg_duration']:.1f}h
Kaizen Score: {stats['kaizen_score']}/100

=== ANÁLISIS POR SÍMBOLO (top 5) ===
{sym_lines}

=== ANÁLISIS POR HORARIO ===
Mejores horas: {best_hours}
Peores horas: {worst_hours}

=== ANÁLISIS POR DÍA ===
Mejores días: {best_days}
Peores días: {worst_days}

Usa estos datos para dar respuestas personalizadas y accionables.
Sé directo, usa números reales del trader, y da consejos específicos.
Responde en formato markdown cuando sea útil (listas, negrita)."""

    # Sugerencias rápidas
    SUGERENCIAS = [
        "¿Cuál es mi mayor área de mejora?",
        "Analiza mis horas de trading",
        "¿Qué símbolo debería evitar?",
        "Dame un plan de mejora semanal",
        "Explícame mi drawdown",
        "¿Cómo mejorar mi win rate?",
    ]

    st.markdown(f"""
<div style="background:#0d1117;border:1px solid #1e2a3a;border-left:4px solid #2dd4bf;
     border-radius:8px;padding:14px 20px;margin-bottom:20px;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-size:15px;font-weight:700;color:#f1f5f9;">🤖 Kaizen AI</div>
    <div style="font-size:11px;color:#475569;margin-top:2px;">
      Analizando datos de <b style="color:#2dd4bf;">{meta['trader'] or 'tu cuenta'}</b> · 
      {stats['total_ops']} operaciones · Kaizen Score {stats['kaizen_score']}/100
    </div>
  </div>
  <div style="font-size:11px;color:#4ade80;font-weight:600;">● Contexto cargado</div>
</div>
""", unsafe_allow_html=True)

    # Inicializar historial de chat
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    # Sugerencias rápidas
    st.markdown("<div style='font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;'>Preguntas rápidas</div>", unsafe_allow_html=True)
    cols_sug = st.columns(3)
    for i, sug in enumerate(SUGERENCIAS):
        with cols_sug[i % 3]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state.ai_messages.append({"role": "user", "content": sug})
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Mostrar historial
    for msg in st.session_state.ai_messages:
        is_user = msg["role"] == "user"
        bg    = "#1e2a3a" if is_user else "#0d1117"
        border = "#334155" if is_user else "#1e2a3a"
        align  = "flex-end" if is_user else "flex-start"
        label  = "Tú" if is_user else "🤖 Kaizen AI"
        label_color = "#94a3b8" if is_user else "#2dd4bf"
        st.markdown(f"""
<div style="display:flex;justify-content:{align};margin-bottom:12px;">
  <div style="max-width:85%;background:{bg};border:1px solid {border};
       border-radius:12px;padding:12px 16px;">
    <div style="font-size:10px;color:{label_color};font-weight:700;
         margin-bottom:6px;text-transform:uppercase;">{label}</div>
    <div style="font-size:13px;color:#e2e8f0;line-height:1.6;">{msg['content']}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Si último mensaje es del user → llamar a Claude API
    if st.session_state.ai_messages and st.session_state.ai_messages[-1]["role"] == "user":
        with st.spinner("Analizando tus datos..."):
            try:
                import requests as _req
                messages_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.ai_messages
                ]
                api_key = st.secrets.get("GROQ_API_KEY", "")
                if not api_key:
                    answer = "⚠️ Falta la API key. Añade `GROQ_API_KEY` en Settings → Secrets de Streamlit Cloud."
                else:
                    resp = _req.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}",
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "max_tokens": 1024,
                            "messages": [
                                {"role": "system", "content": TRADING_CONTEXT},
                                *messages_api
                            ],
                        },
                        timeout=30
                    )
                    if resp.status_code == 200:
                        answer = resp.json()["choices"][0]["message"]["content"]
                    else:
                        answer = f"Error {resp.status_code}: {resp.text[:200]}"
            except Exception as e:
                answer = f"Error conectando con la IA: {e}"

        st.session_state.ai_messages.append({"role": "assistant", "content": answer})
        st.rerun()

    # Input del usuario
    st.markdown("<br>", unsafe_allow_html=True)
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        user_input = st.text_input(
            "",
            placeholder="Pregúntame sobre tus operaciones, estrategia, mejoras...",
            key="ai_input",
            label_visibility="collapsed"
        )
    with col_btn:
        send = st.button("Enviar →", type="primary", key="ai_send")

    if send and user_input.strip():
        st.session_state.ai_messages.append({"role": "user", "content": user_input.strip()})
        st.rerun()

    # Botón limpiar chat
    if st.session_state.ai_messages:
        if st.button("🗑️ Limpiar conversación", key="ai_clear"):
            st.session_state.ai_messages = []
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB LIVE MT5
# ══════════════════════════════════════════════════════════════════════════════
if _nav == "live":
    show_live_tab()


