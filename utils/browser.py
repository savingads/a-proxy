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

from config import BROWSER_HEADLESS
from utils.persona_browser import (
    build_context_options as persona_context_options,
    channel_for_persona,
)

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

    def _build_context_options(self, locale=None, geolocation=None, timezone_id=None,
                               proxy=None, persona=None, har_path=None, video_dir=None,
                               extra_options=None):
        """Build Playwright context options from persona attributes and runtime settings.

        Layering (later wins):
          1. persona attributes (locale/geo/timezone/viewport/mobile) via the shared
             ``utils.persona_browser`` mapping -- the full 4-D signal, not just lang+geo.
          2. explicit locale/geolocation/timezone_id overrides (form-driven flows).
          3. runtime concerns: proxy, HAR recording, video recording.
          4. extra_options (escape hatch, overrides everything).
        """
        context_options = {}

        if persona:
            context_options.update(persona_context_options(persona))

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
                permissions = set(context_options.get("permissions", []))
                permissions.add("geolocation")
                context_options["permissions"] = list(permissions)

        if timezone_id:
            context_options["timezone_id"] = timezone_id

        if proxy:
            context_options["proxy"] = {"server": proxy}

        if har_path:
            context_options["record_har_path"] = str(har_path)

        if video_dir:
            context_options["record_video_dir"] = str(video_dir)

        if extra_options:
            context_options.update(extra_options)

        return context_options

    def create_context(self, locale=None, geolocation=None, timezone_id=None, proxy=None,
                       persona=None, har_path=None, video_dir=None):
        """Create an isolated browser context with emulation settings."""
        self._ensure_browser()
        context_options = self._build_context_options(
            locale=locale, geolocation=geolocation, timezone_id=timezone_id,
            proxy=proxy, persona=persona, har_path=har_path, video_dir=video_dir,
        )
        return self._browser.new_context(**context_options)

    # ── Headful session management ──────────────────────────────────────

    def start_session(self, persona_id, locale=None, geolocation=None,
                      timezone_id=None, proxy=None, persona=None,
                      start_url="https://www.google.com"):
        """Launch a headful browsing session for a persona."""
        self.stop_session()
        self._ensure_headful_browser()

        context_options = self._build_context_options(
            locale=locale, geolocation=geolocation, timezone_id=timezone_id,
            proxy=proxy, persona=persona,
        )
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

    @staticmethod
    def _memento_paths(url):
        """Compute and create the archives/<url_hash>/<timestamp>/ memento dir.

        Returns (url_dir, memento_dir, timestamp).
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        url_dir = os.path.join("archives", url_hash)
        memento_dir = os.path.join(url_dir, timestamp)
        os.makedirs(memento_dir, exist_ok=True)
        return url_dir, memento_dir, timestamp

    def _write_memento(self, page, url, *, locale=None, persona_id=None,
                       extra_metadata=None, memento_dir=None, timestamp=None,
                       save_to_db=True):
        """Persist an already-navigated ``page`` as a memento under archives/.

        Writes content.html, screenshot.png, metadata.json (common keys plus any
        ``extra_metadata``) and updates the url-level metadata index; unless
        ``save_to_db`` is False, also records the archived_website/memento rows.
        Callers that record HAR/video pre-create the dir and pass
        ``memento_dir``/``timestamp``. Shared by archive_page /
        archive_session_page / capture_as_persona.
        """
        page_title = page.title()

        # Best-effort HTTP info (adds Accept-Language when a locale is known).
        http_status = content_type = content_length = None
        headers = {}
        try:
            req_headers = {"Accept-Language": locale} if locale else {}
            response = requests.get(url, headers=req_headers, timeout=10)
            http_status = response.status_code
            headers = dict(response.headers)
            content_type = response.headers.get("Content-Type", "")
            content_length = len(response.content)
        except Exception as e:
            logger.error(f"Error getting HTTP information: {e}")

        if memento_dir is None:
            url_dir, memento_dir, timestamp = self._memento_paths(url)
        else:
            url_dir = os.path.dirname(memento_dir)

        html_path = os.path.join(memento_dir, "content.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())

        screenshot_path = os.path.join(memento_dir, "screenshot.png")
        page.screenshot(path=screenshot_path, full_page=True)

        metadata = {
            "url": url,
            "title": page_title,
            "timestamp": timestamp,
            "persona_id": persona_id,
            "http_status": http_status,
            "content_type": content_type,
            "content_length": content_length,
            "headers": headers,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        with open(os.path.join(memento_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # URL-level metadata index.
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

        result = {
            "url": url,
            "title": page_title,
            "memento_location": memento_dir,
            "screenshot_path": screenshot_path,
            "html_path": html_path,
            "http_status": http_status,
        }

        if save_to_db:
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
                    archive_type="filesystem", archive_location=url_dir,
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
            result["archived_website_id"] = archived_website_id
            result["memento_id"] = memento_id

        return result

    def archive_session_page(self, persona_id=None) -> Optional[Dict[str, Any]]:
        """Archive the current page from the active browsing session."""
        session = self._active_session
        if not session:
            return None

        page = session.page
        persona_id = persona_id or session.persona_id

        try:
            url = page.url
            logger.info(f"Archiving session page: {url}")
            result = self._write_memento(
                page, url, persona_id=persona_id,
                extra_metadata={"language": None, "geolocation": None},
            )
            logger.info("Session page archived: website=%s, memento=%s",
                        result.get("archived_website_id"), result.get("memento_id"))
            return result
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
                   proxy=None, persona=None, screenshot=False, wait_time=5):
        """Visit a page with emulated settings and optionally take a screenshot."""
        context = self.create_context(
            locale=locale, geolocation=geolocation,
            timezone_id=timezone_id, proxy=proxy, persona=persona,
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
                     proxy=None, persona=None, persona_id=None):
        """Archive a webpage: save HTML, screenshot, metadata, and database record."""
        context = self.create_context(
            locale=locale, geolocation=geolocation,
            timezone_id=timezone_id, proxy=proxy, persona=persona,
        )
        try:
            page = context.new_page()
            logger.info(f"Archiving {url} with locale={locale}, geolocation={geolocation}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            return self._write_memento(
                page, url, locale=locale, persona_id=persona_id,
                extra_metadata={
                    "language": locale,
                    "geolocation": geolocation if isinstance(geolocation, str) else None,
                },
            )

        except Exception as e:
            logger.error(f"Error archiving page: {e}", exc_info=True)
            return None
        finally:
            context.close()

    # ── Persona capture (full attributes + HAR/video + real profile) ────

    @staticmethod
    def _resolve_user_data_dir(profile_dir):
        """Return the Chrome user-data dir for launch_persistent_context.

        Accepts either the user-data dir itself (contains 'Local State'/'Default')
        or a parent holding exactly one such dir, e.g. an unzipped
        'Alex_Johnson_Browser_Profile/Alex_Johnson'.
        """
        def _is_user_data_dir(path):
            return (os.path.exists(os.path.join(path, "Local State"))
                    or os.path.isdir(os.path.join(path, "Default")))

        if _is_user_data_dir(profile_dir):
            return profile_dir
        try:
            for name in os.listdir(profile_dir):
                sub = os.path.join(profile_dir, name)
                if os.path.isdir(sub) and _is_user_data_dir(sub):
                    return sub
        except OSError:
            pass
        return profile_dir

    def capture_as_persona(self, url, persona, *, profile_dir=None, channel=None,
                           record_har=False, record_video=False, wait_time=5,
                           headless=None, persona_id=None, extra_options=None):
        """Capture a page *as a persona* with full attribute emulation and optional
        HAR/video, into the archives/<url_hash>/<timestamp>/ memento layout.

        Modes:
          * synthesized  -- a fresh context built from the persona's attributes.
          * real profile -- if ``profile_dir`` is given, a *persistent* context from
            a real Chrome user-data dir, so the persona's accumulated cookies/history/
            ad-personalization drive the session (the demo "money shot").

        Returns a result dict (screenshot_path, har_path, video_path, html_path,
        title, final_url, http_status, persona_snapshot, memento_location). This is
        pure capture -- persisting it as a journey waypoint is Phase C.
        """
        self._ensure_playwright()
        headless = BROWSER_HEADLESS if headless is None else headless
        channel = channel or channel_for_persona(persona)
        if persona_id is None:
            persona_id = persona.get("id")

        # Pre-compute the memento dir so HAR/video (fixed at context creation) land in it.
        url_dir, memento_dir, timestamp = self._memento_paths(url)

        har_path = os.path.join(memento_dir, "traffic.har") if record_har else None
        video_dir = memento_dir if record_video else None

        options = self._build_context_options(
            persona=persona, har_path=har_path, video_dir=video_dir,
            extra_options=extra_options,
        )

        browser = None
        if profile_dir:
            user_data_dir = self._resolve_user_data_dir(profile_dir)
            logger.info("Capturing %s as %r via real profile %s (channel=%s)",
                        url, persona.get("name"), user_data_dir, channel)
            context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir, headless=headless, channel=channel, **options,
            )
        else:
            logger.info("Capturing %s as %r via synthesized context (channel=%s)",
                        url, persona.get("name"), channel)
            browser = self._playwright.chromium.launch(headless=headless, channel=channel)
            context = browser.new_context(**options)

        video_path = None
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(wait_time * 1000)

            final_url = page.url

            if record_video and page.video:
                try:
                    video_path = page.video.path()  # finalized on context.close()
                except Exception as e:
                    logger.error(f"Error resolving video path: {e}")

            persona_snapshot = {
                "id": persona_id,
                "name": persona.get("name"),
                "demographic": persona.get("demographic"),
                "contextual": persona.get("contextual"),
                "mode": "real_profile" if profile_dir else "synthesized",
                "channel": channel,
                "context_options": {k: v for k, v in options.items()
                                    if k not in ("record_har_path", "record_video_dir")},
            }

            # Reuse the shared persist pipeline (no DB row for ad-hoc captures).
            result = self._write_memento(
                page, url, persona_id=persona_id,
                memento_dir=memento_dir, timestamp=timestamp, save_to_db=False,
                extra_metadata={
                    "final_url": final_url,
                    "persona_snapshot": persona_snapshot,
                    "artifacts": {
                        "screenshot": "screenshot.png",
                        "html": "content.html",
                        "har": "traffic.har" if har_path else None,
                        "video": os.path.basename(video_path) if video_path else None,
                    },
                },
            )
            result.update({
                "final_url": final_url,
                "har_path": har_path,
                "video_path": video_path,
                "persona_snapshot": persona_snapshot,
            })
        finally:
            context.close()  # flushes HAR + finalizes video
            if browser is not None:
                browser.close()

        logger.info("Captured %s as %r -> %s", url, persona.get("name"), memento_dir)
        return result

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
