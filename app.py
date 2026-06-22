import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Formulario de Encuesta",
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

def save_response(nombre, email, edad, ciudad, pregunta1, pregunta2, pregunta3):
    """Guarda una respuesta en el CSV"""
    new_data = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Nombre': nombre,
        'Email': email,
        'Edad': edad,
        'Ciudad': ciudad,
        '¿Cómo califica nuestro servicio?': pregunta1,
        '¿Volvería a utilizar nuestros servicios?': pregunta2,
        '¿Nos recomendaría?': pregunta3
    }
    
    df = load_responses()
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Layout principal
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<h1 class='main-title'>📋 Formulario de Encuesta en Vivo</h1>", unsafe_allow_html=True)

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
                "Nombre completo",
                placeholder="Juan Pérez"
            )
            edad = st.number_input(
                "Edad",
                min_value=13,
                max_value=120,
                value=25
            )
        
        with col2:
            email = st.text_input(
                "Correo electrónico",
                placeholder="correo@ejemplo.com"
            )
            ciudad = st.text_input(
                "Ciudad",
                placeholder="Bogotá"
            )
        
        st.divider()
        st.write("### Preguntas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pregunta1 = st.radio(
                "¿Cómo califica nuestro servicio?",
                ["⭐ Excelente", "👍 Bueno", "😐 Regular", "👎 Malo"],
                key="q1"
            )
        
        with col2:
            pregunta2 = st.radio(
                "¿Volvería a utilizar nuestros servicios?",
                ["✅ Sí, definitivamente", "Probablemente", "No estoy seguro", "❌ No"],
                key="q2"
            )
        
        with col3:
            pregunta3 = st.radio(
                "¿Nos recomendaría?",
                ["🎯 Muy probablemente", "Probablemente", "Tal vez", "❌ No"],
                key="q3"
            )
        
        comentarios = st.text_area(
            "Comentarios adicionales (opcional)",
            placeholder="Comparta sus sugerencias o comentarios..."
        )
        
        submitted = st.form_submit_button("📤 Enviar respuesta", use_container_width=True)
        
        if submitted:
            # Validar campos obligatorios
            if not nombre or not email or not ciudad:
                st.error("⚠️ Por favor complete todos los campos obligatorios")
            elif "@" not in email:
                st.error("⚠️ Por favor ingrese un correo válido")
            else:
                save_response(nombre, email, edad, ciudad, pregunta1, pregunta2, pregunta3)
                st.success("✅ ¡Gracias por completar el formulario!")
                st.balloons()
                st.session_state.form_submitted = True

with tab2:
    df = load_responses()
    
    if len(df) == 0:
        st.info("📭 Aún no hay respuestas. ¡Sé el primero en responder!")
    else:
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de respuestas", len(df))
        with col2:
            st.metric("Participantes únicos", df['Email'].nunique())
        with col3:
            st.metric("Edad promedio", f"{df['Edad'].mean():.1f}")
        with col4:
            st.metric("Ciudades representadas", df['Ciudad'].nunique())
        
        st.divider()
        
        # Gráficas
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Calificación del servicio")
            q1_counts = df['¿Cómo califica nuestro servicio?'].value_counts()
            fig1 = px.pie(
                values=q1_counts.values,
                names=q1_counts.index,
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.RdYlGn_r
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
                color_discrete_sequence=px.colors.sequential.Blues_r
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
                color_discrete_sequence=px.colors.sequential.Greens_r
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
                color_discrete_sequence=["#636EFA"]
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
            color_discrete_sequence=["#AB63FA"]
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
