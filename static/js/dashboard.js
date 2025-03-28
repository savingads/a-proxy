/* globals Chart:false */

(() => {
  'use strict'

  // Graphs
  const ctx = document.getElementById('myChart')
  // eslint-disable-next-line no-unused-vars
  const myChart = ctx ? new Chart(ctx, {
    type: 'line',
    data: {
      labels: [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
      ],
      datasets: [{
        data: [
          15339,
          21345,
          18483,
          24003,
          23489,
          24092,
          12034
        ],
        lineTension: 0,
        backgroundColor: 'transparent',
        borderColor: '#007bff',
        borderWidth: 4,
        pointBackgroundColor: '#007bff'
      }]
    },
    options: {
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          boxPadding: 3
        }
      }
    }
  }) : null;

  // Handle region selection to update target browser settings
  document.addEventListener('DOMContentLoaded', function() {
    // Get region select element
    const regionSelect = document.getElementById('region');
    if (regionSelect) {
      regionSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const regionCode = selectedOption.getAttribute('data-code');
        
        // Update target language based on region
        updateTargetLanguage(regionCode);
        
        // Update target geolocation based on region
        updateTargetGeolocation(regionCode);
      });
    }

    // Initialize form fields
    initializeFormFields();
  });

  // Function to update target language based on region code
  function updateTargetLanguage(regionCode) {
    const targetLanguageSelect = document.getElementById('target-language');
    if (!targetLanguageSelect) return;
    
    // Map region codes to language values
    const regionLanguageMap = {
      'US': 'en-US',
      'BR': 'pt-BR',
      'DE': 'de-DE',
      'JP': 'ja-JP',
      'ZA': 'af-ZA'
    };
    
    const language = regionLanguageMap[regionCode];
    if (language) {
      // Set the selected language in the dropdown
      for (let i = 0; i < targetLanguageSelect.options.length; i++) {
        if (targetLanguageSelect.options[i].value === language) {
          targetLanguageSelect.selectedIndex = i;
          break;
        }
      }
      
      // Also update the hidden input for the test form
      const testLanguageInput = document.getElementById('test-language-input');
      if (testLanguageInput) {
        testLanguageInput.value = language;
      }
    }
  }

  // Function to update target geolocation based on region code
  function updateTargetGeolocation(regionCode) {
    // Map region codes to geolocation coordinates
    const regionGeolocationMap = {
      'US': { lat: '37.0902', lng: '-95.7129' },
      'BR': { lat: '-14.2350', lng: '-51.9253' },
      'DE': { lat: '51.1657', lng: '10.4515' },
      'JP': { lat: '36.2048', lng: '138.2529' },
      'ZA': { lat: '-30.5595', lng: '22.9375' }
    };
    
    const geolocation = regionGeolocationMap[regionCode];
    if (geolocation) {
      // Update latitude and longitude fields
      const targetLatitude = document.getElementById('target-latitude');
      const targetLongitude = document.getElementById('target-longitude');
      
      if (targetLatitude) targetLatitude.value = geolocation.lat;
      if (targetLongitude) targetLongitude.value = geolocation.lng;
      
      // Also update the hidden input for the test form
      const testGeolocationInput = document.getElementById('test-geolocation-input');
      if (testGeolocationInput) {
        testGeolocationInput.value = `${geolocation.lat},${geolocation.lng}`;
      }
    }
  }

  // Function to initialize form fields
  function initializeFormFields() {
    // Set up geolocation button
    const setGeolocationBtn = document.getElementById('set-geolocation');
    if (setGeolocationBtn) {
      setGeolocationBtn.addEventListener('click', function() {
        const lat = document.getElementById('target-latitude').value;
        const lng = document.getElementById('target-longitude').value;
        
        if (lat && lng) {
          const testGeolocationInput = document.getElementById('test-geolocation-input');
          if (testGeolocationInput) {
            testGeolocationInput.value = `${lat},${lng}`;
          }
        }
      });
    }
    
    // Set up language button
    const setLanguageBtn = document.getElementById('set-language');
    if (setLanguageBtn) {
      setLanguageBtn.addEventListener('click', function() {
        const language = document.getElementById('target-language').value;
        
        if (language) {
          const testLanguageInput = document.getElementById('test-language-input');
          if (testLanguageInput) {
            testLanguageInput.value = language;
          }
        }
      });
    }
  }
})()
