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
.stApp { background:#1c2333; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding:1.2rem 2rem 3rem; max-width:100%; }

/* ── Sidebar siempre visible — ocultar botón cerrar ─────── */
section[data-testid="stSidebar"] {
    transform:none !important;
    visibility:visible !important;
    display:flex !important;
}
[data-testid="stSidebarCollapseButton"] {
    display:none !important;
}
[data-testid="stSidebarCollapsedControl"] {
    display:none !important;
}

/* ── Sidebar panel ───────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background:#151c2e !important;
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
    display:block !important;
    opacity:1 !important;
    position:fixed !important;
    left:0 !important; top:50% !important;
    transform:translateY(-50%) !important;
    z-index:99999 !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    background:#2dd4bf !important;
    border-radius:0 10px 10px 0 !important;
    color:#0a0f1a !important;
    border:none !important;
    width:28px !important; height:56px !important;
    box-shadow:4px 0 20px rgba(45,212,191,.6) !important;
    cursor:pointer !important;
    visibility:visible !important;
    display:flex !important;
    opacity:1 !important;
    font-size:18px !important;
}
[data-testid="stSidebarCollapsedControl"] button svg {
    fill:#0a0f1a !important;
    color:#0a0f1a !important;
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
    background:#111520 !important;
    border:1px solid #182035 !important;
    border-top:2px solid #2dd4bf !important;
    border-radius:8px !important;
    color:#2dd4bf !important;
    font-size:13px !important; font-weight:700 !important;
    padding:10px 14px !important;
    text-align:left !important;
    margin-bottom:3px !important;
    box-shadow:0 4px 16px rgba(0,0,0,.5) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p {
    color:#2dd4bf !important; font-weight:700 !important;
}
/* Inactive nav item (type=secondary) */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] {
    background:#111520 !important;
    border:1px solid #182035 !important;
    border-top:2px solid transparent !important;
    border-radius:8px !important;
    color:#64748b !important;
    font-size:13px !important; font-weight:500 !important;
    padding:10px 14px !important;
    text-align:left !important;
    margin-bottom:3px !important;
    transition:all .2s ease !important;
    box-shadow:0 2px 8px rgba(0,0,0,.3) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
    background:#111520 !important;
    border-color:#243055 !important;
    border-top:2px solid #2dd4bf !important;
    color:#e2e8f0 !important;
    box-shadow:0 4px 16px rgba(0,0,0,.5) !important;
    transform:translateY(-1px) !important;
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
/* ── Light/dark toggle — gris cuando esta apagado ────────── */
[data-testid="stToggle"] [role="switch"] {
    background-color:#374151 !important;
    border-color:#4b5563 !important;
    outline:none !important;
}
[data-testid="stToggle"] [role="switch"][aria-checked="true"] {
    background-color:#2dd4bf !important;
    border-color:#2dd4bf !important;
}
[data-testid="stToggle"] [role="switch"] div {
    background-color:#9ca3af !important;
}
[data-testid="stToggle"] [role="switch"][aria-checked="true"] div {
    background-color:#0a0f1a !important;
}
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

    # Auto-derivar capital inicial desde MT5: balance_actual - pnl_total_historico
    cuenta_info = live.get("cuenta", {})
    mt5_balance = cuenta_info.get("balance", 0)
    total_pnl   = float(df["pnl_net"].sum()) if len(df) > 0 else 0.0
    if mt5_balance > 0 and abs(total_pnl) > 0:
        derived = round(mt5_balance - total_pnl, 2)
        if derived > 100:
            capital = derived

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
    TEAL = "#2dd4bf"

    st.markdown("""
<style>
.step-card {
    background:#0d1117 !important; border:1px solid #1e2a3a !important;
    border-radius:12px !important; padding:20px 22px !important; margin-bottom:10px !important;
    display:flex !important; align-items:flex-start !important; gap:16px !important;
}
.step-num {
    background:linear-gradient(135deg,#0d9488,#2dd4bf) !important;
    color:#0a0f1a !important; font-weight:800 !important; font-size:14px !important;
    min-width:32px !important; height:32px !important; border-radius:50% !important;
    display:flex !important; align-items:center !important; justify-content:center !important;
    flex-shrink:0 !important; margin-top:2px !important;
}
.step-title { font-size:14px !important; font-weight:700 !important; color:#f1f5f9 !important; margin-bottom:4px !important; }
.step-body  { font-size:12px !important; color:#94a3b8 !important; line-height:1.6 !important; }
.step-body b { color:#e2e8f0 !important; }
.step-code  {
    background:#050810 !important; border:1px solid #2dd4bf44 !important; border-radius:6px !important;
    font-family:'JetBrains Mono',monospace !important; font-size:11px !important; color:#2dd4bf !important;
    padding:6px 10px !important; margin-top:6px !important; word-break:break-all !important;
    display:block !important;
}
.welcome-hero { text-align:center !important; padding:32px 0 24px !important; }
.welcome-hero div { color:inherit !important; }
.connect-box {
    background:#0d1117 !important; border:1px solid #1e2a3a !important; border-top:3px solid #2dd4bf !important;
    border-radius:12px !important; padding:24px !important; margin-bottom:24px !important;
}
.welcome-footer {
    text-align:center !important; margin-top:20px !important; padding:14px !important;
    background:#050810 !important; border-radius:8px !important; border:1px solid #0f1923 !important;
}
.welcome-footer span { font-size:11px !important; color:#475569 !important; }
</style>
""", unsafe_allow_html=True)

    if not_found:
        st.warning("⚠️ Cuenta no encontrada. Asegurate de que el EA este activo en MT5 y espera 10 segundos.")

    # ── Hero ────────────────────────────────────────────────────────────
    st.markdown("""
<div class="welcome-hero">
  <div style="margin-bottom:12px;">
    <svg width="52" height="40" viewBox="0 0 52 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polyline points="2,32 12,20 22,26 34,8 50,14" stroke="#2dd4bf" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <circle cx="2" cy="32" r="2.5" fill="#2dd4bf" opacity="0.6"/>
      <circle cx="12" cy="20" r="2.5" fill="#2dd4bf" opacity="0.6"/>
      <circle cx="22" cy="26" r="2.5" fill="#2dd4bf" opacity="0.6"/>
      <circle cx="34" cy="8" r="2.5" fill="#2dd4bf"/>
      <circle cx="50" cy="14" r="2.5" fill="#2dd4bf" opacity="0.6"/>
    </svg>
  </div>
  <div style="font-size:26px;font-weight:800;color:#f1f5f9;font-family:'Space Grotesk',Inter,sans-serif;">
    CRZ Kaizen Journal
  </div>
  <div style="font-size:13px;color:#475569;margin-top:6px;">
    Trading consciente · Mejora continua · 1% mejor cada día
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Connect box ─────────────────────────────────────────────────────
    st.markdown('<div class="connect-box">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:11px;color:{TEAL};font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px;">Conectar cuenta MT5</div>', unsafe_allow_html=True)
    _, col_c, _ = st.columns([1, 3, 1])
    with col_c:
        cuenta_val = st.text_input("Cuenta", value=st.session_state.get("cuenta_mt5",""),
            placeholder="Escribe tu número de cuenta MT5 (ej: 504062347)",
            label_visibility="collapsed", key="cuenta_input_main")
        if st.button("⚡  Conectar ahora", use_container_width=True, type="primary"):
            val = st.session_state.get("cuenta_input_main", cuenta_val).strip()
            if val:
                st.session_state.cuenta_mt5 = val
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Steps ───────────────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:11px;color:{TEAL};font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:14px;">Instala el EA una sola vez · 5 minutos</div>', unsafe_allow_html=True)

    _, col_dl, _ = st.columns([1, 2, 1])
    with col_dl:
        st.link_button(
            "⬇️  Descargar CRZ_Kaizen_Bridge.mq5",
            "https://raw.githubusercontent.com/cristianzafra924-source/crz-kaizen-journal/main/CRZ_Kaizen_Bridge.mq5",
            use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("""
<div class="step-card">
  <div class="step-num">1</div>
  <div>
    <div class="step-title">Instala el EA en MT5</div>
    <div class="step-body">
      Abre MT5 y ve a:<br>
      <b>Archivo → Abrir carpeta de datos → MQL5 → Experts</b><br>
      Pega el archivo <b>CRZ_Kaizen_Bridge.mq5</b> en esa carpeta y cierra.
    </div>
  </div>
</div>

<div class="step-card">
  <div class="step-num">2</div>
  <div>
    <div class="step-title">Activa WebRequest</div>
    <div class="step-body">
      En MT5: <b>Herramientas → Opciones → Asesores Expertos</b><br>
      Marca <b>"Permitir WebRequest"</b> y añade esta URL:
      <div class="step-code">https://crz-bridge.cristian-zafra924.workers.dev</div>
      Haz clic en <b>Aceptar</b>.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    with col_r:
        st.markdown("""
<div class="step-card">
  <div class="step-num">3</div>
  <div>
    <div class="step-title">Activa el EA en un gráfico</div>
    <div class="step-body">
      En el <b>Navegador</b> de MT5 busca <b>CRZ_Kaizen_Bridge</b>.<br>
      Arrástralo a cualquier gráfico abierto.<br>
      En la ventana que aparece, pulsa <b>Aceptar</b>.<br>
      Verás una carita 🙂 en la esquina del gráfico.
    </div>
  </div>
</div>

<div class="step-card">
  <div class="step-num">4</div>
  <div>
    <div class="step-title">Conecta aquí arriba</div>
    <div class="step-body">
      El EA sube tus datos automáticamente cada <b>10 segundos</b>.<br>
      Escribe tu <b>número de cuenta MT5</b> en el campo de arriba<br>
      y pulsa <b>Conectar</b>. ¡Listo! 🎯
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="text-align:center;margin-top:20px;padding:14px;background:#050810;
     border-radius:8px;border:1px solid #0f1923;">
  <span style="font-size:11px;color:#334155;">
    ✅ Sin Python · ✅ Sin terminal · ✅ Datos en tiempo real · ✅ Seguro y encriptado
  </span>
</div>
""", unsafe_allow_html=True)

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
# ── Header ─────────────────────────────────────────────────────────────────────
col_hd, _ = st.columns([5, 1])
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
light_mode = False

if light_mode:
    st.markdown("""<style>
    .stApp { background: #e8edf2 !important; } .block-container { padding:1.2rem 2rem 3rem !important; }
    .crz-header { background: #ffffff !important; border-color: #cbd5e1 !important; }
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
    p, span, label, div { color: #1e293b !important; }
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
        ("◈",  "Noticias",     "news"),
        ("📡", "Monitor",      "monitor"),
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
    # Usar capital derivado de MT5 (no el manual) si es válido
    if stats.get("capital", 0) > CAPITAL:
        CAPITAL = stats["capital"]
        st.session_state.capital_manual = int(CAPITAL)
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
_lm = False
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
    _lm = False
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

    light_mode = False
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
        (max(0, 100+stats["max_dd"]), AMBER, 140, 11, "Max DD", f"{stats['max_dd']:.0f}%"),
    ]
    c_main, c1, c2, c3, c4 = st.columns([1.4, 1, 1, 1, 1])
    for col_w, (pct, color, size, stroke, label, val) in zip([c_main,c1,c2,c3,c4], circles):
        svg = hud_circle(pct, color, size, stroke, label, val)
        col_w.markdown(f"<div style='display:flex;justify-content:center;align-items:center;background:#050810;border:1px solid #0f1923;border-radius:12px;padding:12px;margin:4px;'>{svg}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    stats_grid = [
        ("PnL Total",     f"{stats['pnl_net']:+,.2f}$",   GREEN if stats["pnl_net"] >= 0 else RED),
        ("Operaciones",   str(stats["total_ops"]),          "#e2e8f0"),
        ("Mejor Trade",   f"{stats['best']:+,.0f}$",       GREEN),
        ("Peor Trade",    f"{stats['worst']:+,.0f}$",      RED),
        ("Mejor Hora",    f"{best_hour}:00",               TEAL),
        ("Peor Hora",     f"{worst_hour}:00",              "#f43f5e"),
        ("Mejor Símbolo", best_sym,                        GREEN),
        ("Evitar",        worst_sym,                       RED),
        ("Ganadoras",     str(stats["winners"]),           GREEN),
        ("Perdedoras",    str(stats["losers"]),            RED),
        ("Avg Ganadora",  f"{stats['avg_win']:+,.0f}$",   GREEN),
        ("Avg Perdedora", f"{stats['avg_loss']:+,.0f}$",  RED),
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
                            "model": "llama-3.3-70b-versatile",
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

if _nav == "news":
    import requests as _rq
    from datetime import date, timedelta

    st.markdown("""
<div style='font-size:9px;color:#2dd4bf;font-weight:700;letter-spacing:.15em;text-transform:uppercase;margin-bottom:16px;'>
◈ Calendario Económico · Datos en tiempo real
</div>""", unsafe_allow_html=True)

    _fh_key = st.secrets.get("FINNHUB_API_KEY", "")
    if not _fh_key:
        st.error("Añade FINNHUB_API_KEY en Streamlit Secrets.")
        st.stop()

    _today = date.today()
    _col1, _col2, _col3, _col4 = st.columns(4)
    with _col1:
        _from = st.date_input("Desde", value=_today, key="news_from")
    with _col2:
        _to   = st.date_input("Hasta", value=_today + timedelta(days=7), key="news_to")
    with _col3:
        _impact_filter = st.selectbox("Impacto", ["Todos", "high", "medium", "low"], index=0, key="news_impact")
    with _col4:
        _country_options = {
            "Todos": None,
            "🇺🇸 USD": "US",
            "🇪🇺 EUR": "EU",
            "🇩🇪 EUR/DE": "DE",
            "🇬🇧 GBP": "GB",
            "🇯🇵 JPY": "JP",
            "🇨🇦 CAD": "CA",
            "🇦🇺 AUD": "AU",
            "🇨🇭 CHF": "CH",
            "🇳🇿 NZD": "NZ",
        }
        _country_label = st.selectbox("País", list(_country_options.keys()), index=0, key="news_country")
        _country_filter = _country_options[_country_label]

    @st.cache_data(ttl=300)
    def _fetch_calendar(from_dt, to_dt, api_key):
        url = f"https://finnhub.io/api/v1/calendar/economic?from={from_dt}&to={to_dt}&token={api_key}"
        resp = _rq.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            cal = data.get("economicCalendar", [])
            return cal, resp.status_code, str(list(data.keys()))
        return [], resp.status_code, resp.text[:200]

    _events, _api_status, _api_keys = _fetch_calendar(str(_from), str(_to), _fh_key)
    if _api_status != 200 or len(_events) == 0:
        st.caption(f"Debug: status={_api_status} | keys={_api_keys} | from={_from} to={_to}")

    if _impact_filter != "Todos":
        _events = [e for e in _events if e.get("impact") == _impact_filter]
    if _country_filter:
        _events = [e for e in _events if e.get("country", "").upper() == _country_filter]

    _impact_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
    _impact_labels = {"high": "ALTO", "medium": "MEDIO", "low": "BAJO"}

    if not _events:
        st.info('No hay eventos para el periodo seleccionado. Prueba a ampliar las fechas o cambia el filtro de impacto a Todos.')
    else:
        st.markdown(f"<div style='font-size:11px;color:#475569;margin-bottom:12px;'>{len(_events)} eventos encontrados</div>", unsafe_allow_html=True)
        _ES_NAMES = {
            # US Employment
            "Non-Farm Payrolls": "Nóminas No Agrícolas",
            "Unemployment Rate": "Tasa de Desempleo",
            "Average Hourly Earnings MoM": "Salario Medio/Hora Mensual",
            "ADP Employment Change": "Variación Empleo ADP",
            "JOLTS Job Openings": "Ofertas de Trabajo JOLTS",
            "Initial Jobless Claims": "Solicitudes Iniciales de Desempleo",
            "Continuing Jobless Claims": "Solicitudes Continuas de Desempleo",
            # Prices
            "CPI MoM": "IPC Mensual",
            "CPI YoY": "IPC Anual",
            "Core CPI MoM": "IPC Subyacente Mensual",
            "Core CPI YoY": "IPC Subyacente Anual",
            "PPI MoM": "IPP Mensual",
            "PPI YoY": "IPP Anual",
            "Core PPI MoM": "IPP Subyacente Mensual",
            "PCE Price Index MoM": "Índice PCE Mensual",
            "PCE Price Index YoY": "Índice PCE Anual",
            "Core PCE Price Index MoM": "PCE Subyacente Mensual",
            "Core PCE Price Index YoY": "PCE Subyacente Anual",
            # GDP
            "GDP Growth Rate QoQ Adv": "PIB Trimestral (Preliminar)",
            "GDP Growth Rate QoQ 2nd Est": "PIB Trimestral (2ª Estimación)",
            "GDP Growth Rate QoQ Final": "PIB Trimestral (Final)",
            "GDP Growth Rate YoY": "PIB Anual",
            "GDP QoQ": "PIB Trimestral",
            "GDP YoY": "PIB Anual",
            # Retail / Consumer
            "Retail Sales MoM": "Ventas Minoristas Mensual",
            "Core Retail Sales MoM": "Ventas Minoristas Subyacente Mensual",
            "Consumer Confidence": "Confianza del Consumidor",
            "Michigan Consumer Sentiment": "Sentimiento Consumidor Michigan",
            "Michigan Consumer Sentiment Final": "Sentimiento Consumidor Michigan (Final)",
            "Personal Income MoM": "Ingreso Personal Mensual",
            "Personal Spending MoM": "Gasto Personal Mensual",
            # Fed
            "Fed Interest Rate Decision": "Decisión de Tipos de la Fed",
            "Federal Funds Rate": "Tasa de Fondos Federales",
            "FOMC Statement": "Comunicado del FOMC",
            "FOMC Minutes": "Actas del FOMC",
            "Fed Chair Powell Speech": "Discurso Presidente Powell (Fed)",
            # PMI / ISM
            "ISM Manufacturing PMI": "PMI Manufacturero ISM",
            "ISM Non-Manufacturing PMI": "PMI de Servicios ISM",
            "ISM Services PMI": "PMI de Servicios ISM",
            "S&P Global Manufacturing PMI": "PMI Manufacturero S&P Global",
            "S&P Global Services PMI": "PMI de Servicios S&P Global",
            "S&P Global Composite PMI": "PMI Compuesto S&P Global",
            "Manufacturing PMI": "PMI Manufacturero",
            "Services PMI": "PMI de Servicios",
            "Composite PMI": "PMI Compuesto",
            # Housing
            "Building Permits": "Permisos de Construcción",
            "Building Permits MoM": "Permisos de Construcción Mensual",
            "Housing Starts": "Inicio Construcción de Viviendas",
            "Housing Starts MoM": "Inicio Construcción Mensual",
            "Existing Home Sales": "Venta Viviendas Existentes",
            "New Home Sales": "Venta Viviendas Nuevas",
            "Pending Home Sales MoM": "Ventas Pendientes de Viviendas Mensual",
            "Case-Shiller Home Price MoM": "Precios Vivienda Case-Shiller Mensual",
            # Trade / Industry
            "Trade Balance": "Balanza Comercial",
            "Current Account": "Cuenta Corriente",
            "Industrial Production MoM": "Producción Industrial Mensual",
            "Capacity Utilization Rate": "Tasa Utilización de Capacidad",
            "Durable Goods Orders MoM": "Pedidos Bienes Duraderos Mensual",
            "Core Durable Goods Orders MoM": "Pedidos Bienes Duraderos (sin transp.) Mensual",
            "Factory Orders MoM": "Pedidos de Fábricas Mensual",
            # Treasury auctions
            "3-Month Bill Auction": "Subasta Letras 3 Meses",
            "6-Month Bill Auction": "Subasta Letras 6 Meses",
            "2-Year Note Auction": "Subasta Bonos 2 Años",
            "5-Year Note Auction": "Subasta Bonos 5 Años",
            "7-Year Note Auction": "Subasta Bonos 7 Años",
            "10-Year Note Auction": "Subasta Bonos 10 Años",
            "30-Year Bond Auction": "Subasta Bonos 30 Años",
            # Europe / ECB
            "ECB Interest Rate Decision": "Decisión de Tipos del BCE",
            "ECB Press Conference": "Rueda de Prensa del BCE",
            "ECB Monetary Policy Meeting Accounts": "Actas Política Monetaria BCE",
            "Eurozone CPI MoM": "IPC Eurozona Mensual",
            "Eurozone CPI YoY": "IPC Eurozona Anual",
            "Eurozone Core CPI YoY": "IPC Subyacente Eurozona Anual",
            "Eurozone GDP Growth Rate QoQ": "PIB Eurozona Trimestral",
            "Eurozone Unemployment Rate": "Tasa de Desempleo Eurozona",
            "Germany CPI MoM": "IPC Alemania Mensual",
            "Germany GDP Growth Rate QoQ": "PIB Alemania Trimestral",
            "Germany Ifo Business Climate": "Clima Empresarial IFO Alemania",
            "Germany ZEW Economic Sentiment": "Sentimiento Económico ZEW Alemania",
            "Germany Manufacturing PMI": "PMI Manufacturero Alemania",
            "Germany Services PMI": "PMI Servicios Alemania",
            # UK
            "BoE Interest Rate Decision": "Decisión de Tipos Banco de Inglaterra",
            "BoE MPC Meeting Minutes": "Actas MPC (Banco de Inglaterra)",
            "UK CPI MoM": "IPC Reino Unido Mensual",
            "UK CPI YoY": "IPC Reino Unido Anual",
            "UK GDP Growth Rate QoQ": "PIB Reino Unido Trimestral",
            "UK Unemployment Rate": "Tasa de Desempleo Reino Unido",
            # Others
            "Japan BoJ Interest Rate Decision": "Decisión de Tipos BoJ Japón",
            "Canada Unemployment Rate": "Tasa de Desempleo Canadá",
            "BoC Interest Rate Decision": "Decisión de Tipos Banco de Canadá",
            "China NBS Manufacturing PMI": "PMI Manufacturero NBS China",
            "China Caixin Manufacturing PMI": "PMI Manufacturero Caixin China",
        }
        _ES_SFXS = [
            (" MoM", " Mensual"), (" YoY", " Anual"), (" QoQ", " Trimestral"),
            (" Adv", " (Preliminar)"), (" Prel", " (Preliminar)"),
            (" 2nd Est", " (2ª Est.)"), (" Final", " (Final)"), (" Flash", " (Flash)"),
        ]
        def _translate_ev(n):
            if n in _ES_NAMES: return _ES_NAMES[n]
            for en, es in _ES_SFXS: n = n.replace(en, es)
            return n
        for ev in sorted(_events, key=lambda x: x.get("time","")):
            _imp   = ev.get("impact", "low")
            _color = _impact_colors.get(_imp, "#475569")
            _label = _impact_labels.get(_imp, _imp.upper())
            _actual  = ev.get("actual",  "-")
            _est     = ev.get("estimate","-")
            _prev    = ev.get("prev",    "-")
            _unit    = ev.get("unit",    "")
            _country = ev.get("country", "")
            _time    = ev.get("time",    "")
            _event   = ev.get("event",   "")
            _event_es = _translate_ev(_event)

            def _fmt(v):
                if v is None or v == "": return "—"
                try: return f"{float(v):+.2f}{_unit}"
                except: return str(v)

            st.markdown(f"""
<div style='background:#111520;border:1px solid #182035;border-left:3px solid {_color};
     border-radius:8px;padding:12px 16px;margin-bottom:2px;
     display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
  <div style='min-width:90px;font-family:JetBrains Mono,monospace;font-size:11px;color:#475569;'>{_time}</div>
  <div style='min-width:36px;background:{_color}22;border:1px solid {_color}44;border-radius:4px;
       padding:2px 6px;font-size:9px;font-weight:700;color:{_color};text-align:center;'>{_country}</div>
  <div style='flex:1;font-size:13px;font-weight:600;color:#e2e8f0;'>{_event_es}</div>
  <div style='min-width:40px;text-align:center;'>
    <div style='font-size:9px;color:#475569;'>IMPACTO</div>
    <div style='font-size:10px;font-weight:700;color:{_color};'>{_label}</div>
  </div>
  <div style='min-width:60px;text-align:center;'>
    <div style='font-size:9px;color:#475569;'>ACTUAL</div>
    <div style='font-family:JetBrains Mono;font-size:12px;color:#2dd4bf;font-weight:700;'>{_fmt(_actual)}</div>
  </div>
  <div style='min-width:60px;text-align:center;'>
    <div style='font-size:9px;color:#475569;'>PREVISIÓN</div>
    <div style='font-family:JetBrains Mono;font-size:12px;color:#94a3b8;'>{_fmt(_est)}</div>
  </div>
  <div style='min-width:60px;text-align:center;'>
    <div style='font-size:9px;color:#475569;'>ANTERIOR</div>
    <div style='font-family:JetBrains Mono;font-size:12px;color:#64748b;'>{_fmt(_prev)}</div>
  </div>
</div>""", unsafe_allow_html=True)

            with st.expander(f"📖 ¿Qué es '{_event}'?", expanded=False):
                _cache_key = f"news_desc_{_event}"
                if _cache_key not in st.session_state:
                    _groq_key = st.secrets.get("GROQ_API_KEY", "")
                    if _groq_key:
                        with st.spinner("Generando descripción..."):
                            import time as _time
                            _groq_payload = {
                                "model": "llama-3.3-70b-versatile",
                                "max_tokens": 300,
                                "messages": [{"role":"user","content":
                                    f"Explica en español, en 3-4 frases claras y concisas, qué es el indicador económico '{_event}' ({_country}), "
                                    f"qué mide, por qué es importante para los mercados financieros y cómo afecta al trading. "
                                    f"Sé directo y práctico. Sin introducción ni conclusión."}]
                            }
                            try:
                                _resp = _rq.post(
                                    "https://api.groq.com/openai/v1/chat/completions",
                                    headers={"Content-Type":"application/json","Authorization":f"Bearer {_groq_key}"},
                                    json=_groq_payload, timeout=15
                                )
                                if _resp.status_code == 429:
                                    _time.sleep(3)
                                    _resp = _rq.post(
                                        "https://api.groq.com/openai/v1/chat/completions",
                                        headers={"Content-Type":"application/json","Authorization":f"Bearer {_groq_key}"},
                                        json=_groq_payload, timeout=15
                                    )
                                if _resp.status_code == 200:
                                    st.session_state[_cache_key] = _resp.json()["choices"][0]["message"]["content"]
                                elif _resp.status_code == 429:
                                    st.markdown("<div style='font-size:12px;color:#f59e0b;'>⏳ Límite de peticiones alcanzado. Cierra y vuelve a abrir en unos segundos.</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div style='font-size:12px;color:#ef4444;'>Error {_resp.status_code} al obtener descripción.</div>", unsafe_allow_html=True)
                            except Exception as _ex:
                                st.markdown(f"<div style='font-size:12px;color:#ef4444;'>Error de conexión: {_ex}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='font-size:12px;color:#64748b;'>Añade <b>GROQ_API_KEY</b> en Streamlit Cloud → Settings → Secrets para ver la descripción.</div>", unsafe_allow_html=True)
                if _cache_key in st.session_state:
                    st.markdown(f"<div style='font-size:13px;color:#94a3b8;line-height:1.7;padding:4px 0;'>{st.session_state[_cache_key]}</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)


    # ── Riesgo Geopolítico (GDELT) ─────────────────────────────────────────
    st.markdown("""<div style='margin-top:32px;margin-bottom:16px;'>
<div style='font-size:9px;color:#2dd4bf;font-weight:700;letter-spacing:.15em;text-transform:uppercase;'>
🌍 Riesgo Geopolítico · GDELT en tiempo real
</div></div>""", unsafe_allow_html=True)

    _geo_categories = {
        "⚔️ Conflictos":       ("war conflict military attack strike invasion",
                                "guerra conflicto militar ataque invasion bombardeo"),
        "🚫 Sanciones":        ("sanctions embargo trade war tariff",
                                "sanciones embargo guerra comercial aranceles"),
        "🛢️ Energía":          ("oil gas crude petroleum OPEC energy pipeline",
                                "petroleo gas crudo OPEP energia ducto"),
        "🏦 Bancos Centrales": ("central bank interest rate federal reserve ECB inflation",
                                "banco central tipos interes reserva federal BCE inflacion"),
        "⚠️ Crisis política":  ("political crisis protest coup election instability",
                                "crisis politica protesta golpe estado elecciones"),
        "🌊 Rutas comerciales":("shipping strait Hormuz Suez Red Sea blockade",
                                "envios estrecho Hormuz Suez Mar Rojo bloqueo"),
    }
    _geo_col1, _geo_col2 = st.columns([2, 1])
    with _geo_col1:
        _geo_cat = st.selectbox("Categoría", list(_geo_categories.keys()), key="geo_cat")
    with _geo_col2:
        _geo_lang = st.selectbox("Idioma", ["Español", "English", "Todos"], key="geo_lang")

    @st.cache_data(ttl=600)
    def _fetch_gdelt(query, lang):
        import urllib.parse
        _q = urllib.parse.quote(query)
        _url = (f"https://api.gdeltproject.org/api/v2/doc/doc?query={_q}"
                f"&mode=artlist&format=json&maxrecords=30&sort=DateDesc&timespan=14d")
        try:
            _res = _rq.get(_url, timeout=20)
            if _res.status_code == 200:
                return _res.json().get("articles", [])
            elif _res.status_code == 429:
                st.warning("GDELT: demasiadas peticiones, espera 1 minuto y recarga.")
        except Exception as _ex:
            st.warning(f"GDELT error: {_ex}")
        return []

    _geo_qen, _geo_qes = _geo_categories[_geo_cat]
    _geo_query = _geo_qes if _geo_lang == "Español" else _geo_qen
    _geo_articles = _fetch_gdelt(_geo_query, _geo_lang)

    _cat_colors = {
        "⚔️ Conflictos":      "#ef4444",
        "🚫 Sanciones":       "#f97316",
        "🛢️ Energía":         "#eab308",
        "🏦 Bancos Centrales": "#3b82f6",
        "⚠️ Crisis política":  "#a855f7",
        "🌊 Rutas comerciales": "#06b6d4",
    }
    _geo_color = _cat_colors.get(_geo_cat, "#2dd4bf")

    if not _geo_articles:
        st.info("No se encontraron noticias. Prueba otra categoría o idioma.")
    else:
        from datetime import datetime as _dt, timezone as _tz
        _now = _dt.now(_tz.utc)
        for _art in _geo_articles:
            _title  = _art.get("title", "Sin título")
            _url    = _art.get("url", "#")
            _domain = _art.get("domain", "")
            _seen   = _art.get("seendate", "")
            try:
                _pub = _dt.strptime(_seen, "%Y%m%dT%H%M%SZ").replace(tzinfo=_tz.utc)
                _diff = int((_now - _pub).total_seconds() / 3600)
                _time_str = f"hace {_diff}h" if _diff > 0 else "Ahora"
            except:
                _time_str = ""
            st.markdown(f"""
<div style='background:#0d1117;border:1px solid #1e2a3a;border-left:3px solid {_geo_color};
     border-radius:8px;padding:12px 16px;margin-bottom:8px;'>
  <div style='font-size:13px;color:#e2e8f0;line-height:1.5;margin-bottom:6px;'>
    <a href='{_url}' target='_blank' style='color:#e2e8f0;text-decoration:none;'>{_title}</a>
  </div>
  <div style='font-size:11px;color:#475569;'>
    <span style='color:{_geo_color};font-weight:600;'>{_geo_cat}</span>
    &nbsp;·&nbsp;{_domain}&nbsp;·&nbsp;{_time_str}
  </div>
</div>""", unsafe_allow_html=True)

if _nav == "monitor":
    import streamlit.components.v1 as _comp
    import json as _json
    import time as _time_m
    from datetime import datetime as _dtnow, timezone as _utc

    _ch_defs = [
        ("Euronews", "UCSrZ3UV4jOidv8ppoVuvW9Q", "#3b82f6"),
        ("DW News",  "UCknLrEdhRCp1aegoMqRaCZg", "#6366f1"),
    ]

    _yt_key = st.secrets.get("YOUTUBE_API_KEY", "")
    _now_ts = _time_m.time()

    if "yt_ch_cache" not in st.session_state or _now_ts - st.session_state.get("yt_ch_ts", 0) > 1800:
        _ids = {}
        for _cn, _cid, _cc in _ch_defs:
            _ids[_cid] = ""
            if _yt_key:
                try:
                    _yr = requests.get("https://www.googleapis.com/youtube/v3/search",
                        params={"part":"id","channelId":_cid,"type":"video","eventType":"live","key":_yt_key,"maxResults":1},
                        timeout=8)
                    if _yr.status_code == 200:
                        _it = _yr.json().get("items", [])
                        _ids[_cid] = _it[0]["id"]["videoId"] if _it else ""
                except Exception:
                    pass
        st.session_state["yt_ch_cache"] = _ids
        st.session_state["yt_ch_ts"] = _now_ts

    _vid_map = st.session_state.get("yt_ch_cache", {})
    _ch_list = [{"name":_cn,"channelId":_cid,"videoId":_vid_map.get(_cid,""),"color":_cc}
                for _cn, _cid, _cc in _ch_defs]

    _utc_str = _dtnow.now(_utc.utc).strftime("%a %d %b %Y  %H:%M UTC")
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:7px 16px;
     background:#060d1a;border:1px solid #0f1f35;border-radius:8px;margin-bottom:12px;">
  <div style="width:8px;height:8px;background:#ef4444;border-radius:50%;box-shadow:0 0 8px #ef4444;"></div>
  <span style="font-size:11px;color:#2dd4bf;font-weight:700;letter-spacing:.12em;">MONITOR GLOBAL</span>
  <span style="color:#1e2a3a;">|</span>
  <span style="font-size:9px;color:#334155;">YT: {'OK' if _yt_key else 'sin key'}</span>
  <span style="font-size:10px;color:#475569;margin-left:auto;">{_utc_str}</span>
</div>""", unsafe_allow_html=True)

    _mon_maps = {
        "GLOBAL / Ucrania": "https://liveuamap.com",
        "Siria":            "https://syria.liveuamap.com",
        "Libano":           "https://lebanon.liveuamap.com",
        "Iran":             "https://iran.liveuamap.com",
        "Israel / Gaza":    "https://israel.liveuamap.com",
        "Asia":             "https://asia.liveuamap.com",
    }
    _sel_map = st.selectbox("Zona del mapa", list(_mon_maps.keys()), key="mon_map")
    _map_url = _mon_maps[_sel_map]

    _col_map, _col_right = st.columns([6, 4])

    with _col_map:
        st.markdown("<div style='font-size:8px;color:#ef4444;font-weight:700;"
                    "letter-spacing:.15em;margin-bottom:4px;'>SITUACION GLOBAL EN VIVO</div>",
                    unsafe_allow_html=True)
        _comp.iframe(_map_url, height=680)

    with _col_right:
        _ch_json = _json.dumps(_ch_list, ensure_ascii=True)

        _news_json  = '[{"title": "Ir\\u00e1n Exige Levantar Sanciones para Reabrir el Estrecho de Ormuz y Alcanzar un Acuerdo con EE. UU. - UNITED24 Media", "url": "https://news.google.com/rss/articles/CBMi0gFBVV95cUxOaWNsOUhLaHM2R2kzVE51UElibE40dDVMYXJNQUxBWEJySG5fQU1tWUtUaXhsR01Ga0s2NjJlOFMtdkt6M3JvWEpvVVdWb2gxZ084Mkh5MVo3UnBYZGFwWmFLU010M0VMQy04QmFNWWs0M1ZKbldEWFI1ZUQ2WkR4TkNrZXpoZlhrcTNIemdkQmp3Ry1TdXJnWlc5OGl5RXp3YUxCY3p1TUIwUzNlQURSTnFPX0Z3UUhxSEJLMDNCLWxnN1hramF3Y0RjMmppa0ZCdFE?oc=5", "src": "UNITED24 Media", "ago": "hace 26d", "ts": 1775545200}, {"title": "Por qu\\u00e9 la guerra de Ir\\u00e1n es una oportunidad para Putin y Rusia - BBC", "url": "https://news.google.com/rss/articles/CBMiW0FVX3lxTFBxbTRSaHpkTlB1UFUxelV3NHVBMlhxYXRGZ0hWTTkwWlFueC0zT3kwV29idllUMTR2S0JTcUlPWWd0blBQNEdvUzdkbV80c21qYkszSUtmMnpKQ2_SAWBBVV95cUxOVW9NUnlLa0F6MmZCV3dOMWZxcmVZTWJPOHlkVXdYdFhMUGtXVnZiYzctcHdOdENIdU54dkFYdGF1T3pnNERrT21La0d4cldNYlhUaHNfcFY1ZHNXVkVyYUs?oc=5", "src": "BBC", "ago": "hace 53d", "ts": 1773212400}, {"title": "\\u00bfEs Rusia el que m\\u00e1s se beneficia de la guerra de Estados Unidos e Israel contra Ir\\u00e1n? - TRT Espa\\u00f1ol", "url": "https://news.google.com/rss/articles/CBMiW0FVX3lxTFA5a2I0YnJndXZCeHN5dkJlYjM2VDRNLVBxaXlMUDV6NE14a0hCSmpiS3VZb0p6NVF2RTlkNWY4WndLMzlNTDc0X1A4Y3JvZm92a0FPUEdWU0E5VGc?oc=5", "src": "TRT Espa\\u00f1ol", "ago": "hace 45d", "ts": 1773932684}, {"title": "Zelenski avisa de que Rusia est\\u00e1 ganando la guerra de Ir\\u00e1n: pues as\\u00ed lo est\\u00e1 haciendo - El HuffPost", "url": "https://news.google.com/rss/articles/CBMirwFBVV95cUxPTVR1ZklxS2F4WGYzT05fRnVMSERDWlFPREE0Wk4yLUlhd2p2eTNYRGJPRmFSMllObmZJU0prNHZHbzRXQmduajBTcFRCZmsyMjdzdzZxYmxzSFVFcG5PcVpVOElyYVVBOWRjRUlaWGV1cjlZclFBaWZ1TVFoWVRkY3RST3FVVU5NWnY0WUdJTWNjR3FkUTBVeDdPRW1ERmF2bU5HV2t4WW5SWnR4WElr0gHDAUFVX3lxTFBfQmZQSkFVY2NFaEJ2Rk5GXzgwVmgwVEZjbjNMZWJrajgxN0RRRXBKMHFfY0IxWHlhUVFpRXRWOGNHQjNvRW9yTWhLbVltNE9sczhDcW5YRHl6bEJwaUFVdzVXeU5UWm0xMjhpYzZkS3RsUkh2WUFCY2xyUjlhRXlJNFF6NDJ0WlFTSGFCbkl6LWZNRVVEdDBHYmJwYTFTcE1MS1dMQ3dMRXduZ1FuQlQ4U280MkhvUzJfNHBxb09TdGtfRQ?oc=5", "src": "El HuffPost", "ago": "hace 30d", "ts": 1775199600}, {"title": "Merz critica a EEUU y considera \\"un error\\" levantar las sanciones al petr\\u00f3leo ruso tras la escalada de - LaSexta", "url": "https://news.google.com/rss/articles/CBMihgJBVV95cUxNTGF6RGxvQW9vdHY0OUJfWUpFNzJfRFhkRWY5aXdFVHdsV0FmYkRKNHBIYjJjd0k4SF9KeVRVLVV6ek9aNjlndUEyVWxWY3ZSWHdweF8tRFozNmF5VjlkamZVeE50bkJCTG1NTWtQdUdTTkVwMzItZ0J5WVk0bnZaMjl5Zk1lcFJEQzhXT05FUF9hMnhMV1UyUWdzMEM0YUM5QUtGbVFkS21GdkZSTWxpa01WR2lRYnh6bDVMV2VoXzRrYUo1NWtYREU3emJzOHRZSFhqXzNjZVBtSFJIQjRMdGtpeFBnbVVObFRzV0FaYU16bVVJS2p2NUFfQ3N3YVk5d1FpbFZR0gGGAkFVX3lxTE16NEtNWVVlSTlKbk5uLURiWU9oVGZTem5PWWlta0w1aFF0QWpRMkFZU05xNEpfSi11MGxDZE8xcVIzMkU4cm1EQ0Vpb3lLOXplbGh0NDExVjJPZmNXUEU4aV85SUVzbTlHdmNtR0l0Y2pnYzk5eloxWjdnamtsU2QxemdSWDRTRjJSaTlKZ1ZsZjRXbzM0R3lFdHlHTHlyakZDY0ZSbzYwUEJSN2FZZi1hWnRZUnlvU2RzN1Q5VUF5QjBxM1BGVnNtMGRseV9QdjRqVzJveDcta3dNcDROWHVTTDJnNURLYVp6XzZQMkR6WkhKRUFzRm5HcVo3eHNWYnptUHkxTnc?oc=5", "src": "LaSexta", "ago": "hace 51d", "ts": 1773385200}, {"title": "Trump relaja sanciones al petr\\u00f3leo ruso para frenar el precio del crudo - La Raz\\u00f3n", "url": "https://news.google.com/rss/articles/CBMi3gFBVV95cUxPWDZnUWY4bTlibTF3ZGR1dnp1Sm1pektqUGZLUGgtMG01eGtFLTRON0hMUW9XbkNsVXh0ZGQ1cnFyLUI3X2RHNll0dWRUclVpejBIZ2ZGaV9GTHdjQkhSem1aUGl4SlI5dTgyc2J4ZG5lY0FyVHZfcDBfLW9keDlYR3BwS1FKdlhONU04VExGRlJpaTh1SUhiMDZGOEc5UkRhQ09rTG5zMXRESHNRRV9DVmMwU3owYXFRLUZLOHg3M1hwckZhZnZHR1VqcTFacGh1MGNYUmNwTFQtNFM5SWfSAfIBQVVfeXFMTUd4b29jNFFLd29VMkFpUWkwUEFJRmNGQ19wQWppN3gxM0ZRZzNfV1pVdjlnOUd2Vjl6ZUU0clUwQXNLTV9DclFLenVXaXZ0a1ZKdlJ5TER3aUd0VUNLcHJCUFFWTU9waGJQSk90c3Y0TTFlTV9HbVIwZ0tiRTNFNDVmOGRDQnZycThzTVJPUkhKc1FTNnVITGVnSkFBZ3FhcFNVQ2NQYmJvTjhrbDhpQzFnXzhEZzIzOF83SlE1V0RMcmV3eWEtLWltMEJucEp3dnpkd1hGNzM3UHZYUm9oMEtic0ZMZllHQmVMdTJTejhqWlE?oc=5", "src": "La Raz\\u00f3n", "ago": "hace 51d", "ts": 1773385200}, {"title": "Europa y Ucrania cierran filas contra el alivio de sanciones al petr\\u00f3leo ruso - MUNDIARIO", "url": "https://news.google.com/rss/articles/CBMi5wFBVV95cUxNUnpNZGdBblhTTGFBWWtQenJQVkJqZ01YOHNleFFzLVZRVjFTbXZwaFFfeDBoZ1ZzNUJ2ZFJoY0hRMEhKZDAyUG1vbHBkaEtfMmNZQS03Qzh2WWZMYjJtZzZwRmtuTFdUaUxUNVMzRGRHT0R0anN1QVpnaml1aHZZTE52Wmh0eTVkYmd3QmRFX3NsTVpMc2hLbzE1VlMyTFE5Y3RTRlFmMEtEV0w2SmhyQVRQYkc3TWEzLXlSTFdSTERlcFRvLUw1eGdkVVhMNU5HVnNWYVowZ2VBRlVvWnY3TTZRek4tS0HSAewBQVVfeXFMUEZ5eGZvQXQ5ODJPNDhxcFphVmRYaUJENFBONVZvbTRFM3liYmpWRVowSHBVZ1FSZDhzYnRSVEV3MVYyRUJVbjc2YXZVQlZjWW1QcFVKdUdvLXNQaDB5VHJpTVVSQ04zYmI4SFNpN1V3eEFWQU5VTEZYTTQ4UjNTdjdqVzJld3dPODNlZVp5WFhmblpkdnJXZkNiTVZQWmQ4SjFUTVc3ZFc2cFo5eENwZlN3R2stRXhDSGU3Q0VYb0ZCWC1TNmhIeW9sT18ycXpzakZjTlhXTW11ZjFqT1ZHa19vcEpmY1Z0U1VXdXU?oc=5", "src": "MUNDIARIO", "ago": "hace 50d", "ts": 1773471600}, {"title": "Zelensky y Starmer reclaman que la guerra con Ir\\u00e1n no desv\\u00ede el apoyo occidental a Ucrania - Infobae", "url": "https://news.google.com/rss/articles/CBMi1wFBVV95cUxQMGN3anBuWW5MWkUtd2FNclRhbVgwTDJscnFwaG5DUndaamJWOXJSb3U3WDNiY1prVWp6UEROZm85OVlJMVc0QkhtaVh6RHMwdy1hcUFPdHVKUXMwVjhGbDh5MDRpRzZvV2ZMNHl1Q2h6eWJzLUFTSld5VENmY0pqZnVQQ0x2LXYzMmdCcnFqNXZzTy1LLWRwdF80WTBvTU1JWlZfajVEMm9Zd1VFME5ZYUt0SWNRNlA0bkJKQnhnSVZoRDZKUUZ0Ny1aaVJicHBiMVk5b1I2VdIB8gFBVV95cUxQcy1Ud2JyLTVBOHhmU0h4REhQVlZsU0hzNnZRYUVYVElBNTJTV3J4WU9RN3drV29BXzBiMTNza1VyR3VxX09UaGE1UTh4bmNKb1BpdEpsYVVIdXdSS0paVE5GbEx4UVgxRjBZc2gxMTl2TUM0SllMSXZ4V1BDU2RHdDQzQnVKY3pkdFFXcklNVXQ5bUR3M1N6Ujhsc0Y1SHdFZm9UQ1dPZ1ZEYWpoZVowbTMyalpUcVNrVFpvSnlPa2d6cV9mT3p2QW9FcmFkMXhrZ05NeVEydEhvUDhFelVMZWF3bzgySkFQcnEzcXNuYjNBQQ?oc=5", "src": "Infobae", "ago": "hace 47d", "ts": 1773730800}, {"title": "Trump amenaza a Ir\\u00e1n con \\"golpear 20 veces m\\u00e1s fuerte\\" si bloquea el petr\\u00f3leo en el estrecho de Ormuz - El HuffPost", "url": "https://news.google.com/rss/articles/CBMimwFBVV95cUxOTnZIMzBkQmozcWpJOUk5NzJMVWVUVDJDVlhGME5SbGxJYVRCM3h5ZkNPYWhteWZlZjFJSFhKLTJiYXNHRUlpbVc3clRQZGpicG02Y2F4MjlCT3o1MVplU2w1NjNubEhzTkxKQXJja0dEWXhCSFg5Ty1ZRzNtR1BDTDJRUFNXYlA4MjVoaFJYUTJ0T21YRTc1UU1wZ9IBrwFBVV95cUxOMEE0alpBYnNmNTNoVzB3b3ZlM2JkbzctQmRkU1pxZVVibVc5d09RS2xQUjRVZDJsQ01oNVFlU0hSemFmc09sdVozZmJGcHprVkRybTlfdHRCUVRFMmJNamQyMDNoTU1QdUJOT3pIWnotQXR3WjhFUmdjdUdLUnFYV1V5RE95YkJFWmtVdVdZSHpFYjdNMkYyT1JNX0tnZDVPc0NkZFJjOGxnOWNQWG9J?oc=5", "src": "El HuffPost", "ago": "hace 55d", "ts": 1773039600}, {"title": "Crisis en Medio Oriente: Ir\\u00e1n elev\\u00f3 sus exigencias y complica las negociaciones con Estados Unidos - Infobae", "url": "https://news.google.com/rss/articles/CBMi4AFBVV95cUxQVUZmVkJaN3BpR01RTm5tUEx3al8zN0RNTklwVTgtX3NBX2p4UWpja1hHa0s2d2pQSTV4V3N0NDJGbkdOdHRnMG5MS21JclJyTFlBdFRQWDlJZ3BJd04yUDZ6LWR5RnZWRDNIVURaOWZReGlNOHhkdGxSSF9TczJmRnBxbFg3TEpVakJSRXFyV3BWOWptZEczQUlGM1lIODlKODhkbHM0eFQ4aEhkLW9pRHdBaUhoSm4yRDdIM0dmLXdHSE4yN0hYSjUyQnp1M0hfNFFjZkxHRC1pTndyT1lCUdIB-wFBVV95cUxPLTdSbnRLekxEQTNyQlVYRFBWTnlZbnVaN0NuWWdtcThYeUJfd0o3bkFFVnF4MUFEUHdRMnUyMUhOTUlTcHVDcnZPd2t3OGRBMDlndm5YWnhJT1h5b1dNaFJtTDRKMHJuY1U5ZkYyZk5maUFIQXhQVmNPLVUzYWw4Z2pSVThOSVNscHlTMmlzX0ZzbHpENUNkTUVBYVVBWThPX0ZFVEwxNFNRdFlTb1ZIZkJDS1JLSTlBRnFReXp3dHRCTE1iT192eGhsM3lQM2JfaWxLc3g3ZWFVZlpYYlhGZEp6UWhqSlB6a3ZEOVFsamRSdUFEX0xSVnlUVQ?oc=5", "src": "Infobae", "ago": "hace 39d", "ts": 1774422000}, {"title": "Estados Unidos sopesa levantar las sanciones al petr\\u00f3leo iran\\u00ed en el mar en medio de la guerra en Medio Oriente - Infoba", "url": "https://news.google.com/rss/articles/CBMi8wFBVV95cUxOWXRqZUFRbEhsUWdLdUZ2V192NXQ1Skh0RW1VOEU0SVFVXzVLNnVIc3BHZzZsQl9Za3p0NHV5dDlwZVkzdklvbVdOZFZPSmNRNEgxbXVqVmo4cDFhZEk5b0ZMU3NRbzF4am1RVkpVZnk5Z3dPdDQ5bG84cTVmRXFpbnphTG5FSjUzaS00alpmVU9YWW1FSXRIR0U5SlJjelE5blZDQU9ibEdKakdSemNGVGtfVjVxQnRXVkxxck9qUzVzRFgtdGpaY3R1Y1Z3ZG5fVndDcFRoVnpYbzRxWHd3RExTOVNqUzdGOXpKUnlkVlA1OWfSAY4CQVVfeXFMTVZoY0Zudi01dkVoOUFCUEQ3SGFxT1BTaUFNb2FTMTIxM3RVS05QbnpsbExoUnFFVE5uMjRJOUhhWldaWU54REVGQU1jODFuVlhWOHFkTElXZ0txMFdySm1ibmhYd0lBbWFQVWxIajJqOUdzZUZCVmlyc3cyejBONXVSdzdhYXg3ZHBMMGdYZmtNLXJzb3FWZ2x6MzQ0SDRyb3NmWHRERUd4YmJGYkswR0xUb3hkTVNQSU5EN2NpUS1mRFpyX1J0MXRJSkhOV1FOLVZ2ejdIMzFYZE9VNmROQ2pQUFQxc2JUVkQ0eUhiOFVpMkZuWWhUT3BJdUs2YmNIdGs4a3N5RjRuYmFCd1VR?oc=5", "src": "Infobae", "ago": "hace 45d", "ts": 1773903600}, {"title": "Estados Unidos levanta las sanciones a los petroleros rusos durante un mes - EL PA\\u00cdS", "url": "https://news.google.com/rss/articles/CBMiwAFBVV95cUxNdVdwOEpMVzBmYUFwdGNieXdzSHB4OU5BSS1wb09YT3R1VG43aHp5eDJhUHRuUl9zMGVzdDB1MWVkWkk0ZUZHNDQ3NjE1WHh0c2xJemczTFJzQkpxSEdUTHQyQVhDQ1h2eU1aQVBNRXBtZGVvOEF1VHZJeTkxZ2p5RFc0WEtlV0xvRlU4V0E3bTMzMnVKeFpheHpHc0h4R3Z2SERiVWNmanRRNmJWNHM2T1AyZEZKVngtdXU2TTgzM1jSAdQBQVVfeXFMTXNKbllxM0o5eGtWTV8tcjRnTUhYRS15RGR6YTZVbmtWbHVWWnU5eEFQb05zZHk0eWEtTENwZWNhbWpUUFhzcllWaFAzcDg4Q0JEWTVHN0QtUUpHclJFQjhDSlJnUGtubHJMb3BJUEZnc01EYm1YZmxzckllcHhzMnBfNlM0MmV5TGUwVVlBWXVSZ3Naelg5OFBra05wdHh0cFY3RlVRanJNY0IyUVBjTUZLVXlDMzhqMHJhRVRXVUhmWjBxaDdoVzVrRENHb2FJaDBoYTQ?oc=5", "src": "EL PA\\u00cdS", "ago": "hace 51d", "ts": 1773385200}, {"title": "El presidente de Ucrania critica la exenci\\u00f3n de sanciones al petr\\u00f3leo ruso por Estados Unidos - Infobae", "url": "https://news.google.com/rss/articles/CBMi2wFBVV95cUxPMThtVWFuM1RHSGEyVDBCbkljWWpPV2ctVzRtZkRhdGFERFNpeDM0cFVrbkpfMGEyQldqNmZ3Q1Q2dzdXTFhEOXg3eTVpWnZNSkItd1RwN1oyTHVMVGQyZ1FROGc2SWFyS01NQTlsdUU4V09rbFg2X1h6UHFjaS14M0dLcHVLYTNCdnJPQ0RLSVNVSVlLaWFIRkhERE9IUzBZRGtBSFRJaWJsZGh6bTJ2OFhqeVl1UzFKd3g1SGVQTDZLSkgxVjYxYWZwQ2FMaDZDV2tHdklMTUpiYk3SAfYBQVVfeXFMTnJrazkwZU9wU3dlVzFQWV9mSDlTdE01cVl6ZUU5N3JxajhEWGhmdFVWNmhHRkJockZxcGlUc3JkR2FuczNvWm5yZjFZRFJocGNNbjBzZzdxN3VMUnJyRFR1OEs2SzNROVpHd3ZMSkZZUWpJWWZHbGdycTRHbi1VTC1VbC1LTk1qVW5zNE9yQjdpdE9kdnVrbDJDMEpNMkpNWkVrUDJ0N2pXa1J0WXFXamlKTTdIRlIzem9UWkFkbnhBazllTjV1dkFvMjVRbEhqOFdWRGJWeldnbEw3cHFGZXFCV1R2ZTZWOEx5TVB4VFN4aUtsWlZ3?oc=5", "src": "Infobae", "ago": "hace 51d", "ts": 1773385200}, {"title": "Zelensky advirti\\u00f3 que levantar las sanciones al petr\\u00f3leo ruso ser\\u00eda un \\u201cgolpe serio\\u201d para Ucrania y el mundo - Infobae", "url": "https://news.google.com/rss/articles/CBMi7AFBVV95cUxQYXZPVzZkRlY1ZW15dC14QkNkM3cxLWpZQjEzYUZtYmZSWGc5NXlYdXRvQlNONEdIYXo2RnY2aVFYSVM0TExRcjFYNk50Zy1EV0Y5Qzdsek5PbXRUVmxHbXVFMEMtRTBLYW1BNDF1TFlDUXJCMjVRWF9KU0dWekx0bHBkSXlhWmRBdzV5ZUI2TlVacnMtM3pWQU1hdnZ1RkJrWHVab2xDWi1UdVUxb0FpYmltV2N5N2ZEMGxjb2xNZmNWckVPWEZJQ2xvd2NjRHBVeDBEU19TR1VvZGpzWkpxbWh1S2RSUmR3cUdpMtIBhwJBVV95cUxONzNDVGhieUVpZko3WnZXNGJUWk9XWHNiUTFGSXp0VHQ5by1XaHNiUW9DMVFBUDZtclExaGY4MnpNWThweElzaEVUSi12MUhSOGtHaUt5ZDBadU1TXzR1VGcxQktCVW84R0dFQjlpTzUzZXVUaW1uTW5nQ09USUphV3dqZHg1RWFibTJSUjRYZ2YzLWFDZFY1VnRxU2x6cVJIT2RIZDUwUktnZS1CaVVoa20telpJS1NjSmdMbHM2TXdWNkdSUXVMMmpuMkpfQmloa1AwTG9aNkI0am4wVDB6M1FVM0lsQkhKX1NqM3ZUWVFzcnhRUWhweXhMUjItNG0xTEtCUndRUQ?oc=5", "src": "Infobae", "ago": "hace 54d", "ts": 1773126000}, {"title": "La Uni\\u00f3n Europea propuso prohibir las exportaciones de componentes para drones y misiles a Ir\\u00e1n: prepara nuevas sancione", "url": "https://news.google.com/rss/articles/CBMi_wFBVV95cUxORGYyY0M3N0JxeTBaVU5lNWUxVFpuYmVBcjNFVFZGdEg1YXdyOG1fWjQxd0Nwbmc0RmRSVDAtZVRrMDdXcmxTZFZyLVMwNjk3TnpPNTNWcUV1ZDMxMWQwaXFXdlBZVzRFSlM5NmxLaUwya0RldFRaTkxRS3M5WGRKZE1rUWxrQ2UzRTQ5NXM4a09KNnlEN2ZKVUlSV2p2UE5YbkZ0N2pteWlhYkFKQUtPYVA4V05rXzhQWW1CYUJnT25NaDloR01oa2VSdFhpWDdUUXV1OXZPR3VxUTZvRWtGcVJncFZSVklFTFJaZ1BoWjNHbDlwdjl4eFI3SnlBeTTSAZoCQVVfeXFMUFN1Q2tHcWdEeEVnX3J5UF9FdlJvdWh3THIySU1zclBJYlZNc0JxVnFSOGFIWXc2Q09pVk0tTUxqSDNNSmJJZ2l4VnFkaDd4SXdnVmVRUHNGajRGa0hMMzRzenJ6Z3FCbFo2WGVWN19kNks0QkIxaU5yN24yN0kwN19NRnQtRGVMbjJNS2kyMUtrdnlQQURvZzhjRnl1MWg2T2daZ1o4cFI4LWhRbHQ5cVFXcTlJWkg0cjZPLVFZeUg4NzRfTFBzanNOekg0YklqT2V6bHJrQlpXT0JXLS1kY1hReTBPaHVZUnBfWnBjWFBodmcyOFh4Vk0yeTJxS1dWeUJrWjM3cDBudUZxbjhsSng5UXZGRXQ3NjlR?oc=5", "src": "Infobae", "ago": "hace 103d", "ts": 1768896000}, {"title": "Zelenski acusa a Rusia de buscar que la guerra en Ir\\u00e1n \\"se prolongue\\" para desviar la atenci\\u00f3n de Ucrania - Infobae", "url": "https://news.google.com/rss/articles/CBMi7AFBVV95cUxPRzAyWWFtVExzVlQ4WWpXeXMxbFV6aEluTm9kWnR3Q3pJWElRU1JXeXg2STU1dFZOems3enk2WkRlN1puQmVwT2hkNDlWZkpkZU1QRkM5U2RRZzlBLUpGN0I2TmhQbDd3TXBmZkF2Z2F4RXNCbzRvTm54QzdsaGdCREtGRUZSNWxqMDduSVBES0o5aFNYdkllLUFST2dQOHRBcThuTDlnLVZYSm5YWHFIaXZ6RWhFRHNRTDFUeWtFYWVhaXZnR0pKQ3BMU1ZncmtaZnd4Y3ZocEF4YnVlVE1nU0ZlYW03bkhWeFEydtIBhwJBVV95cUxNajMwWmJjTGJ4VGRIUzYxNnB3VHN5TzJkY1JGU2FfSGNvZ3ZWejZtUjBTazE0c0VhQ3p6OEdnWlRXb3hZenloVUIzR1I5M3g0RjFkRHVCeS1tMFRkVTN6WFJNZk9ZN3A0RnAtTnl6NkJtZUUzTmJMOExIS3BFVGpaUmRweVFveWVmYlFOQlBXUnM3Z2Vkc0k4Ty1KOG5taXV5OG1jR1c1dDNIZEZqcXdhZ2JTQ21ieXNGV0JwV0FvamJ4OTNxb2swbHBzRnllTGNOTW1YdGtNNWlwb0w0aU1BSUhTSkV1enM5N3hTSFpoUXotcWNhRURhOWdCVG1FMU9BVHZPMG55SQ?oc=5", "src": "Infobae", "ago": "hace 33d", "ts": 1774940400}, {"title": "Trump y Putin hablan de guerra y paz, mientras EEUU sopesa suavizar las sanciones al petr\\u00f3leo ruso - GBM", "url": "https://news.google.com/rss/articles/CBMixwFBVV95cUxPai1KclRLRVFnZmJsdGFVUmQ4V1BoTVhIbFBRb0pDSmtPRVRRQm5ybmtSNkxsdnhqcDZET0NLNGZOS08wampfMXlRc0tMcm5XUzc2R3V2ak1zOXFFeHJJWXYtYURZYWdkY2UxM2NrTHNaaFNWY1hyNzRqQU4zQndxZG1vQ2ZjaTlTMEpSZEs0dVNkVUR1TnlybGc3VHlNUGJ4eGx2NV9JSWdtTTktblZVX0xaS2VncUtsaG1xYTdOd1ZTUE5kNkRR?oc=5", "src": "GBM", "ago": "hace 54d", "ts": 1773126000}, {"title": "Kallas pide mantener el foco en Ucrania pese al conflicto en Ir\\u00e1n: \\"Ucrania no puede desaparecer de la agenda\\" - Infobae", "url": "https://news.google.com/rss/articles/CBMi8gFBVV95cUxQUUlDMFVoUkJPQnpLY3BiRE8xcVFZUUFuYThsdW0yUWl5TncwOThKR2lwY0REMmNJZm1lUDVKUVFCTW5LdFhLS3d4Yk1SbkZsTVg0Y0luT1JMR2p1Qk1IQm5zcXpGOGtOdDI0eS1GMWlzbUR3UEd3eV9lNHlVRnFEMlpZa1dIeFd3ZUlzNlJSeHFqaTdaQVJWWlpmQmlUQUZjTVVnSTRVSXpVdHEyQk9fd205ZUJycnJBb00yS01UWVUtRjg3blVHalBVaUtqQzBrTUJrd3YzT3h1dDNYRGpjdHZhTzlGbzNZOTFvZlVLeFNTd9IBjAJBVV95cUxNNDctLUc1dVU0ekFfS0ZuZU5KTjJSOVV2eTdiRHdFU1hQS05iVVczcGV6bExFZFJXSjNYZ0MxRURaR0tIUjhoYjVLNkh4X0RUNS1uTGVWSWxiMUN1SXdaV3dMWVY2MVJZczFYVkIwT3FmdG52R3dHTmg0R25SUmVqWXIwWGZXLVcxbDN2eFVDcVZYaWxfNTczdDBXaHNYN1JxcW5CY2ZpN1diOVpKTWxUMlQ0a1p6WkxhdmFvRjI4ZTlDOElIUmJZN2stc0ZSQTV2VHNlcU5vMUNMbVVZVW9ibUtzVWlJWE5wRmozbHRKSmNNamF4MjhoX3RjUEloTHNLYVBrdDRVZWVGT3JV?oc=5", "src": "Infobae", "ago": "hace 60d", "ts": 1772611200}, {"title": "Las claves para entender la crisis en Ir\\u00e1n: protestas masivas, econom\\u00eda colapsada y tensiones nucleares - Infobae", "url": "https://news.google.com/rss/articles/CBMi5gFBVV95cUxNcWJYVUE3WFppMzgyRjkyMGRYNW84VGlGeGZIUWZXRWx5M2xPaHdFVnNUc0FmM2NVT1RMZ2lDeGowWmZFb0Jsd21iZldkbXV5YWVrY3YzOXNPNlFtWjl6VDlVWFVMRGh4S0FzWTFlYkpkQ25WV3YtUGVzZkgzREU0SWR5WGJqWmRLVWZqbDR4MUpSQkIyUlFEQkNMZDNwemtTOUF3MWVaVUh2ODkwTkhGYmZDNzBHR1I4QnFIX0k5LTIzTkpTcDM1NmluU1Z5NG93Z2Ezdm5tNlRvaGJhM2pBV0dwNzZYUdIBgAJBVV95cUxNVU5QVlhacjZqUDlOYmtsQzlvSUVnQkFORlRCZkRJQ2lKMDJudEVfR0VrM2I2aGVvZnJoaU9sUE9FQzU0TGVqR241OWYxU2t2TTBQcjlheDZpclgzZ1NOcFdILW1KNUVKY01GbHU5d0JwcmhuQTFTU2dvQU42YnljLVE3VUlwbngyLW9jNUJNWWJVSGhKcFBGQTdLYnJZVzdyZW0zcG9xb3ItaXhWUllXVE9fZWJBZ3NrY2dVclM4N2ZXTFNmSXBLRUJfMWhybjUtVl9GVGNqSGNwUy1SR09WSlJYNGV5dlRuOEk3VlRRVGg5R2UwWGhoZGp5NXFsM2xN?oc=5", "src": "Infobae", "ago": "hace 115d", "ts": 1767859200}, {"title": "Trump y Putin hablan de guerra y paz mientras Estados Unidos eval\\u00faa aliviar sanciones petroleras rusas - Forbes M\\u00e9xico", "url": "https://news.google.com/rss/articles/CBMiwwFBVV95cUxQZXRwcVZXZlNvWWszV0VNOUY3WHF0djZVVDM5U2VyWXRueVJacFIyVjUtTzFxbnFONk9vUTZPSGZPeXFibllBN000ZU5rR2hxc3FQcGhPU3hRc2dYVm1PMXJkRkRWT2RFOWZGYVFEM3RxUTRvMHA3NXh2WDRkSnZ6Y21uY3BhR0JEV1VyTTZDdlZNcGpPLVRPSVpKcUk1QnVrdmVDTi1tb1Y4V1hFbmE4akxRVUFZa3hBYmRrQXFTdmYyRzg?oc=5", "src": "Forbes M\\u00e9xico", "ago": "hace 54d", "ts": 1773126000}, {"title": "La FIFA analiza a Ir\\u00e1n y Estados Unidos: \\u00bfSanciones y adi\\u00f3s al Mundial? - El Comercio", "url": "https://news.google.com/rss/articles/CBMikgFBVV95cUxOeG4tU3N0SkxxLXZndVk0NDN5YnVhZUdHNlVLdnIwYWROUDhINXBDSFNPaHJsRElOVld5U3FMeFBWbWd0MFJ3Y3k3TjdjUjdUOE1VdldVUzA0U0lhRjZudGJoUmZDZklSWFM3aTlWVjBqd1BpOGJfSmhZa21FUjZ2d0t4U29GN0pGSlRGQkN5c2tJZw?oc=5", "src": "El Comercio", "ago": "hace 61d", "ts": 1772524800}, {"title": "Trump da a Putin \\u201c10 o 12 d\\u00edas\\u201d para resolver la guerra en Ucrania o afrontar sanciones en forma de aranceles - EL PA\\u00cdS", "url": "https://news.google.com/rss/articles/CBMi7AFBVV95cUxPV0ZkbHFQYkd2UXFaUEZBS2Y1VGRaR3ZBZFhpbUVjTzJRRXBCeUwzaU84S1FOZl9KRTByS3BqWXdnWmhwUlNtSnB5TTdSaS00ZTQ2WHlLTGFMZ3Flc3B0M1N2TUhIQmE3UXRXWHYzeDlpdWV4eWllVHJoei1mMWRjc1JZNXlEeVhmTXp1MUpmbGVqN2JNQms5VzNXbVctTUtOOGVsS2hkTDAtUGRRSkx5RnRlZG9PUXNiRnJ3MllENVdwVVRKUEJ1QVpwQnhLMXVkU282UTZmb0lDX1FOcy1sVlRoVVpvR1VjUm9lNtIBgAJBVV95cUxNQjhlUk5DN0dUbEhhX0dCU0VDenZsYV9icmtLVUthS05idzR4ZmdzSi1YZ1B3OHlNMHhNclN5R3dqMkxqT0dwdnRBMTM5eHlBbVpjZXVsajZXVVhhSnd3N3pDSXM4T2thQmhrdmprNmcwbXRzUWotUW9SNUtjcDRTTEJiRXFDeTZtTEdmWG91UGZtOHAtZG9fdzdfYWI2QlJyaEg2TTFGQklGMHJKSXhmY05qQzgyMkUwQTY2bDNMOVpsaVlud1Q4b3BhQlF1ejFjdnF2MDdrdDN2LXFaLV9DWjZETlNNTngteElzdGdQV3lqZWx0dGNlUnZ5RXJlbmxI?oc=5", "src": "EL PA\\u00cdS", "ago": "hace 279d", "ts": 1753686000}, {"title": "Resumen de la Guerra entre Ucrania y Rusia el 14 de junio | Ucrania y Rusia canjean al tercer grupo de prisioneros en el", "url": "https://news.google.com/rss/articles/CBMiiAFBVV95cUxOLXY0N1BWUUs4VHlRMTdaaDNVUWt4WHU0enBSUEcwcG1MSVZCdVBCc1k2R1pPeGY3MGdUQzhHdko3REMwYzlxTm9yZ0lFbVVhc3otVkVVeERXWnlXVEx4aWJqY1p3NkZFWDRuMGVhSGxOS1YxUlB1UmhpMjBIcGxZckZTUXVyV2tY0gGIAUFVX3lxTE5ZVkJ3RTNaUTZNcjcxM2hfSW5Kcy00cUZnZGhsLVdRRHJXOTRNcmloR2Z1bllNWG1CZEg2OXdaVVlEQVpSVzlzajMzdmVmQ3BkbTZWODdmWVhRQ29UcXRXS0FLTjdFdVpPYnVYVTctWmpfWXZoaDBwbXpiYjZPckphbkVZVGJkZFk?oc=5", "src": "RTVE.es", "ago": "hace 323d", "ts": 1749884400}, {"title": "Fluctuaciones del petr\\u00f3leo ruso y el efecto de las sanciones de la UE en la guerra en Ucrania - UNITED24 Media", "url": "https://news.google.com/rss/articles/CBMi8gFBVV95cUxQSG1FMDFYT1A2SUlzUzR3UHlVeXdveFJQdFJQSl9seUNBUDlvbG1oR3V2Q25vX2EwNVd1T3RCd1FfUVY0UzhvNWhDTERBMkgySUJQU3ZUeHJuYlhqS29RR3R0SGtsdHh4SnB5S21faDZ1X0k1NFZzZW0zYnJyYlhaUW1sSjlfRHpiTVdOY01MLVlYUExDTU02VkpjTXZPSldJSURTemhpQ3lqeFBFNGdEcE1vajFjaWRNLU5kZkZNRlFaUHA4N21QUFd2SzROZ1d5RDhkaVY2WEJ0STNaMk0wX2h5a0w3eVRVeW9Tczd1aXRmdw?oc=5", "src": "UNITED24 Media", "ago": "hace 307d", "ts": 1751266800}, {"title": "La simbiosis estrat\\u00e9gica de Rusia e Ir\\u00e1n: inteligencia a cambio de drones en una alianza que complica la ofensiva de EE.", "url": "https://news.google.com/rss/articles/CBMi2wFBVV95cUxNODhRLVZvdVFZSktlbF9EVmJGckdBMzJrYnVpQ3FMQ2ktUmttLXZoMW83ZGhMUUdqTzRQZW5MN2JFSWxmS0dZMzVhUDRBUzktQ1U5cHVuZGhDMnRBSmotUlpRNFBrYkw5NFg2U0dNZzA4RXVPOHZIZzBZMHJ0cTA5dDA3NnlhbG1ER2tsRW92ZEhCUUNQTUktR1FhRzU1SXpVd3JGelctUVNaVVk2X3FlcHIwM0hjdnNaZGhDdGhST2twQ3BpSWw0czZYdmZqZXladGM4Q1ZWRnVWY0XSAdsBQVVfeXFMTmFwWUJCTHNWQkQtZ0JFT2VUSnBzRWJtS0c5MjNZNXROZDF0bDExWHhwNmVhSlJEUEdPUUNNd0dJTW9GV0QyenJTQndsTC1lRXQ1QjExYlMtRnpVSW9SZ2k2U0VmNGVBMWRRbnhpUHVfS2ZkWHpyMDcwV2V0dEYxeVlqYmlRcDh0SmJOVG1NaVJxZE9tU0VXRU1MQ19QWWYtaWNCZHdMTGhLaFhlZ0cxWkFwQlVMT01sTGZidHJhQ2NGY05ab0pIV3lKem1wODdhcWlFOWJEVmQtcU9v?oc=5", "src": "RTVE.es", "ago": "hace 53d", "ts": 1773212400}, {"title": "Ataque de EE.UU. e Israel a Ir\\u00e1n: \\u00bfd\\u00f3nde est\\u00e1n Rusia y China, los aliados de la naci\\u00f3n isl\\u00e1mica? - BBC", "url": "https://news.google.com/rss/articles/CBMiW0FVX3lxTE9Ca3h6UVM0ZTYxYm9VUjduanpmMW9RN3R1ckNYZF9fbC1xYU9KT191TlhQc0ZOZHYxaUxNbmVCYzhaVkhBRm9KSUUyX0poSjFnMGp6NFZ0aFBvSWfSAWBBVV95cUxQa1dReWZlQ3ZTVk0tMHlzUTBkM2dwSTJ5VzAtaXFaNldTejhNdE02dkpSYS1hY09tc0UwR1lkYlc3VVhmdW9fM2t3TU1ZWUN2bEhHM1cyaUVXSVF5a29Rb0s?oc=5", "src": "BBC", "ago": "hace 61d", "ts": 1772524800}, {"title": "Trump da por \\u201ccasi terminada\\u201d la guerra ante la escalada del petr\\u00f3leo - EL PA\\u00cdS", "url": "https://news.google.com/rss/articles/CBMixwFBVV95cUxOMHF2Wi1NbFhIMTAzeFM2QllWRGx6Y3U2M2RjV25FWjhmWnhZdVFRWTVEUlF2M1ZzZEtYV1dEcUp0VDktNTllT0llVDhRVW5GR3BhLWo5cndyS3VGMmlWUmRkWnI2bHRzVExYQVNJZW1QMXhGc0RjdU55WXcxbDgtcHV6YjM5ZmJNSGFzYWhvWlh0ekFQb2NhX3kzWTRtX1dOdzM4SmZrczI1UFQzNGtqN2I3OHd0dW1VYTRSVnJGcVYwbjRQdm5R0gHbAUFVX3lxTE43eHJ6YXZycmotZXZSM0tsRGUxanhrV1hIbTFMUkdtQ3AzWThCSGtldjhiQ3NqX1JveG5wMW5yWWFYaDBkQjF3dGJTVnY0ODVuSWFFT2ZRMWtXSWpVMUdlUDRWNlpxNFgwRDlycTdmVFdaUWY5THFGU25qLXo5SUNSM1hsczhfX0dyV25YQjBDM0YxYVZleU95aTVRb3RPdnpSdjNLMHd4enhoWXRqVFBoYVhpWjlLX0ZESWlPOFZqOFVZUFlnYTh0by1fVmpSS21HQkQ0TWhfVmFobw?oc=5", "src": "EL PA\\u00cdS", "ago": "hace 55d", "ts": 1773039600}, {"title": "EE. UU. dice que podr\\u00eda retirar m\\u00e1s sanciones al petr\\u00f3leo ruso para mejorar el suministro global - France 24", "url": "https://news.google.com/rss/articles/CBMi6AFBVV95cUxNYVNfYlVtZUdjdjRMaHQ2WURyMk54UUhRY3BhV3BXWkxCSlI1Vmw3RTJiMUxlay1GUFlZZklXUERHUUdyWXVER0p3WUNVMmZERVdHbWRmbnUyUFhuVU8xaUEzUGdtZzA0eUw2d1Q5NXRJZDVuQnozOTlKelFKSXlPOTBEakRlSzJEQ080LXU1MG1jOXREczBxTEszMTRVaWxuZ2dmd19Kd3NVZ3M1Q3NibDF6UkZjYVUxczktVEpxNzktbTItRm55eTJISlp5ekotZjdEd2tnam81bWJaTUxnYXRmLWdHQ1Mt?oc=5", "src": "France 24", "ago": "hace 57d", "ts": 1772870400}, {"title": "El peor escenario: los platos de la guerra en Ir\\u00e1n los va a pagar, una vez m\\u00e1s, Ucrania - El Confidencial", "url": "https://news.google.com/rss/articles/CBMipwFBVV95cUxPNnFPemxKWkEwMTNrOFV4UnBma3lIYkd3bEZIQnluMUhMTFVJM013R2Vjanc0aWlhQWd6emRWV253OU9Bd2VkTnpaQ0VmWlRxeklSNHY5WGQxZUJIdEM2QlRwOGRVTW5XRU45ZS1sT0RfY3B5bXpSenM0RFN1X0daSWJTSjVfUlE5TkJvSmIxWjVIRFp2cEZfSTFWWVhNRFlvZjZuRFNEdw?oc=5", "src": "El Confidencial", "ago": "hace 50d", "ts": 1773471600}, {"title": "La suspensi\\u00f3n de las sanciones de EEUU al crudo ruso \\"no ayuda a la paz\\", afirma Zelenski - France 24", "url": "https://news.google.com/rss/articles/CBMi3AFBVV95cUxOazdnUVYzVzB3Y2Jjel9makw4bXA3N2NtcXRXTExYYVlkbERuRy0wdWZuQ0Z6VVozdFpKMWZBV3lfSi1TNWZaT3RRVzdnVDFrcU4xQ1M1ZjVQZnR3OWYwbFpCeTRaM0d6UU1xYkRPbExZNUs2SUhkeFdXNGFXZmt3N3I2YjVVb2V4SWJRN29oRmpxa3NFNHowQzE1OVZfUHAtTlE5UlZpOFVCSlZub3BHSHBIVXFoSlRNdVdsQUJFMUt2MVZ2ZWhvRXRTcUtSQ3ZmWHNwb3RFOVNHLW9V?oc=5", "src": "France 24", "ago": "hace 50d", "ts": 1773471600}, {"title": "Conflicto Israel - Ir\\u00e1n: cu\\u00e1l es el papel de Rusia y China - BBC", "url": "https://news.google.com/rss/articles/CBMiW0FVX3lxTE03QUd5dHZ6U3lmd19ZOG12Y1RPd0F5NHM2b2ExRGZRckZ4bXd0Wm5JckYwQnZEYzZOTlotSXJyRjBpdDZIUGFIOE50N3E2Uy1DVHJHb0hiOVItMknSAWBBVV95cUxNX1JSTWFkSjc4TE93YUp5aHp2VmN0RmhoOWpocjE4bnhFbHNzR0pIOU1PV0ZydzJtMEU1RHY3WXVUc1BWeWdkSGE1LUQyT1JNNGVLZk5YTDFlVnlRRHl2YnM?oc=5", "src": "BBC", "ago": "hace 545d", "ts": 1730707200}, {"title": "La UE se dispone a ampliar sus sanciones a Ir\\u00e1n como advertencia pol\\u00edtica tras el ataque a Israel - EL PA\\u00cdS", "url": "https://news.google.com/rss/articles/CBMi3wFBVV95cUxQR2J5VlpicW8xcVc2SlkzMmpJVnRPUXlEc1Q3R0NaNHFWODg4TzhBcjRPUXVnc3FIdDN3enNYYjB6c0ptUEw1X3BpVlJBMXZUazU0Rm8xTWh4QzNvYXZXOGY1NVpJRHVxOUoxLW9TTWl2UHhUNVlILVVZdVh6VEwxa1J5djRiblAwM3JlTFJsU3ZnUXU1VEF3WkFiOE9jb2hsLXQ3YmZGLTFFelJZZnVxQkpBX3dVS0x5clBZNmNCaHFOOHFVVUJCbmVLQUZ4VGc3NnNpNXhVcHJsOVAxVC0w0gHzAUFVX3lxTE1TZFBiaWlzWWhpTGlxZEJpaEEtek5ZNVVfeHdDQXZpUDFLYm1XUGNHczVJM09hLV9uZjFzdjlXdUg2VmFPeXNHVlNhZFBZR25jOUJQem42SVd2cnVPSGVib1NEYVpHODBoVkZtUWhzbjViX1RhNDYxNmJ2cTNRODhmTG9kYjhpOElMdTJ2UDRRNjZkcmtOcVg4ZmpXRnE1ZmRzNldESmd3YW0zVE1kMGphSUlMUTBqdjd0eWQ5b01nT1Rrdy1RY0pwTXlRYzhGWW9JZl9BVm1tUklHUTduVXVZSUw1NzBnQjJwQnowMVZ3SXk5NA?oc=5", "src": "EL PA\\u00cdS", "ago": "hace 742d", "ts": 1713682800}, {"title": "Israel e Ir\\u00e1n est\\u00e1n confirmando lo que intu\\u00edamos en Ucrania: la guerra sucede ahora a miles de kil\\u00f3metros de nuestras ca", "url": "https://news.google.com/rss/articles/CBMixwFBVV95cUxQRTQzT3dnd183bnZfT20wcjBEempsbUV3WHFQbUhHWmU4Tmw1SVd1NC1jVEtKZXVDU2ljcjVreGloWGNXRHBpb21zOW5ra2oyU21saGpaZ3lOZ3NGVVV4emU4VDBGMllNOWZKYjBlLV9MWWZCSjA3RmxwZHlQUFdQb1RfS0EtQXlKbm1ubVBYc1NEdTBnNWt2Y1FobnZMczBRTlFZRHJpdkxKUHV1YmRZbFlJU1NpNFAxbUZVajJJNUhYUXJTNlpN0gHMAUFVX3lxTE1DUDRnbFF4My1PSHd4RlAyOVBSbExuYzVFZ2s2b09wd0Q3bkR4a3RBM29XVE5HTnhHUDdvUHpmYkdMdnVWV3RxQW4wZmJYRjlMS01YTGJfeUN4Ynp1djVrcHJiQVpza2VaSk94Tmo2dW12aGM1aEVBZklsUENaaFdaWWxTd0RpTk1CRVpSaUdORWhJTkVjWUFzQjZxMi0yVmdRNmVnMXRjbnpYYXdvRjRsclJQYWJyNWp4bFRlVWhyRzRWMXc1ZVlDN2REdg?oc=5", "src": "Xataka", "ago": "hace 314d", "ts": 1750662000}, {"title": "La UE impulsa nuevas sanciones contra Ir\\u00e1n - European Newsroom", "url": "https://news.google.com/rss/articles/CBMigAFBVV95cUxQQzBrVHdHcHJRWGE5ZzBVaFRCcENCN2Z6aVhxOXJUTzhWRjg5ZmNveUtVMnFUTFRqNFU4cVpkWWZ3eVRoZGFPUWV1eEFlT0Z3V1JxeURkek45OWVIcF96ZnVjZDF3eGxsM1AwNlhjbEZVTEw0VnE3ckk0OGhWVVJUYg?oc=5", "src": "European Newsroom", "ago": "hace 739d", "ts": 1713942000}, {"title": "La propuesta de 10 puntos de Ir\\u00e1n exige el fin de los ataques y las sanciones - Infobae", "url": "https://news.google.com/rss/articles/CBMi1wFBVV95cUxORDU3OUNYWHJXbDljRFVfZUpjSE1oTWhaSnp0bjFYN3BCbWU3U29TNEdCNmlSNGFLSVZQd0sxZ181UFhCeElHNGw5ODlIZmlzbHhFemRIMVNqeEhvazBhTDdOaHZhODBvNGVvcy1nSDk5OXp1VHpWMXRvNVRDb0JncFpEelVONWxmYkhxa2FwS29pSzc0X0E5NkxFT2JQZ3BqMWdoRnJpa1BnNHhuM0lkeG9FU01lZ2RmanFKQzQzTVRsRXJjOGp6LXZuWmlieEJWNWhhYUU3VdIB8gFBVV95cUxQYmlvM1d3NGY5ZXNOX0g4dzgzVGZYUnFqTFVVOVh6aTlUNGR3V1U4RXRqUldjUE5tM3VjM1lhSkE1Tk42eGpVcDdTbGt1dUF1SmlvV1h6NW45T0JNRlJtMjAzNGJCSjQ3UHRYME1ncUxhSTdoczNzQUNGM3BHYnBtT01NV2c1cnVaTmREMF9JNklSb25JRDFBcVBObUVqSFI4Z0w0QzhyYnNFWVdKVzFjLXdkUFQwdHNtTHF3UlJza3lHcmhrcGJlZjIwd2xTVFBRQjF6WlpuWXg5WERYSlJQZzVGN0x3aUF5TnRuLTA3RE81UQ?oc=5", "src": "Infobae", "ago": "hace 26d", "ts": 1775545200}, {"title": "EEUU baraja \\"retirar las sanciones al petr\\u00f3leo iran\\u00ed\\" que ya est\\u00e9 en tr\\u00e1nsito mar\\u00edtimo para contener la - LaSexta", "url": "https://news.google.com/rss/articles/CBMijwJBVV95cUxNd3l1R0NETkdqcXU2eFBobnZKNi1tWmpxMWZNTkV1cm5ycGFJUmRkVldLWW1PTHplVnh1aVJJWkgwVDNRaFFrQndxYW1tQ0VfNzBlRlA1X213cVAtNmtuWXZxOFJWMGZQS3VwTGVKcjFZYTRidV9XbzV0TFNlbGMxVjBKbDQtakNBaXZCZW1DWUc1c3RGOGl0eURnZkVJMEZ4M3o2dk9lUC10aXZrclZ2OHVsY01vTnZUaDFRcHA5YW5Ga19ycTF5WXhMcklHUUp4YjJHLS1TMDlRMC1SOGh0WHdWbXRURDJVS25sWk1acGdFUEdzQnp4aG12SlhvYS1mcDhxX3lyVXRMM0M4Z3hv0gGPAkFVX3lxTFBfdExyWWRqbUlOWDlNUVJwRDJndHhMSWV3cXE3SHpyXzAzcnA1M3FBQ2lvWGFXV1BUSnpHU25UZUdHSmZFdVBWZ2FuN1NiZlpxenlMSDBOU1loa0p4ZG8yQ2w5bHBlMTZmTUkwTWZCSVZ1Y0VPQ0hBVWlfcTA4VDlCMEN1VkpIU09iWTM4NGJxWFU2ZXZ2RmNoZXRYdkRGVnBDMV9maXBsU1dmaDRsLVpBS2lLSUdDTEg2OXh3ZUsxeE9oblk3VXF6WmFrZXRNcmp6WFZrbnF6OFJJdENXU280YXdfaVRkSm1tU3NrZ2ZCM3N0NElIUHV2RWxvRndER2dFT0hoQ0VyNkFwNWJ4clE?oc=5", "src": "LaSexta", "ago": "hace 45d", "ts": 1773903600}, {"title": "El ataque de EEUU e Israel a Ir\\u00e1n ha hecho subir el petr\\u00f3leo. Pero el precio m\\u00e1s alto que hemos pagado por la gasolina l", "url": "https://news.google.com/rss/articles/CBMihwJBVV95cUxNOGRLcG1yOXE5VWdsVmZPNHBwcWNLNXdmNGlJQkxNTldaODJXWDZiU2JYdWQxQ2NseTVxTFY1V3pkSlp6UWR1VTdPN0ZVc0h0d3BGZzFaZlQzMDhsdVNFbjVOb0tyVjNmY3N5NXBHQko0N21VZWF3ejFiZ2lyTDBNM3AxOHVwakV0TkxUMF9QazJIc2gyQVVfS09ZcGVPTzA2RGY0eWhhY293d04wSDcwcl9sYkU5YTRac3l0OElaYVFmbEVOVUY2V1MyQ05VczFaczJMcmRyaGw5dnh0ZXd1Vmt4NVRnUXRyY1VOd3Z3TEJuOWxDc2JwZ29MTF9WXy1MZV9oVHhFQQ?oc=5", "src": "Auto Bild Espa\\u00f1a", "ago": "hace 56d", "ts": 1772956800}, {"title": "EE.UU. autoriza la compra temporal de petr\\u00f3leo ruso sancionado para combatir la subida de precios por la guerra en Ir\\u00e1n ", "url": "https://news.google.com/rss/articles/CBMiW0FVX3lxTE0ydEhlSVUxSXRFalkyenZielZxNTRUWEdjYXZHb3lOTW13OHJmanctdHFEdDlFcDhBX2Q3dHBzbmJZcXppUUwzejJ5RzlJeFVfZEpXNkhHSnRLMkXSAWBBVV95cUxOMUVHYlM5Y25Mc2FWTnR4R3YwLVBVaHdRX0lMTjBodUFfU2VhNUFNSkIyTmNqOWJqVlZfSWxPMURlVnBwSHBfUjBBOWFacjFqeFJ6SXNmUHJVZ0NkTXB4aVo?oc=5", "src": "BBC", "ago": "hace 51d", "ts": 1773385200}, {"title": "Dos semanas despu\\u00e9s de iniciarse, la guerra de Ir\\u00e1n ya tiene una gran beneficiada: la industria petrolera de Rusia - Xat", "url": "https://news.google.com/rss/articles/CBMivwFBVV95cUxORmZZUE5hd3FhY0Q1Q1lrQVZvVEo5SnM2VG9hN2xyTHhwelhhX1E2UHlBckRGdDRPTHlFcnNBeFZ0U1pIcTc5V2Z2YjBJbC1ZZmtMNlpub2o0cHFacm1TMmN0UGZCX0xFUVB1NXM0R0NzbG9ocWZBdkRtUDJ2ZUhkaUMwbEYwNDFZRWFOLVdTWXNuMmhXYmI5MUIyVVZCMTVsMXlROWhvTkpIY09iTlU5S2ktQjM2T21nQzhNOWJ5Z9IBxAFBVV95cUxNMG9WM1FVYWh4bkRGVGVUZExFSFZ4SExieWNOd0tYbF9PamZ2MFpvWkM0Ym9kOWYxaVlqV2I5T3o5ZlJYZmZocENuMTN5ekpVbGZ6ODFUeWRRMHBmeFlhbm9KVWR5enRvWDlvTVcweE1Dcm5KdkVNejQwdG5SWm9zOU9RV3l5X1plbzR5VHhyaTNXU2UyLTRtcVFfaWp4TEZadThhbFJjVFJ3d0VkYTc3Wm9nNU5TUE1KczNUNHlhNUVQRENp?oc=5", "src": "Xataka", "ago": "hace 51d", "ts": 1773385200}, {"title": "Qu\\u00e9 podr\\u00eda pasar si EEUU decide atacar al r\\u00e9gimen de Ir\\u00e1n - Infobae", "url": "https://news.google.com/rss/articles/CBMivAFBVV95cUxQY2FURk9fTHhEUUwyNU9oY2d2VVFkbFF0VUtPNmp1eUxoTjZSUVMxLWNLaEVhZ21faVZwdzQxbTlwbGZoMU9jR0lrWXJYaFU1R3B1QTFVV29zWWVLYXhZby02eFppSkhTYjJLa0lTZkp1Mk9UZV91UDVJOUFUTXZQVWt1Q29peGRlVFFBYXhJZjJEM3dranFrbi15cEZiY2pwTjJZbDB3WElQX0pGdHdQRFphczhoSGdIbkFnbtIB1wFBVV95cUxPdWk5cVJRTUViLVhERW85ZUJJc2tWaHBkZ1IyQnNNVG5qbWc5b1Fsc0tsMG8zc3BZQ0tJSkJvYUQxNW56cUxUTFpRbmdkelRIaWFFYnM1ZTN3LU9wRm5uRmk4LUQ4b3FIVHhxLVFrNWwyMGlCTjZPYWtXSXFHZnJ6TzMwX3o3dDJ0MUt3RUs4WkQwYXZnVEdKMEhMdXQ3eGtkYkVLV1VvVWdwdkVKdWJUTm55ZzZSWUtNaFdNTnIyOUpNUUNjRGVXTWZkM1pxTG80S0ZLSW1kMA?oc=5", "src": "Infobae", "ago": "hace 316d", "ts": 1750489200}]'
        _trump_json = '[{"title": "Trump uses Supreme Court ruling that weakens minority voting rights to improve his chances at the polls - EL PA\\u00cdS Englis", "url": "https://news.google.com/rss/articles/CBMi5AFBVV95cUxOTENwcm01enktd0lOTFdERDY2Nmg0b2VSOWEtRzJfSDFaQ0dfYjlrblRNQTJzSnBveDgtRHVrVDBQR0Q4YjQzRnptMk1USExXNS1nclN4NFdQRjNBVTlzMUdqbjE0ODA0VVJ0YWgzWHdmNG5VMlh3OXJsdVEyMXBfTWxrN1hDTXlSMG1VM3hnRXJmQTJsT3NvN2V6YlgxdkQ5cnFmYmw4QmtGN0JYZkIweHAycTJfeTZGVnNEN3dCTmxKZTFodjJ0TlNGVGI1NkRMaF9BTWpiRjRyUjZGZTRPX3JuMjPSAfgBQVVfeXFMUFNHb0syNVI4RHgxZGFCY293NmI3U25VVXMzTFg1REwxN1VNeUxYOWlIcmQ4QVNvOXJhYi14YzMyMXd5QUl3a0JwQkhXWFU2QUtBTGJHcjZkODMtYmNVZ2x5Z1pDSEVDbGtxT05IbkwybGxQRGtuT0x0VUU3MVdrakpHY19uRnFRQUFVSmxWMktEdTZOU1VSa1JBdjBXYlhqSm9MdFItdkhNbzFrU2pFT1htVGJrZ2VGV1JwdXAyZ2tTUHhSZjlEZDF1VUpxRW9kOTJKRnVOYlhSMXYtWXp5SERJenQ5aGVMejBXTEpqX2VLWTlqUTJQRXo?oc=5", "src": "EL PA\\u00cdS English", "ago": "hace 2d", "ts": 1777623263}, {"title": "Trump apoya la idea de cambiar el nombre ICE NICE - Fox News", "url": "https://news.google.com/rss/articles/CBMigAFBVV95cUxQQS1SM1F0QnFJRFZkc2lwSnR6cHdHX2pOTm9Da2RwQVEzdm01N3RuQ3BDcFFWU0tlY1E4VGwwM1UtUHNwQXUxQk9HcDlWc1BoUjRqQUhlSzNfNmlLWEl2bUYyRGotQ080RkJOblZySjNzaU9QeUt5TEx5OXc4amZVcdIBhgFBVV95cUxQOXo3R01Pb1Vwb3hjVEZGNy0tOEJqRU9MN0xQRnFJSjl3Yy14U1hWN0JHOG5Za05ic2hZUnBfUTg4eHFlckZmVktBRTMtRnZpbEJGMmh6WS12UHJDQmZwQjNFRmZwcUNsN2tFTWcwS0oyUXd4R2FaTnNRWmg5V0ZMS04zd0tZQQ?oc=5", "src": "Fox News", "ago": "hace 6d", "ts": 1777283617}, {"title": "US and Iran announce Strait of Hormuz open, Trump hints at wider deal - Euronews.com", "url": "https://news.google.com/rss/articles/CBMiqAFBVV95cUxNaFJudFR4WUNIeDhkbVpBU2NIcW1DODJtcDhiM25oOVoyMWZ6OEYxaXRZc1ZuRzVpNUFPc0JNVmFFYkd0OGg3U3FUekd0cExzekdkT1JIQ096bW5EcmE2NEdPeTl5NV9qa0Eta1daUlQwdjBkYXZwSWNLWjdkX0JEUjBZWEMzRjdGQnBOa25YT2NnZnRxSTBxekE4Tmk1MEdVcHpldUItU28?oc=5", "src": "Euronews.com", "ago": "hace 16d", "ts": 1776409200}, {"title": "Trump says Israel and Lebanon\\u2019s leaders will speak on Thursday - Al Jazeera", "url": "https://news.google.com/rss/articles/CBMipAFBVV95cUxORkVyTmF2VEwyV3c1SUlRbDlpbjNfUkRQeE9zaXZjLU1iNzFtN0FlYjljUVhwT1VfQXZPeUdubEF5UFhocXRBVXhRcS1vQlJfeS1JVXlxSXFnVFZiRmk0MTl1SmNVNzJzdk9IQVR3eWk3QXpadXBDdlpZRU8tblNVa0d6cHhEbF9nd2kyTWhtMXJMR2tQSG93ZDNncWx5TVlnLUZMV9IBqgFBVV95cUxNemljTVpYcWJJa3h4OTFwMXhUbV9paVNxX3RnczJkNG9xcW1aY3A1OEdwbVppNnBvYjRId0ptYlpmZE5tWWdzV19Na2wwRmZFUHJDUGFtckI2bUVlWFdBODRnbDV1OXdmV0kwSXE4Tk5pcU5CVzRsS1pYWmgzbnljNzhTN0c3LWpNWVpHeXE4RURqSWNPQWNwSGNJWlhDOHJVNWFBSjFXUUh1UQ?oc=5", "src": "Al Jazeera", "ago": "hace 17d", "ts": 1776322800}, {"title": "Israel and Lebanon agree to a 10-day ceasefire - NBC News", "url": "https://news.google.com/rss/articles/CBMipgFBVV95cUxOczFQSjR1cG9GRUhvaXBtaWl6VGZZQjlEdGp6OXMydzVRR3NHUE9IVl9MYWZVNXdhQW83bjRaU2dUYThKMlJZWTZHcEpzQnNmUGdNSWYyUUJkT0JJRDJUcWJCSEJ6S1N1UzF4UVU1N2JITjMybU16Njg1UzNjcW93Y0JKODlRNU9DOWxTMUlSQ1pMRjM2UUJNZloweWdVRjl3UFR1MERB?oc=5", "src": "NBC News", "ago": "hace 17d", "ts": 1776322800}, {"title": "Trump says U.S. will blockade Strait of Hormuz after Iran peace talks fail - CNBC", "url": "https://news.google.com/rss/articles/CBMid0FVX3lxTE9PbTY2UnlVRmhDNk1JLXJBYTlzUFBPVXZ0VDR5b3htTnpwTGM2bklzdjJZTkNBTGNHUHQ5RE5YNjl6NF9mWl83WVlOU0VqU1Y1SlJBMksxTU12ZFhkR2M2MTRJcVd2cDVVSGxBU196NU82YnVMLUpr0gF8QVVfeXFMT3lmemY2VlRadjc0WlRlemNuQ3pHNWlPMzFyMWZDMEtqUE5odEtNYWxTaWNRNUZQNXZKVXdMVU13Yk53WDZySUZOb1laVkhiVUlmeGtrTDJGeWd3c0o4ZWtJOE1oZFlzbGRMVDFmYjdab0xpMENXaVpWT29zZw?oc=5", "src": "CNBC", "ago": "hace 21d", "ts": 1775977200}, {"title": "Experts: Trump threat to wipe out Iran\'s civilization violates international law, Christian ethics - The Boston Pilot", "url": "https://news.google.com/rss/articles/CBMiYkFVX3lxTE93TGlTVElhcEhHdHlMSGF0Y2FHaUhDV1hzV21TMVdyY3U1akNHbmZlRVZ6SG9iN041TDhnV2hFNThSSjBfYklYWmxCd0lyb20yZEZOeHpVc2JpQU1rSnlaSzVB?oc=5", "src": "The Boston Pilot", "ago": "hace 23d", "ts": 1775804400}, {"title": "U.S. and Iran reach 2-week ceasefire ahead of Trump\'s deadline - CBS News", "url": "https://news.google.com/rss/articles/CBMirAFBVV95cUxOQWdMR2RQZEpSSnE3R1BPd1dPVVNvX21tYjhCbFZjcVJRMkozZVFxc3NKUFZid19fMTBZR2Zia3lhbmtLbDlXV21fSERfY3JNYkhEMktlNHZKVXdzaEk4UGlkcDBienpZWjl2OHpwQW9pRnBBaUh2aU5sQlBsVlNkM1FLLVowRXB4WFhWc2g3dmQxYjZzelJzNWhXRlROZjFmN2psUkJWbS1NcHF00gGyAUFVX3lxTE9YUXdxUGhSZ2lHV1p6cHJ1WExBTkFKRlgyQmZuaWRqMGFMTjUtamk2TnI3WGc0eWh5MkpNRTV3bEptbUhFMFdhTmlfZ1lMaFVBbEFseUxDLU9HdVNadkdBUHh1YUVuc1JKTzVJRTNLdXNGbGhYdnFMZlJmSlJfbUhoempHaVB2RjA3bVdFV1dvblpvUnVNRzFubFU0TTlNakk1R0xJTnIwNHFlcmc4VXhkZEE?oc=5", "src": "CBS News", "ago": "hace 25d", "ts": 1775631600}, {"title": "Trump announces Iran ceasefire ahead of 8 p.m. deadline - Politico", "url": "https://news.google.com/rss/articles/CBMiiAFBVV95cUxNUVRia3cwN0ZDYXJfb2FxV1I0NEsyNTkzUG4xZnFXR3pZMEhIWHFPdkR3bEQyQ2hUbGlsNlV2U3MtMXk2M1NrLTZGcG1aV3lwYzNHSi1FQUQ2TWd0eXQwc1dDWk1qSkhWVFJ4Z05zcm5CZm9lMFZtWVJwS2ZQT1lkeU1mZERLTHZZ?oc=5", "src": "Politico", "ago": "hace 26d", "ts": 1775545200}, {"title": "Trump announces 2-week Iran ceasefire after he\'d warned \'a whole civilization will die tonight\' - NBC News", "url": "https://news.google.com/rss/articles/CBMivgFBVV95cUxNeDVvMWphVlRaelExQXQyNnM2S2Q2Y3FVYzRqbUpEYVQycXpUUGMwN0ZCUk9rQUZ6Y3UxdnhTdExYZUtVWUNqWjBQSXBQeDVCWFJiOGlVME5JWFlidHlTSTFBQUhuQ2J3TGtWbVQxdU1DYlIwNHREQW1YeFljRzhfUHJNWUE2YkhLUGVHX2JFSDRtcUxYbFVxazE3ZDBsNlhCM0hkZ0Y3S1RFeTBsXzltbWNSVzNJanRRc05TT09n?oc=5", "src": "NBC News", "ago": "hace 26d", "ts": 1775545200}, {"title": "Trump announces two-week ceasefire as Iran agrees to reopen Hormuz Strait - Al Jazeera", "url": "https://news.google.com/rss/articles/CBMipwFBVV95cUxPakpsZDJIX0FnblhFT3dZdWo1bW4tb3c3MWxESkgwbGo1OU5yUFBuTk84SU83dzcxX2w4R3JOeWVvd1dydXFyTmZVcWNEU0Q4SzlLWjJ4dFJ1amFCSzdaM1dNYmZ1SnFsMHVDaHFDcm50NnF6d0JOZG1jOTk0cTZUbnB6cVlXQS1IN2FFcjRDSk8zcWQ2TG9UUWpmTWU3Q2xtYUFXNEEtTdIBrAFBVV95cUxNUk9Bd0laOGhzYjh2NTRJWUF6NDF1TTB3QzFlUlRiVXV3MG5nZVJrMDlzVEV5TlJQVncwV2Y0a0FIZGNURnV3OHZpLTN2dm5NZEdSSHpwbWNrRGJqYk94U1lLVW10cWhWemtFN3U2UUJ0a0Q3enBJSEo2YXdneGM2WHU2czVPWDZTUXh5OFRPb21ORWVydWVHeXRoaEVBajJKN0h2dW5wSDMteVds?oc=5", "src": "Al Jazeera", "ago": "hace 26d", "ts": 1775545200}, {"title": "Following Trump\\u2019s Iran social media post, could the 25th Amendment be invoked against him? - Dallas News", "url": "https://news.google.com/rss/articles/CBMipgFBVV95cUxPcUphOGlCQkV0TUcwQmowWGliOThSc29nZERXa2FlTHV1T0FkVDg1QUZDUHNHQVB1VFk4anNieVI1V1BaUzZGNTJzNlFIWGI5czBrQlhMU0xhOVh0b3UycTBDRkdtNV8tekhjelVzSFp4eHp5dlczZ18ydDk0eUlTN0lKNG5qUklXNVdHajFLWnZoWmdsaWRZbWtocm1rakxRYWJhVUln?oc=5", "src": "Dallas News", "ago": "hace 27d", "ts": 1775458800}, {"title": "Trump declara el estado de emergencia en los aeropuertos y firmar\\u00e1 una orden para DHS inmediatamente\\u00bb DHS los agentes de", "url": "https://news.google.com/rss/articles/CBMizwFBVV95cUxOaktLWEVtUUM4WGgzQ0R4NHBYRWpXUkFHSWNKZmlfUzBfbUlURGRnenptMnJpRWFFMXB0cExoVGpzMVUwMDdaU3BjMEZLZ1lXTVY3SEZGQmY0bU1jbGNuQnVMVzdfMHpacklXTkZmem1DSDlKZ2duN2pzNkFsbXFxSGVoOHZRWW9mNFliRzBJbDB6VjU3Y2k1bTZFSVRaUE5Qbk8wRnU4YW9VUFh4eDd1TVFQM2EtZlBGa3ZNczhwSHpYMGxhVjAydzlqYW9IN2vSAdQBQVVfeXFMTjU2OGFFWVJqeDMxX3N5dXU0TnJadkpnaEtuOTk2S1dlNzdGVlkzR0w2dV9lSDlpOE51VUMxWnB5Z1FGcjhRMDRBQ0kyclBzVV9WUXNNc1Q2UWhUWlpfTHhXN3dyUjJodWFTRy03dFZIam9tZUxjVW5xUUFPUVNTOUY0VUZhbVAyOUFhTTRwMzBZZlNPXzgxTU10cjhDMU1zVlhDX0d4M3hTUC03MktaN3RMOXVsZVZGcXFtTHhpMFdkUUd1RTNUblZfMEVwZ2tyaDBIR00?oc=5", "src": "Fox News", "ago": "hace 38d", "ts": 1774508400}, {"title": "Trump says he\'s granting Iran\'s request to extend pause on energy site strikes - CBS News", "url": "https://news.google.com/rss/articles/CBMijwFBVV95cUxNWTZ6U0ZzODN3dWZDNUdrZXhDMGlCdHZfRUU5M1A1WDBlejJBQkFuaWREUnZmN19xNC01T2xfX0t0eERxOC0yWnpBWGtYcVRGS3YwaGhhQzBFN3VrTHZXeVNlRzBIV0JPY2tMRDc0ZVJUV3BTUFhsRDMzTU5NcE9ibXMzUVQ0SllOUHpHVV9nd9IBlAFBVV95cUxQZWFwVWpMVG5ieGI2ZjlLRVR5WTRLYVFtQWlRZ0Y0NVA4NVptVTR5YjhLS1lnZW5aemZjWl9fa3FtWHhIdmNSeHQ0VGNDYWhrdEFSUE1WTGNVUUp5WXZ3LVJ4dy1aN21BUExvRmRtNV82UVhCS1huYXNuTGptcHlIeDN3cFRIZFVoOUM1dkp3dEpaRk1D?oc=5", "src": "CBS News", "ago": "hace 38d", "ts": 1774508400}, {"title": "Mattis se\\u00f1ala un \\u00abproblema\\u00bb si EE. UU. declara ahora la victoria sobre Ir\\u00e1n - Fox News", "url": "https://news.google.com/rss/articles/CBMingFBVV95cUxQTUplVGMzVzQ3SFp5OU5JOFduOTRVbkdlcFk3dHZTMjVZTjZpUExLNXQtRnhqMjFHSkZwWlRhNFpQbl9EWUVRSXJXTmNRLTYtMnVESWtpZTFpazFoOHlmNXM5SmdBeXU4R0pRQlFYRzAzR0oyRlplUkU1Q29PMHVDUzJDLWVrOEMxTy1rVU9FdThDb2ZsMVNKa0dEbGR5Z9IBowFBVV95cUxOVld1UGlRNkNJM1BKclFkSlVtVGdkYU9rd0U2UktFanBRbDVZdndfUkVSaUktUGNvRGpwS0kySWZQaVo2NVdTeW1rN1o4WXhmWHAwZE5vYWVNd25EaG5OSVhJbHo5dDJZeHFNNjA3c1JaM2dyWkNpX2hGOV9QSWdTdjJ6WG0zcXZhNG4za0tLRFpSNUdHZ2R5b3lQcWxJdEhQUVhR?oc=5", "src": "Fox News", "ago": "hace 40d", "ts": 1774335600}, {"title": "Tehran denies claims of progress in peace talks, as Trump declares war \\u2018won\\u2019 - The Washington Post", "url": "https://news.google.com/rss/articles/CBMipAFBVV95cUxQNUt2aWJIRUluMnc1SGRORkZpT0hnaXpvcGZJbmFadlo5ZWlWUW0wTnVxV0VZZ09DazliOVlYVHRsb0Q5Z0h3d1Q5R1ZBbFpWN2hMS2Y5MzVXYUJqUlpMa1JTZVZvcG9MU1dFT3MxOXczZml3c01vSVhuN0ZWMHZadERIRE43NGxkT1ZsZG9xS3RDeWFHSEZCSHJHc194THZ3ZXEtUQ?oc=5", "src": "The Washington Post", "ago": "hace 40d", "ts": 1774335600}, {"title": "What we know on Day 24 of the US and Israel\\u2019s war with Iran - CNN", "url": "https://news.google.com/rss/articles/CBMiowFBVV95cUxQNkJjaEpRejZ5aUkxa19iU1NhaE51VHRTV3pjdWdKWXIwMjA0TC1fQjE5bVpSMUNoMnRtSHFpR3RDdGNsbjZIdUhyMmJwb29UVVduTk9DTEdUbVYxaEhtc3hTa1RDd1p2ZVVhWXZqVklOQlM2bVZycHZ5a1B5V3g4MHdMQmFCdy1iV1RWZTBxNVNkX1pWd2xMUkQ1bDZadHpGNF9F?oc=5", "src": "CNN", "ago": "hace 42d", "ts": 1774162800}, {"title": "Trump dice que la mayor\\u00eda de los aliados de la OTAN \\u00abno quieren involucrarse\\u00bb en la operaci\\u00f3n contra Ir\\u00e1n, pero que EE. ", "url": "https://news.google.com/rss/articles/CBMiwgFBVV95cUxQa0VsbHZjOGd1akFuaFdIaTVYRUg4Nm9oN3JFczBEX2xVU1IyNV9wcnNXX2o0T2NfaGhOUFk4SEpmc2tpbldyZy1BdVpUd0NRYjhUMTBGR0N1Um9CU1RkWlFURkV3bTQ4ZEJCd3QzUGswS1ktZU5PNHlUZWdrTlpSNnJJaVkybXZVMHM1VE8xV3J6aE0tbTVlYzFxbnhhRjhZWkJ5eUl5QkZ5UVpiYzhEaTVXUEEtV2JGSmMzYW1zVTA0UdIBxwFBVV95cUxOcHFQa3oyaVFzTkJNMDN2ZW0xbWFqVFVMd3BseHJncm83cXZSMkhHM19oQU9mYlQzUFlMVW9IaW5MZjEtaDJwQTluS2l5bTJURFR0VFRuTGxZRlJSNGd2cXNwbG9UVGJfMG84cXJLNmFXdEo5d1ZraWt0dDVOTXo3XzBvNEZYLUxnejhBTTZ1WjZIY2ZxWkZpTnJTd2hSZ0pKSEV6dEU3ZGVjVnJTOVphcnJkakxGbmpNb09Xb1plQmpDNldCcWd3?oc=5", "src": "Fox News", "ago": "hace 47d", "ts": 1773730800}, {"title": "Trump dice que EE. UU. est\\u00e1 \\u00abdestruyendo por completo\\u00bb a Ir\\u00e1n: \\u00abMira lo que les pasa hoy a estos cabrones desquiciados\\u00bb ", "url": "https://news.google.com/rss/articles/CBMiugFBVV95cUxPeUE2aUpsckFRUVVaekdmdTloMWJEMTJQVThrOS1IM3Q1cnc3U1V4QkVfMUZpemo2MkpxdmpwVGx6RTV6akxNdVVRX1lRYVB4LXlZV08wYjd5N2xyanJxQ3U2QWtvRU5vdHhPNWRESno0NVZRelJDTG5zZnF1YW5uaG82ZWItRlFISnQ2bzFwRl9MaWVpRkJSZ29PX2ZEaGpfWTV3eDlwYTE1ZndVbkZCTmFnWVdWenZEVUHSAb8BQVVfeXFMTV9ZR0VZYUF0emtQWGh0SFlrZ0JSbnBKSXhVb1BuN1VNMDFOTkNvRVp2c3JBaDBxTUFmTEExcHBzNTMyajEwYVZOMlRKbUlLSnFYLXIxS25KaklDTmR3T2FDVkVOb0V4SDlEeUtKbEFxMW16Z09paTBsQlBxRUtOTFNrVlRGR2xlbm1mdnM3aHl3emczSXdyN2x3RVV6ZjVvNXkxN0Y2b3Y3WDRlWFJFV2tQTWI0ZmNyQ3Z4cjJWOXc?oc=5", "src": "Fox News", "ago": "hace 51d", "ts": 1773385200}, {"title": "Trump vows to hit \\u2018very hard\\u2019 after Iran\\u2019s president says he won\\u2019t surrender - Politico", "url": "https://news.google.com/rss/articles/CBMimAFBVV95cUxNeVh4LVFURU1ZcWlOZndENDY3cGx6TVB2c3dmM0lKY1VrRTZWaUNIelhqVF9zSzlEcmhwV3UySmp0a0wxQlhpZkttSUtEX3FTQmpVMmVZczM1N0FhODd3MHhKR2dfUjVpbUc5ajRvRkJTRkcyRjN0MVYtcl95WVNoOFowbHhOcnRRbE54WEtweTRGNlQ4YnhjVQ?oc=5", "src": "Politico", "ago": "hace 57d", "ts": 1772870400}, {"title": "Read President Donald Trump\'s Truth Social post naming Sen. Markwayne Mullin next DHS secretary - KOCO", "url": "https://news.google.com/rss/articles/CBMinwFBVV95cUxOOXpjZ0pCQlY3MlF0MUxfMXlEVFNlc25ON3B0c0dFQ1RWY2R5QlF6aTVYV2xsNm1uZXBwR01uTzJDdzNzaVBhbV9OczhlRDB1eGdKdUhUT1pSdG9wOV9kMV9SX2FSU1phV2ZnZExNXzBvb3VGazZNS0tHcDM4a2lqcjZmSGpCQ1RrWVdVYUs3LUVDM2k1cV9WT05WQXlIcWM?oc=5", "src": "KOCO", "ago": "hace 59d", "ts": 1772697600}, {"title": "Trump dice que el alcalde de Nueva York, Mamdani, ha hecho \\u00abgrandes avances\\u00bb al adoptar la Declaraci\\u00f3n de Independencia ", "url": "https://news.google.com/rss/articles/CBMiuwFBVV95cUxPQW01cTZWeHNEeTREbk5MT0U4eXJIRXJGcFdYMVNrUVpENHpEdFJpcENwM0FIMG1OSFdEZmI4TWt1ektwM1U5dl94WEhJLWdwakRsbEZBckc4NmJ2QmxZcGNIY1dtbVVRcVRDR204RnRlQXJOeE02MkNGMmZxeTVpYXc4MC00RTkzT2xwUjFvMTZnWFVzdnJ0aVpNTXl5c3ZCcGZpZE9GWGN5OUxza0xWeTd1TEFleGhPbV840gHAAUFVX3lxTE56dnhjWFh4bmZxaFFPNEdwRXNiU0NmN3RmaHQ1QnF1UlRWVGxzd0hYSGNYdnhUOUhvMGxoQzc2MFFFYnRCbTV0Q3JoMnN2bjNseHVCM21IMzNUVXpPMHRGa2czMWJucDFobTVHUllPZDlnZmlXNm5iQTVfNTlaS21pdHVRVmNrbFVUQTBocXo4V25KREUzVFZQWW5XNllNQzU2cmZ5SnNUT3JtRERnM0p5UUVDY0NXS1lQajlkZE90dA?oc=5", "src": "Fox News", "ago": "hace 61d", "ts": 1772524800}, {"title": "Washington Policy Weekly: Trump Launches War on Iran Without Congressional Approval - Arab Center Washington DC", "url": "https://news.google.com/rss/articles/CBMiuAFBVV95cUxPaXZ5Z1RUbnRyb24yNDd6bEVEdnBOZ1pmeDV2NFpNVHVQSzJIQ095VWZuRkl0RjE3bEJITVY3QnRmS1B5QmtBanpEaHBpLXZyRHE0T1dSaENmMGNmbmc0YVBUaVdFMTIzbGpUVWxGYnVlODhDU2R0X2g5RnpEcFBPWkJCQmFVd1BiQjBQWkZSX1dxODJZZFF1MFBrUGc5TUFtZG85VURhMXAxTDMtTFB4VnJ0a3JMWlRy?oc=5", "src": "Arab Center Washington DC", "ago": "hace 62d", "ts": 1772438400}, {"title": "Trump warns \'there will likely be more\' US deaths in Iran conflict - BBC", "url": "https://news.google.com/rss/articles/CBMiV0FVX3lxTE9kMjlHSnFrTlA4MnROY0FSTWpSVnBDb0JCek85NnBOV1FXTXZQNHBiNW5YQVN6UngteWNFa09ObW55cnQxTGJWQy1QVVVVQmE4dWkzdkNnWQ?oc=5", "src": "BBC", "ago": "hace 63d", "ts": 1772352000}, {"title": "Read Trump\'s full statement on Iran attacks - PBS", "url": "https://news.google.com/rss/articles/CBMiggFBVV95cUxOTGpPcVNMcndGbmtlTmxSZ01VUS1VZTVfNWxGRkpkNHIzWHhyRnJUWkNtVV9lSVU3eXVWWTBobkd2X242ZjBZeXVGN0w4NG1WU0JrV3VLc0VSYjZIcktGOE8wazMweXpxbjJtc2k4TzdOcTZBMy1lU29GQTYtQ0dEZUF30gGHAUFVX3lxTE03TlBsSWxFOTdfcUxLQUNDUHRmRURZeWVrS21ybjNGaWdnUnhkT2tTNm1VVWtCRTVrYkxzMnRWclY3bjdYLUhtTXZ1RUl4MGZSWDluY1lSVThWWTJMQ3dKTVVTbm5rT0xpTmpSMUxyZEdKSFp4cThCMTF5R0pHQ1BpTnBLREEzUQ?oc=5", "src": "PBS", "ago": "hace 64d", "ts": 1772265600}, {"title": "US and Israel launch massive attack on Iran - Politico", "url": "https://news.google.com/rss/articles/CBMiekFVX3lxTE9qeG1XaW80UEF5MG5pQkJVZDdBd0EtaWpTNlN5ZXNHbEFyWjdkb0JSNWR3ZE82ZmVmX2I1U2J3ZHV4ZEVidEc5SEhQSG92QzMwYXQ1RFJxNDFCQTZZeHd2TmF2cVRCUnJrZ3d0b3FTa3FQcU5QTkFxWk1R?oc=5", "src": "Politico", "ago": "hace 64d", "ts": 1772265600}, {"title": "Watch: Trump announces \'major combat operations\' in Iran - BBC", "url": "https://news.google.com/rss/articles/CBMiV0FVX3lxTE0wTEwtUU12Y0k1ZUxTRUV0ZFEwbXZtRVU5bXRDbGJDMm9lVEI3QkJMRktZeUhDY0lNdWV4bzFjTUlkd1dNX1dJZzZaWDM3Y2pzQ1JWSHR3SQ?oc=5", "src": "BBC", "ago": "hace 64d", "ts": 1772265600}, {"title": "Trump Stays Out of Public View After U.S. Launches Military Assault on Iran - The New York Times", "url": "https://news.google.com/rss/articles/CBMihAFBVV95cUxNY09ablU0MWkxaW5OMldOdk0zdW5NS1QwZFVaN01jMmV5XzdLalMxYVdGeEsxZlJNbFBGaG9xbjZiU1M4aWJtaDI3YnhkbFRFdkZ1aXFkWXlXanpqanpQbEg0OUFtZTRMaF9oWUNYOWxNb2FOZlZoa2dFOFhWc25NNWtQbU0?oc=5", "src": "The New York Times", "ago": "hace 64d", "ts": 1772265600}, {"title": "Iran confirms supreme leader killed in strikes by U.S. and Israel - MS NOW", "url": "https://news.google.com/rss/articles/CBMiZ0FVX3lxTE5ucHNSNkFZU1VyY1dkYVJ1YVJ5VkszZ2s4SkdEdlRwY2hwYS1QdkxuUHdaVUJnbGtYXzJXRk5sZlJldEdMYlhtb2EzM20yTUhjNzRkQXV0dkxYRmtmRkVMUHNkVGFXR0U?oc=5", "src": "MS NOW", "ago": "hace 64d", "ts": 1772265600}, {"title": "Trump to hike global tariffs to 15% from 10%, \'effective immediately\' - CNBC", "url": "https://news.google.com/rss/articles/CBMiX0FVX3lxTFBsSTVOOEs2eG1WN3haUmNaYXYtNENCTjlFN3h3aThTcERxQ0RaTGUtaWRHb3o1VmU2TEQtZTgtOUhSbHF3amJlMGpHU21ZQ085ajBHcmtWNkNSWXJoNDNV0gFkQVVfeXFMUDNUVFBUQ211U1g1R2IwcVY4bFZJdm4ybnEza1hqRkFtdUQxYVhld2s5SHR4aWU2QzBnQ1BBZXdYTTFsOEFBdjRaWUVUbm5fQkMtRk9uZldfVldDNnVoQUs1UkdqeQ?oc=5", "src": "CNBC", "ago": "hace 71d", "ts": 1771660800}, {"title": "Mexican ships arrive in Cuba with humanitarian cargo amid US oil blockade - Al Jazeera", "url": "https://news.google.com/rss/articles/CBMitAFBVV95cUxQQUJDdFJ5R3c1czJLUmpDcFpURWJodEc0YzQ1RUJPNkE5UllDdE5BcG9taUFweWd1R2NUcm92cGhndmZNRHpCd28ySUM3TEpxdVhGYkFlMVBLOHJQbUcxc0doOEJPY1NrOEFBRUZGMzhLcTFMb0NXYlRFOHdaNThNT2xzemo2VDlOSGpBVFpsc2xIOHRlWVV2Z2s2UDNrTDYtQ2k4b0FHMEd4MDVrSGdvT0puTTnSAboBQVVfeXFMTmJiaklBaGxURlB4WV93UmdBbHV3ZklKNW5EVjNVRnRPN25aa1NMWWdIQXFiOFpQUU56Q0dQZlM4NUxKd2ZRaE9VRWpvYTRkTlJ3Um9GakpfR1BKazgzdTNKZ2VNd3AtV3FDaVEybFBwRUk4OWt6ek9zMWVRNmxTYjNMc3NQTHB5Nkxja2U4bVpCbVZQR2thVFJla1A3T2lEYktraWlEYW9fY09NX3c5RDk1RnZMV1JpaFVn?oc=5", "src": "Al Jazeera", "ago": "hace 80d", "ts": 1770883200}, {"title": "Trump se autoproclama \\u00abpresidente interino\\u00bb de Venezuela en una publicaci\\u00f3n en Internet tras la destituci\\u00f3n de Maduro - ", "url": "https://news.google.com/rss/articles/CBMivAFBVV95cUxOLXFuSnV4QXQzS3RtTHlTam5JRWJwT2hGZ2ZDODJSRnpUZ2dPUmVaN1lEaG5peUZuREszaGdHWFUyNm1UZUhWazh0TnJyaEdYNm5UUGljajgxenF0ei14QWhsTkZ4aTc0NTlIZlFuRmJaMldQRl9vRThZYnowZUFNRTRSYU1kaTNEalZ0V2F2NkhxdXhQY3RLVXE3eFlydmhHbEZFMmRrSWZmY2VoS3M2Z3VaZDJLRndnZlpITNIBwgFBVV95cUxQOWJmZENVLXJIa1lhNVBCdGduSjl1UERhbEVxU0l0azNOTEpLNjBOdkdrR1V0SGRJN3U1TF9XcWdRWGhVbmQzdjlhVXYzSmNQYzFoWHBGTVpuSTNMSnBTaXpjNXRQSmRheGtXSHU1aHdBUlFTUG1hUHhyU1lHdzRnbkstY25VV1NXZ3daVVpYbEpyeFVsVmNRSDI5aUVBWDZIU3F2N3d2ZnZkV29zUGl5LThzRUlvLXVVZ3d6REVHbjFfZw?oc=5", "src": "Fox News", "ago": "hace 111d", "ts": 1768204800}, {"title": "Mientras Trump insta a llegar a un acuerdo, el presidente cubano advierte de que el pa\\u00eds se defender\\u00e1 \\u00abhasta la \\u00faltima g", "url": "https://news.google.com/rss/articles/CBMitAFBVV95cUxQcTFkRjhhdWNuWVZmT1NhNjFMdnhKODE5RkFaY0xleWFHelRrREprUnJwY2dROHlxb0RIaFdNYlhLVUxNaEd3aEZ3eHRmWklic09vbENIUFNrUHVGV1Y2ZDdiVHZvdWItdVRmUnZMbHE2WDk2ZHk4anNBQ0EtaE42Q3pDMXZENzhKUzBVN1h6OGNVUDNLYkNPb0pVWUl1bmhpNUxncUJHS0toeTZscVhybHRnODDSAboBQVVfeXFMTld0QjB1T2hWcXRvX2l6aE94NldURkluZGtYTTBMalVvcUxYSkswUk9HLVZ6RXQ5YkhRb0lfLVdtWHBXdmd3T2hQUjE4SkYtakxZd3ZGYWlNRUZWRXFvbzAwNXNHVDRva2pubkVrSkRjR3hxOHBtUnpGYmNwUHJSZkxrM3RNaGxLS0VLdHFwZUt2cXlzeXBJM0pzZWkyaV9KbEFVVVNnNmtHNjFJejlkcGdvOTRtLW5ldWVB?oc=5", "src": "Fox News", "ago": "hace 111d", "ts": 1768204800}, {"title": "\\u00abEE. UU. podr\\u00eda seguir involucrado en Venezuela durante a\\u00f1os\\u00bb, dice Trump - Fox News", "url": "https://news.google.com/rss/articles/CBMihwFBVV95cUxQMWRmYjF1SXNyYkZUT0taek5keTh2NFRYeWw0VzlWU25tSWNaNkc5ckxzUDlwRHdfUTVISDIxMmRmTUZZOVZGYXZ6MFVNUFRXN0FGbDZPNlRCS0g2MU05bGliY3JINmJtTllhSlJmTFl2T0RWelRNYzd0a1ZUaW42UUloTC03bjjSAYwBQVVfeXFMTVZhZUdFbExJVzFLYzBzcFd5cDA1NmxYNFNvejdiVUc0Sk1aRWhFTVpzd1djTEVibzB0UUxZNllqQlpVd01ZY2paaFZMdGdjZF9wZUZzWktwMVJNLVIwZ0doTlZ4Z2VGTTZ2WXU4Z2tQMFNZYWppOXZISVVkck83cEtCdjI3eW5kYlJTeUo?oc=5", "src": "Fox News", "ago": "hace 115d", "ts": 1767859200}, {"title": "Trump says US to get 30 million to 50 million barrels of oil from Venezuela at market price - ABC7 Los Angeles", "url": "https://news.google.com/rss/articles/CBMirAFBVV95cUxObzMtWXNwN2hwSWFrbEJqLXpZMXBsWXhpWjFKYWlwQjFlamZCMWQ5eXN5WktPLW1haHg2UnZRVHAzQWgzTDlXbExfRlp4cExteVZiSnRWNEdpRFVFekx6STNhamQ3QUc2UXE4eWJ5QVhMV01tNkt4aGkyWkIzWl92VUxaZVphOTlMa1Qxb0NtZ1pkMnRWbzI3NG1yUVcxS1otQjBkMFZfRERfRW8t0gGyAUFVX3lxTE1VYTN5eDRsMnk4TUNJRnpoSzFzcVJkMTM2dmcxRFNiNW5tODBMeW4wX3JnRDhEeDZ6RmwyV1dlYV9hZjVsMHUzRnFuaVZaVUZiOTVwQXZJTXBvZmgzMUdmR1RYbmRUbHlSajFfbEppb3REa2V2RDFXSWNzQWxOLTRxbTc5WjRNcVAwRU9IbzJmVDFSbWo0TzRSM20wSDRTa3hWX3Y5dE1HMVktQkVkRU1RWVE?oc=5", "src": "ABC7 Los Angeles", "ago": "hace 117d", "ts": 1767686400}, {"title": "US-Venezuela news LIVE: Venezuelan President Nicolas Maduro captured, with wife Cilia Flores, amid US strikes, Donald Tr", "url": "https://news.google.com/rss/articles/CBMiuwFBVV95cUxPbXM0eU9EVlQ5akFvUHFvak1Da0NWZVVqMnk1a183YjZtc1JMMEFKUE9GczBaVFUxZEE3aXhza2xteE5qTGExWUx6cTB5Ykx0ZTFBYkJPTERDaTJMeWplSHVPOGJrSHQ4TkJCby1lSkh6S2dqaE1xS3dPaF9Uck96NWtjd3ZaNnppSHJsaEIwX2U1WGxKaGJYYkZjMGZDYWZMdnVoZ1pKNkl1VkxtYm5JV3NKc0hvbVB4c0k40gHAAUFVX3lxTFBvR28wdXBPdXlVbUo0bnd4Uy1TbkVYS3lTZTRwVHV4bVl0cDBGT012cVNDSThtZUE2Qi16SDQ1Z0c3T3ZmVm1SU3o2QVFMR3NkNlBQMHN1SGVIVFNXWEM0dXZmUE5tdVM4a0YxX2R6bjJvc2ZnYTNyN2JzQ0NmamZFRlBPWERObG93bGJMYWhfTHFKaDU2N0otcFZISWxZb1d4TC0xWHRJUjdzTnZta1hBZldBWGNaUHFUTnlhcmVySw?oc=5", "src": "ABC7 Los Angeles", "ago": "hace 120d", "ts": 1767427200}, {"title": "Why, really, is Trump going after Venezuela? - The Week", "url": "https://news.google.com/rss/articles/CBMicEFVX3lxTE9uTTNJNlE0Q0labEZDR25LWDZGOEVxU0VLSTZSRlAxNmpQRXMzR0diQVJka3hnTi05aHhDQV9wRmstYjU1U1g0bmJtczZ1NzFySFY3SG90OHBiN0JJNG9vazN3RzJMT0NfdjRzcTZyVlI?oc=5", "src": "The Week", "ago": "hace 132d", "ts": 1766390400}, {"title": "Trump nombra a un gobernador republicano como enviado especial a Groenlandia - Fox News", "url": "https://news.google.com/rss/articles/CBMinwFBVV95cUxQVE1lb21Hb2JWaWdQM1NINzh6VHhERU5EWHpFbng1eGNxZnJERDExVmxjZEVxYlh5SmdlXy1feHNjXzhyOW43SG9JV2d3RUlUc1c5ZHRZbi1Udl85MmZqeGFSdUFQZnVPbHE1WldlbXJVZllDQVh0Y1QyajBXRXh0NXZ2anRIdWVGUGhWa1g1NzJMNGw1XzA1WFJrS3BrQmvSAaQBQVVfeXFMT1lWMmcwdjVOSDZFSmloVVFWX0F5R2YxbW1iSTNLTEI1YWdjOFp6SnppdUZDU2hvVGEzVnBQaFBvUHpZWUFUY0Uxd3lVWXJnQjZHZVhnUWJxU3B5M2ZDZGNvX3dkMFZOWTNQVXptZlNXV3pyLWxSaTFGOVhOd1ktYl9Za3FuMmMwaURhbEI0MF9YN25PSG9IdWRVZXJBVWdpcjd0d2Q?oc=5", "src": "Fox News", "ago": "hace 132d", "ts": 1766390400}, {"title": "Trump doubles down on his criticism of slain director Rob Reiner - CNN", "url": "https://news.google.com/rss/articles/CBMiiAFBVV95cUxNRjEyQkxFbDRHdjR1U0R1ZFNGcnZZbXRranAtMFctNkhMN1VST0Fsc3lVUjJBMVY3TGJIQkJBbF9hYjlJTDE0czlwZW1LTjJIdmxGV1c3ZG5MdEhuYW1YWGFSVmtNdHpBdXZDREhhNmh2NXVlQVd0MHZiR195ZUNOLWNocnByY1Fw?oc=5", "src": "CNN", "ago": "hace 139d", "ts": 1765785600}, {"title": "Trump arremete contra las compa\\u00f1\\u00edas de seguros \\u00abGRANDES, GORDAS Y RICAS\\u00bb y anuncia el \\u00ab\\u00daNICO SISTEMA SANITARIO\\u00bb que apro", "url": "https://news.google.com/rss/articles/CBMixgFBVV95cUxNaDJkbC1lMzdabnA0YmJHTjZ1ZU1lcm5SSTQ0ODJLWjlMMV9KcmN2dlhDLXhXLVU0QUNYQ1ktaldiQzdibEdUcXpxcDNiSlZnTzUxTFpPNDRxemtFSDJ6UlM5QVZsSFZuYXZFdzQ3WEdUT29XWGt5YzVNeDVJTzVyY2w1YTFWc1ViZndCZHZnYlh3MmN6bFVFSEVSbnpCT2M4Q0VjS0o5RHVfZGEteXVLbFpYTlZsdHdBVVF5RVhWY3F6NlNCaVHSAcsBQVVfeXFMTl85WGNxOExweDd3bnlZTDRYNTczY3ZXWHF5Z2tLVzZ3eFdiMHdSanlqeW4wRG5sS0pkOTg5Ykhaa3FYSjd4OTNsaV90Mkloa3FIVms2QjI1c2pVcjJjalliTjctR2s2S2xSM25qLWRpZVVUWVgybGk0T3djaEVSa2tMRDNMeXNTMzZPb1pHbFJaQnlVMklZYkhCOGZhcE1jNjVrSVppOWlXemg1TVl5a1JFdVY1eWE2aGRrUVIyYzFrYnpuc0NDbUFWN28?oc=5", "src": "Fox News", "ago": "hace 166d", "ts": 1763452800}, {"title": "US announces new attack on \\u2018narco-trafficking vessel\\u2019 off the coast of Venezuela - EL PA\\u00cdS English", "url": "https://news.google.com/rss/articles/CBMiwwFBVV95cUxOTG1PdUN1Y25Ea0RPaU1KY1Y1NmJlSlNTOXdXWVRiNzR4Ml9qR3Y1WmxBbVNndWdvMUlUT0hnS2JDY1lkdFFGQ2xleEFGQ2dwNkR0MUVjXzd0OG9RYTk2aWhXb0NkSlUyTkJpMGk3RXdtZHlZMGRXU1l6RzJLVHZOcVoxZVVQMDZTaGNRQXZneVlLZWdjMW5qUnRTT3hOVWRwQnZlTjl4dGVWMmRGMHhDVGRpOTEyS3A0SG1RT1Bkd2pwV3PSAdcBQVVfeXFMTUF2WWlVeUhfUWhnWVQ2dWVYbEhCejY2eTNZbk8zb1E5RTJ1aXZsTEVwdDN6R3ZDQ3E1UUdWOERqeW52UXBneDdkeFdIWUJjX0U5Y3NaT0kxelBsRHdYNHpiemZqTGV3dHZSdzROY2VhdjFjdkR4bnhyVjVpZmtMeGlpeXhodlBoT3M0QWx2ZzFBNzk3TFVxQlNrOVc4RldfNndCTjROQUhKRmJyZG82dlNLUHpoNzBRQWhIQTY5ZkVyX09KS0pyaDNvV0hVRWlfZVpoaTZycnc?oc=5", "src": "EL PA\\u00cdS English", "ago": "hace 212d", "ts": 1759474800}, {"title": "Trump says Argentina does not \'need\' bailout at Milei meeting - Buenos Aires Times", "url": "https://news.google.com/rss/articles/CBMiqAFBVV95cUxNSE5qYWtWMFg4OXBCM0J3V0pSRFRKSFJDUVNQUTNuRkZNbEo0SHRZdjlpVmlBM0IzS09rVzBhT3Rnb3lWUldJV1ljcmVmTnFMZWg4OEY3SndMYmtLa2VXRExjMWM1a2RhbGNUWWRwcHBJVEo1RTdBVy1lZlIyUnBJb2tiQ0hiUDBWQmU5eUY0ZXphNE9acmU5Z1BTeTh3djkyWTJxLWoyQnfSAa4BQVVfeXFMT09zekFRbUFqeHBFcmRZdTVHVHNpVmpPenVCM3c2T2JzVThTT0lDYXd3cmtIV2Y3OWZoYVFjT3ZMbmJ0N2NsU1h5VHByOUFTSGZXX01mT0FjVURhNngwQ2h6UXF0dnZZTlpUY3A3cVdsX3ptYmtqLTFCVEZjc0ZjNl9kNmFBSlNpRzM0M0JndEU3dXJoZEFadzhUODNvb2N3bVR1SmVnZUtYQTJCNzlR?oc=5", "src": "Buenos Aires Times", "ago": "hace 222d", "ts": 1758610800}, {"title": "Trump says he will designate Antifa as a \\u2018terrorist organization\\u2019 without providing further details - EL PA\\u00cdS English", "url": "https://news.google.com/rss/articles/CBMi3AFBVV95cUxQaU44M2xIZTF1YWxhR3hiZ2hFbTNjMVZzR0U4LV9KRmJhUkJBWGV3UzIwM3hwZmtSQmJNY2t2Qk9tLVdLTUFIY29rT2RYWk5YY2ppZ256V19VNUxvN2N2WmFRODRjVjhhbzZXWVNMTzVwcnF4ODY3OGhQOWI4cFI2ZkFPRV93dk4yQkVYU1RfaDJ6akpKSHk0Q1Ricng4djh0N2xBcDBSMnd1X3FkTGZiMXp5R1hIZTJhMG9ERTVuOFJCQVdMLXFxVGwxc2pkQUE2QWpXQmJnX1YyZW1V0gHwAUFVX3lxTFBMNkRSQlE1UGVJQ1FLTWJndFBBanlwU2JzR0dycG01QU9TZDQwS0E5aUphNnpHZjZTcXNnNzVpYWR1TndBSWpXR0pRc0tIdnc2WTRvSUVkaWFzZDViSVFHaS1iaVoyeExCT2N0UmY1VkVDRlVjb3lZZ3VOblJuTWliNXNCZ19mcW9BYVF0bDdqM3l5bUlldjRHVjE5ZHdmQ0V6RmZ1Ul9SNlV6YUhXTHRRUGpBSndMdGthN2ZPVnp4TC1wczUwajVXU3hid2pkbW1rT0FvdEgwRXJiTXZYRTQ4a1EyeFUzX3hYcTVhVS1aaQ?oc=5", "src": "EL PA\\u00cdS English", "ago": "hace 227d", "ts": 1758178800}, {"title": "Trump\\u2019s \\u2018war hero\\u2019 comment is merely his latest flippant comparison of himself to troops - CNN", "url": "https://news.google.com/rss/articles/CBMifEFVX3lxTE82YXptT01tTmVjVUVwS1FySHFWbHZKOTFmM29DcFYxaFFqNUZoNHlwN3BmM1gzRnc3S01wYk1ITGY0aEhQcnBtT3hIU3FTQ0o1elc5Y3B6VGw2Q2piV3RzMmlpRTV4SE50aEZRYTc5MEhHelBVSHpZUTZWak4?oc=5", "src": "CNN", "ago": "hace 256d", "ts": 1755673200}, {"title": "By acknowledging \'real starvation\' in Gaza, Trump sharpens Western pressure on Netanyahu - CBC", "url": "https://news.google.com/rss/articles/CBMihwFBVV95cUxPeU1wdFpxclpEbFgyc0xOS1lrdVJMbHZkWG9leTgzWWY2MVhVNmJITnFVY1VrNUpMdmdXRG1EWlFEWVlOTTJ2Tl9iSHdCOTdydlBoYUhOX3hzRFkxR1NySld4Z2xqSlJQOTFjSkR3VGJxa2JJdXI2UWhMNkl6OEdhN1BFSVdIaTg?oc=5", "src": "CBC", "ago": "hace 278d", "ts": 1753772400}, {"title": "Trump assails Spain over NATO defense spending target - Axios", "url": "https://news.google.com/rss/articles/CBMifEFVX3lxTFBEZGV6ZnUydTQwNmpfN2kxbjJEVng0U3BISHRjNkg4MklfTk44SmllNVotTTNzSVB5VmhOVnZ0YmtMcHpsa1J5TjgwTjIyX2lYU1czcjUxcXExT2ZQQjA5bUw1X0RHeG1BMTgtVWw3bGQySDhGMGxkZElPUFA?oc=5", "src": "Axios", "ago": "hace 312d", "ts": 1750834800}, {"title": "Trump says he wants Iran to give up entirely on nuclear weapons - Reuters", "url": "https://news.google.com/rss/articles/CBMisAFBVV95cUxNV200bWd1bDRFc0lfSzI1dnR4UmxqeHE4amp0SEM2a0JlejJVc19NdzlwZU94Mkc5ck1HZ0IzZnpmeVF4VEFkVV9LRk9zSW1rODhBandQYUMwMUhKeXI0RG5LTmtJS2FWc3JjTjZISmEzUlNRWlZQalI5RzB3Ml85cm1rcXhvTVJiMWdmU211cDVEOUxmWEx6TTYwSFJwNkt1aWFnQWx3MzRSQnZQUGdWOQ?oc=5", "src": "Reuters", "ago": "hace 320d", "ts": 1750143600}, {"title": "Trump plans to attend Pope Francis\' funeral; orders US flags flown at half staff. Published Apr. 22 2025. Nation. - The ", "url": "https://news.google.com/rss/articles/CBMiYkFVX3lxTFBjSzA4Z3Rja19hNkk0clB5NGJvS1JPb2tjaWx1NUswLUo5Zzd4VHBWY0d6VWZNc0w4U3Rfc2xSaklLYlpqS3RvX3ZqNnFzcXpON2VjXzc2TDk2RUhFNy1ZOTl3?oc=5", "src": "The Boston Pilot", "ago": "hace 376d", "ts": 1745305200}, {"title": "Ivanka Trump Takes Daughter to Eras Tour Despite Donald\\u2019s Hatred of Taylor Swift - IMDb", "url": "https://news.google.com/rss/articles/CBMiUkFVX3lxTFBuNS1KRnBEaXZaa1FJak1Ldkx2MkE3MlhfWFpJQXF5aERIX1NHcnNVT0NkbGI2c2hZcVB3YmhXTWQzZkdGYUZXRU5pcWN0eWVLdnc?oc=5", "src": "IMDb", "ago": "hace 392d", "ts": 1743922829}, {"title": "Trump opens tariff war against Mexico, Canada and China - EL PA\\u00cdS English", "url": "https://news.google.com/rss/articles/CBMiugFBVV95cUxOLThEdzZBZEV4alQ5N3dHck8wdWZ5QW1iXy1maW85V0RFY2ZMNlZQdXI0eWE1R1BkRmJlTS0zMWZDb1FqdnNQQ21XSXFlYmg1R0hMNXV2LUh1TTlMdDNjUnkyNFdkV2J6a0pQdWEyS0syMk9yT3Y2NEVPR2tJcWFIVndhTV9Zb0RWem1GcVlQbndKUkFQcW9OTUZRbTdtQ0lkQjgzcV96amZCSzF0eHBSUkxIY2p5eWxDNHfSAc4BQVVfeXFMTTVWNWZ4Sl9KZmxMd0w5M3lZMXVyNDdHU05qZ0hrVmYzVEVsZWhLM3MtVmxyOXh1QTFTdkJNUlJPQWM2aWdGbDl6aW5rTFp4c1llMDFucFRwVGZCaVRnM2pCZlo2cWtEVWxCUi1KVEdzQTNGdmNCdTc4ZzRKTUFaSFk4cFFtcFFhZnVJNlV0NGpsbnRzaWlHY3lSWHRMeWVkT3FGaGdmaF84dkt4SUJndGticzlrNHlBTUQ3OU9nekV6RGRHVEg5QXppOUI3VWc?oc=5", "src": "EL PA\\u00cdS English", "ago": "hace 456d", "ts": 1738396800}]'

        _panel_html = (
            '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
            '*{margin:0;padding:0;box-sizing:border-box}'
            'body{background:#060d1a;font-family:system-ui,sans-serif;color:#e2e8f0;height:705px;overflow:hidden;display:flex;flex-direction:column}'
            '.cht{display:flex;gap:3px;padding:7px;flex-shrink:0;border-bottom:1px solid #0f1f35}'
            '.ch{padding:4px 12px;font-size:9px;font-weight:700;border-radius:4px;cursor:pointer;border:1px solid #1e2a3a;color:#475569;background:#0a1020;transition:all .12s;white-space:nowrap}'
            '.ch:hover{color:#e2e8f0}.ch.on{color:#060d1a;border-color:var(--c);background:var(--c)}'
            '.player{width:100%;height:230px;background:#000;flex-shrink:0}'
            '.player iframe{width:100%;height:230px;border:none;display:block}'
            '.note{font-size:9px;color:#475569;padding:2px 9px;flex-shrink:0;border-bottom:1px solid #0f1f35;min-height:15px;background:#060d1a}'
            '.sectabs{display:flex;flex-shrink:0;border-bottom:1px solid #0f1f35}'
            '.stab{flex:1;padding:5px 0;text-align:center;font-size:8px;font-weight:700;cursor:pointer;color:#475569;background:#060d1a;border-right:1px solid #0f1f35;transition:color .12s;letter-spacing:.05em}'
            '.stab:last-child{border-right:none}.stab.on{color:#2dd4bf;border-bottom:2px solid #2dd4bf}'
            '.filters{display:flex;flex-wrap:wrap;gap:3px;padding:4px 7px;flex-shrink:0;border-bottom:1px solid #0f1f35}'
            '.filt{padding:2px 7px;font-size:8px;font-weight:700;border-radius:99px;cursor:pointer;border:1px solid #1e2a3a;color:#475569;background:#0a1020;transition:all .1s}'
            '.filt.on{color:#060d1a;background:#2dd4bf;border-color:#2dd4bf}'
            '.feed{flex:1;overflow-y:auto;padding:4px 8px 8px}'
            '.feed::-webkit-scrollbar{width:3px}.feed::-webkit-scrollbar-thumb{background:#1e2a3a;border-radius:99px}'
            '.card{padding:6px 9px;margin-bottom:4px;background:#0a1020;border-radius:5px;border-left:3px solid #475569}'
            '.card a{font-size:11px;color:#cbd5e1;text-decoration:none;line-height:1.4;display:block;font-weight:500}'
            '.card a:hover{color:#38bdf8}'
            '.meta{display:flex;align-items:center;gap:5px;margin-top:3px}'
            '.dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}'
            '.src{font-size:9px;color:#475569;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}'
            '.when{font-size:9px;color:#2dd4bf;flex-shrink:0;font-weight:600}'
            '.xbtn{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:14px;padding:20px}'
            '.xbtn a{padding:10px 28px;background:#1d9bf0;color:#fff;border-radius:99px;text-decoration:none;font-weight:700;font-size:12px}'
            '</style>'
            '</head><body>'
            '<div class="cht" id="cht"></div>'
            '<div class="player"><iframe id="yt" allowfullscreen allow="accelerometer;autoplay;encrypted-media;gyroscope;picture-in-picture"></iframe></div>'
            '<div class="note" id="note"></div>'
            '<div class="sectabs">'
            '<div class="stab on" id="sn" onclick="showSec(\'n\')">NOTICIAS</div>'
            '<div class="stab" id="sx" onclick="showSec(\'x\')">&#120143; TRUMP / X</div>'
            '<div class="stab" id="st" onclick="showSec(\'t\')">TRUMP NEWS</div>'
            '</div>'
            '<div class="filters" id="filts">'
            '<span class="filt on" data-k="" onclick="doFilt(this)">Todo</span>'
            '<span class="filt" data-k="guerra,war,conflict,ataque,attack,strike,killed" onclick="doFilt(this)">Guerra</span>'
            '<span class="filt" data-k="ucrania,ukraine,rusia,russia,putin" onclick="doFilt(this)">Ucrania</span>'
            '<span class="filt" data-k="israel,gaza,palestin,libano,iran,siria" onclick="doFilt(this)">Or.Medio</span>'
            '<span class="filt" data-k="petroleo,oil,gas,energia,energy" onclick="doFilt(this)">Energ&#237;a</span>'
            '<span class="filt" data-k="sancion,sanction,arancel,tariff" onclick="doFilt(this)">Sanciones</span>'
            '</div>'
            '<div class="feed" id="sec-n"></div>'
            '<div class="feed" id="sec-x" style="display:none;"></div>'
            '<div class="feed" id="sec-t" style="display:none;"></div>'
            '<script>'
            'var CHS='   + _ch_json    + ';'
            'var NEWS='  + _news_json  + ';'
            'var TRUMP=' + _trump_json + ';'
            'var CUR="",ACTIVE_FEED=NEWS;'
            'document.getElementById("cht").innerHTML=CHS.map(function(ch,i){'
            '  return \'<div class="ch\'+(i===0?\' on\':\'\')+\'" style="--c:\'+ch.color+\'" onclick="playC(\'+i+\')">\'+ch.name+\'</div>\';'
            '}).join("");'
            'function playC(i){'
            '  document.querySelectorAll(".ch").forEach(function(x){x.classList.remove("on");});'
            '  document.querySelectorAll(".ch")[i].classList.add("on");'
            '  var ch=CHS[i];'
            '  document.getElementById("yt").src=ch.videoId&&ch.videoId.length===11'
            '    ?"https://www.youtube-nocookie.com/embed/"+ch.videoId+"?autoplay=1&rel=0&modestbranding=1"'
            '    :"https://www.youtube-nocookie.com/embed/live_stream?channel="+ch.channelId+"&autoplay=1&rel=0&modestbranding=1";'
            '  document.getElementById("note").textContent=ch.videoId&&ch.videoId.length===11?"EN VIVO":"Stream directo";'
            '}'
            'if(CHS.length)playC(0);'
            'function showSec(s){'
            '  ["n","x","t"].forEach(function(id){document.getElementById("sec-"+id).style.display="none";document.getElementById("s"+id).className="stab";});'
            '  document.getElementById("s"+s).className="stab on";'
            '  var el=document.getElementById("sec-"+s);'
            '  el.style.display="block";'
            '  document.getElementById("filts").style.display=s==="n"?"flex":"none";'
            '  if(s==="n"){ACTIVE_FEED=NEWS;render(el);}'
            '  if(s==="x"){renderX(el);}'
            '  if(s==="t"){ACTIVE_FEED=TRUMP;render(el);}'
            '}'
            'function renderX(el){'
            '  el.innerHTML=\'<div class="xbtn"><div style="font-size:36px;color:#1d9bf0">&#120143;</div>\''
            '    +\'<div style="font-size:11px;color:#94a3b8;text-align:center;">X/Twitter no permite<br>embedding directo</div>\''
            '    +\'<a href="https://x.com/realDonaldTrump" target="_blank">Ver @realDonaldTrump en X</a></div>\';'
            '}'
            'function doFilt(el){'
            '  document.querySelectorAll(".filt").forEach(function(x){x.classList.remove("on");});'
            '  el.classList.add("on");'
            '  CUR=el.dataset.k||"";'
            '  render(document.getElementById("sec-n"));'
            '}'
            'function getCol(t){'
            '  t=(t||"").toLowerCase();'
            '  var m={guerra:"#ef4444",war:"#ef4444",conflict:"#ef4444",conflicto:"#ef4444",ataque:"#ef4444",attack:"#ef4444",strike:"#ef4444",killed:"#ef4444",'
            '    militar:"#f97316",military:"#f97316",sancion:"#f97316",sanction:"#f97316",arancel:"#f97316",tariff:"#f97316",'
            '    petroleo:"#eab308",oil:"#eab308",gas:"#eab308",energia:"#eab308",energy:"#eab308",'
            '    iran:"#ef4444",rusia:"#f97316",russia:"#f97316",ukraine:"#f97316",ucrania:"#f97316",'
            '    israel:"#f97316",gaza:"#ef4444",china:"#a855f7",nuclear:"#a855f7",trump:"#22c55e"};'
            '  for(var k in m)if(t.indexOf(k)>=0)return m[k];return "#475569";'
            '}'
            'function render(el){'
            '  var ks=CUR?CUR.split(","):[];'
            '  var arts=CUR?ACTIVE_FEED.filter(function(a){var t=(a.title||"").toLowerCase();return ks.some(function(k){return t.indexOf(k.trim())>=0;});}):ACTIVE_FEED;'
            '  if(!arts.length){el.innerHTML=\'<div style="color:#94a3b8;font-size:11px;padding:16px;text-align:center;">Sin resultados</div>\';return;}'
            '  el.innerHTML=arts.map(function(a){'
            '    var c=getCol(a.title);'
            '    return \'<div class="card" style="border-left-color:\'+c+\'">\''
            '      +\'<a href="\'+a.url+\'" target="_blank">\'+a.title+\'</a>\''
            '      +\'<div class="meta"><div class="dot" style="background:\'+c+\'"></div>\''
            '      +\'<span class="src">\'+a.src+\'</span>\''
            '      +(a.ago?\'<span class="when">\'+a.ago+\'</span>\':\'\')'
            '      +\'</div></div>\';'
            '  }).join("");'
            '}'
            'render(document.getElementById("sec-n"));'
            '</script></body></html>'
        )
        _comp.html(_panel_html, height=705, scrolling=False)
