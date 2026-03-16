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
    background-color: #F8FAFC;
}

h1 {
    color: #0F172A;
    font-weight: 700;
}

h2, h3 {
    color: #1E293B;
}

section[data-testid="stSidebar"] {
    background-color: #0F172A;
    color: white;
}

.stMetric {
    background-color: #FFFFFF;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
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

    conn = get_connection()
    st.write(pd.read_sql("DESCRIBE estudiantes", conn))
    st.write(pd.read_sql("DESCRIBE carreras", conn))
    st.write(pd.read_sql("DESCRIBE asistencias", conn))
    # =====================================================
    # DATA GENERAL CON RELACIONES
    # =====================================================
    df = pd.read_sql("""
    SELECT 
        e.id_estudiante,
        CONCAT(e.Primer_nombre,' ',e.Primer_apellido) as nombre,
        e.edad,
        c.nombre_carrera,
        COUNT(a.Id_asistencia) as total_asistencias
    FROM estudiantes e
    INNER JOIN estudiantes_carreras ec
        ON e.id_estudiante = ec.id_estudiante
    INNER JOIN carreras c
        ON ec.id_carrera = c.id_carrera
    LEFT JOIN asistencias a
        ON e.id_estudiante = a.Id_estudiante
    GROUP BY 
        e.id_estudiante,
        e.Primer_nombre,
        e.Primer_apellido,
        e.edad,
        c.nombre_carrera
""", conn)

    # =====================================================
    # 🎛 FILTROS GLOBALES (SIDEBAR)
    # =====================================================
    st.sidebar.subheader("🎛 Filtros Globales")

    # Filtro carrera
    carreras = ["Todas"] + sorted(df["nombre_carrera"].unique().tolist())
    carrera_sel = st.sidebar.selectbox("Filtrar por Carrera", carreras)

    # Filtro edad
    edad_min, edad_max = st.sidebar.slider(
        "Rango de Edad",
        int(df["edad"].min()),
        int(df["edad"].max()),
        (int(df["edad"].min()), int(df["edad"].max()))
    )

    # Filtro mínimo asistencia
    min_asistencia = st.sidebar.slider(
        "Mínimo de Asistencias",
        0,
        int(df["total_asistencias"].max()),
        0
    )

    # =====================================================
    # APLICAR FILTROS
    # =====================================================
    df_filtrado = df.copy()

    if carrera_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["nombre_carrera"] == carrera_sel]

    df_filtrado = df_filtrado[
        (df_filtrado["edad"] >= edad_min) &
        (df_filtrado["edad"] <= edad_max) &
        (df_filtrado["total_asistencias"] >= min_asistencia)
    ]

    # =====================================================
    # KPIs
    # =====================================================
    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Estudiantes Filtrados", df_filtrado.shape[0])
    col2.metric("📊 Promedio Asistencia", round(df_filtrado["total_asistencias"].mean(), 1) if not df_filtrado.empty else 0)
    col3.metric("🎂 Edad Promedio", round(df_filtrado["edad"].mean(), 1) if not df_filtrado.empty else 0)

    st.divider()

    # =====================================================
    # 🔝 GRÁFICOS SUPERIORES
    # =====================================================
    colA, colB, colC = st.columns(3)

    with colA:
        st.subheader("📈 Edad vs Asistencia")
        fig1, ax1 = plt.subplots(figsize=(5,4))
        sns.scatterplot(data=df_filtrado, x="edad", y="total_asistencias", ax=ax1)
        st.pyplot(fig1)

    with colB:
        st.subheader("🏆 Top 10 Mayor")
        top10 = df_filtrado.sort_values(by="total_asistencias", ascending=False).head(10)
        fig2, ax2 = plt.subplots(figsize=(5,4))
        sns.barplot(data=top10, x="total_asistencias", y="nombre", ax=ax2)
        st.pyplot(fig2)

    with colC:
        st.subheader("⚠️ Top 10 Menor")
        bottom10 = df_filtrado.sort_values(by="total_asistencias", ascending=True).head(10)
        fig3, ax3 = plt.subplots(figsize=(5,4))
        sns.barplot(data=bottom10, x="total_asistencias", y="nombre", ax=ax3)
        st.pyplot(fig3)

    st.divider()

    # =====================================================
    # 🔽 CONSULTA INDIVIDUAL
    # =====================================================
    col_left, col_right = st.columns(2)

    with col_left:

        st.subheader("🎓 Promedio por Carrera (Filtrado)")

        promedio_carrera = df_filtrado.groupby("nombre_carrera")["total_asistencias"].mean().reset_index()

        fig_carr, ax_carr = plt.subplots(figsize=(6,4))
        sns.barplot(data=promedio_carrera, x="total_asistencias", y="nombre_carrera", ax=ax_carr)
        st.pyplot(fig_carr)

    with col_right:

        st.subheader("👤 Asistencia por Estudiante")

        if not df_filtrado.empty:

            estudiante_sel = st.selectbox(
                "Selecciona un estudiante",
                df_filtrado["nombre"]
            )

            id_est = df_filtrado[df_filtrado["nombre"] == estudiante_sel]["id_estudiante"].values[0]

            asistencias_ind = pd.read_sql("""
                SELECT Fecha
                FROM asistencias
                WHERE Id_estudiante = %s
                ORDER BY Fecha
            """, conn, params=(int(id_est),))

            if not asistencias_ind.empty:

                asistencias_ind["Fecha"] = pd.to_datetime(asistencias_ind["Fecha"])
                asistencias_ind["Año-Mes"] = asistencias_ind["Fecha"].dt.to_period("M")

                conteo_mensual = asistencias_ind.groupby("Año-Mes").size().reset_index(name="Total")
                conteo_mensual["Año-Mes"] = conteo_mensual["Año-Mes"].astype(str)

                fig_est, ax_est = plt.subplots(figsize=(6,4))
                sns.lineplot(data=conteo_mensual, x="Año-Mes", y="Total", marker="o", ax=ax_est)
                plt.xticks(rotation=45)
                st.pyplot(fig_est)

                st.metric("📌 Total Asistencias", len(asistencias_ind))

    conn.close()
# =====================================================
# 📚 DOCUMENTACIÓN
# =====================================================

elif menu == "📚 Documentación":

    st.title("📚 Documentación Técnica del Proyecto")

    tab1, tab2, tab3 = st.tabs(["📦 Base de Datos", "📊 Modelo Analítico", "⚙️ Tecnologías"])

    # =====================================================
    # BASE DE DATOS
    # =====================================================
    with tab1:
        st.markdown("""
        ## 📦 Modelo Relacional

        El sistema está basado en un modelo relacional normalizado compuesto por:

        ### Tablas Principales

        - **estudiantes**
            - id_estudiante (PK)
            - Primer_nombre
            - Primer_apellido
            - edad

        - **carreras**
            - id_carrera (PK)
            - nombre_carrera

        - **estudiantes_carreras**
            - id_estudiante (FK)
            - id_carrera (FK)

        - **asistencias**
            - Id_asistencia (PK)
            - Fecha
            - Id_estudiante (FK)

        ### Relaciones

        - Un estudiante puede pertenecer a múltiples carreras.
        - Un estudiante puede tener múltiples registros de asistencia.
        - La relación muchos-a-muchos entre estudiantes y carreras se maneja mediante la tabla intermedia `estudiantes_carreras`.

        El modelo permite realizar análisis segmentados por carrera, edad y nivel de asistencia.
        """)

    # =====================================================
    # MODELO ANALÍTICO
    # =====================================================
    with tab2:
        st.markdown("""
        ## 📊 Enfoque Analítico

        El dashboard implementa:

        ### 🔹 KPIs Principales
        - Total de estudiantes
        - Promedio general de asistencia
        - Edad promedio

        ### 🔹 Análisis Exploratorio
        - Relación entre edad y asistencia
        - Identificación de estudiantes con mayor y menor compromiso
        - Tendencia mensual individual

        ### 🔹 Segmentación Dinámica
        - Filtros globales por:
            - Carrera
            - Rango de edad
            - Nivel mínimo de asistencia

        ### 🔹 Métricas Derivadas
        - Promedio de asistencia por carrera
        - Conteo mensual de asistencias
        - Ranking de desempeño

        Este enfoque permite detectar patrones de comportamiento académico y posibles riesgos de deserción.
        """)

    # =====================================================
    # TECNOLOGÍAS
    # =====================================================
    with tab3:
        st.markdown("""
        ## ⚙️ Tecnologías Utilizadas

        - **Python 3**
        - **Streamlit** (Dashboard interactivo)
        - **MySQL** (Base de datos relacional)
        - **Pandas** (Manipulación de datos)
        - **Seaborn & Matplotlib** (Visualización)
        - **SQL Joins y Agregaciones** (Modelo analítico)

        ## 🏗 Arquitectura

        - Separación de conexión en módulo `database.connection`
        - Consultas relacionales con INNER JOIN y LEFT JOIN
        - Filtros globales aplicados sobre DataFrame principal
        - Visualización modular organizada por secciones

        El sistema fue diseñado siguiendo buenas prácticas de análisis de datos y visualización ejecutiva.
        """)
