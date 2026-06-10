"""
Cartas de Control de Calidad — UTP
Herramienta Didáctica Interactiva
Universidad Tecnológica de Pereira
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, random, datetime, json, os

# ── Google Sheets ──────────────────────────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_OK = True
except ImportError:
    GSPREAD_OK = False

SHEET_URL = "https://docs.google.com/spreadsheets/d/1DO_VamNj70zT1qTDe185aMPIfDhTGcYjDZtzjK-kygQ/edit"

def get_gsheet():
    if not GSPREAD_OK:
        return None
    try:
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL)
        ws = sheet.sheet1
        if not ws.row_values(1):
            ws.append_row(["Nombre","Codigo","Correctas","Nota","Fecha"])
        return ws
    except Exception:
        return None

def guardar_en_sheets(nombre, codigo, correctas, nota, fecha):
    try:
        ws = get_gsheet()
        if ws:
            ws.append_row([nombre, codigo, int(correctas), float(nota), fecha])
            return True
    except Exception:
        pass
    return False

def leer_de_sheets():
    try:
        ws = get_gsheet()
        if ws:
            datos = ws.get_all_records()
            if datos:
                return pd.DataFrame(datos)
    except Exception:
        pass
    return None

st.set_page_config(
    page_title="Cartas de Control de Calidad — UTP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  ESTILOS
# ══════════════════════════════════════════════════════════════
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
.quiz-fullscreen{background:white;padding:32px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);}
.ref-card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:12px;font-size:0.88rem;color:#374151;line-height:1.7;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CONSTANTES SPC
# ══════════════════════════════════════════════════════════════
XR_CONST = {
    2:(1.880,0.000,3.267,1.128), 3:(1.023,0.000,2.575,1.693),
    4:(0.729,0.000,2.282,2.059), 5:(0.577,0.000,2.115,2.326),
    6:(0.483,0.000,2.004,2.534), 7:(0.419,0.076,1.924,2.704),
    8:(0.373,0.136,1.864,2.847), 9:(0.337,0.184,1.816,2.970),
    10:(0.308,0.223,1.777,3.078),
}

# ══════════════════════════════════════════════════════════════
#  BANCO DE 50 PREGUNTAS
# ══════════════════════════════════════════════════════════════
BANCO_PREGUNTAS = [
    # Fundamentos
    {"p":"¿Quién desarrolló las cartas de control en la década de 1920?",
     "ops":["A) W. Edwards Deming","B) Joseph Juran","C) Walter A. Shewhart","D) Kaoru Ishikawa"],"r":"C",
     "exp":"Walter A. Shewhart las desarrolló en los Laboratorios Bell de AT&T en la década de 1920."},
    {"p":"¿Qué representa la Línea Central (LC) en una carta de control?",
     "ops":["A) El límite máximo permitido","B) El promedio del estadístico graficado","C) La especificación del cliente","D) La desviación estándar"],"r":"B",
     "exp":"La LC es el promedio del estadístico graficado (media, rango, proporción, etc.)."},
    {"p":"¿Por qué se usan límites de control a ±3 sigmas?",
     "ops":["A) Por convención arbitraria","B) Porque cubre el 95% de los datos","C) Por equilibrio entre falsas alarmas y detección real","D) Porque lo exige la norma ISO"],"r":"C",
     "exp":"Shewhart eligió 3σ por equilibrio económico entre el error tipo I (falsa alarma, 0.27%) y el error tipo II (no detectar un cambio real)."},
    {"p":"¿Cuál es la probabilidad de una falsa alarma con límites a ±3 sigmas?",
     "ops":["A) 5%","B) 1%","C) 0.27%","D) 3%"],"r":"C",
     "exp":"Con límites a ±3σ, solo el 0.27% de los puntos caen fuera estando el proceso bajo control (aprox. 1 de cada 370 puntos)."},
    {"p":"Un proceso 'bajo control estadístico' significa:",
     "ops":["A) Produce sin ningún defecto","B) Solo tiene variación por causas comunes","C) Cumple las especificaciones del cliente","D) Tiene Cpk mayor a 1.33"],"r":"B",
     "exp":"Control estadístico significa que solo están presentes causas comunes. No implica ausencia de defectos ni cumplimiento de especificaciones."},
    {"p":"¿Cuál es la diferencia principal entre límites de control y límites de especificación?",
     "ops":["A) Son exactamente lo mismo","B) Los de control vienen del proceso, los de especificación del cliente","C) Los de especificación son más amplios siempre","D) Solo los de control se dibujan en la carta"],"r":"B",
     "exp":"Los límites de control salen de la voz del proceso (variabilidad real). Los de especificación salen de la voz del cliente. Nunca se mezclan en la misma carta."},
    {"p":"¿Qué es el 'sobreajuste' o tampering en SPC?",
     "ops":["A) Ajustar el proceso cuando hay una causa especial","B) Reaccionar al ruido como si fuera señal y ajustar un proceso estable","C) Agregar más límites de control","D) Usar subgrupos demasiado grandes"],"r":"B",
     "exp":"El sobreajuste es reaccionar al ruido como si fuera señal. Deming lo ilustró con el experimento del embudo: ajustar un proceso estable lo empeora."},
    {"p":"¿Qué tipo de distribución estadística respalda las cartas por variables?",
     "ops":["A) Binomial","B) Poisson","C) Normal","D) Exponencial"],"r":"C",
     "exp":"Las cartas por variables se basan en la distribución Normal, ya que los datos son mediciones continuas."},
    {"p":"¿Qué tipo de distribución respalda las cartas p y np?",
     "ops":["A) Normal","B) Poisson","C) Binomial","D) Uniforme"],"r":"C",
     "exp":"Las cartas p y np se basan en la distribución Binomial, ya que cada unidad se clasifica como defectuosa o no defectuosa (pasa/no pasa)."},
    {"p":"¿Qué distribución estadística respalda las cartas c y u?",
     "ops":["A) Normal","B) Binomial","C) Poisson","D) t de Student"],"r":"C",
     "exp":"Las cartas c y u se basan en la distribución de Poisson, usada cuando se cuentan defectos (una pieza puede tener múltiples defectos)."},
    # Tipos de cartas
    {"p":"¿Qué controla la carta X̄ (de medias)?",
     "ops":["A) La variabilidad dentro del subgrupo","B) La tendencia central del proceso","C) El número de defectuosos","D) La proporción defectiva"],"r":"B",
     "exp":"La carta X̄ controla la tendencia central (la media) del proceso a partir de subgrupos. Siempre va emparejada con la carta R o S."},
    {"p":"¿Qué controla la carta R?",
     "ops":["A) El promedio del proceso","B) La proporción de defectuosos","C) La variabilidad dentro de cada subgrupo usando el rango","D) El número total de defectos"],"r":"C",
     "exp":"La carta R controla la variabilidad dentro de cada subgrupo usando el rango (máximo menos mínimo)."},
    {"p":"¿Cuándo se prefiere la carta S sobre la carta R?",
     "ops":["A) Con subgrupos pequeños (n=2 a 9)","B) Con subgrupos grandes (n≥10) o de tamaño variable","C) Cuando los datos son atributos","D) Cuando n=1"],"r":"B",
     "exp":"La carta S usa la desviación estándar, que estima σ mejor que el rango cuando hay muchos datos por subgrupo (n≥10)."},
    {"p":"¿Cuándo se usa la carta I-MR?",
     "ops":["A) Cuando n≥10","B) Cuando n=2 a 9","C) Cuando n=1 (una medición por dato)","D) Solo con datos de atributos"],"r":"C",
     "exp":"La carta I-MR se usa cuando cada medición es su propio subgrupo (n=1). Por ejemplo: pH de cada lote en un reactor, una medición por lote."},
    {"p":"¿Cuál es la constante E₂ para la carta de individuos I-MR?",
     "ops":["A) 1.880","B) 2.660","C) 0.577","D) 3.267"],"r":"B",
     "exp":"E₂ = 2.66 para rango móvil de 2 puntos. Se usa para calcular los límites de la carta de individuos: LCS = X̄ + 2.66·MR̄."},
    {"p":"¿Qué diferencia hay entre una unidad defectuosa y un defecto?",
     "ops":["A) Son exactamente lo mismo","B) Una unidad defectuosa es la que no cumple; un defecto es cada falla individual","C) Los defectos son solo para productos físicos","D) Una unidad defectuosa tiene exactamente un defecto"],"r":"B",
     "exp":"Una camisa con tres costuras mal hechas es UNA unidad defectuosa pero tiene TRES defectos. Esta diferencia determina si se usa carta p/np (defectuosas) o c/u (defectos)."},
    {"p":"¿Cuándo se usa la carta np en lugar de la carta p?",
     "ops":["A) Cuando el tamaño de muestra varía","B) Solo con tamaño de muestra constante","C) Cuando los datos siguen distribución Poisson","D) Con subgrupos grandes"],"r":"B",
     "exp":"La carta np solo se usa con tamaño de muestra constante. Es más intuitiva que la carta p porque grafica el número de defectuosas, no la proporción."},
    {"p":"¿Cuándo se usa la carta c?",
     "ops":["A) Cuando el área de inspección varía","B) Cuando el área de inspección es constante","C) Con tamaño de muestra variable","D) Cuando n=1"],"r":"B",
     "exp":"La carta c se usa cuando el área de inspección (la unidad inspeccionada) es constante. Ejemplo: defectos de pintura por carrocería del mismo modelo."},
    {"p":"¿Cuál es la fórmula del LCS de la carta c?",
     "ops":["A) c̄ + 3·√(c̄/n)","B) c̄ + A₂·R̄","C) c̄ + 3·√c̄","D) p̄ + 3·√(p̄(1-p̄)/n)"],"r":"C",
     "exp":"Para la carta c: LCS = c̄ + 3·√c̄ y LCI = c̄ - 3·√c̄ (si da negativo se usa 0). Se basa en la distribución Poisson."},
    {"p":"¿Cuál es la diferencia entre la carta c y la carta u?",
     "ops":["A) La carta c es para variables y la u para atributos","B) La carta u normaliza los defectos por unidad cuando el área de inspección varía","C) La carta u usa distribución Binomial","D) No hay diferencia práctica"],"r":"B",
     "exp":"La carta u es la versión normalizada de la carta c. Se usa cuando las unidades de inspección tienen tamaño distinto (defectos por metro cuadrado, por ejemplo)."},
    # Carta X̄-R específica
    {"p":"Para n=5, ¿cuánto vale la constante A₂?",
     "ops":["A) 1.880","B) 0.729","C) 0.577","D) 0.419"],"r":"C",
     "exp":"Para subgrupos de tamaño n=5, A₂ = 0.577. Esta constante se multiplica por R̄ para calcular los límites de la carta X̄."},
    {"p":"¿Qué constante se usa para calcular el LCS de la carta R?",
     "ops":["A) A₂","B) D₃","C) D₄","D) d₂"],"r":"C",
     "exp":"LCS de la carta R = D₄ · R̄. D₄ depende del tamaño del subgrupo n."},
    {"p":"Para n≤6, ¿cuánto vale D₃?",
     "ops":["A) 0.076","B) 0.136","C) 0","D) 1.023"],"r":"C",
     "exp":"Para n menor o igual a 6, D₃ = 0, lo que significa que el LCI de la carta R siempre es 0."},
    {"p":"¿Para qué sirve la constante d₂ en la carta X̄-R?",
     "ops":["A) Para calcular el LCS de X̄","B) Para estimar la desviación estándar del proceso a partir de R̄","C) Para calcular el LCI de la carta R","D) Para determinar el tamaño del subgrupo"],"r":"B",
     "exp":"σ̂ = R̄/d₂. La constante d₂ permite estimar la desviación estándar del proceso a partir del rango promedio."},
    {"p":"¿Por qué se analiza primero la carta R antes que la carta X̄?",
     "ops":["A) Por convención histórica","B) Porque si la variabilidad está fuera de control, los límites de X̄ no son confiables","C) Porque la carta R es más fácil de interpretar","D) No importa el orden de análisis"],"r":"B",
     "exp":"Regla de oro: si la variabilidad está fuera de control, los límites de la carta de medias no son confiables porque se calculan a partir de R̄ o S̄."},
    {"p":"¿Qué representa el rango R en un subgrupo?",
     "ops":["A) El promedio de las mediciones","B) La desviación estándar del subgrupo","C) La diferencia entre el valor máximo y mínimo","D) El total de mediciones del subgrupo"],"r":"C",
     "exp":"El rango R = máximo - mínimo dentro del subgrupo. Mide la variabilidad interna de cada muestra."},
    # Carta p específica
    {"p":"¿Cuál es la fórmula del LCS de la carta p?",
     "ops":["A) p̄ + A₂·R̄","B) p̄ + 3·√(p̄(1-p̄)/n)","C) p̄ + 3·√p̄","D) p̄ + D₄·R̄"],"r":"B",
     "exp":"LCS de la carta p = p̄ + 3·√(p̄(1-p̄)/n). Se basa en la distribución binomial aproximada por la normal."},
    {"p":"Si el LCI de la carta p resulta negativo, ¿qué valor se usa?",
     "ops":["A) El valor negativo calculado","B) -0.01","C) 0","D) No tiene LCI la carta p"],"r":"C",
     "exp":"Una proporción no puede ser negativa. Si el LCI calculado es negativo, se establece LCI = 0."},
    {"p":"¿Cómo se calcula p̄ (proporción media global)?",
     "ops":["A) Promedio de las proporciones individuales","B) Total de defectuosas dividido entre total de unidades inspeccionadas","C) Total de defectuosas dividido entre número de períodos","D) Suma de los tamaños de muestra dividido entre k"],"r":"B",
     "exp":"p̄ = Σdᵢ / Σnᵢ. Es el total de unidades defectuosas dividido entre el total de unidades inspeccionadas."},
    {"p":"¿Qué ocurre con los límites de la carta p cuando el tamaño de muestra varía?",
     "ops":["A) Se mantienen constantes","B) Se recalculan por punto y forman escalones","C) Se usa el promedio de los tamaños","D) Se invalida la carta"],"r":"B",
     "exp":"Cuando n varía, los límites se recalculan para cada punto usando el n correspondiente, formando una línea escalonada en la gráfica."},
    # Reglas de Nelson
    {"p":"¿Cuántos puntos consecutivos al mismo lado del CL indica la Regla 2 de Nelson?",
     "ops":["A) 6","B) 7","C) 9","D) 12"],"r":"C",
     "exp":"La Regla 2 establece que 9 puntos consecutivos al mismo lado de la línea central es señal de corrimiento de la media."},
    {"p":"¿Qué indica la Regla 3 de Nelson (6 puntos en tendencia)?",
     "ops":["A) Corrimiento de la media","B) Cambio gradual como desgaste o temperatura","C) Mezcla de dos procesos","D) Error de medición puntual"],"r":"B",
     "exp":"6 puntos consecutivos todos subiendo o bajando indican un cambio gradual: desgaste de herramienta, temperatura creciente, fatiga del operador."},
    {"p":"¿Qué causa típica indica la Regla 4 (14 puntos alternando)?",
     "ops":["A) Desgaste de herramienta","B) Corrimiento de la media","C) Mezcla de dos procesos o fuentes de variación","D) Error en el sistema de medición"],"r":"C",
     "exp":"14 puntos alternando sistemáticamente sugieren mezcla de dos procesos diferentes: dos máquinas, dos operadores o dos turnos."},
    {"p":"La Regla 5 de Nelson dice que hay señal cuando:",
     "ops":["A) 5 de 6 puntos están más allá de ±2σ","B) 2 de 3 puntos consecutivos están más allá de ±2σ en el mismo lado","C) 3 puntos seguidos están en zona A","D) 4 puntos seguidos están fuera de ±1σ"],"r":"B",
     "exp":"Regla 5: 2 de 3 puntos consecutivos más allá de ±2σ (zona A) en el mismo lado. Es señal temprana de desestabilización."},
    {"p":"¿Qué indica la Regla 7 (15 puntos dentro de ±1σ)?",
     "ops":["A) Proceso muy preciso y estable","B) Variabilidad sospechosamente baja, posible estratificación","C) La media se corrió al centro","D) El proceso está mejorando"],"r":"B",
     "exp":"15 puntos dentro de ±1σ indica variabilidad sospechosamente baja. Puede indicar estratificación: datos de diferentes distribuciones mezclados artificialmente."},
    {"p":"¿Qué indica la Regla 8 (8 puntos fuera de ±1σ en ambos lados)?",
     "ops":["A) Proceso muy variable","B) Bimodalidad: el proceso tiene dos modos de operación mezclados","C) Tendencia creciente","D) Corrimiento de la media"],"r":"B",
     "exp":"Regla 8: 8 puntos fuera de ±1σ en ambos lados indica bimodalidad. El proceso tiene dos poblaciones mezcladas que evitan la zona central."},
    {"p":"¿Cuál de las 8 Reglas de Nelson requiere acción más inmediata?",
     "ops":["A) Regla 2","B) Regla 4","C) Regla 1","D) Regla 7"],"r":"C",
     "exp":"La Regla 1 (punto fuera de ±3σ) requiere acción inmediata. Indica un evento extraordinario que casi con certeza no fue por azar (probabilidad 0.27%)."},
    {"p":"Activar más Reglas de Nelson en una carta:",
     "ops":["A) Siempre mejora la detección sin consecuencias","B) Aumenta la sensibilidad pero también las falsas alarmas","C) Reduce las falsas alarmas","D) No tiene ningún efecto práctico"],"r":"B",
     "exp":"Activar más reglas aumenta la sensibilidad para detectar problemas, pero también aumenta las falsas alarmas. Se eligen según el proceso y el costo de cada tipo de error."},
    # Cómo elegir la carta
    {"p":"Si el dato se mide (continuo) y n=1, ¿qué carta se usa?",
     "ops":["A) X̄-R","B) X̄-S","C) I-MR","D) p"],"r":"C",
     "exp":"Cuando no es posible o no tiene sentido agrupar (n=1), se usa la carta I-MR (individuales y rango móvil)."},
    {"p":"Si el dato se cuenta (discreto), son unidades defectuosas y n es constante, ¿qué carta es más intuitiva?",
     "ops":["A) p","B) np","C) c","D) u"],"r":"B",
     "exp":"La carta np es más intuitiva para planta porque grafica el número de defectuosas directamente, no la proporción. Requiere n constante."},
    {"p":"Para controlar defectos por metro cuadrado de tela en rollos de longitud variable, ¿qué carta se usa?",
     "ops":["A) c","B) p","C) u","D) np"],"r":"C",
     "exp":"La carta u se usa para defectos por unidad cuando el área de inspección varía. Es la versión normalizada de la carta c."},
    {"p":"¿Cuándo se prefiere X̄-R sobre X̄-S?",
     "ops":["A) Con subgrupos grandes (n≥10)","B) Con subgrupos pequeños (n=2 a 9)","C) Cuando los datos no son normales","D) Cuando n varía"],"r":"B",
     "exp":"Con subgrupos pequeños (n=2 a 9) se prefiere la carta R porque el rango es fácil de calcular y suficiente para pocos datos por subgrupo."},
    # Capacidad del proceso
    {"p":"¿Qué mide el índice Cp?",
     "ops":["A) Si el proceso está centrado","B) La capacidad potencial comparando el ancho de la especificación con el del proceso","C) El número de defectos por millón","D) La estabilidad del proceso"],"r":"B",
     "exp":"Cp = (LSE - LIE) / 6σ. Compara el ancho de la especificación con el ancho natural del proceso (±3σ). Mide la capacidad potencial, ignorando si está centrado."},
    {"p":"¿Qué ventaja tiene Cpk sobre Cp?",
     "ops":["A) Es más fácil de calcular","B) Penaliza el descentrado del proceso","C) No requiere límites de especificación","D) Se puede calcular sin datos históricos"],"r":"B",
     "exp":"Cpk = mín[(LSE-X̄)/3σ, (X̄-LIE)/3σ]. Penaliza el descentrado. Si Cpk es menor que Cp, el proceso está corrido respecto al centro de la especificación."},
    {"p":"¿Cuál es el valor mínimo de Cpk que muchas industrias exigen?",
     "ops":["A) 1.00","B) 1.33","C) 1.67","D) 2.00"],"r":"B",
     "exp":"Cpk ≥ 1.33 es la referencia común en muchas industrias para considerar un proceso capaz. Equivale a tener los límites de especificación a ±4σ del proceso."},
    {"p":"¿Cuál es el orden correcto para analizar un proceso?",
     "ops":["A) Primero capacidad, luego estabilidad","B) Primero estabilidad (carta de control), luego capacidad (Cp/Cpk)","C) Se pueden hacer simultáneamente","D) Solo se necesita uno de los dos análisis"],"r":"B",
     "exp":"La capacidad solo tiene sentido sobre un proceso que ya está bajo control estadístico. Medir la capacidad de un proceso inestable da un número sin significado porque σ no es constante."},
    {"p":"¿Cómo se estima σ para calcular los índices de capacidad cuando se usa carta X̄-R?",
     "ops":["A) Con la desviación estándar de todos los datos","B) Con σ = R̄/d₂","C) Con σ = S̄/c₄","D) Con el rango total de los datos"],"r":"B",
     "exp":"Cuando se usa carta X̄-R, σ se estima a partir de la carta con σ̂ = R̄/d₂. Esto garantiza que se usa la variabilidad dentro de los subgrupos, no la variabilidad total."},
    # CUSUM y EWMA
    {"p":"¿Para qué tipo de cambios son más efectivas las cartas CUSUM y EWMA?",
     "ops":["A) Cambios grandes y repentinos (≥2σ)","B) Cambios pequeños y sostenidos (0.5σ–1σ)","C) Variaciones aleatorias normales","D) Cambios estacionales"],"r":"B",
     "exp":"Las cartas Shewhart reaccionan rápido a cambios grandes, pero son lentas para cambios pequeños. CUSUM y EWMA llenan ese hueco detectando corrimientos pequeños y persistentes."},
    {"p":"¿Qué hace la carta CUSUM?",
     "ops":["A) Promedia los últimos k puntos","B) Acumula las desviaciones respecto a un valor objetivo en dos sumas","C) Calcula la desviación estándar móvil","D) Grafica el valor individual sin transformación"],"r":"B",
     "exp":"CUSUM (suma acumulada) acumula las desviaciones respecto a un valor objetivo en dos sumas (superior e inferior). Señala cuando una suma supera el intervalo de decisión h."},
    {"p":"En la carta EWMA, ¿qué efecto tiene un valor menor de λ?",
     "ops":["A) Más sensibilidad a cambios grandes","B) Más sensibilidad a cambios pequeños y sostenidos","C) Menos peso a los datos recientes","D) Límites de control más amplios"],"r":"B",
     "exp":"En EWMA, cuanto menor es λ, más peso se da a datos históricos y más sensible es a cambios pequeños. λ típicamente está entre 0.05 y 0.25."},
    # Glosario y conceptos generales
    {"p":"¿Qué es un subgrupo racional en SPC?",
     "ops":["A) Un grupo de muestras tomadas en condiciones diferentes","B) Un grupo de muestras tomadas en condiciones similares para minimizar la variabilidad interna","C) Cualquier grupo de 5 mediciones","D) Un grupo con exactamente n=4 observaciones"],"r":"B",
     "exp":"Un subgrupo racional es un grupo de muestras tomadas en condiciones tan similares como sea posible, para que la variabilidad dentro del subgrupo refleje solo la variación aleatoria del proceso."},
    {"p":"¿Cuántos subgrupos se recomiendan mínimo para establecer los límites de control?",
     "ops":["A) 5 a 10","B) 10 a 15","C) 20 a 25","D) 30 a 50"],"r":"C",
     "exp":"Se recomiendan mínimo 20 a 25 subgrupos para establecer los límites de control con suficiente confiabilidad estadística."},
    {"p":"¿Qué significa CEP?",
     "ops":["A) Control Estadístico de Procesos","B) Carta de Evaluación del Proceso","C) Control de Especificaciones del Producto","D) Carta de Estabilidad del Proceso"],"r":"A",
     "exp":"CEP = Control Estadístico de Procesos. Es la traducción al español de SPC (Statistical Process Control)."},
    {"p":"En la carta I-MR, ¿cómo se calcula el rango móvil (MR)?",
     "ops":["A) Máximo menos mínimo de todos los datos","B) Diferencia en valor absoluto entre dos observaciones consecutivas","C) Desviación estándar de los últimos 5 puntos","D) Promedio de los últimos 3 rangos"],"r":"B",
     "exp":"El rango móvil MR(i) = |x(i) - x(i-1)|. Es la diferencia en valor absoluto entre cada observación y la anterior."},
    {"p":"¿Cuál es la fórmula del LCS de la carta np?",
     "ops":["A) np̄ + 3·√(np̄(1-p̄))","B) n·p̄ + 3·√(n·p̄·(1-p̄))","C) p̄ + 3·√(p̄/n)","D) n·p̄ + A₂·R̄"],"r":"B",
     "exp":"LCS de la carta np = n·p̄ + 3·√(n·p̄·(1-p̄)). Es la carta p multiplicada por n, sin dividir entre el tamaño de muestra."},
]

# ══════════════════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════════════════
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
    for ax, datos, ucl, cl, lcl, ylabel, color_ok in [
        (ax1, xbars, ucl_x, cl_x, lcl_x, 'X̄ (Promedio)', '#2563eb'),
        (ax2, rangos, ucl_r, cl_r, lcl_r, 'R (Rango)', '#16a34a'),
    ]:
        ax.set_facecolor('#f8fafc')
        ax.grid(True, color='#e2e8f0', linestyle='--', alpha=0.8)
        s = (ucl - cl) / 3 if ucl != cl else 1
        ax.axhspan(cl+2*s, ucl+abs(s)*0.5, alpha=0.07, color='#ef4444')
        ax.axhspan(max(0, lcl-abs(s)*0.5), cl-2*s, alpha=0.07, color='#ef4444')
        ax.axhspan(cl+s, cl+2*s, alpha=0.07, color='#f59e0b')
        ax.axhspan(cl-2*s, cl-s, alpha=0.07, color='#f59e0b')
        ax.axhline(ucl, color='#ef4444', linestyle='--', linewidth=1.8, label=f'UCL={ucl:.3f}')
        ax.axhline(cl,  color='#2563eb', linestyle='-',  linewidth=2.0, label=f'CL ={cl:.3f}')
        ax.axhline(lcl, color='#ef4444', linestyle='--', linewidth=1.8, label=f'LCL={lcl:.3f}')
        fuera = [i for i,v in enumerate(datos) if v>ucl or v<lcl]
        colores = ['#ef4444' if i in fuera else color_ok for i in range(len(datos))]
        ax.plot(idx, datos, color='#94a3b8', linewidth=1.3, zorder=2)
        ax.scatter(idx, datos, c=colores, s=[80 if i in fuera else 45 for i in range(len(datos))],
                   zorder=3, edgecolors='white', linewidths=1.2)
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
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y,_: f'{y*100:.1f}%'))
    ax.set_xlabel('Período', color='#64748b')
    ax.set_ylabel('Proporción defectiva', color='#1e3a5f')
    ax.tick_params(colors='#64748b')
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
    for sp in ax.spines.values(): sp.set_edgecolor('#e2e8f0')
    plt.tight_layout()
    return fig_to_image(fig)

def graficar_regla(datos, ucl, cl, lcl, flagged, titulo):
    fig, ax = plt.subplots(figsize=(11, 4), facecolor='white')
    ax.set_facecolor('#f8fafc')
    ax.set_title(titulo, color='#1e3a5f', fontweight='bold')
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
    colores = ['#f59e0b' if i in flagged else ('#ef4444' if (v>ucl or v<lcl) else '#2563eb')
               for i,v in enumerate(datos)]
    tamaños = [90 if i in flagged else 45 for i in range(len(datos))]
    ax.scatter(idx, datos, c=colores, s=tamaños, zorder=3, edgecolors='white', linewidths=1.2)
    ax.legend(fontsize=8, framealpha=0.9)
    for sp in ax.spines.values(): sp.set_edgecolor('#e2e8f0')
    plt.tight_layout()
    return fig_to_image(fig)

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
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
            "🗂️ Tipos de Cartas",
            "⚠️ Reglas de Nelson",
            "📐 Capacidad del Proceso",
            "🚀 Cartas Avanzadas",
            "🎯 Quiz de Evaluación",
            "👨‍🏫 Panel del Profesor",
            "📄 Exportar Reporte",
            "📚 Referencias",
        ], label_visibility="collapsed")
        st.markdown("---")
        st.markdown("<div style='font-size:0.75rem;color:#94a3b8;line-height:1.8;'><b style='color:#bfdbfe;'>Normativa</b><br>ISO 7870-2<br>AIAG SPC Manual<br>Nelson (1984)<br><br><b style='color:#bfdbfe;'>Tecnología</b><br>Python · Streamlit</div>", unsafe_allow_html=True)
    return modulo

# ══════════════════════════════════════════════════════════════
#  MÓDULO 1 — TEORÍA
# ══════════════════════════════════════════════════════════════
def modulo_teoria():
    st.markdown('<div class="section-title">📘 Teoría y Fundamentos del SPC</div>', unsafe_allow_html=True)
    tab1,tab2,tab3,tab4,tab5 = st.tabs(["¿Qué es SPC?","Tipos de Variación","Anatomía","Zonas","Implementación"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><h4>📌 Definición</h4>Una carta de control es un gráfico que muestra una característica de un proceso a lo largo del tiempo, junto con tres líneas de referencia. Sirve para distinguir si la variación observada es "normal" o si algo cambió y hay que intervenir.<br><br>Desarrollada por <b>Walter A. Shewhart</b> en los Laboratorios Bell en la década de 1920.</div>', unsafe_allow_html=True)
            st.markdown('<div class="teoria-card"><h4>🎯 Objetivo principal</h4>Separar el <b>ruido</b> (variación natural) de la <b>señal</b> (evento que requiere acción). Un proceso bajo control estadístico es <b>estable y predecible</b>, aunque no necesariamente bueno.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="teoria-card"><h4>⚖️ ¿Por qué ±3 sigmas?</h4>Shewhart eligió 3σ por equilibrio económico entre dos errores:<br><br>• <b>Error tipo I</b> (falsa alarma): declarar que el proceso cambió cuando no lo hizo. Con ±3σ solo el 0.27% de puntos caen fuera (~1 de cada 370).<br><br>• <b>Error tipo II</b>: no detectar un cambio real. Es una decisión práctica de ingeniería, no un nivel de significancia estadístico puro.</div>', unsafe_allow_html=True)
            st.markdown('<div class="teoria-card"><h4>⚠️ Dos errores a evitar</h4><b>1. Sobreajuste (tampering):</b> reaccionar al ruido como señal y ajustar un proceso estable. Lo empeora (experimento del embudo de Deming).<br><br><b>2. Ignorar señales reales:</b> no reaccionar ante una causa especial.</div>', unsafe_allow_html=True)
    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card" style="border-left:4px solid #16a34a;"><h4 style="color:#16a34a;">✅ Causas Comunes (aleatorias)</h4>Variación natural e inherente al proceso. Es el "ruido" de fondo. Siempre presente y predecible dentro de un rango.<br><br><b>El proceso está BAJO CONTROL.</b><br><br>No se ajusta individualmente. Para reducirla hay que mejorar el sistema completo.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="teoria-card" style="border-left:4px solid #dc2626;"><h4 style="color:#dc2626;">🚨 Causas Especiales (asignables)</h4>Una señal de que algo cambió: una máquina se desajustó, entró un lote distinto de materia prima, cambió el operario, falló un instrumento.<br><br><b>El proceso está FUERA DE CONTROL.</b><br><br>Requiere investigación y acción inmediata.</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="alert-error">⚠️ <b>Distinción crítica:</b> Límites de control ≠ Límites de especificación. Los límites de control salen de la <b>voz del proceso</b> (variabilidad real). Los de especificación salen de la <b>voz del cliente</b>. Un proceso puede estar bajo control y aun así producir piezas fuera de especificación. <b>Nunca se dibujan los límites de especificación sobre una carta de control.</b></div>', unsafe_allow_html=True)
    with tab3:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("### Las tres líneas de toda carta")
            st.markdown('<div class="formula-box">LCS / UCL = LC + 3σ  ← Límite Superior de Control<br>─────────────────────────────────<br>LC       = promedio   ← Línea Central<br>─────────────────────────────────<br>LCI / LCL = LC - 3σ  ← Límite Inferior de Control<br><br>Nota: Si LCI da negativo en cartas de conteo → se toma 0</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("### Las dos grandes familias")
            st.dataframe(pd.DataFrame({
                "Familia":["Por variables","Por atributos"],
                "Tipo de dato":["Cuantitativo continuo (se mide)","Cualitativo discreto (se cuenta)"],
                "Ejemplo":["Peso, longitud, temperatura","N° defectos, pasa/no pasa"],
                "Distribución":["Normal","Binomial o Poisson"]
            }), hide_index=True, use_container_width=True)
    with tab4:
        st.markdown("### Distribución de zonas (±1σ, ±2σ, ±3σ)")
        st.markdown("""
        <div style="display:flex;border-radius:8px;overflow:hidden;height:48px;margin:8px 0;font-size:0.68rem;font-weight:700;text-align:center;">
        <div style="flex:0.3;background:#fca5a5;display:flex;align-items:center;justify-content:center;">0.13%</div>
        <div style="flex:2;background:#fed7aa;display:flex;align-items:center;justify-content:center;">C 2.1%</div>
        <div style="flex:13.6;background:#fef08a;display:flex;align-items:center;justify-content:center;">B 13.6%</div>
        <div style="flex:34;background:#bbf7d0;display:flex;align-items:center;justify-content:center;">A 34.13%</div>
        <div style="flex:34;background:#bbf7d0;display:flex;align-items:center;justify-content:center;">A 34.13%</div>
        <div style="flex:13.6;background:#fef08a;display:flex;align-items:center;justify-content:center;">B 13.6%</div>
        <div style="flex:2;background:#fed7aa;display:flex;align-items:center;justify-content:center;">C 2.1%</div>
        <div style="flex:0.3;background:#fca5a5;display:flex;align-items:center;justify-content:center;">0.13%</div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#64748b;font-family:monospace;margin-top:4px;">
        <span>LCI(−3σ)</span><span>−2σ</span><span>−1σ</span><span>LC</span><span>+1σ</span><span>+2σ</span><span>LCS(+3σ)</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.dataframe(pd.DataFrame({
            "Zona":["C (central)","B (intermedia)","A (alerta)","Fuera de límites"],
            "Rango":["Entre LC y ±1σ","Entre ±1σ y ±2σ","Entre ±2σ y ±3σ","Más allá de ±3σ"],
            "% área cada lado":["34.13%","13.59%","2.14%","0.13%"],
            "Acción":["Normal","Vigilar patrones","Señal de alerta","🚨 Investigar ya"]
        }), hide_index=True, use_container_width=True)
    with tab5:
        cols = st.columns(5)
        pasos = [("📥","1. Recolectar","Mín. 20-25 subgrupos racionales"),("🧮","2. Calcular","Estadísticos y límites de control"),("📊","3. Graficar","Puntos, LC, LCS y LCI"),("🔍","4. Analizar","Aplicar Reglas de Nelson"),("🔧","5. Actuar","Eliminar causas especiales")]
        for col,(ic,tit,desc) in zip(cols,pasos):
            with col:
                st.markdown(f'<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px;text-align:center;height:160px;"><div style="font-size:2rem;">{ic}</div><div style="font-weight:700;color:#1e3a5f;font-size:0.85rem;margin:8px 0 4px;">{tit}</div><div style="font-size:0.75rem;color:#64748b;">{desc}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO — TIPOS DE CARTAS
# ══════════════════════════════════════════════════════════════
def modulo_tipos_cartas():
    st.markdown('<div class="section-title">🗂️ Los 8 Tipos de Cartas de Control</div>', unsafe_allow_html=True)
    st.markdown("Existen **8 tipos** de cartas de control organizadas en dos grandes familias.")

    tab1,tab2,tab3 = st.tabs(["📏 Variables (4 cartas)","🔢 Atributos (4 cartas)","🧭 Cómo elegir la carta"])

    with tab1:
        st.markdown('<div class="alert-info">📌 <b>Regla de oro:</b> Se analiza primero la carta de dispersión (R o S). Si la variabilidad está fuera de control, los límites de la carta de medias no son confiables.</div>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("### 1) Carta X̄ (de medias)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> La tendencia central (media) del proceso a partir de subgrupos.<br><br><b>¿Cuándo usarla?</b> Siempre que se quiera vigilar el centrado del proceso. Va emparejada con carta R o S.<br><br><b>Ejemplo:</b> Diámetro promedio de un eje tomando muestras de 5 piezas cada hora.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">LC  = X̿ (gran media)<br>LCS = X̿ + A₂ · R̄<br>LCI = X̿ − A₂ · R̄</div>', unsafe_allow_html=True)

        st.markdown("### 2) Carta R (de rangos)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> La variabilidad dentro de cada subgrupo usando el rango (máximo − mínimo).<br><br><b>¿Cuándo usarla?</b> Con subgrupos pequeños (n = 2 a 9). El rango es fácil de calcular.<br><br><b>Ejemplo:</b> Dispersión del diámetro dentro de cada muestra de 5 ejes.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">LC  = R̄<br>LCS = D₄ · R̄<br>LCI = D₃ · R̄</div>', unsafe_allow_html=True)

        st.markdown("### 3) Carta S (de desviación estándar)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> La variabilidad dentro del subgrupo usando la desviación estándar (mejor que el rango para n grande).<br><br><b>¿Cuándo usarla?</b> Con subgrupos grandes (n ≥ 10) o de tamaño variable.<br><br><b>Ejemplo:</b> Proceso automatizado que registra 15–20 mediciones por subgrupo.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">LC  = S̄<br>LCS = B₄ · S̄<br>LCI = B₃ · S̄</div>', unsafe_allow_html=True)

        st.markdown("### 4) Carta I-MR (individuales y rango móvil)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> Procesos donde cada medición es su propio subgrupo (n = 1). La carta I grafica valores individuales; la MR, el rango móvil entre lecturas consecutivas.<br><br><b>¿Cuándo usarla?</b> Procesos lentos, mediciones costosas o destructivas, producción de bajo volumen.<br><br><b>Ejemplo:</b> pH de cada lote en un reactor (una medición por lote).</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">Carta I:<br>LC  = X̄<br>LCS = X̄ + E₂ · MR̄  (E₂ = 2.66)<br>LCI = X̄ − E₂ · MR̄<br><br>Carta MR:<br>LC  = MR̄<br>LCS = D₄ · MR̄ = 3.267 · MR̄<br>LCI = 0</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="alert-info">📌 La diferencia clave: <b>unidades defectuosas</b> (pasa/no pasa → Binomial → cartas p y np) vs <b>defectos</b> (múltiples fallas por pieza → Poisson → cartas c y u).<br><br>Ejemplo: Una camisa con 3 costuras mal hechas es <b>1 unidad defectuosa</b> pero tiene <b>3 defectos</b>.</div>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("### 5) Carta p (proporción de defectuosas)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> La proporción (fracción) de unidades defectuosas en cada muestra.<br><br><b>¿Cuándo usarla?</b> Tamaño de muestra constante o variable. Si n varía, los límites forman "escalones".<br><br><b>Ejemplo:</b> Porcentaje de facturas con error sobre el total revisado cada día.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">LC  = p̄<br>LCS = p̄ + 3·√(p̄(1−p̄)/n)<br>LCI = p̄ − 3·√(p̄(1−p̄)/n)<br>(si LCI < 0, usar 0)</div>', unsafe_allow_html=True)

        st.markdown("### 6) Carta np (número de defectuosas)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> El número de unidades defectuosas por muestra (la carta p sin dividir).<br><br><b>¿Cuándo usarla?</b> Solo con tamaño de muestra constante. Más intuitiva de leer en planta.<br><br><b>Ejemplo:</b> Número de piezas defectuosas en lotes fijos de 200 unidades.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">LC  = n·p̄<br>LCS = n·p̄ + 3·√(n·p̄·(1−p̄))<br>LCI = n·p̄ − 3·√(n·p̄·(1−p̄))<br>(si LCI < 0, usar 0)</div>', unsafe_allow_html=True)

        st.markdown("### 7) Carta c (número de defectos)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> El número total de defectos en una unidad de inspección de tamaño constante.<br><br><b>¿Cuándo usarla?</b> Cuando el área de oportunidad (unidad inspeccionada) es constante.<br><br><b>Ejemplo:</b> Defectos de pintura por carrocería; burbujas por lámina de vidrio del mismo tamaño.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">LC  = c̄<br>LCS = c̄ + 3·√c̄<br>LCI = c̄ − 3·√c̄<br>(si LCI < 0, usar 0)</div>', unsafe_allow_html=True)

        st.markdown("### 8) Carta u (defectos por unidad)")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><b>¿Qué controla?</b> La tasa de defectos por unidad cuando el área de inspección varía. Es la versión normalizada de la carta c.<br><br><b>¿Cuándo usarla?</b> Cuando las unidades de inspección tienen tamaño distinto.<br><br><b>Ejemplo:</b> Defectos por metro cuadrado de tela en rollos de longitud variable.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">LC  = ū<br>LCS = ū + 3·√(ū/n)<br>LCI = ū − 3·√(ū/n)<br>(si LCI < 0, usar 0)</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Tabla resumen de los 8 tipos")
        st.dataframe(pd.DataFrame({
            "#":["1","2","3","4","5","6","7","8"],
            "Carta":["X̄ (medias)","R (rangos)","S (desv. est.)","I-MR","p","np","c","u"],
            "Familia":["Variables"]*4+["Atributos"]*4,
            "Estadístico":["Media subgrupo","Rango subgrupo","Desv. est. subgrupo","Valor individual + rango móvil","Proporción defectuosa","N° defectuosas","N° defectos","Defectos por unidad"],
            "Distribución":["Normal"]*4+["Binomial","Binomial","Poisson","Poisson"],
            "Condición clave":["Tendencia central; va con R o S","n=2–9, dispersión","n≥10, dispersión","n=1","n variable o constante","n constante","Área constante","Área variable"],
        }), hide_index=True, use_container_width=True)

    with tab3:
        st.markdown("### Árbol de decisión para elegir la carta correcta")
        st.markdown("""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:24px;">
        <div style="font-size:1rem;font-weight:700;color:#1e3a5f;margin-bottom:16px;">¿El dato se mide o se cuenta?</div>
        <div style="display:flex;gap:24px;">
            <div style="flex:1;background:#eff6ff;border-radius:8px;padding:16px;">
                <div style="font-weight:700;color:#2563eb;margin-bottom:12px;">📏 Se MIDE (continuo) → Variables</div>
                <div style="font-size:0.9rem;color:#374151;line-height:2;">
                <b>n = 1</b> → Carta I-MR<br>
                <b>n = 2 a 9</b> → Carta X̄-R<br>
                <b>n ≥ 10</b> → Carta X̄-S
                </div>
            </div>
            <div style="flex:1;background:#f0fdf4;border-radius:8px;padding:16px;">
                <div style="font-weight:700;color:#16a34a;margin-bottom:12px;">🔢 Se CUENTA (discreto) → Atributos</div>
                <div style="font-size:0.9rem;color:#374151;line-height:2;">
                <b>Unidades defectuosas + n constante</b> → Carta np<br>
                <b>Unidades defectuosas + n variable</b> → Carta p<br>
                <b>Defectos + área constante</b> → Carta c<br>
                <b>Defectos + área variable</b> → Carta u
                </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO — CARTA X̄-R
# ══════════════════════════════════════════════════════════════
def modulo_xbar():
    st.markdown('<div class="section-title">📈 Carta X̄-R — Variables Continuas</div>', unsafe_allow_html=True)
    with st.expander("📐 Fórmulas y constantes"):
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="formula-box">X̄ᵢ = (x₁+...+xₙ)/n<br>Rᵢ = max−min<br>X̿ = ΣX̄ᵢ/k<br>R̄ = ΣRᵢ/k<br>LCS(X̄) = X̿+A₂·R̄<br>LCI(X̄) = X̿−A₂·R̄<br>LCS(R) = D₄·R̄<br>LCI(R) = max(0,D₃·R̄)<br>σ̂ = R̄/d₂</div>', unsafe_allow_html=True)
        with c2:
            df_c = pd.DataFrame(XR_CONST, index=["A₂","D₃","D₄","d₂"]).T
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
        for col,lbl,val,cls in [(c1,"X̿",f"{xdbar:.4f}",""),(c2,"R̄",f"{rbar:.4f}",""),(c3,"LCS(X̄)",f"{ucl_x:.4f}","bad"),(c4,"LCI(X̄)",f"{lcl_x:.4f}","bad"),(c5,"σ̂",f"{sigma_e:.4f}",""),(c6,"Fuera",str(total),"ok" if total==0 else "bad")]:
            with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {cls}">{val}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        if total==0: st.markdown('<div class="alert-ok">✅ <b>PROCESO BAJO CONTROL ESTADÍSTICO</b></div>',unsafe_allow_html=True)
        else: st.markdown(f'<div class="alert-error">🚨 <b>{total} punto(s) FUERA DE CONTROL</b> — X̄: subgrupos {[i+1 for i in fuera_x]} · R: subgrupos {[i+1 for i in fuera_r]}</div>',unsafe_allow_html=True)
        st.image(graficar_xbar_r(xbars,rangos,ucl_x,xdbar,lcl_x,ucl_r,rbar,lcl_r),use_column_width=True)
        df=pd.DataFrame({"Subgrupo":range(1,k_r+1),"X̄":np.round(xbars,4),"R":np.round(rangos,4),"LCS(X̄)":round(ucl_x,4),"LCI(X̄)":round(lcl_x,4),"Estado X̄":["🔴 FUERA" if i in fuera_x else "🟢 OK" for i in range(k_r)],"Estado R":["🔴 FUERA" if i in fuera_r else "🟢 OK" for i in range(k_r)]})
        st.dataframe(df,hide_index=True,use_container_width=True)
        st.session_state["df_xbar"]=df

# ══════════════════════════════════════════════════════════════
#  MÓDULO — CARTA p
# ══════════════════════════════════════════════════════════════
def modulo_carta_p():
    st.markdown('<div class="section-title">📉 Carta p — Proporción Defectiva</div>',unsafe_allow_html=True)
    with st.expander("📐 Fórmulas"):
        st.markdown('<div class="formula-box">pᵢ = dᵢ/nᵢ<br>p̄ = Σdᵢ/Σnᵢ<br>σᵢ = √(p̄·(1−p̄)/nᵢ)<br>LCS = p̄+3·σᵢ<br>LCI = max(0, p̄−3·σᵢ)</div>',unsafe_allow_html=True)
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
        for col,lbl,val,cls in [(c1,"p̄",f"{p_bar*100:.3f}%",""),(c2,"LCS",f"{ucl_i.mean()*100:.3f}%","bad"),(c3,"LCI",f"{lcl_i.mean()*100:.3f}%","bad"),(c4,"Fuera",str(len(fuera)),"ok" if len(fuera)==0 else "bad")]:
            with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {cls}">{val}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        if len(fuera)==0: st.markdown('<div class="alert-ok">✅ Proporción defectiva bajo control estadístico.</div>',unsafe_allow_html=True)
        else: st.markdown(f'<div class="alert-error">🚨 {len(fuera)} período(s) fuera de control — Períodos: {[i+1 for i in fuera]}</div>',unsafe_allow_html=True)
        st.image(graficar_carta_p(p_i,ucl_i,p_bar,lcl_i),use_column_width=True)
        df_p=pd.DataFrame({"Período":range(1,k_r+1),"Defectuosos":defs.astype(int),"n":n_r,"p(%)":np.round(p_i*100,3),"LCS(%)":np.round(ucl_i*100,3),"LCI(%)":np.round(lcl_i*100,3),"Estado":["🔴 FUERA" if i in fuera else "🟢 OK" for i in range(k_r)]})
        st.dataframe(df_p,hide_index=True,use_container_width=True)
        st.session_state["df_p"]=df_p

# ══════════════════════════════════════════════════════════════
#  MÓDULO — REGLAS DE NELSON
# ══════════════════════════════════════════════════════════════
REGLAS=[
    ("1","Punto fuera de ±3σ","Un punto más allá del LCS o LCI.","Evento súbito, error de medición.","🚨 Detener e investigar"),
    ("2","9 puntos mismo lado del LC","9 puntos consecutivos sobre o bajo la línea central.","Corrimiento de la media.","⚠️ Verificar cambios"),
    ("3","6 puntos en tendencia","6 puntos seguidos todos subiendo o bajando.","Desgaste, temperatura, fatiga.","⚠️ Revisar equipos"),
    ("4","14 puntos alternando","14 puntos alternando sistemáticamente arriba/abajo.","Mezcla de dos procesos.","⚠️ Separar fuentes"),
    ("5","2/3 en Zona A (>±2σ)","2 de 3 puntos más allá de ±2σ en el mismo lado.","Señal temprana de descontrol.","⚠️ Investigar"),
    ("6","4/5 en Zona B (>±1σ)","4 de 5 puntos más allá de ±1σ en el mismo lado.","Proceso descentrado.","⚠️ Verificar"),
    ("7","15 puntos en ±1σ","15 puntos consecutivos dentro de ±1σ.","Estratificación de datos.","ℹ️ Revisar medición"),
    ("8","8 fuera de ±1σ ambos lados","8 puntos fuera de ±1σ en ambos lados.","Bimodalidad.","ℹ️ Investigar"),
]

def modulo_nelson():
    st.markdown('<div class="section-title">⚠️ Reglas de Nelson — Patrones de Descontrol</div>',unsafe_allow_html=True)
    st.markdown("Las **Reglas de Nelson (1984)** detectan patrones no aleatorios, incluso cuando ningún punto está fuera de los límites. Activar más reglas aumenta la sensibilidad pero también las falsas alarmas.")
    tab1,tab2=st.tabs(["📋 Las 8 Reglas","🧪 Simulador de señales"])
    with tab1:
        st.dataframe(pd.DataFrame(REGLAS,columns=["#","Nombre","Descripción","Causa típica","Acción"]),hide_index=True,use_container_width=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown('<div class="alert-error">🚨 <b>Acción inmediata</b><br>Regla 1</div>',unsafe_allow_html=True)
        with c2: st.markdown('<div class="alert-warn">⚠️ <b>Investigar proceso</b><br>Reglas 2, 3, 4, 5, 6</div>',unsafe_allow_html=True)
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
            with c2: st.markdown(f'<div class="teoria-card"><h4>Regla {r_info[0]}: {r_info[1]}</h4><b>Descripción:</b><br>{r_info[2]}<br><br><b>Causa:</b><br>{r_info[3]}<br><br><b>Acción:</b><br>{r_info[4]}<br><br><div class="alert-warn"><b>Puntos activados:</b><br>{[i+1 for i in flagged]}</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO — CAPACIDAD DEL PROCESO
# ══════════════════════════════════════════════════════════════
def modulo_capacidad():
    st.markdown('<div class="section-title">📐 Capacidad del Proceso — Cp y Cpk</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">📌 <b>Orden correcto:</b> Primero estabilidad (carta de control), después capacidad (Cp/Cpk). Medir la capacidad de un proceso inestable da un número sin significado porque σ no es constante.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📖 Conceptos", "🧮 Calculadora"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><h4>📊 Índice Cp</h4><b>Cp = (LSE − LIE) / 6σ</b><br><br>Compara el ancho de la especificación con el ancho natural del proceso (±3σ).<br><br>Mide la <b>capacidad potencial</b>. Ignora si el proceso está centrado o no.<br><br>Si Cp = 1 → el proceso justo cabe en la especificación.<br>Si Cp > 1 → hay margen de holgura.</div>', unsafe_allow_html=True)
            st.markdown('<div class="teoria-card"><h4>📊 Índice Cpk</h4><b>Cpk = mín[ (LSE−X̄)/3σ , (X̄−LIE)/3σ ]</b><br><br>Penaliza el <b>descentrado</b> del proceso. Si Cpk es menor que Cp, el proceso está corrido respecto al centro de la especificación.<br><br>Referencia común: <b>Cpk ≥ 1.33</b> para considerar el proceso capaz.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="teoria-card"><h4>🔗 Relación entre Cp y Cpk</h4>• Si Cp = Cpk → el proceso está perfectamente centrado.<br>• Si Cpk < Cp → el proceso está descentrado.<br>• Cpk siempre es ≤ Cp.<br><br><b>Estimación de σ desde la carta:</b><br>σ̂ = R̄/d₂ (carta X̄-R)<br>σ̂ = S̄/c₄ (carta X̄-S)</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({
                "Cpk":["< 1.00","1.00 – 1.33","1.33 – 1.67","≥ 1.67"],
                "Interpretación":["Proceso no capaz","Marginalmente capaz","Capaz (estándar industrial)","Muy capaz (Six Sigma)"],
            }), hide_index=True, use_container_width=True)

    with tab2:
        st.markdown("### Calculadora de Cp y Cpk")
        c1,c2,c3,c4 = st.columns(4)
        with c1: lse = st.number_input("LSE (Límite Superior Especificación)", value=105.0)
        with c2: lie = st.number_input("LIE (Límite Inferior Especificación)", value=95.0)
        with c3: media = st.number_input("Media del proceso (X̄)", value=100.0)
        with c4: sigma = st.number_input("Desv. estándar (σ)", value=1.5, min_value=0.01)

        if st.button("▶ Calcular índices", type="primary"):
            cp  = (lse - lie) / (6 * sigma)
            cpu = (lse - media) / (3 * sigma)
            cpl = (media - lie) / (3 * sigma)
            cpk = min(cpu, cpl)

            c1,c2,c3,c4 = st.columns(4)
            for col,lbl,val in [(c1,"Cp",f"{cp:.3f}"),(c2,"Cpk",f"{cpk:.3f}"),(c3,"CPU",f"{cpu:.3f}"),(c4,"CPL",f"{cpl:.3f}")]:
                with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {"ok" if float(val)>=1.33 else "bad"}">{val}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if cpk >= 1.67:
                st.markdown('<div class="alert-ok">🏆 <b>Proceso muy capaz</b> — Cpk ≥ 1.67. Nivel Six Sigma.</div>', unsafe_allow_html=True)
            elif cpk >= 1.33:
                st.markdown('<div class="alert-ok">✅ <b>Proceso capaz</b> — Cpk ≥ 1.33. Cumple el estándar industrial.</div>', unsafe_allow_html=True)
            elif cpk >= 1.00:
                st.markdown('<div class="alert-warn">⚠️ <b>Marginalmente capaz</b> — Cpk entre 1.00 y 1.33. Requiere monitoreo estrecho.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-error">🚨 <b>Proceso NO capaz</b> — Cpk < 1.00. Se producen unidades fuera de especificación.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO — CARTAS AVANZADAS
# ══════════════════════════════════════════════════════════════
def modulo_avanzadas():
    st.markdown('<div class="section-title">🚀 Cartas Avanzadas — CUSUM y EWMA</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">📌 Las cartas Shewhart reaccionan rápido a cambios grandes (≥2σ), pero son lentas para cambios pequeños y sostenidos (0.5σ–1σ) porque evalúan cada punto de forma aislada, sin memoria. CUSUM y EWMA llenan ese hueco.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 CUSUM", "📈 EWMA"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><h4>CUSUM — Suma Acumulada</h4>Acumula las desviaciones respecto a un valor objetivo en dos sumas (una superior C⁺ y una inferior C⁻).<br><br>Detecta corrimientos pequeños y persistentes mucho antes que una carta Shewhart.<br><br><b>Señal:</b> cuando una suma supera el intervalo de decisión <i>h</i>.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">C⁺(i) = max[0, xᵢ − (μ₀+k) + C⁺(i-1)]<br>C⁻(i) = max[0, (μ₀-k) − xᵢ + C⁻(i-1)]<br><br>k = valor de referencia ≈ Δ/2<br>   (mitad del cambio a detectar)<br><br>h = intervalo de decisión<br>   (usualmente 4 o 5)<br><br>Señal: C⁺(i) > h  o  C⁻(i) > h</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-warn">⚙️ <b>Ejemplo de uso:</b> Proceso químico donde un corrimiento de 0.5σ en el pH de un reactor debe detectarse antes de que afecte la calidad del lote. Una carta Shewhart tardaría muchos puntos; CUSUM lo detecta en pocos.</div>', unsafe_allow_html=True)

    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="teoria-card"><h4>EWMA — Media Móvil Exponencialmente Ponderada</h4>Promedia los datos dando más peso a las observaciones recientes y menos a las antiguas.<br><br><b>Ventaja adicional:</b> más robusta frente a datos que no son perfectamente normales.<br><br>λ típicamente entre 0.05 y 0.25. Cuanto menor λ, más sensible a cambios pequeños.</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="formula-box">zₜ = λ·xₜ + (1−λ)·zₜ₋₁<br><br>Límites:<br>LCS = μ₀ + L·σ·√(λ/(2-λ))<br>LCI = μ₀ − L·σ·√(λ/(2-λ))<br><br>λ = parámetro de suavización (0.05–0.25)<br>L = multiplicador (usualmente 3)<br>z₀ = μ₀ (valor inicial)</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Comparación CUSUM vs EWMA vs Shewhart")
        st.dataframe(pd.DataFrame({
            "Característica":["Mejor para cambios","Memoria del proceso","Complejidad","Robustez a no-normalidad","Uso típico"],
            "Shewhart":["Grandes (≥2σ)","Ninguna (cada punto independiente)","Baja","Moderada","Monitoreo general en planta"],
            "CUSUM":["Pequeños y sostenidos (0.5–1σ)","Alta (acumula desviaciones)","Media","Moderada","Procesos químicos, farmacéuticos"],
            "EWMA":["Pequeños y sostenidos","Alta (promedio ponderado)","Media","Alta","Procesos con datos no normales"],
        }), hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO — QUIZ (PANTALLA COMPLETA)
# ══════════════════════════════════════════════════════════════
def nota_desde_correctas(n):
    tabla = {0:0.0,1:0.5,2:1.0,3:1.5,4:2.0,5:2.5,6:3.0,7:3.5,8:4.0,9:4.5,10:5.0}
    return tabla.get(n, 0.0)

def modulo_quiz():
    # Modo pantalla completa: ocultar sidebar y header
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important;}
    header{display:none!important;}
    .stApp > div:first-child{padding-top:0!important;}
    </style>
    """, unsafe_allow_html=True)

    if "qest" not in st.session_state:
        st.session_state.qest = "registro"
        st.session_state.qidx = 0
        st.session_state.qscore = 0
        st.session_state.qpregs = []
        st.session_state.qresp = {}
        st.session_state.qnombre = ""
        st.session_state.qcodigo = ""

    # ── REGISTRO ──
    if st.session_state.qest == "registro":
        st.markdown("<br>", unsafe_allow_html=True)
        _,col,_ = st.columns([1,2,1])
        with col:
            try: st.image("utp_logo.png", width=120)
            except: pass
            st.markdown("""
            <div style="background:white;border:2px solid #2563eb;border-radius:12px;padding:32px;text-align:center;margin-top:16px;">
                <div style="font-size:1.5rem;font-weight:700;color:#1e3a5f;margin-bottom:4px;">🎯 Quiz de Evaluación</div>
                <div style="font-size:0.9rem;color:#64748b;margin-bottom:24px;">Control Estadístico de Procesos — UTP</div>
                <div style="text-align:left;margin-bottom:16px;background:#f8fafc;border-radius:8px;padding:16px;font-size:0.85rem;color:#374151;">
                <b>📋 Instrucciones:</b><br>
                • 10 preguntas de selección múltiple<br>
                • Cada pregunta vale <b>0.5 puntos</b><br>
                • Nota máxima: <b>5.0</b><br>
                • Una vez iniciado no puedes volver al contenido<br>
                • Responde con honestidad
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            nombre = st.text_input("👤 Nombre completo", placeholder="Ej: Juan David Cardona")
            codigo = st.text_input("🔢 Código estudiantil", placeholder="Ej: 1234567")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("▶ Iniciar Quiz", type="primary", use_container_width=True):
                if nombre.strip() and codigo.strip():
                    st.session_state.qnombre = nombre.strip()
                    st.session_state.qcodigo = codigo.strip()
                    st.session_state.qpregs = random.sample(BANCO_PREGUNTAS, 10)
                    st.session_state.qest = "curso"
                    st.session_state.qidx = 0
                    st.session_state.qscore = 0
                    st.session_state.qresp = {}
                    st.rerun()
                else:
                    st.warning("Por favor ingresa tu nombre y código antes de comenzar.")
            if st.button("← Volver a la aplicación", use_container_width=True):
                st.session_state["_modo_quiz"] = False
                st.session_state.qest = "registro"
                st.rerun()

    # ── EN CURSO ──
    elif st.session_state.qest == "curso":
        idx = st.session_state.qidx
        pregs = st.session_state.qpregs
        total = len(pregs)

        st.markdown("<br>", unsafe_allow_html=True)
        _,col,_ = st.columns([0.5,3,0.5])
        with col:
            st.markdown(f"""
            <div style="background:#1e3a5f;border-radius:10px;padding:12px 20px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
                <div style="color:white;font-weight:700;">🎯 Quiz — {st.session_state.qnombre}</div>
                <div style="color:#bfdbfe;font-size:0.85rem;">Pregunta {idx+1} de {total} &nbsp;|&nbsp; Correctas: {st.session_state.qscore}</div>
            </div>
            """, unsafe_allow_html=True)

            st.progress((idx)/total)
            q = pregs[idx]

            st.markdown(f"""
            <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:24px;margin:12px 0;">
                <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Pregunta {idx+1} de {total}</div>
                <div style="font-size:1.05rem;font-weight:600;color:#1e3a5f;margin-top:8px;">{q["p"]}</div>
            </div>
            """, unsafe_allow_html=True)

            if idx not in st.session_state.qresp:
                resp = st.radio("Selecciona tu respuesta:", q["ops"], key=f"q_{idx}", index=None)
                if resp:
                    letra = resp[0]
                    ok = letra == q["r"]
                    st.session_state.qresp[idx] = {"resp": letra, "ok": ok}
                    if ok: st.session_state.qscore += 1
                    st.rerun()
            else:
                info = st.session_state.qresp[idx]
                rd = next(o for o in q["ops"] if o.startswith(info["resp"]))
                st.radio("Selecciona tu respuesta:", q["ops"], key=f"q_{idx}_s",
                         index=q["ops"].index(rd), disabled=True)
                if info["ok"]:
                    st.markdown(f'<div class="quiz-ok">✅ <b>¡Correcto!</b> — {q["exp"]}</div>', unsafe_allow_html=True)
                else:
                    rc = next(o for o in q["ops"] if o.startswith(q["r"]))
                    st.markdown(f'<div class="quiz-bad">❌ <b>Incorrecto.</b> Respuesta correcta: <b>{rc}</b><br>{q["exp"]}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                lbl = "Ver resultado final →" if idx == total-1 else "Siguiente pregunta →"
                if st.button(lbl, type="primary", use_container_width=True):
                    if idx < total-1:
                        st.session_state.qidx += 1
                    else:
                        # Guardar resultado en lista acumulada
                        nota = nota_desde_correctas(st.session_state.qscore)
                        resultado = {
                            "nombre": st.session_state.qnombre,
                            "codigo": st.session_state.qcodigo,
                            "correctas": st.session_state.qscore,
                            "nota": nota,
                            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                        if "resultados_quiz" not in st.session_state:
                            st.session_state.resultados_quiz = []
                        st.session_state.resultados_quiz.append(resultado)
                        # Guardar en Google Sheets
                        ok = guardar_en_sheets(
                            resultado["nombre"], resultado["codigo"],
                            resultado["correctas"], resultado["nota"], resultado["fecha"]
                        )
                        st.session_state["sheets_ok"] = ok
                        st.session_state.qest = "fin"
                    st.rerun()

    # ── FINALIZADO ──
    elif st.session_state.qest == "fin":
        sc = st.session_state.qscore
        nota = nota_desde_correctas(sc)
        if nota >= 4.5:   niv, col = "🏆 EXCELENTE", "#16a34a"
        elif nota >= 3.5: niv, col = "👍 BIEN", "#2563eb"
        elif nota >= 3.0: niv, col = "📚 APROBADO", "#d97706"
        else:             niv, col = "🔄 NO APROBADO", "#dc2626"

        st.markdown("<br>", unsafe_allow_html=True)
        _,c,_ = st.columns([1,2,1])
        with c:
            st.markdown(f"""
            <div style="background:white;border:2px solid {col};border-radius:12px;padding:40px;text-align:center;">
                <div style="font-size:3rem;margin-bottom:8px;">{niv.split()[0]}</div>
                <div style="font-size:1.1rem;color:#64748b;margin-bottom:4px;">{st.session_state.qnombre}</div>
                <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:20px;">Código: {st.session_state.qcodigo}</div>
                <div style="font-size:2.5rem;font-weight:700;color:{col};">{nota:.1f} / 5.0</div>
                <div style="font-size:1rem;color:#64748b;margin:8px 0;">{sc} de 10 respuestas correctas</div>
                <div style="height:8px;background:#e2e8f0;border-radius:4px;margin:16px 0;">
                    <div style="height:100%;width:{nota/5*100:.0f}%;background:{col};border-radius:4px;"></div>
                </div>
                <div style="font-size:1.1rem;font-weight:600;color:{col};">{" ".join(niv.split()[1:])}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.get("sheets_ok"):
                st.markdown('<div class="alert-ok" style="text-align:center;">✅ Resultado guardado en Google Sheets</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-warn" style="text-align:center;">⚠️ Resultado guardado solo en esta sesión</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Volver a la aplicación", use_container_width=True, type="primary"):
                # Desactivar modo quiz y limpiar estado para próximo estudiante
                st.session_state["_modo_quiz"] = False
                st.session_state.qest = "registro"
                st.session_state.qnombre = ""
                st.session_state.qcodigo = ""
                st.session_state.qidx = 0
                st.session_state.qscore = 0
                st.session_state.qresp = {}
                st.session_state.qpregs = []
                st.rerun()
            if st.button("🔄 Nuevo estudiante (otro quiz)", use_container_width=True):
                # Mantener modo quiz activo pero limpiar datos del estudiante anterior
                st.session_state.qest = "registro"
                st.session_state.qnombre = ""
                st.session_state.qcodigo = ""
                st.session_state.qidx = 0
                st.session_state.qscore = 0
                st.session_state.qresp = {}
                st.session_state.qpregs = []
                st.rerun()

# ══════════════════════════════════════════════════════════════
#  MÓDULO — PANEL DEL PROFESOR
# ══════════════════════════════════════════════════════════════
def modulo_profesor():
    st.markdown('<div class="section-title">👨‍🏫 Panel del Profesor — Resultados del Quiz</div>', unsafe_allow_html=True)

    resultados = st.session_state.get("resultados_quiz", [])

    if not resultados:
        st.markdown('<div class="alert-warn">⚠️ Aún no hay resultados registrados. Los estudiantes deben completar el quiz primero.</div>', unsafe_allow_html=True)
        return

    st.markdown(f'<div class="alert-ok">✅ <b>{len(resultados)} estudiante(s)</b> han completado el quiz en esta sesión.</div>', unsafe_allow_html=True)
    st.markdown("---")

    df_res = pd.DataFrame(resultados)
    df_res.columns = ["Nombre","Código","Correctas","Nota","Fecha"]

    # Estadísticas rápidas
    c1,c2,c3,c4 = st.columns(4)
    for col,lbl,val,cls in [
        (c1,"Estudiantes",str(len(df_res)),""),
        (c2,"Nota promedio",f"{df_res['Nota'].mean():.2f}",""),
        (c3,"Nota más alta",f"{df_res['Nota'].max():.1f}","ok"),
        (c4,"Aprobados",str(len(df_res[df_res['Nota']>=3.0]))+" / "+str(len(df_res)),"ok"),
    ]:
        with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {cls}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Tabla de resultados")

    # Colorear según nota
    def color_nota(val):
        if val >= 4.0: return 'color: #16a34a; font-weight: bold'
        elif val >= 3.0: return 'color: #d97706; font-weight: bold'
        else: return 'color: #dc2626; font-weight: bold'

    try:
        styled = df_res.style.map(color_nota, subset=['Nota'])
    except AttributeError:
        styled = df_res.style.applymap(color_nota, subset=['Nota'])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### ⬇️ Descargar resultados")
    csv = df_res.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="⬇️ Descargar resultados completos (.csv)",
        data=csv,
        file_name=f"resultados_quiz_SPC_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        type="primary",
    )
    st.markdown('<div class="alert-info">💡 El archivo CSV se puede abrir directamente en Excel. Compatible con Google Sheets.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO — EXPORTAR
# ══════════════════════════════════════════════════════════════
def modulo_exportar():
    st.markdown('<div class="section-title">📄 Exportar Reportes de Análisis</div>', unsafe_allow_html=True)
    tx = "df_xbar" in st.session_state
    tp = "df_p"    in st.session_state
    if not tx and not tp:
        st.markdown('<div class="alert-warn">⚠️ No hay datos para exportar. Genera primero una Carta X̄-R o una Carta p.</div>', unsafe_allow_html=True)
        return
    if tx:
        st.markdown("### 📈 Reporte Carta X̄-R")
        st.dataframe(st.session_state["df_xbar"], hide_index=True, use_container_width=True)
        csv = st.session_state["df_xbar"].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("⬇️ Descargar Carta X̄-R (.csv)", csv, "reporte_xbar_r.csv", "text/csv", type="primary")
    if tp:
        st.markdown("### 📉 Reporte Carta p")
        st.dataframe(st.session_state["df_p"], hide_index=True, use_container_width=True)
        csv = st.session_state["df_p"].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("⬇️ Descargar Carta p (.csv)", csv, "reporte_carta_p.csv", "text/csv", type="primary")
    st.markdown('<div class="alert-info">💡 <b>Abrir en Excel:</b> Datos → Desde texto/CSV → UTF-8 → Delimitador: coma → Cargar.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO — REFERENCIAS APA
# ══════════════════════════════════════════════════════════════
def modulo_referencias():
    st.markdown('<div class="section-title">📚 Referencias Bibliográficas</div>', unsafe_allow_html=True)
    st.markdown("Todas las referencias están en formato **APA 7.ª edición**.")
    st.markdown("---")

    st.markdown("### 📖 Libros y manuales")
    refs_libros = [
        "Montgomery, D. C. (2020). <i>Introduction to statistical quality control</i> (8.ª ed.). John Wiley & Sons.",
        "Shewhart, W. A. (1931). <i>Economic control of quality of manufactured product</i>. D. Van Nostrand Company.",
        "Wheeler, D. J., & Chambers, D. S. (1992). <i>Understanding statistical process control</i> (2.ª ed.). SPC Press.",
        "Ryan, T. P. (2011). <i>Statistical methods for quality improvement</i> (3.ª ed.). John Wiley & Sons.",
        "Deming, W. E. (1986). <i>Out of the crisis</i>. MIT Center for Advanced Engineering Study.",
        "Juran, J. M., & Godfrey, A. B. (1999). <i>Juran's quality handbook</i> (5.ª ed.). McGraw-Hill.",
    ]
    for r in refs_libros:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

    st.markdown("### 📄 Artículos y publicaciones")
    refs_articulos = [
        "Nelson, L. S. (1984). The Shewhart control chart — tests for special causes. <i>Journal of Quality Technology, 16</i>(4), 237–239. https://doi.org/10.1080/00224065.1984.11978921",
        "Nelson, L. S. (1985). Interpreting Shewhart X̄ control charts. <i>Journal of Quality Technology, 17</i>(2), 114–116. https://doi.org/10.1080/00224065.1985.11978946",
        "Page, E. S. (1954). Continuous inspection schemes. <i>Biometrika, 41</i>(1/2), 100–115. https://doi.org/10.2307/2333009",
        "Roberts, S. W. (1959). Control chart tests based on geometric moving averages. <i>Technometrics, 1</i>(3), 239–250. https://doi.org/10.1080/00401706.1959.10489860",
    ]
    for r in refs_articulos:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

    st.markdown("### 🏛️ Normas y estándares")
    refs_normas = [
        "International Organization for Standardization. (2013). <i>ISO 7870-2: Control charts — Part 2: Shewhart control charts</i>. ISO.",
        "International Organization for Standardization. (2014). <i>ISO 7870-1: Control charts — Part 1: General guidelines</i>. ISO.",
        "Automotive Industry Action Group. (2005). <i>Statistical process control (SPC) reference manual</i> (2.ª ed.). AIAG.",
        "American Society for Quality. (2023). <i>ASQ glossary of quality terms</i>. https://asq.org/quality-resources/quality-glossary",
    ]
    for r in refs_normas:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

    st.markdown("### 🌐 Recursos digitales")
    refs_web = [
        "American Society for Quality. (2023). <i>Control chart</i>. https://asq.org/quality-resources/control-chart",
        "National Institute of Standards and Technology. (2023). <i>NIST/SEMATECH e-handbook of statistical methods</i>. https://www.itl.nist.gov/div898/handbook/",
        "Universidad Tecnológica de Pereira. (2024). <i>Cartas de Control de Calidad: herramienta didáctica interactiva</i> [Software]. Desarrollado con Python y Streamlit.",
    ]
    for r in refs_web:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════════════
def main():
    # La única condición para mostrar el quiz en pantalla completa
    # es que el flag "_modo_quiz" esté activo Y el quiz no haya terminado
    en_quiz = (
        st.session_state.get("_modo_quiz", False) and
        st.session_state.get("qest") in ["registro", "curso"]
    )

    if en_quiz:
        modulo_quiz()
        return

    # Si el quiz terminó, desactivar el modo quiz automáticamente
    if st.session_state.get("qest") == "fin":
        st.session_state["_modo_quiz"] = False
        st.session_state["qest"] = "registro"

    mostrar_header()
    mod = sidebar_nav()

    if   "Teoría"       in mod: modulo_teoria()
    elif "X̄-R"          in mod: modulo_xbar()
    elif "Carta p"      in mod: modulo_carta_p()
    elif "Tipos"        in mod: modulo_tipos_cartas()
    elif "Nelson"       in mod: modulo_nelson()
    elif "Capacidad"    in mod: modulo_capacidad()
    elif "Avanzadas"    in mod: modulo_avanzadas()
    elif "Quiz"         in mod:
        st.session_state["_modo_quiz"] = True
        modulo_quiz()
    elif "Profesor"     in mod: modulo_profesor()
    elif "Exportar"     in mod: modulo_exportar()
    elif "Referencias"  in mod: modulo_referencias()

if __name__ == "__main__":
    main()
