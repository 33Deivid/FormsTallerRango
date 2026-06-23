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

CONFIG_FILE = "config_proyectos.json"
DATA_FILE = "respuestas_percentiles.csv"
ADMIN_PASSWORD = "Hola1234"

def load_config():
    """Carga la configuración de proyectos"""
    if os.path.exists(CONFIG_FILE):
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

    If drop_personal is True, 'Nombre' and 'Email' columns are removed.
    """
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if proyecto_id:
            df = df[df['Proyecto'] == proyecto_id]
        if drop_personal:
            # Eliminar columnas personales si existen
            for col in ['Nombre', 'Email']:
                if col in df.columns:
                    df = df.drop(columns=[col])
        return df
    return pd.DataFrame()

def save_response(proyecto_id, p1, p50, p99, comentarios=""):
    """Guarda una respuesta en el CSV (sin datos personales); ahora guarda P1, P50, P99."""
    new_data = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Proyecto': proyecto_id,
        'P1': p1,
        'P50': p50,
        'P99': p99,
        'Comentarios': comentarios
    }
    try:
        df = load_responses(proyecto_id=None, drop_personal=False)
        # append keeping columns consistent
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception:
        return False

def calcular_percentiles_datos(valores):
    """Calcula percentiles de los datos recopilados"""
    if len(valores) == 0:
        return {}
    
    return {
        'p1': np.percentile(valores, 1),
        'p50': np.percentile(valores, 50),
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

# ========== LAYOUT PRINCIPAL ==========

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<h1 class='main-title'>📊 Estimador de Percentiles</h1>", unsafe_allow_html=True)

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
        st.info(f"📌 **P50 (Mediana esperada): {proyecto['p50']} {unidad}**")
        
        with st.form(f"form_{proyecto['id']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Se elimina la recolección de nombre y email por privacidad
                pass
            
            with col2:
                pass  # Espacio para balance
            
            st.divider()
            st.write(f"### Estimaciones de {titulo_tipo} ({unidad})")
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
                
                # P10 ya no se solicita
            
            with col2:
                st.markdown("#### Percentiles Altos (Peor Caso)")
                
                # P90 ya no se solicita
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

                # Nuevo: preguntar P50 al usuario (límites por defecto 35.0 - 65.0)
                p50_user = st.number_input(
                    "¿Qué valor consideras como P50?",
                    min_value=35.0,
                    max_value=65.0,
                    value=_clamp_one_decimal(proyecto.get('p50', 50), 35.0, 65.0),
                    step=0.1,
                    format="%.1f",
                    key=f"p50_user_{proyecto['id']}",
                    help="Rango por defecto: 35.0 - 65.0"
                )
            
            # Validaciones visuales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if p1 <= proyecto['p50']:
                    st.success("✅ P1 válido")
                else:
                    st.error("❌ P1 debe ser ≤ P50")
            
            with col2:
                # No se valida P10
                pass
            
            with col3:
                # No se valida P90
                pass
            
            with col4:
                if p99 >= proyecto['p50']:
                    st.success("✅ P99 válido")
                else:
                    st.error("❌ P99 debe ser ≥ P50")
            
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
                # Validar y convertir a float de forma segura
                try:
                    p1f = float(p1)
                    p50f = float(p50_user)
                    p99f = float(p99)
                except Exception:
                    st.error("⚠️ Valores inválidos: asegúrate de ingresar números válidos con máximo 1 decimal")
                else:
                    # Comprobaciones lógicas
                    if not (p1f <= p50f and p50f <= p99f):
                        st.error("⚠️ Verifica: debe cumplirse P1 ≤ P50 ≤ P99")
                    elif p1f > p99f:
                        st.error("⚠️ P1 debe ser menor o igual a P99")
                    else:
                        saved = save_response(proyecto['id'], round(p1f,1), round(p50f,1), round(p99f,1), comentarios)
                        if saved:
                            st.success(f"✅ ¡Gracias por tus estimaciones para {proyecto['nombre']}!")
                            # Mostrar globos solo si el guardado fue exitoso
                            st.balloons()
                        else:
                            st.error("❌ Ocurrió un error al guardar. Intenta nuevamente más tarde.")

# Tab de análisis completo
with tabs[-1]:
    st.write("## 📊 Análisis Completo de Percentiles")
    
    # Selector de proyecto para análisis
    opciones_analisis = [f"{p['nombre']} ({p['subtipo']})" for p in proyectos_activos]
    proyecto_seleccionado_idx = st.selectbox(
        "Selecciona un proyecto para análisis detallado",
        range(len(opciones_analisis)),
        format_func=lambda i: opciones_analisis[i],
        key="proyecto_analisis"
    )
    
    proyecto_seleccionado = proyectos_activos[proyecto_seleccionado_idx]
    proyecto_id = proyecto_seleccionado['id']
    p50_valor = proyecto_seleccionado['p50']
    unidad = proyecto_seleccionado['unidad']
    tipo = proyecto_seleccionado['tipo']
    titulo_tipo = "Costos" if tipo == 'costos' else "Plazos"
    
    df_proyecto = load_responses(proyecto_id)
    
    if len(df_proyecto) == 0:
        st.info(f"📭 Aún no hay respuestas para {proyecto_seleccionado['nombre']}. ¡Sé el primero en responder!")
    else:
        st.divider()
        
        # ========== MÉTRICAS PRINCIPALES ==========
        st.write("### 📈 Métricas de Estimaciones")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total participantes", len(df_proyecto))
        with col2:
            st.metric(f"P50 objetivo", f"{p50_valor} {unidad}")
        with col3:
            st.metric("Última actualización", df_proyecto['Timestamp'].iloc[-1])
        
        st.divider()
        
        # ========== ANÁLISIS POR PERCENTIL ==========
        st.write("### 📊 Distribución de Estimaciones")
        
        col1, col2 = st.columns(2)
        
        # Gráfico 1: Histograma de P1
        with col1:
            st.write("#### Percentiles Bajos (P1)")

            fig1 = go.Figure()
            fig1.add_trace(go.Histogram(
                x=df_proyecto['P1'],
                name='P1',
                opacity=0.7,
                marker_color='#3498DB',
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
        
        # Gráfico 2: Histograma de P99
        with col2:
            st.write("#### Percentiles Altos (P99)")

            fig2 = go.Figure()
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
        
        st.divider()
        
        # ========== GRÁFICO COMPARATIVO ==========
        st.write(f"### 📉 Comparativa de Percentiles vs P50 ({titulo_tipo})")
        
        # Calcular promedios (P1, P50 usuario, P99)
        promedios = {
            'P1': df_proyecto['P1'].mean(),
            'P50': df_proyecto['P50'].mean() if 'P50' in df_proyecto.columns else np.nan,
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
            'Percentil': ['P1', 'P50', 'P99'],
            'Mín': [
                df_proyecto['P1'].min(),
                df_proyecto['P50'].min() if 'P50' in df_proyecto.columns else np.nan,
                df_proyecto['P99'].min()
            ],
            'Promedio': [
                df_proyecto['P1'].mean(),
                df_proyecto['P50'].mean() if 'P50' in df_proyecto.columns else np.nan,
                df_proyecto['P99'].mean()
            ],
            'Mediana': [
                df_proyecto['P1'].median(),
                df_proyecto['P50'].median() if 'P50' in df_proyecto.columns else np.nan,
                df_proyecto['P99'].median()
            ],
            'Máx': [
                df_proyecto['P1'].max(),
                df_proyecto['P50'].max() if 'P50' in df_proyecto.columns else np.nan,
                df_proyecto['P99'].max()
            ],
            'Desv. Est.': [
                df_proyecto['P1'].std(),
                df_proyecto['P50'].std() if 'P50' in df_proyecto.columns else np.nan,
                df_proyecto['P99'].std()
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # ========== TABLA DE DATOS COMPLETOS ==========
        st.write("### 📊 Datos Detallados")
        
        # Tabla de datos completos: solo visible para admin
        if st.session_state.admin_authenticated:
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
        
        st.write("### Modificar P50")
        
        cols = st.columns(len(config['proyectos']))
    
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
