//---------------------------------------------------
// 1. CONFIGURACIÓN INICIAL Y VARIABLES GLOBALES
//---------------------------------------------------

// Tu Token de Cesium Ion
Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3NmY0NDc1NS0wNTI1LTQ5MzktODU4Yi04MzEyZDBhNGQ1OGMiLCJpZCI6MzY3NDIwLCJpYXQiOjE3NjUxMjUyNzJ9.rNorYTcXLUMNiocHyuT9VPqrMUdC6yHvbKq8kW-PVds";

// Variables Globales
let viewer;             // El visor 3D
let radioEntity = null; // El círculo amarillo

// Contenedor de capas
const layers = {
    localidades: null,
    manzanas: null,
    transporte: null,
    colegios: null,
    salud: null,
    verde: null,
    pot: null
};

// Rutas de Datos (GitHub Raw)
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

//---------------------------------------------------
// 2. PARÁMETROS DE URL
//---------------------------------------------------
const defaults = {
    lat: 4.6097,
    lon: -74.0817,
    zoom: 15,
    radio: 600
};

function getParam(name, fallback) {
    const url = new URLSearchParams(window.location.search);
    if (url.has(name)) {
        const v = url.get(name);
        const n = Number(v);
        return isNaN(n) ? v : n;
    }
    return fallback;
}

const lat = getParam("lat", defaults.lat);
const lon = getParam("lon", defaults.lon);
let radio = getParam("radio", defaults.radio);

// Actualizar panel HTML
const infoDiv = document.getElementById("info-coords");
if (infoDiv) {
    infoDiv.innerHTML = `<b>Lat:</b> ${lat.toFixed(4)} <br> <b>Lon:</b> ${lon.toFixed(4)}`;
}
const inputRadio = document.getElementById("input-radio");
if (inputRadio) {
    inputRadio.value = radio;
}

//---------------------------------------------------
// 3. FUNCIONES DE ESTILO (CORREGIDAS PARA DIFERENCIAR COLORES)
//---------------------------------------------------

// 1. Localidad
function styleLocalidad(ent) {
    if (ent.polygon) {
        ent.polygon.material = Cesium.Color.fromCssColorString("#0047FF").withAlpha(0.1);
        ent.polygon.classificationType = Cesium.ClassificationType.CESIUM_3D_TILE;
        ent.polygon.outline = false;
    }
}

// 2. Manzanas (Extrusión)
function styleManzana(ent) {
    if (!ent.polygon) return;
    const props = ent.properties;
    let estrato = 0;
    if (props && props.hasProperty('estrato')) {
        estrato = Number(props.estrato.getValue(Cesium.JulianDate.now()));
    }
    const altura = estrato > 0 ? estrato * 15 : 5;
    const color = Cesium.Color.fromCssColorString("#F1C40F").withAlpha(0.6);

    ent.polygon.material = color;
    ent.polygon.extrudedHeight = altura;
    ent.polygon.outline = false;
}

// 3. Transporte (ROJO)
function styleTransporte(ent) {
    // Eliminamos el Billboard (Pin por defecto) si existe
    ent.billboard = undefined;
    
    // Creamos un Punto explícito
    ent.point = new Cesium.PointGraphics({
        pixelSize: 12,
        color: Cesium.Color.RED,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    });
}

// 4. Colegios (MORADO)
function styleColegios(ent) {
    ent.billboard = undefined;
    ent.point = new Cesium.PointGraphics({
        pixelSize: 10,
        color: Cesium.Color.fromCssColorString("#9B59B6"), // Morado
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 1,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    });
}

// 5. Salud (AZUL OSCURO / CRUZ)
function styleSalud(ent) {
    ent.billboard = undefined;
    ent.point = new Cesium.PointGraphics({
        pixelSize: 14,
        color: Cesium.Color.fromCssColorString("#0905F7"), // Azul Rey
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    });
}

// 6. Verde
function styleVerde(ent) {
    if (ent.polygon) {
        ent.polygon.material = Cesium.Color.fromCssColorString("#27AE60").withAlpha(0.6);
        ent.polygon.classificationType = Cesium.ClassificationType.CESIUM_3D_TILE;
        ent.polygon.outline = false;
    }
}

// 7. POT
function colorPOT(cat) {
    const map = {
        "Comercio y Servicios Locales": "#E67E22",
        "Residencial Mixto": "#3498DB",
        "Empresarial e Industrial": "#8E44AD",
        "Grandes Dotacionales": "#2ECC71",
        "Alta Densidad / VIS": "#C0392B",
        "Histórico y Patrimonial": "#F1C40F",
        "Otro / Sin Clasificar": "#95A5A6"
    };
    for (const key in map) {
        if (cat && cat.includes(key)) return map[key];
    }
    return "#95A5A6";
}

function stylePOT(ent) {
    const props = ent.properties;
    let categoria = "Otro";
    if (props && props.hasProperty('uso_pot_simplificado')) {
        categoria = props.uso_pot_simplificado.getValue(Cesium.JulianDate.now());
    }
    const col = Cesium.Color.fromCssColorString(colorPOT(categoria));

    if (ent.polygon) {
        ent.polygon.material = col.withAlpha(0.3);
        ent.polygon.classificationType = Cesium.ClassificationType.CESIUM_3D_TILE;
        ent.polygon.outline = false;
    }
}

//---------------------------------------------------
// 4. FUNCIÓN DE CARGA DE CAPAS
//---------------------------------------------------
async function loadLayer(name, url, styleFn) {
    try {
        console.log(`⏳ Cargando capa: ${name}...`);
        
        const ds = await Cesium.GeoJsonDataSource.load(url, {
            clampToGround: true
        });

        // Aplicar estilos entidad por entidad
        const entities = ds.entities.values;
        for (let i = 0; i < entities.length; i++) {
            styleFn(entities[i]);
        }

        await viewer.dataSources.add(ds);
        layers[name] = ds;
        
        console.log(`✅ Capa ${name} cargada.`);
        return ds;
    } catch (e) {
        console.warn(`❌ Error cargando capa ${name}:`, e);
        return null;
    }
}

//---------------------------------------------------
// 5. FUNCIÓN DIBUJAR RADIO (Con Borde Visible)
//---------------------------------------------------
function dibujarRadio(lat, lon, r) {
    if (!viewer) return;

    if (radioEntity) viewer.entities.remove(radioEntity);

    radioEntity = viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(lon, lat),
        ellipse: {
            semiMinorAxis: r,
            semiMajorAxis: r,
            // Relleno más fuerte para que se note
            material: Cesium.Color.YELLOW.withAlpha(0.3),
            
            // BORDE ENCENDIDO (Lo que pediste)
            outline: true, 
            outlineColor: Cesium.Color.YELLOW,
            outlineWidth: 3,
            
            // Nota: El borde a veces genera warning en 3D Tiles, pero es necesario para verlo bien.
            classificationType: Cesium.ClassificationType.CESIUM_3D_TILE
        }
    });

    // CÁMARA AJUSTADA: Más lejos para ver mejor el contexto
    const cameraHeight = Math.max(3000, r * 5.0); // Aumenté altura
    
    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(lon, lat, cameraHeight),
        orientation: {
            heading: 0.0,
            pitch: Cesium.Math.toRadians(-40.0),
            roll: 0.0
        },
        duration: 2.0
    });

    const divRadio = document.getElementById("info-radio");
    if(divRadio) divRadio.innerHTML = `<b>Radio:</b> ${r} m`;
}

//---------------------------------------------------
// 6. INICIALIZACIÓN PRINCIPAL
//---------------------------------------------------
async function initCesium() {
    
    viewer = new Cesium.Viewer("cesiumContainer", {
        terrain: Cesium.Terrain.fromWorldTerrain(),
        animation: false,
        timeline: false,
        baseLayerPicker: false,
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        navigationHelpButton: false,
        infoBox: true,
        selectionIndicator: true
    });

    viewer._cesiumWidget._creditContainer.style.display = "none";

    // CÁMARA INICIAL (Más alejada - 5000m)
    viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(lon, lat, 5000), 
        orientation: {
            heading: 0.0,
            pitch: Cesium.Math.toRadians(-30.0),
            roll: 0.0
        }
    });

    // Cargar Google 3D Tiles
    try {
        const tileset = await Cesium.Cesium3DTileset.fromIonAssetId(2275207);
        viewer.scene.primitives.add(tileset);
        console.log("✅ Gemelo Digital cargado.");
    } catch (error) {
        console.error("❌ Error cargando Google 3D Tiles:", error);
    }
}

//---------------------------------------------------
// 7. EJECUCIÓN
//---------------------------------------------------
initCesium().then(async () => {
    // Cargamos capas
    await loadLayer("localidades", files.localidades, styleLocalidad);
    await loadLayer("manzanas",    files.manzanas,    styleManzana);
    await loadLayer("pot",         files.pot,         stylePOT);
    await loadLayer("verde",       files.verde,       styleVerde);
    
    // Puntos (Encima)
    await loadLayer("transporte",  files.transporte,  styleTransporte);
    await loadLayer("colegios",    files.colegios,    styleColegios);
    await loadLayer("salud",       files.salud,       styleSalud);

    // Radio
    dibujarRadio(lat, lon, radio);
});

//---------------------------------------------------
// 8. EVENTOS UI
//---------------------------------------------------
const btnRadio = document.getElementById("btn-aplicar-radio");
if (btnRadio) {
    btnRadio.onclick = () => {
        const val = document.getElementById("input-radio").value;
        const newR = Number(val);
        if (!isNaN(newR) && newR > 0) {
            radio = newR;
            dibujarRadio(lat, lon, radio);
        }
    };
}

function bindToggle(id, layerName) {
    const cb = document.getElementById(id);
    if (cb) {
        cb.onchange = e => {
            if (layers[layerName]) {
                layers[layerName].show = e.target.checked;
            }
        };
    }
}

bindToggle("layer-localidad", "localidades");
bindToggle("layer-manzanas", "manzanas");
bindToggle("layer-transporte", "transporte");
bindToggle("layer-colegios", "colegios");
bindToggle("layer-salud", "salud");
bindToggle("layer-verde", "verde");
bindToggle("layer-pot", "pot");

//---------------------------------------------------
// 9. CLIC INTELIGENTE
//---------------------------------------------------
const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

handler.setInputAction(function (movement) {
    const picked = viewer.scene.pick(movement.position);

    if (Cesium.defined(picked) && picked.id && picked.id.properties) {
        const props = picked.id.properties;
        const tiempo = Cesium.JulianDate.now();

        let nombre = "Objeto Urbano";
        if (props.hasProperty('nombre')) nombre = props.nombre.getValue(tiempo);
        else if (props.hasProperty('nombre_hospital')) nombre = props.nombre_hospital.getValue(tiempo);
        else if (props.hasProperty('nombre_estacion')) nombre = props.nombre_estacion.getValue(tiempo);
        else if (props.hasProperty('nombre_parque')) nombre = props.nombre_parque.getValue(tiempo);
        else if (props.hasProperty('nombre_localidad')) nombre = props.nombre_localidad.getValue(tiempo);
        else if (props.hasProperty('nombre_area')) nombre = props.nombre_area.getValue(tiempo);

        picked.id.name = nombre;

        let html = '<table style="width:100%; font-family:sans-serif; font-size:13px; color:#fff;">';
        
        const intereses = ['estrato', 'uso_pot_simplificado', 'troncal', 'sector', 'top_3_delitos'];
        
        props.propertyNames.forEach(key => {
            if (intereses.includes(key)) {
                try {
                    const val = props[key].getValue(tiempo);
                    const label = key.replace(/_/g, ' ').toUpperCase();
                    html += `<tr><td style="color:#aaa;padding:4px;">${label}</td><td style="padding:4px;"><b>${val}</b></td></tr>`;
                } catch(e){}
            }
        });
        html += '</table>';
        picked.id.description = html;
        
        viewer.selectedEntity = picked.id;
    }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);