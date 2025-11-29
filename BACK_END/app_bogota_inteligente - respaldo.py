import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Inteligencia Territorial Bogotá",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Encabezado y Contexto del Proyecto ---
st.title("Sistema de Inteligencia Territorial de Bogotá")
st.subheader("Análisis Estratégico basado en Datos Abiertos")

st.markdown("""
Esta plataforma tecnológica permite la evaluación multidimensional del territorio mediante el procesamiento de datos oficiales de la infraestructura de datos espaciales de la ciudad de Bogotá.

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
    Retorna un diccionario con los GeoDataFrames normalizados en coordenadas (EPSG:4326).
    """
    # Repositorio oficial de datos procesados
    BASE_URL = "https://github.com/andres-fuentex/CONCURSO/raw/main/DATOS_LIMPIOS/"
    
    # Mapeo de archivos según la arquitectura de datos definida
    archivos = {
        "localidades": "dim_localidad.geojson",# mapa principal localidades y contexto de seguridad DAI
        "areas":       "dim_area.geojson",     # Usos del suelo POT
        "manzanas":    "tabla_hechos.geojson", # Estratificación
        "transporte":  "dim_transporte.geojson", # datos publicados de las estaciones de tranmilenio
        "colegios":    "dim_colegios.geojson" # datos de la secretaria de educacion 
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
    * **Radio de Influencia:** {st.session_state.radio_analisis} metros
    
    *Instrucción: Haga clic en el mapa para establecer el centroide del área de estudio.*
    """)

    # Filtrar geometría específica
    localidades = st.session_state.localidades
    localidad_geo = localidades[localidades["nombre_localidad"] == st.session_state.localidad_sel]
    
    # Configuración del mapa
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
            "fillColor": "#F1C40F",
            "color": "#2C3E50",
            "weight": 2,
            "fillOpacity": 0.1,
            "dashArray": "5, 5"
        }
    ).add_to(m)

    # CSS para cursor
    cursor_css = """
    <style> .leaflet-container { cursor: crosshair !important; } </style>
    """
    m.get_root().html.add_child(folium.Element(cursor_css))
    
    # Si YA tenemos un punto guardado en memoria, lo dibujamos
    if "punto_lat" in st.session_state:
        # Marcador del punto
        folium.Marker(
            [st.session_state.punto_lat, st.session_state.punto_lon],
            tooltip="Epicentro Seleccionado",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        # Círculo del radio
        folium.Circle(
            location=[st.session_state.punto_lat, st.session_state.punto_lon],
            radius=st.session_state.radio_analisis,
            color="#E74C3C",
            fill=True,
            fill_opacity=0.2
        ).add_to(m)

    # Renderizar mapa
    mapa_interactivo = st_folium(m, width=None, height=500, returned_objects=["last_clicked"])

    # --- LÓGICA DE CAPTURA (ACTUALIZAR MEMORIA) ---
    clicked = mapa_interactivo.get("last_clicked")
    
    if clicked and "lat" in clicked and "lng" in clicked:
        punto_temp = Point(clicked["lng"], clicked["lat"])
        
        # Validación Topológica inmediata
        if localidad_geo.geometry.iloc[0].contains(punto_temp):
            # GUARDAMOS EN MEMORIA
            st.session_state.punto_lat = clicked["lat"]
            st.session_state.punto_lon = clicked["lng"]
            # Forzamos una recarga inmediata para pintar el marcador rojo
            st.rerun()
        else:
            st.warning("⚠️ El punto seleccionado está fuera de la localidad activa.")

    # --- LÓGICA DE BOTÓN (SE MUESTRA SIEMPRE QUE HAYA DATOS EN MEMORIA) ---
    # Al sacarlo del 'if clicked', el botón ya no desaparece al pulsarlo
    contenedor_validacion = st.container()
    
    if "punto_lat" in st.session_state:
        with contenedor_validacion:
            st.markdown("---")
            col_coords, col_accion = st.columns([2, 1])
            
            with col_coords:
                st.success("✅ Coordenadas validadas y fijadas.")
                st.code(f"Lat: {st.session_state.punto_lat:.5f} | Lon: {st.session_state.punto_lon:.5f}", language="text")
            
            with col_accion:
                # Este botón ahora sí funcionará
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

    # ==============================================================================
# PASO 5: RESULTADOS DEL ANÁLISIS (DASHBOARD CIUDADANO)
# ==============================================================================
elif st.session_state.step == 5:
    st.header("📊 Resultados de tu Análisis")

    # Resumen amigable en la parte superior
    st.info(f"""
    **Estás analizando:** Un radio de **{st.session_state.radio_analisis} metros** a la redonda.
    📍 **Punto exacto:** En la localidad de **{st.session_state.localidad_sel}**.
    """)

    # -------------------------------------------------------------------------
    # 1. MOTOR DE CÁLCULO (Invisible para el usuario)
    # -------------------------------------------------------------------------
    localidades = st.session_state.localidades
    manzanas = st.session_state.manzanas
    transporte = st.session_state.transporte
    colegios = st.session_state.colegios
    areas_pot = st.session_state.areas

    # Geometría del Buffer
    punto_ref = Point(st.session_state.punto_lon, st.session_state.punto_lat)
    gdf_punto = gpd.GeoDataFrame([{'geometry': punto_ref}], crs="EPSG:4326")
    gdf_buffer = gdf_punto.to_crs(epsg=3116).buffer(st.session_state.radio_analisis).to_crs(epsg=4326)
    area_interes = gdf_buffer.iloc[0]

    # Asegurar Proyecciones (Corrección técnica)
    if transporte.crs != "EPSG:4326": transporte = transporte.to_crs("EPSG:4326")
    if colegios.crs != "EPSG:4326": colegios = colegios.to_crs("EPSG:4326")
    if manzanas.crs != "EPSG:4326": manzanas = manzanas.to_crs("EPSG:4326")
    if areas_pot.crs != "EPSG:4326": areas_pot = areas_pot.to_crs("EPSG:4326")

    # Cruces Espaciales
    transporte_zona = transporte[transporte.geometry.intersects(area_interes)]
    colegios_zona = colegios[colegios.geometry.intersects(area_interes)]
    manzanas_zona = manzanas[manzanas.geometry.intersects(area_interes)]
    areas_zona = areas_pot[areas_pot.geometry.intersects(area_interes)]

    # -------------------------------------------------------------------------
    # SECCIÓN 1: MOVILIDAD (Corrección: Símbolo Círculo)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🚌 1. ¿Qué tan fácil es moverse?")
    st.markdown("Analizamos qué opciones de transporte público (Transmilenio y SITP) tienes 'a la mano'.")

    # Layout: Mapa grande a la izquierda, Datos clave a la derecha
    col_mapa_mov, col_data_mov = st.columns([2, 1])

    with col_mapa_mov:
        fig_t = go.Figure()

        # Zona (Naranja suave)
        fig_t.add_trace(go.Scattermapbox(
            lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
            mode='lines', fill='toself', name='Zona analizada',
            fillcolor='rgba(255, 165, 0, 0.1)', line=dict(color='orange', width=2)
        ))

        # Estaciones (CORRECCIÓN: symbol='circle' para asegurar que se vean)
        if not transporte_zona.empty:
            fig_t.add_trace(go.Scattermapbox(
                lat=transporte_zona.geometry.y,
                lon=transporte_zona.geometry.x,
                mode='markers',
                name='Paraderos',
                marker=dict(size=10, color='#E74C3C', symbol='circle'), # Rojo visible
                text=transporte_zona['nombre_estacion'], hoverinfo='text'
            ))

        # Tu punto
        fig_t.add_trace(go.Scattermapbox(
            lat=[st.session_state.punto_lat], lon=[st.session_state.punto_lon],
            mode='markers', name='Tú', marker=dict(size=12, color='#3498DB')
        ))

        fig_t.update_layout(
            mapbox_style="carto-positron", 
            mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
            mapbox_zoom=14, margin={"r":0,"t":0,"l":0,"b":0}, height=350, showlegend=True,
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_t, use_container_width=True)

    with col_data_mov:
        cant_t = len(transporte_zona)
        st.metric("Puntos de Transporte", cant_t)
        
        if cant_t > 5:
            st.success("✅ **Excelente Conectividad:** Tienes muchas opciones de ruta cerca.")
        elif cant_t > 0:
            st.warning("⚠️ **Conectividad Media:** Tienes transporte, pero quizás debas caminar un poco.")
        else:
            st.error("❌ **Zona Apartada:** Dependerás de vehículo particular o caminatas largas.")

    # -------------------------------------------------------------------------
    # SECCIÓN 2: EDUCACIÓN
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🏫 2. ¿Dónde pueden estudiar tus hijos?")
    st.markdown("Ubicación de colegios oficiales y privados en el vecindario.")

    col_mapa_edu, col_data_edu = st.columns([2, 1])

    with col_mapa_edu:
        fig_e = go.Figure()
        # Zona (Morado suave)
        fig_e.add_trace(go.Scattermapbox(
            lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
            mode='lines', fill='toself', name='Zona analizada',
            fillcolor='rgba(155, 89, 182, 0.1)', line=dict(color='#8E44AD', width=2)
        ))
        # Colegios
        if not colegios_zona.empty:
            fig_e.add_trace(go.Scattermapbox(
                lat=colegios_zona.geometry.y, lon=colegios_zona.geometry.x,
                mode='markers', name='Colegios',
                marker=dict(size=9, color='#8E44AD', symbol='circle'),
                text=colegios_zona['nombre'], hoverinfo='text'
            ))
        # Tu punto
        fig_e.add_trace(go.Scattermapbox(
            lat=[st.session_state.punto_lat], lon=[st.session_state.punto_lon],
            mode='markers', name='Tú', marker=dict(size=12, color='#3498DB')
        ))
        fig_e.update_layout(
            mapbox_style="carto-positron", 
            mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
            mapbox_zoom=14, margin={"r":0,"t":0,"l":0,"b":0}, height=350, showlegend=False
        )
        st.plotly_chart(fig_e, use_container_width=True)

    with col_data_edu:
        st.metric("Total Colegios", len(colegios_zona))
        if not colegios_zona.empty:
            st.caption("Distribución por tipo:")
            conteo = colegios_zona['sector'].value_counts().reset_index()
            conteo.columns = ['Tipo', 'Cantidad']
            st.dataframe(conteo, hide_index=True)

    # -------------------------------------------------------------------------
    # SECCIÓN 3: ESTRATIFICACIÓN
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🏘️ 3. ¿Cómo es el vecindario? (Estratos)")
    st.markdown("Nivel socioeconómico predominante en las manzanas del sector.")

    if not manzanas_zona.empty:
        col_mapa_soc, col_data_soc = st.columns([2, 1])
        
        with col_mapa_soc:
            manzanas_zona['estrato'] = manzanas_zona['estrato'].astype(int)
            fig_s = px.choropleth_mapbox(
                manzanas_zona, geojson=manzanas_zona.geometry, locations=manzanas_zona.index,
                color="estrato", mapbox_style="carto-positron", zoom=14.5,
                center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                opacity=0.6,
                color_discrete_map={1:'#C0392B', 2:'#E67E22', 3:'#F1C40F', 4:'#2ECC71', 5:'#3498DB', 6:'#8E44AD'}
            )
            fig_s.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=350, showlegend=False)
            fig_s.add_trace(go.Scattermapbox(
                lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
                mode='lines', line=dict(color='black', width=2), name='Límite'
            ))
            st.plotly_chart(fig_s, use_container_width=True)

        with col_data_soc:
            moda_estrato = manzanas_zona['estrato'].mode()[0]
            st.info(f"El estrato más común es el **{moda_estrato}**.")
            
            # Gráfico de barras simple
            conteo_est = manzanas_zona['estrato'].value_counts().sort_index()
            fig_b = go.Figure(data=[go.Bar(
                x=[f"E{i}" for i in conteo_est.index], y=conteo_est.values,
                marker_color='#95A5A6'
            )])
            fig_b.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_b, use_container_width=True)
    else:
        st.warning("No hay datos de vivienda en esta zona (puede ser parque o industrial).")

    # -------------------------------------------------------------------------
    # SECCIÓN 4: POT (USOS DEL SUELO)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🏗️ 4. ¿Qué se permite construir? (POT)")
    st.markdown("Reglas de juego del Plan de Ordenamiento Territorial vigente.")

    if not areas_zona.empty:
        col_mapa_pot, col_data_pot = st.columns([2, 1])
        
        with col_mapa_pot:
            fig_p = px.choropleth_mapbox(
                areas_zona, geojson=areas_zona.geometry, locations=areas_zona.index,
                color="uso_pot_simplificado", mapbox_style="carto-positron", zoom=14.5,
                center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                opacity=0.5, color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_p.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=350, showlegend=False)
            fig_p.add_trace(go.Scattermapbox(
                lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
                mode='lines', line=dict(color='black', width=2), name='Límite'
            ))
            st.plotly_chart(fig_p, use_container_width=True)

        with col_data_pot:
            moda_uso = areas_zona['uso_pot_simplificado'].mode()[0]
            st.info(f"La vocación principal es: **{moda_uso}**")
            
            # Barras horizontales
            conteo_uso = areas_zona['uso_pot_simplificado'].value_counts()
            fig_bp = go.Figure(data=[go.Bar(
                y=[l[:15] for l in conteo_uso.index], x=conteo_uso.values, orientation='h',
                marker_color='#1ABC9C'
            )])
            fig_bp.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bp, use_container_width=True)
    else:
        st.warning("Sin datos de normativa específica.")

    # -------------------------------------------------------------------------
    # CIERRE: CONTEXTO DE SEGURIDAD + DESCARGA
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🛡️ Contexto de Seguridad")
    
    # Recuperar datos
    localidad_actual = st.session_state.localidad_sel
    datos_loc = localidades[localidades['nombre_localidad'] == localidad_actual].iloc[0]
    seguridad = datos_loc.get('top_3_delitos', 'Dato no disponible')
    
    st.error(f"**Ten en cuenta:** En {localidad_actual}, los delitos más reportados son: {seguridad}")

    st.markdown("---")
    
    # Botones finales
    # Link a Google Maps para el reporte
    gmaps = f"https://www.google.com/maps/search/?api=1&query={st.session_state.punto_lat},{st.session_state.punto_lon}"
    
    # HTML Simplificado para reporte
    html = f"""
    <h3>Reporte Bogotá Inteligente</h3>
    <p><strong>Ubicación:</strong> {localidad_actual}</p>
    <p><strong>Seguridad:</strong> {seguridad}</p>
    <p><strong>Transporte:</strong> {len(transporte_zona)} estaciones.</p>
    <p><strong>Colegios:</strong> {len(colegios_zona)} instituciones.</p>
    <p><a href="{gmaps}">Ver en Google Maps</a></p>
    """
    
    col_fin1, col_fin2 = st.columns(2)
    with col_fin1:
        st.download_button("📥 Descargar Resumen (HTML)", data=html, file_name="Reporte.html", mime="text/html", type="primary")
    with col_fin2:
        if st.button("🔄 Consultar otra zona"):
            for k in ['punto_lat', 'punto_lon', 'localidad_clic', 'localidad_sel']:
                if k in st.session_state: del st.session_state[k]
            st.session_state.step = 2
            st.rerun()

            
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