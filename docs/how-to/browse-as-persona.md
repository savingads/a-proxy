# Browse as Persona

A-Proxy allows you to browse the web from a persona's perspective, with browser configuration reflecting the persona's attributes.

## Overview

When browsing as a persona, the system configures:

- Geographic location (via VPN if enabled)
- Browser language settings
- User-agent string
- Viewport/screen size
- Other contextual parameters

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

The following are configured based on persona attributes:

| Persona Attribute | Browser Setting |
|-------------------|-----------------|
| Language | Accept-Language header |
| Device Type | User-Agent string |
| Browser Type | User-Agent string |
| Screen Size | Viewport dimensions |

### VPN Integration

If VPN is configured and the persona has geographic attributes:

| Persona Attribute | VPN Setting |
|-------------------|-------------|
| Country | VPN exit node region |
| City | Closest available server |

See [VPN Integration](vpn-integration.md) for setup details.

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
- Cleared when session ends

### Cookie Limitations

- No persistent cookie profiles per persona
- Each session starts fresh
- Cookie-based personalization requires building history within a session

## Browser Fingerprinting

Some websites use browser fingerprinting beyond cookies.

### What A-Proxy Configures

A-Proxy sets these basic browser attributes:

- User-Agent string (based on device/browser type)
- Accept-Language header
- Viewport dimensions

### Not Configured

A-Proxy does not spoof these fingerprint elements:

- Canvas fingerprinting
- WebGL fingerprinting
- Audio fingerprinting
- Timezone
- Installed fonts
- Hardware concurrency

!!! warning "Fingerprint Limitations"
    A-Proxy provides basic browser configuration, not full fingerprint spoofing. Websites using advanced fingerprinting may still identify the browser environment.

## Best Practices

### Planning Sessions

Before browsing:

1. Review the persona's attributes
2. Ensure VPN is configured if needed
3. Determine target websites
4. Create or select an appropriate journey

### Documenting Observations

During browsing:

1. Note differences from expected content
2. Capture screenshots of personalized elements
3. Record any error states or blocking

### Session Hygiene

For clean captures:

1. Start with fresh session (no cookies)
2. Or load persona-specific cookie profile
3. Avoid mixing persona sessions

## Troubleshooting

### Pages Not Loading

1. Check internet connectivity
2. Verify VPN connection (if using)
3. Try without VPN to isolate issue

### Wrong Location Detected

1. Confirm VPN is connected
2. Check VPN exit node matches persona location
3. Some sites use multiple detection methods

### Missing Personalization

1. Personalization may require browsing history
2. Build session history through repeated visits
3. Some personalization requires login

## Related Guides

- [VPN Integration](vpn-integration.md) - Geographic spoofing setup
- [Archive Web Pages](archive-pages.md) - Saving captured content
- [Manage Journeys](manage-journeys.md) - Organizing browsing sessions
