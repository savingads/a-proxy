from selenium_proxy import setup_vpn_browser
import logging
import time

logging.basicConfig(level=logging.DEBUG)

# Initialize WebDriver (Now using VPN, No Proxy)
driver = setup_vpn_browser()

# Visit the page directly
logging.debug("Visiting https://www.google.com")
driver.get("https://www.google.com")

# Print the page title
logging.debug(f"Page title: {driver.title}")

# Capture a screenshot
driver.save_screenshot('screenshot.png')
logging.debug("Screenshot saved as screenshot.png")

# Wait before closing
time.sleep(10)

# Close the WebDriver
driver.quit()
