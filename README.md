# 🏙️ Bogotá Visible: Inteligencia Territorial

> **Herramienta de microanálisis urbano y Gemelo Digital para la toma de decisiones ciudadanas.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bogota-inteligente.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Cesium](https://img.shields.io/badge/CesiumJS-3D-orange)

## 📖 Descripción del Proyecto

**Bogotá Visible** es una plataforma interactiva diseñada para democratizar el acceso a los datos urbanos. Permite a ciudadanos, ediles y planificadores analizar el territorio de Bogotá a nivel de barrio, integrando normativas (POT), seguridad, movilidad y equipamientos en una sola interfaz.

El proyecto conecta un **Dashboard Analítico** (Streamlit) con un **Gemelo Digital 3D** (CesiumJS) para ofrecer una experiencia inmersiva del territorio.

## 🚀 Características Principales

1.  **Microanálisis Territorial:** Selecciona cualquier punto de Bogotá y define un radio de influencia (300m - 2km).
2.  **Multidimensionalidad:** Cruce de datos de:
    * 🚌 Movilidad (Transmilenio/SITP)
    * 🏫 Educación (Colegios Oficiales y Privados)
    * 🏥 Salud (Red Adscrita)
    * 🌳 Espacio Público
    * 🛡️ Seguridad (Top 3 delitos por zona)
3.  **Gemelo Digital 3D:** Visualización volumétrica del sector analizado utilizando **CesiumJS** y fotogrametría satelital.
4.  **Diagnóstico Automático:** Generación de informes ejecutivos en tiempo real.

## 🛠️ Arquitectura Técnica

El proyecto utiliza una arquitectura híbrida:

* **Back-End / Analítica:** Python + Streamlit + Geopandas para el procesamiento geoespacial de los datos abiertos.
* **Front-End 3D:** HTML5 + Javascript + Cesium Ion para la renderización del Gemelo Digital.
* **Datos:** Integración de datasets oficiales de Datos Abiertos Bogotá (Secretaría de Educación, Transmilenio, IDECA, Secretaría de Seguridad).

## 📂 Estructura del Repositorio

* `app_bogota_inteligente.py`: Aplicación principal (Streamlit).
* `docs/`: Código fuente del visor 3D (Cesium) desplegado en GitHub Pages.
* `DATOS_LIMPIOS/`: Insumos geoespaciales (GeoJSON) procesados y optimizados.
* `notebooks/`: Procesos ETL y limpieza de datos (EDA).

## 👥 Equipo (Proponentes)

* **Sergio Andrés Fuentes** - *Líder Técnico & Desarrollo*
* **Miguel Alejandro Gonzalez** - *Estrategia*
* **Sandra Yazmin Torres** - *Analisis de datos*

---
*Proyecto desarrollado para el Reto de Datos Abiertos 2025 - Temática libre: Uso del suelo y planificación territorial.*
