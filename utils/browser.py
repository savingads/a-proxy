"""
Browser automation module using Playwright.

Supports two modes:
- Headless: ephemeral contexts for visit_page() and archive_page()
- Headful: persistent browsing sessions launched via start_session()
"""
import logging
import os
import json
import hashlib
import requests
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from playwright.sync_api import sync_playwright

from config import BROWSER_HEADLESS, PROXY_URL

logger = logging.getLogger(__name__)


@dataclass
class BrowsingSession:
    """A persistent headful browsing session tied to a persona."""
    persona_id: int
    context: Any  # BrowserContext
    page: Any  # Page
    history: List[Dict[str, str]] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)


class BrowserManager:
    """Manages Playwright browser instances for headless automation and headful sessions."""

    _instance = None
    _playwright = None
    _browser = None  # headless browser for visit_page/archive_page
    _headful_browser = None  # headful browser for interactive sessions
    _active_session: Optional[BrowsingSession] = None

    def __init__(self):
        raise RuntimeError("Use BrowserManager.get_instance() instead")

    @classmethod
    def get_instance(cls):
        """Get or create the singleton BrowserManager."""
        if cls._instance is None:
            instance = object.__new__(cls)
            cls._instance = instance
        return cls._instance

    def _ensure_playwright(self):
        """Lazily start Playwright."""
        if self._playwright is None:
            self._playwright = sync_playwright().start()

    def _ensure_browser(self):
        """Lazily launch the headless browser."""
        self._ensure_playwright()
        if self._browser is None:
            logger.info("Launching headless Chromium...")
            self._browser = self._playwright.chromium.launch(headless=BROWSER_HEADLESS)
            logger.info("Headless Chromium launched successfully")

    def _ensure_headful_browser(self):
        """Lazily launch the headful browser for interactive sessions."""
        self._ensure_playwright()
        if self._headful_browser is None:
            logger.info("Launching headful Chromium for interactive browsing...")
            self._headful_browser = self._playwright.chromium.launch(headless=False)
            logger.info("Headful Chromium launched successfully")

    def _build_context_options(self, locale=None, geolocation=None, timezone_id=None, proxy=None):
        """Build context options dict from persona settings."""
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

        return context_options

    def create_context(self, locale=None, geolocation=None, timezone_id=None, proxy=None):
        """Create an isolated browser context with emulation settings."""
        self._ensure_browser()
        context_options = self._build_context_options(locale, geolocation, timezone_id, proxy)
        return self._browser.new_context(**context_options)

    # ── Headful session management ──────────────────────────────────────

    def start_session(self, persona_id, locale=None, geolocation=None,
                      timezone_id=None, proxy=None, start_url="https://www.google.com"):
        """Launch a headful browsing session for a persona."""
        self.stop_session()
        self._ensure_headful_browser()

        context_options = self._build_context_options(locale, geolocation, timezone_id, proxy)
        context = self._headful_browser.new_context(**context_options)
        page = context.new_page()

        session = BrowsingSession(persona_id=persona_id, context=context, page=page)

        def on_navigate(frame):
            if frame == page.main_frame:
                try:
                    title = page.title()
                except Exception:
                    title = ""
                session.history.append({
                    "url": frame.url,
                    "title": title,
                    "timestamp": datetime.now().isoformat(),
                })
        page.on("framenavigated", on_navigate)

        logger.info(f"Starting headful session for persona {persona_id}, navigating to {start_url}")
        page.goto(start_url, wait_until="domcontentloaded", timeout=30000)

        self.__class__._active_session = session
        return session

    def get_session_status(self) -> Dict[str, Any]:
        """Return the current browsing session status."""
        session = self._active_session
        if not session:
            return {"active": False}

        try:
            current_url = session.page.url
            current_title = session.page.title()
        except Exception:
            self.stop_session()
            return {"active": False}

        return {
            "active": True,
            "persona_id": session.persona_id,
            "current_url": current_url,
            "current_title": current_title,
            "history": session.history,
            "started_at": session.started_at.isoformat(),
        }

    def capture_page(self) -> Optional[Dict[str, str]]:
        """Take a screenshot of the active session page."""
        session = self._active_session
        if not session:
            return None

        try:
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join(screenshots_dir, f"session-{timestamp}.png")
            session.page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Session screenshot saved to {screenshot_path}")
            return {
                "screenshot_path": screenshot_path,
                "url": session.page.url,
                "title": session.page.title(),
            }
        except Exception as e:
            logger.error(f"Error capturing session page: {e}", exc_info=True)
            return None

    def archive_session_page(self, persona_id=None) -> Optional[Dict[str, Any]]:
        """Archive the current page from the active browsing session."""
        session = self._active_session
        if not session:
            return None

        page = session.page
        persona_id = persona_id or session.persona_id

        try:
            url = page.url
            page_title = page.title()
            locale = None
            geolocation_str = None
            logger.info(f"Archiving session page: {url}")

            # Get HTTP info
            http_status = None
            headers = {}
            content_type = None
            content_length = None
            try:
                response = requests.get(url, timeout=10)
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

            # Save HTML
            html_content = page.content()
            html_file_path = os.path.join(memento_dir, "content.html")
            with open(html_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Save screenshot
            screenshot_path = os.path.join(memento_dir, "screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)

            # Save metadata
            metadata = {
                "url": url,
                "title": page_title,
                "timestamp": timestamp,
                "language": locale,
                "geolocation": geolocation_str,
                "persona_id": persona_id,
                "http_status": http_status,
                "content_type": content_type,
                "content_length": content_length,
                "headers": headers,
            }
            metadata_file_path = os.path.join(memento_dir, "metadata.json")
            with open(metadata_file_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

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
            else:
                archived_website_id = database.save_archived_website(
                    url=url, persona_id=persona_id,
                    archive_type="filesystem", archive_location=url_dir
                )

            memento_id = database.save_memento(
                archived_website_id=archived_website_id,
                memento_location=memento_dir,
                http_status=http_status,
                content_type=content_type,
                content_length=content_length,
                headers=headers,
                screenshot_path=screenshot_path,
            )

            logger.info(f"Session page archived: website={archived_website_id}, memento={memento_id}")
            return {
                "archived_website_id": archived_website_id,
                "memento_id": memento_id,
                "url": url,
                "title": page_title,
                "memento_location": memento_dir,
                "screenshot_path": screenshot_path,
            }

        except Exception as e:
            logger.error(f"Error archiving session page: {e}", exc_info=True)
            return None

    def stop_session(self):
        """Close the active browsing session."""
        session = self._active_session
        if session:
            logger.info(f"Stopping browsing session for persona {session.persona_id}")
            try:
                session.context.close()
            except Exception as e:
                logger.error(f"Error closing session context: {e}")
            self.__class__._active_session = None

    # ── Headless automation (existing API) ──────────────────────────────

    def visit_page(self, url, locale=None, geolocation=None, timezone_id=None,
                   proxy=None, screenshot=False, wait_time=5):
        """Visit a page with emulated settings and optionally take a screenshot."""
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
        """Archive a webpage: save HTML, screenshot, metadata, and database record."""
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

            url_hash = hashlib.md5(url.encode()).hexdigest()
            archives_dir = "archives"
            os.makedirs(archives_dir, exist_ok=True)

            url_dir = os.path.join(archives_dir, url_hash)
            os.makedirs(url_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            memento_dir = os.path.join(url_dir, timestamp)
            os.makedirs(memento_dir, exist_ok=True)

            html_content = page.content()
            html_file_path = os.path.join(memento_dir, "content.html")
            with open(html_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            screenshot_path = os.path.join(memento_dir, "screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)

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

            import database

            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM archived_websites WHERE uri_r = ?", (url,))
            existing = cursor.fetchone()
            conn.close()

            if existing:
                archived_website_id = existing["id"]
            else:
                archived_website_id = database.save_archived_website(
                    url=url, persona_id=persona_id,
                    archive_type="filesystem", archive_location=url_dir
                )

            memento_id = database.save_memento(
                archived_website_id=archived_website_id,
                memento_location=memento_dir,
                http_status=http_status,
                content_type=content_type,
                content_length=content_length,
                headers=headers,
                screenshot_path=screenshot_path,
            )

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
        """Close all browsers and stop Playwright."""
        self.stop_session()

        if self._headful_browser:
            logger.info("Shutting down headful browser...")
            try:
                self._headful_browser.close()
            except Exception as e:
                logger.error(f"Error closing headful browser: {e}")
            self.__class__._headful_browser = None

        if self._browser:
            logger.info("Shutting down headless browser...")
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
