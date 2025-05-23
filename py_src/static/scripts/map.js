/**
 * Generates a Google Maps embed URL with the specified parameters
 * @param {Object} options - Map configuration options
 * @param {number} options.lat - Latitude coordinate
 * @param {number} options.lng - Longitude coordinate
 * @param {number} options.viewRadius - View radius in meters (higher = more zoomed out)
 * @returns {string} The complete Google Maps embed URL
 */
function generateMapUrl({ lat, lng, viewRadius = 2000 }) {
    console.log('Generating map URL for:', { lat, lng, viewRadius });
    
    // Create a Google Maps embed URL that properly zooms to location
    const zoom = viewRadius < 2000 ? 18 : 16; // Reduced zoom levels to show more context
    const locationName = 'SUNY Oneonta';
    
    // Use place mode with both coordinates and location name for better accuracy
    return `https://www.google.com/maps/embed/v1/place` +
        `?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8` +
        `&q=${lat},${lng} ${locationName}` +
        `&zoom=${zoom}` +
        `&center=${lat},${lng}`;
}

// Campus map interaction functionality
function initMap() {
    console.log('Initializing map...');
    window.addEventListener('load', () => {
        console.log('Page loaded, setting up location clicks...');
        const locationItems = document.querySelectorAll('.location-item');
        const iframe = document.getElementById('campus-map');
        
        if (!iframe) {
            console.error('Map iframe not found!');
            return;
        }

        locationItems.forEach(item => {
            item.addEventListener('click', () => {
                console.log('Location clicked:', item.dataset.locationId);
                // Handle location selection
                document.querySelectorAll('.location-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                // Get coordinates and update map
                const locationId = item.dataset.locationId;
                focusLocation(locationId);
            });
        });
        
        // Set initial map view
        setInitialMapView();
    });
}

function focusLocation(locationId) {
    console.log('Focusing location:', locationId);
    const iframe = document.getElementById('campus-map');
    const locationEl = document.querySelector(`[data-location-id="${locationId}"]`);
    
    if (!locationEl) {
        console.error('Location element not found:', locationId);
        return;
    }
    
    // Get coordinates from data attributes
    const lat = parseFloat(locationEl.dataset.lat);
    const lng = parseFloat(locationEl.dataset.lng);
    
    if (isNaN(lat) || isNaN(lng)) {
        console.error('Invalid coordinates:', { lat, lng });
        return;
    }
    
    // Get the location name
    const locationName = locationEl.querySelector('h4').textContent;
    console.log('Updating map for:', { lat, lng, name: locationName });
    iframe.src = generateMapUrl({ lat, lng, viewRadius: 1000, locationName }); // Closer view for selected location
    
    // Scroll the location into view on mobile
    if (window.innerWidth < 768) {
        locationEl.scrollIntoView({ behavior: 'smooth' });
    }
}

// Set initial map view centered on SUNY Oneonta campus
function setInitialMapView() {
    console.log('Setting initial map view...');
    const iframe = document.getElementById('campus-map');
    if (!iframe) {
        console.error('Map iframe not found!');
        return;
    }
    
    // Center coordinates for SUNY Oneonta campus
    iframe.src = generateMapUrl({
        lat: 42.4688,
        lng: -75.0617,
        viewRadius: 2500 // Wider view to show all locations
    });
}

// Initialize map functionality
initMap();
