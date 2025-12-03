# importacion de librerias necesarioas
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# Configuración de la Página
st.set_page_config(
    page_title="Bogotá a un Clic",
    page_icon="💛", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# INICIO: MOSTRAR LOGO EN CABECERA
ruta_logo = "BACK_END/logo.png"

# columnas para centrarlo o ajustarlo
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])

with col_logo2:
    if os.path.exists(ruta_logo):
        
        st.image(ruta_logo, width=350, caption="Datos al Ecosistema 2025")
    else:
        # Fallback por si la imagen no carga
        st.title("🏙️ Bogotá Inteligente")
        st.warning(f"Nota: No se encontró el logo en '{ruta_logo}'")

st.markdown("---")

# Inyección de Estilos

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

# Encabezado y Bienvenida 
st.title("Bogotá Visible: Tu Barrio en Datos 🏙️")
st.subheader("Toma decisiones inteligentes sobre el territorio de tu ciudad.")

# Texto introductorio
st.markdown("""
<div class="intro-box">
    ¿Alguna vez te has preguntado qué tan seguro es realmente un barrio, qué colegios tiene cerca o qué se puede construir allí?<br><br>
    Esta herramienta conecta los <b>datos oficiales de la ciudad</b> contigo. Olvídate de los mapas complicados; aquí traducimos la información técnica en respuestas claras para que conozcas la vocación real de cualquier rincón de Bogotá.
</div>
""", unsafe_allow_html=True)

st.write("")

# Explicación de valor con iconos
col_info1, col_info2, col_info3, col_info4 = st.columns(4)

with col_info1:
    st.markdown("### 👮 Seguridad")
    st.info("Conoce el **Top 3 de delitos** reales. No es lo mismo un barrio donde roban celulares a uno con hurto de casas.")

with col_info2:
    st.markdown("### 🏡 Normativa")
    st.warning("Consulta el POT vigente. Descubre si tu vecino será un edificio residencial o una zona industrial ruidosa.")

with col_info3:
    st.markdown("### 🚌 Movilidad")
    st.success("Mide la conectividad real. Ubica las estaciones de **Transmilenio y SITP** a pasos de tu ubicación.")

with col_info4:
    st.markdown("### 🏫 Educación")
    st.error("Para las familias: encuentra la oferta de **Colegios Oficiales y Privados** en el sector.")

st.markdown("---")


# Función de Carga de Datos (Conectada a DATOS_LIMPIOS)
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
            
            # Lectura directa
            gdf = gpd.read_file(url_completa)
            
            
            if gdf.crs.to_string() != "EPSG:4326":
                gdf = gdf.to_crs("EPSG:4326")
                
            dataframes[nombre_clave] = gdf
            
        except Exception as e:
            errores.append(f"Error cargando capa {nombre_clave}: {str(e)}")
    
    if errores:
        for err in errores:
            st.error(err)
        return None
        
    return dataframes

# Inicialización del Estado
if "step" not in st.session_state:
    st.session_state.step = 1


# PASO 1: SINCRONIZACIÓN Y CARGA DE DATOS

if st.session_state.step == 1:
    st.markdown("### 🔌 Conectando con tu Ciudad")
    
    st.markdown("""
    Para darte un diagnóstico confiable, estamos conectando en tiempo real con el repositorio de **Datos Abiertos de Bogotá**.
    
    Este proceso garantiza que consultes la información más reciente sobre:
    * 🛡️ **Seguridad:** Datos directos de la Secretaría de Seguridad.
    * 🗺️ **Normativa:** Reglas de juego del POT (Decreto 555).
    * 🚌 **Infraestructura:** Red oficial de Transmilenio y Educación.
    """)

    # CSS PARA BOTÓN VERDE
    st.markdown("""
        <style>
        /* Forzamos el estilo del botón solo para que sea Verde Éxito */
        div.stButton > button {
            background-color: #27AE60 !important; /* Verde Esmeralda */
            color: white !important;
            font-weight: bold;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }
        div.stButton > button:hover {
            background-color: #2ECC71 !important; /* Verde más claro al pasar mouse */
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Usamos spinner
    with st.spinner("⏳ Sincronizando mapas y estadísticas oficiales... por favor espera."):
        try:
            # Ejecutamos la carga
            dataframes = cargar_datasets()
            
            if dataframes:
                # Guardamos en memoria silenciosamente
                st.session_state.update(dataframes)
                
                # Mensaje de  limpio
                st.success("✅ **¡Conexión Exitosa!** Todos los datos de Bogotá están listos para tu análisis.")
                
                st.markdown("---")
                
                # Botón de acción centrado 
                col_izq, col_centro, col_der = st.columns([1, 2, 1])
                with col_centro:
                    if st.button("📍 Comenzar a Explorar", use_container_width=True):
                        st.session_state.step = 2
                        st.rerun()
            else:
                st.error("❌ No pudimos conectar con los datos. Por favor revisa tu internet.")
                
        except Exception as e:
            st.error(f"Ocurrió un error técnico: {e}")


# PASO 2: SELECCIÓN DE LOCALIDAD (EXPERIENCIA MEJORADA)

elif st.session_state.step == 2:
    # CSS PERSONALIZADO PARA BOTONES
    st.markdown("""
        <style>
        /* 1. Estilo para el botón PRINCIPAL (Verde - Confirmar) */
        /* Buscamos botones con el atributo kind="primary" */
        div.stButton > button[kind="primary"] {
            background-color: #27AE60 !important;
            border-color: #27AE60 !important;
            color: white !important;
            font-size: 16px !important;
            border-radius: 8px !important;
            height: 50px !important;
            transition: all 0.3s ease;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #2ECC71 !important;
            border-color: #2ECC71 !important;
            transform: scale(1.02);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* 2. Estilo para el botón SECUNDARIO (Gris - Volver) */
        /* Buscamos botones normales (kind="secondary") */
        div.stButton > button[kind="secondary"] {
            background-color: #95A5A6 !important;
            border-color: #95A5A6 !important;
            color: white !important;
            border-radius: 8px !important;
            height: 50px !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #7F8C8D !important;
            border-color: #7F8C8D !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🗺️ Paso 2: Ubica tu Localidad")

    col_mapa, col_datos = st.columns([3, 1])

    with col_datos:
        st.markdown("### ¿Cómo funciona?")
        st.info("""
        Bogotá tiene 20 localidades, cada una con su propia identidad.
        
        👉 **Haz clic en el mapa** sobre la zona que te interesa investigar.
        
        El sistema te mostrará inmediatamente los **3 delitos más frecuentes** en esa zona para que conozcas el contexto real antes de seguir.
        """)
        
        st.markdown("---")
        # Botón de regreso
        if st.button("⬅ Volver al Inicio", type="secondary", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    with col_mapa:
        # Colores Identidad 
        COLOR_BASE = "#776314"     # Amarillo
        COLOR_LINEA = "#1B0BA8"    # Azul
        COLOR_HOVER = "#AA1A0F"    # Rojo 

        localidades = st.session_state.localidades
        centro_urbano = [4.6097, -74.0817] 

        m = folium.Map(
            location=centro_urbano, 
            zoom_start=11, 
            tiles="CartoDB positron",
            control_scale=True
        )
        
        folium.GeoJson(
            localidades,
            style_function=lambda feature: {
                "fillColor": COLOR_BASE,
                "color": COLOR_LINEA,
                "weight": 2,
                "fillOpacity": 0.5,
            },
            highlight_function=lambda feature: {
                "fillColor": COLOR_HOVER,
                "color": "white",
                "weight": 3,
                "fillOpacity": 0.7,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["nombre_localidad"],
                aliases=["Localidad:"],
                style="font-family: sans-serif; font-size: 14px;",
                sticky=True
            )
        ).add_to(m)

        output = st_folium(m, width=None, height=550, returned_objects=["last_clicked"])

    # Lógica de Selección y Ranking
    clicked = output.get("last_clicked")
    contenedor_resultado = st.container()

    if clicked and "lat" in clicked and "lng" in clicked:
        punto = Point(clicked["lng"], clicked["lat"])
        
        seleccion = None
        perfil_seguridad = "Sin datos"
        
        for _, row in localidades.iterrows():
            if row["geometry"].contains(punto):
                seleccion = row["nombre_localidad"]
                if "top_3_delitos" in row:
                    perfil_seguridad = row["top_3_delitos"]
                break
        
        if seleccion:
            st.session_state.localidad_clic = seleccion
            
            with contenedor_resultado:
                st.markdown("---")
                col_res1, col_res2, col_res3 = st.columns([1, 1.5, 1])
                
                with col_res1:
                    st.markdown(f"### 📍 {seleccion}")
                    st.caption("Has seleccionado esta zona.")
                
                with col_res2:
                    
                    st.markdown("**🚨 Top 3 Riesgos de Seguridad:**")
                    
                    if "," in perfil_seguridad:
                        delitos = perfil_seguridad.split(",")
                        html_lista = ""
                        iconos = ["🥇", "🥈", "🥉"] 
                        
                        for i, delito in enumerate(delitos):
                            if i < 3: 
                                texto_delito = delito.split(".")[-1].strip() if "." in delito else delito.strip()
                                html_lista += f"<div style='margin-bottom:5px; font-size:15px;'>{iconos[i]} <b>{texto_delito}</b></div>"
                        
                        st.markdown(html_lista, unsafe_allow_html=True)
                    else:
                        st.info(perfil_seguridad)
                
                with col_res3:
                    st.write("") 
                    st.write("") 
                    
                    if st.button("🔍 Analizar esta Zona", type="primary", use_container_width=True):
                        st.session_state.localidad_sel = seleccion
                        st.session_state.step = 3
                        st.rerun()


# PASO 3: DEFINICIÓN DEL ENTORNO DE ANÁLISIS

elif st.session_state.step == 3:
    st.header("📍 Paso 3: Define tu Entorno de Análisis")

    # CSS Botón Verde
    st.markdown("""
        <style>
        div.stButton > button[kind="primary"] {
            background-color: #27AE60 !important;
            color: white !important;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    
    # 1. BARRA LATERAL DE CONTROLES
    
    col_controles, col_mapa = st.columns([1, 2])

    with col_controles:
        
        st.markdown(f"### 1. Ubicación en {st.session_state.localidad_sel}")
        st.info("Haz clic en el mapa para marcar el punto exacto.")
        
        st.markdown("---")
        
        st.markdown("### 2. Alcance")
        radio_analisis = st.select_slider(
            "¿Qué tan lejos quieres mirar?",
            options=[300, 600, 900, 1200, 1500, 1800, 2100],
            value=st.session_state.get('radio_analisis', 600),
            help="Define el radio del círculo rojo en el mapa."
        )
        st.session_state.radio_analisis = radio_analisis

        tiempo_caminata = int(radio_analisis / 80)
        if radio_analisis <= 600:
            desc_radio = "🚶‍♂️ **Vecindario (5-8 min):** Comercio local."
        elif radio_analisis <= 1200:
            desc_radio = "🚲 **Barrio (10-15 min):** Colegios y rutas."
        else:
            desc_radio = "🚗 **Zona Amplia:** Impacto zonal."
            
        st.caption(f"{desc_radio}")

    
    # 2. MAPA INTERACTIVO  CENTRADO DINÁMICO
    
    with col_mapa:
        localidades = st.session_state.localidades
        localidad_geo = localidades[localidades["nombre_localidad"] == st.session_state.localidad_sel]
        
        bounds = localidad_geo.total_bounds
        
        
        if "punto_lat" in st.session_state:
            # Si hay pin, centramos en el pin y hacemos ZOOM IN 
            centro_mapa = [st.session_state.punto_lat, st.session_state.punto_lon]
            zoom_inicial = 15
        else:
            # Si no hay pin, centramos en la localidad con ZOOM OUT 
            centro_mapa = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
            zoom_inicial = 13

        m = folium.Map(
            location=centro_mapa,
            zoom_start=zoom_inicial,
            tiles="CartoDB positron",
            control_scale=True
        )

        folium.GeoJson(
            localidad_geo,
            style_function=lambda x: {
                "fillColor": "#F1C40F",
                "color": "#7F8C8D",
                "weight": 2,
                "fillOpacity": 0.1,
                "dashArray": "5, 5"
            }
        ).add_to(m)

        m.get_root().html.add_child(folium.Element("""
            <style>.leaflet-container { cursor: crosshair !important; }</style>
        """))

        if "punto_lat" in st.session_state:
            folium.Marker(
                [st.session_state.punto_lat, st.session_state.punto_lon],
                icon=folium.Icon(color="red", icon="info-sign"),
                tooltip="Punto de Análisis"
            ).add_to(m)
            
            folium.Circle(
                location=[st.session_state.punto_lat, st.session_state.punto_lon],
                radius=st.session_state.radio_analisis,
                color="#E74C3C",
                fill=True,
                fill_opacity=0.2
            ).add_to(m)

        mapa_output = st_folium(m, width=None, height=500, returned_objects=["last_clicked"])

    
    # 3. LÓGICA Y BOTONES
    
    
    clicked = mapa_output.get("last_clicked")
    if clicked and "lat" in clicked and "lng" in clicked:
        punto_temp = Point(clicked["lng"], clicked["lat"])
        
        if localidad_geo.geometry.iloc[0].contains(punto_temp):
            st.session_state.punto_lat = clicked["lat"]
            st.session_state.punto_lon = clicked["lng"]
            st.rerun() 
        else:
            st.toast("⚠️ El punto está fuera de la localidad. Intenta más adentro.", icon="🚫")

    st.markdown("---")
    
    col_atras, col_accion = st.columns([1, 4])
    
    with col_atras:
        
        if st.button("⬅ Atrás"):
            # Borramos el punto para que si vuelve a entrar, el mapa esté limpio
            for key in ['punto_lat', 'punto_lon']:
                if key in st.session_state: del st.session_state[key]
            st.session_state.step = 2
            st.rerun()
            
    with col_accion:
        if "punto_lat" in st.session_state:
            if st.button("🚀 Generar Diagnóstico Completo", type="primary", use_container_width=True):
                st.session_state.step = 5
                st.rerun()
        else:
            st.info("👈 Por favor, haz clic en el mapa para continuar.")



# PASO 5: RESULTADOS DEL ANÁLISIS (DASHBOARD FINAL)

elif st.session_state.step == 5:
    st.header("📊 Resultados de tu Análisis")

    st.info(f"""
    **Estás analizando:** Un radio de **{st.session_state.radio_analisis} metros** a la redonda.
    📍 **Punto exacto:** En la localidad de **{st.session_state.localidad_sel}**.
    """)

    
    # 1. MOTOR DE CÁLCULO ESPACIAL
    
    localidades = st.session_state.localidades
    manzanas    = st.session_state.manzanas
    transporte  = st.session_state.transporte
    colegios    = st.session_state.colegios
    areas_pot   = st.session_state.areas

    # 1.1 Buffer de Análisis
    punto_ref = Point(st.session_state.punto_lon, st.session_state.punto_lat)
    gdf_punto = gpd.GeoDataFrame([{'geometry': punto_ref}], crs="EPSG:4326")
    gdf_buffer = gdf_punto.to_crs(epsg=3116).buffer(st.session_state.radio_analisis).to_crs(epsg=4326)
    area_interes = gdf_buffer.iloc[0]

    # 1.2 Asegurar Proyecciones Idénticas
    if transporte.crs != "EPSG:4326": transporte = transporte.to_crs("EPSG:4326")
    if colegios.crs != "EPSG:4326": colegios = colegios.to_crs("EPSG:4326")
    if manzanas.crs != "EPSG:4326": manzanas = manzanas.to_crs("EPSG:4326")
    if areas_pot.crs != "EPSG:4326": areas_pot = areas_pot.to_crs("EPSG:4326")

    # 1.3 Cruces Espaciales 
    transporte_zona = transporte[transporte.geometry.intersects(area_interes)]
    colegios_zona = colegios[colegios.geometry.intersects(area_interes)]
    manzanas_zona = manzanas[manzanas.geometry.intersects(area_interes)]

    
    # SECCIÓN 1: MOVILIDAD
   
    st.markdown("---")
    st.markdown("### 🚌 1. ¿Qué tan fácil es moverse?")
    st.markdown("Analizamos qué opciones de transporte público (Transmilenio y SITP) tienes 'a la mano'.")

    col_mapa_mov, col_data_mov = st.columns([2, 1])

    with col_mapa_mov:
        fig_t = go.Figure()
        # Zona
        fig_t.add_trace(go.Scattermapbox(
            lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
            mode='lines', fill='toself', name='Zona analizada',
            fillcolor='rgba(255, 165, 0, 0.1)', line=dict(color='orange', width=2)
        ))
        # Estaciones
        if not transporte_zona.empty:
            fig_t.add_trace(go.Scattermapbox(
                lat=transporte_zona.geometry.y, lon=transporte_zona.geometry.x,
                mode='markers', name='Paraderos',
                marker=dict(size=10, color='#E74C3C', symbol='circle'),
                text=transporte_zona['nombre_estacion'], hoverinfo='text'
            ))
        # Tú
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
            st.success("✅ **Excelente Conectividad:**\nTienes muchas opciones de ruta cerca.")
        elif cant_t > 0:
            st.warning("⚠️ **Conectividad Media:**\nTienes transporte, pero quizás debas caminar un poco.")
        else:
            st.error("❌ **Zona Apartada:**\nDependerás de vehículo particular o caminatas largas.")

    
    # SECCIÓN 2: EDUCACIÓN
    
    st.markdown("---")
    st.markdown("### 🏫 2. ¿Dónde pueden estudiar tus hijos?")
    st.markdown("Ubicación de colegios oficiales y privados en el vecindario.")

    col_mapa_edu, col_data_edu = st.columns([2, 1])

    with col_mapa_edu:
        fig_e = go.Figure()
        fig_e.add_trace(go.Scattermapbox(
            lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]),
            mode='lines', fill='toself', name='Zona analizada',
            fillcolor='rgba(155, 89, 182, 0.1)', line=dict(color='#8E44AD', width=2)
        ))
        if not colegios_zona.empty:
            fig_e.add_trace(go.Scattermapbox(
                lat=colegios_zona.geometry.y, lon=colegios_zona.geometry.x,
                mode='markers', name='Colegios',
                marker=dict(size=9, color='#8E44AD', symbol='circle'),
                text=colegios_zona['nombre'], hoverinfo='text'
            ))
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
        cant_c = len(colegios_zona)
        st.metric("Total Colegios", cant_c)
        
        if cant_c > 3:
            st.success("✅ **Alta Oferta Educativa:**\nVariedad de opciones para las familias.")
        elif cant_c > 0:
            st.info("ℹ️ **Oferta Moderada:**\nColegios accesibles en el sector.")
        else:
            st.error("❌ **Déficit Educativo:**\nNo se identifican colegios en el radio inmediato.")

        if not colegios_zona.empty:
            st.caption("Por tipo:")
            st.dataframe(colegios_zona['sector'].value_counts(), use_container_width=True)

    
    # SECCIÓN 3: ESTRATIFICACIÓN
    
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
            fig_s.add_trace(go.Scattermapbox(lat=list(area_interes.exterior.xy[1]), lon=list(area_interes.exterior.xy[0]), mode='lines', line=dict(color='black', width=2), name='Límite'))
            st.plotly_chart(fig_s, use_container_width=True)
        with col_data_soc:
            st.info(f"Moda: **Estrato {manzanas_zona['estrato'].mode()[0]}**")
            conteo_est = manzanas_zona['estrato'].value_counts().sort_index()
            fig_b = go.Figure(data=[go.Bar(x=[f"E{i}" for i in conteo_est.index], y=conteo_est.values, marker_color='#95A5A6')])
            fig_b.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_b, use_container_width=True)
    else:
        st.warning("Sin datos residenciales.")

    

    
    # SECCIÓN 4: POT 
    
    st.markdown("---")
    st.markdown("### 🏗️ 4. ¿Qué se permite construir? (POT)")
    st.markdown("Vocación normativa proyectada sobre cada manzana del sector.")

    # 1. Copia de seguridad
    manzanas_final = manzanas_zona.copy()
    clasificacion_exitosa = False

    # Solo para ver si hay datos cargados
    # st.write(f"Cantidad de áreas POT cargadas: {len(areas_pot)}")
    # st.write(f"CRS Manzanas: {manzanas_final.crs}")
    # st.write(f"CRS Áreas POT: {areas_pot.crs}")

    if not manzanas_final.empty and not areas_pot.empty:
        try:
            # Asegurar CRS idéntico
            if areas_pot.crs != manzanas_final.crs:
                areas_pot = areas_pot.to_crs(manzanas_final.crs)

            # Reparar geometrías inválidas 
            areas_pot['geometry'] = areas_pot.geometry.buffer(0)
            manzanas_final['geometry'] = manzanas_final.geometry.buffer(0)

            # CRUCE ESPACIAL
            
            # Esto atrapa la manzana si aunque sea un pedacito toca el área del POT.
            cruce = gpd.sjoin(
                manzanas_final,  # Usamos el polígono completo, no el centroide
                areas_pot[['uso_pot_simplificado', 'geometry']], 
                how='left', 
                predicate='intersects' 
            )
            
            # Limpieza de duplicados
            
            # (Simplificación: nos quedamos con la primera que encuentre para no complicar el código)
            cruce = cruce[~cruce.index.duplicated(keep='first')]
            
            # Asignar
            manzanas_final['uso_pot_simplificado'] = cruce['uso_pot_simplificado']
            
            # Rellenar nulos
            manzanas_final['uso_pot_simplificado'] = manzanas_final['uso_pot_simplificado'].fillna('Sin Clasificación')
            
            # Validar si logramos clasificar algo
            if len(manzanas_final[manzanas_final['uso_pot_simplificado'] != 'Sin Clasificación']) > 0:
                clasificacion_exitosa = True
            
        except Exception as e:
            st.error(f"Error técnico en el cruce: {str(e)}")
            manzanas_final['uso_pot_simplificado'] = 'Sin Clasificación'
    else:
        st.warning("No hay datos de POT cargados o manzanas seleccionadas.")
        manzanas_final['uso_pot_simplificado'] = 'Sin Clasificación'

    
    # VISUALIZACIÓN
    
    col_mapa_pot, col_data_pot = st.columns([2, 1])
    
    with col_mapa_pot:
        # Definir colores
        cats = manzanas_final["uso_pot_simplificado"].unique().tolist()
        palette = px.colors.qualitative.Bold # Usamos colores fuertes
        
        
        color_map = {}
        for i, cat in enumerate(cats):
            if cat == "Sin Clasificación":
                color_map[cat] = "#95A5A6" # Gris
            else:
                color_map[cat] = palette[i % len(palette)]
        
        fig_p = px.choropleth_mapbox(
            manzanas_final, 
            geojson=manzanas_final.geometry, 
            locations=manzanas_final.index,
            color="uso_pot_simplificado", 
            color_discrete_map=color_map,
            mapbox_style="carto-positron", 
            zoom=14.5,
            center={"lat": st.session_state.punto_lat, "lon": st.session_state.punto_lon},
            opacity=0.6,
            title="Vocación del Suelo"
        )
        fig_p.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=350, showlegend=True)
        
        # Línea de límite
        if 'area_interes' in locals():
             fig_p.add_trace(go.Scattermapbox(
                lat=list(area_interes.exterior.xy[1]), 
                lon=list(area_interes.exterior.xy[0]), 
                mode='lines', 
                line=dict(color='black', width=2), 
                name='Zona'
            ))
        st.plotly_chart(fig_p, use_container_width=True)

    with col_data_pot:
        conteo = manzanas_final['uso_pot_simplificado'].value_counts()
        
        # Verificar si hay datos reales
        hay_datos = not (len(conteo) == 1 and 'Sin Clasificación' in conteo)
        
        if clasificacion_exitosa and hay_datos:
            moda = conteo.index[0]
            st.info(f"Uso predominante: **{moda}**")
            
            # Usar los mismos colores del mapa
            colores_barras = [color_map.get(x, '#333') for x in conteo.index]
            
            fig_bp = go.Figure(data=[go.Bar(
                y=[str(x)[:25] for x in conteo.index], 
                x=conteo.values, 
                orientation='h',
                marker_color=colores_barras
            )])
            fig_bp.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bp, use_container_width=True)
        else:
            st.warning("⚠️ No se cruzó información.")
            st.markdown("""
            **Posibles causas:**
            1. El dataset de 'Áreas' está vacío o no cubre esta zona.
            2. Las coordenadas están desplazadas (revisa el CRS).
            """)
            # Botón de depuración
            if st.checkbox("Ver datos crudos del POT"):
                st.write(areas_pot.head())

    
    # SEGURIDAD 
    
    st.markdown("---")
    st.markdown("### 🛡️ Contexto de Seguridad")
    
    localidad_actual = st.session_state.localidad_sel
    datos_loc = localidades[localidades['nombre_localidad'] == localidad_actual].iloc[0]
    seguridad_raw = datos_loc.get('top_3_delitos', 'Dato no disponible')
    
    # Formato Lista para Seguridad
    if "," in seguridad_raw:
        items = seguridad_raw.split(",")
        lista_html = "".join([f"<li>{i.strip()}</li>" for i in items])
        texto_seg = f"<ul>{lista_html}</ul>"
    else:
        texto_seg = seguridad_raw

    st.markdown(f"""
    <div style="background-color: #FDEDEC; padding: 15px; border-left: 5px solid #C0392B; border-radius: 5px;">
        <h4 style="color: #922B21; margin:0;">🚨 En {localidad_actual} ten cuidado con:</h4>
        {texto_seg}
    </div>
    """, unsafe_allow_html=True)

# PASO 5: REPORTE EJECUTIVO (VERSIÓN FINAL - MAPA DETALLADO Y TEXTOS)

if st.session_state.step == 5: 
    import base64
    import plotly.graph_objects as go
    import geopandas as gpd

    st.markdown("---")
    st.header("📑 Informe Ejecutivo")

    # RECUPERACIÓN Y PROCESAMIENTO DE DATOS
    
    # Recuperar Dataframe de Manzanas
    # Intentamos recuperar la variable ya procesada. Si no existe, usamos la zona base.
    if 'manzanas_final' in locals() and not manzanas_final.empty:
        df_reporte = manzanas_final.copy()
    else:
        df_reporte = manzanas_zona.copy()
        # Cruce con POT si la columna no existe
        if not areas_pot.empty and 'uso_pot_simplificado' not in df_reporte.columns:
            try:
                if areas_pot.crs != df_reporte.crs:
                    areas_pot = areas_pot.to_crs(df_reporte.crs)
                cruce = gpd.sjoin(df_reporte, areas_pot[['uso_pot_simplificado', 'geometry']], how='left', predicate='intersects')
                cruce = cruce[~cruce.index.duplicated(keep='first')]
                df_reporte['uso_pot_simplificado'] = cruce['uso_pot_simplificado']
            except:
                pass 

    # Calcular KPIs (Los 5 puntos clave)
    
    # 1. Transporte (Cantidad)
    num_tm = len(transporte_zona)
    
    # 2. Educación (Cantidad)
    num_col = len(colegios_zona)
    
    # 3. Normativa (POT) - Moda
    if 'uso_pot_simplificado' not in df_reporte.columns:
        df_reporte['uso_pot_simplificado'] = "Sin Clasificación"
    uso_moda = df_reporte['uso_pot_simplificado'].fillna("Sin Clasificación").mode()[0]
    
    # 4. Estratificación (Moda)
    try:
        if 'estrato' in df_reporte.columns:
            estrato_moda = int(df_reporte['estrato'].mode()[0])
        else:
            estrato_moda = "N/A"
    except:
        estrato_moda = "N/A"

    # 5. Seguridad
    localidad = st.session_state.localidad_sel
    datos_loc = localidades[localidades['nombre_localidad'] == localidad].iloc[0]
    seguridad_texto = datos_loc.get('top_3_delitos', 'No disponible')
    
    # Formatear seguridad en lista vertical
    if "," in seguridad_texto:
        items_seg = seguridad_texto.split(",")
        lista_seguridad_html = "<ul style='margin-top:5px; margin-bottom:5px;'>"
        for item in items_seg:
            lista_seguridad_html += f"<li>{item.strip()}</li>"
        lista_seguridad_html += "</ul>"
    else:
        lista_seguridad_html = f"<p>{seguridad_texto}</p>"

    # Variables de Contexto
    radio = st.session_state.radio_analisis
    lat, lon = st.session_state.punto_lat, st.session_state.punto_lon

    # ALGORITMO DE SCORING VIABILIDAD
    score = 0
    if num_tm >= 2: score += 1
    if num_col >= 1: score += 1
    if uso_moda != "Sin Clasificación": score += 1
    
    dictamen = "VIABILIDAD ALTA" if score == 3 else "VIABILIDAD MEDIA" if score == 2 else "VIABILIDAD RESTRINGIDA"
    color_fondo = "#27AE60" if score == 3 else "#F39C12" if score == 2 else "#C0392B" #

    # GENERACIÓN DE IMAGEN
    with st.spinner("Generando mapa detallado con estaciones y colegios..."):
        try:
            fig_mapa = go.Figure()

            # Radio de Influencia
            if 'area_interes' in locals():
                lats_poly = list(area_interes.exterior.xy[1])
                lons_poly = list(area_interes.exterior.xy[0])
                fig_mapa.add_trace(go.Scattermapbox(
                    lat=lats_poly, lon=lons_poly,
                    mode='lines', fill='toself',
                    fillcolor='rgba(52, 152, 219, 0.1)',
                    line=dict(color='#3498DB', width=2),
                    name='Zona'
                ))

            # Estaciones de Transmilenio
            if not transporte_zona.empty:
                fig_mapa.add_trace(go.Scattermapbox(
                    lat=transporte_zona.geometry.y,
                    lon=transporte_zona.geometry.x,
                    mode='markers',
                    marker=dict(size=8, color='#E74C3C'), # Rojo
                    name='Estaciones'
                ))

            # Colegios
            if not colegios_zona.empty:
                fig_mapa.add_trace(go.Scattermapbox(
                    lat=colegios_zona.geometry.y,
                    lon=colegios_zona.geometry.x,
                    mode='markers',
                    marker=dict(size=8, color='#8E44AD'), # Morado
                    name='Colegios'
                ))

            # El PIN del Usuario
            fig_mapa.add_trace(go.Scattermapbox(
                lat=[lat], lon=[lon],
                mode='markers',
                marker=dict(size=15, color='black', symbol='marker'),
                name='Ubicación'
            ))

            fig_mapa.update_layout(
                mapbox_style="carto-positron",
                mapbox_zoom=14.5,
                mapbox_center={"lat": lat, "lon": lon},
                margin={"r":0,"t":0,"l":0,"b":0},
                showlegend=False
            )
            
            # Exportar a Base64 para poder incrustar en HTML
            img_bytes = fig_mapa.to_image(format="png", width=600, height=350, scale=2)
            b64_mapa = base64.b64encode(img_bytes).decode('utf-8')
            html_mapa = f'<img src="data:image/png;base64,{b64_mapa}" style="width:100%; border-radius:8px; border:1px solid #ccc;">'
            
        except Exception as e:
            html_mapa = f"<div style='padding:20px; background:#f0f0f0;'>Mapa no disponible ({str(e)})</div>"
    

    
    # PLANTILLA HTML (TEXTOS Y TABLAS) lo que el usuario se lleva
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Helvetica', sans-serif; max-width: 800px; margin: 0 auto; color: #333; }}
            .header {{ text-align: center; padding: 25px; background: #2C3E50; color: white; border-radius: 0 0 10px 10px; }}
            .card {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .intro-text {{ font-size: 14px; color: #555; font-style: italic; margin-bottom: 15px; text-align: justify; }}
            
            /* Estilo Tabla KPI */
            .kpi-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            .kpi-table th {{ background-color: #F4F6F7; padding: 10px; text-align: center; border: 1px solid #ddd; font-size: 12px; color: #777; }}
            .kpi-table td {{ padding: 15px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; color: #2C3E50; }}
            
            .dictamen-box {{ margin-top: 20px; padding: 20px; background: {color_fondo}; color: white; text-align: center; border-radius: 8px; }}
            .security-box {{ margin-top: 10px; padding: 15px; background: #FDEDEC; border-left: 5px solid #C0392B; color: #922B21; }}
        </style>
    </head>
    <body>
        <div class="header">
            
            <h1 style="margin:0;">Ficha de Inteligencia Territorial</h1>
            <p style="margin:5px 0 0;">Bogotá D.C. | Localidad {localidad}</p>
        </div>

        <div class="card">
            <h3 style="margin-top:0; border-bottom: 1px solid #eee; padding-bottom: 10px;">📍 Análisis de Entorno y Cobertura</h3>
            
            <p class="intro-text">
                Una vez evaluada la zona seleccionada en las coordenadas ({lat:.4f}, {lon:.4f}) con un radio de {radio} metros, 
                es importante determinar los factores de infraestructura y normativa detallados en las ayudas siguientes:
            </p>
            
            {html_mapa}
            
            <table class="kpi-table">
                <tr>
                    <th>ESTACIONES TM (Rojo)</th>
                    <th>COLEGIOS (Morado)</th>
                    <th>ESTRATO MODA</th>
                    <th>DOMINIO DE POT</th>
                </tr>
                <tr>
                    <td>{num_tm}</td>
                    <td>{num_col}</td>
                    <td>{estrato_moda}</td>
                    <td style="font-size:14px;">{uso_moda}</td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h3 style="margin-top:0; border-bottom: 1px solid #eee; padding-bottom: 10px;">🛡️ Contexto de Seguridad</h3>
            
            <p class="intro-text">
                A nivel de la localidad de {localidad}, es prudente destacar que el entorno de seguridad se caracteriza 
                por la prevalencia de los siguientes incidentes de alto impacto:
            </p>
            
            <div class="security-box">
                {lista_seguridad_html}
            </div>
        </div>

        <div class="dictamen-box">
            <p style="margin:0; font-size:14px; opacity:0.9;">DICTAMEN TÉCNICO</p>
            <h2 style="margin:5px 0 0; font-size:24px;">{dictamen}</h2>
            <p style="margin-top:10px; font-size:12px;">De acuerdo con el análisis algorítmico de puntuación aditiva.</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 11px;">
            Reporte generado automáticamente el 28/11/2025
        </div>
    </body>
    </html>
    """

    # ZONA DE DESCARGA Y REINICIO
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""<style>div.stDownloadButton > button {background-color: #27AE60 !important; color: white !important; border-color: #1E8449 !important; font-weight: bold !important; width: 100%;}</style>""", unsafe_allow_html=True)
        st.download_button(
            label="📥 Descargar Ficha Técnica (PDF/HTML)",
            data=html_report,
            file_name=f"Ficha_{localidad}.html",
            mime="text/html"
        )
        
    with col2:
        if st.button("🔄 Nuevo Análisis"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.step = 1 # Volver al inicio real
            st.rerun()
