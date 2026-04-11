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
    font-size: 28px;
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
    border-bottom: 1px solid #1e2a3a;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    color: #475569;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.05em;
    padding: 12px 20px;
    border-radius: 0;
    text-transform: uppercase;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #2dd4bf !important;
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

hr { border-color: #1e2a3a; }
p, span, div { color: #e2e8f0; }
h1, h2, h3 { color: #f1f5f9; }
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
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(color="#64748b", family="JetBrains Mono", size=11),
    margin=dict(l=16, r=16, t=24, b=16),
    xaxis=dict(gridcolor="#1e2a3a", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e2a3a", showgrid=True, zeroline=False),
)
GREEN  = "#22c55e"
RED    = "#ef4444"
TEAL   = "#2dd4bf"
BLUE   = "#3b82f6"
AMBER  = "#f59e0b"
PURPLE = "#8b5cf6"
MUTED  = "#475569"

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="crz-header">
  <div>
    <div class="crz-logo">CRZ <span>Kaizen</span> Journal</div>
    <div class="crz-tagline">Mejora continua · Trading consciente</div>
  </div>
  <div style="font-size:11px;color:#475569;">改善 · 1% mejor cada día</div>
</div>
""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Sube tu historial MT5",
    type=["xlsx", "xls"],
    label_visibility="collapsed"
)

if not uploaded:
    st.markdown("""
<div class="upload-zone">
  <div style="font-size:48px;margin-bottom:16px;">📊</div>
  <div style="font-size:20px;font-weight:600;color:#f1f5f9;margin-bottom:8px;">Analiza tu trading</div>
  <div style="font-size:14px;color:#64748b;margin-bottom:4px;">Sube tu historial exportado desde MetaTrader 5</div>
  <div style="font-size:12px;color:#334155;">MT5 → Historial → Click derecho → Guardar como informe (.xlsx)</div>
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
st.markdown(f"""
<div style="background:#0d1117;border:1px solid #1e2a3a;border-left:4px solid {TEAL};
     border-radius:8px;padding:14px 20px;margin-bottom:24px;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-size:16px;font-weight:600;color:#f1f5f9;">{meta['trader'] or 'Mi Cuenta'}</div>
    <div style="font-size:11px;color:#475569;margin-top:2px;">{meta['cuenta']} · {meta['empresa']} · {meta['fecha']}</div>
  </div>
  <div style="display:flex;gap:24px;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">PnL Total</div>
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
    "📊 Dashboard", "📅 Calendario", "📋 Operaciones",
    "🎯 Por Símbolo", "⏰ Por Horario", "🧠 Kaizen Score"
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
        st.markdown("#### Curva de Equity")
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=df_s["close_dt"], y=df_s["equity"],
            mode="lines", name="Equity",
            line=dict(color=TEAL, width=2),
            fill="tozeroy",
            fillcolor="rgba(45,212,191,0.06)"
        ))
        # Underwater (drawdown fill)
        peak = df_s["equity"].cummax()
        fig_eq.add_trace(go.Scatter(
            x=df_s["close_dt"], y=peak,
            mode="lines", name="Peak",
            line=dict(color=MUTED, width=1, dash="dot"),
            showlegend=False
        ))
        fig_eq.add_hline(y=0, line_dash="dash", line_color=MUTED, opacity=0.4)
        fig_eq.update_layout(**LAYOUT, height=260)
        st.plotly_chart(fig_eq, use_container_width=True)

    with col_daily:
        st.markdown("#### PnL Diario")
        daily = df_s.groupby("close_date")["pnl_net"].sum().reset_index()
        daily.columns = ["fecha", "pnl"]
        colors_bar = [GREEN if v >= 0 else RED for v in daily["pnl"]]
        fig_daily = go.Figure(go.Bar(
            x=daily["fecha"], y=daily["pnl"],
            marker_color=colors_bar,
            hovertemplate="%{x}<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        fig_daily.add_hline(y=0, line_color=MUTED, opacity=0.4)
        fig_daily.update_layout(**LAYOUT, height=260)
        st.plotly_chart(fig_daily, use_container_width=True)

    # Win/Loss distribution + RR ratio
    col_wl, col_rr = st.columns(2)

    with col_wl:
        st.markdown("#### Distribución Ganancia / Pérdida")
        wins  = df[df.profit > 0]["profit"].tolist()
        losses= df[df.profit < 0]["profit"].tolist()
        fig_wl = go.Figure()
        fig_wl.add_trace(go.Histogram(x=wins,   name="Ganadoras", marker_color=GREEN, opacity=0.7, nbinsx=20))
        fig_wl.add_trace(go.Histogram(x=losses, name="Perdedoras", marker_color=RED,   opacity=0.7, nbinsx=20))
        fig_wl.update_layout(**LAYOUT, height=220, barmode="overlay")
        st.plotly_chart(fig_wl, use_container_width=True)

    with col_rr:
        st.markdown("#### Avg Win vs Avg Loss")
        fig_rr = go.Figure(go.Bar(
            x=["Ganancia Media", "Pérdida Media"],
            y=[stats["avg_win"], abs(stats["avg_loss"])],
            marker_color=[GREEN, RED],
            text=[f"${stats['avg_win']:,.2f}", f"${abs(stats['avg_loss']):,.2f}"],
            textposition="outside"
        ))
        rr = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
        fig_rr.add_annotation(
            x=0.5, y=0.9, xref="paper", yref="paper",
            text=f"RR Ratio: {rr:.2f}",
            font=dict(size=14, color=TEAL), showarrow=False
        )
        fig_rr.update_layout(**LAYOUT, height=220, showlegend=False)
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

    months = sorted(daily_cal["close_date"].dt.to_period("M").unique(), reverse=True)
    sel_month = st.selectbox(
        "Mes",
        options=[str(m) for m in months],
        label_visibility="collapsed"
    )

    y, m = int(sel_month[:4]), int(sel_month[5:7])
    month_data = daily_cal[daily_cal["close_date"].dt.to_period("M") == sel_month]
    day_map = {row["close_date"].day: row for _, row in month_data.iterrows()}

    days_in_month = calendar.monthrange(y, m)[1]
    first_weekday = calendar.monthrange(y, m)[0]  # 0=Mon
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    # Header
    cols_h = st.columns(7)
    for i, d in enumerate(day_names):
        cols_h[i].markdown(f"<div style='text-align:center;font-size:11px;color:#475569;font-weight:600;padding:6px 0;'>{d}</div>", unsafe_allow_html=True)

    # Grid
    total_cells = first_weekday + days_in_month
    rows_needed = (total_cells + 6) // 7

    cell = 0
    for week in range(rows_needed):
        cols = st.columns(7)
        for wd in range(7):
            day_num = cell - first_weekday + 1
            if cell < first_weekday or day_num > days_in_month:
                cols[wd].markdown("<div class='cal-day empty'>·</div>", unsafe_allow_html=True)
            else:
                if day_num in day_map:
                    row = day_map[day_num]
                    pnl = row["pnl"]
                    ops = row["ops"]
                    cls = "win" if pnl >= 0 else "loss"
                    color = GREEN if pnl >= 0 else RED
                    cols[wd].markdown(f"""
<div class='cal-day {cls}'>
  <div style='font-size:11px;color:#94a3b8;font-weight:600;'>{day_num}</div>
  <div style='font-family:JetBrains Mono;font-size:11px;color:{color};font-weight:600;'>{pnl:+,.0f}$</div>
  <div style='font-size:9px;color:#475569;'>{ops} ops</div>
</div>""", unsafe_allow_html=True)
                else:
                    cols[wd].markdown(f"""
<div class='cal-day'>
  <div style='font-size:11px;color:#334155;'>{day_num}</div>
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
            if val > 0: return "color: #22c55e; font-weight: 600"
            if val < 0: return "color: #ef4444; font-weight: 600"
        return "color: #94a3b8"

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
        fig_sym = go.Figure(go.Bar(
            x=sym_g["symbol"],
            y=sym_g["PnL"],
            marker_color=[GREEN if v >= 0 else RED for v in sym_g["PnL"]],
            text=[f"${v:+,.0f}" for v in sym_g["PnL"]],
            textposition="outside",
            hovertemplate="%{x}<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        fig_sym.update_layout(**LAYOUT, height=280, title="PnL por Símbolo")
        st.plotly_chart(fig_sym, use_container_width=True)

    with col_wr:
        fig_wr = go.Figure(go.Bar(
            x=sym_g["symbol"],
            y=sym_g["Win_Rate"],
            marker_color=BLUE,
            text=[f"{v:.0f}%" for v in sym_g["Win_Rate"]],
            textposition="outside",
        ))
        fig_wr.add_hline(y=50, line_dash="dash", line_color=MUTED, opacity=0.5)
        fig_wr.update_layout(**LAYOUT, height=280, title="Win Rate por Símbolo")
        fig_wr.update_yaxes(range=[0, 105], ticksuffix="%")
        st.plotly_chart(fig_wr, use_container_width=True)

    st.dataframe(
        sym_g[["symbol","Ops","Ganadoras","Win_Rate","PnL","Factor","Mejor","Peor"]]
        .rename(columns={"symbol":"Símbolo","Win_Rate":"Win Rate %","Factor":"Factor Ben."})
        .style
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
        fig_hr.add_trace(go.Bar(
            x=hr_g["hour"], y=hr_g["pnl"],
            marker_color=[GREEN if v >= 0 else RED for v in hr_g["pnl"]],
            name="PnL", yaxis="y1",
            hovertemplate="Hora %{x}:00<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        fig_hr.add_trace(go.Scatter(
            x=hr_g["hour"], y=hr_g["win_rate"],
            mode="lines+markers", name="Win Rate",
            line=dict(color=TEAL, width=2),
            yaxis="y2",
            hovertemplate="Win Rate: %{y:.1f}%<extra></extra>"
        ))
        fig_hr.update_layout(
            **LAYOUT, height=280,
            title="PnL y Win Rate por Hora",
            yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                       gridcolor="transparent", color=TEAL)
        )
        st.plotly_chart(fig_hr, use_container_width=True)

    with col_h2:
        fig_wd = go.Figure()
        fig_wd.add_trace(go.Bar(
            x=wd_g["weekday"], y=wd_g["pnl"],
            marker_color=[GREEN if v >= 0 else RED for v in wd_g["pnl"]],
            name="PnL",
            hovertemplate="%{x}<br>PnL: $%{y:+,.2f}<extra></extra>"
        ))
        fig_wd.update_layout(**LAYOUT, height=280, title="PnL por Día de Semana")
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
# TAB KAIZEN SCORE
# ══════════════════════════════════════════════════════════════════════════════
with tab_kaizen:
    st.markdown("#### Tu Kaizen Score — Mejora Continua")

    score = stats["kaizen_score"]
    if score >= 80:   nivel, color_s, emoji = "Excelente", GREEN, "🏆"
    elif score >= 60: nivel, color_s, emoji = "Bueno", TEAL, "📈"
    elif score >= 40: nivel, color_s, emoji = "En desarrollo", AMBER, "⚡"
    else:             nivel, color_s, emoji = "Necesita trabajo", RED, "🎯"

    col_score, col_breakdown = st.columns([1, 2])

    with col_score:
        # Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x":[0,1],"y":[0,1]},
            number={"font":{"size":48,"color":color_s,"family":"JetBrains Mono"},"suffix":"/100"},
            gauge={
                "axis":{"range":[0,100],"tickcolor":MUTED,"tickfont":{"color":MUTED}},
                "bar":{"color":color_s,"thickness":0.25},
                "bgcolor":"#0d1117",
                "borderwidth":0,
                "steps":[
                    {"range":[0,40],"color":"#2d0a0a"},
                    {"range":[40,60],"color":"#1c1a06"},
                    {"range":[60,80],"color":"#052e16"},
                    {"range":[80,100],"color":"#042f2e"},
                ],
                "threshold":{"line":{"color":color_s,"width":3},"thickness":0.75,"value":score}
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
            margin=dict(l=20,r=20,t=20,b=20), height=260
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f"""
<div style='text-align:center;padding:8px;'>
  <div style='font-size:32px;'>{emoji}</div>
  <div style='font-size:18px;font-weight:700;color:{color_s};'>{nivel}</div>
  <div style='font-size:12px;color:#475569;margin-top:4px;'>改善 · Mejora continua</div>
</div>""", unsafe_allow_html=True)

    with col_breakdown:
        st.markdown("##### Desglose del Score")
        wr_score  = min(stats["win_rate"] / 60 * 30, 30)
        pf_score  = min(stats["pfactor"] / 2 * 30, 30)
        rr_ratio  = abs(stats["avg_win"] / stats["avg_loss"]) if stats["avg_loss"] else 0
        rr_score  = min(rr_ratio / 2 * 20, 20)
        dd_score  = max(20 + stats["max_dd"] / 5, 0)

        metrics_score = [
            ("Win Rate", wr_score, 30, f"{stats['win_rate']:.1f}% (objetivo >60%)", BLUE),
            ("Factor Beneficio", pf_score, 30, f"{stats['pfactor']:.2f} (objetivo >2.0)", TEAL),
            ("Risk/Reward", rr_score, 20, f"{rr_ratio:.2f} (objetivo >2.0)", PURPLE),
            ("Control DD", dd_score, 20, f"{stats['max_dd']:.1f}% máx drawdown", AMBER),
        ]

        for name, val, max_val, desc, col in metrics_score:
            pct = val / max_val * 100
            st.markdown(f"""
<div style='margin-bottom:16px;'>
  <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
    <span style='font-size:12px;font-weight:600;color:#f1f5f9;'>{name}</span>
    <span style='font-family:JetBrains Mono;font-size:12px;color:{col};'>{val:.1f}/{max_val}</span>
  </div>
  <div style='background:#1e2a3a;border-radius:4px;height:8px;overflow:hidden;'>
    <div style='background:{col};width:{pct}%;height:100%;border-radius:4px;transition:width 0.3s;'></div>
  </div>
  <div style='font-size:10px;color:#475569;margin-top:3px;'>{desc}</div>
</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("##### Plan Kaizen — Áreas de Mejora")

    suggestions = []
    if stats["win_rate"] < 50:
        suggestions.append(("🎯", "Win Rate bajo el 50%", "Revisa tus entradas. Sé más selectivo — menos operaciones pero de mayor calidad.", RED))
    if stats["pfactor"] < 1.5:
        suggestions.append(("⚖️", "Factor Beneficio bajo", "Trabaja el ratio riesgo/recompensa. Deja correr más las ganadoras y corta antes las perdedoras.", AMBER))
    if rr_ratio < 1.5:
        suggestions.append(("📏", "RR Ratio mejorable", "Busca setups con mínimo 1:2 de RR. Si tu stop es 20 pips, tu objetivo debe ser 40 pips.", AMBER))
    if stats["max_dd"] < -10:
        suggestions.append(("🛡️", "Drawdown elevado", "Reduce el tamaño de posición. El control del riesgo es la base de la consistencia.", RED))

    # Best hour
    best_hour = hr_g.loc[hr_g["pnl"].idxmax(), "hour"] if len(hr_g) else 0
    worst_hour = hr_g.loc[hr_g["pnl"].idxmin(), "hour"] if len(hr_g) else 0
    suggestions.append(("⏰", f"Tu mejor hora: {best_hour}:00", f"Concentra tus operaciones en tu horario más rentable. Evita operar a las {worst_hour}:00.", TEAL))

    best_sym = sym_g.iloc[0]["symbol"] if len(sym_g) else "—"
    worst_sym = sym_g.iloc[-1]["symbol"] if len(sym_g) else "—"
    suggestions.append(("🎯", f"Mejor símbolo: {best_sym}", f"Especialízate en lo que mejor te funciona. Considera reducir exposición en {worst_sym}.", GREEN))

    for icon, title, desc, col in suggestions:
        st.markdown(f"""
<div style='background:#0d1117;border:1px solid #1e2a3a;border-left:4px solid {col};
     border-radius:6px;padding:14px 16px;margin-bottom:10px;'>
  <div style='font-size:13px;font-weight:600;color:#f1f5f9;margin-bottom:4px;'>{icon} {title}</div>
  <div style='font-size:12px;color:#64748b;'>{desc}</div>
</div>""", unsafe_allow_html=True)
