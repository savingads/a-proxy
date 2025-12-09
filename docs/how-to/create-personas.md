# Create Personas

This guide explains how to create and configure personas in A-Proxy.

## Quick Start

1. Navigate to **Personas** in the main menu
2. Click **Create New Persona**
3. Fill in the persona attributes
4. Click **Save**

## Step-by-Step Guide

### 1. Access the Persona Creation Form

From the main navigation, click **Personas** to view the persona list, then click **Create New Persona**.

### 2. Basic Information

Enter a descriptive name for your persona:

| Field | Example | Notes |
|-------|---------|-------|
| Name | "Brooklyn Chef" | Use a memorable, descriptive name |

### 3. Demographic Attributes

Configure geographic and demographic information:

| Field | Example | Purpose |
|-------|---------|---------|
| Country | United States | Sets GeoIP region |
| City | Brooklyn | Local content targeting |
| Region | New York | State/province identification |
| Language | en-US | Browser Accept-Language header |
| Latitude/Longitude | 40.6782, -73.9442 | Precise geolocation |
| Age | 34 | Demographic targeting |
| Gender | Male | Demographic segmentation |
| Education | Culinary Degree | Profile context |
| Income | $60,000-80,000 | Economic targeting |
| Occupation | Chef | Professional context |

### 4. Psychographic Attributes

Define psychological characteristics:

| Field | Type | Example |
|-------|------|---------|
| Interests | List | cooking, food sourcing, Italian cuisine |
| Personal Values | List | quality, authenticity, sustainability |
| Attitudes | List | health-conscious, locally-focused |
| Lifestyle | Text | urban professional |
| Personality | Text | creative, detail-oriented |
| Opinions | List | organic is worth the cost, local sourcing matters |

**Tips for Lists**: Enter items separated by commas or use the add button for each item.

### 5. Behavioral Attributes

Specify online behavior patterns:

| Field | Type | Example |
|-------|------|---------|
| Browsing Habits | List | recipe sites, food suppliers, restaurant reviews |
| Purchase History | List | kitchen equipment, specialty ingredients |
| Brand Interactions | List | KitchenAid, Whole Foods, local farms |
| Device Usage | Object | {"primary": "mobile", "work": "tablet"} |
| Social Media Activity | Object | {"instagram": "daily", "twitter": "weekly"} |
| Content Consumption | Object | {"video": "cooking shows", "reading": "food blogs"} |

### 6. Contextual Attributes

Define situational parameters:

| Field | Options | Example |
|-------|---------|---------|
| Time of Day | morning, afternoon, evening, night, all day | morning |
| Day of Week | weekday, weekend, all week | weekday |
| Season | spring, summer, fall, winter | fall |
| Weather | (free text) | clear |
| Device Type | desktop, laptop, tablet, mobile | mobile |
| Browser Type | chrome, firefox, safari, edge | chrome |
| Screen Size | (resolution) | 390x844 |
| Connection Type | wifi, ethernet, 4g, 5g, 3g | 4g |

### 7. Save the Persona

Click **Save** to create the persona. You will be redirected to the persona list.

## Editing Personas

1. Navigate to **Personas**
2. Click on the persona name to view details
3. Click **Edit** to modify attributes
4. Make changes and click **Save**

## Deleting Personas

1. Navigate to **Personas**
2. Click on the persona to view details
3. Click **Delete**
4. Confirm the deletion

!!! warning "Cascade Deletion"
    Deleting a persona may affect associated journeys. Review linked journeys before deletion.

## Best Practices

### Creating Realistic Personas

1. **Consistency**: Ensure attributes align logically (e.g., a student persona shouldn't have high income)
2. **Specificity**: More detailed personas produce more targeted archival captures
3. **Research Basis**: Base personas on actual demographic research when possible

### Persona Naming Conventions

Use names that indicate key characteristics:

- "Brooklyn Chef, 34, Mobile" - location + occupation + age + device
- "German Student Researcher" - nationality + role
- "Retired UK Gardener" - status + location + interest

### Geographic Accuracy

For location-based personalization:

1. Set accurate latitude/longitude coordinates
2. Ensure city/region/country are consistent
3. Use appropriate language codes (e.g., "de-DE" for German in Germany)

## LLM-Assisted Creation

Personas can also be developed through chat. See [Develop Personas via Chat](develop-personas.md) for details.

## Related Guides

- [Develop Personas via Chat](develop-personas.md) - Build personas through conversation
- [Persona Model](../concepts/persona-model.md) - Understanding the 4-dimensional framework
- [Browse as Persona](browse-as-persona.md) - Using personas for web browsing
