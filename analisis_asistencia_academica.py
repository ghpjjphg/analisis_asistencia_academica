import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from database.connection import get_connection

st.set_page_config(
    page_title="Sistema Experto de Alerta Temprana Académica",
    layout="wide"
)

# =====================================================
# ESTILOS PRO
# =====================================================

st.markdown("""
<style>
.stMetric {
    background-color: #FFFFFF;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS
# =====================================================

@st.cache_data
def cargar_datos():
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

# =====================================================
# FUNCIÓN DE SCORE INTELIGENTE
# =====================================================

def calcular_risk_score(df):
    min_val = df["total_asistencias"].min()
    max_val = df["total_asistencias"].max()

    df["risk_score"] = 100 - (
        (df["total_asistencias"] - min_val) /
        (max_val - min_val + 1e-5) * 100
    )

    return df

def clasificacion_percentil(df):
    q1 = df["risk_score"].quantile(0.25)
    q3 = df["risk_score"].quantile(0.75)

    def clasificar(score):
        if score >= q3:
            return "🔴 Alto Riesgo"
        elif score >= q1:
            return "🟡 Riesgo Medio"
        else:
            return "🟢 Bajo Riesgo"

    df["nivel_riesgo"] = df["risk_score"].apply(clasificar)
    return df

# =====================================================
# MENÚ
# =====================================================

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "📊 Sistema Experto"]
)

if st.sidebar.button("🔄 Recargar Datos"):
    st.cache_data.clear()

# =====================================================
# INICIO
# =====================================================

if menu == "🏠 Inicio":

    st.title("🎓 Sistema Experto de Alerta Temprana Académica")
    st.markdown("""
    Sistema inteligente basado en análisis estadístico y normalización.
    Permite detectar estudiantes en riesgo usando percentiles dinámicos.
    """)

# =====================================================
# SISTEMA EXPERTO
# =====================================================

elif menu == "📊 Sistema Experto":

    st.title("📊 Panel Inteligente de Riesgo")

    df = cargar_datos()
    df = calcular_risk_score(df)
    df = clasificacion_percentil(df)

    # ================= KPIs =================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Total Estudiantes", df.shape[0])
    col2.metric("📊 Asistencia Promedio", round(df["total_asistencias"].mean(),1))
    col3.metric("⚠️ Promedio Risk Score", round(df["risk_score"].mean(),1))

    alto = df[df["nivel_riesgo"]=="🔴 Alto Riesgo"].shape[0]
    col4.metric("🚨 Estudiantes Alto Riesgo", alto)

    st.divider()

    # ================= DISTRIBUCIÓN =================

    st.subheader("📈 Distribución del Risk Score")

    fig1, ax1 = plt.subplots(figsize=(7,4))
    sns.histplot(df["risk_score"], bins=15, kde=True, ax=ax1)
    st.pyplot(fig1)

    st.divider()

    # ================= RANKING =================

    st.subheader("🏆 Ranking Estratégico de Riesgo")

    ranking = df.sort_values("risk_score", ascending=False)

    st.dataframe(
        ranking[["nombre", "nombre_carrera", "total_asistencias", "risk_score", "nivel_riesgo"]],
        use_container_width=True
    )

    st.divider()

    # ================= EXPORTACIÓN =================

    st.subheader("📤 Exportar Alto Riesgo")

    alto_riesgo_df = df[df["nivel_riesgo"]=="🔴 Alto Riesgo"]

    csv = alto_riesgo_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Descargar lista de Alto Riesgo",
        data=csv,
        file_name='estudiantes_alto_riesgo.csv',
        mime='text/csv'
    )
