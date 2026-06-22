import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Formulario Taller de Rango API N20MS10",
    page_icon="📋",
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
        .metrics-container {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Archivo de datos
DATA_FILE = "respuestas.csv"

# Inicializar sesión
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

def load_responses():
    """Carga las respuestas del CSV"""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def save_response(nombre, email, pregunta1, pregunta2, pregunta3, pregunta4):
    """Guarda una respuesta en el CSV"""
    new_data = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Nombre': nombre,
        'Email': email,
        'P1': pregunta1,
        'p10': pregunta2,
        'P90': pregunta3,
        'p99': pregunta4
    }
    
    df = load_responses()
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Layout principal
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<h1 class='main-title'>📋 Formulario  Taller de Rango API N20MS10</h1>", unsafe_allow_html=True)

with col2:
    if st.button("🔄 Actualizar datos", key="refresh_btn"):
        st.rerun()

# Tabs para formulario y resultados
tab1, tab2 = st.tabs(["✍️ Formulario", "📊 Resultados en Vivo"])

with tab1:
    st.write("### Complete el siguiente formulario")
    
    with st.form("survey_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input(
                "Nombre",
                placeholder="Juan Pérez"
            )
        
        with col2:
            email = st.text_input(
                "Correo electrónico",
                placeholder="correo@ejemplo.com"
            )
        
        st.divider()
        st.write("### ¿Cual crees que es el percentil 1, 10, 90 y 99 del costo estimado de Talleres de Mantenimiento?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pregunta1 = st.slider(
                "¿Cual crees que es el P1?",
                1,5,3,
                key="q1"
            )
        
        with col2:
            pregunta2 =st.slider(
                "¿Cual crees que es el P10?",
                1,5,3,
                key="q2"
            )
        
        with col3:
            pregunta3 = st.slider(
                "¿Cual crees que es el P90?",
                1,5,3,
                key="q3"
            )
            
        with col4:
            pregunta4 = st.slider(
                "¿Cual crees que es el P99?",
                1,5,3,
                key="q4"
            )
        
        comentarios = st.text_area(
            "Comentarios adicionales (opcional)",
            placeholder="Comparta sus sugerencias o comentarios..."
        )
        
        submitted = st.form_submit_button("📤 Enviar respuesta", use_container_width=True)
        
        if submitted:
            # Validar campos obligatorios
            if not nombre or not email:
                st.error("⚠️ Por favor complete todos los campos obligatorios")
            elif "@" not in email:
                st.error("⚠️ Por favor ingrese un correo válido")
            else:
                save_response(nombre, email, pregunta1, pregunta2, pregunta3, pregunta4 )
                st.success("✅ ¡Gracias por completar el formulario!")
                st.balloons()
                st.session_state.form_submitted = True

with tab2:
    df = load_responses()
    
    if len(df) == 0:
        st.info("📭 Aún no hay respuestas. ¡Sé el primero en responder!")
    else:
        # Métricas principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de respuestas", len(df))
        with col2:
            st.metric("Participantes únicos", df['Email'].nunique())
        
        st.divider()
        
        # Gráficas
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### p1")
            q1_counts = df['¿Cual el el P1?'].value_counts()
            fig1 = px.pie(
                values=q1_counts.values,
                names=q1_counts.index,
                hole=0.3,
                color_discrete_sequence=["#FF6B6B", "#4ECDC4", "#FFE66D", "#95A5A6"]
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.write("### ¿Volvería a utilizar nuestros servicios?")
            q2_counts = df['¿Volvería a utilizar nuestros servicios?'].value_counts()
            fig2 = px.bar(
                x=q2_counts.index,
                y=q2_counts.values,
                color=q2_counts.index,
                color_discrete_sequence=["#3498DB", "#2ECC71", "#F39C12", "#E74C3C"]
            )
            fig2.update_layout(height=400, showlegend=False)
            fig2.update_xaxes(title_text="")
            fig2.update_yaxes(title_text="Cantidad")
            st.plotly_chart(fig2, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### ¿Nos recomendaría?")
            q3_counts = df['¿Nos recomendaría?'].value_counts()
            fig3 = px.bar(
                x=q3_counts.index,
                y=q3_counts.values,
                color=q3_counts.index,
                color_discrete_sequence=["#27AE60", "#2ECC71", "#F39C12", "#E74C3C"]
            )
            fig3.update_layout(height=400, showlegend=False)
            fig3.update_xaxes(title_text="")
            fig3.update_yaxes(title_text="Cantidad")
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.write("### Distribución por edad")
            fig4 = px.histogram(
                df,
                x='Edad',
                nbins=10,
                color_discrete_sequence=["#9B59B6"]
            )
            fig4.update_layout(height=400, showlegend=False)
            fig4.update_xaxes(title_text="Edad")
            fig4.update_yaxes(title_text="Cantidad")
            st.plotly_chart(fig4, use_container_width=True)
        
        # Distribución geográfica
        st.write("### Ciudades representadas")
        ciudades_counts = df['Ciudad'].value_counts().head(10)
        fig5 = px.bar(
            x=ciudades_counts.index,
            y=ciudades_counts.values,
            labels={'x': 'Ciudad', 'y': 'Respuestas'},
            color_discrete_sequence=["#E67E22"]
        )
        fig5.update_layout(height=400)
        fig5.update_xaxes(title_text="Ciudad")
        fig5.update_yaxes(title_text="Cantidad")
        st.plotly_chart(fig5, use_container_width=True)
        
        st.divider()
        
        # Tabla de datos completos
        st.write("### Datos detallados")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Opción de descargar datos
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Descargar datos (CSV)",
            data=csv,
            file_name="respuestas_encuesta.csv",
            mime="text/csv"
        )

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9em; margin-top: 30px;'>
        Formulario creado con ❤️ usando Streamlit | 
        Comparte el link de esta página para recopilar más respuestas
    </div>
""", unsafe_allow_html=True)
