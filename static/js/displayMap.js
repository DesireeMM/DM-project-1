'use strict';

function initMap() {
    // event listener listening for submitting the form
    const button = document.querySelector('#search-form');
    button.addEventListener('click', () => {
        const keyword = document.querySelector('#search-input').value
        const location = document.querySelector('#search-location').value
        const radius = document.querySelector('#search-radius').value
    // take the values from the form and pass them into the fetch using a query string

    const queryString = `keyword=${keyword}&location=${location}&radius=${radius}`

    fetch(`/api/search?${queryString}`)
    .then((response) => response.json())
    .then((searchResults) => {

        const searchCoords = {
            lat: searchResults['geo_location_lat'],
            lng: searchResults['geo_location_lng']
        }

        const map = new google.maps.Map(document.querySelector('#map'), {
            center: searchCoords,
            zoom: 11,
        });

        const placeInfo = new google.maps.InfoWindow();

        for (const resultIndex in searchResults['results']) {
            const placeInfoContent = `
            <div class="window-content">
              <ul class="place-info">
                <li><b>Name: </b>${searchResults['results'][resultIndex]['name']}</li>
                <li><b>Location: </b>${searchResults['results'][resultIndex]['geometry']['location']['lat']}, 
                ${searchResults['results'][resultIndex]['geometry']['location']['lng']}</li>
              </ul>
            </div>
          `;

            const placeMarker = new google.maps.Marker({
                position: {
                  lat: searchResults['results'][resultIndex]['geometry']['location']['lat'], 
                  lng: searchResults['results'][resultIndex]['geometry']['location']['lng']
                },
                title: `Result: ${resultIndex}`,
                map: map
                });
  
            placeMarker.addListener('click', () => {
                placeInfo.close();
                placeInfo.setContent(placeInfoContent);
                placeInfo.open(map, placeMarker);
          });
        }
    })
    })
   
}
