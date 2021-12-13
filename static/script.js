var mymap = L.map('mapid').setView([48.838, 2.586], 13);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
            'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1
    }).addTo(mymap);

    var popup = L.popup();
    L.marker([48.838, 2.586]).addTo(mymap).bindTooltip("Votre image");

    function onMapClick(e) {
        popup
            .setLatLng(e.latlng)
            .setContent(e.latlng.toString().substring(7, 13) + "°N, " + e.latlng.toString().substring(18, 24) + "°E")
            .openOn(mymap);
            // var newMarker = new L.marker(e.latlng).addTo(mymap); // uncomment to add markers when clicked
    }
    mymap.on('click', onMapClick); 