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
    # KPIs
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total", df.shape[0])
    col2.metric("📊 Promedio Asistencia", round(df["total_asistencias"].mean(), 1))
    col3.metric("🎂 Edad Promedio", round(df["edad"].mean(), 1))

    st.divider()

    # =========================
    # GRÁFICOS SUPERIORES (2 EN FILA)
    # =========================
    colA, colB = st.columns(2)

    with colA:
        st.subheader("📈 Edad vs Asistencia")
        fig1, ax1 = plt.subplots(figsize=(5,3))
        sns.scatterplot(data=df, x="edad", y="total_asistencias", ax=ax1)
        st.pyplot(fig1)

    with colB:
        st.subheader("🏆 Top 10 Mayor Asistencia")
        top10 = df.sort_values(by="total_asistencias", ascending=False).head(10)
        fig2, ax2 = plt.subplots(figsize=(5,3))
        sns.barplot(data=top10, x="total_asistencias", y="nombre", ax=ax2)
        st.pyplot(fig2)

    st.divider()

    # =========================
    # TOP 10 MENOR ASISTENCIA
    # =========================
    st.subheader("⚠️ Top 10 Menor Asistencia")

    bottom10 = df.sort_values(by="total_asistencias", ascending=True).head(10)

    fig3, ax3 = plt.subplots(figsize=(6,3))
    sns.barplot(data=bottom10, x="total_asistencias", y="nombre", ax=ax3)
    st.pyplot(fig3)

    st.divider()

    # =========================
    # CONSULTA INDIVIDUAL
    # =========================
    st.subheader("🔎 Asistencias por Estudiante")

    estudiante_sel = st.selectbox(
        "Selecciona un estudiante",
        df["nombre"]
    )

    id_est = df[df["nombre"] == estudiante_sel]["id_estudiante"].values[0]

    conn = get_connection()

    asistencias_individual = pd.read_sql("""
    SELECT Fecha
    FROM asistencias
    WHERE Id_estudiante = %s
    ORDER BY Fecha
    """, conn, params=(id_est,))

    conn.close()

    # =========================
    # CONTEO POR MES (SOLO GRÁFICO)
    # =========================
    asistencias_individual["Fecha"] = pd.to_datetime(asistencias_individual["Fecha"])
    asistencias_individual["Año-Mes"] = asistencias_individual["Fecha"].dt.to_period("M")

    conteo_mensual = asistencias_individual.groupby("Año-Mes").size().reset_index(name="Total")
    conteo_mensual["Año-Mes"] = conteo_mensual["Año-Mes"].astype(str)

    st.subheader("📆 Tendencia Mensual")

    fig_mes, ax_mes = plt.subplots(figsize=(6,3))
    sns.lineplot(data=conteo_mensual, x="Año-Mes", y="Total", marker="o", ax=ax_mes)
    plt.xticks(rotation=45)
    st.pyplot(fig_mes)
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
