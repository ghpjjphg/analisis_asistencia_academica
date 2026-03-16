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
            e.edad,
            COUNT(a.Id_asistencia) as total_asistencias
        FROM estudiantes e
        LEFT JOIN asistencias a
            ON e.id_estudiante = a.Id_estudiante
        GROUP BY e.id_estudiante
    """, conn)

    conn.close()

    # =========================
    # KPIs SUPERIORES
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total Estudiantes", df.shape[0])
    col2.metric("📊 Promedio Asistencia", round(df["total_asistencias"].mean(), 1))
    col3.metric("🎂 Edad Promedio", round(df["edad"].mean(), 1))

    st.divider()

    # =====================================================
    # 🔝 FILA SUPERIOR
    # =====================================================
    col_top_left, col_top_right = st.columns(2)

    # --------- Edad vs Asistencia
    with col_top_left:
        st.subheader("📈 Edad vs Asistencia")

        fig1, ax1 = plt.subplots(figsize=(6,4))
        sns.scatterplot(data=df, x="edad", y="total_asistencias", ax=ax1)
        ax1.set_xlabel("Edad")
        ax1.set_ylabel("Total Asistencias")
        st.pyplot(fig1)

    # --------- Asistencia por estudiante
    with col_top_right:
        st.subheader("🔎 Asistencia por Estudiante")

        estudiante_sel = st.selectbox(
            "Selecciona un estudiante",
            df["nombre"]
        )

        id_est = df[df["nombre"] == estudiante_sel]["id_estudiante"].values[0]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT Fecha
            FROM asistencias
            WHERE Id_estudiante = %s
            ORDER BY Fecha
        """

        cursor.execute(query, (int(id_est),))
        rows = cursor.fetchall()
        conn.close()

        asistencias_individual = pd.DataFrame(rows, columns=["Fecha"])

        if not asistencias_individual.empty:

            asistencias_individual["Fecha"] = pd.to_datetime(asistencias_individual["Fecha"])
            asistencias_individual["Año-Mes"] = asistencias_individual["Fecha"].dt.to_period("M")

            conteo_mensual = asistencias_individual.groupby("Año-Mes").size().reset_index(name="Total")
            conteo_mensual["Año-Mes"] = conteo_mensual["Año-Mes"].astype(str)
            
            st.metric("📌 Total Asistencias", len(asistencias_individual))

        else:
            st.warning("Este estudiante no tiene asistencias registradas.")
            
            fig_mes, ax_mes = plt.subplots(figsize=(6,4))
            sns.lineplot(data=conteo_mensual, x="Año-Mes", y="Total", marker="o", ax=ax_mes)
            plt.xticks(rotation=45)
            ax_mes.set_xlabel("Año-Mes")
            ax_mes.set_ylabel("Total mensual")
            st.pyplot(fig_mes)

            

    st.divider()

    # =====================================================
    # 🔽 FILA INFERIOR
    # =====================================================
    col_bottom_left, col_bottom_right = st.columns(2)

    # --------- Top 10 Mayor Asistencia
    with col_bottom_left:
        st.subheader("🏆 Top 10 Mayor Asistencia")

        top10 = df.sort_values(by="total_asistencias", ascending=False).head(10)

        fig2, ax2 = plt.subplots(figsize=(6,4))
        sns.barplot(data=top10, x="total_asistencias", y="nombre", ax=ax2)
        ax2.set_xlabel("Total Asistencias")
        ax2.set_ylabel("Estudiante")
        st.pyplot(fig2)

    # --------- Top 10 Menor Asistencia
    with col_bottom_right:
        st.subheader("⚠️ Top 10 Menor Asistencia")

        bottom10 = df.sort_values(by="total_asistencias", ascending=True).head(10)

        fig3, ax3 = plt.subplots(figsize=(6,4))
        sns.barplot(data=bottom10, x="total_asistencias", y="nombre", ax=ax3)
        ax3.set_xlabel("Total Asistencias")
        ax3.set_ylabel("Estudiante")
        st.pyplot(fig3)
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
