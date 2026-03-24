from selenium_proxy import setup_vpn_browser
import logging
import time
import sys
import argparse
import os
import json
import hashlib
import requests
from datetime import datetime
from selenium.common.exceptions import WebDriverException
import database
import shutil

# Configure logging to show more detailed information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_dir_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug(f"Created directory: {directory}")

def archive_page(url, language="en-US", geolocation=None, persona_id=None):
    """
    Archive a webpage with specific language and geolocation settings
    
    Args:
        url: URL to archive
        language: Language setting (e.g., en-US, pt-BR)
        geolocation: Geolocation coordinates (format: latitude,longitude)
        persona_id: ID of the persona used to visit the page
    
    Returns:
        Dictionary with archive information
    """
    driver = None
    try:
        # Log the parameters
        logger.info(f"Archiving page with the following settings:")
        logger.info(f"  URL: {url}")
        logger.info(f"  Language: {language}")
        logger.info(f"  Geolocation: {geolocation}")
        logger.info(f"  Persona ID: {persona_id}")
        
        # Create a hash of the URL for the archive location
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Create the archive directory structure
        archives_dir = 'archives'
        ensure_dir_exists(archives_dir)
        
        url_dir = os.path.join(archives_dir, url_hash)
        ensure_dir_exists(url_dir)
        
        # Create a timestamp for this memento
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        memento_dir = os.path.join(url_dir, timestamp)
        ensure_dir_exists(memento_dir)
        
        # Initialize WebDriver with the specified parameters
        logger.debug("Initializing WebDriver...")
        driver = setup_vpn_browser(
            language=language,
            geolocation=geolocation,
            url=url
        )
        
        # Wait for the page to load
        time.sleep(5)
        
        # Get page information
        page_title = driver.title
        logger.info(f"Page title: {page_title}")
        
        # Get HTTP status and headers using requests
        # Note: This won't capture the exact headers that Selenium sees
        try:
            response = requests.get(url, headers={'Accept-Language': language})
            http_status = response.status_code
            headers = dict(response.headers)
            content_type = response.headers.get('Content-Type', '')
            content_length = len(response.content)
        except Exception as e:
            logger.error(f"Error getting HTTP information: {e}")
            http_status = None
            headers = {}
            content_type = None
            content_length = None
        
        # Save the page HTML
        html_content = driver.page_source
        html_file_path = os.path.join(memento_dir, 'content.html')
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"HTML content saved to {html_file_path}")
        
        # Capture a screenshot
        screenshot_path = os.path.join(memento_dir, 'screenshot.png')
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved as {screenshot_path}")
        
        # Save metadata
        metadata = {
            'url': url,
            'title': page_title,
            'timestamp': timestamp,
            'language': language,
            'geolocation': geolocation,
            'persona_id': persona_id,
            'http_status': http_status,
            'content_type': content_type,
            'content_length': content_length,
            'headers': headers
        }
        
        metadata_file_path = os.path.join(memento_dir, 'metadata.json')
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to {metadata_file_path}")
        
        # Save overall URL metadata if it doesn't exist
        url_metadata_path = os.path.join(url_dir, 'metadata.json')
        if not os.path.exists(url_metadata_path):
            url_metadata = {
                'url': url,
                'first_archived': timestamp,
                'mementos': []
            }
            with open(url_metadata_path, 'w', encoding='utf-8') as f:
                json.dump(url_metadata, f, indent=2)
        
        # Update the URL metadata to include this memento
        with open(url_metadata_path, 'r', encoding='utf-8') as f:
            url_metadata = json.load(f)
        
        url_metadata['mementos'].append(timestamp)
        url_metadata['last_archived'] = timestamp
        
        with open(url_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(url_metadata, f, indent=2)
        
        # Save to database
        # First check if this URL is already archived
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM archived_websites WHERE uri_r = ?", (url,))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            archived_website_id = existing['id']
            logger.info(f"URL already exists in database with ID {archived_website_id}")
        else:
            # Save the archived website
            archived_website_id = database.save_archived_website(
                url=url,
                persona_id=persona_id,
                archive_type='filesystem',
                archive_location=url_dir
            )
            logger.info(f"Saved archived website to database with ID {archived_website_id}")
        
        # Save the memento
        memento_id = database.save_memento(
            archived_website_id=archived_website_id,
            memento_location=memento_dir,
            http_status=http_status,
            content_type=content_type,
            content_length=content_length,
            headers=headers,
            screenshot_path=screenshot_path
        )
        logger.info(f"Saved memento to database with ID {memento_id}")
        
        # Placeholder for Internet Archive submission
        # In the future, this would submit the URL to the Internet Archive
        # and update the memento with the resulting archive.org URL
        logger.info("Internet Archive submission placeholder - not implemented yet")
        
        return {
            'archived_website_id': archived_website_id,
            'memento_id': memento_id,
            'url': url,
            'memento_location': memento_dir,
            'screenshot_path': screenshot_path
        }
        
    except WebDriverException as wde:
        logger.error(f"WebDriver error: {wde}")
        print(f"\nERROR: Failed to launch browser. Details: {wde}\n")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nERROR: An unexpected error occurred. Details: {e}\n")
        return None
    finally:
        # Ensure we clean up the WebDriver
        try:
            if driver:
                logger.info("Closing WebDriver...")
                driver.quit()
                logger.info("WebDriver closed successfully.")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Archive a webpage with specific language and geolocation settings')
    parser.add_argument('url', help='URL to archive')
    parser.add_argument('--language', default='en-US', help='Language setting (e.g., en-US, pt-BR)')
    parser.add_argument('--geolocation', help='Geolocation coordinates (format: latitude,longitude)')
    parser.add_argument('--persona-id', type=int, help='ID of the persona to use')
    args = parser.parse_args()
    
    # Archive the page
    result = archive_page(
        url=args.url,
        language=args.language,
        geolocation=args.geolocation,
        persona_id=args.persona_id
    )
    
    if result:
        print(f"\nArchived {args.url} successfully.")
        print(f"Archived website ID: {result['archived_website_id']}")
        print(f"Memento ID: {result['memento_id']}")
        print(f"Memento location: {result['memento_location']}")
        print(f"Screenshot: {result['screenshot_path']}")
    else:
        print(f"\nFailed to archive {args.url}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
