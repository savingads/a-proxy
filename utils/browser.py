"""
Browser automation module using Playwright.

Replaces the Selenium-based selenium_proxy.py with a cross-platform
Playwright implementation that supports geolocation, locale, timezone,
and proxy emulation per browser context.
"""
import logging
import os
import json
import hashlib
import time
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

from config import BROWSER_HEADLESS, PROXY_URL

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages a singleton Playwright browser instance with per-request contexts."""

    _instance = None
    _playwright = None
    _browser = None

    def __init__(self):
        raise RuntimeError("Use BrowserManager.get_instance() instead")

    @classmethod
    def get_instance(cls):
        """Get or create the singleton BrowserManager."""
        if cls._instance is None:
            instance = object.__new__(cls)
            cls._instance = instance
        return cls._instance

    def _ensure_browser(self):
        """Lazily start Playwright and launch Chromium."""
        if self._browser is None:
            logger.info("Starting Playwright and launching Chromium...")
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=BROWSER_HEADLESS
            )
            logger.info("Chromium browser launched successfully")

    def create_context(self, locale=None, geolocation=None, timezone_id=None, proxy=None):
        """
        Create an isolated browser context with emulation settings.

        Args:
            locale: Browser locale (e.g. "de-DE", "en-US")
            geolocation: Dict with "latitude" and "longitude", or "lat,lng" string
            timezone_id: Timezone (e.g. "Europe/Berlin")
            proxy: Proxy URL string (e.g. "socks5://host:port")

        Returns:
            BrowserContext instance
        """
        self._ensure_browser()

        context_options = {}

        if locale:
            context_options["locale"] = locale

        if geolocation:
            if isinstance(geolocation, str):
                try:
                    lat, lng = map(float, geolocation.split(","))
                    geolocation = {"latitude": lat, "longitude": lng}
                except (ValueError, AttributeError):
                    logger.error(f"Invalid geolocation string: {geolocation}")
                    geolocation = None

            if geolocation:
                context_options["geolocation"] = geolocation
                context_options["permissions"] = ["geolocation"]

        if timezone_id:
            context_options["timezone_id"] = timezone_id

        if proxy:
            context_options["proxy"] = {"server": proxy}

        context = self._browser.new_context(**context_options)
        return context

    def visit_page(self, url, locale=None, geolocation=None, timezone_id=None,
                   proxy=None, screenshot=False, wait_time=5):
        """
        Visit a page with emulated settings and optionally take a screenshot.

        Args:
            url: URL to visit
            locale: Browser locale
            geolocation: Geolocation string "lat,lng" or dict
            timezone_id: Timezone string
            proxy: Proxy URL
            screenshot: Whether to take a screenshot
            wait_time: Seconds to wait after page load

        Returns:
            Dict with page info: {title, url, screenshot_path}
        """
        context = self.create_context(
            locale=locale, geolocation=geolocation,
            timezone_id=timezone_id, proxy=proxy
        )
        try:
            page = context.new_page()
            logger.info(f"Visiting {url} with locale={locale}, geolocation={geolocation}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(wait_time * 1000)

            result = {
                "title": page.title(),
                "url": page.url,
                "screenshot_path": None,
            }

            if screenshot:
                screenshots_dir = "screenshots"
                os.makedirs(screenshots_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                screenshot_path = os.path.join(screenshots_dir, f"screenshot-{timestamp}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved to {screenshot_path}")
                result["screenshot_path"] = screenshot_path

            return result
        finally:
            context.close()

    def archive_page(self, url, locale=None, geolocation=None, timezone_id=None,
                     proxy=None, persona_id=None):
        """
        Archive a webpage: save HTML, screenshot, metadata, and database record.

        Args:
            url: URL to archive
            locale: Browser locale (e.g. "en-US")
            geolocation: Geolocation string "lat,lng" or dict
            timezone_id: Timezone string
            proxy: Proxy URL
            persona_id: ID of persona used

        Returns:
            Dict with archive info, or None on failure
        """
        context = self.create_context(
            locale=locale, geolocation=geolocation,
            timezone_id=timezone_id, proxy=proxy
        )
        try:
            page = context.new_page()
            logger.info(f"Archiving {url} with locale={locale}, geolocation={geolocation}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            page_title = page.title()
            logger.info(f"Page title: {page_title}")

            # Get HTTP status and headers via requests
            http_status = None
            headers = {}
            content_type = None
            content_length = None
            try:
                req_headers = {}
                if locale:
                    req_headers["Accept-Language"] = locale
                response = requests.get(url, headers=req_headers, timeout=10)
                http_status = response.status_code
                headers = dict(response.headers)
                content_type = response.headers.get("Content-Type", "")
                content_length = len(response.content)
            except Exception as e:
                logger.error(f"Error getting HTTP information: {e}")

            # Create archive directory structure
            url_hash = hashlib.md5(url.encode()).hexdigest()
            archives_dir = "archives"
            os.makedirs(archives_dir, exist_ok=True)

            url_dir = os.path.join(archives_dir, url_hash)
            os.makedirs(url_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            memento_dir = os.path.join(url_dir, timestamp)
            os.makedirs(memento_dir, exist_ok=True)

            # Save HTML content
            html_content = page.content()
            html_file_path = os.path.join(memento_dir, "content.html")
            with open(html_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML content saved to {html_file_path}")

            # Save screenshot
            screenshot_path = os.path.join(memento_dir, "screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Screenshot saved to {screenshot_path}")

            # Save metadata
            metadata = {
                "url": url,
                "title": page_title,
                "timestamp": timestamp,
                "language": locale,
                "geolocation": geolocation if isinstance(geolocation, str) else None,
                "persona_id": persona_id,
                "http_status": http_status,
                "content_type": content_type,
                "content_length": content_length,
                "headers": headers,
            }
            metadata_file_path = os.path.join(memento_dir, "metadata.json")
            with open(metadata_file_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Metadata saved to {metadata_file_path}")

            # Save/update URL-level metadata
            url_metadata_path = os.path.join(url_dir, "metadata.json")
            if os.path.exists(url_metadata_path):
                with open(url_metadata_path, "r", encoding="utf-8") as f:
                    url_metadata = json.load(f)
            else:
                url_metadata = {"url": url, "first_archived": timestamp, "mementos": []}

            url_metadata["mementos"].append(timestamp)
            url_metadata["last_archived"] = timestamp
            with open(url_metadata_path, "w", encoding="utf-8") as f:
                json.dump(url_metadata, f, indent=2)

            # Save to database
            import database

            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM archived_websites WHERE uri_r = ?", (url,))
            existing = cursor.fetchone()
            conn.close()

            if existing:
                archived_website_id = existing["id"]
                logger.info(f"URL already exists in database with ID {archived_website_id}")
            else:
                archived_website_id = database.save_archived_website(
                    url=url, persona_id=persona_id,
                    archive_type="filesystem", archive_location=url_dir
                )
                logger.info(f"Saved archived website with ID {archived_website_id}")

            memento_id = database.save_memento(
                archived_website_id=archived_website_id,
                memento_location=memento_dir,
                http_status=http_status,
                content_type=content_type,
                content_length=content_length,
                headers=headers,
                screenshot_path=screenshot_path,
            )
            logger.info(f"Saved memento with ID {memento_id}")

            return {
                "archived_website_id": archived_website_id,
                "memento_id": memento_id,
                "url": url,
                "memento_location": memento_dir,
                "screenshot_path": screenshot_path,
            }

        except Exception as e:
            logger.error(f"Error archiving page: {e}", exc_info=True)
            return None
        finally:
            context.close()

    def shutdown(self):
        """Close the browser and stop Playwright."""
        if self._browser:
            logger.info("Shutting down browser...")
            try:
                self._browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            self.__class__._browser = None

        if self._playwright:
            try:
                self._playwright.stop()
            except Exception as e:
                logger.error(f"Error stopping Playwright: {e}")
            self.__class__._playwright = None

        logger.info("Browser manager shut down")
