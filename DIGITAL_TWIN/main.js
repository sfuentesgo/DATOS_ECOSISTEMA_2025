//---------------------------------------------------
// 1. CONFIGURACIÓN INICIAL Y TOKEN
//---------------------------------------------------
// Tu Token real (Es necesario para cargar los Google 3D Tiles)
Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3NmY0NDc1NS0wNTI1LTQ5MzktODU4Yi04MzEyZDBhNGQ1OGMiLCJpZCI6MzY3NDIwLCJpYXQiOjE3NjUxMjUyNzJ9.rNorYTcXLUMNiocHyuT9VPqrMUdC6yHvbKq8kW-PVds";

// Parámetros por defecto (Bogotá Centro)
const defaults = {
    lat: 4.6097,
    lon: -74.0817,
    zoom: 15, // En Cesium esto se controla con la altura (range)
    radio: 600
};

// Función para leer parámetros de la URL (Lo que envía Streamlit)
function getParam(name, fallback) {
    const url = new URLSearchParams(window.location.search);
    if (url.has(name)) {
        const v = url.get(name);
        const n = Number(v);
        // Si es lat/lon devuelve número, si es texto devuelve texto
        return isNaN(n) ? v : n;
    }
    return fallback;
}

// Capturamos las variables
const lat = getParam("lat", defaults.lat);
const lon = getParam("lon", defaults.lon);
let radio = getParam("radio", defaults.radio);

// Actualizamos el panel HTML (Asegúrate que estos IDs existan en tu index.html)
const divInfo = document.getElementById("info-coords");
if (divInfo) {
    divInfo.innerHTML = `<b>Lat:</b> ${lat.toFixed(4)} <br> <b>Lon:</b> ${lon.toFixed(4)}`;
}

//---------------------------------------------------
// 2. INICIALIZAR VISOR (EL MOTOR 3D)
//---------------------------------------------------
async function initCesium() {
    
    // A. Crear el Visor
        viewer = new Cesium.Viewer("cesiumContainer", {
        terrain: Cesium.Terrain.fromWorldTerrain(), // Terreno mundial base
        animation: false,
        timeline: false,
        baseLayerPicker: false, // Ocultamos selector para que se vea limpio
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        navigationHelpButton: false,
        infoBox: true,
        selectionIndicator: true
    });

    // Limpieza visual (créditos discretos)
    viewer._cesiumWidget._creditContainer.style.display = "none"; 

    // B. MOVER LA CÁMARA (CRÍTICO: Sin esto, no ves tu punto)
    viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(lon, lat, 2000), // 2000m de altura inicial
        orientation: {
            heading: Cesium.Math.toRadians(0.0), // Mirando al Norte
            pitch: Cesium.Math.toRadians(-35.0), // Inclinación "Vuelo de pájaro"
            roll: 0.0
        }
    });

    // C. CARGAR LOS EDIFICIOS 3D DE GOOGLE (El "Digital Twin")
    // Esto es lo que hace que se vea real. Asset ID 2275207 es el estándar.
    try {
        const tileset = await Cesium.Cesium3DTileset.fromIonAssetId(2275207);
        viewer.scene.primitives.add(tileset);
        console.log("✅ Gemelo Digital (Google 3D Tiles) cargado.");
    } catch (error) {
        console.error("❌ Error cargando Google 3D Tiles (Verifica tu Token):", error);
    }

    // Aquí llamaremos a la carga de datos (Paso siguiente)
    // cargarCapas(viewer); 
}

//---------------------------------------------------
// 3. RUTAS DE DATOS (Corrección de URL)
//---------------------------------------------------
// Usamos 'raw.githubusercontent.com' para evitar problemas de redirección
const baseURL = "https://raw.githubusercontent.com/andres-fuentex/CONCURSO/main/DATOS_LIMPIOS/";

const files = {
    localidades: baseURL + "dim_localidad.geojson",
    manzanas:    baseURL + "tabla_hechos.geojson",
    transporte:  baseURL + "dim_transporte.geojson",
    colegios:    baseURL + "dim_colegios.geojson",
    salud:       baseURL + "dim_salud.geojson",
    verde:       baseURL + "dim_verde.geojson",
    pot:         baseURL + "dim_area.geojson"
};

// Iniciamos



//---------------------------------------------------
// FUNCIONES DE ESTILO (CORREGIDAS)
//---------------------------------------------------

// 1. Localidad — polígonos azules (CLAMP TO GROUND para que se pegue al terreno)
function styleLocalidad(ent) {
    if (ent.polygon) {
        ent.polygon.material = Cesium.Color.fromCssColorString("#0047FF").withAlpha(0.2); // Más transparente
        ent.polygon.outline = true;
        ent.polygon.outlineColor = Cesium.Color.fromCssColorString("#0047FF");
        ent.polygon.outlineWidth = 3;
        // CRÍTICO: Esto hace que se pinte SOBRE los edificios 3D
        ent.polygon.classificationType = Cesium.ClassificationType.CESIUM_3D_TILE; 
    }
}

// 2. Manzanas — Extrusión (Cuidado: esto atraviesa los edificios 3D)
function styleManzana(ent) {
    if (!ent.polygon) return;

    // Forma segura de leer propiedades en Cesium
    const props = ent.properties;
    let estrato = 0;
    
    // Verificamos si existe la propiedad 'estrato'
    if (props && props.hasProperty('estrato')) {
        estrato = Number(props.estrato.getValue(Cesium.JulianDate.now()));
    }

    const altura = estrato > 0 ? estrato * 15 : 5; // Ajusté altura para no tapar todo
    const color = Cesium.Color.fromCssColorString("#F1C40F").withAlpha(0.6);

    ent.polygon.material = color;
    ent.polygon.extrudedHeight = altura;
    ent.polygon.outline = false;
}

// 3. Transporte — puntos rojos (CLAMP TO GROUND)
function styleTransporte(ent) {
    if (ent.point) {
        ent.point.pixelSize = 12; // Un poco más grandes
        ent.point.color = Cesium.Color.RED;
        ent.point.outlineColor = Cesium.Color.WHITE;
        ent.point.outlineWidth = 2;
        // CRÍTICO: Evita que el punto quede enterrado bajo el edificio
        ent.point.heightReference = Cesium.HeightReference.CLAMP_TO_GROUND;
    }
}

// 4. Colegios — puntos morados
function styleColegios(ent) {
    if (ent.point) {
        ent.point.pixelSize = 10;
        ent.point.color = Cesium.Color.fromCssColorString("#9B59B6");
        ent.point.outlineColor = Cesium.Color.WHITE;
        ent.point.outlineWidth = 1;
        ent.point.heightReference = Cesium.HeightReference.CLAMP_TO_GROUND;
    }
}

// 5. Salud — puntos azul oscuro (Cruz simulada con outline grueso)
function styleSalud(ent) {
    if (ent.point) {
        ent.point.pixelSize = 14;
        ent.point.color = Cesium.Color.fromCssColorString("#0905F7");
        ent.point.outlineColor = Cesium.Color.WHITE;
        ent.point.outlineWidth = 2;
        ent.point.heightReference = Cesium.HeightReference.CLAMP_TO_GROUND;
    }
}

// 6. Verde — polígonos verdes (Pintar sobre el suelo)
function styleVerde(ent) {
    if (ent.polygon) {
        ent.polygon.material = Cesium.Color.fromCssColorString("#27AE60").withAlpha(0.6);
        ent.polygon.outline = false; // Sin borde para que se vea más natural
        // Pinta encima de los Google 3D Tiles
        ent.polygon.classificationType = Cesium.ClassificationType.CESIUM_3D_TILE;
    }
}

// 7. POT — CORRECCIÓN DE CATEGORÍAS (Match con Python)
function colorPOT(cat) {
    // Estas llaves deben ser idénticas a lo que sale de tu Python (mapeo_pot)
    const map = {
        "Comercio y Servicios Locales": "#E67E22", // Naranja
        "Residencial Mixto": "#3498DB",            // Azul
        "Empresarial e Industrial": "#8E44AD",     // Morado
        "Grandes Dotacionales": "#2ECC71",         // Verde
        "Alta Densidad / VIS": "#C0392B",          // Rojo Ladrillo
        "Histórico y Patrimonial": "#F1C40F",      // Amarillo
        "Otro / Sin Clasificar": "#95A5A6"         // Gris
    };
    // Búsqueda parcial por si acaso (ej. "Residencial" encuentra el color)
    for (const key in map) {
        if (cat.includes(key)) return map[key];
    }
    return "#95A5A6"; // Default
}

function stylePOT(ent) {
    const props = ent.properties;
    let categoria = "Otro";

    if (props && props.hasProperty('uso_pot_simplificado')) {
        categoria = props.uso_pot_simplificado.getValue(Cesium.JulianDate.now());
    }

    const col = Cesium.Color.fromCssColorString(colorPOT(categoria));

    if (ent.polygon) {
        ent.polygon.material = col.withAlpha(0.3); // Relleno suave
        ent.polygon.outline = true;
        ent.polygon.outlineColor = col;
        ent.polygon.outlineWidth = 2;
        // Pintar sobre el terreno 3D
        ent.polygon.classificationType = Cesium.ClassificationType.CESIUM_3D_TILE;
    }
}

//---------------------------------------------------
// VARIABLES GLOBALES (Para que todo el script las vea)
//---------------------------------------------------
let viewer; // El visor 3D
let radioEntity = null; // El círculo amarillo

//---------------------------------------------------
// 8. CARGA UTILITARIA DE GEOJSON (ROBUSTA)
//---------------------------------------------------
async function loadLayer(name, url, styleFn) {
    try {
        console.log(`⏳ Cargando capa: ${name}...`);
        
        // Cargar GeoJSON
        const ds = await Cesium.GeoJsonDataSource.load(url, {
            clampToGround: true // Intentar pegar al suelo por defecto
        });

        // Aplicar Estilos Personalizados
        const entities = ds.entities.values;
        for (let i = 0; i < entities.length; i++) {
            const ent = entities[i];
            styleFn(ent); // Tu función de estilo específica
        }

        // Agregar al Visor
        await viewer.dataSources.add(ds);
        layers[name] = ds; // Guardar referencia para los toggles
        
        console.log(`✅ Capa ${name} cargada.`);
        return ds;
    } catch (e) {
        console.warn(`❌ Error cargando capa ${name}:`, e);
        return null;
    }
}

//---------------------------------------------------
// 9. DIBUJAR RADIO (EFECTO ESCÁNER)
//---------------------------------------------------
function dibujarRadio(lat, lon, r) {
    if (!viewer) return; // Protección por si no ha cargado

    // Borrar radio anterior
    if (radioEntity) viewer.entities.remove(radioEntity);

    // Crear nuevo radio
    radioEntity = viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(lon, lat),
        ellipse: {
            semiMinorAxis: r,
            semiMajorAxis: r,
            // TRUCO VISUAL: Material transparente amarillo
            material: Cesium.Color.YELLOW.withAlpha(0.25),
            outline: true,
            outlineColor: Cesium.Color.YELLOW,
            outlineWidth: 2,
            // MAGIA: Esto hace que el círculo se "pinte" sobre los edificios 3D
            classificationType: Cesium.ClassificationType.CESIUM_3D_TILE
        }
    });

    // Mover cámara suavemente para encuadrar
    // Nota: heightReference asegura que la cámara no choque con montañas
    const cameraHeight = Math.max(800, r * 3.5); 
    
    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(lon, lat, cameraHeight),
        orientation: {
            heading: 0.0,
            pitch: Cesium.Math.toRadians(-45.0), // Ángulo picado
            roll: 0.0
        },
        duration: 2.0 // Segundos de vuelo
    });

    // Actualizar texto HTML
    const divRadio = document.getElementById("info-radio");
    if(divRadio) divRadio.innerHTML = `<b>Radio:</b> ${r} m`;
}

//---------------------------------------------------
// 10. MODIFICACIÓN A INITCESIUM (INTEGRACIÓN)
//---------------------------------------------------
// Reemplaza tu llamada final de initCesium() con esta lógica
// para que cargue las capas APENAS termine de cargar el mapa.

initCesium().then(async () => {
    // Asignamos la variable global
    // (Asegúrate de que en tu función initCesium hayas puesto: viewer = new Cesium...)
    
    // Si 'viewer' estaba declarado dentro de initCesium con 'const', 
    // cámbialo allá arriba a la variable global 'viewer = ...' (sin const).

    // --- CARGAR CAPAS EN ORDEN ---
    // Usamos await para que no se trabe el navegador cargando todo a la vez
    await loadLayer("localidades", files.localidades, styleLocalidad);
    await loadLayer("manzanas",    files.manzanas,    styleManzana);
    await loadLayer("pot",         files.pot,         stylePOT);
    await loadLayer("verde",       files.verde,       styleVerde);
    
    // Capas de puntos al final (para que queden encima)
    await loadLayer("transporte",  files.transporte,  styleTransporte);
    await loadLayer("colegios",    files.colegios,    styleColegios);
    await loadLayer("salud",       files.salud,       styleSalud);

    // --- DIBUJAR RADIO INICIAL ---
    dibujarRadio(lat, lon, radio);
});

//---------------------------------------------------
// 11. EVENTOS UI (BOTONES Y TOGGLES)
//---------------------------------------------------

// Botón Aplicar Radio
const btnRadio = document.getElementById("btn-aplicar-radio");
if (btnRadio) {
    btnRadio.onclick = () => {
        const inputVal = document.getElementById("input-radio").value;
        const newR = Number(inputVal);
        if (!isNaN(newR) && newR > 0) {
            radio = newR;
            dibujarRadio(lat, lon, radio);
        }
    };
}

// Función Genérica de Toggles
function bindToggle(id, layerName) {
    const checkbox = document.getElementById(id);
    if (checkbox) {
        checkbox.onchange = e => {
            if (layers[layerName]) {
                layers[layerName].show = e.target.checked;
            }
        };
    }
}

// Vincular todos los checkboxes (Asegúrate que estos IDs existan en index.html)
bindToggle("layer-localidad", "localidades");
bindToggle("layer-manzanas", "manzanas");
bindToggle("layer-transporte", "transporte");
bindToggle("layer-colegios", "colegios");
bindToggle("layer-salud", "salud");
bindToggle("layer-verde", "verde");
bindToggle("layer-pot", "pot");

//---------------------------------------------------
// INTERACCIÓN INTELIGENTE (INFOBOX)
//---------------------------------------------------
// En lugar de un 'alert', configuramos la entidad seleccionada
// para que el InfoBox nativo de Cesium muestre los datos limpios.

const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

handler.setInputAction(function (movement) {
    const picked = viewer.scene.pick(movement.position);

    // Si tocamos un objeto con propiedades
    if (Cesium.defined(picked) && picked.id && picked.id.properties) {
        const props = picked.id.properties;
        const tiempo = Cesium.JulianDate.now(); // Hora actual para leer el dato

        // 1. INTENTAR RESCATAR EL NOMBRE (Para el Título de la Caja)
        // Buscamos columnas comunes en tus GeoJSON
        let nombre = "Objeto Urbano";
        if (props.hasProperty('nombre')) nombre = props.nombre.getValue(tiempo);
        else if (props.hasProperty('nombre_hospital')) nombre = props.nombre_hospital.getValue(tiempo);
        else if (props.hasProperty('nombre_estacion')) nombre = props.nombre_estacion.getValue(tiempo);
        else if (props.hasProperty('nombre_parque')) nombre = props.nombre_parque.getValue(tiempo);
        else if (props.hasProperty('nombre_localidad')) nombre = props.nombre_localidad.getValue(tiempo);
        else if (props.hasProperty('CODIGO_MAN')) nombre = "Manzana " + props.CODIGO_MAN.getValue(tiempo);

        // Asignamos el nombre para que salga en el título naranja
        picked.id.name = nombre;

        // 2. FORMATEAR LA DESCRIPCIÓN (Tabla HTML limpia)
        // Esto reemplaza la tabla fea por defecto con una curada
        let html = '<table style="width:100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px;">';
        
        // Lista de atributos que SÍ nos interesa mostrar (Filtro)
        const atributosInteres = [
            'estrato', 'uso_pot_simplificado', 'troncal', 
            'sector', 'calendario', 'top_3_delitos'
        ];

        // Recorremos las propiedades
        const propertyIds = props.propertyNames;
        propertyIds.forEach(function(key) {
            // Solo mostramos si está en la lista de interés O si es un nombre que no capturamos arriba
            if (atributosInteres.includes(key)) {
                try {
                    const val = props[key].getValue(tiempo);
                    // Formateo bonito de la llave (Ej: uso_pot_simplificado -> Uso Pot Simplificado)
                    const label = key.replace(/_/g, ' ').toUpperCase();
                    
                    html += `
                        <tr style="border-bottom: 1px solid #444;">
                            <td style="padding: 5px; color: #aaa;">${label}</td>
                            <td style="padding: 5px; font-weight: bold; color: white;">${val}</td>
                        </tr>`;
                } catch (e) {}
            }
        });
        html += '</table>';

        // Inyectamos la descripción HTML
        picked.id.description = html;
        
        // Seleccionamos el objeto (Esto dispara el InfoBox automáticamente)
        viewer.selectedEntity = picked.id;
    }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);
