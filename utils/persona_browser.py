"""
Persona -> Playwright browser-context mapping (pure, no Playwright import).

This is the single source of truth for translating a persona's 4-dimensional
attributes into Playwright browser-context options. It is consumed by
``utils.browser.BrowserManager`` (the live engine) and by the
``capture_as_persona`` CLI, so synthesized and real-profile sessions configure
the browser identically.

Kept import-light on purpose: it has no Playwright dependency, so the mapping
logic can be unit-tested without a browser installed.

Persona shape (as returned by ``utils.persona_client`` / ``PersonaRepository``):

    {
      "demographic": {"language", "latitude", "longitude", "geolocation",
                      "country", "city"},
      "contextual":  {"device_type", "browser_type", "screen_size"},
      ...
    }
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from utils.geo import infer_timezone

logger = logging.getLogger(__name__)


# Playwright launch channels for real browser builds. None => bundled Chromium.
# Safari/WebKit isn't a Chromium channel, so it falls back to Chromium emulation.
_BROWSER_CHANNELS = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "msedge": "msedge",
}


def _extract_latlon(demographic: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """Return (lat, lon), preferring explicit float columns, then a 'lat,lon' string."""
    lat = demographic.get("latitude")
    lon = demographic.get("longitude")
    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon)
        except (TypeError, ValueError):
            pass

    geo = demographic.get("geolocation")
    if isinstance(geo, str) and "," in geo:
        try:
            lat_str, lon_str = geo.split(",", 1)
            return float(lat_str.strip()), float(lon_str.strip())
        except (TypeError, ValueError):
            pass

    return None, None


def _parse_screen_size(screen_size: Optional[str]) -> Optional[Dict[str, int]]:
    """Parse '1920x1080' (or '1920X1080' / '1920×1080') into a viewport dict."""
    if not screen_size or not isinstance(screen_size, str):
        return None
    normalized = screen_size.lower().replace("×", "x").strip()
    if "x" not in normalized:
        return None
    width_str, height_str = normalized.split("x", 1)
    try:
        return {"width": int(width_str.strip()), "height": int(height_str.strip())}
    except (TypeError, ValueError):
        return None


def channel_for_persona(persona: Dict[str, Any]) -> Optional[str]:
    """
    Map ``contextual.browser_type`` to a Playwright launch channel
    ('chrome'/'msedge'), or None to use bundled Chromium. This is a *launch*
    argument, not a context option, so it lives outside build_context_options.
    """
    contextual = persona.get("contextual") or {}
    browser_type = (contextual.get("browser_type") or "").strip().lower()
    return _BROWSER_CHANNELS.get(browser_type)


def build_context_options(persona: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build Playwright *context* options from a persona dict. Only keys we can
    populate are included, so the result can be splatted into ``new_context`` /
    ``launch_persistent_context``.

    Maps:
      demographic.language               -> locale
      demographic.lat/lon (or geo string)-> geolocation + permissions
      demographic.city/country           -> timezone_id (city beats country)
      contextual.screen_size             -> viewport
      contextual.device_type             -> is_mobile + has_touch (mobile/tablet)
    """
    demographic = persona.get("demographic") or {}
    contextual = persona.get("contextual") or {}
    options: Dict[str, Any] = {}

    language = demographic.get("language")
    if language:
        options["locale"] = language

    lat, lon = _extract_latlon(demographic)
    if lat is not None and lon is not None:
        options["geolocation"] = {"latitude": lat, "longitude": lon}
        options["permissions"] = ["geolocation"]

    timezone_id = infer_timezone(demographic.get("country"), demographic.get("city"))
    if timezone_id:
        options["timezone_id"] = timezone_id

    viewport = _parse_screen_size(contextual.get("screen_size"))
    if viewport:
        options["viewport"] = viewport

    device_type = (contextual.get("device_type") or "").strip().lower()
    if device_type in ("mobile", "tablet"):
        options["is_mobile"] = True
        options["has_touch"] = True

    return options
