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
    ["🏠 Inicio", "📊 Panel Analítico", "🤖 Panel Predictivo"]
)

if st.sidebar.button("🔄 Recargar Datos"):
    st.cache_data.clear()
    st.cache_resource.clear()

# =====================================================
# INICIO (MEJORADO 🚀)
# =====================================================

if menu == "🏠 Inicio":

    st.markdown("""
    <h1 style='text-align: center; font-size: 3em;'>
    🎓 Sistema Inteligente de Riesgo Académico y Deserción
    </h1>

    <p style='text-align: center; font-size: 1.2em;'>
    Plataforma avanzada que integra <b>Analítica de Datos, Machine Learning y Visualización Interactiva</b> 
    para la detección temprana del riesgo académico.
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.markdown("""
    ### 📊 Analítica Avanzada
    - Análisis Exploratorio (EDA)
    - Estadísticos descriptivos
    - Detección de patrones
    """)

    col2.markdown("""
    ### 🤖 Machine Learning
    - Regresión Logística
    - Predicción de riesgo
    - Probabilidad en tiempo real
    """)

    col3.markdown("""
    ### 🎯 Toma de Decisiones
    - Identificación de estudiantes críticos
    - Análisis por carrera
    - Soporte estratégico
    """)

    st.divider()

    st.subheader("📌 ¿Qué hace este sistema?")

    st.markdown("""
    ✔ Detecta estudiantes en riesgo académico  
    ✔ Analiza asistencia y rendimiento  
    ✔ Aplica modelos predictivos  
    ✔ Genera información estratégica  
    """)

    st.divider()

    st.subheader("⚙️ ¿Cómo funciona?")

    st.markdown("""
    1️⃣ Recolección de datos  
    2️⃣ Análisis exploratorio  
    3️⃣ Cálculo de risk score  
    4️⃣ Clasificación de riesgo  
    5️⃣ Predicción con Machine Learning  
    """)

    st.divider()

    st.subheader("👥 Integrantes")

    colA, colB, colC = st.columns(3)

    colA.markdown("**Juan Pablo Henao**")
    colB.markdown("**María Ángela Arrieta**")
    colC.markdown("**Javier Rivera Vielmas**")
    st.divider()

    st.subheader("📓 Notebook del Proyecto")
    
    st.markdown("""
    Accede al análisis completo (EDA, generación de datos y modelo predictivo) desarrollado en Google Colab.
    """)
    
    st.link_button(
        "🚀 Abrir Cuaderno en Colab",
        "https://colab.research.google.com/drive/1o5IyGvpxgEmbH5ltBxay88vK9xyCr4X8?usp=sharing"
    )

    st.divider()

    st.markdown("""
    <h3 style='text-align: center;'>
    🚀 Explora el sistema desde el menú lateral
    </h3>
    """, unsafe_allow_html=True)

# =====================================================
# PANEL ANALÍTICO
# =====================================================

elif menu == "📊 Panel Analítico":

    st.title("📊 Panel Analítico Estadístico")

    df = cargar_datos()
    df = calcular_risk_score(df)
    df = clasificacion_percentil(df)

    # =====================================================
    # KPIs BÁSICOS
    # =====================================================

    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total Estudiantes", df.shape[0])
    col2.metric("📊 Asistencia Promedio", round(df["total_asistencias"].mean(),2))
    col3.metric("🚨 Casos Alto Riesgo", df["alto_riesgo"].sum())

    st.divider()

    # =====================================================
    # ESTADÍSTICOS DESCRIPTIVOS PROFESIONALES
    # =====================================================

    st.subheader("📈 Estadísticos Descriptivos")

    media = df["total_asistencias"].mean()
    mediana = df["total_asistencias"].median()
    std = df["total_asistencias"].std()
    varianza = df["total_asistencias"].var()
    q1 = df["total_asistencias"].quantile(0.25)
    q3 = df["total_asistencias"].quantile(0.75)
    coef_var = std / media if media != 0 else 0

    colA, colB, colC = st.columns(3)
    colA.metric("Media", round(media,2))
    colB.metric("Mediana", round(mediana,2))
    colC.metric("Desviación Estándar", round(std,2))

    colD, colE, colF = st.columns(3)
    colD.metric("Varianza", round(varianza,2))
    colE.metric("Q1 (25%)", round(q1,2))
    colF.metric("Q3 (75%)", round(q3,2))

    st.metric("Coeficiente de Variación", round(coef_var,2))

    st.divider()

    # =====================================================
    # HISTOGRAMA + CAMPANA DE GAUSS
    # =====================================================

    st.subheader("📊 Distribución con Campana de Gauss")

    datos = df["total_asistencias"]

    fig1, ax1 = plt.subplots(figsize=(8,5))
    sns.histplot(datos, bins=15, stat="density", kde=False, ax=ax1)

    # Curva normal
    x = np.linspace(datos.min(), datos.max(), 100)
    y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - media) / std)**2)

    ax1.plot(x, y, linewidth=3)
    ax1.set_title("Distribución de Asistencias con Curva Normal")
    st.pyplot(fig1)

    st.divider()

    # =====================================================
    # BOXPLOT PROFESIONAL
    # =====================================================

    st.subheader("📦 Análisis de Outliers (Boxplot)")

    fig2, ax2 = plt.subplots(figsize=(6,4))
    sns.boxplot(x=df["total_asistencias"], ax=ax2)
    st.pyplot(fig2)

    st.divider()

    # =====================================================
    # INTERPRETACIÓN AUTOMÁTICA
    # =====================================================

    st.subheader("🧠 Interpretación Estadística Automática")

    interpretacion = ""

    if abs(media - mediana) < 1:
        interpretacion += "La distribución es aproximadamente simétrica.\n\n"
    elif media > mediana:
        interpretacion += "La distribución presenta sesgo positivo (cola hacia la derecha).\n\n"
    else:
        interpretacion += "La distribución presenta sesgo negativo (cola hacia la izquierda).\n\n"

    if coef_var < 0.3:
        interpretacion += "La variabilidad es baja (datos homogéneos).\n\n"
    elif coef_var < 0.6:
        interpretacion += "La variabilidad es moderada.\n\n"
    else:
        interpretacion += "Existe alta dispersión en los datos.\n\n"

    st.info(interpretacion)

    st.divider()

    # =====================================================
    # TABLA DETALLADA
    # =====================================================

    st.subheader("📋 Tabla Detallada")

    st.dataframe(
        df[["nombre","nombre_carrera","total_asistencias","risk_score","nivel_riesgo"]],
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
