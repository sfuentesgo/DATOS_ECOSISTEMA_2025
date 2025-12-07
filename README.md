# 🏙️ Bogotá Inteligente: Explorador del Territorio

> **Propuesta Reto: Datos al Ecosistema 2025** > *Línea Temática: Uso del suelo y planificación territorial*

<div align="center">
  <img src="BACK_END/logo.png" alt="Logo Bogotá Inteligente" width="500">
</div>

---

## 💡 Descripción del Proyecto

**Explorador Inteligente del Territorio Bogotano** es una plataforma de micro-análisis urbano diseñada para democratizar el acceso a la "inteligencia territorial". 

A diferencia de los visores tradicionales, esta herramienta no solo muestra mapas, sino que **cruza, procesa e interpreta** datos abiertos en tiempo real. Permite a ciudadanos, ediles e inversionistas seleccionar una manzana específica y obtener un diagnóstico automático sobre:
- 🏗️ Normativa urbana (POT).
- 🚇 Conectividad y transporte.
- 🏫 Cobertura educativa.
- 🛡️ Perfil de seguridad.
- 🌳 Equipamento de zonas verdes
- 👨‍⚕️ Unidades medicas relacionadas en el sector


El resultado final es una **Ficha Técnica Ejecutiva (HTML)** descargable, lista para la toma de decisiones.

---

## 🚀 Funcionalidades Clave

1.  **📍 Geolocalización Inteligente:** Selección interactiva de puntos de interés con radios de análisis dinámicos (300m, 500m, 800m).
2.  **🔄 Cruce Espacial (Spatial Join):** Algoritmo en tiempo real que integra la capa de Manzanas Catastrales con las Áreas de Actividad del POT para determinar la normativa exacta.
3.  **📊 Cálculo de KPIs:** Indicadores automáticos de cobertura (ej. % de estaciones de TM cercanas vs. total localidad).
4.  **📑 Generador de Reportes:** Motor de renderizado que captura "fotos" de los mapas y gráficas para generar un informe HTML autocontenido (sin dependencias externas) y profesional.


---

## 📂 Fuentes de Datos (Datos Abiertos)

Este proyecto integra y estandariza los siguientes conjuntos de datos del portal **Datos.gov.co**:

| Dataset | Fuente | Uso en la App |
| :--- | :--- | :--- |
| **Manzanas Catastrales** | Catastro Distrital | Geometría base y valor del m². |
| **Áreas de Actividad (POT)** | Secretaría de Planeación | Determinación de usos del suelo permitidos. |
| **Estaciones TransMilenio** | TransMilenio S.A. | Cálculo de accesibilidad y transporte. |
| **Colegios Bogotá** | Secretaría de Educación | Análisis de cobertura educativa. |
| **Delitos de Alto Impacto** | Secretaría de Seguridad | Contexto de seguridad y riesgos. |

---
## 🔗 enlace directo a la aplicacion web

https://bogota-inteligente.streamlit.app/

## 🛠️ Instalación y Uso Local

Sigue estos pasos para correr el proyecto en tu máquina local:

### 1. Clonar el repositorio
```bash
git clone https://github.com/andres-fuentex/CONCURSO
cd bogota-inteligente

### 2. Entorno virtual recomendado
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

### 3. Instalar dependencias
pip install -r requirements.txt
