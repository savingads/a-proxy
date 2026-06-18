# Archive Web Pages

This guide documents the process of capturing and storing web pages within the A-Proxy system.

## Archive Process

Web archiving in A-Proxy captures page content along with the persona context used during retrieval. This preserves both the content and the conditions under which it was served.

## How Capture Works

A-Proxy captures pages with a real browser (Playwright driving Chromium), not a plain HTTP fetch. This matters: what gets saved is the **rendered DOM after JavaScript runs**, so dynamic content — ads, lazy-loaded images, trackers — is captured as the persona's browser would actually render it.

Each capture has three steps:

1. **Configure a browser context** from the persona's attributes — locale, geolocation, timezone, viewport, mobile/touch flags, and an optional proxy — before the page opens.
2. **Navigate and settle** — load the URL (`wait_until="domcontentloaded"`), then pause ~5 seconds so JavaScript-rendered content finishes loading.
3. **Write the artifacts** — the serialized rendered DOM (`content.html`), a full-page screenshot (`screenshot.png`), and `metadata.json`. Persona captures run via `capture_as_persona.py` also record `traffic.har` (every network request) and `video.webm`.

!!! note "HTTP headers come from a separate request"
    The HTML and screenshot come from the persona's browser, but the HTTP status and response headers stored in `metadata.json` come from a separate `requests.get(url)` that does **not** use the persona's browser context or proxy. Those header values reflect a generic fetch, not what the persona's browser received — keep this in mind if you analyze response headers per persona.

## Initiating an Archive

### From the Browsing Interface

1. Navigate to a page while browsing as a persona
2. Click the **Archive** button in the interface
3. The system captures the current page state

### Direct Archive

Use the archive endpoint with persona context:

1. Provide the target URL
2. Select the persona context (language, geolocation)
3. Submit the archive request

## Captured Data

Each archive record contains:

| Component | Description |
|-----------|-------------|
| HTML Content | Full page source |
| Screenshot | Visual capture of rendered page |
| Timestamp | Exact capture datetime |
| Persona ID | Associated persona for context |

### Storage Structure

Archives are stored in the `archives/` directory, organized by URL hash and timestamp:

```
archives/
├── [url_hash]/
│   └── [timestamp]/
│       ├── content.html
│       ├── screenshot.png
│       ├── metadata.json
│       ├── traffic.har      # persona captures run with --har
│       └── video.webm       # persona captures run with --video
```

Persona captures made with `capture_as_persona.py` add `traffic.har` (network
traffic) and/or `video.webm` to the same memento directory, plus a
`persona_snapshot` block inside `metadata.json`. Standard archives contain only
the HTML, screenshot, and metadata.

## Viewing Archives

### Archive List

1. Navigate to **Archives**
2. Browse archived pages
3. Click to view individual archives

### Archive Detail

Each archive view displays:

- HTML content viewer
- Screenshot preview
- Capture metadata
- Option to submit to Internet Archive

### Memento Viewer

View the captured HTML content rendered in the browser.

## Internet Archive Integration

A-Proxy can submit captures to the Internet Archive:

1. View an archive/memento
2. Click **Submit to Internet Archive**
3. The URL is submitted to the Wayback Machine

Rate limiting is enforced (configurable in **Settings**).

## Archive Formats

### HTML Archive

The captured HTML includes:

- Document structure
- Inline styles
- Script references (not executed on replay)

### Screenshot Archive

PNG screenshot capturing:

- The entire scrollable page (full-page capture, not just the visible viewport)
- Rendered state including dynamic content

## Limitations

### Dynamic Content

- JavaScript-rendered content may vary between captures
- Infinite scroll content is limited to initial load
- Authenticated content requires session handling

### External Resources

- Third-party resources may be blocked or unavailable
- CDN content may differ by region
- Ad content is inherently variable

### Features Not Yet Implemented

The following features are not currently available:

- **Bulk archiving**: Archives must be created one at a time
- **Comparison tools**: No built-in side-by-side comparison
- **WARC format**: Archives are stored as HTML/screenshot, not WARC

To compare archives, manually open multiple archive views or use external diff tools.

## Research Considerations

### Reproducibility

For reproducible research:

1. Document exact persona configuration
2. Record proxy/network settings if used
3. Note capture timing
4. Version the capture methodology

### Citation

When citing archived content:

```
[Page Title]. Archived [DATE] via A-Proxy using persona
[PERSONA_NAME] with geographic context [LOCATION].
```

## Settings

Archive settings are available at **Settings**:

- Internet Archive integration enable/disable
- Rate limit for Internet Archive submissions
- View daily submission count

## Related Guides

- [Browse as Persona](browse-as-persona.md) - Navigating before archiving
- [Manage Journeys](manage-journeys.md) - Organizing archived captures
- [Archival Goals](../concepts/archival-goals.md) - Research context for archiving
