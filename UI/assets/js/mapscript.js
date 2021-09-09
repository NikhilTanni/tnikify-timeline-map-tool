var map = L.map('map').setView([12.9466368,77.6536064], 6);

function getThemeProperties(theme) {
    if (theme === "Default") {
        return L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: '<replace-your-access-token-here>'
        })
    } else if (theme === "NatgeoMap") {
        return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC',
            maxZoom: 16
        });
    } else if (theme === "Toner") {
        return L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.{ext}', {
            attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            subdomains: 'abcd',
            minZoom: 0,
            maxZoom: 20,
            ext: 'png'
        });
    } else if (theme === "SmoothDark") {
        return L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
            maxZoom: 20,
            attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
        });
    } else {
        return undefined;
    }
}

// define currentLayer to use across when theme is changed
var currentLayer = getThemeProperties("Default").addTo(map);

function changeTheme(theme) {
    const newTheme = getThemeProperties(theme);
    // change only if theme id is valid
    if (newTheme !== undefined) {
        // remove existing layer
        map.removeLayer(currentLayer);

        // add new theme to map layer
        currentLayer = newTheme.addTo(map);
    }
}

var popGroupLayer1Obj = new L.featureGroup();
function displayResultsOnMap(events) {
    popGroupLayer1Obj.clearLayers();
    for (const key in events) {
        // lifespan
        if(events[key]["type"] === "lifespan") {
            for (const spanMode in events[key]["time"]["lifespan"]) {
                if (spanMode in events[key]["location"]["geo"]) {
                    loc = events[key]["location"]["geo"][spanMode];
                    var dispText = `<table>
                    <tr border="1">
                        <td>Event:</td>
                        <td>${events[key]["event"]}</td>
                        <td>(${spanMode})</td>
                    </tr>
                    <tr>
                        <td>Time:</td>
                        <td>${events[key]["time"]["lifespan"][spanMode]}</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>Location:</td>
                        <td colspan="2">${events[key]["location"]["geo"][spanMode]["name"]}</td>
                    </tr>
                    <tr>
                        <td>lat:</td>
                        <td colspan="2">${events[key]["location"]["geo"][spanMode]["lat"]}</td>
                    </tr>
                    <tr>
                        <td>lon:</td>
                        <td colspan="2">${events[key]["location"]["geo"][spanMode]["lon"]}</td>
                    </tr>
                    </table>`;
                    L.marker([loc['lat'], loc['lon']]).addTo(popGroupLayer1Obj).bindPopup(dispText);
                }
            }
            
        }        
    }
    popGroupLayer1Obj.addTo(map)
}
// var cities = L.layerGroup([L.marker([19.1930448,73.855456]).bindPopup('This is Golden, CO.'), L.marker([ 18.2346909,73.4442557]).bindPopup('This is Golden, CO.')]).addTo(map);
// map.removeLayer(cities);

var lineGroupLayer1Obj = new L.featureGroup();
function displayLinesOnMap(lines) {
    lineGroupLayer1Obj.clearLayers();
    var linesArr = []
    for (const line in lines) {
        linesArr.push(lines[line]);
    }
    L.polyline(linesArr).addTo(lineGroupLayer1Obj);
    lineGroupLayer1Obj.addTo(map);
}



