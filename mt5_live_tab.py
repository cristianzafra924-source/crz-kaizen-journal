"""
CRZ Kaizen Journal — Módulo Live MT5
=====================================
Añade esto a tu app.py:

    from mt5_live_tab import show_live_tab
    # Dentro del bloque de tabs:
    tab_live = st.tabs([..., "⚡ Live MT5"])
    with tab_live:
        show_live_tab()

El archivo mt5_live.json debe estar en la misma carpeta que app.py,
generado por mt5_bridge.py corriendo en tu PC Windows.
"""

import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

LIVE_FILE    = "mt5_live.json"
REFRESH_SECS = 5   # auto-refresh cada N segundos

GREEN  = "#10b981"
RED    = "#f43f5e"
TEAL   = "#2dd4bf"
AMBER  = "#f59e0b"
PURPLE = "#a78bfa"

LAYOUT = dict(
    paper_bgcolor="#080c14", plot_bgcolor="#080c14",
    font=dict(color="#64748b", family="Inter, sans-serif", size=11),
    margin=dict(l=16, r=16, t=32, b=16),
    xaxis=dict(gridcolor="#0f1923", showgrid=True, zeroline=False,
               linecolor="#1e2a3a", tickcolor="#1e2a3a"),
    yaxis=dict(gridcolor="#0f1923", showgrid=True, zeroline=False,
               linecolor="#1e2a3a", tickcolor="#1e2a3a"),
)


def load_live_data() -> dict | None:
    path = Path(LIVE_FILE)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def time_ago(ts_str: str) -> str:
    try:
        ts  = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        sec = int((datetime.now() - ts).total_seconds())
        if sec < 60:   return f"hace {sec}s"
        if sec < 3600: return f"hace {sec//60}m"
        return f"hace {sec//3600}h"
    except:
        return ts_str


def show_live_tab():
    # ── Auto-refresh ──────────────────────────────────────────────────────────
    st.markdown(
        f'<meta http-equiv="refresh" content="{REFRESH_SECS}">',
        unsafe_allow_html=True
    )

    data = load_live_data()

    # ── Sin datos ─────────────────────────────────────────────────────────────
    if data is None:
        st.markdown("""
<div style="background:#0d1117;border:1.5px dashed #1e2a3a;border-radius:12px;
     padding:48px;text-align:center;margin:32px auto;max-width:600px;">
  <div style="font-size:40px;margin-bottom:16px;">📡</div>
  <div style="font-size:18px;font-weight:600;color:#f1f5f9;margin-bottom:8px;">
    Bridge MT5 no activo</div>
  <div style="font-size:13px;color:#64748b;margin-bottom:16px;">
    El archivo <code>mt5_live.json</code> no existe todavía.</div>
  <div style="font-size:12px;color:#64748b;text-align:left;
       background:#050810;border-radius:8px;padding:16px;font-family:monospace;">
    1. Instala la librería:<br>
    &nbsp;&nbsp;<span style="color:#4ade80;">pip install MetaTrader5</span><br><br>
    2. Copia <b>mt5_bridge.py</b> a tu PC Windows<br><br>
    3. Abre MT5 y ejecútalo:<br>
    &nbsp;&nbsp;<span style="color:#4ade80;">python mt5_bridge.py</span><br><br>
    4. Esta pantalla se actualizará sola cada 5s ⚡
  </div>
</div>""", unsafe_allow_html=True)
        return

    # ── Error de conexión ─────────────────────────────────────────────────────
    if data.get("estado") == "error":
        st.error(f"❌ Bridge error: {data.get('mensaje','desconocido')} — {time_ago(data.get('timestamp',''))}")
        return

    cuenta = data.get("cuenta", {})
    posiciones = data.get("posiciones_abiertas", [])
    deals_hoy  = data.get("deals_hoy", [])
    pnl_dia    = data.get("pnl_dia", 0)
    historial  = data.get("historial", [])
    ts         = data.get("timestamp", "")

    balance  = cuenta.get("balance", 0)
    equity   = cuenta.get("equity", 0)
    profit_open = cuenta.get("profit_abierto", 0)
    margin_lvl  = cuenta.get("margin_nivel", 0)

    # ── Header live ───────────────────────────────────────────────────────────
    estado_color = "#4ade80" if equity >= balance else "#f43f5e"
    st.markdown(f"""
<div style="background:#111827;border:1px solid #2d3748;border-left:4px solid #4ade80;
     border-radius:8px;padding:12px 20px;margin-bottom:20px;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-size:15px;font-weight:700;color:#f1f5f9;">
      ⚡ {cuenta.get('nombre','—')} 
      <span style="font-size:11px;color:#94a3b8;font-weight:400;">
        #{cuenta.get('login','')} · {cuenta.get('servidor','')}
      </span>
    </div>
    <div style="font-size:10px;color:#64748b;margin-top:2px;">
      Última actualización: {time_ago(ts)} · 
      Apalancamiento 1:{cuenta.get('apalancamiento','')} · 
      {cuenta.get('divisa','')}
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:8px;">
    <div style="width:8px;height:8px;border-radius:50%;background:#4ade80;
         animation:pulse 2s infinite;"></div>
    <span style="font-size:11px;color:#4ade80;font-weight:700;">EN VIVO</span>
  </div>
</div>
<style>
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
</style>
""", unsafe_allow_html=True)

    # ── KPIs cuenta ───────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpis = [
        (k1, "Balance",        f"${balance:,.2f}",      "#f1f5f9"),
        (k2, "Equity",         f"${equity:,.2f}",       "#4ade80" if equity >= balance else "#f43f5e"),
        (k3, "Profit Abierto", f"${profit_open:+,.2f}", "#4ade80" if profit_open >= 0 else "#f43f5e"),
        (k4, "PnL Hoy",        f"${pnl_dia:+,.2f}",     "#4ade80" if pnl_dia >= 0 else "#f43f5e"),
        (k5, "Posiciones",     str(len(posiciones)),    TEAL),
        (k6, "Nivel Margen",   f"{margin_lvl:.0f}%",    "#4ade80" if margin_lvl > 200 else AMBER if margin_lvl > 100 else RED),
    ]
    for col, label, val, color in kpis:
        col.markdown(f"""
<div style="background:#111827;border:1px solid #2d3748;border-radius:8px;padding:14px 16px;">
  <div style="font-size:9px;color:#94a3b8;text-transform:uppercase;
       letter-spacing:.12em;font-weight:600;margin-bottom:4px;">{label}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:17px;
       font-weight:700;color:{color};">{val}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Posiciones abiertas ───────────────────────────────────────────────────
    col_pos, col_eq = st.columns([1, 1])

    with col_pos:
        st.markdown("#### Posiciones abiertas")
        if not posiciones:
            st.markdown("<div style='color:#94a3b8;font-size:13px;padding:16px 0;'>Sin posiciones abiertas</div>", unsafe_allow_html=True)
        else:
            for p in posiciones:
                pnl_c = "#4ade80" if p["pnl_net"] >= 0 else "#f43f5e"
                tipo_c = "#3b82f6" if p["type"] == "buy" else "#f59e0b"
                st.markdown(f"""
<div style="background:#111827;border:1px solid #2d3748;border-radius:7px;
     padding:10px 14px;margin-bottom:6px;display:flex;
     justify-content:space-between;align-items:center;">
  <div>
    <span style="font-size:13px;font-weight:700;color:#f1f5f9;">{p['symbol']}</span>
    <span style="font-size:10px;color:{tipo_c};font-weight:700;
         margin-left:8px;text-transform:uppercase;">{p['type']}</span>
    <span style="font-size:10px;color:#94a3b8;margin-left:8px;">{p['volume']} lots</span>
  </div>
  <div style="text-align:right;">
    <div style="font-family:'JetBrains Mono';font-size:14px;
         font-weight:700;color:{pnl_c};">${p['pnl_net']:+,.2f}</div>
    <div style="font-size:9px;color:#94a3b8;">
      {p['price_open']} → {p['price_current']}
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Mini equity curve live ────────────────────────────────────────────────
    with col_eq:
        st.markdown("#### Equity curve (historial)")
        if historial:
            df_h = pd.DataFrame(historial)
            df_h["time"] = pd.to_datetime(df_h["time"])
            df_h = df_h.sort_values("time").reset_index(drop=True)
            df_h["equity_cum"] = df_h["pnl_net"].cumsum()
            capital = st.session_state.get("capital_manual", balance)
            df_h["rent"] = df_h["equity_cum"] / capital * 100

            last = df_h["rent"].iloc[-1]
            lc   = "#4ade80" if last >= 0 else "#f43f5e"

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_h["time"], y=df_h["rent"],
                mode="lines", line=dict(color=lc, width=1.8),
                fill="tozeroy", fillcolor=f"rgba(74,222,128,0.15)" if last >= 0 else "rgba(244,63,94,0.15)",
                hovertemplate="<b>%{x|%d %b %H:%M}</b><br>%{y:.2f}%<extra></extra>"
            ))
            fig.add_hline(y=0, line_color="rgba(255,255,255,0.08)", line_width=1)
            fig.update_layout(**LAYOUT, height=240, showlegend=False,
                margin=dict(l=40, r=16, t=16, b=32))
            fig.update_yaxes(ticksuffix="%", tickfont=dict(color="#6b7280", size=10))
            fig.update_xaxes(tickfont=dict(color="#6b7280", size=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("<div style='color:#94a3b8;font-size:13px;padding:32px 0;text-align:center;'>Sin historial disponible</div>", unsafe_allow_html=True)

    # ── Deals del día ─────────────────────────────────────────────────────────
    st.markdown("#### Operaciones de hoy")
    if not deals_hoy:
        st.markdown("<div style='color:#94a3b8;font-size:13px;padding:12px 0;'>Sin operaciones hoy</div>", unsafe_allow_html=True)
    else:
        df_deals = pd.DataFrame(deals_hoy)
        df_deals = df_deals[["time","symbol","type","volume","price","profit","commission","swap","pnl_net"]]
        df_deals.columns = ["Hora","Símbolo","Tipo","Vol","Precio","Beneficio","Comisión","Swap","PnL Neto"]

        def color_p(val):
            if isinstance(val, (int, float)):
                if val > 0: return "color:#16a34a;font-weight:600"
                if val < 0: return "color:#dc2626;font-weight:600"
            return ""

        st.dataframe(
            df_deals.style
                .map(color_p, subset=["Beneficio","PnL Neto"])
                .format({"Precio":"{:.5g}","Beneficio":"{:+.2f}",
                         "Comisión":"{:.2f}","Swap":"{:.2f}","PnL Neto":"{:+.2f}"}),
            use_container_width=True, height=min(300, 60 + len(df_deals)*35)
        )

        # Mini resumen del día
        wins_h = sum(1 for d in deals_hoy if d["profit"] > 0)
        st.markdown(f"""
<div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;">
  <span style="font-size:11px;color:#94a3b8;">
    Operaciones hoy: <b style="color:#f1f5f9;">{len(deals_hoy)}</b>
  </span>
  <span style="font-size:11px;color:#94a3b8;">
    Ganadoras: <b style="color:#4ade80;">{wins_h}</b>
  </span>
  <span style="font-size:11px;color:#94a3b8;">
    Perdedoras: <b style="color:#f43f5e;">{len(deals_hoy)-wins_h}</b>
  </span>
  <span style="font-size:11px;color:#94a3b8;">
    PnL total hoy: <b style="color:{'#4ade80' if pnl_dia>=0 else '#f43f5e'};">${pnl_dia:+,.2f}</b>
  </span>
</div>""", unsafe_allow_html=True)
