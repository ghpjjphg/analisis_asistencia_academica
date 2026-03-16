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

    st.title("📊 Panel Analítico")

    # =========================
    # CONEXIÓN
    # =========================
    conn = get_connection()

    df = pd.read_sql("""
    SELECT 
        e.id_estudiante,
        CONCAT(e.Primer_nombre,' ',e.Primer_apellido) as nombre,
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

    col1, col2, col3, col4 = st.columns(4)

    total_estudiantes = df["id_estudiante"].nunique()
    promedio_asistencia = df["total_asistencias"].mean()
    max_asistencia = df["total_asistencias"].max()
    min_asistencia = df["total_asistencias"].min()

    col1.metric("👥 Total Estudiantes", total_estudiantes)
    col2.metric("📊 Promedio Asistencia", round(promedio_asistencia, 1))
    col3.metric("🏆 Máxima Asistencia", max_asistencia)
    col4.metric("⚠️ Mínima Asistencia", min_asistencia)

    st.divider()

    # =========================
    # ANÁLISIS ESTADÍSTICO
    # =========================
    st.subheader("📈 Análisis Estadístico")

    col1, col2, col3 = st.columns(3)
    col1.write("Media:", round(df["total_asistencias"].mean(), 2))
    col2.write("Mediana:", round(df["total_asistencias"].median(), 2))
    col3.write("Desviación estándar:", round(df["total_asistencias"].std(), 2))

    fig1, ax1 = plt.subplots()
    sns.histplot(df["total_asistencias"], kde=True)
    st.pyplot(fig1)

    st.divider()

    # =========================
    # SEGMENTACIÓN DE RIESGO
    # =========================
    st.subheader("⚠️ Segmentación de Riesgo Académico")

    df["porcentaje"] = (df["total_asistencias"] / 240) * 100

    def clasificar(x):
        if x < 70:
            return "Alto Riesgo"
        elif x < 85:
            return "Riesgo Medio"
        else:
            return "Bajo Riesgo"

    df["segmento"] = df["porcentaje"].apply(clasificar)

    fig2, ax2 = plt.subplots()
    sns.countplot(x="segmento", data=df)
    st.pyplot(fig2)

    porcentaje_riesgo = round((df[df["segmento"] == "Alto Riesgo"].shape[0] / total_estudiantes) * 100, 2)

    if porcentaje_riesgo > 30:
        st.error(f"⚠️ {porcentaje_riesgo}% de estudiantes están en alto riesgo académico.")
    else:
        st.success("✅ El nivel de riesgo académico está bajo control.")

    st.divider()

    # =========================
    # TOP 10 ESTUDIANTES
    # =========================
    st.subheader("🏆 Top 10 Estudiantes con Mayor Asistencia")

    top10 = df.sort_values(by="total_asistencias", ascending=False).head(10)

    fig3, ax3 = plt.subplots()
    sns.barplot(x="total_asistencias", y="nombre", data=top10)
    st.pyplot(fig3)

    st.divider()

    # =========================
    # PERFIL INDIVIDUAL
    # =========================
    st.subheader("👤 Perfil Individual del Estudiante")

    estudiante_sel = st.selectbox(
        "Selecciona un estudiante",
        df["nombre"]
    )

    info = df[df["nombre"] == estudiante_sel]

    st.metric("Total Asistencias", int(info["total_asistencias"]))
    st.metric("Porcentaje de Asistencia", round(info["porcentaje"].values[0], 2))
    st.metric("Segmento", info["segmento"].values[0])

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
