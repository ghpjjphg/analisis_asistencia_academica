# 🎓 Sistema Inteligente de Riesgo Académico y Predicción de Deserción

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Machine Learning](https://img.shields.io/badge/ML-Logistic%20Regression-green)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Colab](https://img.shields.io/badge/Google-Colab-yellow)
![Status](https://img.shields.io/badge/Status-Activo-success)

Proyecto integral desarrollado para **Talento Tech**, que combina:

- 📊 Análisis Exploratorio de Datos (EDA)  
- 🤖 Machine Learning  
- 📈 Visualización interactiva con Streamlit  
- 🧠 Modelamiento predictivo de riesgo académico y deserción  

---

## 🎯 Objetivo del Proyecto

Desarrollar un sistema inteligente capaz de:

- Detectar estudiantes en riesgo académico  
- Analizar patrones de asistencia y comportamiento  
- Predecir la deserción estudiantil  
- Apoyar la toma de decisiones estratégicas  

---

## 🧠 Enfoque del Proyecto

El proyecto se divide en dos componentes principales:

### 1️⃣ Análisis y Modelamiento (Google Colab)

- Generación de datos sintéticos realistas  
- Construcción de dataset analítico  
- Análisis exploratorio (EDA)  
- Entrenamiento de modelo predictivo  

---

### 2️⃣ Aplicación Interactiva (Streamlit)

- Dashboard analítico profesional  
- Visualización de KPIs  
- Clasificación de riesgo en tiempo real  
- Predicción individual de estudiantes  

---

## 🧩 Modelo de Datos

Se construyen múltiples tablas:

- **ESTUDIANTES** → Datos demográficos y socioeconómicos  
- **ASISTENCIA** → Registro diario  
- **ACADEMICO** → Rendimiento académico  
- **COMPORTAMIENTO** → Uso de plataforma  
- **DATA_FINAL** → Dataset consolidado  

---

## 🔥 Variables Clave

- Edad, género, ciudad  
- Estrato socioeconómico  
- Apoyo familiar  
- Tasa de asistencia  
- Promedio académico  
- Materias reprobadas  
- Logins, tiempo en plataforma, interacciones  

---

## ⚙️ Ingeniería de Datos

- Generación de datos sintéticos realistas  
- Simulación de deterioro en asistencia  
- Creación de variables derivadas:
  - Riesgo económico  
  - Racha de fallas  
- Integración de múltiples fuentes  

---

## 📊 Análisis Exploratorio (EDA)

- Distribución de deserción  
- Asistencia vs deserción  
- Promedio vs deserción  
- Mapa de correlación  

---

## 🤖 Modelo Predictivo

### Modelo utilizado:
- **Regresión Logística**

### Variables:
- Edad  
- Asistencia  
- Variables académicas  
- Variables de comportamiento  

### Variable objetivo:
- `desercion` (1 = Sí, 0 = No)

---

## 📈 Evaluación del Modelo

- Matriz de confusión  
- Precisión (Accuracy)  
- Curva ROC  
- AUC  
- Importancia de variables  

---

## 🚀 Aplicación Streamlit

### 🏠 Panel de Inicio
- Presentación del sistema  
- Explicación del flujo  

---

### 📊 Panel Analítico Experto

- KPIs:
  - Total estudiantes  
  - Promedio asistencia  
  - Casos de alto riesgo  

- Estadísticos:
  - Media, mediana, desviación estándar  
  - Varianza y coeficiente de variación  

- Visualizaciones:
  - Histograma con curva normal  
  - Boxplot  

- Interpretación automática  
- Tabla detallada  

---

### 🤖 Panel Predictivo

- Precisión del modelo  
- Matriz de confusión  
- Predicción individual  
- Distribución de probabilidades  
- Ranking de riesgo por carrera  
- Identificación de carrera crítica  

---

## 🧠 Lógica del Sistema

1. Recolección / generación de datos  
2. Cálculo de asistencia  
3. Generación de **Risk Score**  
4. Clasificación por percentiles  
5. Entrenamiento del modelo  
6. Predicción de riesgo  

---

## 🗄️ Exportación de Datos

- CSV → `DATA_FINAL.csv`  
- SQLite → `data_estudiantes.db`  

---

## 🏗️ Tecnologías Utilizadas

- Python  
- Streamlit  
- Pandas  
- NumPy  
- Seaborn  
- Matplotlib  
- Scikit-learn  
- MySQL / SQLite  
- Google Colab  

---

## 👥 Autores

- 👨‍💻 **Juan Pablo Henao**  
- 👩‍💻 **María Ángela Arrieta**  
- 👨‍💻 **Javier Rivera Vielmas**
