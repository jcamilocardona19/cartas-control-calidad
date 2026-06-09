"""
Cartas de Control de Calidad
Universidad Tecnológica de Pereira
Herramienta Didáctica Web — Streamlit
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, random

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cartas de Control de Calidad — UTP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  ESTILOS CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Fuentes y base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Fondo principal */
    .stApp { background-color: #f8fafc; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0f2440 100%);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stRadio label { color: #e2e8f0 !important; }

    /* Header personalizado */
    .header-container {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        padding: 20px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 20px;
        color: white;
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    .header-sub {
        font-size: 0.95rem;
        color: #bfdbfe;
        margin: 4px 0 0 0;
    }

    /* Tarjetas métricas */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    .metric-value.ok    { color: #16a34a; }
    .metric-value.warn  { color: #d97706; }
    .metric-value.bad   { color: #dc2626; }

    /* Alertas */
    .alert-ok    { background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:12px 16px; color:#166534; margin:8px 0; }
    .alert-warn  { background:#fffbeb; border:1px solid #fcd34d; border-radius:8px; padding:12px 16px; color:#92400e; margin:8px 0; }
    .alert-error { background:#fef2f2; border:1px solid #fca5a5; border-radius:8px; padding:12px 16px; color:#991b1b; margin:8px 0; }
    .alert-info  { background:#eff6ff; border:1px solid #93c5fd; border-radius:8px; padding:12px 16px; color:#1e40af; margin:8px 0; }

    /* Fórmulas */
    .formula-box {
        background: #f1f5f9;
        border-left: 4px solid #2563eb;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        color: #1e3a5f;
        margin: 12px 0;
        line-height: 2;
    }

    /* Sección título */
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a5f;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }

    /* Quiz */
    .quiz-feedback-ok   { background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:14px; color:#166534; margin:8px 0; }
    .quiz-feedback-bad  { background:#fef2f2; border:1px solid #fca5a5; border-radius:8px; padding:14px; color:#991b1b; margin:8px 0; }

    /* Tabla bonita */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Botones */
    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 20px;
        transition: all 0.2s;
    }
    .stButton > button:hover { background: #1d4ed8; transform: translateY(-1px); }

    /* Info boxes teoría */
    .teoria-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .teoria-card h4 { color: #1e3a5f; margin-bottom: 10px; font-size: 1rem; }

    /* Zona distribución */
    .zona-bar {
        display: flex;
        border-radius: 8px;
        overflow: hidden;
        height: 44px;
        margin: 12px 0;
        font-size: 0.75rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CONSTANTES SPC
# ══════════════════════════════════════════════════════════════
XR_CONST = {
    2:  (1.880, 0.000, 3.267, 1.128),
    3:  (1.023, 0.000, 2.575, 1.693),
    4:  (0.729, 0.000, 2.282, 2.059),
    5:  (0.577, 0.000, 2.115, 2.326),
    6:  (0.483, 0.000, 2.004, 2.534),
    7:  (0.419, 0.076, 1.924, 2.704),
    8:  (0.373, 0.136, 1.864, 2.847),
    9:  (0.337, 0.184, 1.816, 2.970),
    10: (0.308, 0.223, 1.777, 3.078),
}

COLORES = {
    "azul":    "#2563eb",
    "rojo":    "#dc2626",
    "verde":   "#16a34a",
    "naranja": "#d97706",
    "gris":    "#64748b",
    "fondo":   "#f8fafc",
    "ucl":     "#ef4444",
    "lcl":     "#ef4444",
    "cl":      "#2563eb",
    "pts_ok":  "#2563eb",
    "pts_bad": "#dc2626",
}

# ══════════════════════════════════════════════════════════════
#  HEADER CON LOGO UTP
# ══════════════════════════════════════════════════════════════
def mostrar_header():
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        try:
            st.image("utp_logo.png", width=110)
        except:
            st.markdown("**UTP**")
    with col_titulo:
        st.markdown("""
        <div style="padding: 8px 0;">
            <div style="font-size:1.6rem; font-weight:700; color:#1e3a5f; line-height:1.2;">
                📊 Cartas de Control de Calidad
            </div>
            <div style="font-size:0.95rem; color:#64748b; margin-top:4px;">
                Universidad Tecnológica de Pereira &nbsp;·&nbsp; 
                Herramienta Didáctica Interactiva &nbsp;·&nbsp;
                Control Estadístico de Procesos
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:2px solid #2563eb;margin:8px 0 24px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SIDEBAR NAVEGACIÓN
# ══════════════════════════════════════════════════════════════
def sidebar_nav():
    with st.sidebar:
        try:
            st.image("utp_logo.png", width=140)
        except:
            pass
        st.markdown("---")
        st.markdown("### 📚 Navegación")
        modulo = st.radio(
            "",
            options=[
                "📘 Teoría y Fundamentos",
                "📈 Carta X̄-R",
                "📉 Carta p",
                "⚠️ Reglas de Nelson",
                "🎯 Quiz de Evaluación",
                "📄 Exportar Reporte",
            ],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.78rem; color:#94a3b8; line-height:1.8;">
        <b style="color:#bfdbfe;">Referencia normativa</b><br>
        ISO 7870-2<br>
        AIAG SPC Manual<br>
        Nelson (1984)<br><br>
        <b style="color:#bfdbfe;">Desarrollado en</b><br>
        Python · Streamlit · Plotly
        </div>
        """, unsafe_allow_html=True)
    return modulo

# ══════════════════════════════════════════════════════════════
#  UTILIDADES DE GRÁFICAS
# ══════════════════════════════════════════════════════════════
def color_punto(v, ucl, lcl):
    return COLORES["pts_bad"] if (v > ucl or v < lcl) else COLORES["pts_ok"]

def fig_xbar_r(xbars, rangos, ucl_x, cl_x, lcl_x, ucl_r, cl_r, lcl_r):
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Carta X̄ — Promedio del subgrupo", "Carta R — Rango del subgrupo"),
        vertical_spacing=0.14,
    )
    idx = list(range(1, len(xbars)+1))
    sigma_x = (ucl_x - cl_x) / 3

    # ── Zonas carta X̄ ──
    for z, c, name in [
        (2, "rgba(254,202,202,0.25)", "Zona A (>2σ)"),
        (1, "rgba(254,240,138,0.20)", "Zona B (1-2σ)"),
    ]:
        fig.add_trace(go.Scatter(
            x=idx+idx[::-1],
            y=[cl_x+z*sigma_x]*len(idx)+[cl_x+(z-1)*sigma_x]*len(idx),
            fill='toself', fillcolor=c,
            line=dict(width=0), showlegend=(z==2), name=name, opacity=0.7,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=idx+idx[::-1],
            y=[cl_x-z*sigma_x]*len(idx)+[cl_x-(z-1)*sigma_x]*len(idx),
            fill='toself', fillcolor=c,
            line=dict(width=0), showlegend=False, opacity=0.7,
        ), row=1, col=1)

    # ── Líneas de control X̄ ──
    for val, color, name, dash in [
        (ucl_x, COLORES["ucl"], f"UCL = {ucl_x:.3f}", "dash"),
        (cl_x,  COLORES["cl"],  f"CL  = {cl_x:.3f}",  "solid"),
        (lcl_x, COLORES["lcl"], f"LCL = {lcl_x:.3f}", "dash"),
    ]:
        fig.add_hline(y=val, line_color=color, line_dash=dash,
                      line_width=2, row=1, col=1,
                      annotation_text=name,
                      annotation_position="right",
                      annotation_font_color=color)

    # ── Puntos y línea X̄ ──
    colores_x = [color_punto(v, ucl_x, lcl_x) for v in xbars]
    fig.add_trace(go.Scatter(
        x=idx, y=xbars, mode='lines+markers',
        name="X̄", line=dict(color="#64748b", width=1.5),
        marker=dict(color=colores_x, size=9, line=dict(color="white", width=1.5)),
        hovertemplate="Subgrupo %{x}<br>X̄ = %{y:.4f}<extra></extra>",
    ), row=1, col=1)

    # ── Líneas control R ──
    for val, color, name, dash in [
        (ucl_r, COLORES["ucl"], f"UCL = {ucl_r:.3f}", "dash"),
        (cl_r,  COLORES["cl"],  f"CL  = {cl_r:.3f}",  "solid"),
        (lcl_r, COLORES["lcl"], f"LCL = {lcl_r:.3f}", "dash"),
    ]:
        fig.add_hline(y=val, line_color=color, line_dash=dash,
                      line_width=2, row=2, col=1,
                      annotation_text=name,
                      annotation_position="right",
                      annotation_font_color=color)

    # ── Puntos y línea R ──
    colores_r = [color_punto(v, ucl_r, lcl_r) for v in rangos]
    fig.add_trace(go.Scatter(
        x=idx, y=rangos, mode='lines+markers',
        name="R", line=dict(color="#64748b", width=1.5),
        marker=dict(color=colores_r, size=9,
                    symbol=["circle" if c==COLORES["pts_ok"] else "diamond" for c in colores_r],
                    line=dict(color="white", width=1.5)),
        hovertemplate="Subgrupo %{x}<br>R = %{y:.4f}<extra></extra>",
    ), row=2, col=1)

    fig.update_layout(
        height=560, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=12, color="#1e293b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=60, r=120, t=60, b=40),
    )
    fig.update_xaxes(gridcolor="#f1f5f9", title_text="Subgrupo", row=1, col=1)
    fig.update_xaxes(gridcolor="#f1f5f9", title_text="Subgrupo", row=2, col=1)
    fig.update_yaxes(gridcolor="#f1f5f9", row=1, col=1)
    fig.update_yaxes(gridcolor="#f1f5f9", row=2, col=1)
    return fig

def fig_carta_p(p_i, ucl_i, cl, lcl_i, idx):
    fig = go.Figure()
    # Banda de control
    fig.add_trace(go.Scatter(
        x=list(idx)+list(idx[::-1]),
        y=list(ucl_i)+list(lcl_i[::-1]),
        fill='toself', fillcolor='rgba(239,68,68,0.08)',
        line=dict(width=0), name="Banda ±3σ",
    ))
    # Líneas
    fig.add_trace(go.Scatter(x=list(idx), y=list(ucl_i), mode='lines',
        line=dict(color=COLORES["ucl"], dash="dash", width=2),
        name=f"UCL ≈ {ucl_i.mean()*100:.2f}%"))
    fig.add_hline(y=cl, line_color=COLORES["cl"], line_width=2,
                  annotation_text=f"p̄ = {cl*100:.3f}%",
                  annotation_position="right",
                  annotation_font_color=COLORES["cl"])
    fig.add_trace(go.Scatter(x=list(idx), y=list(lcl_i), mode='lines',
        line=dict(color=COLORES["lcl"], dash="dash", width=2),
        name=f"LCL ≈ {lcl_i.mean()*100:.2f}%"))
    # Puntos
    colores = [COLORES["pts_bad"] if (v>u or v<l) else COLORES["pts_ok"]
               for v,u,l in zip(p_i, ucl_i, lcl_i)]
    fig.add_trace(go.Scatter(
        x=list(idx), y=list(p_i), mode='lines+markers',
        name="pᵢ", line=dict(color="#64748b", width=1.5),
        marker=dict(color=colores, size=9, line=dict(color="white", width=1.5)),
        hovertemplate="Período %{x}<br>p = %{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=12, color="#1e293b"),
        yaxis=dict(tickformat=".1%", gridcolor="#f1f5f9"),
        xaxis=dict(gridcolor="#f1f5f9", title="Período"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=60, r=120, t=40, b=40),
    )
    return fig

# ══════════════════════════════════════════════════════════════
#  MÓDULO 1 — TEORÍA
# ══════════════════════════════════════════════════════════════
def modulo_teoria():
    st.markdown('<div class="section-title">📘 Teoría y Fundamentos del SPC</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "¿Qué es una Carta de Control?",
        "Anatomía de la Carta",
        "Tipos de Cartas",
        "Proceso de Implementación",
    ])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="teoria-card">
            <h4>📌 Definición</h4>
            Una carta de control es una <b>gráfica de series de tiempo</b> que muestra 
            cómo varía una característica de calidad a lo largo del tiempo, 
            comparándola contra límites estadísticamente calculados.<br><br>
            Desarrollada por <b>Walter A. Shewhart en 1924</b> en los Laboratorios Bell (AT&T).
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="teoria-card">
            <h4>✅ Causa Común (aleatoria)</h4>
            Inherente al proceso. Siempre presente. El proceso está <b>bajo control</b>.<br>
            → No requiere acción correctiva sobre el proceso.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="teoria-card">
            <h4>🚨 Causa Especial (asignable)</h4>
            Evento inusual. Indica que algo cambió. El proceso está <b>fuera de control</b>.<br>
            → Requiere investigación y acción inmediata.
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="teoria-card">
            <h4>🎯 Objetivo principal</h4>
            Distinguir entre variación <b>normal</b> (siempre existe) y variación 
            <b>anormal</b> que indica un problema real en el proceso.<br><br>
            <b>Regla de los 3σ:</b> bajo distribución normal, el <b>99.73%</b> 
            de los datos caen dentro de ±3σ cuando el proceso es estable.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="teoria-card">
            <h4>📋 Referencias normativas</h4>
            • ISO 7870-2 — Cartas de Shewhart<br>
            • AIAG Statistical Process Control Manual<br>
            • Nelson (1984) — Reglas de detección<br>
            • ASQ — American Society for Quality
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### Componentes de toda carta de control")
        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown("""
            <div class="formula-box">
            UCL = X̿ + 3σ &nbsp;&nbsp; ← Límite Superior de Control<br>
            ─────────────────────────────────<br>
            CL  = X̿ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ← Línea Central (media)<br>
            ─────────────────────────────────<br>
            LCL = X̿ − 3σ &nbsp;&nbsp; ← Límite Inferior de Control
            </div>
            """, unsafe_allow_html=True)
            st.info("Los límites a **±3σ** significan que un proceso estable producirá puntos fuera de control solo el **0.27%** del tiempo (1 de cada 370 puntos), lo que es una falsa alarma.")

        with col2:
            st.markdown("#### Distribución de zonas (±1σ, ±2σ, ±3σ)")
            st.markdown("""
            <div style="display:flex; border-radius:8px; overflow:hidden; height:48px; margin:8px 0; font-size:0.7rem; font-weight:700; text-align:center;">
                <div style="flex:0.3; background:#fca5a5; display:flex; align-items:center; justify-content:center;">0.13%</div>
                <div style="flex:2.1; background:#fed7aa; display:flex; align-items:center; justify-content:center;">C 2.1%</div>
                <div style="flex:13.6; background:#fef08a; display:flex; align-items:center; justify-content:center;">Zona B 13.6%</div>
                <div style="flex:34.1; background:#bbf7d0; display:flex; align-items:center; justify-content:center;">Zona A — 34.13%</div>
                <div style="flex:34.1; background:#bbf7d0; display:flex; align-items:center; justify-content:center;">Zona A — 34.13%</div>
                <div style="flex:13.6; background:#fef08a; display:flex; align-items:center; justify-content:center;">Zona B 13.6%</div>
                <div style="flex:2.1; background:#fed7aa; display:flex; align-items:center; justify-content:center;">C 2.1%</div>
                <div style="flex:0.3; background:#fca5a5; display:flex; align-items:center; justify-content:center;">0.13%</div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#64748b; font-family:monospace; margin-top:4px;">
                <span>LCL (−3σ)</span><span>−2σ</span><span>−1σ</span><span>X̄</span><span>+1σ</span><span>+2σ</span><span>UCL (+3σ)</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### ¿Cuándo actuar?")
            st.markdown("""
            | Zona | % área | Acción |
            |------|--------|--------|
            | Zona A (±1σ) | 68.27% | Normal |
            | Zona B (±2σ) | 95.45% | Vigilar patrones |
            | Zona C (±3σ) | 99.73% | Límite de control |
            | Fuera de ±3σ | 0.27%  | 🚨 Investigar |
            """)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📏 Cartas para Variables (datos medibles)")
            st.markdown("""
            | Carta | Monitorea | Uso típico |
            |-------|-----------|------------|
            | **X̄-R** | Promedio y Rango | n ≤ 10, más usada |
            | **X̄-S** | Promedio y Desv. Est. | n > 10 |
            | **I-MR** | Individual y Rango móvil | n = 1 |
            """)
            st.info("Este módulo incluye la **Carta X̄-R**, la más utilizada en manufactura.")

        with col2:
            st.markdown("#### 🔢 Cartas para Atributos (pasa/no pasa)")
            st.markdown("""
            | Carta | Monitorea | Uso típico |
            |-------|-----------|------------|
            | **p**  | Proporción defectiva | n variable o fijo |
            | **np** | Número de defectivos | n constante |
            | **c**  | Número de defectos | Área fija |
            | **u**  | Defectos por unidad | Área variable |
            """)
            st.info("Este módulo incluye la **Carta p**, la más usada en inspección.")

    with tab4:
        pasos = [
            ("📥", "1. Recolectar", "Mínimo 20–25 subgrupos racionales. Tamaño de subgrupo constante (n = 4 o 5). Condiciones homogéneas dentro de cada subgrupo."),
            ("🧮", "2. Calcular", "Calcular X̄ᵢ y Rᵢ para cada subgrupo. Obtener X̿ (gran media) y R̄ (rango promedio). Aplicar constantes para calcular UCL y LCL."),
            ("📊", "3. Graficar", "Trazar puntos y líneas de control. Identificar visualmente patrones. Marcar puntos fuera de los límites."),
            ("🔍", "4. Analizar", "Aplicar Reglas de Nelson para detectar señales. Verificar estabilidad del proceso. Investigar subgrupos sospechosos."),
            ("🔧", "5. Actuar", "Investigar y eliminar causas especiales. Documentar acciones correctivas. Recalcular límites si se eliminan subgrupos."),
        ]
        cols = st.columns(5)
        for col, (icono, titulo, desc) in zip(cols, pasos):
            with col:
                st.markdown(f"""
                <div style="background:white; border:1px solid #e2e8f0; border-radius:10px;
                     padding:16px; text-align:center; height:180px; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                    <div style="font-size:2rem;">{icono}</div>
                    <div style="font-weight:700; color:#1e3a5f; font-size:0.9rem; margin:8px 0 6px;">{titulo}</div>
                    <div style="font-size:0.78rem; color:#64748b; line-height:1.5;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 2 — CARTA X̄-R
# ══════════════════════════════════════════════════════════════
def modulo_xbar():
    st.markdown('<div class="section-title">📈 Carta X̄-R — Variables Continuas</div>', unsafe_allow_html=True)

    with st.expander("📐 Ver fórmulas y constantes", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="formula-box">
            X̄ᵢ = (x₁+x₂+...+xₙ) / n<br>
            Rᵢ = max(xⱼ) − min(xⱼ)<br>
            X̿ = ΣX̄ᵢ / k<br>
            R̄ = ΣRᵢ / k<br>
            UCL_X̄ = X̿ + A₂·R̄<br>
            LCL_X̄ = X̿ − A₂·R̄<br>
            UCL_R  = D₄·R̄<br>
            LCL_R  = max(0, D₃·R̄)<br>
            σ̂ = R̄ / d₂
            </div>
            """, unsafe_allow_html=True)
        with col2:
            df_const = pd.DataFrame(XR_CONST, index=["A₂","D₃","D₄","d₂"]).T
            df_const.index.name = "n"
            st.dataframe(df_const.round(3), use_container_width=True)

    st.markdown("---")
    modo = st.radio("**¿Cómo deseas ingresar los datos?**",
                    ["🎲 Simular datos automáticamente", "✏️ Ingresar mis propios datos"],
                    horizontal=True)

    if "🎲" in modo:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            mu    = st.number_input("Media del proceso (μ)", value=100.0, step=1.0)
        with col2:
            sigma = st.number_input("Desviación estándar (σ)", value=2.5, min_value=0.1, step=0.5)
        with col3:
            n     = st.selectbox("Tamaño subgrupo (n)", options=list(range(2,11)), index=3)
        with col4:
            k     = st.number_input("N° de subgrupos (k)", value=20, min_value=10, max_value=30, step=1)

        anomalia = st.selectbox("Anomalía a simular", [
            "Sin anomalías (proceso estable)",
            "Corrimiento de media",
            "Tendencia creciente",
            "Punto fuera de control",
        ])

        if st.button("▶ Generar carta X̄-R", type="primary"):
            np.random.seed(None)
            datos = np.zeros((int(k), n))
            for i in range(int(k)):
                mu_act = mu
                if "Corrimiento" in anomalia and i >= int(k*0.6):
                    mu_act = mu + 2*sigma
                elif "Tendencia" in anomalia:
                    mu_act = mu + (i/k)*3*sigma
                obs = np.random.normal(mu_act, sigma, n)
                if "Punto" in anomalia and i == int(k*0.7):
                    obs[0] = mu + 4.5*sigma
                datos[i] = obs
            st.session_state["xbar_datos"] = datos

    else:
        col1, col2 = st.columns(2)
        with col1:
            n = st.selectbox("Tamaño subgrupo (n)", options=list(range(2,11)), index=3)
        with col2:
            k = st.number_input("N° de subgrupos", value=10, min_value=5, max_value=30)

        st.markdown(f"Ingresa **{n} valores** por subgrupo separados por espacio o coma:")
        datos_list = []
        valido = True
        for i in range(int(k)):
            entrada = st.text_input(f"Subgrupo {i+1}", key=f"sg_{i}",
                                    placeholder=f"Ej: {' '.join(['10.'+str(random.randint(0,9)) for _ in range(n)])}")
            if entrada:
                try:
                    vals = [float(x) for x in entrada.replace(',',' ').split()]
                    if len(vals) == n:
                        datos_list.append(vals)
                    else:
                        st.warning(f"Subgrupo {i+1}: necesitas exactamente {n} valores")
                        valido = False
                except:
                    st.error(f"Subgrupo {i+1}: solo números")
                    valido = False

        if st.button("▶ Calcular carta X̄-R", type="primary"):
            if len(datos_list) == int(k) and valido:
                st.session_state["xbar_datos"] = np.array(datos_list)
            else:
                st.warning(f"Completa los {int(k)} subgrupos correctamente.")

    # ── Mostrar resultados ──
    if "xbar_datos" in st.session_state:
        datos = st.session_state["xbar_datos"]
        k_r, n_r = datos.shape
        xbars  = datos.mean(axis=1)
        rangos = datos.max(axis=1) - datos.min(axis=1)
        xdbar  = xbars.mean()
        rbar   = rangos.mean()
        A2, D3, D4, d2 = XR_CONST[n_r]
        ucl_x = xdbar + A2*rbar
        lcl_x = xdbar - A2*rbar
        ucl_r = D4*rbar
        lcl_r = max(0.0, D3*rbar)
        sigma_est = rbar/d2

        fuera_x = [i for i,v in enumerate(xbars)  if v>ucl_x or v<lcl_x]
        fuera_r = [i for i,v in enumerate(rangos) if v>ucl_r or v<lcl_r]
        total_fuera = len(fuera_x)+len(fuera_r)

        st.markdown("---")
        st.markdown("### 📊 Estadísticos y Límites de Control")

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        stats = [
            (c1, "X̿ (Gran media)",   f"{xdbar:.4f}", ""),
            (c2, "R̄ (Rango medio)",  f"{rbar:.4f}",  ""),
            (c3, "UCL (Carta X̄)",    f"{ucl_x:.4f}", "bad"),
            (c4, "LCL (Carta X̄)",    f"{lcl_x:.4f}", "bad"),
            (c5, "σ̂ estimada",        f"{sigma_est:.4f}", ""),
            (c6, "Puntos fuera",      str(total_fuera), "ok" if total_fuera==0 else "bad"),
        ]
        for col, label, val, cls in stats:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {cls}">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if total_fuera == 0:
            st.markdown('<div class="alert-ok">✅ <b>PROCESO BAJO CONTROL ESTADÍSTICO</b> — No se detectaron causas especiales en los límites de ±3σ.</div>', unsafe_allow_html=True)
        else:
            msg = f'<div class="alert-error">🚨 <b>PROCESO FUERA DE CONTROL</b> — {total_fuera} punto(s) fuera de los límites.'
            if fuera_x: msg += f' Carta X̄: subgrupos {[i+1 for i in fuera_x]}.'
            if fuera_r: msg += f' Carta R: subgrupos {[i+1 for i in fuera_r]}.'
            msg += ' Investigar causas especiales.</div>'
            st.markdown(msg, unsafe_allow_html=True)

        if "Corrimiento" in st.session_state.get("anomalia",""):
            st.markdown('<div class="alert-warn">⚠️ Se simuló un <b>corrimiento de media</b> — Los puntos se alejan de la línea central a partir del subgrupo señalado.</div>', unsafe_allow_html=True)

        # Gráfica
        st.markdown("### 📈 Gráfica X̄-R")
        fig = fig_xbar_r(xbars, rangos, ucl_x, xdbar, lcl_x, ucl_r, rbar, lcl_r)
        st.plotly_chart(fig, use_container_width=True)

        # Tabla
        st.markdown("### 📋 Tabla de Datos")
        df = pd.DataFrame({
            "Subgrupo": range(1, k_r+1),
            "X̄":        np.round(xbars, 4),
            "R":         np.round(rangos, 4),
            "UCL (X̄)":  round(ucl_x, 4),
            "LCL (X̄)":  round(lcl_x, 4),
            "X̄ Estado": ["🔴 FUERA" if i in fuera_x else "🟢 OK" for i in range(k_r)],
            "R Estado":  ["🔴 FUERA" if i in fuera_r else "🟢 OK" for i in range(k_r)],
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.session_state["df_xbar"] = df

# ══════════════════════════════════════════════════════════════
#  MÓDULO 3 — CARTA p
# ══════════════════════════════════════════════════════════════
def modulo_carta_p():
    st.markdown('<div class="section-title">📉 Carta p — Proporción Defectiva</div>', unsafe_allow_html=True)

    with st.expander("📐 Ver fórmulas", expanded=False):
        st.markdown("""
        <div class="formula-box">
        pᵢ  = dᵢ / nᵢ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ← Proporción del período i<br>
        p̄   = Σdᵢ / Σnᵢ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ← Proporción media global<br>
        σᵢ  = √(p̄·(1−p̄)/nᵢ) &nbsp; ← Desviación estándar del período<br>
        UCL = p̄ + 3·σᵢ<br>
        LCL = max(0, p̄ − 3·σᵢ)
        </div>
        """, unsafe_allow_html=True)
        st.info("Se basa en la **distribución binomial**, aproximada por la normal para n grande (n·p̄ ≥ 5).")

    st.markdown("---")
    modo = st.radio("**¿Cómo deseas ingresar los datos?**",
                    ["🎲 Simular datos automáticamente", "✏️ Ingresar mis propios datos"],
                    horizontal=True, key="modo_p")

    if "🎲" in modo:
        col1, col2, col3 = st.columns(3)
        with col1:
            n_p  = st.number_input("Tamaño de muestra (n)", value=100, min_value=20, max_value=500)
        with col2:
            k_p  = st.number_input("N° de períodos (k)", value=20, min_value=10, max_value=30)
        with col3:
            p_real = st.slider("Proporción defectiva real (p)", 0.01, 0.30, 0.05, 0.01,
                               format="%.2f")

        anomalia_p = st.selectbox("Anomalía a simular", [
            "Sin anomalías",
            "Incremento súbito en la tasa de defectos",
            "Incremento gradual en la tasa de defectos",
        ], key="an_p")

        if st.button("▶ Generar carta p", type="primary"):
            defs = np.zeros(int(k_p), dtype=int)
            for i in range(int(k_p)):
                p_act = p_real
                if "súbito" in anomalia_p and i >= int(k_p*0.65):
                    p_act = min(0.95, p_real*3)
                elif "gradual" in anomalia_p:
                    p_act = min(0.95, p_real+(i/k_p)*p_real*2)
                defs[i] = np.random.binomial(int(n_p), p_act)
            st.session_state["p_datos"] = (defs, int(n_p))

    else:
        col1, col2 = st.columns(2)
        with col1:
            n_p = st.number_input("Tamaño de muestra por período", value=100, min_value=10)
        with col2:
            k_p = st.number_input("N° de períodos", value=10, min_value=5, max_value=30)

        st.markdown(f"Ingresa el número de **defectuosos** por período (de {int(n_p)} unidades):")
        defs_list = []
        cols_inp = st.columns(5)
        for i in range(int(k_p)):
            with cols_inp[i % 5]:
                d = st.number_input(f"P{i+1}", 0, int(n_p), 0, key=f"p_{i}")
                defs_list.append(d)

        if st.button("▶ Calcular carta p", type="primary"):
            st.session_state["p_datos"] = (np.array(defs_list), int(n_p))

    # ── Resultados ──
    if "p_datos" in st.session_state:
        defs, n_p_r = st.session_state["p_datos"]
        k_r  = len(defs)
        p_i  = defs / n_p_r
        p_bar = defs.sum() / (k_r * n_p_r)
        std_i = np.sqrt(p_bar*(1-p_bar)/n_p_r)
        ucl_i = np.full(k_r, p_bar + 3*std_i)
        lcl_i = np.maximum(0.0, p_bar - 3*std_i)
        fuera = [i for i,v in enumerate(p_i) if v>ucl_i[i] or v<lcl_i[i]]

        st.markdown("---")
        c1,c2,c3,c4 = st.columns(4)
        for col, lbl, val, cls in [
            (c1, "p̄ (Proporción media)", f"{p_bar*100:.3f}%", ""),
            (c2, "UCL", f"{ucl_i.mean()*100:.3f}%", "bad"),
            (c3, "LCL", f"{lcl_i.mean()*100:.3f}%", "bad"),
            (c4, "Períodos fuera", str(len(fuera)), "ok" if len(fuera)==0 else "bad"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{lbl}</div>
                    <div class="metric-value {cls}">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if len(fuera) == 0:
            st.markdown('<div class="alert-ok">✅ <b>Proporción defectiva bajo control estadístico</b></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-error">🚨 <b>{len(fuera)} período(s) fuera de control</b> — Períodos: {[i+1 for i in fuera]}</div>', unsafe_allow_html=True)

        st.markdown("### 📉 Gráfica p")
        st.plotly_chart(fig_carta_p(p_i, ucl_i, p_bar, lcl_i, np.arange(1,k_r+1)),
                        use_container_width=True)

        st.markdown("### 📋 Tabla de Datos")
        df_p = pd.DataFrame({
            "Período":      range(1, k_r+1),
            "Defectuosos":  defs.astype(int),
            "n":            n_p_r,
            "p (%)":        np.round(p_i*100, 3),
            "UCL (%)":      np.round(ucl_i*100, 3),
            "LCL (%)":      np.round(lcl_i*100, 3),
            "Estado":       ["🔴 FUERA" if i in fuera else "🟢 OK" for i in range(k_r)],
        })
        st.dataframe(df_p, use_container_width=True, hide_index=True)
        st.session_state["df_p"] = df_p

# ══════════════════════════════════════════════════════════════
#  MÓDULO 4 — REGLAS DE NELSON
# ══════════════════════════════════════════════════════════════
REGLAS = [
    ("1", "Punto fuera de ±3σ",           "1 punto más allá de UCL o LCL.",                      "Evento súbito, material defectuoso, error de medición.",      "🚨 Detener e investigar"),
    ("2", "9 puntos mismo lado del CL",   "9 puntos consecutivos sobre o bajo la línea central.", "Corrimiento de media (cambio de turno, lote diferente).",     "⚠️ Verificar cambios en el proceso"),
    ("3", "6 puntos en tendencia",        "6 puntos seguidos todos subiendo o bajando.",          "Desgaste de herramienta, temperatura, fatiga del operador.",  "⚠️ Revisar equipos y condiciones"),
    ("4", "14 puntos alternando",         "14 puntos alternando sistemáticamente arriba/abajo.",  "Mezcla de dos procesos, máquinas u operadores.",             "⚠️ Separar fuentes de variación"),
    ("5", "2 de 3 en Zona A (>±2σ)",      "2 de 3 puntos consecutivos más allá de ±2σ.",         "Señal temprana de desestabilización del proceso.",           "⚠️ Investigar preventivamente"),
    ("6", "4 de 5 en Zona B (>±1σ)",      "4 de 5 puntos consecutivos más allá de ±1σ.",         "Proceso descentrado.",                                       "⚠️ Verificar centrado"),
    ("7", "15 puntos en ±1σ",             "15 puntos consecutivos dentro de ±1σ.",                "Datos de distribuciones mezcladas (estratificación).",       "ℹ️ Revisar sistema de medición"),
    ("8", "8 puntos fuera de ±1σ",        "8 puntos consecutivos fuera de ±1σ (ambos lados).",   "Bimodalidad en la distribución.",                            "ℹ️ Investigar causas"),
]

def modulo_nelson():
    st.markdown('<div class="section-title">⚠️ Reglas de Nelson — Patrones de Descontrol</div>', unsafe_allow_html=True)
    st.markdown("Las **Reglas de Nelson (1984)** detectan patrones no aleatorios en cartas de control, incluso cuando no hay puntos fuera de los límites.")

    tab1, tab2, tab3 = st.tabs(["📋 Las 8 Reglas", "🧪 Simulador de señales", "🔎 Verificar mis datos"])

    with tab1:
        df_reglas = pd.DataFrame(REGLAS, columns=["#", "Nombre", "Descripción", "Causa típica", "Acción"])
        st.dataframe(df_reglas, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### Clasificación por urgencia")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="alert-error">🚨 <b>Acción inmediata</b><br>Regla 1 — Punto fuera de control</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="alert-warn">⚠️ <b>Investigar proceso</b><br>Reglas 2, 3, 4, 5, 6</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="alert-info">ℹ️ <b>Revisar sistema</b><br>Reglas 7, 8</div>', unsafe_allow_html=True)

    with tab2:
        regla_sel = st.selectbox("Selecciona la regla a simular", [f"Regla {r[0]}: {r[1]}" for r in REGLAS[:5]])
        num = int(regla_sel.split(":")[0].split(" ")[1])

        if st.button("▶ Simular señal", type="primary"):
            cl, ucl, lcl = 0.0, 3.0, -3.0
            np.random.seed(None)
            if num == 1:
                datos = np.concatenate([np.random.normal(0,.8,14),[4.2],np.random.normal(0,.8,5)])
                flagged = [14]
            elif num == 2:
                datos = np.concatenate([np.random.normal(0,.7,5), np.abs(np.random.normal(.8,.4,9)), np.random.normal(0,.7,4)])
                flagged = list(range(5,14))
            elif num == 3:
                datos = np.concatenate([np.random.normal(0,.5,7), [-1.5+i*0.42+np.random.normal(0,.1) for i in range(6)], np.random.normal(0,.5,5)])
                flagged = list(range(7,13))
            elif num == 4:
                arr = [(-1)**i*(1.5+np.random.uniform(0,.3)) for i in range(14)]
                datos = np.concatenate([np.random.normal(0,.5,3), arr, np.random.normal(0,.5,3)])
                flagged = list(range(3,17))
            else:
                datos = np.concatenate([np.random.normal(0,.5,5),[2.3,-0.2,2.5],np.random.normal(0,.5,6)])
                flagged = [5,7]

            regla_info = REGLAS[num-1]
            col1, col2 = st.columns([2,1])
            with col1:
                idx = list(range(1,len(datos)+1))
                sigma = (ucl-cl)/3
                fig = go.Figure()
                # Zonas
                fig.add_hrect(y0=cl+2*sigma, y1=ucl, fillcolor="rgba(239,68,68,0.08)", line_width=0)
                fig.add_hrect(y0=lcl, y1=cl-2*sigma, fillcolor="rgba(239,68,68,0.08)", line_width=0)
                fig.add_hrect(y0=cl+sigma, y1=cl+2*sigma, fillcolor="rgba(234,179,8,0.08)", line_width=0)
                fig.add_hrect(y0=cl-2*sigma, y1=cl-sigma, fillcolor="rgba(234,179,8,0.08)", line_width=0)
                # Líneas
                for val,color,name,dash in [(ucl,"#ef4444",f"UCL={ucl}","dash"),(cl,"#2563eb",f"CL={cl}","solid"),(lcl,"#ef4444",f"LCL={lcl}","dash")]:
                    fig.add_hline(y=val, line_color=color, line_dash=dash, line_width=1.8,
                                  annotation_text=name, annotation_position="right",
                                  annotation_font_color=color)
                # Líneas ±1σ, ±2σ
                for z in [1,2,-1,-2]:
                    fig.add_hline(y=cl+z*sigma, line_color="#94a3b8", line_dash="dot", line_width=0.8)
                fig.add_trace(go.Scatter(x=idx,y=list(datos),mode='lines',
                    line=dict(color="#94a3b8",width=1.5),showlegend=False))
                colores_pts = ["#f59e0b" if i in flagged else ("#ef4444" if (v>ucl or v<lcl) else "#2563eb")
                               for i,v in enumerate(datos)]
                tamaños = [12 if i in flagged else 8 for i in range(len(datos))]
                fig.add_trace(go.Scatter(x=idx,y=list(datos),mode='markers',
                    marker=dict(color=colores_pts,size=tamaños,line=dict(color="white",width=1.5)),
                    showlegend=False))
                fig.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter",size=11),
                    yaxis=dict(gridcolor="#f1f5f9"),
                    xaxis=dict(gridcolor="#f1f5f9",title="Observación"),
                    margin=dict(l=50,r=100,t=30,b=40))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown(f"""
                <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:20px;">
                    <div style="font-size:1rem;font-weight:700;color:#1e3a5f;margin-bottom:12px;">
                        Regla {regla_info[0]}: {regla_info[1]}
                    </div>
                    <div style="font-size:0.85rem;color:#374151;margin-bottom:10px;">
                        <b>Descripción:</b><br>{regla_info[2]}
                    </div>
                    <div style="font-size:0.85rem;color:#374151;margin-bottom:10px;">
                        <b>Causa típica:</b><br>{regla_info[3]}
                    </div>
                    <div style="font-size:0.85rem;color:#374151;margin-bottom:10px;">
                        <b>Acción:</b><br>{regla_info[4]}
                    </div>
                    <div style="font-size:0.85rem;color:#92400e;background:#fffbeb;border-radius:6px;padding:8px;">
                        <b>Puntos activados:</b><br>{[i+1 for i in flagged]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.markdown("Ingresa tu serie de valores X̄ y los límites para verificar las reglas:")
        col1, col2, col3 = st.columns(3)
        with col1:
            cl_inp  = st.number_input("Línea Central (CL)", value=0.0)
        with col2:
            ucl_inp = st.number_input("UCL", value=3.0)
        with col3:
            lcl_inp = st.number_input("LCL", value=-3.0)

        datos_txt = st.text_area("Valores X̄ (separados por espacio o coma)",
                                  placeholder="Ej: 0.2 -0.1 0.5 2.3 2.5 -0.3 0.1 ...")
        if st.button("🔎 Verificar reglas", type="primary"):
            try:
                pts = np.array([float(x) for x in datos_txt.replace(',',' ').split()])
                if len(pts) < 5:
                    st.warning("Ingresa al menos 5 valores.")
                else:
                    sigma_v = (ucl_inp - cl_inp)/3
                    resultados = []
                    for r in REGLAS:
                        resultados.append({"Regla": f"Regla {r[0]}: {r[1]}", "Estado": "⚪ No aplicada (verificación manual)"})

                    # Verificar regla 1
                    fuera_v = [i+1 for i,v in enumerate(pts) if v>ucl_inp or v<lcl_inp]
                    r1 = f"🔴 SEÑAL — Puntos: {fuera_v}" if fuera_v else "🟢 Sin señal"

                    df_res = pd.DataFrame([
                        {"#": "1", "Regla": "Punto fuera de ±3σ", "Resultado": r1},
                    ])
                    st.dataframe(df_res, use_container_width=True, hide_index=True)
                    st.info("💡 Para las demás reglas usa el simulador o analiza la gráfica visualmente.")

                    fig_v = go.Figure()
                    fig_v.add_hline(y=ucl_inp, line_color="#ef4444", line_dash="dash", line_width=2,
                                    annotation_text=f"UCL={ucl_inp}", annotation_position="right")
                    fig_v.add_hline(y=cl_inp,  line_color="#2563eb", line_width=2,
                                    annotation_text=f"CL={cl_inp}", annotation_position="right")
                    fig_v.add_hline(y=lcl_inp, line_color="#ef4444", line_dash="dash", line_width=2,
                                    annotation_text=f"LCL={lcl_inp}", annotation_position="right")
                    colores_v = ["#ef4444" if (v>ucl_inp or v<lcl_inp) else "#2563eb" for v in pts]
                    fig_v.add_trace(go.Scatter(x=list(range(1,len(pts)+1)), y=list(pts),
                        mode='lines+markers',
                        marker=dict(color=colores_v, size=9, line=dict(color="white",width=1.5)),
                        line=dict(color="#94a3b8", width=1.5)))
                    fig_v.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                        font=dict(family="Inter",size=11),
                        xaxis=dict(gridcolor="#f1f5f9",title="Observación"),
                        yaxis=dict(gridcolor="#f1f5f9"),
                        margin=dict(l=50,r=100,t=30,b=40))
                    st.plotly_chart(fig_v, use_container_width=True)
            except Exception as e:
                st.error(f"Error al procesar: {e}")

# ══════════════════════════════════════════════════════════════
#  MÓDULO 5 — QUIZ
# ══════════════════════════════════════════════════════════════
PREGUNTAS = [
    {"p": "¿Cuántos puntos consecutivos al mismo lado del CL indica la Regla 2 de Nelson?",
     "ops": ["A) 6", "B) 7", "C) 9", "D) 12"], "r": "C",
     "exp": "La Regla 2 establece 9 puntos consecutivos al mismo lado de la línea central."},
    {"p": "Los límites de control en una carta de Shewhart se ubican a:",
     "ops": ["A) ±1σ", "B) ±2σ", "C) ±3σ", "D) ±4σ"], "r": "C",
     "exp": "Los límites a ±3σ cubren el 99.73% de la distribución normal."},
    {"p": "¿Qué constante se usa para calcular el UCL en la carta X̄?",
     "ops": ["A) D₄", "B) A₂", "C) D₃", "D) d₂"], "r": "B",
     "exp": "A₂ multiplica al rango promedio R̄: UCL = X̿ + A₂·R̄"},
    {"p": "La carta p se usa para monitorear:",
     "ops": ["A) Dimensiones en mm", "B) Temperatura del proceso", "C) Proporción de artículos defectivos", "D) Número de defectos por unidad"], "r": "C",
     "exp": "La carta p monitorea la fracción defectiva en cada muestra."},
    {"p": "Un proceso 'bajo control estadístico' significa:",
     "ops": ["A) Sin ningún defecto", "B) Solo variación por causas comunes", "C) Cumple especificaciones del cliente", "D) Cp > 1.33"], "r": "B",
     "exp": "Control estadístico = solo causas comunes presentes. No implica ausencia de defectos."},
    {"p": "¿Qué probabilidad tiene un punto de caer fuera de ±3σ si el proceso es estable?",
     "ops": ["A) 1%", "B) 5%", "C) 0.27%", "D) 3%"], "r": "C",
     "exp": "La distribución normal acumula 99.73% en ±3σ, dejando 0.27% fuera."},
    {"p": "Si LCL_p resulta negativo al calcularlo, ¿qué valor se debe usar?",
     "ops": ["A) El valor negativo calculado", "B) −0.01", "C) 0", "D) No tiene LCL"], "r": "C",
     "exp": "Una proporción no puede ser negativa. Si LCL < 0, se establece LCL = 0."},
    {"p": "¿Quién desarrolló las cartas de control en 1924?",
     "ops": ["A) W. Edwards Deming", "B) Joseph Juran", "C) Walter A. Shewhart", "D) Kaoru Ishikawa"], "r": "C",
     "exp": "Walter A. Shewhart las desarrolló en los Laboratorios Bell de AT&T en 1924."},
    {"p": "Una tendencia de 6 puntos en la carta X̄ sugiere principalmente:",
     "ops": ["A) Proceso muy preciso", "B) Cambio gradual (desgaste, temperatura)", "C) Mezcla de dos distribuciones", "D) Error de medición"], "r": "B",
     "exp": "6 puntos en tendencia indican un cambio gradual: desgaste de herramienta, temperatura, etc."},
    {"p": "Para n=5, ¿cuánto vale la constante A₂?",
     "ops": ["A) 1.880", "B) 0.729", "C) 0.577", "D) 0.419"], "r": "C",
     "exp": "Para subgrupos de tamaño n=5, A₂ = 0.577."},
]

def modulo_quiz():
    st.markdown('<div class="section-title">🎯 Quiz de Evaluación</div>', unsafe_allow_html=True)

    if "quiz_estado" not in st.session_state:
        st.session_state.quiz_estado = "inicio"
        st.session_state.quiz_idx    = 0
        st.session_state.quiz_score  = 0
        st.session_state.quiz_pregs  = random.sample(PREGUNTAS, 10)
        st.session_state.quiz_resp   = {}

    if st.session_state.quiz_estado == "inicio":
        st.markdown("""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:24px;max-width:600px;">
            <h3 style="color:#1e3a5f;">📋 Instrucciones</h3>
            <ul style="color:#374151;line-height:2;">
                <li>10 preguntas de selección múltiple</li>
                <li>Retroalimentación inmediata en cada pregunta</li>
                <li>Calificación final al terminar</li>
                <li>Puedes reiniciar en cualquier momento</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Iniciar evaluación", type="primary"):
            st.session_state.quiz_estado = "en_curso"
            st.session_state.quiz_idx    = 0
            st.session_state.quiz_score  = 0
            st.session_state.quiz_pregs  = random.sample(PREGUNTAS, 10)
            st.session_state.quiz_resp   = {}
            st.rerun()

    elif st.session_state.quiz_estado == "en_curso":
        idx   = st.session_state.quiz_idx
        pregs = st.session_state.quiz_pregs
        total = len(pregs)

        # Barra progreso
        st.progress((idx)/total, text=f"Pregunta {idx+1} de {total}")

        q = pregs[idx]
        st.markdown(f"""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:24px;margin:12px 0;">
            <div style="font-size:0.8rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">
                Pregunta {idx+1} de {total}
            </div>
            <div style="font-size:1.05rem;font-weight:600;color:#1e3a5f;">{q['p']}</div>
        </div>
        """, unsafe_allow_html=True)

        if idx not in st.session_state.quiz_resp:
            resp = st.radio("Selecciona tu respuesta:", q["ops"], key=f"q_{idx}", index=None)
            if resp:
                letra = resp[0]
                correcto = letra == q["r"]
                st.session_state.quiz_resp[idx] = {"resp": letra, "correcto": correcto}
                if correcto:
                    st.session_state.quiz_score += 1
                st.rerun()
        else:
            info = st.session_state.quiz_resp[idx]
            resp_dada = next(o for o in q["ops"] if o.startswith(info["resp"]))
            resp_correcta = next(o for o in q["ops"] if o.startswith(q["r"]))

            st.radio("Selecciona tu respuesta:", q["ops"], key=f"q_{idx}_show",
                     index=q["ops"].index(resp_dada), disabled=True)

            if info["correcto"]:
                st.markdown(f'<div class="quiz-feedback-ok">✅ <b>¡Correcto!</b> — {q["exp"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="quiz-feedback-bad">❌ <b>Incorrecto.</b> Respuesta correcta: <b>{resp_correcta}</b><br>{q["exp"]}</div>', unsafe_allow_html=True)

            col1, col2 = st.columns([1,4])
            with col1:
                if idx < total-1:
                    if st.button("Siguiente →", type="primary"):
                        st.session_state.quiz_idx += 1
                        st.rerun()
                else:
                    if st.button("Ver resultado final →", type="primary"):
                        st.session_state.quiz_estado = "finalizado"
                        st.rerun()

        if st.button("🔄 Reiniciar quiz", key="reiniciar_curso"):
            st.session_state.quiz_estado = "inicio"
            st.rerun()

    elif st.session_state.quiz_estado == "finalizado":
        score = st.session_state.quiz_score
        total = len(st.session_state.quiz_pregs)
        pct   = round(score/total*100)

        if pct >= 90:   nivel, color_n = "🏆 EXCELENTE", "#16a34a"
        elif pct >= 70: nivel, color_n = "👍 BIEN", "#2563eb"
        elif pct >= 50: nivel, color_n = "📚 REGULAR", "#d97706"
        else:           nivel, color_n = "🔄 NECESITAS REPASAR", "#dc2626"

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown(f"""
            <div style="background:white;border:2px solid {color_n};border-radius:12px;
                 padding:32px;text-align:center;">
                <div style="font-size:3rem;margin-bottom:8px;">{nivel.split()[0]}</div>
                <div style="font-size:2rem;font-weight:700;color:{color_n};">{pct}%</div>
                <div style="font-size:1rem;color:#64748b;margin:8px 0;">
                    {score} de {total} respuestas correctas
                </div>
                <div style="font-size:1.1rem;font-weight:600;color:{color_n};margin-top:12px;">
                    {' '.join(nivel.split()[1:])}
                </div>
                <div style="height:8px;background:#e2e8f0;border-radius:4px;margin:16px 0;">
                    <div style="height:100%;width:{pct}%;background:{color_n};border-radius:4px;"></div>
                </div>
                {"<div style='color:#64748b;font-size:0.9rem;'>Revisa los módulos de Teoría y Reglas de Nelson para reforzar.</div>" if pct<70 else ""}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Hacer quiz nuevamente", type="primary"):
            st.session_state.quiz_estado = "inicio"
            st.rerun()

# ══════════════════════════════════════════════════════════════
#  MÓDULO 6 — EXPORTAR
# ══════════════════════════════════════════════════════════════
def modulo_exportar():
    st.markdown('<div class="section-title">📄 Exportar Reporte</div>', unsafe_allow_html=True)

    tiene_xbar = "df_xbar" in st.session_state
    tiene_p    = "df_p"    in st.session_state

    if not tiene_xbar and not tiene_p:
        st.markdown('<div class="alert-warn">⚠️ <b>No hay datos para exportar.</b><br>Primero genera una Carta X̄-R o una Carta p en los módulos correspondientes.</div>', unsafe_allow_html=True)
        return

    if tiene_xbar:
        st.markdown("### 📈 Reporte Carta X̄-R")
        st.dataframe(st.session_state["df_xbar"], use_container_width=True, hide_index=True)
        csv_xbar = st.session_state["df_xbar"].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="⬇️ Descargar Reporte X̄-R (.csv)",
            data=csv_xbar,
            file_name="reporte_carta_xbar_r.csv",
            mime="text/csv",
            type="primary",
        )

    if tiene_p:
        st.markdown("### 📉 Reporte Carta p")
        st.dataframe(st.session_state["df_p"], use_container_width=True, hide_index=True)
        csv_p = st.session_state["df_p"].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="⬇️ Descargar Reporte Carta p (.csv)",
            data=csv_p,
            file_name="reporte_carta_p.csv",
            mime="text/csv",
            type="primary",
        )

    st.markdown("---")
    st.markdown("""
    <div class="alert-info">
    💡 <b>Para abrir en Excel:</b> Datos → Desde texto/CSV → selecciona el archivo → 
    Codificación UTF-8 → Delimitador: coma → Cargar.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════════════
def main():
    mostrar_header()
    modulo = sidebar_nav()

    if   "Teoría"    in modulo: modulo_teoria()
    elif "X̄-R"       in modulo: modulo_xbar()
    elif "Carta p"   in modulo: modulo_carta_p()
    elif "Nelson"    in modulo: modulo_nelson()
    elif "Quiz"      in modulo: modulo_quiz()
    elif "Exportar"  in modulo: modulo_exportar()

if __name__ == "__main__":
    main()
