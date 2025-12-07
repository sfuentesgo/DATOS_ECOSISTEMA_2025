//---------------------------------------------------
// CONFIGURACIÓN INICIAL
//---------------------------------------------------
Cesium.Ion.defaultAccessToken = null; // No usamos Cesium Ion

// Parámetros por defecto
const defaults = {
    lat: 4.6097,
    lon: -74.0817,
    zoom: 15,
    radio: 600
};

// Función para leer parámetros
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
const zoom = getParam("zoom", defaults.zoom);

// Mostrar valores iniciales en el panel
document.getElementById("info-coords").innerHTML = `
    <b>Lat:</b> ${lat.toFixed(5)} · 
    <b>Lon:</b> ${lon.toFixed(5)}
`;
document.getElementById("input-radio").value = radio;

//---------------------------------------------------
// INICIALIZAR VISOR
//---------------------------------------------------
const viewer = new Cesium.Viewer("cesiumContainer", {
    terrainProvider: await Cesium.CesiumTerrainProvider.fromIonAssetId(1),
    animation: false,
    timeline: false,
    baseLayerPicker: true,
    sceneModePicker: true
});

// Convertir zoom a altura
function zoomToHeight(z) {
    return Math.max(150, 60000 / (z || 15));
}

viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(lon, lat, zoomToHeight(zoom)),
    duration: 1.5
});

//---------------------------------------------------
// CARGA DE GEOJSON DESDE GITHUB RAW
//---------------------------------------------------
const baseURL = "https://github.com/andres-fuentex/CONCURSO/raw/main/DATOS_LIMPIOS/";

const files = {
    localidades: baseURL + "dim_localidad.geojson",
    manzanas: baseURL + "tabla_hechos.geojson",
    transporte: baseURL + "dim_transporte.geojson",
    colegios: baseURL + "dim_colegios.geojson",
    salud: baseURL + "dim_salud.geojson",
    verde: baseURL + "dim_verde.geojson",
    pot: baseURL + "dim_area.geojson"
};

// Contenedor general para las capas cargadas
const layers = {
    localidades: null,
    manzanas: null,
    transporte: null,
    colegios: null,
    salud: null,
    verde: null,
    pot: null
};

//---------------------------------------------------
// FUNCIONES DE ESTILO
//---------------------------------------------------

// 1. Localidad — polígonos azules
function styleLocalidad(ent) {
    if (ent.polygon) {
        ent.polygon.material = Cesium.Color.fromCssColorString("#0047FF").withAlpha(0.3);
        ent.polygon.outline = true;
        ent.polygon.outlineColor = Cesium.Color.fromCssColorString("#0047FF");
        ent.polygon.outlineWidth = 2;
    }
}

// 2. Manzanas — extrusión por estrato
function styleManzana(ent) {
    if (!ent.polygon) return;

    const props = ent.properties;
    const estrato = props?.estrato ? Number(props.estrato.getValue()) : 0;
    const altura = estrato > 0 ? estrato * 20 : 5;

    const color = Cesium.Color.fromCssColorString("#F1C40F").withAlpha(0.55);

    ent.polygon.material = color;
    ent.polygon.extrudedHeight = altura;
    ent.polygon.outline = false;
}

// 3. Transporte — puntos rojos
function styleTransporte(ent) {
    if (ent.point) {
        ent.point.pixelSize = 10;
        ent.point.color = Cesium.Color.RED;
    }
}

// 4. Colegios — puntos morados
function styleColegios(ent) {
    if (ent.point) {
        ent.point.pixelSize = 9;
        ent.point.color = Cesium.Color.fromCssColorString("#9B59B6");
    }
}

// 5. Salud — puntos azul oscuro
function styleSalud(ent) {
    ent.point && (
        ent.point.pixelSize = 10,
        ent.point.color = Cesium.Color.fromCssColorString("#0905F7")
    );
}

// 6. Verde — polígonos verdes
function styleVerde(ent) {
    if (ent.polygon) {
        ent.polygon.material = Cesium.Color.fromCssColorString("#27AE60").withAlpha(0.5);
        ent.polygon.outline = true;
        ent.polygon.outlineColor = Cesium.Color.fromCssColorString("#145A32");
    }
}

// 7. POT — solo borde, color según categoría
function colorPOT(cat) {
    const map = {
        "COMERCIO": "#E67E22",
        "RESIDENCIAL": "#3498DB",
        "INDUSTRIAL": "#8E44AD",
        "DOTACIONAL": "#2ECC71",
        "OTRO": "#95A5A6"
    };
    return map[cat] || "#E67E22";
}

function stylePOT(ent) {
    const props = ent.properties;
    let categoria = null;

    if (props?.uso_pot_simplificado)
        categoria = props.uso_pot_simplificado.getValue();

    const col = Cesium.Color.fromCssColorString(colorPOT(categoria || "OTRO"));

    if (ent.polygon) {
        ent.polygon.material = Cesium.Color.TRANSPARENT;
        ent.polygon.outline = true;
        ent.polygon.outlineColor = col;
        ent.polygon.outlineWidth = 2;
    }
}

//---------------------------------------------------
// CARGA UTILITARIA DE GEOJSON
//---------------------------------------------------
async function loadLayer(name, url, styleFn) {
    try {
        const ds = await Cesium.GeoJsonDataSource.load(url);
        viewer.dataSources.add(ds);
        layers[name] = ds;

        ds.entities.values.forEach(ent => styleFn(ent));

        return ds;
    } catch (e) {
        console.warn("Error cargando capa:", name, e);
        return null;
    }
}

//---------------------------------------------------
// CARGAR TODAS LAS CAPAS
//---------------------------------------------------
(async function () {

    await loadLayer("localidades", files.localidades, styleLocalidad);
    await loadLayer("manzanas", files.manzanas, styleManzana);
    await loadLayer("transporte", files.transporte, styleTransporte);
    await loadLayer("colegios", files.colegios, styleColegios);
    await loadLayer("salud", files.salud, styleSalud);
    await loadLayer("verde", files.verde, styleVerde);
    await loadLayer("pot", files.pot, stylePOT);

})();

//---------------------------------------------------
// RADIO DINÁMICO
//---------------------------------------------------
let radioEntity = null;

function dibujarRadio(lat, lon, r) {
    if (radioEntity) viewer.entities.remove(radioEntity);

    radioEntity = viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(lon, lat),
        ellipse: {
            semiMajorAxis: r,
            semiMinorAxis: r,
            material: Cesium.Color.YELLOW.withAlpha(0.18),
            outline: true,
            outlineColor: Cesium.Color.YELLOW,
            height: 2
        }
    });

    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(lon, lat, Math.max(200, r * 2.2)),
        duration: 1.2
    });

    document.getElementById("info-radio").innerHTML = `<b>Radio:</b> ${r} m`;
}

// Render inicial
dibujarRadio(lat, lon, radio);

// Botón aplicar
document.getElementById("btn-aplicar-radio").onclick = () => {
    const newR = Number(document.getElementById("input-radio").value);
    if (!isNaN(newR) && newR > 0) {
        radio = newR;
        dibujarRadio(lat, lon, radio);
    }
};

//---------------------------------------------------
// TOGGLES DE VISIBILIDAD
//---------------------------------------------------
function bindToggle(id, layerName) {
    document.getElementById(id).onchange = e => {
        if (layers[layerName]) {
            layers[layerName].show = e.target.checked;
        }
    };
}

bindToggle("layer-localidad", "localidades");
bindToggle("layer-manzanas", "manzanas");
bindToggle("layer-transporte", "transporte");
bindToggle("layer-colegios", "colegios");
bindToggle("layer-salud", "salud");
bindToggle("layer-verde", "verde");
bindToggle("layer-pot", "pot");

//---------------------------------------------------
// POPUP SIMPLIFICADO AL CLIC
//---------------------------------------------------
const clickHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

clickHandler.setInputAction(function (movement) {
    const picked = viewer.scene.pick(movement.position);
    if (picked?.id?.properties) {

        let texto = "";
        const props = picked.id.properties;

        for (const key in props) {
            try {
                const val = props[key].getValue();
                texto += `${key}: ${val}\n`;
            } catch { }
        }

        alert(texto || "Objeto sin atributos");
    }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);
