import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from database.connection import get_connection
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score

st.set_page_config(
    page_title="Sistema Inteligente de Riesgo Académico",
    layout="wide"
)

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
# RISK SCORE DINÁMICO
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
    df["alto_riesgo"] = (df["nivel_riesgo"]=="🔴 Alto Riesgo").astype(int)
    return df

# =====================================================
# MODELO PREDICTIVO
# =====================================================

@st.cache_resource
def entrenar_modelo(df):

    X = df[["edad", "total_asistencias"]]
    y = df["alto_riesgo"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    modelo = LogisticRegression()
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    matriz = confusion_matrix(y_test, y_pred)

    return modelo, acc, matriz

# =====================================================
# MENÚ
# =====================================================

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "📊 Panel Analítico Experto", "🤖 Panel Predictivo"]
)

if st.sidebar.button("🔄 Recargar Datos"):
    st.cache_data.clear()
    st.cache_resource.clear()

# =====================================================
# INICIO
# =====================================================

if menu == "🏠 Inicio":

    st.title("🎓 Sistema Inteligente de Alerta Temprana Académica")
    st.markdown("""
    Sistema integral que combina:

    ✔ Análisis descriptivo avanzado  
    ✔ Score dinámico de riesgo  
    ✔ Clasificación estadística  
    ✔ Modelo predictivo de Machine Learning  
    ✔ Análisis estratégico por carrera  

    Diseñado como Early Warning System universitario.
    """)

# =====================================================
# PANEL ANALÍTICO EXPERTO
# =====================================================

elif menu == "📊 Panel Analítico Experto":

    st.title("📊 Panel Analítico de Riesgo")

    df = cargar_datos()
    df = calcular_risk_score(df)
    df = clasificacion_percentil(df)

    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total Estudiantes", df.shape[0])
    col2.metric("📊 Asistencia Promedio", round(df["total_asistencias"].mean(),1))
    col3.metric("🚨 Alto Riesgo", df["alto_riesgo"].sum())

    st.divider()

    st.subheader("📈 Distribución del Risk Score")

    fig1, ax1 = plt.subplots(figsize=(7,4))
    sns.histplot(df["risk_score"], bins=15, kde=True, ax=ax1)
    st.pyplot(fig1)

    st.divider()

    st.subheader("🏆 Ranking Estratégico")

    ranking = df.sort_values("risk_score", ascending=False)

    st.dataframe(
        ranking[["nombre","nombre_carrera","total_asistencias","risk_score","nivel_riesgo"]],
        use_container_width=True
    )

# =====================================================
# PANEL PREDICTIVO
# =====================================================

elif menu == "🤖 Panel Predictivo":

    st.title("🤖 Modelo Predictivo de Alto Riesgo")

    df = cargar_datos()
    df = calcular_risk_score(df)
    df = clasificacion_percentil(df)

    modelo, acc, matriz = entrenar_modelo(df)

    col1, col2 = st.columns(2)
    col1.metric("🎯 Precisión del Modelo", f"{round(acc*100,2)}%")
    col2.metric("⚠️ Casos Alto Riesgo", df["alto_riesgo"].sum())

    st.divider()

    st.subheader("📊 Matriz de Confusión")

    fig2, ax2 = plt.subplots()
    sns.heatmap(matriz, annot=True, fmt="d", cmap="Blues", ax=ax2)
    ax2.set_xlabel("Predicción")
    ax2.set_ylabel("Real")
    st.pyplot(fig2)

    st.divider()

    st.subheader("🔮 Predicción Individual")

    estudiante_sel = st.selectbox(
        "Selecciona un estudiante",
        df["nombre"]
    )

    estudiante = df[df["nombre"]==estudiante_sel]

    X_ind = estudiante[["edad","total_asistencias"]]
    prob = modelo.predict_proba(X_ind)[0][1]

    label = "🔴 Alto Riesgo" if prob>=0.5 else "🟢 Bajo/Medio"

    colA, colB = st.columns(2)
    colA.metric("Probabilidad Alto Riesgo", f"{round(prob*100,2)}%")
    colB.metric("Clasificación Predicha", label)

    st.divider()

    st.subheader("📈 Distribución de Probabilidades")

    probs = modelo.predict_proba(df[["edad","total_asistencias"]])[:,1]

    fig3, ax3 = plt.subplots()
    sns.histplot(probs, bins=15, kde=True, ax=ax3)
    st.pyplot(fig3)

    # =====================================================
    # RIESGO POR CARRERA
    # =====================================================

    st.divider()
    st.subheader("🏫 Análisis Predictivo de Riesgo por Carrera")

    df["prob_alto_riesgo"] = modelo.predict_proba(
        df[["edad","total_asistencias"]]
    )[:,1]

    resumen_carrera = df.groupby("nombre_carrera").agg(
        estudiantes=("nombre","count"),
        promedio_probabilidad=("prob_alto_riesgo","mean"),
        casos_alto_riesgo=("alto_riesgo","sum")
    ).reset_index()

    resumen_carrera["porcentaje_alto_riesgo"] = (
        resumen_carrera["casos_alto_riesgo"] /
        resumen_carrera["estudiantes"] * 100
    )

    resumen_carrera = resumen_carrera.sort_values(
        "promedio_probabilidad",
        ascending=False
    )

    carrera_critica = resumen_carrera.iloc[0]

    colX, colY = st.columns(2)
    colX.metric("🏆 Carrera con Mayor Riesgo",
                carrera_critica["nombre_carrera"])
    colY.metric("📉 Probabilidad Promedio",
                f"{round(carrera_critica['promedio_probabilidad']*100,2)}%")

    st.divider()

    st.subheader("📊 Ranking de Riesgo por Carrera")

    fig4, ax4 = plt.subplots(figsize=(8,5))
    sns.barplot(
        data=resumen_carrera,
        x="promedio_probabilidad",
        y="nombre_carrera",
        ax=ax4
    )
    ax4.set_xlabel("Probabilidad Promedio de Alto Riesgo")
    ax4.set_ylabel("Carrera")
    st.pyplot(fig4)

    st.divider()

    st.subheader("📋 Resumen Estratégico por Carrera")

    st.dataframe(
        resumen_carrera,
        use_container_width=True
    )
