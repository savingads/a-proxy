# Browse as Persona

A-Proxy allows you to browse the web from a persona's perspective, with browser configuration reflecting the persona's attributes.

## Overview

When browsing as a persona, the system configures via Playwright:

- Geographic location (via proxy if configured, plus geolocation emulation)
- Browser language and locale
- Timezone
- Viewport/screen size

This enables capturing web content as it would appear to that specific user type.

## Starting a Browsing Session

### Method 1: Interact As Page

1. Navigate to **Interact As**
2. Select a persona from the dropdown
3. Choose **Browse** mode
4. Enter a URL or start exploring

### Method 2: Journey Browse

1. Navigate to **Journeys**
2. Open an existing journey
3. Click **Browse** to continue the journey
4. The persona is automatically selected

### Method 3: Persona Quick Action

1. Navigate to **Personas**
2. Click on a persona
3. Click **Browse As** button
4. Enter a starting URL

## Browser Configuration

### Automatic Settings

Playwright configures the following based on persona attributes:

| Persona Attribute | Browser Setting |
|-------------------|-----------------|
| Language | Locale (Accept-Language + UI language) |
| Latitude/Longitude | Geolocation emulation |
| Country/Region | Timezone emulation |
| Device Type | Viewport dimensions |

### Proxy Integration

If a proxy is configured and the persona has geographic attributes:

| Persona Attribute | Proxy Setting |
|-------------------|---------------|
| Country | Proxy exit node region |
| City | Closest available proxy server |

See [Proxy & Geo-IP](proxy-setup.md) for setup details.

### What Playwright Emulates Natively

Playwright provides native emulation for:

- **Geolocation** -- precise lat/lng coordinates reported to the browser
- **Locale** -- language and regional formatting
- **Timezone** -- `Intl.DateTimeFormat` and related APIs
- **Proxy** -- per-context traffic routing

No JavaScript injection or CDP commands needed.

## Browsing Interface

### Navigation Bar

The browsing interface includes:

- **URL Bar**: Enter addresses directly
- **Back/Forward**: Navigate history
- **Refresh**: Reload current page
- **Archive**: Save the current page

### Persona Context Display

A sidebar or header shows:

- Current persona name
- Active geographic settings
- Browser configuration summary

### Page Viewer

The main area displays web content with:

- Full page rendering
- JavaScript execution
- Cookie handling based on session

## Recording Waypoints

Each page visit is automatically recorded as a waypoint:

1. Page URL is logged
2. Page title is captured
3. Timestamp is recorded
4. Sequence number is assigned

### Adding Notes

While browsing:

1. Click the **Notes** button
2. Add observations about the current page
3. Notes are attached to the waypoint

### Taking Screenshots

Manually capture the current view:

1. Click the **Screenshot** button
2. The image is saved to the waypoint
3. Useful for capturing specific states

## Managing Cookies

Cookies affect personalization and tracking:

### Session Cookies

- Created during browsing
- Persist within the browsing session
- Cleared when session ends (Playwright contexts are isolated)

### Cookie Limitations

- No persistent cookie profiles per persona
- Each session starts fresh
- Cookie-based personalization requires building history within a session

## Best Practices

### Planning Sessions

Before browsing:

1. Review the persona's attributes
2. Ensure proxy is configured if needed
3. Determine target websites
4. Create or select an appropriate journey

### Documenting Observations

During browsing:

1. Note differences from expected content
2. Capture screenshots of personalized elements
3. Record any error states or blocking

### Session Hygiene

For clean captures:

1. Start with fresh session (each Playwright context is isolated)
2. Avoid mixing persona sessions
3. Use different proxies for different geographic personas

## Troubleshooting

### Pages Not Loading

1. Check internet connectivity
2. Verify proxy connection (if using)
3. Try without proxy to isolate issue

### Wrong Location Detected

1. Confirm proxy is active (check dashboard IP info)
2. Check proxy exit node matches persona location
3. Some sites use multiple detection methods beyond GeoIP

### Missing Personalization

1. Personalization may require browsing history
2. Build session history through repeated visits
3. Some personalization requires login

## Related Guides

- [Proxy & Geo-IP](proxy-setup.md) - Geographic shifting setup
- [Archive Web Pages](archive-pages.md) - Saving captured content
- [Manage Journeys](manage-journeys.md) - Organizing browsing sessions
