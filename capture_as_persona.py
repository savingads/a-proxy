#!/usr/bin/env python3
"""
Capture a page as a persona using Playwright.

Thin CLI over ``BrowserManager.capture_as_persona`` -- the *same* engine path the
web app uses, so the CLI and the app configure the browser identically (one
persona -> context mapping, in ``utils/persona_browser.py``).

Builds a browser context from the persona's full attribute set -- or, with
``--profile-dir``, loads a real Chrome profile so the persona's accumulated state
(cookies, history, ad-personalization) drives the session -- then navigates and
captures a screenshot, and optionally a HAR (network traffic, for cross-persona
ad diffs) and a video. Artifacts land in archives/<url_hash>/<timestamp>/.

Examples:
    # Synthesized context for the first available persona (or pass --persona-name)
    python3 capture_as_persona.py https://www.cnn.com

    # Real Alex Chrome profile (the demo "money shot"), capturing traffic + video.
    # Point --profile-dir at the unzipped Alex_Johnson_Browser_Profile (the loader
    # descends into the inner user-data dir automatically).
    python3 capture_as_persona.py https://www.cnn.com \
        --profile-dir ./Alex_Johnson_Browser_Profile --channel chrome --har --video

Note on real-profile mode:
    ``Alex_Johnson_Browser_Profile.zip`` (~510 MB) is NOT included in the repo --
    it is gitignored, so a fresh clone does not have it. To use ``--profile-dir``
    you must obtain that zip out-of-band and unzip it next to this script (giving
    ``./Alex_Johnson_Browser_Profile/``), or point ``--profile-dir`` at any other
    real Chrome user-data dir. A real profile holds live cookies/login state, so
    treat it as sensitive -- do not commit or share it. Without ``--profile-dir``
    the tool runs in synthesized mode and needs no external profile.
"""
import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _load_persona(persona_id, persona_name):
    """Fetch a persona by id, by name, or -- if neither is given -- the first
    available persona (so the tool isn't bound to any specific seed persona)."""
    from database.repositories.persona import PersonaRepository

    repo = PersonaRepository()
    if persona_id is not None:
        persona = repo.get(persona_id)
        if not persona:
            raise SystemExit(f"No persona with id {persona_id}")
        return persona

    personas = repo.get_all(per_page=500).get("personas", [])
    if not personas:
        raise SystemExit("No personas found; create one first "
                         "(e.g. python3 create_sample_personas_simple.py).")

    if persona_name:
        for candidate in personas:
            if candidate.get("name", "").strip().lower() == persona_name.strip().lower():
                # get_all rows can be summaries; re-fetch the full persona by id.
                return repo.get(candidate["id"]) or candidate
        raise SystemExit(f"No persona named {persona_name!r}")

    # Neither id nor name given: fall back to the first available persona.
    first = personas[0]
    logger.info("No persona specified; using %r (id=%s).", first.get("name"), first.get("id"))
    return repo.get(first["id"]) or first


def main():
    parser = argparse.ArgumentParser(description="Capture a page as a persona (Playwright).")
    parser.add_argument("url", help="URL to visit")
    parser.add_argument("--persona-id", type=int, help="Persona ID (overrides --persona-name)")
    parser.add_argument("--persona-name", help="Persona name (default: first available persona)")
    parser.add_argument("--profile-dir", help="Real Chrome user-data dir for real-profile mode "
                                              "(e.g. an unzipped *_Browser_Profile; not shipped with the repo)")
    parser.add_argument("--channel", help="Browser channel, e.g. 'chrome' (for real Google Chrome profiles)")
    parser.add_argument("--har", action="store_true", help="Record network traffic to traffic.har")
    parser.add_argument("--video", action="store_true", help="Record a session video")
    parser.add_argument("--wait", type=int, default=5, help="Settle time after load (seconds)")
    parser.add_argument("--headed", action="store_true", help="Run with a visible browser window")
    args = parser.parse_args()

    persona = _load_persona(args.persona_id, args.persona_name)
    logger.info("Capturing %s as persona %r", args.url, persona.get("name"))

    from utils.browser import BrowserManager

    manager = BrowserManager.get_instance()
    try:
        result = manager.capture_as_persona(
            args.url,
            persona,
            profile_dir=args.profile_dir,
            channel=args.channel,
            record_har=args.har,
            record_video=args.video,
            wait_time=args.wait,
            headless=not args.headed,
        )
    finally:
        manager.shutdown()

    logger.info("Title: %s", result.get("title"))
    logger.info("Memento: %s", result.get("memento_location"))
    logger.info("Screenshot: %s", result.get("screenshot_path"))
    if result.get("har_path"):
        logger.info("HAR: %s", result["har_path"])
    if result.get("video_path"):
        logger.info("Video: %s", result["video_path"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - surface a clean CLI error
        logger.error("Capture failed: %s", exc, exc_info=True)
        sys.exit(1)
