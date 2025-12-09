# Archive Web Pages

This guide documents the process of capturing and storing web pages within the A-Proxy system.

## Archive Process

Web archiving in A-Proxy captures page content along with the persona context used during retrieval. This preserves both the content and the conditions under which it was served.

## Initiating an Archive

### During Browsing

1. Navigate to a page while browsing as a persona
2. Click the **Archive** button in the interface
3. The system captures the current page state

### Bulk Archiving

For multiple pages:

1. Create a list of target URLs
2. Select the persona context
3. Initiate batch capture
4. Monitor progress

## Captured Data

Each archive record contains:

| Component | Description |
|-----------|-------------|
| HTML Content | Full page source |
| Screenshot | Visual capture of rendered page |
| HTTP Headers | Server response headers |
| Cookies | Session cookies at capture time |
| Timestamp | Exact capture datetime |
| Persona Context | Attributes used during retrieval |

### Metadata Stored

```json
{
    "url": "https://example.com/page",
    "capture_time": "2024-12-09T10:30:00Z",
    "persona_id": 1,
    "browser_context": {
        "user_agent": "...",
        "accept_language": "en-US",
        "viewport": "1920x1080"
    },
    "network_context": {
        "exit_ip_region": "US-NY",
        "connection_type": "wifi"
    }
}
```

## Storage Location

Archives are stored in the `archives/` directory:

```
archives/
├── 2024/
│   └── 12/
│       └── 09/
│           ├── archive_001/
│           │   ├── page.html
│           │   ├── screenshot.png
│           │   └── metadata.json
│           └── archive_002/
│               └── ...
```

## Viewing Archives

### Archive List

1. Navigate to **Archives**
2. Browse archived pages by date or persona
3. Click to view individual archives

### Archive Detail

Each archive view displays:

- Rendered page preview
- Original HTML source
- Capture metadata
- Associated persona information

## Archive Formats

### HTML Archive

The captured HTML includes:

- Document structure
- Inline styles
- Script references (not executed on replay)

### Screenshot Archive

PNG screenshot capturing:

- Visible viewport at capture time
- Rendered state including dynamic content

### Full Page Archive (Optional)

Extended capture including:

- All referenced resources (CSS, images, scripts)
- Structured as WARC or similar format

## Comparison Capabilities

Compare archives across:

### Temporal Comparison

Same URL archived at different times:

1. Select two archive dates
2. View side-by-side
3. Identify content changes

### Persona Comparison

Same URL with different personas:

1. Select two personas
2. Compare captured content
3. Document personalization differences

## Limitations

### Dynamic Content

- JavaScript-rendered content may vary
- Infinite scroll content is limited to initial load
- Authenticated content requires session handling

### External Resources

- Third-party resources may be blocked
- CDN content may differ by region
- Ad content is inherently variable

## Research Considerations

### Reproducibility

For reproducible research:

1. Document exact persona configuration
2. Record VPN/network settings
3. Note capture timing
4. Version the capture methodology

### Citation

When citing archived content:

```
[Page Title]. Archived [DATE] via A-Proxy using persona
[PERSONA_NAME] with geographic context [LOCATION].
```

## Related Guides

- [Browse as Persona](browse-as-persona.md) - Navigating before archiving
- [Manage Journeys](manage-journeys.md) - Organizing archived captures
- [Archival Goals](../concepts/archival-goals.md) - Research context for archiving
