from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import logging
import os
import shutil

def setup_vpn_browser(language="en-US", geolocation=None, url=None):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument(f'--lang={language}')
    
    # Try to find Chrome/Chromium in common locations
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # For macOS
    ]
    
    # Find the first available Chrome binary
    chrome_binary = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_binary = path
            logging.debug(f"Found Chrome binary at: {chrome_binary}")
            break
    
    if chrome_binary:
        options.binary_location = chrome_binary
    else:
        logging.warning("Chrome binary not found in common locations, will try to use system default")
    
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
    
    # Use the system chromedriver (which we just installed)
    try:
        chromedriver_path = shutil.which('chromedriver')
        if chromedriver_path:
            logging.debug(f"Using chromedriver found at: {chromedriver_path}")
            driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
        else:
            logging.debug("Chromedriver not found in PATH")
            driver = webdriver.Chrome(options=options)  # Let Selenium find it
    except Exception as e:
        logging.error(f"Failed to initialize Chrome: {e}")
        raise
    
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
