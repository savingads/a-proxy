# Manage Journeys

Journeys track sequences of interactions performed as a persona. This guide covers creating, viewing, and managing journeys and their waypoints.

## Viewing Journeys

### Journey List

1. Navigate to **Journeys** in the main menu
2. View all journeys sorted by last update
3. Each entry shows:
   - Journey name
   - Associated persona
   - Journey type
   - Status
   - Last updated timestamp

### Journey Details

Click on a journey name to view:

- Full journey information
- List of waypoints in sequence order
- Options to add waypoints or edit the journey

## Creating Journeys

### Automatic Creation

Journeys are automatically created when you:

1. Start browsing as a persona
2. Begin a chat session with a persona
3. Archive a page from persona context

### Manual Creation

1. Navigate to **Journeys**
2. Click **Create New Journey**
3. Fill in the details:

| Field | Description | Required |
|-------|-------------|----------|
| Name | Descriptive journey name | Yes |
| Description | Detailed purpose of the journey | No |
| Persona | Select associated persona | Yes |
| Journey Type | marketing, research, shopping, general | Yes |
| Status | active, completed, paused | Yes |

4. Click **Save**

## Journey Types

| Type | Use Case | Example |
|------|----------|---------|
| marketing | Consumer behavior analysis | Capturing ad targeting |
| research | Information gathering | Academic research patterns |
| shopping | E-commerce interactions | Purchase decision journeys |
| general | Unspecified browsing | General exploration |

## Managing Waypoints

### Viewing Waypoints

1. Open a journey's detail page
2. Waypoints are listed in sequence order
3. Each waypoint shows:
   - Sequence number
   - Type (browse/agent)
   - URL or context
   - Timestamp
   - Preview (for browse waypoints)

### Adding Waypoints Manually

1. Open the journey detail page
2. Click **Add Waypoint**
3. Fill in the waypoint details:

| Field | Description |
|-------|-------------|
| URL | Web address or reference |
| Title | Page title or waypoint label |
| Type | browse or agent |
| Notes | Additional context |

4. Click **Save**

### Adding Waypoints Through Browsing

Waypoints are automatically added when browsing as the journey's persona:

1. Navigate to **Interact As**
2. Select the persona associated with your journey
3. Browse websites
4. Each page visit creates a new waypoint

### Editing Waypoints

1. Open the journey detail page
2. Click on a waypoint
3. Modify the fields
4. Click **Save**

### Deleting Waypoints

1. Open the journey detail page
2. Click on the waypoint
3. Click **Delete**
4. Confirm the deletion

## Journey Status

| Status | Description |
|--------|-------------|
| active | Currently in progress |
| completed | Finished, no more waypoints expected |
| paused | Temporarily suspended |

### Changing Status

1. Open the journey detail page
2. Click **Edit**
3. Change the status field
4. Click **Save**

## Filtering and Searching

### By Persona

View journeys for a specific persona:

1. Navigate to a persona's detail page
2. View the **Journeys** section
3. Click on journeys to view details

### By Type

Filter journeys by type:

1. Navigate to **Journeys**
2. Use the type filter dropdown
3. Select the desired journey type

## Exporting Journey Data

Journey data can be exported for analysis:

1. Open the journey detail page
2. Click **Export**
3. Choose format (JSON recommended)
4. Download the file

Export includes:

- Journey metadata
- All waypoints with timestamps
- Agent conversation data (if applicable)
- Screenshot references

## Best Practices

### Naming Conventions

Use descriptive names that indicate:

- Purpose: "Product Research", "Ad Capture"
- Date: "2024-12-09 Morning Session"
- Persona: "Brooklyn Chef - Coffee Equipment"

### Journey Scope

Keep journeys focused:

- One research topic per journey
- One browsing session per journey
- Clear start and end points

### Documentation

Add notes to waypoints explaining:

- Why a page was visited
- What was observed
- Relevant findings

## Related Guides

- [Journeys and Waypoints](../concepts/journeys-waypoints.md) - Understanding the data model
- [Browse as Persona](browse-as-persona.md) - Creating browse waypoints
- [Archive Web Pages](archive-pages.md) - Saving page captures
