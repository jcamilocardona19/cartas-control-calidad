import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io, random

st.set_page_config(
    page_title="Cartas de Control de Calidad — UTP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background-color:#f8fafc;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1e3a5f,#0f2440);}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
.metric-card{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px 20px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.08);margin-bottom:8px;}
.metric-label{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:#64748b;font-weight:600;margin-bottom:4px;}
.metric-value{font-size:1.3rem;font-weight:700;color:#1e3a5f;font-family:monospace;}
.metric-value.ok{color:#16a34a;}.metric-value.bad{color:#dc2626;}
.alert-ok{background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:12px 16px;color:#166534;margin:8px 0;}
.alert-warn{background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:12px 16px;color:#92400e;margin:8px 0;}
.alert-error{background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:12px 16px;color:#991b1b;margin:8px 0;}
.alert-info{background:#eff6ff;border:1px solid #93c5fd;border-radius:8px;padding:12px 16px;color:#1e40af;margin:8px 0;}
.formula-box{background:#f1f5f9;border-left:4px solid #2563eb;border-radius:0 8px 8px 0;padding:14px 18px;font-family:monospace;font-size:0.9rem;color:#1e3a5f;margin:12px 0;line-height:2;}
.section-title{font-size:1.4rem;font-weight:700;color:#1e3a5f;border-bottom:2px solid #2563eb;padding-bottom:8px;margin-bottom:20px;}
.teoria-card{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06);}
.stButton>button{background:#2563eb;color:white;border:none;border-radius:8px;font-weight:600;}
.stButton>button:hover{background:#1d4ed8;}
.quiz-ok{background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:14px;color:#166534;margin:8px 0;}
.quiz-bad{background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:14px;color:#991b1b;margin:8px 0;}
</style>
""", unsafe_allow_html=True)

XR_CONST = {
    2:(1.880,0.000,3.267,1.128), 3:(1.023,0.000,2.575,1.693),
    4:(0.729,0.000,2.282,2.059), 5:(0.577,0.000,2.115,2.326),
    6:(0.483,0.000,2.004,2.534), 7:(0.419,0.076,1.924,2.704),
    8:(0.373,0.136,1.864,2.847), 9:(0.337,0.184,1.816,2.970),
    10:(0.308,0.223,1.777,3.078),
}

def fig_to_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf

def graficar_xbar_r(xbars, rangos, ucl_x, cl_x, lcl_x, ucl_r, cl_r, lcl_r):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), facecolor='white')
    fig.suptitle('Carta X̄-R — Control Estadístico de Procesos', fontsize=13, fontweight='bold', color='#1e3a5f')
    idx = range(1, len(xbars)+1)
    sigma_x = (ucl_x - cl_x) / 3

    for ax, datos, ucl, cl, lcl, ylabel, color_ok in [
        (ax1, xbars, ucl_x, cl_x, lcl_x, 'X̄ (Promedio)', '#2563eb'),
        (ax2, rangos, ucl_r, cl_r, lcl_r, 'R (Rango)', '#16a34a'),
    ]:
        ax.set_facecolor('#f8fafc')
        ax.grid(True, color='#e2e8f0', linestyle='--', alpha=0.8)
        s = (ucl - cl) / 3
        ax.axhspan(cl+2*s, ucl+s*0.5, alpha=0.07, color='#ef4444')
        ax.axhspan(max(0,lcl-s*0.5), cl-2*s, alpha=0.07, color='#ef4444')
        ax.axhspan(cl+s, cl+2*s, alpha=0.07, color='#f59e0b')
        ax.axhspan(cl-2*s, cl-s, alpha=0.07, color='#f59e0b')
        ax.axhline(ucl, color='#ef4444', linestyle='--', linewidth=1.8, label=f'UCL={ucl:.3f}')
        ax.axhline(cl,  color='#2563eb', linestyle='-',  linewidth=2.0, label=f'CL ={cl:.3f}')
        ax.axhline(lcl, color='#ef4444', linestyle='--', linewidth=1.8, label=f'LCL={lcl:.3f}')
        fuera = [i for i,v in enumerate(datos) if v>ucl or v<lcl]
        colores = ['#ef4444' if i in fuera else color_ok for i in range(len(datos))]
        tamaños = [80 if i in fuera else 45 for i in range(len(datos))]
        ax.plot(idx, datos, color='#94a3b8', linewidth=1.3, zorder=2)
        ax.scatter(idx, datos, c=colores, s=tamaños, zorder=3, edgecolors='white', linewidths=1.2)
        for i in fuera:
            ax.annotate('⚠', (i+1, datos[i]), textcoords="offset points",
                       xytext=(0,10), color='#ef4444', fontsize=10, ha='center')
        ax.set_ylabel(ylabel, color='#1e3a5f', fontsize=11)
        ax.set_xlabel('Subgrupo', color='#64748b', fontsize=9)
        ax.tick_params(colors='#64748b')
        ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
        for sp in ax.spines.values(): sp.set_edgecolor('#e2e8f0')
    plt.tight_layout()
    return fig_to_image(fig)

def graficar_carta_p(p_i, ucl_i, cl, lcl_i):
    fig, ax = plt.subplots(figsize=(12, 5), facecolor='white')
    fig.suptitle('Carta p — Proporción Defectiva', fontsize=13, fontweight='bold', color='#1e3a5f')
    idx = range(1, len(p_i)+1)
    ax.set_facecolor('#f8fafc')
    ax.grid(True, color='#e2e8f0', linestyle='--', alpha=0.8)
    ax.fill_between(idx, lcl_i, ucl_i, alpha=0.07, color='#ef4444', label='Banda ±3σ')
    ax.plot(idx, ucl_i, color='#ef4444', linestyle='--', linewidth=1.8, label=f'UCL≈{ucl_i.mean()*100:.2f}%')
    ax.axhline(cl, color='#2563eb', linewidth=2.0, label=f'p̄={cl*100:.3f}%')
    ax.plot(idx, lcl_i, color='#ef4444', linestyle='--', linewidth=1.8, label=f'LCL≈{lcl_i.mean()*100:.2f}%')
    fuera = [i for i,v in enumerate(p_i) if v>ucl_i[i] or v<lcl_i[i]]
    colores = ['#ef4444' if i in fuera else '#16a34a' for i in range(len(p_i))]
    ax.plot(idx, p_i, color='#94a3b8', linewidth=1.3, zorder=2)
    ax.scatter(idx, p_i, c=colores, s=55, zorder=3, edgecolors='white', linewidths=1.2)
    for i in fuera:
        ax.annotate('⚠', (i+1, p_i[i]), textcoords="offset points",
                   xytext=(0,10), color='#ef4444', fontsize=10, ha='center')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y,_: f'{y*100:.1f}%'))
    ax.set_xlabel('Período', color='#64748b'); ax.set_ylabel('Proporción defectiva', color='#1e3a5f')
    ax.tick_params(colors='#64748b')
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
    for sp in ax.spines.values(): sp.set_edgecolor('#e2e8f0')
    plt.tight_layout()
    return fig_to_image(fig)

def graficar_regla(datos, ucl, cl, lcl, flagged, titulo):
    fig, ax = plt.subplots(figsize=(11, 4), facecolor='white')
    ax.set_facecolor('#f8fafc'); ax.set_title(titulo, color='#1e3a5f', fontweight='bold')
    ax.grid(True, color='#e2e8f0', linestyle='--', alpha=0.8)
    s = (ucl-cl)/3
    ax.axhspan(cl+2*s, ucl+0.3, alpha=0.07, color='#ef4444')
    ax.axhspan(lcl-0.3, cl-2*s, alpha=0.07, color='#ef4444')
    ax.axhspan(cl+s, cl+2*s, alpha=0.07, color='#f59e0b')
    ax.axhspan(cl-2*s, cl-s, alpha=0.07, color='#f59e0b')
    for val,c,dash,lbl in [(ucl,'#ef4444','--',f'UCL={ucl}'),(cl,'#2563eb','-',f'CL={cl}'),(lcl,'#ef4444','--',f'LCL={lcl}')]:
        ax.axhline(val, color=c, linestyle=dash, linewidth=1.8, label=lbl)
    for z in [s,2*s,-s,-2*s]:
        ax.axhline(cl+z, color='#cbd5e1', linestyle=':', linewidth=0.8)
    idx = range(1, len(datos)+1)
    ax.plot(idx, datos, color='#94a3b8', linewidth=1.3, zorder=2)
    colores = ['#f59e0b' if i in flagged else ('#ef4444' if (v>ucl or v<lcl) else '#2563eb') for i,v in enumerate(datos)]
    tamaños = [90 if i in flagged else 45 for i in range(len(datos))]
    ax.scatter(idx, datos, c=colores, s=tamaños, zorder=3, edgecolors='white', linewidths=1.2)
    ax.legend(fontsize=8, framealpha=0.9)
    for sp in ax.spines.values(): sp.set_edgecolor('#e2e8f0')
    plt.tight_layout()
    return fig_to_image(fig)

def mostrar_header():
    col1, col2 = st.columns([1,5])
    with col1:
        try: st.image("utp_logo.png", width=110)
        except: st.markdown("**UTP**")
    with col2:
        st.markdown("""
        <div style="padding:8px 0;">
        <div style="font-size:1.6rem;font-weight:700;color:#1e3a5f;">📊 Cartas de Control de Calidad</div>
        <div style="font-size:0.9rem;color:#64748b;margin-top:4px;">
        Universidad Tecnológica de Pereira &nbsp;·&nbsp; Herramienta Didáctica &nbsp;·&nbsp; Control Estadístico de Procesos
        </div></div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:2px solid #2563eb;margin:8px 0 24px 0;'>", unsafe_allow_html=True)

def sidebar_nav():
    with st.sidebar:
        try: st.image("utp_logo.png", width=130)
        except: pass
        st.markdown("---")
        st.markdown("### 📚 Navegación")
        modulo = st.radio("", [
            "📘 Teoría y Fundamentos",
            "📈 Carta X̄-R",
            "📉 Carta p",
            "⚠️ Reglas de Nelson",
            "🎯 Quiz de Evaluación",
            "📄 Exportar Reporte",
        ], label_visibility="collapsed")
        st.markdown("---")
        st.markdown("<div style='font-size:0.75rem;color:#94a3b8;line-height:1.8;'><b style='color:#bfdbfe;'>Normativa</b><br>ISO 7870-2<br>AIAG SPC Manual<br>Nelson (1984)<br><br><b style='color:#bfdbfe;'>Tecnología</b><br>Python · Streamlit</div>", unsafe_allow_html=True)
    return modulo

def modulo_teoria():
    st.markdown('<div class="section-title">📘 Teoría y Fundamentos del SPC</div>', unsafe_allow_html=True)
    tab1,tab2,tab3,tab4 = st.tabs(["¿Qué es una Carta de Control?","Anatomía","Tipos de Cartas","Implementación"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><h4>📌 Definición</h4>Una carta de control es una <b>gráfica de series de tiempo</b> que muestra cómo varía una característica de calidad a lo largo del tiempo, comparándola contra límites estadísticamente calculados.<br><br>Desarrollada por <b>Walter A. Shewhart en 1924</b> en los Laboratorios Bell.</div>', unsafe_allow_html=True)
            st.markdown('<div class="teoria-card"><h4>✅ Causa Común</h4>Inherente al proceso. Siempre presente. El proceso está <b>bajo control</b>. No requiere acción correctiva.</div>', unsafe_allow_html=True)
            st.markdown('<div class="teoria-card"><h4>🚨 Causa Especial</h4>Evento inusual. El proceso está <b>fuera de control</b>. Requiere investigación inmediata.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="teoria-card"><h4>🎯 Objetivo</h4>Distinguir entre variación <b>normal</b> e <b>anormal</b>. Los límites a ±3σ cubren el <b>99.73%</b> de los datos cuando el proceso es estable.</div>', unsafe_allow_html=True)
            st.markdown('<div class="teoria-card"><h4>📋 Referencias</h4>• ISO 7870-2 — Cartas de Shewhart<br>• AIAG SPC Manual<br>• Nelson (1984) — Reglas de detección<br>• ASQ — American Society for Quality</div>', unsafe_allow_html=True)
    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("### Fórmulas básicas")
            st.markdown('<div class="formula-box">UCL = X̿ + 3σ &nbsp; ← Límite Superior<br>────────────────────────<br>CL  = X̿ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ← Línea Central<br>────────────────────────<br>LCL = X̿ − 3σ &nbsp; ← Límite Inferior</div>', unsafe_allow_html=True)
            st.info("La probabilidad de una **falsa alarma** es solo el **0.27%** (1 de cada 370 puntos).")
        with c2:
            st.markdown("### Distribución de zonas")
            st.markdown("""
            <div style="display:flex;border-radius:8px;overflow:hidden;height:44px;margin:8px 0;font-size:0.68rem;font-weight:700;text-align:center;">
            <div style="flex:0.3;background:#fca5a5;display:flex;align-items:center;justify-content:center;">0.13%</div>
            <div style="flex:2;background:#fed7aa;display:flex;align-items:center;justify-content:center;">2.1%</div>
            <div style="flex:13.6;background:#fef08a;display:flex;align-items:center;justify-content:center;">B 13.6%</div>
            <div style="flex:34;background:#bbf7d0;display:flex;align-items:center;justify-content:center;">A 34.13%</div>
            <div style="flex:34;background:#bbf7d0;display:flex;align-items:center;justify-content:center;">A 34.13%</div>
            <div style="flex:13.6;background:#fef08a;display:flex;align-items:center;justify-content:center;">B 13.6%</div>
            <div style="flex:2;background:#fed7aa;display:flex;align-items:center;justify-content:center;">2.1%</div>
            <div style="flex:0.3;background:#fca5a5;display:flex;align-items:center;justify-content:center;">0.13%</div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#64748b;font-family:monospace;">
            <span>LCL(−3σ)</span><span>−2σ</span><span>−1σ</span><span>X̄</span><span>+1σ</span><span>+2σ</span><span>UCL(+3σ)</span>
            </div>""", unsafe_allow_html=True)
            st.markdown("#### ¿Cuándo actuar?")
            st.dataframe(pd.DataFrame({"Zona":["A (±1σ)","B (±2σ)","C (±3σ)","Fuera ±3σ"],"% área":["68.27%","95.45%","99.73%","0.27%"],"Acción":["Normal","Vigilar","Límite","🚨 Investigar"]}), hide_index=True)
    with tab3:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("#### 📏 Variables (datos medibles)")
            st.dataframe(pd.DataFrame({"Carta":["X̄-R","X̄-S","I-MR"],"Monitorea":["Promedio y Rango","Promedio y Desv.Est.","Individual y Rango móvil"],"Uso":["n ≤ 10 ✅","n > 10","n = 1"]}), hide_index=True)
        with c2:
            st.markdown("#### 🔢 Atributos (pasa/no pasa)")
            st.dataframe(pd.DataFrame({"Carta":["p","np","c","u"],"Monitorea":["Proporción defectiva","N° defectivos","N° defectos","Defectos/unidad"],"Uso":["n variable ✅","n constante","Área fija","Área variable"]}), hide_index=True)
    with tab4:
        cols = st.columns(5)
        pasos = [("📥","1. Recolectar","Mín. 20-25 subgrupos racionales"),("🧮","2. Calcular","X̄, R, X̿, R̄, UCL, LCL"),("📊","3. Graficar","Trazar puntos y límites"),("🔍","4. Analizar","Aplicar Reglas de Nelson"),("🔧","5. Actuar","Eliminar causas especiales")]
        for col,(ic,tit,desc) in zip(cols,pasos):
            with col:
                st.markdown(f'<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px;text-align:center;height:160px;"><div style="font-size:2rem;">{ic}</div><div style="font-weight:700;color:#1e3a5f;font-size:0.85rem;margin:8px 0 4px;">{tit}</div><div style="font-size:0.75rem;color:#64748b;">{desc}</div></div>', unsafe_allow_html=True)

def modulo_xbar():
    st.markdown('<div class="section-title">📈 Carta X̄-R — Variables Continuas</div>', unsafe_allow_html=True)
    with st.expander("📐 Fórmulas y constantes"):
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="formula-box">X̄ᵢ = (x₁+...+xₙ)/n<br>Rᵢ = max−min<br>X̿ = ΣX̄ᵢ/k<br>R̄ = ΣRᵢ/k<br>UCL_X̄ = X̿+A₂·R̄<br>LCL_X̄ = X̿−A₂·R̄<br>UCL_R = D₄·R̄<br>LCL_R = max(0,D₃·R̄)</div>', unsafe_allow_html=True)
        with c2:
            df_c = pd.DataFrame(XR_CONST,index=["A₂","D₃","D₄","d₂"]).T
            df_c.index.name="n"; st.dataframe(df_c.round(3))
    st.markdown("---")
    modo = st.radio("**¿Cómo deseas ingresar los datos?**",["🎲 Simular automáticamente","✏️ Datos propios"],horizontal=True)
    if "🎲" in modo:
        c1,c2,c3,c4 = st.columns(4)
        with c1: mu=st.number_input("Media (μ)",value=100.0,step=1.0)
        with c2: sigma=st.number_input("Desv. estándar (σ)",value=2.5,min_value=0.1,step=0.5)
        with c3: n=st.selectbox("Subgrupo (n)",list(range(2,11)),index=3)
        with c4: k=st.number_input("Subgrupos (k)",value=20,min_value=10,max_value=30)
        an=st.selectbox("Anomalía",["Sin anomalías","Corrimiento de media","Tendencia creciente","Punto fuera de control"])
        if st.button("▶ Generar carta X̄-R",type="primary"):
            datos=np.zeros((int(k),n))
            for i in range(int(k)):
                mu_a=mu
                if "Corrimiento" in an and i>=int(k*0.6): mu_a=mu+2*sigma
                elif "Tendencia" in an: mu_a=mu+(i/k)*3*sigma
                obs=np.random.normal(mu_a,sigma,n)
                if "Punto" in an and i==int(k*0.7): obs[0]=mu+4.5*sigma
                datos[i]=obs
            st.session_state["xbar_datos"]=datos
    else:
        c1,c2=st.columns(2)
        with c1: n=st.selectbox("Subgrupo (n)",list(range(2,11)),index=3)
        with c2: k=st.number_input("Subgrupos (k)",value=10,min_value=5,max_value=30)
        st.markdown(f"Ingresa **{n} valores** por subgrupo separados por espacio:")
        datos_l=[]
        for i in range(int(k)):
            e=st.text_input(f"Subgrupo {i+1}",key=f"sg_{i}",placeholder="10.2 10.5 9.8 ...")
            if e:
                try:
                    v=[float(x) for x in e.split()]
                    if len(v)==n: datos_l.append(v)
                except: pass
        if st.button("▶ Calcular carta X̄-R",type="primary"):
            if len(datos_l)==int(k): st.session_state["xbar_datos"]=np.array(datos_l)
            else: st.warning(f"Completa los {int(k)} subgrupos.")

    if "xbar_datos" in st.session_state:
        datos=st.session_state["xbar_datos"]; k_r,n_r=datos.shape
        xbars=datos.mean(axis=1); rangos=datos.max(axis=1)-datos.min(axis=1)
        xdbar=xbars.mean(); rbar=rangos.mean()
        A2,D3,D4,d2=XR_CONST[n_r]
        ucl_x=xdbar+A2*rbar; lcl_x=xdbar-A2*rbar
        ucl_r=D4*rbar; lcl_r=max(0.0,D3*rbar); sigma_e=rbar/d2
        fuera_x=[i for i,v in enumerate(xbars) if v>ucl_x or v<lcl_x]
        fuera_r=[i for i,v in enumerate(rangos) if v>ucl_r or v<lcl_r]
        total=len(fuera_x)+len(fuera_r)
        st.markdown("---")
        c1,c2,c3,c4,c5,c6=st.columns(6)
        for col,lbl,val,cls in [(c1,"X̿",f"{xdbar:.4f}",""),(c2,"R̄",f"{rbar:.4f}",""),(c3,"UCL(X̄)",f"{ucl_x:.4f}","bad"),(c4,"LCL(X̄)",f"{lcl_x:.4f}","bad"),(c5,"σ̂",f"{sigma_e:.4f}",""),(c6,"Fuera",str(total),"ok" if total==0 else "bad")]:
            with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {cls}">{val}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        if total==0: st.markdown('<div class="alert-ok">✅ <b>PROCESO BAJO CONTROL ESTADÍSTICO</b> — No se detectaron causas especiales.</div>',unsafe_allow_html=True)
        else: st.markdown(f'<div class="alert-error">🚨 <b>{total} punto(s) FUERA DE CONTROL</b> — Carta X̄: {[i+1 for i in fuera_x]} · Carta R: {[i+1 for i in fuera_r]}</div>',unsafe_allow_html=True)
        st.markdown("### 📈 Gráfica X̄-R")
        img=graficar_xbar_r(xbars,rangos,ucl_x,xdbar,lcl_x,ucl_r,rbar,lcl_r)
        st.image(img,use_column_width=True)
        st.markdown("### 📋 Tabla de datos")
        df=pd.DataFrame({"Subgrupo":range(1,k_r+1),"X̄":np.round(xbars,4),"R":np.round(rangos,4),"UCL(X̄)":round(ucl_x,4),"LCL(X̄)":round(lcl_x,4),"X̄ Estado":["🔴 FUERA" if i in fuera_x else "🟢 OK" for i in range(k_r)],"R Estado":["🔴 FUERA" if i in fuera_r else "🟢 OK" for i in range(k_r)]})
        st.dataframe(df,hide_index=True,use_container_width=True)
        st.session_state["df_xbar"]=df

def modulo_carta_p():
    st.markdown('<div class="section-title">📉 Carta p — Proporción Defectiva</div>',unsafe_allow_html=True)
    with st.expander("📐 Fórmulas"):
        st.markdown('<div class="formula-box">pᵢ = dᵢ/nᵢ<br>p̄ = Σdᵢ/Σnᵢ<br>σᵢ = √(p̄·(1−p̄)/nᵢ)<br>UCL = p̄+3·σᵢ<br>LCL = max(0, p̄−3·σᵢ)</div>',unsafe_allow_html=True)
    st.markdown("---")
    modo=st.radio("**¿Cómo ingresar datos?**",["🎲 Simular","✏️ Datos propios"],horizontal=True,key="modo_p")
    if "🎲" in modo:
        c1,c2,c3=st.columns(3)
        with c1: n_p=st.number_input("Muestra (n)",value=100,min_value=20)
        with c2: k_p=st.number_input("Períodos (k)",value=20,min_value=10,max_value=30)
        with c3: p_r=st.slider("p real",0.01,0.30,0.05,0.01,format="%.2f")
        an_p=st.selectbox("Anomalía",["Sin anomalías","Incremento súbito","Incremento gradual"],key="an_p")
        if st.button("▶ Generar carta p",type="primary"):
            defs=np.zeros(int(k_p),dtype=int)
            for i in range(int(k_p)):
                p_a=p_r
                if "súbito" in an_p and i>=int(k_p*0.65): p_a=min(0.95,p_r*3)
                elif "gradual" in an_p: p_a=min(0.95,p_r+(i/k_p)*p_r*2)
                defs[i]=np.random.binomial(int(n_p),p_a)
            st.session_state["p_datos"]=(defs,int(n_p))
    else:
        c1,c2=st.columns(2)
        with c1: n_p=st.number_input("Muestra por período",value=100,min_value=10)
        with c2: k_p=st.number_input("Períodos",value=10,min_value=5,max_value=30)
        st.markdown("Ingresa defectuosos por período:")
        defs_l=[]; cols_i=st.columns(5)
        for i in range(int(k_p)):
            with cols_i[i%5]: defs_l.append(st.number_input(f"P{i+1}",0,int(n_p),0,key=f"p_{i}"))
        if st.button("▶ Calcular carta p",type="primary"):
            st.session_state["p_datos"]=(np.array(defs_l),int(n_p))
    if "p_datos" in st.session_state:
        defs,n_r=st.session_state["p_datos"]; k_r=len(defs)
        p_i=defs/n_r; p_bar=defs.sum()/(k_r*n_r)
        std_i=np.sqrt(p_bar*(1-p_bar)/n_r)
        ucl_i=np.full(k_r,p_bar+3*std_i); lcl_i=np.maximum(0.0,p_bar-3*std_i)
        fuera=[i for i,v in enumerate(p_i) if v>ucl_i[i] or v<lcl_i[i]]
        st.markdown("---")
        c1,c2,c3,c4=st.columns(4)
        for col,lbl,val,cls in [(c1,"p̄",f"{p_bar*100:.3f}%",""),(c2,"UCL",f"{ucl_i.mean()*100:.3f}%","bad"),(c3,"LCL",f"{lcl_i.mean()*100:.3f}%","bad"),(c4,"Fuera",str(len(fuera)),"ok" if len(fuera)==0 else "bad")]:
            with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {cls}">{val}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        if len(fuera)==0: st.markdown('<div class="alert-ok">✅ Proporción defectiva bajo control estadístico.</div>',unsafe_allow_html=True)
        else: st.markdown(f'<div class="alert-error">🚨 {len(fuera)} período(s) fuera de control — Períodos: {[i+1 for i in fuera]}</div>',unsafe_allow_html=True)
        st.markdown("### 📉 Gráfica p")
        st.image(graficar_carta_p(p_i,ucl_i,p_bar,lcl_i),use_column_width=True)
        df_p=pd.DataFrame({"Período":range(1,k_r+1),"Defectuosos":defs.astype(int),"n":n_r,"p(%)":np.round(p_i*100,3),"UCL(%)":np.round(ucl_i*100,3),"LCL(%)":np.round(lcl_i*100,3),"Estado":["🔴 FUERA" if i in fuera else "🟢 OK" for i in range(k_r)]})
        st.dataframe(df_p,hide_index=True,use_container_width=True)
        st.session_state["df_p"]=df_p

REGLAS=[("1","Punto fuera de ±3σ","1 punto más allá de UCL o LCL.","Evento súbito, error de medición.","🚨 Detener e investigar"),("2","9 puntos mismo lado","9 puntos consecutivos sobre o bajo CL.","Corrimiento de media.","⚠️ Verificar cambios"),("3","6 puntos en tendencia","6 puntos todos subiendo o bajando.","Desgaste, temperatura, fatiga.","⚠️ Revisar equipos"),("4","14 puntos alternando","14 puntos alternando arriba/abajo.","Mezcla de procesos.","⚠️ Separar fuentes"),("5","2/3 en Zona A (>±2σ)","2 de 3 más allá de ±2σ mismo lado.","Señal temprana de descontrol.","⚠️ Investigar"),("6","4/5 en Zona B (>±1σ)","4 de 5 más allá de ±1σ mismo lado.","Proceso descentrado.","⚠️ Verificar"),("7","15 puntos en ±1σ","15 puntos dentro de ±1σ.","Estratificación de datos.","ℹ️ Revisar medición"),("8","8 fuera de ±1σ","8 puntos fuera de ±1σ ambos lados.","Bimodalidad.","ℹ️ Investigar")]

def modulo_nelson():
    st.markdown('<div class="section-title">⚠️ Reglas de Nelson — Patrones de Descontrol</div>',unsafe_allow_html=True)
    st.markdown("Las **Reglas de Nelson (1984)** detectan patrones no aleatorios, incluso cuando no hay puntos fuera de los límites.")
    tab1,tab2=st.tabs(["📋 Las 8 Reglas","🧪 Simulador de señales"])
    with tab1:
        st.dataframe(pd.DataFrame(REGLAS,columns=["#","Nombre","Descripción","Causa típica","Acción"]),hide_index=True,use_container_width=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown('<div class="alert-error">🚨 <b>Acción inmediata</b><br>Regla 1</div>',unsafe_allow_html=True)
        with c2: st.markdown('<div class="alert-warn">⚠️ <b>Investigar</b><br>Reglas 2, 3, 4, 5, 6</div>',unsafe_allow_html=True)
        with c3: st.markdown('<div class="alert-info">ℹ️ <b>Revisar sistema</b><br>Reglas 7, 8</div>',unsafe_allow_html=True)
    with tab2:
        rsel=st.selectbox("Regla a simular",[f"Regla {r[0]}: {r[1]}" for r in REGLAS[:5]])
        num=int(rsel.split(":")[0].split(" ")[1])
        if st.button("▶ Simular señal",type="primary"):
            np.random.seed(None)
            cl,ucl,lcl=0.0,3.0,-3.0
            if num==1: datos=np.concatenate([np.random.normal(0,.8,14),[4.2],np.random.normal(0,.8,5)]); flagged=[14]
            elif num==2: datos=np.concatenate([np.random.normal(0,.7,5),np.abs(np.random.normal(.8,.4,9)),np.random.normal(0,.7,4)]); flagged=list(range(5,14))
            elif num==3: datos=np.concatenate([np.random.normal(0,.5,7),[-1.5+i*0.42+np.random.normal(0,.1) for i in range(6)],np.random.normal(0,.5,5)]); flagged=list(range(7,13))
            elif num==4: arr=[(-1)**i*(1.5+np.random.uniform(0,.3)) for i in range(14)]; datos=np.concatenate([np.random.normal(0,.5,3),arr,np.random.normal(0,.5,3)]); flagged=list(range(3,17))
            else: datos=np.concatenate([np.random.normal(0,.5,5),[2.3,-0.2,2.5],np.random.normal(0,.5,6)]); flagged=[5,7]
            r_info=REGLAS[num-1]
            c1,c2=st.columns([2,1])
            with c1: st.image(graficar_regla(datos,ucl,cl,lcl,flagged,f"Regla {r_info[0]}: {r_info[1]}"),use_column_width=True)
            with c2:
                st.markdown(f'<div class="teoria-card"><h4>Regla {r_info[0]}: {r_info[1]}</h4><b>Descripción:</b><br>{r_info[2]}<br><br><b>Causa:</b><br>{r_info[3]}<br><br><b>Acción:</b><br>{r_info[4]}<br><br><div class="alert-warn"><b>Puntos activados:</b><br>{[i+1 for i in flagged]}</div></div>',unsafe_allow_html=True)

PREGUNTAS=[
    {"p":"¿Cuántos puntos al mismo lado del CL indica la Regla 2?","ops":["A) 6","B) 7","C) 9","D) 12"],"r":"C","exp":"La Regla 2 establece 9 puntos consecutivos al mismo lado de la línea central."},
    {"p":"Los límites de control en una carta de Shewhart se ubican a:","ops":["A) ±1σ","B) ±2σ","C) ±3σ","D) ±4σ"],"r":"C","exp":"Los límites a ±3σ cubren el 99.73% de la distribución normal."},
    {"p":"¿Qué constante se usa para calcular el UCL en la carta X̄?","ops":["A) D₄","B) A₂","C) D₃","D) d₂"],"r":"B","exp":"A₂ multiplica al rango promedio R̄: UCL = X̿ + A₂·R̄"},
    {"p":"La carta p se usa para monitorear:","ops":["A) Dimensiones en mm","B) Temperatura","C) Proporción de defectivos","D) Defectos por unidad"],"r":"C","exp":"La carta p monitorea la fracción defectiva en cada muestra."},
    {"p":"Un proceso 'bajo control estadístico' significa:","ops":["A) Sin defectos","B) Solo variación por causas comunes","C) Cumple especificaciones","D) Cp > 1.33"],"r":"B","exp":"Control estadístico = solo causas comunes. No implica ausencia de defectos."},
    {"p":"¿Qué probabilidad tiene un punto de caer fuera de ±3σ en proceso estable?","ops":["A) 1%","B) 5%","C) 0.27%","D) 3%"],"r":"C","exp":"La distribución normal acumula 99.73% en ±3σ, dejando 0.27% fuera."},
    {"p":"Si LCL_p resulta negativo, ¿qué valor se usa?","ops":["A) El valor negativo","B) −0.01","C) 0","D) No tiene LCL"],"r":"C","exp":"Una proporción no puede ser negativa. Si LCL < 0, se establece LCL = 0."},
    {"p":"¿Quién desarrolló las cartas de control en 1924?","ops":["A) Deming","B) Juran","C) Walter A. Shewhart","D) Ishikawa"],"r":"C","exp":"Walter A. Shewhart las desarrolló en los Laboratorios Bell de AT&T."},
    {"p":"Una tendencia de 6 puntos en la carta X̄ sugiere:","ops":["A) Proceso preciso","B) Cambio gradual (desgaste)","C) Mezcla de distribuciones","D) Error aleatorio"],"r":"B","exp":"6 puntos en tendencia indican cambio gradual: desgaste, temperatura, etc."},
    {"p":"Para n=5, ¿cuánto vale A₂?","ops":["A) 1.880","B) 0.729","C) 0.577","D) 0.419"],"r":"C","exp":"Para subgrupos de tamaño n=5, A₂ = 0.577."},
]

def modulo_quiz():
    st.markdown('<div class="section-title">🎯 Quiz de Evaluación</div>',unsafe_allow_html=True)
    if "qest" not in st.session_state:
        st.session_state.qest="inicio"; st.session_state.qidx=0
        st.session_state.qscore=0; st.session_state.qpregs=random.sample(PREGUNTAS,10)
        st.session_state.qresp={}
    if st.session_state.qest=="inicio":
        st.markdown('<div class="teoria-card"><h4>📋 Instrucciones</h4><ul><li>10 preguntas de selección múltiple</li><li>Retroalimentación inmediata</li><li>Calificación final al terminar</li></ul></div>',unsafe_allow_html=True)
        if st.button("▶ Iniciar evaluación",type="primary"):
            st.session_state.qest="curso"; st.session_state.qidx=0
            st.session_state.qscore=0; st.session_state.qpregs=random.sample(PREGUNTAS,10)
            st.session_state.qresp={}; st.rerun()
    elif st.session_state.qest=="curso":
        idx=st.session_state.qidx; pregs=st.session_state.qpregs; total=len(pregs)
        st.progress(idx/total,text=f"Pregunta {idx+1} de {total} | Correctas: {st.session_state.qscore}")
        q=pregs[idx]
        st.markdown(f'<div class="teoria-card"><div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Pregunta {idx+1} de {total}</div><div style="font-size:1.05rem;font-weight:600;color:#1e3a5f;margin-top:8px;">{q["p"]}</div></div>',unsafe_allow_html=True)
        if idx not in st.session_state.qresp:
            resp=st.radio("Selecciona:",q["ops"],key=f"q_{idx}",index=None)
            if resp:
                letra=resp[0]; ok=letra==q["r"]
                st.session_state.qresp[idx]={"resp":letra,"ok":ok}
                if ok: st.session_state.qscore+=1
                st.rerun()
        else:
            info=st.session_state.qresp[idx]
            rd=next(o for o in q["ops"] if o.startswith(info["resp"]))
            st.radio("Selecciona:",q["ops"],key=f"q_{idx}_s",index=q["ops"].index(rd),disabled=True)
            if info["ok"]: st.markdown(f'<div class="quiz-ok">✅ <b>¡Correcto!</b> — {q["exp"]}</div>',unsafe_allow_html=True)
            else:
                rc=next(o for o in q["ops"] if o.startswith(q["r"]))
                st.markdown(f'<div class="quiz-bad">❌ <b>Incorrecto.</b> Correcta: <b>{rc}</b><br>{q["exp"]}</div>',unsafe_allow_html=True)
            c1,c2=st.columns([1,4])
            with c1:
                lbl="Ver resultado →" if idx==total-1 else "Siguiente →"
                if st.button(lbl,type="primary"):
                    if idx<total-1: st.session_state.qidx+=1
                    else: st.session_state.qest="fin"
                    st.rerun()
        if st.button("🔄 Reiniciar",key="rein"):
            st.session_state.qest="inicio"; st.rerun()
    elif st.session_state.qest=="fin":
        sc=st.session_state.qscore; tot=len(st.session_state.qpregs); pct=round(sc/tot*100)
        if pct>=90: niv,col="🏆 EXCELENTE","#16a34a"
        elif pct>=70: niv,col="👍 BIEN","#2563eb"
        elif pct>=50: niv,col="📚 REGULAR","#d97706"
        else: niv,col="🔄 NECESITAS REPASAR","#dc2626"
        _,c,_=st.columns([1,2,1])
        with c:
            st.markdown(f'<div style="background:white;border:2px solid {col};border-radius:12px;padding:32px;text-align:center;"><div style="font-size:3rem;">{niv.split()[0]}</div><div style="font-size:2rem;font-weight:700;color:{col};">{pct}%</div><div style="color:#64748b;">{sc} de {tot} correctas</div><div style="height:8px;background:#e2e8f0;border-radius:4px;margin:16px 0;"><div style="height:100%;width:{pct}%;background:{col};border-radius:4px;"></div></div><div style="font-size:1.1rem;font-weight:600;color:{col};">{" ".join(niv.split()[1:])}</div></div>',unsafe_allow_html=True)
        if st.button("🔄 Hacer quiz nuevamente",type="primary"):
            st.session_state.qest="inicio"; st.rerun()

def modulo_exportar():
    st.markdown('<div class="section-title">📄 Exportar Reporte</div>',unsafe_allow_html=True)
    tx=st.session_state.get("df_xbar") is not None
    tp=st.session_state.get("df_p") is not None
    if not tx and not tp:
        st.markdown('<div class="alert-warn">⚠️ <b>No hay datos para exportar.</b> Genera primero una Carta X̄-R o una Carta p.</div>',unsafe_allow_html=True)
        return
    if tx:
        st.markdown("### 📈 Reporte Carta X̄-R")
        st.dataframe(st.session_state["df_xbar"],hide_index=True,use_container_width=True)
        csv=st.session_state["df_xbar"].to_csv(index=False,encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("⬇️ Descargar X̄-R (.csv)",csv,"reporte_xbar_r.csv","text/csv",type="primary")
    if tp:
        st.markdown("### 📉 Reporte Carta p")
        st.dataframe(st.session_state["df_p"],hide_index=True,use_container_width=True)
        csv=st.session_state["df_p"].to_csv(index=False,encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("⬇️ Descargar Carta p (.csv)",csv,"reporte_carta_p.csv","text/csv",type="primary")
    st.markdown('<div class="alert-info">💡 <b>Abrir en Excel:</b> Datos → Desde texto/CSV → UTF-8 → Delimitador: coma</div>',unsafe_allow_html=True)

def main():
    mostrar_header()
    mod=sidebar_nav()
    if "Teoría" in mod: modulo_teoria()
    elif "X̄-R" in mod: modulo_xbar()
    elif "Carta p" in mod: modulo_carta_p()
    elif "Nelson" in mod: modulo_nelson()
    elif "Quiz" in mod: modulo_quiz()
    elif "Exportar" in mod: modulo_exportar()

if __name__=="__main__":
    main()
