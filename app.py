import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
from pathlib import Path
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Estimador de Percentiles",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Estilos CSS
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .percentil-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px 2px;
        }
        .p50-line {
            border: 2px dashed #FF6B6B;
            position: relative;
        }
    </style>
""", unsafe_allow_html=True)

# ========== CONFIGURACIÓN Y FUNCIONES ==========

# Obtener la ruta del directorio del script actual
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_FILE = SCRIPT_DIR / "config_proyectos.json"
DATA_FILE = SCRIPT_DIR / "respuestas_percentiles.csv"
ADMIN_PASSWORD = "Hola1234"

def load_config():
    """Carga la configuración de proyectos"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"proyectos": []}

def save_config(config):
    """Guarda la configuración de proyectos"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_proyectos_activos(config):
    """Retorna solo los proyectos activos ordenados"""
    return sorted(
        [p for p in config["proyectos"] if p["activo"]], 
        key=lambda x: x["orden"]
    )

def load_responses(proyecto_id=None, drop_personal=True):
    """Carga las respuestas del CSV, opcionalmente filtradas por proyecto.
    """
    if DATA_FILE.exists():
        try:
            # Intenta con utf-8-sig primero (mejor para CSV con BOM)
            df = pd.read_csv(str(DATA_FILE), encoding='utf-8-sig', engine='python', on_bad_lines='skip')
        except Exception as e1:
            try:
                # Si falla, intenta con latin-1
                df = pd.read_csv(str(DATA_FILE), encoding='latin-1', engine='python', on_bad_lines='skip')
            except Exception as e2:
                try:
                    # Si falla, intenta con utf-8 sin BOM
                    df = pd.read_csv(str(DATA_FILE), encoding='utf-8', engine='python', on_bad_lines='skip')
                except Exception as e3:
                    # Última opción: iso-8859-1
                    df = pd.read_csv(str(DATA_FILE), encoding='iso-8859-1', engine='python', on_bad_lines='skip')
        if proyecto_id:
            df = df[df['Proyecto'] == proyecto_id]
        return df
    return pd.DataFrame()


def save_response(proyecto_id, name, p1,p10,p90, p99, p50_percentil, comentarios=""):
    """Guarda una respuesta en el CSV (sin datos personales).

    Guardamos: `Timestamp`, `Proyecto`, `P1`, p10, p90,`P99`, `P50_percentil` (el percentil
    que el usuario asigna al Valor Esperado) y `Comentarios`. `P50_percentil` es
    obligatorio y no se sobrescribe el `proyecto['p50']`.
    """
    new_data = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Proyecto': proyecto_id,
        'P1': p1,
        'P10': p10,
        'P90': p90,
        'P99': p99,
        'P50_percentil': p50_percentil,
        'Comentarios': comentarios,
        'Nombre': name  
    }

    try:
        df = load_responses(proyecto_id=None, drop_personal=False)
        # append keeping columns consistent
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(str(DATA_FILE), index=False, encoding='utf-8-sig')
        return True
    except Exception:
        return False

def calcular_percentiles_datos(valores):
    """Calcula percentiles de los datos recopilados"""
    if len(valores) == 0:
        return {}
    
    return {
        'p1': np.percentile(valores, 1),
        'p10': np.percentile(valores, 10),
        'p50': np.percentile(valores, 50),
        'p90': np.percentile(valores, 90),
        'p99': np.percentile(valores, 99),
        'media': np.mean(valores),
        'mediana': np.median(valores)
    }


def _clamp_one_decimal(v, lo, hi):
    """Clamp a number to [lo, hi] and round to one decimal place."""
    try:
        vf = float(v)
    except Exception:
        vf = float(lo)
    lo_f = float(lo)
    hi_f = float(hi)
    vf = max(lo_f, min(hi_f, vf))
    return round(vf, 1)

# Inicializar sesión
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = False

# ========== LAYOUT PRINCIPAL ==========

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<h1 class='main-title'>📊 Taller de Rango API N20MS10 - Estimador de Percentiles</h1>", unsafe_allow_html=True)

with col2:
    # Botón para panel de control
    if st.button("⚙️ Panel Control", key="admin_btn"):
        st.session_state.show_admin = not st.session_state.show_admin
    # Botón de descarga rápido para administradores (base completa)
    if st.session_state.admin_authenticated:
        try:
            full_df_header = load_responses(proyecto_id=None, drop_personal=False)
            csv_header = full_df_header.to_csv(index=False)
            st.download_button(
                label="📥 Descargar base completa (admin)",
                data=csv_header,
                file_name="estimaciones_completa.csv",
                mime="text/csv",
                key="download_header_admin"
            )
        except Exception:
            st.warning("⚠️ Error al preparar la descarga completa")

# ========== MODAL DE AUTENTICACIÓN ==========
if st.session_state.show_admin and not st.session_state.admin_authenticated:
    with st.container():
        st.divider()
        col_centro = st.columns([1, 2, 1])
        
        with col_centro[1]:
            st.markdown("### 🔐 Acceso al Panel de Control")
            st.write("Ingresa la contraseña para continuar:")
            
            password_input = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingresa tu contraseña",
                key="password_input"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("✅ Verificar", use_container_width=True):
                    if password_input == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.success("✅ Contraseña correcta. Acceso concedido.")
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta. Intenta nuevamente.")
                        st.session_state.show_admin = False
            
            with col_btn2:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_admin = False
                    st.session_state.admin_authenticated = False
                    st.rerun()
    
    st.stop()

# Cargar configuración
config = load_config()
proyectos_activos = get_proyectos_activos(config)

if not proyectos_activos:
    st.warning("⚠️ No hay proyectos activos en este momento. Por favor intenta más tarde.")
    st.stop()

# ========== TABS PRINCIPALES ==========

tabs = st.tabs([f"✍️ {p['nombre']} ({p['subtipo']})" for p in proyectos_activos] + ["📊 Análisis Completo"])

# Tabs de formularios por proyecto
for idx, proyecto in enumerate(proyectos_activos):
    with tabs[idx]:
        # Título dinámico según tipo
        titulo_tipo = "Estimación de Costos" if proyecto['tipo'] == 'costos' else "Estimación de Plazos"
        unidad = proyecto['unidad']
        # Límites por proyecto (esperados en config JSON como 'limite_inferior' y 'limite_superior')
        min_limit = proyecto.get('limite_inferior', 0.0)
        max_limit = proyecto.get('limite_superior', float(proyecto['p50'] * 5))
        try:
            min_limit = float(min_limit)
        except Exception:
            min_limit = 0.0
        try:
            max_limit = float(max_limit)
        except Exception:
            max_limit = float(proyecto['p50'] * 5)
        
        st.write(f"### {proyecto['nombre']} - {proyecto['subtipo']}")
        st.write(f"_{titulo_tipo} - {proyecto['nombre']}_")
        st.info(f"📌 **VALOR ESPERADO: {proyecto['p50']} {unidad}**")
        
        with st.form(f"form_{proyecto['id']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Se elimina la recolección de nombre y email por privacidad
                pass
            
            with col2:
                pass  # Espacio para balance

            
            st.divider()
            st.write(f"### {titulo_tipo} ({unidad})")

            #Identificador de usuario (puede dejar su nombre o pseudonimo, obligatorio)
            st.write("Proporciona un nombre o Pseudonimo")
            name = st.text_input("Nombre o Pseudonimo", placeholder="Ingresa tu nombre o pseudonimo")

            st.divider()

            st.write("Proporciona tu estimación para cada percentil:")
            
            # Crear dos columnas para los inputs
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Percentiles Bajos (Mejor Caso)")
                
                p1 = st.number_input(
                    f"P1 (Percentil 1) - Mejor caso",
                    min_value=min_limit,
                    max_value=float(proyecto['p50']),
                    value=_clamp_one_decimal(proyecto['p50'] * 0.3, min_limit, proyecto['p50']),
                    step=0.1,
                    format="%.1f",
                    key=f"p1_{proyecto['id']}",
                    help=f"Rango: {min_limit} - {proyecto['p50']} {unidad}"
                )
                
                p10 = st.number_input(
                    f"P10 (Percentil 10) - Mejor caso",
                    min_value=min_limit,
                    max_value=float(proyecto['p50']),
                    value=_clamp_one_decimal(proyecto['p50'] * 0.3, min_limit, proyecto['p50']),
                    step=0.1,
                    format="%.1f",
                    key=f"p10_{proyecto['id']}",
                    help=f"Rango: {min_limit} - {proyecto['p50']} {unidad}"
                )                
            with col2:
                st.markdown("#### Percentiles Altos (Peor Caso)")
                
                p90 = st.number_input(
                                    f"P90 (Percentil 90) - Peor caso",
                                    min_value=float(proyecto['p50']),
                                    max_value=max_limit,
                                    value=_clamp_one_decimal(proyecto['p50'] * 2.5, proyecto['p50'], max_limit),
                                    step=0.1,
                                    format="%.1f",
                                    key=f"p90_{proyecto['id']}",
                                    help=f"Rango: {proyecto['p50']} - {max_limit} {unidad}"
                )

                p99 = st.number_input(
                    f"P99 (Percentil 99) - Peor caso",
                    min_value=float(proyecto['p50']),
                    max_value=max_limit,
                    value=_clamp_one_decimal(proyecto['p50'] * 2.5, proyecto['p50'], max_limit),
                    step=0.1,
                    format="%.1f",
                    key=f"p99_{proyecto['id']}",
                    help=f"Rango: {proyecto['p50']} - {max_limit} {unidad}"
                )

            st.divider()

            #Captura de percentil del valor esperado mostrado (P50) según criterio del usuario
            p50_percentil = st.number_input(
                "¿Qué percentil consideras que corresponde al Valor Esperado mostrado?",
                min_value=35.0,
                max_value=65.0,
                value=_clamp_one_decimal(50.0, 35.0, 65.0),
                step=0.1,
                format="%.1f",
                key=f"p50_percentil_{proyecto['id']}",
                help="Selecciona el percentil que, según tu criterio, representa el Valor Esperado mostrado."
            )
            
            st.divider()
            
            comentarios = st.text_area(
                "Comentarios adicionales (opcional)",
                placeholder="Comparte tu análisis, supuestos o consideraciones especiales...",
                key=f"comentarios_{proyecto['id']}"
            )
            
            submitted = st.form_submit_button(
                f"📤 Enviar estimaciones para {proyecto['nombre']} ({proyecto['subtipo']})",
                use_container_width=True
            )

            if submitted:
                # Nombre/pseudónimo obligatorio
                if not name or str(name).strip() == "":
                    st.error("⚠️ Por favor completa Nombre o Pseudónimo (obligatorio)")
                else:
                    # Validar y convertir a float de forma segura
                    try:
                        p1f = float(p1)
                        p10f = float(p10)
                        p90f = float(p90)
                        p99f = float(p99)
                        p50_percentil_f = float(p50_percentil)
                    except Exception:
                        st.error("⚠️ Valores inválidos: asegúrate de ingresar números válidos con máximo 1 decimal")
                    else:
                        # El Valor Esperado (P50) se toma del proyecto y no se modifica aquí
                        p50_project_val = float(proyecto['p50'])

                        # Límites del proyecto
                        lower_limit = float(min_limit)
                        upper_limit = float(max_limit)

                        # Validaciones solicitadas:
                        # P1 no mayor que P10 ni que P50
                        if p1f > p10f or p1f > p50_project_val:
                            st.error("⚠️ P1 no puede ser mayor que P10 ni que P50")
                        # P10 no menor que P1 ni que límite inferior y no mayor que P50
                        elif p10f < p1f or p10f < lower_limit or p10f > p50_project_val:
                            st.error(f"⚠️ P10 debe ser ≥ P1, ≥ {lower_limit} y ≤ P50 ({p50_project_val})")
                        # P90 y P99 no menores que P50 y no mayores que límite superior
                        elif p90f < p50_project_val or p90f < p50_project_val or p90f > upper_limit:
                            st.error(f"⚠️ P90 debe ser ≥ P50 ({p50_project_val}) y ≤ límite superior ({upper_limit})")
                        elif p99f < p50_project_val or p99f > upper_limit:
                            st.error(f"⚠️ P99 debe ser ≥ P50 ({p50_project_val}) y ≤ límite superior ({upper_limit})")
                        # P90 no mayor que P99
                        elif p90f > p99f:
                            st.error("⚠️ P90 no puede ser mayor que P99")
                        else:
                            # Guardar P1, P10, P90, P99 y el percentil que el usuario asignó al Valor Esperado
                            saved = save_response(
                                proyecto['id'],
                                str(name).strip(),
                                round(p1f, 1),
                                round(p10f, 1),
                                round(p90f, 1),
                                round(p99f, 1),
                                round(p50_percentil_f, 1),
                                comentarios
                            )
                            if saved:
                                st.success(f"✅ ¡Gracias por tus estimaciones para {proyecto['nombre']}!")
                                st.balloons()
                            else:
                                st.error("❌ Ocurrió un error al guardar. Intenta nuevamente más tarde.")

# Tab de análisis completo
with tabs[-1]:
    st.write("## 📊 Análisis Completo de Percentiles")
    
    # Mostrar todos los proyectos (activos e inactivos) para análisis
    todos_proyectos = sorted(config['proyectos'], key=lambda x: x["orden"])
    
    if not todos_proyectos:
        st.warning("⚠️ No hay proyectos configurados.")
    else:
        # Selector de proyecto para análisis
        opciones_analisis = [f"{p['nombre']} ({p['subtipo']})" + (" [INACTIVO]" if not p['activo'] else "") for p in todos_proyectos]
        proyecto_seleccionado_idx = st.selectbox(
            "Selecciona un proyecto para análisis detallado",
            range(len(opciones_analisis)),
            format_func=lambda i: opciones_analisis[i],
            key="proyecto_analisis"
        )
        
        proyecto_seleccionado = todos_proyectos[proyecto_seleccionado_idx]
        proyecto_id = proyecto_seleccionado['id']
        p50_valor = proyecto_seleccionado['p50']
        unidad = proyecto_seleccionado['unidad']
        tipo = proyecto_seleccionado['tipo']
        titulo_tipo = "Costos" if tipo == 'costos' else "Plazos"
        
        # Mostrar indicador si el proyecto está inactivo
        if not proyecto_seleccionado['activo']:
            st.info(f"ℹ️ Este proyecto está **deshabilitado** pero puedes ver su análisis de datos.")
        
        df_proyecto = load_responses(proyecto_id)
        
        if len(df_proyecto) == 0:
            st.warning(f"📭 Aún no hay respuestas para {proyecto_seleccionado['nombre']}.")
        else:
            st.divider()
            
            # ========== MÉTRICAS PRINCIPALES ==========
            st.write("### 📈 Métricas de Estimaciones")
            
            # Mostrar métricas principales y el mapeo medio de percentil (si existe)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total participantes", len(df_proyecto))
            with col2:
                st.metric(f"P50 objetivo", f"{p50_valor} {unidad}")

            # Promedio del percentil que los usuarios asignaron al Valor Esperado
            avg_percentil = None
            if 'P50_percentil' in df_proyecto.columns:
                try:
                    avg_percentil = df_proyecto['P50_percentil'].astype(float).mean()
                except Exception:
                    avg_percentil = None

            with col3:
                if avg_percentil is not None and not pd.isna(avg_percentil):
                    st.metric("P50 - mapeo medio (percentil)", f"{avg_percentil:.1f}")
                else:
                    st.metric("P50 - mapeo medio (percentil)", "n/a")
            
            st.divider()
            
            # ========== ANÁLISIS POR PERCENTIL ==========
            st.write("### 📊 Distribución de Estimaciones")

            col1, col2 = st.columns(2)

            # Gráfico 1: Histograma de P1 y P10
            with col1:
                st.write("#### Percentiles Bajos (P1 y P10)")

                fig1 = go.Figure()
                fig1.add_trace(go.Histogram(
                    x=df_proyecto['P1'],
                    name='P1',
                    opacity=0.7,
                    marker_color='#3498DB',
                    nbinsx=15
                ))
                if 'P10' in df_proyecto.columns:
                    fig1.add_trace(go.Histogram(
                        x=df_proyecto['P10'],
                        name='P10',
                        opacity=0.7,
                        marker_color='#2ECC71',
                        nbinsx=15
                    ))

                fig1.add_vline(x=p50_valor, line_dash="dash", line_color="red",
                              annotation_text=f"P50: {p50_valor}", annotation_position="top right")

                fig1.update_layout(
                    height=400,
                    barmode='overlay',
                    xaxis_title=f'Estimación ({unidad})',
                    yaxis_title='Cantidad de Participantes'
                )

                st.plotly_chart(fig1, use_container_width=True)

            # Gráfico 2: Histograma de P90 y P99
            with col2:
                st.write("#### Percentiles Altos (P90 y P99)")

                fig2 = go.Figure()
                if 'P90' in df_proyecto.columns:
                    fig2.add_trace(go.Histogram(
                        x=df_proyecto['P90'],
                        name='P90',
                        opacity=0.7,
                        marker_color='#F39C12',
                        nbinsx=15
                    ))

                fig2.add_trace(go.Histogram(
                    x=df_proyecto['P99'],
                    name='P99',
                    opacity=0.7,
                    marker_color='#E74C3C',
                    nbinsx=15
                ))

                fig2.add_vline(x=p50_valor, line_dash="dash", line_color="red",
                              annotation_text=f"P50: {p50_valor}", annotation_position="top right")

                fig2.update_layout(
                    height=400,
                    barmode='overlay',
                    xaxis_title=f'Estimación ({unidad})',
                    yaxis_title='Cantidad de Participantes'
                )

                st.plotly_chart(fig2, use_container_width=True)

        # ===== Estadísticas del mapeo de P50 (percentil) =====
            if 'P50_percentil' in df_proyecto.columns:
                try:
                    pct = pd.to_numeric(df_proyecto['P50_percentil'], errors='coerce').dropna()
                except Exception:
                    pct = pd.Series(dtype=float)

                if len(pct) > 0:
                    st.divider()
                    st.write("### 📌 Estadísticas del mapeo de P50 (percentil)")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("Respuestas", len(pct))
                    with c2:
                        st.metric("Promedio (percentil)", f"{pct.mean():.1f}")
                    with c3:
                        st.metric("Mediana (percentil)", f"{pct.median():.1f}")
                    with c4:
                        st.metric("Desv. est.", f"{pct.std():.1f}")

                    fig_pct = go.Figure()
                    fig_pct.add_trace(go.Histogram(
                        x=pct,
                        nbinsx=15,
                        marker_color='#9b59b6',
                        opacity=0.8
                    ))
                    fig_pct.update_layout(
                        height=300,
                        xaxis_title='Percentil asignado',
                        yaxis_title='Cantidad'
                    )
                    st.plotly_chart(fig_pct, use_container_width=True)
                else:
                    st.info("No hay mapeos de percentil registrados para el P50 en este proyecto.")
            
            st.divider()
            
            # ========== GRÁFICO COMPARATIVO ==========
            st.write(f"### 📉 Comparativa de Percentiles vs P50 ({titulo_tipo})")
            
            # Calcular promedios (P1, P10, P50 fijo del proyecto, P90, P99)
            promedios = {
                'P1': df_proyecto['P1'].mean(),
                'P10': df_proyecto['P10'].mean() if 'P10' in df_proyecto.columns else float('nan'),
                # P50 es el Valor Esperado del proyecto (no es una media de respuestas)
                'P50': float(p50_valor),
                'P90': df_proyecto['P90'].mean() if 'P90' in df_proyecto.columns else float('nan'),
                'P99': df_proyecto['P99'].mean()
            }
            
            fig3 = go.Figure()
            
            fig3.add_trace(go.Bar(
                x=list(promedios.keys()),
                y=list(promedios.values()),
                marker_color=['#3498DB', '#F39C12', '#E74C3C'],
                text=[f'{v:.1f}' if not pd.isna(v) else 'n/a' for v in promedios.values()],
                textposition='auto',
                name='Promedio Estimado'
            ))

            fig3.add_hline(y=p50_valor, line_dash="dash", line_color="red",
                          annotation_text=f"P50 Objetivo: {p50_valor} {unidad}")
            
            fig3.update_layout(
                height=400,
                xaxis_title='Percentil',
                yaxis_title=f'Estimación ({unidad})',
                showlegend=False
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
            st.divider()
            
            # ========== ESTADÍSTICAS DETALLADAS ==========
            st.write("### 📋 Estadísticas por Percentil")

            stats_data = {
                'Percentil': ['P1', 'P10', 'P90', 'P99'],
                'Mín': [
                    df_proyecto['P1'].min(),
                    df_proyecto['P10'].min() if 'P10' in df_proyecto.columns else float('nan'),
                    df_proyecto['P90'].min() if 'P90' in df_proyecto.columns else float('nan'),
                    df_proyecto['P99'].min()
                ],
                'Promedio': [
                    df_proyecto['P1'].mean(),
                    df_proyecto['P10'].mean() if 'P10' in df_proyecto.columns else float('nan'),
                    df_proyecto['P90'].mean() if 'P90' in df_proyecto.columns else float('nan'),
                    df_proyecto['P99'].mean()
                ],
                'Mediana': [
                    df_proyecto['P1'].median(),         
                    df_proyecto['P10'].median() if 'P10' in df_proyecto.columns else float('nan'),
                    df_proyecto['P90'].median() if 'P90' in df_proyecto.columns else float('nan'),
                    df_proyecto['P99'].median()
                ],
                'Máx': [
                    df_proyecto['P1'].max(),
                    df_proyecto['P10'].max() if 'P10' in df_proyecto.columns else float('nan'),
                    df_proyecto['P90'].max() if 'P90' in df_proyecto.columns else float('nan'),
                    df_proyecto['P99'].max()
                ],
                'Desv. Est.': [
                    df_proyecto['P1'].std(),
                    df_proyecto['P10'].std() if 'P10' in df_proyecto.columns else float('nan'),
                    df_proyecto['P90'].std() if 'P90' in df_proyecto.columns else float('nan'),
                    df_proyecto['P99'].std()
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # ========== TABLA DE DATOS COMPLETOS ==========
            
            # Tabla de datos completos: solo visible para admin
            if st.session_state.admin_authenticated:
                st.write("### 📊 Datos Detallados")
                st.dataframe(
                    df_proyecto,
                    use_container_width=True,
                    hide_index=True
                )

            # Botón de descarga: solo para admin, descarga la base completa (todos los proyectos)
            if st.session_state.admin_authenticated:
                full_df = load_responses(proyecto_id=None, drop_personal=False)
                csv_all = full_df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Descargar base completa (CSV)",
                    data=csv_all,
                    file_name=f"estimaciones_completa.csv",
                    mime="text/csv"
                )
# ========== PANEL DE CONTROL (Admin) ==========
if st.session_state.show_admin and st.session_state.admin_authenticated:
    st.divider()
    st.markdown("---")
    st.write("## ⚙️ Panel de Control de Proyectos")
    st.success("✅ Acceso de administrador activo")
    
    with st.expander("📋 Gestionar Proyectos", expanded=True):
        config = load_config()
        
        st.write("### Activar/Desactivar Proyectos")
        
        cols = st.columns(len(config['proyectos']))
        
        for idx, proyecto in enumerate(config['proyectos']):
            with cols[idx]:
                nuevo_estado = st.checkbox(
                    f"{proyecto['nombre']}\n({proyecto['subtipo']})",
                    value=proyecto['activo'],
                    key=f"toggle_{proyecto['id']}"
                )
                
                if nuevo_estado != proyecto['activo']:
                    config['proyectos'][idx]['activo'] = nuevo_estado
                    save_config(config)
                    st.success(f"✅ {proyecto['nombre']} actualizado")
                    st.rerun()
        
        st.divider()
    st.divider()
    with st.expander("🧹 Borrar datos de respuestas", expanded=False):
        st.write("Eliminará todas las respuestas y reiniciará el dataset (irreversible).")
        if st.button("🗑️ Iniciar borrado de datos", key="init_delete_root", use_container_width=True):
            st.session_state.confirm_delete = True

        if st.session_state.confirm_delete:
            st.warning("⚠️ Estás a punto de borrar todos los datos. Esta acción no se puede deshacer.")
            colc1, colc2 = st.columns(2)
            with colc1:
                if st.button("⚠️ CONFIRMAR BORRADO (IRREVERSIBLE)", key="confirm_delete_root", use_container_width=True):
                    empty = pd.DataFrame(columns=['Timestamp','Proyecto','Nombre o Pseudónimo','P1','P10','P90','P99','P50_percentil','Comentarios'])
                    empty.to_csv(str(DATA_FILE), index=False, encoding='utf-8-sig')
                    st.success("✅ Datos borrados. Archivo reiniciado.")
                    st.session_state.confirm_delete = False
                    st.rerun()
            with colc2:
                if st.button("❌ Cancelar borrado", key="cancel_delete_root", use_container_width=True):
                    st.session_state.confirm_delete = False
                    st.info("Operación cancelada.")
    
    # Botón para cerrar sesión
    if st.button("🚪 Cerrar sesión de admin", use_container_width=True):
        st.session_state.admin_authenticated = False
        st.session_state.show_admin = False
        st.success("✅ Sesión cerrada")
        st.rerun()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9em; margin-top: 30px;'>
        Estimador de Percentiles creado Streamlit  | 
        Comparte el link para recopilar estimaciones en tiempo real
    </div>
""", unsafe_allow_html=True)
