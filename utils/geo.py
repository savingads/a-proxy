"""
Geographic inference shared across the app (single source of truth).

Used by BOTH the web routes (``_get_persona_browser_settings``) and the
persona -> browser-context mapping (``utils.persona_browser``), so a persona
resolves to the SAME timezone regardless of code path. Previously these two
paths used separate tables and disagreed (e.g. a San-Francisco/US persona got
``America/New_York`` via the routes but ``America/Los_Angeles`` via the engine).

Country -> timezone falls back to the single ``REGION_LANGUAGE_MAP`` table in
``config`` (imported lazily so this module stays cheap to import and free of a
hard config dependency for unit tests).
"""
from typing import Any, Dict, Optional

# City-level timezones (finer than the country defaults). City wins over country.
# Intentionally small; extend as personas need it.
CITY_TIMEZONES = {
    "san francisco": "America/Los_Angeles",
    "los angeles": "America/Los_Angeles",
    "seattle": "America/Los_Angeles",
    "new york": "America/New_York",
    "chicago": "America/Chicago",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "tokyo": "Asia/Tokyo",
}


def infer_timezone(country: Optional[str] = None, city: Optional[str] = None) -> Optional[str]:
    """Infer an IANA timezone id, city first (finer) then country.

    ``country`` is matched against ``REGION_LANGUAGE_MAP`` (2-letter codes), the
    single country->timezone source. Returns None when neither resolves.
    """
    if city:
        tz = CITY_TIMEZONES.get(city.strip().lower())
        if tz:
            return tz
    if country:
        from config import REGION_LANGUAGE_MAP  # lazy: keep import-time deps minimal
        region = REGION_LANGUAGE_MAP.get(country.strip().upper())
        if region:
            return region.get("timezone")
    return None


def persona_geolocation(demographic: Dict[str, Any]) -> Optional[str]:
    """Return a persona's geolocation as a ``'lat,lng'`` string, or None."""
    lat = demographic.get("latitude")
    lng = demographic.get("longitude")
    if lat and lng:
        return f"{lat},{lng}"
    return None
