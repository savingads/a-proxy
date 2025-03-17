from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging

def setup_vpn_browser(language="en-US", geolocation=None, url=None):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(f'--lang={language}')
    options.binary_location = "/usr/bin/google-chrome"
    
    # Add geolocation if provided
    if geolocation:
        try:
            # Parse geolocation string (format: "latitude,longitude")
            lat, lng = map(float, geolocation.split(','))
            # Add geolocation override
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.geolocation": 1
            })
            logging.debug(f"Setting geolocation to: {lat}, {lng}")
        except Exception as e:
            logging.error(f"Error parsing geolocation: {e}")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Set geolocation using JavaScript if coordinates were provided
    if geolocation:
        try:
            # Parse geolocation string (format: "latitude,longitude")
            lat, lng = map(float, geolocation.split(','))
            
            # Log the geolocation values for debugging
            logging.debug(f"Applying geolocation override with: lat={lat}, lng={lng}")
            
            # Navigate to about:blank first to execute the geolocation override
            driver.get("about:blank")
            
            # Override geolocation using JavaScript
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": lat,
                "longitude": lng,
                "accuracy": 100
            })
            
            # Verify the geolocation was set
            logging.debug("Geolocation override applied successfully")
            
            # Add a script to the page that will override the navigator.geolocation API
            driver.execute_script("""
                // Store the original getCurrentPosition function
                const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
                
                // Override the getCurrentPosition function
                navigator.geolocation.getCurrentPosition = function(success, error, options) {
                    // Create a position object with our custom coordinates
                    const position = {
                        coords: {
                            latitude: %f,
                            longitude: %f,
                            accuracy: 100,
                            altitude: null,
                            altitudeAccuracy: null,
                            heading: null,
                            speed: null
                        },
                        timestamp: Date.now()
                    };
                    
                    // Call the success callback with our custom position
                    success(position);
                };
                
                console.log('Geolocation API has been overridden with custom coordinates: %f, %f');
            """ % (lat, lng, lat, lng))
            
            logging.debug("Navigator.geolocation API override applied")
        except Exception as e:
            logging.error(f"Error setting geolocation override: {e}")
    
    # Navigate to the URL if provided
    if url:
        driver.get(url)
    
    return driver
