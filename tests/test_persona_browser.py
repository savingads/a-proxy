"""
Unit tests for persona -> Playwright context option mapping.

These cover the pure attribute-translation logic in ``build_context_options``
and helpers; they do not launch a browser, so they run without Playwright
installed. ``utils.browser.BrowserManager`` consumes this same mapping, so these
tests exercise the live engine's persona handling.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.persona_browser import (  # noqa: E402
    build_context_options,
    channel_for_persona,
    _extract_latlon,
    _infer_timezone,
    _parse_screen_size,
)

# Mirrors Alex Johnson from create_sample_personas_simple.py (San Francisco).
ALEX = {
    "name": "Alex Johnson",
    "demographic": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "language": "en-US",
        "country": "US",
        "city": "San Francisco",
    },
    "contextual": {
        "device_type": "desktop",
        "browser_type": "chrome",
        "screen_size": "1920x1080",
    },
}


def test_alex_context_options():
    opts = build_context_options(ALEX)
    assert opts["locale"] == "en-US"
    assert opts["geolocation"] == {"latitude": 37.7749, "longitude": -122.4194}
    assert opts["permissions"] == ["geolocation"]
    assert opts["timezone_id"] == "America/Los_Angeles"  # city beats country
    assert opts["viewport"] == {"width": 1920, "height": 1080}
    # Desktop persona is not flagged mobile.
    assert "is_mobile" not in opts


def test_alex_browser_channel():
    # browser_type chrome -> real Chrome channel (a launch arg, not a context opt).
    assert channel_for_persona(ALEX) == "chrome"
    assert "channel" not in build_context_options(ALEX)


def test_mobile_persona_flags_touch():
    persona = {
        "demographic": {"language": "ja-JP", "country": "JP", "city": "Tokyo"},
        "contextual": {"device_type": "mobile", "browser_type": "safari", "screen_size": "390x844"},
    }
    opts = build_context_options(persona)
    assert opts["is_mobile"] is True
    assert opts["has_touch"] is True
    assert opts["timezone_id"] == "Asia/Tokyo"
    assert opts["viewport"] == {"width": 390, "height": 844}
    # Safari isn't a Chromium channel -> fall back to bundled Chromium.
    assert channel_for_persona(persona) is None


def test_geolocation_from_string_fallback():
    lat, lon = _extract_latlon({"geolocation": "51.5074,-0.1278"})
    assert lat == 51.5074
    assert lon == -0.1278


def test_country_timezone_when_city_unknown():
    assert _infer_timezone({"country": "GB", "city": "Nowheresville"}) == "Europe/London"


def test_parse_screen_size_variants():
    assert _parse_screen_size("1920x1080") == {"width": 1920, "height": 1080}
    assert _parse_screen_size("1920X1080") == {"width": 1920, "height": 1080}
    assert _parse_screen_size("1920×1080") == {"width": 1920, "height": 1080}
    assert _parse_screen_size("garbage") is None
    assert _parse_screen_size(None) is None


def test_empty_persona_is_safe():
    assert build_context_options({}) == {}
    assert channel_for_persona({}) is None


if __name__ == "__main__":
    # Allow standalone execution without pytest.
    import traceback

    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    sys.exit(1 if failures else 0)
