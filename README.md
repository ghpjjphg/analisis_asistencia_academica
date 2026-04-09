# 🎓 Sistema Inteligente de Riesgo Académico

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Machine Learning](https://img.shields.io/badge/ML-Logistic%20Regression-green)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Status](https://img.shields.io/badge/Status-Activo-success)

Aplicación desarrollada para el curso **Análisis de Datos - Talento Tech**, enfocada en la **detección temprana del riesgo académico** mediante análisis estadístico y modelos de Machine Learning.

---

## 🎯 Objetivo del Proyecto

Desarrollar un sistema inteligente capaz de:

- 📊 Analizar patrones de asistencia estudiantil  
- ⚠️ Detectar estudiantes en riesgo académico  
- 🤖 Predecir probabilidades de riesgo usando Machine Learning  
- 📈 Facilitar la toma de decisiones académicas  

---

## 🚀 Funcionalidades Principales

### 🏠 Panel de Inicio
- Presentación del sistema  
- Explicación del flujo de análisis  
- Beneficios estratégicos  

---

### 📊 Panel Analítico Experto

Incluye análisis estadístico completo:

- ✔ KPIs (Total estudiantes, promedio asistencia, alto riesgo)  
- ✔ Estadísticos descriptivos:
  - Media, mediana, desviación estándar  
  - Varianza y coeficiente de variación  
  - Percentiles (Q1 y Q3)  
- ✔ Visualizaciones:
  - Histograma con curva normal (Gauss)  
  - Boxplot (detección de outliers)  
- ✔ Interpretación automática de datos  
- ✔ Tabla detallada por estudiante  

---

### 🤖 Panel Predictivo (Machine Learning)

- Modelo de **Regresión Logística**  
- División de datos (train/test)  
- Métricas del modelo:
  - 🎯 Precisión (Accuracy)  
  - 📊 Matriz de confusión  
- Predicción individual por estudiante  
- Distribución de probabilidades  
- 📉 Ranking de riesgo por carrera  
- 🏆 Identificación de carrera más crítica  

---

## 🧠 Lógica del Sistema

El sistema sigue este flujo:

1. Recolección de datos desde MySQL  
2. Cálculo de asistencias por estudiante  
3. Generación de **Risk Score dinámico**  
4. Clasificación por percentiles:
   - 🔴 Alto riesgo  
   - 🟡 Riesgo medio  
   - 🟢 Bajo riesgo  
5. Entrenamiento del modelo predictivo  
6. Generación de predicciones  

---

## 🏗️ Tecnologías Utilizadas

- Python 3.11  
- Streamlit  
- Pandas  
- NumPy  
- Seaborn  
- Matplotlib  
- Scikit-learn  
- MySQL  
