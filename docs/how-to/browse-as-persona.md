# Browse as Persona

A-Proxy supports two browsing modes: **headful** (interactive) and **headless** (automated). Both use Playwright to configure the browser with persona-specific locale, geolocation, timezone, and proxy settings.

## Headful Browsing (Interactive)

Headful browsing launches a visible Chromium window configured with the persona's attributes. You browse naturally in the real browser while A-Proxy tracks your navigation and provides controls to archive pages and save waypoints.

### Starting a Session

#### From the Interact As page

1. Navigate to **Interact As**
2. Click **Browse** on a persona card
3. Optionally enter a starting URL (defaults to google.com)
4. Click **Start Browsing**
5. A Chromium window opens with the persona's settings applied

#### From a Journey

1. Navigate to **Journeys**
2. Open a journey that has a linked persona
3. Click **Browse** — this opens the same launch page with the journey pre-selected
4. Waypoints are automatically saved to that journey

### What the Browser Emulates

| Persona Attribute | Browser Setting |
|-------------------|-----------------|
| Language (`demographic.language`) | Locale — Accept-Language header and UI language |
| Latitude/Longitude | Geolocation — `navigator.geolocation` API |
| Country | Timezone — via `REGION_LANGUAGE_MAP` lookup |
| Proxy (session or env) | Per-context traffic routing |

These are applied natively by Playwright — no JavaScript injection needed.

### The Control Page

While browsing, the `/direct-browse/<persona_id>` page shows:

- **Session status** — active/inactive indicator, current URL
- **Navigation history** — every page you visit is tracked automatically
- **Actions:**
    - **Archive Page** — saves HTML, screenshot, and metadata from the live browser page to the archive
    - **Screenshot** — captures a full-page screenshot
    - **Save Waypoint** — saves the current page as a waypoint (with optional journey assignment)
    - **Stop** — closes the browser window and ends the session

The control page polls the session status every 3 seconds, so your navigation history updates in near real-time.

### Session Behavior

- **One session at a time** — starting a new session closes any existing one
- **Isolated contexts** — each session starts fresh with no cookies or history from previous sessions
- **Persistent until stopped** — the browser stays open until you click Stop or the server shuts down

## Headless Browsing (Automated)

Headless browsing runs Playwright in the background without a visible window. This is used for programmatic page visits, archiving, and demo scripts.

### Visit a Page

```
POST /visit-page
```

Visits a URL with persona settings and optionally takes a screenshot. The browser context is created, the page is loaded, and the context is immediately closed.

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| url | string | Target URL |
| language | string | Locale (e.g., "en-US") |
| geolocation | string | "lat,lng" format |
| take_screenshot | string | "true" to capture screenshot |

### Archive a Page

```
POST /archive_page
```

Archives a URL by saving HTML, a full-page screenshot, and metadata to the filesystem and database. Used by the Archive button on persona detail pages.

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| url | string | Target URL |
| language | string | Locale |
| geolocation | string | "lat,lng" format |
| persona_id | int | Persona used for the archive |

### Demo Scripts

The `demo/` directory contains Playwright scripts that automate the app's UI for demonstrations:

```bash
python demo/demo_script.py          # Run the feature demo
python demo/create_pdf_report.py    # Generate PDF from screenshots
```

## Proxy Integration

If a proxy is configured (via `.env` or the session), all browser traffic routes through it:

| Persona Attribute | Proxy Effect |
|-------------------|--------------|
| Country | Proxy exit node determines GeoIP |
| City | Closest available proxy server |

Both headful and headless modes support per-context proxies. See [Proxy & Geo-IP](proxy-setup.md) for configuration.

## Session API Endpoints

These JSON endpoints power the headful browsing control page:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start-session` | POST | Launch a headful session for a persona |
| `/session-status` | GET | Get current URL, history, and session state |
| `/capture-page` | POST | Screenshot the active page |
| `/archive-page-from-session` | POST | Archive the active page (HTML + screenshot + metadata) |
| `/stop-session` | POST | Close the browser and end the session |

## Troubleshooting

### Browser window doesn't open

- Ensure `BROWSER_HEADLESS` is not set to `True` in `.env` (headful sessions always launch in headful mode regardless of this setting)
- On Docker/headless servers, headful browsing requires a display (X11 or Wayland)

### Wrong location detected by websites

1. Check proxy is configured — GeoIP depends on the proxy exit node, not just geolocation emulation
2. Geolocation emulation only affects the JavaScript API (`navigator.geolocation`), not the IP address
3. Some sites use multiple detection methods beyond GeoIP

### Pages not loading

1. Check internet connectivity
2. Verify proxy connection if using one (`/network-status` shows current IP info)
3. Try without proxy to isolate the issue

## Related Guides

- [Proxy & Geo-IP](proxy-setup.md) - Geographic shifting setup
- [Archive Web Pages](archive-pages.md) - Saving captured content
- [Manage Journeys](manage-journeys.md) - Organizing browsing sessions
