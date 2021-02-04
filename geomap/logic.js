
var queryUrl = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2020-12-31&endtime=2021-01-01&maxlongitude=-69.52148437&minlongitude=-123.83789062&maxlatitude=48.74894534&minlatitude=25.16517337";
var queryUrl = 'data/locs.json'
 
d3.json(queryUrl).then(data => { 
  earthquakeData = data;
  
  console.log( data );  

  var earthquakeLayer = L.geoJSON(earthquakeData, {
    onEachFeature: function (feature, layer) {
      layer.bindPopup(`<h3>${feature.properties.place}</h3><hr>${new Date(feature.properties.time)}`);
        }
    });
    
    // Define streetmap and darkmap layers
    var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
      attribution: "© <a href='https://www.mapbox.com/about/maps/'>Mapbox</a> © <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a> <strong><a href='https://www.mapbox.com/map-feedback/' target='_blank'>Improve this map</a></strong>",
      tileSize: 512,
      maxZoom: 18,
      zoomOffset: -1,
      id: "mapbox/streets-v11",
      accessToken: API_KEY
    }); 
    var baseMaps = {  "Street Map": streetmap   }; 
    var overlayMaps = {  Earthquakes: earthquakeLayer   };

    // Create our map, giving it the streetmap and earthquakes layers to display on load
    var myMap = L.map("map", {
      center: [
        37.09, -95.71
      ],
      zoom: 5,
      layers: [streetmap, earthquakeLayer]
    });
 
    L.control.layers(baseMaps, overlayMaps, {
      collapsed: false
    }).addTo(myMap);

});