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

def load_responses(proyecto_id=None):
    """Carga las respuestas del CSV, opcionalmente filtradas por proyecto"""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if proyecto_id:
            df = df[df['Proyecto'] == proyecto_id]
        return df
    return pd.DataFrame()

def save_response(nombre, email, proyecto_id, p1, p10, p90, p99, comentarios=""):
    """Guarda una respuesta en el CSV"""
    new_data = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Nombre': nombre,
        'Email': email,
        'Proyecto': proyecto_id,
        'P1': p1,
        'P10': p10,
        'P90': p90,
        'P99': p99,
        'Comentarios': comentarios
    }
    
    df = load_responses()
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

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

# Inicializar sesión
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False

# ========== LAYOUT PRINCIPAL ==========

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<h1 class='main-title'>📊 Estimador de Percentiles de Costos</h1>", unsafe_allow_html=True)

with col2:
    # Botón para panel de control
    if st.button("⚙️ Panel Control", key="admin_btn"):
        st.session_state.show_admin = not st.session_state.show_admin

# Cargar configuración
config = load_config()
proyectos_activos = get_proyectos_activos(config)

if not proyectos_activos:
    st.warning("⚠️ No hay proyectos activos en este momento. Por favor intenta más tarde.")
    st.stop()

# ========== TABS PRINCIPALES ==========

tabs = st.tabs([f"✍️ {p['nombre']}" for p in proyectos_activos] + ["📊 Análisis Completo"])

# Tabs de formularios por proyecto
for idx, proyecto in enumerate(proyectos_activos):
    with tabs[idx]:
        st.write(f"### {proyecto['nombre']}")
        st.write(f"_{proyecto['descripcion']}_")
        st.info(f"📌 **P50 (Mediana esperada): {proyecto['p50']} KUSD**")
        
        with st.form(f"form_{proyecto['id']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input(
                    "Nombre completo",
                    placeholder="Juan Pérez",
                    key=f"nombre_{proyecto['id']}"
                )
                email = st.text_input(
                    "Correo electrónico",
                    placeholder="correo@ejemplo.com",
                    key=f"email_{proyecto['id']}"
                )
            
            with col2:
                pass  # Espacio para balance
            
            st.divider()
            st.write("### Estimaciones de Costo (KUSD)")
            st.write("Proporciona tu estimación para cada percentil:")
            
            # Crear dos columnas para los inputs
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Percentiles Bajos (Mejor Caso)")
                
                p1 = st.number_input(
                    f"P1 (Percentil 1) - Mejor caso",
                    min_value=0,
                    max_value=proyecto['p50'],
                    value=int(proyecto['p50'] * 0.3),
                    step=5,
                    key=f"p1_{proyecto['id']}",
                    help=f"Máximo: {proyecto['p50']} KUSD"
                )
                
                p10 = st.number_input(
                    f"P10 (Percentil 10)",
                    min_value=0,
                    max_value=proyecto['p50'],
                    value=int(proyecto['p50'] * 0.6),
                    step=5,
                    key=f"p10_{proyecto['id']}",
                    help=f"Máximo: {proyecto['p50']} KUSD"
                )
            
            with col2:
                st.markdown("#### Percentiles Altos (Peor Caso)")
                
                p90 = st.number_input(
                    f"P90 (Percentil 90)",
                    min_value=proyecto['p50'],
                    max_value=int(proyecto['p50'] * 3),
                    value=int(proyecto['p50'] * 1.5),
                    step=5,
                    key=f"p90_{proyecto['id']}",
                    help=f"Mínimo: {proyecto['p50']} KUSD"
                )
                
                p99 = st.number_input(
                    f"P99 (Percentil 99) - Peor caso",
                    min_value=proyecto['p50'],
                    max_value=int(proyecto['p50'] * 5),
                    value=int(proyecto['p50'] * 2.5),
                    step=5,
                    key=f"p99_{proyecto['id']}",
                    help=f"Mínimo: {proyecto['p50']} KUSD"
                )
            
            # Validaciones visuales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if p1 <= proyecto['p50']:
                    st.success("✅ P1 válido")
                else:
                    st.error("❌ P1 debe ser ≤ P50")
            
            with col2:
                if p10 <= proyecto['p50']:
                    st.success("✅ P10 válido")
                else:
                    st.error("❌ P10 debe ser ≤ P50")
            
            with col3:
                if p90 >= proyecto['p50']:
                    st.success("✅ P90 válido")
                else:
                    st.error("❌ P90 debe ser ≥ P50")
            
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
                f"📤 Enviar estimaciones para {proyecto['nombre']}", 
                use_container_width=True
            )
            
            if submitted:
                # Validar campos obligatorios
                if not nombre or not email:
                    st.error("⚠️ Por favor completa nombre y correo")
                elif "@" not in email:
                    st.error("⚠️ Correo inválido")
                elif not (p1 <= proyecto['p50'] and p10 <= proyecto['p50'] and 
                         p90 >= proyecto['p50'] and p99 >= proyecto['p50']):
                    st.error("⚠️ Verifica las restricciones de percentiles")
                elif p1 > p10:
                    st.error("⚠️ P1 debe ser menor o igual a P10")
                elif p90 > p99:
                    st.error("⚠️ P90 debe ser menor o igual a P99")
                else:
                    save_response(nombre, email, proyecto['id'], p1, p10, p90, p99, comentarios)
                    st.success(f"✅ ¡Gracias por tus estimaciones para {proyecto['nombre']}!")
                    st.balloons()

# Tab de análisis completo
with tabs[-1]:
    st.write("## 📊 Análisis Completo de Percentiles")
    
    # Selector de proyecto para análisis
    proyecto_seleccionado = st.selectbox(
        "Selecciona un proyecto para análisis detallado",
        [p['nombre'] for p in proyectos_activos],
        key="proyecto_analisis"
    )
    
    proyecto_id = proyectos_activos[[p['nombre'] for p in proyectos_activos].index(proyecto_seleccionado)]['id']
    p50_valor = proyectos_activos[[p['nombre'] for p in proyectos_activos].index(proyecto_seleccionado)]['p50']
    
    df_proyecto = load_responses(proyecto_id)
    
    if len(df_proyecto) == 0:
        st.info(f"📭 Aún no hay respuestas para {proyecto_seleccionado}. ¡Sé el primero en responder!")
    else:
        st.divider()
        
        # ========== MÉTRICAS PRINCIPALES ==========
        st.write("### 📈 Métricas de Estimaciones")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total participantes", len(df_proyecto))
        with col2:
            st.metric("Correos únicos", df_proyecto['Email'].nunique())
        with col3:
            st.metric("P50 objetivo", f"{p50_valor} KUSD")
        with col4:
            st.metric("Última actualización", df_proyecto['Timestamp'].iloc[-1])
        
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
                xaxis_title='Estimación (KUSD)',
                yaxis_title='Cantidad de Participantes'
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Histograma de P90 y P99
        with col2:
            st.write("#### Percentiles Altos (P90 y P99)")
            
            fig2 = go.Figure()
            
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
                xaxis_title='Estimación (KUSD)',
                yaxis_title='Cantidad de Participantes'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        st.divider()
        
        # ========== GRÁFICO COMPARATIVO ==========
        st.write("### 📉 Comparativa de Percentiles vs P50")
        
        # Calcular promedios
        promedios = {
            'P1': df_proyecto['P1'].mean(),
            'P10': df_proyecto['P10'].mean(),
            'P50': p50_valor,
            'P90': df_proyecto['P90'].mean(),
            'P99': df_proyecto['P99'].mean()
        }
        
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=list(promedios.keys()),
            y=list(promedios.values()),
            marker_color=['#3498DB', '#2ECC71', '#F39C12', '#E74C3C', '#9B59B6'],
            text=[f'{v:.0f}' for v in promedios.values()],
            textposition='auto',
            name='Promedio Estimado'
        ))
        
        fig3.add_hline(y=p50_valor, line_dash="dash", line_color="red",
                      annotation_text=f"P50 Objetivo: {p50_valor} KUSD")
        
        fig3.update_layout(
            height=400,
            xaxis_title='Percentil',
            yaxis_title='Estimación (KUSD)',
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
                df_proyecto['P10'].min(),
                df_proyecto['P90'].min(),
                df_proyecto['P99'].min()
            ],
            'Promedio': [
                df_proyecto['P1'].mean(),
                df_proyecto['P10'].mean(),
                df_proyecto['P90'].mean(),
                df_proyecto['P99'].mean()
            ],
            'Mediana': [
                df_proyecto['P1'].median(),
                df_proyecto['P10'].median(),
                df_proyecto['P90'].median(),
                df_proyecto['P99'].median()
            ],
            'Máx': [
                df_proyecto['P1'].max(),
                df_proyecto['P10'].max(),
                df_proyecto['P90'].max(),
                df_proyecto['P99'].max()
            ],
            'Desv. Est.': [
                df_proyecto['P1'].std(),
                df_proyecto['P10'].std(),
                df_proyecto['P90'].std(),
                df_proyecto['P99'].std()
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # ========== TABLA DE DATOS COMPLETOS ==========
        st.write("### 📊 Datos Detallados")
        
        st.dataframe(
            df_proyecto,
            use_container_width=True,
            hide_index=True
        )
        
        # Descargar datos
        csv = df_proyecto.to_csv(index=False)
        st.download_button(
            label=f"📥 Descargar datos ({proyecto_seleccionado})",
            data=csv,
            file_name=f"estimaciones_{proyecto_id}.csv",
            mime="text/csv"
        )

# ========== PANEL DE CONTROL (Admin) ==========
if st.session_state.show_admin:
    st.divider()
    st.markdown("---")
    st.write("## ⚙️ Panel de Control de Proyectos")
    st.warning("⚠️ Este panel es solo para administradores")
    
    with st.expander("📋 Gestionar Proyectos", expanded=True):
        config = load_config()
        
        st.write("### Activar/Desactivar Proyectos")
        
        cols = st.columns(len(config['proyectos']))
        
        for idx, proyecto in enumerate(config['proyectos']):
            with cols[idx]:
                nuevo_estado = st.checkbox(
                    f"{proyecto['nombre']}",
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
        
        for idx, proyecto in enumerate(config['proyectos']):
            with cols[idx]:
                nuevo_p50 = st.number_input(
                    f"P50 {proyecto['nombre']}",
                    value=proyecto['p50'],
                    step=5,
                    key=f"p50_{proyecto['id']}"
                )
                
                if nuevo_p50 != proyecto['p50']:
                    config['proyectos'][idx]['p50'] = nuevo_p50
                    save_config(config)
                    st.success(f"✅ P50 actualizado")
                    st.rerun()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9em; margin-top: 30px;'>
        Estimador de Percentiles creado con ❤️ usando Streamlit | 
        Comparte el link para recopilar estimaciones en tiempo real
    </div>
""", unsafe_allow_html=True)
