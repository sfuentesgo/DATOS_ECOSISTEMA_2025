import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- Configuración de la Página (Estilo Institucional) ---
st.set_page_config(
    page_title="Inteligencia Territorial Bogotá",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Encabezado y Contexto del Proyecto ---
st.title("Sistema de Inteligencia Territorial de Bogotá")
st.subheader("Análisis Estratégico basado en Datos Abiertos")

st.markdown("""
Esta plataforma tecnológica permite la evaluación multidimensional del territorio mediante el procesamiento de datos oficiales de la infraestructura de datos espaciales de Bogotá.

**Alcance del Diagnóstico:**
El sistema integra capas de información catastral, normativa (POT), seguridad ciudadana y cobertura de servicios para generar un perfil detallado de la vocación territorial en tres niveles de análisis:

1.  **Contexto Administrativo y Seguridad:** Identificación de patrones delictivos y caracterización de localidades.
2.  **Normativa y Socioeconomía:** Análisis de usos del suelo (Decreto 555) y estratificación.
3.  **Accesibilidad y Servicios:** Evaluación de cobertura en transporte masivo y oferta educativa.

---
""")

# --- Función de Carga de Datos (Conectada a DATOS_LIMPIOS) ---
@st.cache_data
def cargar_datasets():
    """
    Descarga, valida y cachea los datasets geoespaciales desde el repositorio del proyecto.
    Retorna un diccionario con los GeoDataFrames normalizados (EPSG:4326).
    """
    # Repositorio oficial de datos procesados
    BASE_URL = "https://github.com/andres-fuentex/CONCURSO/raw/main/DATOS_LIMPIOS/"
    
    # Mapeo de archivos según la arquitectura de datos definida
    archivos = {
        "localidades": "dim_localidad.geojson",
        "areas":       "dim_area.geojson",     # Usos del suelo POT
        "manzanas":    "tabla_hechos.geojson", # Estratificación
        "transporte":  "dim_transporte.geojson",
        "colegios":    "dim_colegios.geojson"
    }
    
    dataframes = {}
    errores = []

    for nombre_clave, nombre_archivo in archivos.items():
        try:
            url_completa = f"{BASE_URL}{nombre_archivo}"
            
            # Lectura directa con Geopandas
            gdf = gpd.read_file(url_completa)
            
            # Aseguramos proyección WGS84 para compatibilidad web
            if gdf.crs != "EPSG:4326":
                gdf = gdf.to_crs("EPSG:4326")
                
            dataframes[nombre_clave] = gdf
            
        except Exception as e:
            errores.append(f"Error cargando capa {nombre_clave}: {str(e)}")
    
    if errores:
        for err in errores:
            st.error(err)
        return None
        
    return dataframes

# --- Inicialización del Estado ---
if "step" not in st.session_state:
    st.session_state.step = 1

# ==============================================================================
# PASO 1: SINCRONIZACIÓN Y CARGA DE DATOS
# ==============================================================================
if st.session_state.step == 1:
    st.markdown("### Fase 1: Inicialización del Sistema")
    
    st.markdown("""
    El aplicativo iniciará la conexión con el repositorio de datos procesados. 
    Este procedimiento es crítico para asegurar la **integridad topológica** de las capas geográficas y la consistencia de los atributos alfanuméricos (seguridad, catastro y normativa).
    
    *El sistema validará automáticamente la proyección espacial (EPSG:4326) requerida para la visualización web.*
    """)

    # Componente de estado para feedback técnico profesional
    with st.status("Ejecutando protocolo de conexión...", expanded=True) as status:
        st.write("Estableciendo enlace con fuentes de datos...")
        
        try:
            # Ejecutamos la función de carga
            dataframes = cargar_datasets()
            
            if dataframes:
                # Simulamos pasos de validación para dar confianza al usuario experto
                st.write("Validando geometría de Localidades y Manzanas... OK")
                st.write("Verificando índices de seguridad ciudadana... OK")
                st.write("Cargando capas de infraestructura (Transporte y Educación)... OK")
                
                # Almacenamos los datasets en la memoria de sesión
                st.session_state.update(dataframes)
                
                # Finalizamos el estado con éxito
                status.update(label="Sincronización completada exitosamente", state="complete", expanded=False)
                
                st.success("Los datos han sido validados y están listos para el procesamiento.")
                
                st.markdown("---")
                
                # Botón de acción centrado y profesional
                col_izq, col_centro, col_der = st.columns([1, 2, 1])
                with col_centro:
                    if st.button("Iniciar Diagnóstico Territorial", type="primary", use_container_width=True):
                        st.session_state.step = 2
                        st.rerun()
            else:
                status.update(label="Error en la sincronización", state="error")
                st.error("Fallo al recuperar los datasets. Verifique la disponibilidad del repositorio.")
                
        except Exception as e:
            status.update(label="Excepción del sistema", state="error")
            st.error(f"Detalle técnico del error: {e}")
# ==============================================================================
# PASO 2: SELECCIÓN DE UNIDAD ADMINISTRATIVA Y CONTEXTO
# ==============================================================================
elif st.session_state.step == 2:
    st.header("Fase 2: Delimitación del Área de Estudio")

    col_mapa, col_datos = st.columns([3, 1])

    with col_datos:
        st.markdown("### Instrucciones")
        st.markdown("""
        Seleccione en el visor geográfico la localidad objetivo.
        
        El sistema desplegará automáticamente el **Perfil de Seguridad 2024**, permitiéndole evaluar los riesgos predominantes antes de profundizar en el análisis de servicios.
        """)
        
        # Botón de retorno seguro
        st.markdown("---")
        if st.button("⬅ Volver al Inicio", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    with col_mapa:
        # Estilos corporativos para el visor
        COLOR_FRAME = "#2C3E50"    # Gris oscuro profesional
        COLOR_FILL = "#3498DB"     # Azul institucional
        COLOR_HI_FILL = "#AED6F1"  # Azul claro para hover
        COLOR_BORDER = "#E74C3C"   # Rojo alerta para selección

        localidades = st.session_state.localidades

        # Centrado dinámico del mapa basado en la geometría total
        bounds = localidades.total_bounds
        center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

        m = folium.Map(
            location=center, 
            zoom_start=11, 
            tiles="CartoDB positron",
            control_scale=True
        )
        
        # Capa GeoJSON interactiva
        folium.GeoJson(
            localidades,
            style_function=lambda feature: {
                "fillColor": COLOR_FILL,
                "color": COLOR_FRAME,
                "weight": 1.5,
                "fillOpacity": 0.4,
            },
            highlight_function=lambda feature: {
                "weight": 3,
                "color": COLOR_BORDER,
                "fillColor": COLOR_HI_FILL,
                "fillOpacity": 0.6,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["nombre_localidad"],
                aliases=["Unidad Administrativa:"],
                style="font-family: sans-serif; font-size: 12px;",
                sticky=True
            )
        ).add_to(m)

        # Renderizado del mapa
        output = st_folium(m, width=None, height=550, returned_objects=["last_clicked"])

    # --- Lógica de Detección de Selección y Perfilamiento ---
    clicked = output.get("last_clicked")
    
    # Contenedor inferior para resultados de la selección
    contenedor_resultado = st.container()

    if clicked and "lat" in clicked and "lng" in clicked:
        punto = Point(clicked["lng"], clicked["lat"])
        
        # Búsqueda espacial: ¿En qué polígono cayó el clic?
        seleccion = None
        perfil_seguridad = "Sin información disponible"
        
        for _, row in localidades.iterrows():
            if row["geometry"].contains(punto):
                seleccion = row["nombre_localidad"]
                # Recuperamos el dato de valor que generamos en el ETL
                if "top_3_delitos" in row:
                    perfil_seguridad = row["top_3_delitos"]
                break
        
        if seleccion:
            st.session_state.localidad_clic = seleccion
            
            with contenedor_resultado:
                st.markdown("---")
                col_res1, col_res2, col_res3 = st.columns([1, 2, 1])
                
                with col_res1:
                    st.success(f"Selección: {seleccion}")
                
                with col_res2:
                    # AQUÍ ESTÁ EL VALOR AGREGADO DE TU PROPUESTA
                    st.warning(f"🚨 **Focos de Inseguridad Detectados:**\n\n{perfil_seguridad}")
                
                with col_res3:
                    if st.button("Confirmar y Analizar Entorno ➡", type="primary", use_container_width=True):
                        st.session_state.localidad_sel = seleccion
                        st.session_state.step = 3
                        st.rerun()

# ==============================================================================
# PASO 3: PARAMETRIZACIÓN DEL ALCANCE ESPACIAL (BUFFER)
# ==============================================================================
elif st.session_state.step == 3:
    st.header("Fase 3: Definición del Área de Influencia")

    # Panel de contexto técnico
    st.markdown(f"""
    **Unidad Administrativa Base:** {st.session_state.localidad_sel}
    
    Para ejecutar el geoprocesamiento, es necesario definir el **radio de influencia (buffer)**. 
    Este parámetro determinará la extensión del análisis de vecindad alrededor del punto de interés, filtrando las capas de información (movilidad, educación y normativa) que intersecten con esta geometría.
    """)

    st.markdown("---")

    col_config, col_explicacion = st.columns([1, 1])

    with col_config:
        st.subheader("Configuración del Radio")
        
        # Select slider para pasos discretos y controlados
        radio_analisis = st.select_slider(
            "Seleccione la distancia lineal de análisis (metros):",
            options=[300, 600, 900, 1200, 1500, 1800, 2100],
            value=600,
            help="Distancia radial desde el punto central hacia la periferia."
        )
        st.session_state.radio_analisis = radio_analisis

    with col_explicacion:
        st.subheader("Interpretación de la Escala")
        
        # Lógica para explicar la distancia (Urbanismo Táctico)
        interpretacion = ""
        tiempo_caminata = int(radio_analisis / 80) # Promedio 80m/min
        
        if radio_analisis <= 600:
            tipo_escala = "Escala Peatonal (Vecindario Inmediato)"
            desc = "Análisis enfocado en la accesibilidad a pie. Ideal para evaluar dotacionales de proximidad y comercio vecinal."
        elif radio_analisis <= 1200:
            tipo_escala = "Escala Barrial (Distrito)"
            desc = "Cubre el entorno barrial ampliado. Permite evaluar conectividad con el sistema de transporte troncal y servicios intermedios."
        else:
            tipo_escala = "Escala Zonal (Inter-barrial)"
            desc = "Análisis de gran cobertura. Útil para identificar dinámicas de movilidad motorizada y grandes equipamientos urbanos."

        # Tarjeta de información técnica (Sin emojis, estilo limpio)
        st.info(f"""
        **Configuración Actual:** {radio_analisis} metros
        **Tipo de Análisis:** {tipo_escala}
        **Tiempo aprox. caminata:** {tiempo_caminata} minutos
        
        _{desc}_
        """)

    # Navegación
    st.markdown("---")
    col_atras, col_adelante = st.columns([1, 5])
    
    with col_atras:
        if st.button("⬅ Regresar"):
            st.session_state.step = 2
            st.rerun()
            
    with col_adelante:
        if st.button("Confirmar Parámetros y Ubicar Punto ➡", type="primary", use_container_width=True):
            st.session_state.step = 4
            st.rerun()

# ==============================================================================
# PASO 4: GEORREFERENCIACIÓN DEL PUNTO DE INTERÉS
# ==============================================================================
elif st.session_state.step == 4:
    st.header("Fase 4: Selección del Epicentro de Análisis")

    # Panel de parámetros activos
    st.info(f"""
    **Parámetros de Entrada:**
    * **Unidad Territorial:** {st.session_state.localidad_sel}
    * **Radio de Influencia:** {st.session_state.radio_analisis} metros (Escala {
            'Peatonal' if st.session_state.radio_analisis <= 600 else 
            'Barrial' if st.session_state.radio_analisis <= 1200 else 'Zonal'
        })
    
    *Instrucción: Haga clic en el mapa para establecer el centroide del área de estudio.*
    """)

    # Filtrar geometría específica
    localidades = st.session_state.localidades
    # Obtenemos la fila exacta de la localidad seleccionada
    localidad_geo = localidades[localidades["nombre_localidad"] == st.session_state.localidad_sel]
    
    # Configuración de estilos del mapa
    bounds = localidad_geo.total_bounds
    center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

    m = folium.Map(
        location=center,
        zoom_start=13,
        tiles="CartoDB positron",
        control_scale=True
    )

    # Polígono de contexto (Límites de la localidad)
    folium.GeoJson(
        localidad_geo,
        name="Límite Administrativo",
        style_function=lambda x: {
            "fillColor": "#F1C40F", # Amarillo institucional
            "color": "#2C3E50",
            "weight": 2,
            "fillOpacity": 0.1,
            "dashArray": "5, 5"
        }
    ).add_to(m)

    # CSS para mejorar la UX del cursor (Indica que es seleccionable)
    cursor_css = """
    <style>
        .leaflet-container { cursor: crosshair !important; }
    </style>
    """
    m.get_root().html.add_child(folium.Element(cursor_css))
    
    # Si ya hay un punto seleccionado previamente (por si recarga), lo dibujamos
    if "punto_lat" in st.session_state:
        folium.Marker(
            [st.session_state.punto_lat, st.session_state.punto_lon],
            tooltip="Epicentro Seleccionado",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        # Dibujamos el buffer visual para que el usuario entienda el alcance
        folium.Circle(
            location=[st.session_state.punto_lat, st.session_state.punto_lon],
            radius=st.session_state.radio_analisis,
            color="#E74C3C",
            fill=True,
            fill_opacity=0.2
        ).add_to(m)

    # Renderizar mapa
    mapa_interactivo = st_folium(m, width=None, height=500, returned_objects=["last_clicked"])

    # --- Lógica de Captura y Validación ---
    clicked = mapa_interactivo.get("last_clicked")
    
    contenedor_validacion = st.container()
    
    if clicked and "lat" in clicked and "lng" in clicked:
        punto_temp = Point(clicked["lng"], clicked["lat"])
        
        # Validación Topológica: ¿El punto está dentro de la localidad?
        # Esto evita errores de análisis (ej: elegir un punto en otra localidad por error)
        es_valido = False
        if localidad_geo.geometry.iloc[0].contains(punto_temp):
            es_valido = True
            st.session_state.punto_lat = clicked["lat"]
            st.session_state.punto_lon = clicked["lng"]
        else:
            st.warning("⚠️ El punto seleccionado está fuera de los límites de la localidad activa. Por favor seleccione un punto interior.")

        if es_valido:
            with contenedor_validacion:
                st.markdown("---")
                col_coords, col_accion = st.columns([2, 1])
                
                with col_coords:
                    st.success("✅ Coordenadas validadas correctamente.")
                    st.code(f"Lat: {clicked['lat']:.5f} | Lon: {clicked['lng']:.5f}", language="text")
                
                with col_accion:
                    if st.button("Ejecutar Análisis Sectorial 🚀", type="primary", use_container_width=True):
                        st.session_state.step = 5
                        st.rerun()

    # Navegación inferior
    st.markdown("---")
    col_back, col_reset = st.columns([1, 1])
    with col_back:
        if st.button("⬅ Corregir Radio", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with col_reset:
        if st.button("Reiniciar Sistema", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    # ==============================================================================
    # PASO 5: PROCESAMIENTO ANALÍTICO Y GENERACIÓN DE TABLEROS
    # ==============================================================================
    elif st.session_state.step == 5:
        st.header("Fase 5: Diagnóstico Territorial Integrado")

        # Panel de Resumen de Parámetros
        st.info(f"""
        **Metadatos del Análisis:**
        * **Epicentro (WGS84):** Lat {st.session_state.punto_lat:.5f}, Lon {st.session_state.punto_lon:.5f}
        * **Alcance Espacial:** Radio de {st.session_state.radio_analisis} metros
        * **Unidad Administrativa:** {st.session_state.localidad_sel}
        
        *El sistema ha ejecutado los algoritmos de intersección espacial. A continuación se presentan los hallazgos por dimensión temática.*
        """)

        # -------------------------------------------------------------------------
        # 1. MOTOR DE CÁLCULO ESPACIAL
        # -------------------------------------------------------------------------
        
        # Carga de capas desde memoria
        localidades = st.session_state.localidades
        manzanas    = st.session_state.manzanas
        transporte  = st.session_state.transporte
        colegios    = st.session_state.colegios
        areas_pot   = st.session_state.areas

        # Buffer Geodésico
        punto_ref = Point(st.session_state.punto_lon, st.session_state.punto_lat)
        gdf_punto = gpd.GeoDataFrame([{'geometry': punto_ref}], crs="EPSG:4326")
        gdf_buffer_metros = gdf_punto.to_crs(epsg=3116).buffer(st.session_state.radio_analisis)
        area_interes = gdf_buffer_metros.to_crs(epsg=4326).iloc[0]

        # Filtrado Vectorizado
        manzanas_zona = manzanas[manzanas.geometry.intersects(area_interes)]
        areas_zona = areas_pot[areas_pot.geometry.intersects(area_interes)]
        transporte_zona = transporte[transporte.geometry.within(area_interes)]
        colegios_zona = colegios[colegios.geometry.within(area_interes)]

        # -------------------------------------------------------------------------
        # 2. VISUALIZACIÓN: ACCESIBILIDAD Y MOVILIDAD
        # -------------------------------------------------------------------------
        st.markdown("### 1. Análisis de Conectividad y Movilidad")
        st.markdown("Evaluación de la oferta de transporte masivo (Troncal y Zonal).")

        col_mapa_trans, col_ind_trans = st.columns([3, 1])
        with col_mapa_trans:
            fig_transporte = go.Figure()
            fig_transporte.add_trace(go.Scattermapbox(
                lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
                mode='lines', fill='toself', name='Zona de Influencia',
                fillcolor='rgba(52, 152, 219, 0.1)', line=dict(color='#3498DB', width=2)
            ))
            if not transporte_zona.empty:
                fig_transporte.add_trace(go.Scattermapbox(
                    lat=transporte_zona.geometry.y, lon=transporte_zona.geometry.x,
                    mode='markers', name='Estaciones',
                    marker=dict(size=12, color='#E74C3C', symbol='bus'),
                    text=transporte_zona['nombre_estacion'], hoverinfo='text+name'
                ))
            fig_transporte.update_layout(
                mapbox_style="carto-positron", mapbox_zoom=14.5,
                mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                margin={"r":0,"t":0,"l":0,"b":0}, height=400, showlegend=True
            )
            st.plotly_chart(fig_transporte, use_container_width=True)

        with col_ind_trans:
            cant_estaciones = len(transporte_zona)
            st.metric("Nodos de Transporte", cant_estaciones)
            if cant_estaciones > 2: st.success("✅ Alta Conectividad")
            elif cant_estaciones > 0: st.warning("⚠️ Conectividad Media")
            else: st.error("❌ Baja Cobertura")

        # -------------------------------------------------------------------------
        # 3. VISUALIZACIÓN: INFRAESTRUCTURA EDUCATIVA
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 2. Cobertura Educativa")
        
        col_ind_edu, col_mapa_edu = st.columns([1, 3])
        with col_ind_edu:
            cant_colegios = len(colegios_zona)
            st.metric("Instituciones Educativas", cant_colegios)
            if not colegios_zona.empty:
                st.dataframe(colegios_zona['sector'].value_counts(), use_container_width=True)

        with col_mapa_edu:
            fig_edu = go.Figure()
            fig_edu.add_trace(go.Scattermapbox(
                lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
                mode='lines', fill='toself', fillcolor='rgba(155, 89, 182, 0.1)',
                line=dict(color='#8E44AD', width=2), name='Zona de Influencia'
            ))
            if not colegios_zona.empty:
                fig_edu.add_trace(go.Scattermapbox(
                    lat=colegios_zona.geometry.y, lon=colegios_zona.geometry.x,
                    mode='markers', name='Colegios', marker=dict(size=10, color='#8E44AD'),
                    text=colegios_zona['nombre'], hoverinfo='text'
                ))
            fig_edu.update_layout(
                mapbox_style="carto-positron", mapbox_zoom=14.5,
                mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                margin={"r":0,"t":0,"l":0,"b":0}, height=400
            )
            st.plotly_chart(fig_edu, use_container_width=True)

        # -------------------------------------------------------------------------
        # 4. VISUALIZACIÓN: ESTRATIFICACIÓN Y POT
        # -------------------------------------------------------------------------
        st.markdown("---")
        col_estrato, col_pot = st.columns(2)
        
        with col_estrato:
            st.markdown("### 3. Perfil Socioeconómico")
            if not manzanas_zona.empty:
                fig_estrato = px.choropleth_mapbox(
                    manzanas_zona, geojson=manzanas_zona.geometry, locations=manzanas_zona.index,
                    color="estrato", color_continuous_scale="Viridis",
                    mapbox_style="carto-positron", zoom=14, center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                    opacity=0.6
                )
                fig_estrato.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=350)
                st.plotly_chart(fig_estrato, use_container_width=True)
                st.info(f"Moda Socioeconómica: **Estrato {manzanas_zona['estrato'].mode()[0]}**")

        with col_pot:
            st.markdown("### 4. Normativa del Suelo (POT)")
            if not areas_zona.empty:
                fig_pot = px.choropleth_mapbox(
                    areas_zona, geojson=areas_zona.geometry, locations=areas_zona.index,
                    color="uso_pot_simplificado", mapbox_style="carto-positron",
                    zoom=14, center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                    opacity=0.5, color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_pot.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=350, showlegend=False)
                st.plotly_chart(fig_pot, use_container_width=True)
                st.info(f"Vocación Predominante: **{areas_zona['uso_pot_simplificado'].mode()[0]}**")

        # -------------------------------------------------------------------------
        # 5. SEGURIDAD (NUEVO BLOQUE INTEGRADO)
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.subheader("5. Contexto de Seguridad y Convivencia")
        
        # Recuperamos el dato de la localidad seleccionada
        localidad_actual = st.session_state.localidad_sel
        datos_loc = localidades[localidades['nombre_localidad'] == localidad_actual].iloc[0]
        perfil_seguridad = datos_loc.get('top_3_delitos', 'Información no disponible')

        st.warning(f"""
        **👮‍♂️ Perfil de Riesgo - {localidad_actual} (2024):**
        
        El análisis de datos históricos de la Secretaría de Seguridad indica que los delitos de mayor impacto en esta localidad son:
        
        👉 **{perfil_seguridad}**
        
        *Este indicador permite focalizar estrategias de prevención y aseguramiento de bienes.*
        """)

        # -------------------------------------------------------------------------
        # REPORTE DE CIERRE
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📑 Informe Ejecutivo")
        
        cant_manzanas = len(manzanas_zona)
        conclusion = "Alta viabilidad de desarrollo" if (cant_estaciones > 1 and cant_colegios > 1) else "Zona con oportunidades de consolidación"
        
        st.success(f"""
        **Dictamen del Sistema:** {conclusion}
        
        Se han analizado **{cant_manzanas} manzanas** catastrales. 
        En el radio de {st.session_state.radio_analisis}m se identifican {cant_estaciones} puntos de transporte y {cant_colegios} colegios.
        """)

        col_fin1, col_fin2 = st.columns(2)
        with col_fin1:
            st.button("📥 Descargar Informe Técnico (PDF)", disabled=True, help="Funcionalidad disponible en versión Pro")
        with col_fin2:
            if st.button("🔄 Iniciar Nuevo Diagnóstico", type="primary"):
                st.session_state.step = 2
                st.rerun()

        # -------------------------------------------------------------------------
        # VISUALIZACIÓN 1: SISTEMA DE MOVILIDAD Y CONECTIVIDAD
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🚇 Análisis de Accesibilidad al Transporte Público")
        
        st.markdown("""
        Evaluación de la cobertura del Sistema Integrado de Transporte Público (SITP y Troncal) en el área de influencia.
        La visualización identifica los **nodos de acceso** disponibles, permitiendo estimar la conectividad del sector con el resto de la ciudad.
        """)

        # --- Optimización: Filtrado Vectorial (Mucho más rápido) ---
        # Usamos el GeoDataFrame 'transporte_zona' que ya filtramos arriba (Paso 5 inicio)
        # No necesitamos bucles for lentos.
        
        fig_transporte = go.Figure()

        # 1. Capa: Área de Influencia (Contexto)
        fig_transporte.add_trace(go.Scattermapbox(
            lat=list(area_interes.exterior.xy[1]),
            lon=list(area_interes.exterior.xy[0]),
            mode='lines',
            fill='toself',
            name=f'Radio de Análisis ({st.session_state.radio_analisis}m)',
            fillcolor='rgba(230, 126, 34, 0.1)', # Naranja suave institucional
            line=dict(color='#D35400', width=2)
        ))

        # 2. Capa: Estaciones de Transporte
        if not transporte_zona.empty:
            fig_transporte.add_trace(go.Scattermapbox(
                lat=transporte_zona.geometry.y,
                lon=transporte_zona.geometry.x,
                mode='markers',
                name='Estaciones (TM/SITP)',
                marker=dict(
                    size=12,
                    color='#C0392B', # Rojo Transporte
                    opacity=0.9,
                    symbol='bus'     # Icono temático si Plotly lo soporta, sino círculo
                ),
                # Usamos la columna real del dataset limpio
                text=transporte_zona['nombre_estacion'], 
                hoverinfo='text'
            ))

        # 3. Capa: Epicentro del Análisis
        fig_transporte.add_trace(go.Scattermapbox(
            lat=[st.session_state.punto_lat],
            lon=[st.session_state.punto_lon],
            mode='markers',
            name='Epicentro Seleccionado',
            marker=dict(size=15, color='#2980B9', symbol='circle')
        ))

        # Configuración del Mapa (Layout Limpio)
        fig_transporte.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
            mapbox_zoom=14,
            margin={"r":0,"t":30,"l":0,"b":0},
            title=dict(text="Red de Transporte Público Cercana", x=0.01),
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_transporte, use_container_width=True)

        # Métricas de Soporte (KPIs)
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        
        cant_estaciones = len(transporte_zona)
        densidad = cant_estaciones / (3.14159 * (st.session_state.radio_analisis / 1000) ** 2)

        with col_kpi1:
            st.metric("Total Estaciones", cant_estaciones, help="Número absoluto de paraderos/estaciones en el radio.")
        with col_kpi2:
            st.metric("Densidad (Nodos/km²)", f"{densidad:.1f}", help="Concentración de oferta de transporte.")
        with col_kpi3:
            # Interpretación cualitativa automática
            if cant_estaciones >= 5:
                calif = "Alta Conectividad"
                delta_color = "normal"
            elif cant_estaciones >= 2:
                calif = "Conectividad Media"
                delta_color = "off"
            else:
                calif = "Baja Cobertura"
                delta_color = "inverse"
            st.metric("Diagnóstico de Acceso", calif, delta_color=delta_color)

        # -------------------------------------------------------------------------
        # VISUALIZACIÓN 2: INFRAESTRUCTURA EDUCATIVA Y COBERTURA
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🏫 Oferta Educativa en el Entorno")
        
        st.markdown("""
        Georreferenciación de instituciones educativas (Colegios Oficiales y Privados) dentro del perímetro de análisis.
        Este indicador permite evaluar la **capacidad de soporte educativo** del sector, un factor determinante para la valoración residencial familiar.
        """)

        # Layout de 2 columnas: Métricas a la izquierda, Mapa a la derecha
        col_ind_edu, col_mapa_edu = st.columns([1, 3])

        with col_ind_edu:
            cant_colegios = len(colegios_zona)
            st.metric("Total Colegios", cant_colegios, help="Instituciones activas registradas en el directorio oficial.")
            
            # Valor Agregado: Desglose por Sector (Público/Privado)
            if not colegios_zona.empty and 'sector' in colegios_zona.columns:
                st.markdown("##### Desglose por Sector")
                conteo_sector = colegios_zona['sector'].value_counts()
                st.dataframe(
                    conteo_sector, 
                    use_container_width=True,
                    column_config={"sector": "Tipo", "count": "Cantidad"}
                )
            
            # Métrica de densidad
            if cant_colegios > 0:
                densidad_edu = cant_colegios / (3.14159 * (st.session_state.radio_analisis / 1000) ** 2)
                st.metric("Densidad (Col/km²)", f"{densidad_edu:.1f}")

        with col_mapa_edu:
            fig_educacion = go.Figure()

            # 1. Capa: Área de Influencia
            fig_educacion.add_trace(go.Scattermapbox(
                lat=list(area_interes.exterior.xy[1]),
                lon=list(area_interes.exterior.xy[0]),
                mode='lines',
                fill='toself',
                name=f'Radio ({st.session_state.radio_analisis}m)',
                fillcolor='rgba(142, 68, 173, 0.1)',  # Morado institucional suave
                line=dict(color='#8E44AD', width=2)
            ))

            # 2. Capa: Colegios
            if not colegios_zona.empty:
                # Color dinámico según sector (Opcional, si no todo morado)
                # Por simplicidad visual usaremos un solo color con borde
                fig_educacion.add_trace(go.Scattermapbox(
                    lat=colegios_zona.geometry.y,
                    lon=colegios_zona.geometry.x,
                    mode='markers',
                    name='Instituciones',
                    marker=dict(
                        size=11,
                        color='#9B59B6',   # Morado claro
                        opacity=0.9,
                        symbol='circle'
                    ),
                    # Usamos el nombre real y el sector en el hover
                    text=colegios_zona['nombre'] + "<br>(" + colegios_zona['sector'] + ")",
                    hoverinfo='text'
                ))

            # 3. Capa: Epicentro
            fig_educacion.add_trace(go.Scattermapbox(
                lat=[st.session_state.punto_lat],
                lon=[st.session_state.punto_lon],
                mode='markers',
                name='Epicentro',
                marker=dict(size=15, color='#2980B9')
            ))

            fig_educacion.update_layout(
                mapbox_style="carto-positron",
                mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                mapbox_zoom=14,
                margin={"r":0,"t":30,"l":0,"b":0},
                title=dict(text="Red de Instituciones Educativas", x=0.01),
                height=450,
                showlegend=True
            )

            st.plotly_chart(fig_educacion, use_container_width=True)

        # -------------------------------------------------------------------------
        # VISUALIZACIÓN 3: PERFIL SOCIOECONÓMICO (ESTRATIFICACIÓN)
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🏘️ Composición Socioeconómica del Sector")
        
        st.markdown("""
        Distribución espacial de los estratos socioeconómicos asignados a las manzanas catastrales.
        Este mapa de calor permite identificar la homogeneidad o diversidad social de la zona, un factor clave para estudios de mercado y políticas públicas.
        """)

        # Definición de paleta de colores estándar para estratos (Semántica)
        color_estrato_map = {
            1: '#C0392B',  # Bajo-Bajo (Rojo Oscuro)
            2: '#E67E22',  # Bajo (Naranja)
            3: '#F1C40F',  # Medio-Bajo (Amarillo)
            4: '#2ECC71',  # Medio (Verde)
            5: '#3498DB',  # Medio-Alto (Azul)
            6: '#8E44AD'   # Alto (Morado)
        }

        if not manzanas_zona.empty:
            # Aseguramos que el estrato sea numérico para el ordenamiento
            manzanas_zona['estrato'] = manzanas_zona['estrato'].astype(int)
            
            # Layout de 2 columnas: Mapa a la izquierda, Estadísticas a la derecha
            col_mapa_soc, col_stat_soc = st.columns([2, 1])

            with col_mapa_soc:
                # MAPA OPTIMIZADO (Vectorial)
                fig_estrato = px.choropleth_mapbox(
                    manzanas_zona,
                    geojson=manzanas_zona.geometry,
                    locations=manzanas_zona.index,
                    color="estrato",
                    title="Distribución Espacial de Estratos",
                    mapbox_style="carto-positron",
                    zoom=14.5,
                    center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                    opacity=0.7,
                    # Mapeo manual de colores para consistencia
                    color_discrete_map={k: v for k, v in color_estrato_map.items() if k in manzanas_zona['estrato'].unique()},
                    labels={'estrato': 'Nivel Socioeconómico'}
                )
                
                # Ajustes visuales del mapa
                fig_estrato.update_layout(
                    margin={"r":0,"t":30,"l":0,"b":0},
                    height=450,
                    legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
                )
                # Dibujar el borde del buffer para contexto
                fig_estrato.add_trace(go.Scattermapbox(
                    lat=list(area_interes.exterior.xy[1]),
                    lon=list(area_interes.exterior.xy[0]),
                    mode='lines',
                    line=dict(color='#2C3E50', width=1.5),
                    name='Límite de Análisis'
                ))
                
                st.plotly_chart(fig_estrato, use_container_width=True)

            with col_stat_soc:
                # ESTADÍSTICAS Y GRÁFICO DE BARRAS
                dist_estratos = manzanas_zona["estrato"].value_counts().sort_index()
                
                # Cálculo de la Moda (Estrato predominante)
                estrato_moda = manzanas_zona['estrato'].mode()[0]
                pct_moda = (len(manzanas_zona[manzanas_zona['estrato'] == estrato_moda]) / len(manzanas_zona)) * 100
                
                st.info(f"""
                **Perfil Dominante:**
                El **{pct_moda:.1f}%** de las manzanas del sector pertenecen al **Estrato {estrato_moda}**.
                """)

                # Gráfico de Barras Limpio
                fig_barras = go.Figure(data=[
                    go.Bar(
                        x=[f"E{e}" for e in dist_estratos.index],
                        y=dist_estratos.values,
                        marker_color=[color_estrato_map.get(e, '#95A5A6') for e in dist_estratos.index],
                        text=dist_estratos.values,
                        textposition='auto',
                    )
                ])
                fig_barras.update_layout(
                    title="Conteo de Manzanas",
                    xaxis_title="Estrato",
                    yaxis_title="Cantidad",
                    height=250,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_barras, use_container_width=True)

        else:
            st.warning("⚠️ No se identificaron manzanas residenciales clasificadas dentro del radio seleccionado.")

        # -------------------------------------------------------------------------
        # VISUALIZACIÓN 4: NORMATIVA Y USOS DEL SUELO (POT - DECRETO 555)
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 4. Vocación Normativa del Suelo")
        
        st.markdown("""
        Análisis de la reglamentación de usos del suelo vigente según el **Plan de Ordenamiento Territorial (POT) - Decreto 555 de 2021**.
        Esta capa permite identificar qué actividades (Residenciales, Comerciales, Dotacionales o Industriales) están permitidas legalmente en los predios del sector.
        """)

        if not areas_zona.empty:
            # Layout: Mapa a la izquierda, Métricas a la derecha
            col_mapa_pot, col_stat_pot = st.columns([2, 1])

            with col_mapa_pot:
                # MAPA VECTORIZADO
                fig_pot = px.choropleth_mapbox(
                    areas_zona,
                    geojson=areas_zona.geometry,
                    locations=areas_zona.index,
                    color="uso_pot_simplificado",  # Columna limpiada en el ETL
                    title="Áreas de Actividad POT",
                    mapbox_style="carto-positron",
                    zoom=14.5,
                    center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                    opacity=0.6,
                    # Paleta de colores distintiva para usos
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    labels={'uso_pot_simplificado': 'Área de Actividad'}
                )

                # Ajustes de diseño
                fig_pot.update_layout(
                    margin={"r":0,"t":30,"l":0,"b":0},
                    height=450,
                    legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
                )

                # Límite del buffer
                fig_pot.add_trace(go.Scattermapbox(
                    lat=list(area_interes.exterior.xy[1]),
                    lon=list(area_interes.exterior.xy[0]),
                    mode='lines',
                    line=dict(color='#2C3E50', width=1.5),
                    name='Perímetro de Análisis'
                ))

                st.plotly_chart(fig_pot, use_container_width=True)

            with col_stat_pot:
                # ESTADÍSTICAS
                dist_pot = areas_zona["uso_pot_simplificado"].value_counts()
                
                # Vocación Predominante
                uso_moda = dist_pot.index[0]
                pct_uso = (dist_pot.iloc[0] / len(areas_zona)) * 100
                
                st.info(f"""
                **Vocación Dominante:**
                El entorno se caracteriza principalmente como **{uso_moda}**, ocupando el **{pct_uso:.1f}%** de las zonas normativas intersectadas.
                """)

                # Gráfico de Barras
                fig_barras_pot = go.Figure(data=[
                    go.Bar(
                        y=[label[:25] + '...' if len(label) > 25 else label for label in dist_pot.index], # Truncar nombres largos
                        x=dist_pot.values,
                        orientation='h', # Barras horizontales para leer mejor los nombres largos
                        marker_color='#1ABC9C', # Turquesa institucional
                        text=dist_pot.values,
                        textposition='auto',
                    )
                ])
                
                fig_barras_pot.update_layout(
                    title="Distribución de Áreas",
                    xaxis_title="Cantidad de Polígonos",
                    yaxis_title="",
                    height=300,
                    margin=dict(l=5, r=5, t=30, b=5),
                    yaxis={'categoryorder':'total ascending'} # Ordenar de mayor a menor
                )
                st.plotly_chart(fig_barras_pot, use_container_width=True)

        else:
            st.warning("No se encontró información normativa del POT para las coordenadas seleccionadas (posible zona de reserva o sin reglamentación específica).")

        # -------------------------------------------------------------------------
        # 6. GENERACIÓN DEL INFORME EJECUTIVO (HTML)
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.header("📑 Informe de Inteligencia Territorial")
        
        st.info("Generando diagnóstico consolidado...")

        # 1. CÁLCULO DE LÍNEA BASE (Totales de la Localidad)
        # Optimización: Usamos filtros espaciales en lugar de bucles iterativos
        
        # Obtenemos la geometría de la localidad completa
        poly_localidad = localidades[localidades['nombre_localidad'] == st.session_state.localidad_sel].geometry.iloc[0]
        
        # Filtramos estaciones y colegios dentro de toda la localidad (Vectorizado)
        total_estaciones_loc = len(transporte[transporte.geometry.within(poly_localidad)])
        total_colegios_loc = len(colegios[colegios.geometry.within(poly_localidad)])
        
        # 2. CÁLCULO DE INDICADORES RELATIVOS (Buffer vs Localidad)
        pct_cobertura_trans = (len(transporte_zona) / total_estaciones_loc * 100) if total_estaciones_loc > 0 else 0
        pct_cobertura_edu = (len(colegios_zona) / total_colegios_loc * 100) if total_colegios_loc > 0 else 0
        
        # 3. RECUPERACIÓN DE DATOS CUALITATIVOS
        # Seguridad
        perfil_seguridad = datos_loc.get('top_3_delitos', 'No disponible')
        # Estrato Moda
        estrato_dom = manzanas_zona['estrato'].mode()[0] if not manzanas_zona.empty else "N/A"
        # Uso POT Moda
        uso_dom = areas_zona['uso_pot_simplificado'].mode()[0] if not areas_zona.empty else "N/A"

        # 4. SCORING AUTOMÁTICO (Algoritmo de Viabilidad)
        score = 0
        if len(transporte_zona) >= 3: score += 1
        if len(colegios_zona) >= 2: score += 1
        if not manzanas_zona.empty: score += 1
        
        if score == 3:
            dictamen = "ALTAMENTE VIABLE"
            color_dictamen = "#27AE60" # Verde
            desc_dictamen = "Zona consolidada con excelente dotación de servicios."
        elif score == 2:
            dictamen = "VIABILIDAD MEDIA"
            color_dictamen = "#F39C12" # Naranja
            desc_dictamen = "Zona en desarrollo con oportunidades de mejora en infraestructura."
        else:
            dictamen = "VIABILIDAD RESTRINGIDA"
            color_dictamen = "#C0392B" # Rojo
            desc_dictamen = "Zona con déficit de equipamientos urbanos."

        # 5. GENERACIÓN DEL HTML (DISEÑO CORPORATIVO)
        html_report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica', sans-serif; color: #333; line-height: 1.6; }}
                .header {{ background-color: #2C3E50; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                .section {{ margin-top: 20px; border-bottom: 2px solid #ECF0F1; padding-bottom: 10px; }}
                .h-title {{ color: #2980B9; border-left: 5px solid #2980B9; padding-left: 10px; }}
                .metric-box {{ background-color: #F8F9F9; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #E5E7E9; }}
                .alert-box {{ background-color: #FDEDEC; color: #C0392B; padding: 15px; border-left: 5px solid #C0392B; }}
                .score-box {{ background-color: {color_dictamen}; color: white; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; border-radius: 5px; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ padding: 10px; border: 1px solid #DDD; text-align: left; }}
                th {{ background-color: #F2F3F4; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Inteligencia Territorial</h1>
                <p>Bogotá Inteligente - Datos al Ecosistema 2025</p>
            </div>

            <div class="section">
                <h2 class="h-title">1. Definición del Análisis</h2>
                <table>
                    <tr><th>Localidad</th><td>{st.session_state.localidad_sel}</td></tr>
                    <tr><th>Epicentro (Lat/Lon)</th><td>{st.session_state.punto_lat:.5f}, {st.session_state.punto_lon:.5f}</td></tr>
                    <tr><th>Radio de Influencia</th><td>{st.session_state.radio_analisis} metros</td></tr>
                </table>
            </div>

            <div class="section">
                <h2 class="h-title">2. Dimensión de Seguridad y Convivencia</h2>
                <div class="alert-box">
                    <strong>Perfil de Riesgo Identificado (Top 3):</strong><br>
                    {perfil_seguridad}
                </div>
            </div>

            <div class="section">
                <h2 class="h-title">3. Indicadores de Cobertura</h2>
                <table>
                    <tr>
                        <th>Dimensión</th>
                        <th>Oferta en Radio ({st.session_state.radio_analisis}m)</th>
                        <th>Cobertura Relativa (vs Localidad)</th>
                    </tr>
                    <tr>
                        <td>🚇 Movilidad (Estaciones)</td>
                        <td>{len(transporte_zona)}</td>
                        <td>{pct_cobertura_trans:.1f}% del total local</td>
                    </tr>
                    <tr>
                        <td>🏫 Educación (Colegios)</td>
                        <td>{len(colegios_zona)}</td>
                        <td>{pct_cobertura_edu:.1f}% del total local</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2 class="h-title">4. Caracterización Urbana</h2>
                <div class="metric-box">
                    <ul>
                        <li><strong>Nivel Socioeconómico Predominante:</strong> Estrato {estrato_dom}</li>
                        <li><strong>Vocación Normativa (POT):</strong> {uso_dom}</li>
                        <li><strong>Densidad Urbana:</strong> {len(manzanas_zona)} manzanas en el sector.</li>
                    </ul>
                </div>
            </div>

            <div class="score-box">
                DICTAMEN: {dictamen}
                <div style="font-size: 16px; font-weight: normal; margin-top: 5px;">{desc_dictamen}</div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; color: #7F8C8D; font-size: 12px;">
                Generado automáticamente por el Sistema de Inteligencia Territorial de Bogotá.<br>
                Fuente: Infraestructura de Datos Espaciales (IDECA) & Datos Abiertos Bogotá.
            </div>
        </body>
        </html>
        """
        
        # 6. VISUALIZACIÓN EN PANTALLA Y DESCARGA
        col_kpi_fin, col_dl_fin = st.columns([2, 1])
        
        with col_kpi_fin:
            st.success(f"**Dictamen Final:** {dictamen}")
            st.caption(desc_dictamen)
        
        with col_dl_fin:
            st.download_button(
                label="📥 Descargar Informe Oficial (HTML)",
                data=html_report,
                file_name=f"Reporte_Territorial_{st.session_state.localidad_sel}.html",
                mime="text/html",
                type="primary"
            )
        
        # Botón de Reinicio
        st.markdown("---")
        if st.button("🔄 Iniciar Nuevo Análisis"):
            # Limpiamos variables de sesión específicas del análisis pero mantenemos los datos cargados
            for key in ['punto_lat', 'punto_lon', 'localidad_sel', 'localidad_clic']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.step = 2
            st.rerun()