# Persona Model

A-Proxy uses a 4-dimensional persona model derived from advertising and user profiling research. Each dimension captures different aspects of user identity that influence web personalization.

## The Four Dimensions

```
                    Persona
                       |
    +--------+---------+---------+--------+
    |        |         |         |        |
Demographic  Psychographic  Behavioral  Contextual
```

## 1. Demographic Data

External, observable characteristics that define who the user is.

| Field | Type | Description |
|-------|------|-------------|
| `latitude` | float | Geographic latitude coordinate |
| `longitude` | float | Geographic longitude coordinate |
| `country` | string | Country of residence |
| `city` | string | City of residence |
| `region` | string | State/province/region |
| `language` | string | Primary language (e.g., "en-US") |
| `age` | integer | Age in years |
| `gender` | string | Gender identity |
| `education` | string | Education level |
| `income` | string | Income bracket |
| `occupation` | string | Job title or profession |

**Impact on Web Experience**: Location affects local content (news, weather, pricing), language determines interface localization, and demographics influence targeted advertising.

## 2. Psychographic Data

Internal psychological attributes that define what the user values and believes.

| Field | Type | Description |
|-------|------|-------------|
| `interests` | list | Personal interests and hobbies |
| `personal_values` | list | Core values the persona prioritizes |
| `attitudes` | list | General outlook and viewpoints |
| `lifestyle` | string | Overall lifestyle description |
| `personality` | string | Personality traits and characteristics |
| `opinions` | list | Specific viewpoints on relevant topics |

**Impact on Web Experience**: Interests drive content recommendations, values influence brand alignment, and personality affects communication style preferences.

## 3. Behavioral Data

Observable online actions and usage patterns.

| Field | Type | Description |
|-------|------|-------------|
| `browsing_habits` | list | Types of websites frequently visited |
| `purchase_history` | list | Types of products/services purchased |
| `brand_interactions` | list | Brands frequently engaged with |
| `device_usage` | dict | How different devices are used |
| `social_media_activity` | dict | Engagement with social platforms |
| `content_consumption` | dict | Media consumption patterns |

**Impact on Web Experience**: Browsing history shapes recommendations, purchase patterns trigger retargeting, and device usage affects UI optimization.

## 4. Contextual Data

Situational and environmental factors at the time of interaction.

| Field | Type | Options/Description |
|-------|------|---------------------|
| `time_of_day` | string | morning, afternoon, evening, night, all day |
| `day_of_week` | string | weekday, weekend, all week |
| `season` | string | spring, summer, fall, winter |
| `weather` | string | Current weather conditions |
| `device_type` | string | desktop, laptop, tablet, mobile |
| `browser_type` | string | chrome, firefox, safari, edge |
| `screen_size` | string | Display resolution (e.g., "1920x1080") |
| `connection_type` | string | wifi, ethernet, 4g, 5g, 3g |

**Impact on Web Experience**: Device type affects layout, time context influences content freshness, and connection speed determines media quality.

## Persona Development

Personas can be developed through two methods:

### 1. Manual Creation

Archivists directly specify attribute values when creating or editing personas through the web interface.

### 2. Chat-Based Development

Through conversations with Claude AI, personas can be developed organically:

```
Archivist: "You have a job as a chef at a restaurant in Brooklyn."
Claude (as persona): "That's right, I work at a small Italian place
in Park Slope. The morning prep is my favorite part of the day..."
```

The system extracts relevant attributes from these conversations to update the persona profile.

## Attribute Reification

A-Proxy translates persona attributes into browser configuration:

| Persona Attribute | Browser Configuration |
|-------------------|----------------------|
| Geographic location | VPN exit node, GeoIP headers |
| Language | Accept-Language header |
| Device type | User-Agent string |
| Browser type | Browser executable |
| Screen size | Viewport dimensions |
| Connection type | Network throttling |

This allows web crawling that authentically represents how a persona would experience the web.

## Data Model

```python
# Example persona structure
{
    "id": 1,
    "name": "Brooklyn Chef",
    "demographic": {
        "latitude": 40.6782,
        "longitude": -73.9442,
        "country": "United States",
        "city": "Brooklyn",
        "region": "New York",
        "language": "en-US",
        "age": 34,
        "occupation": "Chef"
    },
    "psychographic": {
        "interests": ["cooking", "food sourcing", "Italian cuisine"],
        "personal_values": ["quality", "authenticity", "sustainability"],
        "lifestyle": "urban professional",
        "personality": "creative, detail-oriented"
    },
    "behavioral": {
        "browsing_habits": ["recipe sites", "food suppliers", "restaurant reviews"],
        "purchase_history": ["kitchen equipment", "specialty ingredients"],
        "device_usage": {"primary": "mobile", "work": "tablet"}
    },
    "contextual": {
        "time_of_day": "morning",
        "device_type": "mobile",
        "browser_type": "chrome",
        "connection_type": "4g"
    }
}
```

## Related Concepts

- [Archival Goals](archival-goals.md) - Why persona modeling matters for archiving
- [Journeys and Waypoints](journeys-waypoints.md) - Tracking persona interactions
- [Create Personas](../how-to/create-personas.md) - Step-by-step creation guide
