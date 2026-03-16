import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from database.connection import get_connection
# ---------------- CONFIGURACIÓN ----------------

st.set_page_config(
    page_title="Sistema de Análisis de Asistencia Académica",
    layout="wide"
)

# ---------------- ESTILOS ----------------

st.markdown("""
<style>
.main {
    background-color: #F1F5F9;
}
h1, h2, h3 {
    color: #1E3A8A;
}
</style>
""", unsafe_allow_html=True)

# ---------------- MENÚ LATERAL ----------------

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "📊 Panel Analítico", "📚 Documentación"]
)

# =====================================================
# 🏠 LANDING PAGE
# =====================================================

if menu == "🏠 Inicio":

    st.title("📊 Sistema de Análisis de Asistencia Académica")
    st.subheader("Desarrollado por JUAN PABLO HENAO")

    imagen = Image.open("ASISTENCIA.png")
    st.image(imagen, width=250)

    st.markdown("""
    ### 🎯 Objetivo

    Este sistema permite analizar el comportamiento de asistencia de estudiantes universitarios 
    mediante consultas SQL y visualización de datos.

    ### 🗄️ Estructura de la Base de Datos

    - **Estudiantes**
    - **Carreras**
    - **Relación Estudiantes-Carreras**
    - **Asistencias**

    ### 📈 ¿Qué podrás analizar?

    - Promedio de asistencia
    - Estudiantes con mayor compromiso
    - Riesgo académico
    - Estudiantes con múltiples carreras

    ---
    Presiona **Panel Analítico** en el menú para comenzar.
    """)

# =====================================================
# 📊 PANEL ANALÍTICO
# =====================================================


elif menu == "📊 Panel Analítico":

    st.title("📊 Panel Analítico - Edad vs Asistencia")

    # =========================
    # CONEXIÓN
    # =========================
    conn = get_connection()

    df = pd.read_sql("""
    SELECT 
        e.id_estudiante,
        CONCAT(e.Primer_nombre,' ',e.Primer_apellido) as nombre,
        e.edad,
        COUNT(a.Id_asistencia) as total_asistencias
    FROM estudiantes e
    LEFT JOIN asistencias a
        ON e.id_estudiante = a.Id_estudiante
    GROUP BY e.id_estudiante
    """, conn)

    conn.close()

    # =========================
    # KPIs GENERALES
    # =========================
    st.subheader("📌 Indicadores Generales")

    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total Estudiantes", df.shape[0])
    col2.metric("📊 Promedio Asistencia", round(df["total_asistencias"].mean(), 1))
    col3.metric("🎂 Edad Promedio", round(df["edad"].mean(), 1))

    st.divider()

    # =========================
    # RELACIÓN EDAD VS ASISTENCIA
    # =========================
    st.subheader("📈 Relación entre Edad y Asistencias")

    fig1, ax1 = plt.subplots()
    sns.scatterplot(data=df, x="edad", y="total_asistencias")
    st.pyplot(fig1)

    st.divider()

    # =========================
    # TOP 10 QUE MÁS ASISTEN
    # =========================
    st.subheader("🏆 Estudiantes que MÁS asisten y su edad")

    top10 = df.sort_values(by="total_asistencias", ascending=False).head(10)

    fig2, ax2 = plt.subplots()
    sns.barplot(data=top10, x="total_asistencias", y="nombre")
    st.pyplot(fig2)

    st.dataframe(top10[["nombre", "edad", "total_asistencias"]])

    st.divider()

    # =========================
    # TOP 10 QUE MENOS ASISTEN
    # =========================
    st.subheader("⚠️ Estudiantes que MENOS asisten y su edad")

    bottom10 = df.sort_values(by="total_asistencias", ascending=True).head(10)

    fig3, ax3 = plt.subplots()
    sns.barplot(data=bottom10, x="total_asistencias", y="nombre")
    st.pyplot(fig3)

    st.dataframe(bottom10[["nombre", "edad", "total_asistencias"]])

# =====================================================
# 📚 DOCUMENTACIÓN
# =====================================================

elif menu == "📚 Documentación":

    st.title("📚 Documentación Técnica")

    tab1, tab2 = st.tabs(["Base de Datos", "Metodología"])

    with tab1:
        st.markdown("""
        ### Modelo Relacional

        - estudiantes
        - carreras
        - estudiantes_carreras
        - asistencias

        Relaciones:
        - Un estudiante puede tener múltiples asistencias.
        - Un estudiante puede estar en múltiples carreras.
        """)

    with tab2:
        st.markdown("""
        ### Enfoque Analítico

        Se utilizaron consultas agregadas con COUNT y GROUP BY para medir:

        - Promedio de asistencia
        - Distribución
        - Segmentación de riesgo
        """)
