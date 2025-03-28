document.addEventListener('DOMContentLoaded', function () {
    var changeRegionForm = document.getElementById('change-region-form');
    if (changeRegionForm) {
        changeRegionForm.addEventListener('submit', function (event) {
            event.preventDefault();
            var form = event.target;
            var formData = new FormData(form);
            document.getElementById('vpn-spinner').style.display = 'inline-block';
            fetch(form.action, {
                method: 'POST',
                body: formData
            }).then(function (response) {
                return response.json();
            }).then(function (data) {
                if (data.status === 'changing') {
                    document.getElementById('region').value = data.region;
                    pollVpnStatus();
                }
            }).catch(function (error) {
                console.error("Error changing region:", error);
            });
        });
    }

    // This block is replaced by the updated setGeolocationButton handler below

    let pollAttempts = 0;
    function pollVpnStatus() {
        fetch('/vpn-status')
            .then(response => response.json())
            .then(data => {
                if (data.vpn_running && data.ip_info) {
                    document.getElementById('vpn-spinner').style.display = 'none';
                    document.getElementById('geolocation').textContent = data.ip_info.loc || 'Unavailable';

                    // Update save persona form fields
                    document.getElementById('save-geolocation').value = data.ip_info.loc || '';
                    document.getElementById('save-country').value = data.ip_info.country || '';
                    document.getElementById('save-city').value = data.ip_info.city || '';
                    document.getElementById('save-region').value = data.ip_info.region || '';
                }
                if (pollAttempts < 5) {
                    pollAttempts++;
                    setTimeout(pollVpnStatus, 3000);
                }
            })
            .catch(error => console.error("Error polling VPN status:", error));
    }
    pollVpnStatus();

    // Initialize geolocation display based on VPN status
    function initializeGeolocation() {
        // Check if VPN is running (this is determined by the template)
        const vpnRunning = document.body.getAttribute('data-vpn-running') === 'True';
        
        if (!vpnRunning) {
            if (navigator.geolocation) {
                console.log("Geolocation is supported.");
                navigator.geolocation.getCurrentPosition(function (position) {
                    console.log("Geolocation success:", position);
                    document.getElementById('geolocation').textContent = position.coords.latitude + ', ' + position.coords.longitude;
                }, function (error) {
                    console.error("Geolocation error:", error);
                    document.getElementById('geolocation').textContent = 'Unavailable';
                });
            } else {
                console.log("Geolocation is not supported.");
                document.getElementById('geolocation').textContent = 'Not supported';
            }
        }
    }
    initializeGeolocation();

    // Add event listener to region dropdown to fetch geolocation and language when a region is selected
    var regionSelect = document.getElementById('region');
    if (regionSelect) {
        regionSelect.addEventListener('change', function () {
            var selectedOption = this.options[this.selectedIndex];
            var regionCode = selectedOption.getAttribute('data-code');
            var regionName = selectedOption.textContent;
            if (regionCode) {
                fetch('/get-region-geolocation/' + regionCode)
                    .then(response => response.json())
                    .then(data => {
                        if (data.geolocation) {
                            // Update the geolocation display
                            document.getElementById('geolocation').textContent = data.geolocation;

                            // Parse the geolocation coordinates
                            const coordinates = data.geolocation.split(',');
                            if (coordinates.length === 2) {
                                const lat = parseFloat(coordinates[0].trim());
                                const lng = parseFloat(coordinates[1].trim());
                                
                                // Update target latitude and longitude fields
                                const targetLatitudeInput = document.getElementById('target-latitude');
                                const targetLongitudeInput = document.getElementById('target-longitude');
                                if (targetLatitudeInput && targetLongitudeInput) {
                                    targetLatitudeInput.value = lat;
                                    targetLongitudeInput.value = lng;
                                }
                                
                                // Update latitude and longitude input fields
                                const latitudeInput = document.getElementById('latitude');
                                const longitudeInput = document.getElementById('longitude');
                                if (latitudeInput && longitudeInput) {
                                    latitudeInput.value = lat;
                                    longitudeInput.value = lng;
                                }
                                
                                // Clear existing markers and add a new one
                                if (window.markersLayer) {
                                    window.markersLayer.clearLayers();
                                } else {
                                    window.markersLayer = L.layerGroup().addTo(window.map);
                                }
                                
                                // Create a marker with popup showing the region info
                                const marker = L.marker([lat, lng])
                                    .addTo(window.markersLayer)
                                    .bindPopup(`<b>${regionName}</b><br>Location: ${lat.toFixed(4)}, ${lng.toFixed(4)}`)
                                    .openPopup();
                                
                                // Center the map on the new location with appropriate zoom
                                window.map.setView([lat, lng], 5);
                            }

                            // Update language dropdown based on region
                            var targetLanguage = document.getElementById('target-language');
                            var selectedLanguage;

                            switch (regionCode) {
                                case 'US':
                                    selectedLanguage = 'en-US';
                                    break;
                                case 'BR':
                                    selectedLanguage = 'pt-BR';
                                    break;
                                case 'DE':
                                    selectedLanguage = 'de-DE';
                                    break;
                                case 'JP':
                                    selectedLanguage = 'ja-JP';
                                    break;
                                case 'ZA':
                                    selectedLanguage = 'af-ZA';
                                    break;
                                default:
                                    selectedLanguage = 'en-US';
                            }

                            // Set the language dropdown value
                            targetLanguage.value = selectedLanguage;

                            // Update language in the Persona section
                            var personaLanguageElement = document.querySelector('.custom-card .row .col:nth-child(2)');
                            if (personaLanguageElement) {
                                personaLanguageElement.innerHTML = '<strong>Language:</strong> ' + selectedLanguage;
                            }

                            // Update the hidden language input field in the form
                            var languageInput = document.querySelector('form input[name="language"]');
                            if (languageInput) {
                                languageInput.value = selectedLanguage;
                            }

                            // Update the save persona form language field
                            var saveLanguageInput = document.getElementById('save-language');
                            if (saveLanguageInput) {
                                saveLanguageInput.value = selectedLanguage;
                            }
                        }
                    })
                    .catch(error => console.error("Error fetching geolocation:", error));
            }
        });
    }

    // Add event listener to set language button
    var setLanguageButton = document.getElementById('set-language');
    if (setLanguageButton) {
        setLanguageButton.addEventListener('click', function () {
            var selectedLanguage = document.getElementById('target-language').value;
            // Update language in the Persona section
            var personaLanguageElement = document.querySelector('.custom-card .row .col:nth-child(2)');
            if (personaLanguageElement) {
                personaLanguageElement.innerHTML = '<strong>Language:</strong> ' + selectedLanguage;
            }

            // Update the hidden language input field in the form
            var languageInput = document.querySelector('form input[name="language"]');
            if (languageInput) {
                languageInput.value = selectedLanguage;
            }

            // Update the save persona form language field
            var saveLanguageInput = document.getElementById('save-language');
            if (saveLanguageInput) {
                saveLanguageInput.value = selectedLanguage;
            }

            // Update the test browser form language input
            var testLanguageInput = document.getElementById('test-language-input');
            if (testLanguageInput) {
                testLanguageInput.value = selectedLanguage;
                console.log("Set language to:", selectedLanguage);
            }
        });
    }

    // This duplicate event handler is removed as it's already handled by the updated setGeolocationButton handler below

    // Update our setGeolocationButton handler to work with separate lat/lng fields
    var setGeolocationButton = document.getElementById('set-geolocation');
    if (setGeolocationButton) {
        // Clear previous event listeners by cloning and replacing
        var newSetGeoButton = setGeolocationButton.cloneNode(true);
        setGeolocationButton.parentNode.replaceChild(newSetGeoButton, setGeolocationButton);
        
        newSetGeoButton.addEventListener('click', function () {
            var targetLatitude = document.getElementById('target-latitude').value.trim();
            var targetLongitude = document.getElementById('target-longitude').value.trim();
            
            // Combine latitude and longitude into a single string
            var combinedGeolocation = targetLatitude + ', ' + targetLongitude;
            
            // Update geolocation in the Persona section
            document.getElementById('geolocation').textContent = combinedGeolocation;

            // Update the hidden geolocation field in the form
            var geolocationInput = document.getElementById('form-geolocation');
            if (geolocationInput) {
                geolocationInput.value = combinedGeolocation;
            }

            // Update the save persona form geolocation field
            var saveGeolocationInput = document.getElementById('save-geolocation');
            if (saveGeolocationInput) {
                saveGeolocationInput.value = combinedGeolocation;
            }
            
            // Update the test browser form geolocation input
            var testGeolocationInput = document.getElementById('test-geolocation-input');
            if (testGeolocationInput) {
                testGeolocationInput.value = combinedGeolocation;
                console.log("Set geolocation to:", combinedGeolocation);
            }
            
            // Update map with the new coordinates
            const lat = parseFloat(targetLatitude);
            const lng = parseFloat(targetLongitude);
            
            if (!isNaN(lat) && !isNaN(lng)) {
                
                if (!isNaN(lat) && !isNaN(lng)) {
                    // Update latitude and longitude input fields
                    const latitudeInput = document.getElementById('latitude');
                    const longitudeInput = document.getElementById('longitude');
                    if (latitudeInput && longitudeInput) {
                        latitudeInput.value = lat;
                        longitudeInput.value = lng;
                    }
                    
                    // Clear existing markers and add a new one
                    if (window.markersLayer) {
                        window.markersLayer.clearLayers();
                    }
                    
                    // Add marker and center map
                    L.marker([lat, lng])
                        .addTo(window.markersLayer)
                        .bindPopup(`<b>Custom Location</b><br>Coordinates: ${lat.toFixed(4)}, ${lng.toFixed(4)}`)
                        .openPopup();
                    
                    // Center the map on the new location with appropriate zoom
                    window.map.setView([lat, lng], 5);
                }
            }
        });
    }

    // Update form fields before submitting
    var testBrowserForm = document.getElementById('test-browser-form');
    if (testBrowserForm) {
        testBrowserForm.addEventListener('submit', function (event) {
            // Get current values
            var currentLanguage = document.getElementById('target-language').value;
            var targetLatitude = document.getElementById('target-latitude').value.trim();
            var targetLongitude = document.getElementById('target-longitude').value.trim();
            var combinedGeolocation = targetLatitude + ', ' + targetLongitude;

            console.log("Applying and testing with language:", currentLanguage, "and geolocation:", combinedGeolocation);

            // Update the form fields
            document.getElementById('test-language-input').value = currentLanguage;
            document.getElementById('test-geolocation-input').value = combinedGeolocation;
        });
    }

    // Initialize test browser form with current values
    // Set initial language value
    var currentLanguage = document.getElementById('target-language').value;
    var testLanguageInput = document.getElementById('test-language-input');
    if (testLanguageInput && currentLanguage) {
        testLanguageInput.value = currentLanguage;
    }

    // Set initial geolocation value from target latitude and longitude
    var targetLatitude = document.getElementById('target-latitude').value.trim();
    var targetLongitude = document.getElementById('target-longitude').value.trim();
    var testGeolocationInput = document.getElementById('test-geolocation-input');
    
    if (testGeolocationInput && targetLatitude && targetLongitude) {
        var combinedGeolocation = targetLatitude + ', ' + targetLongitude;
        testGeolocationInput.value = combinedGeolocation;
        console.log("Setting test geolocation input to:", combinedGeolocation);
    } else if (testGeolocationInput) {
        // If no geolocation is set, use the current geolocation from the persona section
        var personaGeolocation = document.getElementById('geolocation').textContent;
        if (personaGeolocation && personaGeolocation !== 'Fetching...' && personaGeolocation !== 'Unavailable' && personaGeolocation !== 'Not supported') {
            testGeolocationInput.value = personaGeolocation;
            console.log("Setting test geolocation input from persona:", personaGeolocation);
        }
    }

    // Set language
    document.getElementById('browser-language').textContent = navigator.language || 'Unavailable';

    // Set user agent
    document.getElementById('browser-user-agent').textContent = navigator.userAgent || 'Unavailable';

    // Set geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            document.getElementById('browser-geolocation').textContent =
                position.coords.latitude + ', ' + position.coords.longitude;
        }, function () {
            document.getElementById('browser-geolocation').textContent = 'Unavailable';
        });
    } else {
        document.getElementById('browser-geolocation').textContent = 'Not supported';
    }

    // Handle flash messages from cookies
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    const flashMessage = getCookie('flash_message');
    if (flashMessage) {
        const flashContainer = document.getElementById('flash-message-container');
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = decodeURIComponent(flashMessage) +
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        flashContainer.appendChild(alertDiv);

        // Clear the cookie
        document.cookie = 'flash_message=; Max-Age=0; path=/;';
    }

    // Add event listeners for tab changes to update form fields with current geolocation and language
    document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(function (tabLink) {
        tabLink.addEventListener('shown.bs.tab', function (event) {
            const targetTab = event.target.getAttribute('aria-controls');
            const currentGeolocation = document.getElementById('geolocation').textContent;
            const currentLanguage = document.querySelector('.custom-card .row .col:nth-child(2)').textContent.replace('Language:', '').trim();
            
            // Get country, city, and region from data attributes
            const currentCountry = document.body.getAttribute('data-country') || '';
            const currentCity = document.body.getAttribute('data-city') || '';
            const currentRegion = document.body.getAttribute('data-region') || '';

            // Add hidden fields to the forms for demographic data
            if (targetTab === 'psychographic') {
                // Add hidden fields to psychographic form
                const form = document.getElementById('psychographic-form');
                addHiddenFields(form, currentGeolocation, currentLanguage, currentCountry, currentCity, currentRegion);
            } else if (targetTab === 'behavior') {
                // Add hidden fields to behavioral form
                const form = document.getElementById('behavioral-form');
                addHiddenFields(form, currentGeolocation, currentLanguage, currentCountry, currentCity, currentRegion);
            } else if (targetTab === 'contextual') {
                // Add hidden fields to contextual form
                const form = document.getElementById('contextual-form');
                addHiddenFields(form, currentGeolocation, currentLanguage, currentCountry, currentCity, currentRegion);
            }
        });
    });

    // Function to add hidden fields to a form
    function addHiddenFields(form, geolocation, language, country, city, region) {
        // Check if fields already exist
        if (!form.querySelector('input[name="geolocation"]')) {
            const geoField = document.createElement('input');
            geoField.type = 'hidden';
            geoField.name = 'geolocation';
            geoField.value = geolocation;
            form.appendChild(geoField);
        } else {
            form.querySelector('input[name="geolocation"]').value = geolocation;
        }

        if (!form.querySelector('input[name="language"]')) {
            const langField = document.createElement('input');
            langField.type = 'hidden';
            langField.name = 'language';
            langField.value = language;
            form.appendChild(langField);
        } else {
            form.querySelector('input[name="language"]').value = language;
        }

        if (!form.querySelector('input[name="country"]')) {
            const countryField = document.createElement('input');
            countryField.type = 'hidden';
            countryField.name = 'country';
            countryField.value = country;
            form.appendChild(countryField);
        } else {
            form.querySelector('input[name="country"]').value = country;
        }

        if (!form.querySelector('input[name="city"]')) {
            const cityField = document.createElement('input');
            cityField.type = 'hidden';
            cityField.name = 'city';
            cityField.value = city;
            form.appendChild(cityField);
        } else {
            form.querySelector('input[name="city"]').value = city;
        }

        if (!form.querySelector('input[name="region"]')) {
            const regionField = document.createElement('input');
            regionField.type = 'hidden';
            regionField.name = 'region';
            regionField.value = region;
            form.appendChild(regionField);
        } else {
            form.querySelector('input[name="region"]').value = region;
        }
    }

    // Add event listener for manual lat/lng entry to update map
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    
    if (latitudeInput && longitudeInput) {
        const updateMapFromCoords = function() {
            const lat = parseFloat(latitudeInput.value);
            const lng = parseFloat(longitudeInput.value);
            
            if (!isNaN(lat) && !isNaN(lng)) {
                // Update the target latitude and longitude inputs
                const targetLatitudeInput = document.getElementById('target-latitude');
                const targetLongitudeInput = document.getElementById('target-longitude');
                if (targetLatitudeInput && targetLongitudeInput) {
                    targetLatitudeInput.value = lat;
                    targetLongitudeInput.value = lng;
                }
                
                // Clear existing markers and add a new one
                window.markersLayer.clearLayers();
                
                // Add marker and center map
                L.marker([lat, lng])
                    .addTo(window.markersLayer)
                    .bindPopup(`<b>Custom Location</b><br>Coordinates: ${lat.toFixed(4)}, ${lng.toFixed(4)}`)
                    .openPopup();
                
                // Center the map on the new location with appropriate zoom
                window.map.setView([lat, lng], 5);
            }
        };
        
        // Add blur event listeners to update map when user finishes typing
        latitudeInput.addEventListener('blur', updateMapFromCoords);
        longitudeInput.addEventListener('blur', updateMapFromCoords);
        
        // Also add a button to manually update from the inputs
        const coordsCard = latitudeInput.closest('.custom-card');
        if (coordsCard) {
            const updateButton = document.createElement('button');
            updateButton.type = 'button';
            updateButton.className = 'btn btn-primary mt-2';
            updateButton.textContent = 'Update Map';
            updateButton.addEventListener('click', updateMapFromCoords);
            coordsCard.appendChild(updateButton);
        }
    }
});
