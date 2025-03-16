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
            lat, lng = map(float, geolocation.split(','))
            # Navigate to about:blank first to execute the geolocation override
            driver.get("about:blank")
            # Override geolocation using JavaScript
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": lat,
                "longitude": lng,
                "accuracy": 100
            })
            logging.debug("Geolocation override applied")
        except Exception as e:
            logging.error(f"Error setting geolocation override: {e}")
    
    # Navigate to the URL if provided
    if url:
        driver.get(url)
    
    return driver
