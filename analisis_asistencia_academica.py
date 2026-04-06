import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from database.connection import get_connection

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Sistema de Análisis de Asistencia Académica",
    layout="wide"
)

# =====================================================
# ESTILOS PERSONALIZADOS
# =====================================================

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

# =====================================================
# FUNCIÓN CACHEADA PARA CARGAR DATOS
# =====================================================

@st.cache_data
def cargar_datos():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT 
                e.id_estudiante,
                CONCAT(e.Primer_nombre,' ',e.Primer_apellido) as nombre,
                e.Edad AS edad,
                c.Nombre AS nombre_carrera,
                COUNT(a.Id_asistencia) as total_asistencias
            FROM estudiantes e
            INNER JOIN estudiantes_carreras ec
                ON e.Id_estudiante = ec.Id_estudiante
            INNER JOIN carreras c
                ON ec.Id_carrera = c.Id_carrera
            LEFT JOIN asistencias a
                ON e.Id_estudiante = a.Id_estudiante
            GROUP BY 
                e.Id_estudiante,
                e.Primer_nombre,
                e.Primer_apellido,
                e.Edad,
                c.Nombre
        """, conn)

        conn.close()
        return df

    except Exception as e:
        st.error("Error al conectar con la base de datos.")
        st.stop()

# =====================================================
# MENÚ LATERAL
# =====================================================

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "📊 Panel Analítico", "📚 Documentación"]
)

# Botón para recargar datos
if st.sidebar.button("🔄 Recargar Datos"):
    st.cache_data.clear()
    st.success("Datos recargados correctamente.")

# =====================================================
# LANDING PAGE
# =====================================================

if menu == "🏠 Inicio":

    st.title("📊 Sistema de Análisis de Asistencia Académica")
    st.subheader("Desarrollado por JUAN PABLO HENAO Y MARIA ANGELA ARRIETA")

    try:
        imagen = Image.open("ASISTENCIA.png")
        st.image(imagen, width=250)
    except:
        pass

    st.markdown("""
    ### 🎯 Objetivo

    Este sistema permite analizar el comportamiento de asistencia de estudiantes universitarios 
    mediante consultas SQL y visualización de datos.

    ### 📈 Capacidades Analíticas

    - Promedio de asistencia
    - Ranking de compromiso
    - Análisis por carrera
    - Identificación de riesgo académico
    - Tendencia mensual individual

    ---
    Presiona **Panel Analítico** en el menú para comenzar.
    """)

# =====================================================
# PANEL ANALÍTICO
# =====================================================

elif menu == "📊 Panel Analítico":

    st.title("📊 Panel Analítico")

    df = cargar_datos()

    # =====================================================
    # FILTROS
    # =====================================================

    st.sidebar.subheader("🎛 Filtros Globales")

    carreras = ["Todas"] + sorted(df["nombre_carrera"].unique().tolist())
    carrera_sel = st.sidebar.selectbox("Filtrar por Carrera", carreras)

    edad_min, edad_max = st.sidebar.slider(
        "Rango de Edad",
        int(df["edad"].min()),
        int(df["edad"].max()),
        (int(df["edad"].min()), int(df["edad"].max()))
    )

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

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    # =====================================================
    # KPIs
    # =====================================================

    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Estudiantes", df_filtrado.shape[0])
    col2.metric("📊 Promedio Asistencia", round(df_filtrado["total_asistencias"].mean(), 1))
    col3.metric("🎂 Edad Promedio", round(df_filtrado["edad"].mean(), 1))

    st.divider()

    # =====================================================
    # GRÁFICOS
    # =====================================================

    colA, colB, colC = st.columns(3)

    with colA:
        st.subheader("📈 Edad vs Asistencia")
        fig1, ax1 = plt.subplots(figsize=(5,4))
        sns.scatterplot(
            data=df_filtrado,
            x="edad",
            y="total_asistencias",
            hue="nombre_carrera",
            alpha=0.7,
            ax=ax1
        )
        st.pyplot(fig1)

    with colB:
        st.subheader("🏆 Top 10 Mayor Asistencia")
        top10 = df_filtrado.sort_values(by="total_asistencias", ascending=False).head(10)
        fig2, ax2 = plt.subplots(figsize=(5,4))
        sns.barplot(data=top10, x="total_asistencias", y="nombre", ax=ax2)
        st.pyplot(fig2)

    with colC:
        st.subheader("⚠️ Top 10 Menor Asistencia")
        bottom10 = df_filtrado.sort_values(by="total_asistencias", ascending=True).head(10)
        fig3, ax3 = plt.subplots(figsize=(5,4))
        sns.barplot(data=bottom10, x="total_asistencias", y="nombre", ax=ax3)
        st.pyplot(fig3)

    st.divider()

    # =====================================================
    # PROMEDIO POR CARRERA
    # =====================================================

    col_left, col_right = st.columns(2)

    with col_left:

        st.subheader("🎓 Promedio por Carrera")

        promedio_carrera = df_filtrado.groupby("nombre_carrera")["total_asistencias"].mean().reset_index()

        fig_carr, ax_carr = plt.subplots(figsize=(6,4))
        sns.barplot(data=promedio_carrera, x="total_asistencias", y="nombre_carrera", ax=ax_carr)
        st.pyplot(fig_carr)

    with col_right:

        st.subheader("👤 Tendencia Individual")

        estudiante_sel = st.selectbox(
            "Selecciona un estudiante",
            df_filtrado["nombre"]
        )

        id_est = df_filtrado[df_filtrado["nombre"] == estudiante_sel]["id_estudiante"].values[0]

        conn = get_connection()

        asistencias_ind = pd.read_sql("""
            SELECT Fecha
            FROM asistencias
            WHERE Id_estudiante = %s
            ORDER BY Fecha
        """, conn, params=(int(id_est),))

        conn.close()

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

# =====================================================
# DOCUMENTACIÓN
# =====================================================

elif menu == "📚 Documentación":

    st.title("📚 Documentación Técnica")

    st.markdown("""
    ### 📦 Modelo Relacional

    - estudiantes
    - carreras
    - estudiantes_carreras
    - asistencias

    ### 📊 Enfoque Analítico

    - KPIs estratégicos
    - Segmentación dinámica
    - Ranking de desempeño
    - Identificación de riesgo académico

    ### ⚙️ Tecnologías

    - Python
    - Streamlit
    - MySQL
    - Pandas
    - Seaborn
    - Matplotlib

    Proyecto diseñado bajo buenas prácticas de análisis y visualización ejecutiva.
    """)
