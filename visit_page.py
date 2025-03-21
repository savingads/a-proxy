from selenium_proxy import setup_vpn_browser
import logging
import time
import sys
import argparse
import os
from selenium.common.exceptions import WebDriverException

# Configure logging to show more detailed information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Visit a webpage with specific language and geolocation settings')
        parser.add_argument('url', help='URL to visit')
        parser.add_argument('--language', default='en-US', help='Language setting (e.g., en-US, pt-BR)')
        parser.add_argument('--geolocation', help='Geolocation coordinates (format: latitude,longitude)')
        parser.add_argument('--keep-open', action='store_true', help='Keep browser open until manually closed')
        parser.add_argument('--wait-time', type=int, default=60, help='Time to keep browser open (in seconds) if --keep-open is not used')
        args = parser.parse_args()

        # Log the parameters
        logger.info(f"Starting browser with the following settings:")
        logger.info(f"  URL: {args.url}")
        logger.info(f"  Language: {args.language}")
        logger.info(f"  Geolocation: {args.geolocation}")
        logger.info(f"  Keep open: {args.keep_open}")
        logger.info(f"  Wait time: {args.wait_time} seconds")

        # Initialize WebDriver with the specified parameters
        logger.debug("Initializing WebDriver...")
        driver = setup_vpn_browser(
            language=args.language,
            geolocation=args.geolocation,
            url=args.url
        )

        # Print the page title
        logger.info(f"Browser opened successfully. Page title: {driver.title}")

        # Create screenshots directory if it doesn't exist
        screenshots_dir = 'screenshots'
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # Generate a timestamped filename for the screenshot
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f'screenshot-{timestamp}.png')
        
        # Capture a screenshot
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved as {screenshot_path}")
        
        # Also save as the standard screenshot.png for backward compatibility
        driver.save_screenshot('screenshot.png')

        # Display notice about browser staying open
        if args.keep_open:
            logger.info("Browser will remain open until manually closed.")
            print("\n" + "="*50)
            print("TEST BROWSER IS RUNNING - DO NOT CLOSE THIS TERMINAL")
            print("Browser will remain open until you press Ctrl+C in this terminal")
            print("="*50 + "\n")
            
            try:
                # Keep the script running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt. Closing browser.")
        else:
            wait_time = args.wait_time
            logger.info(f"Browser will automatically close after {wait_time} seconds.")
            print(f"\nBrowser will automatically close after {wait_time} seconds.\n")
            time.sleep(wait_time)

    except WebDriverException as wde:
        logger.error(f"WebDriver error: {wde}")
        print(f"\nERROR: Failed to launch browser. Details: {wde}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nERROR: An unexpected error occurred. Details: {e}\n")
        sys.exit(1)
    finally:
        # Ensure we clean up the WebDriver
        try:
            if 'driver' in locals():
                logger.info("Closing WebDriver...")
                driver.quit()
                logger.info("WebDriver closed successfully.")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {e}")

if __name__ == "__main__":
    main()
