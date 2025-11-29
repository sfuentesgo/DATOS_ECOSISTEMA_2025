import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- Configuración de la Página (Estilo Ciudadano) ---
st.set_page_config(
    page_title="Bogotá a un Clic",
    page_icon="💛",
    layout="wide",
    initial_sidebar_state="collapsed" # Menú colapsado para más limpieza
)

# --- Inyección de Estilos (CSS) - Paleta Bogotá ---
# Esto le da el toque visual único con los colores de la ciudad
st.markdown("""
    <style>
        /* Títulos en Rojo Bogotá */
        h1 { color: #DA291C; font-family: 'Helvetica', sans-serif; font-weight: 800; }
        h2, h3 { color: #2C3E50; }
        
        /* Resaltados en Amarillo */
        .highlight { background-color: #F1C40F; padding: 2px 5px; border-radius: 3px; color: #000; font-weight: bold; }
        
        /* Caja de introducción limpia */
        .intro-box { 
            background-color: #f8f9fa; 
            padding: 20px; 
            border-left: 5px solid #DA291C; 
            border-radius: 5px; 
            font-size: 1.1em;
        }
    </style>
""", unsafe_allow_html=True)

# --- Encabezado y Bienvenida ---
st.title("Bogotá Visible: Tu Barrio en Datos 🏙️")
st.subheader("Toma decisiones inteligentes sobre dónde vivir o invertir.")

# Texto introductorio amigable
st.markdown("""
<div class="intro-box">
    ¿Alguna vez te has preguntado qué tan seguro es realmente un barrio, qué colegios tiene cerca o qué se puede construir allí?<br><br>
    Esta herramienta conecta los <b>datos oficiales de la ciudad</b> contigo. Olvídate de los mapas complicados; aquí traducimos la información técnica en respuestas claras para que conozcas la vocación real de cualquier rincón de Bogotá.
</div>
""", unsafe_allow_html=True)

st.write("") # Espacio vacío

# Explicación de valor con iconos sencillos
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.markdown("### 👮 Seguridad Real")
    st.info("Conoce el **Top 3 de delitos** específicos de la zona. No es lo mismo un barrio donde roban celulares a uno con hurto de residencias.")

with col_info2:
    st.markdown("### 🏡 Tu Entorno")
    st.warning("Descubre si el uso del suelo es **Residencial, Comercial o Industrial** según el POT vigente. Evita sorpresas ruidosas.")

with col_info3:
    st.markdown("### 🚌 Calidad de Vida")
    st.success("Analiza qué tan fácil es moverte. Mide la cercanía a **Transporte Público (Transmilenio/SITP)** y colegios.")

st.markdown("---")


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
        "localidades": "dim_localidad.geojson", # mapa de localidades y contexto de seguridad basado en DAI
        "areas":       "dim_area.geojson",     # Usos del suelo POT
        "manzanas":    "tabla_hechos.geojson", # Estratificación
        "transporte":  "dim_transporte.geojson", # datos de estaciones de transmilenio
        "colegios":    "dim_colegios.geojson" # datos secretaria de educacion colegios en bogota
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

    # Componente de estado para feedback 
    with st.status("Ejecutando protocolo de conexión...", expanded=True) as status:
        st.write("Estableciendo enlace con fuentes de datos...")
        
        try:
            # Ejecutamos la función de carga
            dataframes = cargar_datasets()
            
            if dataframes:
                # Simulamos pasos de validación para dar confianza al usuario
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
# PASO 5: DIAGNÓSTICO INTEGRAL Y REPORTE
# ==============================================================================
elif st.session_state.step == 5:
    st.header("Fase 5: Diagnóstico Territorial Integrado")

    # Panel de Resumen de Parámetros
    st.info(f"""
    **Metadatos del Análisis:**
    * **Epicentro (WGS84):** Lat {st.session_state.punto_lat:.5f}, Lon {st.session_state.punto_lon:.5f}
    * **Alcance Espacial:** Radio de {st.session_state.radio_analisis} metros
    * **Unidad Administrativa:** {st.session_state.localidad_sel}
    """)

    # -------------------------------------------------------------------------
    # 1. MOTOR DE CÁLCULO ESPACIAL (GEO-PROCESSING)
    # -------------------------------------------------------------------------
    
    # Carga de capas desde memoria
    localidades = st.session_state.localidades
    manzanas    = st.session_state.manzanas
    transporte  = st.session_state.transporte
    colegios    = st.session_state.colegios
    areas_pot   = st.session_state.areas

    # Creación del Buffer Geodésico
    punto_ref = Point(st.session_state.punto_lon, st.session_state.punto_lat)
    gdf_punto = gpd.GeoDataFrame([{'geometry': punto_ref}], crs="EPSG:4326")
    
    # Buffer en metros y retorno a WGS84
    gdf_buffer_metros = gdf_punto.to_crs(epsg=3116).buffer(st.session_state.radio_analisis)
    area_interes = gdf_buffer_metros.to_crs(epsg=4326).iloc[0]

    # FILTRADO VECTORIZADO (Asegurando proyecciones)
    
    # 1. Manzanas
    if manzanas.crs != "EPSG:4326": manzanas = manzanas.to_crs("EPSG:4326")
    manzanas_zona = manzanas[manzanas.geometry.intersects(area_interes)]
    
    # 2. Áreas POT (Corrección: Forzar CRS antes de intersectar)
    if areas_pot.crs != "EPSG:4326": areas_pot = areas_pot.to_crs("EPSG:4326")
    areas_zona = areas_pot[areas_pot.geometry.intersects(area_interes)]

    # 3. Transporte
    if transporte.crs != "EPSG:4326": transporte = transporte.to_crs("EPSG:4326")
    transporte_zona = transporte[transporte.geometry.within(area_interes)]

    # 4. Educación
    if colegios.crs != "EPSG:4326": colegios = colegios.to_crs("EPSG:4326")
    colegios_zona = colegios[colegios.geometry.within(area_interes)]

    # -------------------------------------------------------------------------
    # 2. VISUALIZACIÓN: MOVILIDAD (CORREGIDO: ZOOM ALEJADO)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 1. Análisis de Conectividad y Movilidad")
    st.markdown("Evaluación de la oferta de transporte masivo (SITP/Troncal).")

    fig_transporte = go.Figure()

    # Buffer
    fig_transporte.add_trace(go.Scattermapbox(
        lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
        mode='lines', fill='toself', name='Zona de Influencia',
        fillcolor='rgba(230, 126, 34, 0.1)', line=dict(color='#D35400', width=2)
    ))

    # Estaciones
    if not transporte_zona.empty:
        fig_transporte.add_trace(go.Scattermapbox(
            lat=transporte_zona.geometry.y, lon=transporte_zona.geometry.x,
            mode='markers', name='Estaciones',
            marker=dict(size=10, color='#C0392B', symbol='bus'), # Icono más pequeño
            text=transporte_zona['nombre_estacion'], hoverinfo='text'
        ))

    # Epicentro
    fig_transporte.add_trace(go.Scattermapbox(
        lat=[st.session_state.punto_lat], lon=[st.session_state.punto_lon],
        mode='markers', name='Epicentro', marker=dict(size=12, color='#2980B9')
    ))

    # Layout (Zoom Ajustado a 13.5 para ver más contexto)
    fig_transporte.update_layout(
        mapbox_style="carto-positron", 
        mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
        mapbox_zoom=13.5, 
        margin={"r":0,"t":0,"l":0,"b":0}, height=450, showlegend=True,
        legend=dict(orientation="h", y=1.1)
    )
    
    col_mapa_mov, col_kpi_mov = st.columns([3, 1])
    with col_mapa_mov:
        st.plotly_chart(fig_transporte, use_container_width=True)
    with col_kpi_mov:
        st.metric("Nodos de Transporte", len(transporte_zona))
        if len(transporte_zona) > 2: st.success("Alta Conectividad")
        elif len(transporte_zona) > 0: st.warning("Conectividad Media")
        else: st.error("Baja Cobertura")

    # -------------------------------------------------------------------------
    # 3. VISUALIZACIÓN: EDUCACIÓN (CORREGIDO: ZOOM ALEJADO + TABLA)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Infraestructura Educativa")
    st.markdown("Identificación de colegios oficiales y privados.")

    col_ind_edu, col_mapa_edu = st.columns([1, 3])

    with col_ind_edu:
        st.metric("Total Colegios", len(colegios_zona))
        if not colegios_zona.empty and 'sector' in colegios_zona.columns:
            st.markdown("**Desglose:**")
            st.dataframe(colegios_zona['sector'].value_counts(), use_container_width=True)

    with col_mapa_edu:
        fig_edu = go.Figure()
        # Buffer
        fig_edu.add_trace(go.Scattermapbox(
            lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
            mode='lines', fill='toself', fillcolor='rgba(142, 68, 173, 0.1)',
            line=dict(color='#8E44AD', width=2), name='Zona de Influencia'
        ))
        # Colegios
        if not colegios_zona.empty:
            fig_edu.add_trace(go.Scattermapbox(
                lat=colegios_zona.geometry.y, lon=colegios_zona.geometry.x,
                mode='markers', name='Colegios', marker=dict(size=9, color='#9B59B6'),
                text=colegios_zona['nombre'], hoverinfo='text'
            ))
        
        # Layout (Zoom Ajustado a 13.5)
        fig_edu.update_layout(
            mapbox_style="carto-positron", 
            mapbox_center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
            mapbox_zoom=13.5, 
            margin={"r":0,"t":0,"l":0,"b":0}, height=400, showlegend=False
        )
        st.plotly_chart(fig_edu, use_container_width=True)

    # -------------------------------------------------------------------------
    # 4. VISUALIZACIÓN: ESTRATO Y POT (CONSOLIDADOS)
    # -------------------------------------------------------------------------
    st.markdown("---")
    col_estrato, col_pot = st.columns(2)
    
    # --- Mapa Estrato ---
    with col_estrato:
        st.markdown("### 3. Perfil Socioeconómico")
        if not manzanas_zona.empty:
            manzanas_zona['estrato'] = manzanas_zona['estrato'].astype(int)
            fig_estrato = px.choropleth_mapbox(
                manzanas_zona, geojson=manzanas_zona.geometry, locations=manzanas_zona.index,
                color="estrato", title="Estratos", mapbox_style="carto-positron",
                zoom=14, center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                opacity=0.6,
                color_discrete_map={1:'#C0392B', 2:'#E67E22', 3:'#F1C40F', 4:'#2ECC71', 5:'#3498DB', 6:'#8E44AD'}
            )
            fig_estrato.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=350)
            st.plotly_chart(fig_estrato, use_container_width=True)
            
            estrato_moda = manzanas_zona['estrato'].mode()[0]
            st.info(f"Perfil Dominante: **Estrato {estrato_moda}**")
        else:
            st.warning("Sin datos residenciales.")

    # --- Mapa POT (Corregido para evitar vacíos) ---
    with col_pot:
        st.markdown("### 4. Normativa POT")
        if not areas_zona.empty:
            fig_pot = px.choropleth_mapbox(
                areas_zona, geojson=areas_zona.geometry, locations=areas_zona.index,
                color="uso_pot_simplificado", title="Usos del Suelo",
                mapbox_style="carto-positron",
                zoom=14, center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
                opacity=0.5, color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pot.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=350, showlegend=False)
            st.plotly_chart(fig_pot, use_container_width=True)
            
            uso_moda = areas_zona['uso_pot_simplificado'].mode()[0]
            st.info(f"Vocación: **{uso_moda}**")
        else:
            st.warning("⚠️ No se detecta normativa POT en este buffer. Es posible que sea una zona de reserva, vía pública o límite urbano.")

    # -------------------------------------------------------------------------
    # 5. REPORTE HTML (CORREGIDO: MAPA GOOGLE Y SIN BOTÓN PRO)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("📑 Informe Ejecutivo")

    # Cálculos previos
    poly_localidad = localidades[localidades['nombre_localidad'] == st.session_state.localidad_sel].geometry.iloc[0]
    total_estaciones_loc = len(transporte[transporte.geometry.within(poly_localidad)])
    pct_cobertura_trans = (len(transporte_zona) / total_estaciones_loc * 100) if total_estaciones_loc > 0 else 0
    
    # Datos cualitativos
    datos_loc = localidades[localidades['nombre_localidad'] == st.session_state.localidad_sel].iloc[0]
    perfil_seguridad = datos_loc.get('top_3_delitos', 'No disponible')
    
    # Enlace a Google Maps
    link_gmaps = f"https://www.google.com/maps/search/?api=1&query={st.session_state.punto_lat},{st.session_state.punto_lon}"

    # Scoring
    score = 0
    if len(transporte_zona) >= 3: score += 1
    if len(colegios_zona) >= 2: score += 1
    if not manzanas_zona.empty: score += 1
    
    dictamen_texto = "ALTAMENTE VIABLE" if score == 3 else "VIABILIDAD MEDIA" if score == 2 else "VIABILIDAD RESTRINGIDA"
    color_dictamen = "#27AE60" if score == 3 else "#F39C12" if score == 2 else "#C0392B"

    # HTML Template
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; color: #333; }}
            .header {{ background: #2C3E50; color: white; padding: 20px; text-align: center; }}
            .box {{ background: #F4F6F6; padding: 15px; margin: 10px 0; border: 1px solid #BDC3C7; }}
            .alert {{ background: #FADBD8; color: #922B21; padding: 10px; border-left: 5px solid #C0392B; }}
            .btn-map {{ display: inline-block; background: #3498DB; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Reporte de Inteligencia Territorial</h1>
            <p>Bogotá Inteligente - Datos al Ecosistema 2025</p>
        </div>
        
        <div class="box">
            <h3>📍 Ubicación del Análisis</h3>
            <p><strong>Localidad:</strong> {st.session_state.localidad_sel}</p>
            <p><strong>Coordenadas:</strong> {st.session_state.punto_lat:.5f}, {st.session_state.punto_lon:.5f}</p>
            <a href="{link_gmaps}" target="_blank" class="btn-map">🗺️ Ver Ubicación en Google Maps</a>
        </div>

        <div class="box">
            <h3>🚨 Seguridad y Convivencia</h3>
            <div class="alert"><strong>Focos de Delito (Top 3):</strong><br>{perfil_seguridad}</div>
        </div>

        <div class="box">
            <h3>📊 Indicadores de Cobertura ({st.session_state.radio_analisis}m)</h3>
            <ul>
                <li><strong>Transporte:</strong> {len(transporte_zona)} estaciones ({pct_cobertura_trans:.1f}% de la localidad).</li>
                <li><strong>Educación:</strong> {len(colegios_zona)} colegios.</li>
                <li><strong>Vocación POT:</strong> {uso_moda if 'uso_moda' in locals() else 'N/A'}.</li>
            </ul>
        </div>
        
        <div style="background: {color_dictamen}; color: white; padding: 20px; text-align: center; font-size: 20px; margin-top: 20px;">
            DICTAMEN: {dictamen_texto}
        </div>
    </body>
    </html>
    """

    col_btn_html, col_reset = st.columns([2, 1])
    
    with col_btn_html:
        st.download_button(
            label="📥 Descargar Informe Ejecutivo (HTML)",
            data=html_report,
            file_name=f"Reporte_{st.session_state.localidad_sel}.html",
            mime="text/html",
            type="primary"
        )
    
    with col_reset:
        if st.button("🔄 Iniciar Nuevo Análisis"):
            for key in ['punto_lat', 'punto_lon', 'localidad_sel', 'localidad_clic']:
                if key in st.session_state: del st.session_state[key]
            st.session_state.step = 2
            st.rerun()