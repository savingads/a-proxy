from selenium_proxy import setup_vpn_browser
import logging
import time
import sys
import argparse

logging.basicConfig(level=logging.DEBUG)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Visit a webpage with specific language and geolocation settings')
    parser.add_argument('url', help='URL to visit')
    parser.add_argument('--language', default='en-US', help='Language setting (e.g., en-US, pt-BR)')
    parser.add_argument('--geolocation', help='Geolocation coordinates (format: latitude,longitude)')
    args = parser.parse_args()

    # Log the parameters
    logging.debug(f"URL: {args.url}")
    logging.debug(f"Language: {args.language}")
    logging.debug(f"Geolocation: {args.geolocation}")

    # Initialize WebDriver with the specified parameters
    driver = setup_vpn_browser(
        language=args.language,
        geolocation=args.geolocation,
        url=args.url
    )

    # Print the page title
    logging.debug(f"Page title: {driver.title}")

    # Capture a screenshot
    driver.save_screenshot('screenshot.png')
    logging.debug("Screenshot saved as screenshot.png")

    # Wait before closing
    time.sleep(30)

    # Close the WebDriver
    driver.quit()

if __name__ == "__main__":
    main()
