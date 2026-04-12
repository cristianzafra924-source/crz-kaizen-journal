import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
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
.metric-card.green::before  { background: #22c55e; }
.metric-card.red::before    { background: #ef4444; }
.metric-card.blue::before   { background: #3b82f6; }
.metric-card.teal::before   { background: #2dd4bf; }
.metric-card.amber::before  { background: #f59e0b; }
.metric-card.purple::before { background: #8b5cf6; }

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

/* Nav tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #0f1923;
    gap: 4px;
    padding: 0;
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

/* Equity period pills */
.eq-pills { display: flex; gap: 4px; margin-bottom: 12px; }
.eq-pill {
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    padding: 3px 10px; border-radius: 4px; cursor: pointer;
    border: 1px solid #1e2a3a; color: #475569; background: transparent;
    text-transform: uppercase; transition: all 0.15s;
}
.eq-pill.active { background: #2dd4bf22; color: #2dd4bf; border-color: #2dd4bf55; }

/* Selectbox */
.stSelectbox label { color: #94a3b8 !important; font-size: 11px !important; }
.stSelectbox div[data-baseweb="select"] { background: #0d1117 !important; border-color: #1e2a3a !important; }
.stSelectbox div[data-baseweb="select"] * { color: #e2e8f0 !important; }
.stSelectbox [data-baseweb="popover"] * { color: #e2e8f0 !important; background: #0d1117 !important; }

/* Dataframe */
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


# ── Chart theme base ───────────────────────────────────────────────────────────
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


# ── Equity curve Darwinex — componente HTML puro con Chart.js ─────────────────
import streamlit.components.v1 as components
import json

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

# ── Capital inicial ────────────────────────────────────────────────────────────
if "capital_manual" not in st.session_state:
    st.session_state.capital_manual = 10_000

# ── Upload + Capital (siempre visible, antes del parse) ────────────────────────
_col_up, _col_cap = st.columns([4, 1])
with _col_up:
    uploaded = st.file_uploader(
        "Sube tu historial MT5",
        type=["xlsx", "xls"],
        label_visibility="collapsed"
    )
with _col_cap:
    capital_input = st.number_input(
        "Capital inicial ($)",
        min_value=100,
        max_value=10_000_000,
        value=st.session_state.capital_manual,
        step=1000,
        help="Tu balance de partida. Ajústalo si el % no cuadra con tu cuenta real.",
        key="capital_input_widget",
    )
    st.session_state.capital_manual = int(capital_input)

if not uploaded:
    _lm = st.session_state.light_mode
    _bg = "#ffffff" if _lm else "#0d1117"
    _border = "#e2e8f0" if _lm else "#1e2a3a"
    _title = "#0f172a" if _lm else "#f1f5f9"
    _sub = "#64748b"
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
df_s  = stats["df_sorted"].copy()

# ── Recalcular capital y % siempre en tiempo real (no dentro del parser) ───────
CAPITAL = st.session_state.capital_manual
df_s["balance"]      = CAPITAL + df_s["equity"]
df_s["rentabilidad"] = df_s["equity"] / CAPITAL * 100
stats["capital"]     = CAPITAL

# Recalcular max_dd con capital correcto
peak_r = df_s["equity"].cummax()
dd_r   = (df_s["equity"] - peak_r) / peak_r.replace(0, np.nan) * 100
stats["max_dd"] = float(dd_r.min()) if not dd_r.isna().all() else 0

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
with tab_cal:
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
    st.markdown(f"<div style='text-align:center;font-size:16px;font-weight:700;color:#f1f5f9;margin:8px 0;'>{month_names[m]} {y}</div>", unsafe_allow_html=True)

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
with tab_ops:
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
with tab_sym:
    st.markdown("#### Análisis por Símbolo")

    sym_g = df.groupby("symbol").agg(
        Ops=("profit","count"), Ganadoras=("win","sum"), PnL=("pnl_net","sum"),
        Mejor=("profit","max"), Peor=("profit","min"),
        Gan_bruta=("profit", lambda x: x[x>0].sum()),
        Perd_bruta=("profit", lambda x: x[x<0].sum()),
    ).reset_index()
    sym_g["Win_Rate"] = sym_g["Ganadoras"] / sym_g["Ops"] * 100
    sym_g["Factor"]   = sym_g["Gan_bruta"] / sym_g["Perd_bruta"].abs().replace(0, np.nan)
    sym_g = sym_g.sort_values("PnL", ascending=False)

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

    hr_g = df.groupby("hour").agg(ops=("profit","count"), pnl=("pnl_net","sum"), wins=("win","sum")).reset_index()
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
        z=heat_pivot.values, x=[f"{h}:00" for h in heat_pivot.columns],
        y=heat_pivot.index.tolist(),
        colorscale=[[0,"#7f1d1d"],[0.5,"#0d1117"],[1,"#14532d"]], zmid=0,
        hovertemplate="Hora: %{x}<br>Día: %{y}<br>PnL: $%{z:+,.2f}<extra></extra>"
    ))
    fig_heat.update_layout(**LAYOUT, height=280)
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB KAIZEN SCORE
# ══════════════════════════════════════════════════════════════════════════════
with tab_kaizen:
    score    = stats["kaizen_score"]
    wr_score = min(stats["win_rate"] / 60 * 30, 30)
    pf_score = min(stats["pfactor"] / 2 * 30, 30)
    rr_ratio = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
    rr_score = min(rr_ratio / 2 * 20, 20)
    dd_score = max(20 + stats["max_dd"] / 5, 0)

    if score >= 80:   lvl_name, lvl_color, lvl_emoji = "MASTER",   "#10b981", "🏆"
    elif score >= 60: lvl_name, lvl_color, lvl_emoji = "PRO",      "#2dd4bf", "⚡"
    elif score >= 40: lvl_name, lvl_color, lvl_emoji = "PROGRESS", "#f59e0b", "📈"
    else:             lvl_name, lvl_color, lvl_emoji = "TRAINING", "#f43f5e", "🎯"

    best_hour  = hr_g.loc[hr_g["pnl"].idxmax(), "hour"] if len(hr_g) else 0
    worst_hour = hr_g.loc[hr_g["pnl"].idxmin(), "hour"] if len(hr_g) else 0
    best_sym   = sym_g.iloc[0]["symbol"] if len(sym_g) else "—"
    worst_sym  = sym_g.iloc[-1]["symbol"] if len(sym_g) else "—"

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
    font-size="{int(size*0.07)}" fill="#334155">{pct:.0f}%</text>
</svg>"""

    st.markdown("""
<style>
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.hud-container { background:radial-gradient(ellipse at center,#050810 0%,#020408 100%);
  border:1px solid #0f1923; border-radius:16px; padding:28px; position:relative; overflow:hidden; }
.hud-container::before { content:''; position:absolute; top:0;left:0;right:0; height:1px;
  background:linear-gradient(90deg,transparent,#2dd4bf44,#2dd4bf,#2dd4bf44,transparent); }
.hud-stat { background:#0a0f1a; border:1px solid #1e2a3a; border-radius:8px;
  padding:12px 16px; display:flex; justify-content:space-between; align-items:center; }
.hud-label { font-size:9px; color:#334155; text-transform:uppercase; letter-spacing:0.12em; font-weight:600; }
.hud-val { font-family:'JetBrains Mono',monospace; font-size:14px; font-weight:700; }
.hud-online { display:inline-block; width:6px; height:6px; background:#10b981;
  border-radius:50%; animation:blink 2s infinite; margin-right:6px; }
</style>""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="hud-container">
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
