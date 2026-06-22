# 📋 Formulario de Encuesta en Vivo con Streamlit

Aplicación interactiva para crear formularios que permiten recopilar respuestas en tiempo real y visualizar gráficas con los datos actualizados automáticamente.

## 🚀 Características

- ✅ **Formulario interactivo**: Campos para nombre, email, edad, ciudad y preguntas personalizadas
- 📊 **Gráficas en vivo**: Visualizaciones actualizadas automáticamente con Plotly
- 📈 **Métricas principales**: Total de respuestas, participantes únicos, edad promedio, ciudades
- 🌍 **Análisis geográfico**: Muestra distribución de respuestas por ciudad
- 📥 **Descarga de datos**: Exporta los datos en formato CSV
- 🔄 **Actualización en tiempo real**: Refresca los datos automáticamente

## 📋 Componentes del formulario

### Sección 1: Datos personales
- Nombre completo (requerido)
- Correo electrónico (requerido, validado)
- Edad (número entre 13 y 120)
- Ciudad (requerido)

### Sección 2: Preguntas de encuesta
1. ¿Cómo califica nuestro servicio? (Excelente, Bueno, Regular, Malo)
2. ¿Volvería a utilizar nuestros servicios? (Múltiples opciones)
3. ¿Nos recomendaría? (Múltiples opciones)
4. Comentarios adicionales (opcional)

## 📊 Análisis disponibles

- Gráfico de pastel: Calificación del servicio
- Gráfico de barras: Intención de recompra
- Gráfico de barras: Recomendación
- Histograma: Distribución por edad
- Gráfico de barras: Top 10 ciudades
- Tabla de datos completos

## 🛠️ Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/33Deivid/FormsTallerRango.git
cd FormsTallerRango
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

## ▶️ Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📤 Compartir el formulario

Una vez que ejecutes la aplicación, podrás:
1. Copiar el URL de tu navegador
2. Compartir ese link con las personas que quieras que completen el formulario
3. Ver las respuestas en vivo en la pestaña "Resultados en Vivo"

## 💾 Almacenamiento de datos

Las respuestas se almacenan automáticamente en un archivo `respuestas.csv` en la carpeta raíz del proyecto.

### Estructura del archivo CSV:
```
Timestamp,Nombre,Email,Edad,Ciudad,¿Cómo califica nuestro servicio?,¿Volvería a utilizar nuestros servicios?,¿Nos recomendaría?
2026-06-22 10:30:45,Juan Pérez,juan@example.com,28,Bogotá,Excelente,Sí definitivamente,Muy probablemente
```

## 🎨 Personalización

Puedes modificar fácilmente:

### Cambiar las preguntas:
En el archivo `app.py`, busca la sección "Preguntas" y modifica el contenido de los `st.radio()` y agrega nuevos campos según necesites.

### Cambiar colores:
Modifica las `color_discrete_sequence` en las gráficas Plotly.

### Cambiar diseño:
Edita el CSS en la sección de estilos al principio del archivo.

## 📦 Dependencias

- **streamlit**: Framework web para crear aplicaciones de datos
- **pandas**: Manipulación y análisis de datos
- **plotly**: Gráficas interactivas
- **python-dateutil**: Utilidades de fecha

## 🚀 Deployment

Puedes desplegar esta aplicación gratuitamente en:

### Streamlit Cloud:
1. Sube tu repositorio a GitHub
2. Ve a https://streamlit.io/cloud
3. Crea una nueva aplicación desde tu repositorio
4. Streamlit se encargará del resto

### Render, Railway, o Heroku:
Alternativas para desplegar si prefieres otros servicios.

## 📝 Ejemplo de flujo

1. Usuario abre el enlace compartido
2. Completa el formulario en la pestaña "Formulario"
3. Envía sus respuestas
4. Recibe confirmación visual
5. Puede ver análisis en vivo en la pestaña "Resultados en Vivo"
6. Los datos se almacenan automáticamente

## 🤝 Contribuir

Si quieres mejorar esta aplicación:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza cambios
4. Envía un Pull Request

## 📄 Licencia

Este proyecto está disponible bajo la licencia MIT.

## 💡 Próximas mejoras

- [ ] Autenticación de usuarios
- [ ] Múltiples formularios
- [ ] Base de datos centralizada
- [ ] Exportación a Excel
- [ ] Notificaciones por email
- [ ] Análisis avanzado con machine learning
- [ ] Integración con Google Sheets

## ❓ FAQ

**P: ¿Dónde se guardan las respuestas?**
R: En el archivo `respuestas.csv` en la carpeta raíz del proyecto.

**P: ¿Puedo ejecutar múltiples formularios?**
R: Sí, puedes crear copias del archivo `app.py` con diferentes configuraciones.

**P: ¿Los datos se actualizan automáticamente?**
R: Las gráficas se actualizan cada vez que recargas la página o haces clic en "Actualizar datos".

**P: ¿Puedo personalizar los colores y diseño?**
R: Sí, edita los parámetros de Plotly y el CSS en el archivo `app.py`.

---

**Creado con ❤️ usando Streamlit**
