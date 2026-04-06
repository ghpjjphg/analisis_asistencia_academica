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
    page_title="Sistema Predictivo de Riesgo Académico",
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
# PREPARACIÓN DE RIESGO BASE
# =====================================================

def preparar_datos(df):

    min_val = df["total_asistencias"].min()
    max_val = df["total_asistencias"].max()

    df["risk_score"] = 100 - (
        (df["total_asistencias"] - min_val) /
        (max_val - min_val + 1e-5) * 100
    )

    q3 = df["risk_score"].quantile(0.75)

    df["alto_riesgo"] = (df["risk_score"] >= q3).astype(int)

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
    ["📊 Dashboard Predictivo"]
)

# =====================================================
# DASHBOARD
# =====================================================

if menu == "📊 Dashboard Predictivo":

    st.title("🤖 Sistema Predictivo de Riesgo Académico")

    df = cargar_datos()
    df = preparar_datos(df)

    modelo, acc, matriz = entrenar_modelo(df)

    # ================= KPIs =================

    col1, col2 = st.columns(2)
    col1.metric("🎯 Precisión del Modelo", f"{round(acc*100,2)}%")
    col2.metric("👥 Total Estudiantes", df.shape[0])

    st.divider()

    # ================= MATRIZ DE CONFUSIÓN =================

    st.subheader("📊 Matriz de Confusión")

    fig1, ax1 = plt.subplots()
    sns.heatmap(matriz, annot=True, fmt="d", cmap="Blues", ax=ax1)
    ax1.set_xlabel("Predicción")
    ax1.set_ylabel("Real")
    st.pyplot(fig1)

    st.divider()

    # ================= PROBABILIDAD INDIVIDUAL =================

    st.subheader("🔮 Predicción Individual")

    estudiante_sel = st.selectbox(
        "Selecciona un estudiante",
        df["nombre"]
    )

    estudiante = df[df["nombre"] == estudiante_sel]

    X_ind = estudiante[["edad", "total_asistencias"]]
    prob = modelo.predict_proba(X_ind)[0][1]

    riesgo_label = "🔴 Alto Riesgo" if prob >= 0.5 else "🟢 Bajo/Medio Riesgo"

    colA, colB = st.columns(2)
    colA.metric("Probabilidad de Alto Riesgo", f"{round(prob*100,2)}%")
    colB.metric("Clasificación Predicha", riesgo_label)

    st.divider()

    # ================= DISTRIBUCIÓN =================

    st.subheader("📈 Distribución de Probabilidades")

    probs = modelo.predict_proba(df[["edad","total_asistencias"]])[:,1]

    fig2, ax2 = plt.subplots()
    sns.histplot(probs, bins=15, kde=True, ax=ax2)
    st.pyplot(fig2)
