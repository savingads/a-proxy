# First Login

This guide walks you through your first login to A-Proxy and introduces the main interface.

## Default Credentials

When you first start the application, use these credentials:

| Field | Value |
|-------|-------|
| Email | `admin@example.com` |
| Password | `password` |

!!! warning "Security Notice"
    Change these credentials in production environments. The default credentials are intended for initial setup only.

## Login Process

1. Navigate to `http://localhost:5002` in your browser
2. Enter the default email and password
3. Click **Login**

## Main Interface Overview

After logging in, you will see the main navigation with these sections:

### Personas

The **Personas** page displays all created personas. From here you can:

- View existing personas
- Create new personas
- Edit persona attributes
- Delete personas

### Journeys

The **Journeys** page shows recorded interaction sequences. Each journey:

- Is linked to a specific persona
- Contains multiple waypoints (individual interactions)
- Tracks browsing sessions and chat conversations

### Archives

The **Archives** page displays saved web page captures. Archives include:

- Full page screenshots
- HTML content
- Metadata about capture context (location, language, etc.)

### Interact As

The **Interact As** page allows you to:

- Select a persona to embody
- Browse the web as that persona
- Chat with Claude AI from the persona's perspective
- Archive pages during the session

### Settings

The **Settings** page provides configuration options for:

- VPN connection settings
- API key management
- Application preferences

## Interface Navigation

```
+------------------+
|     Header       |
| [Logo] [Nav Menu]|
+------------------+
|                  |
|   Main Content   |
|                  |
+------------------+
```

The navigation menu items:

| Menu Item | Description |
|-----------|-------------|
| Personas | Manage user personas |
| Journeys | View and manage interaction records |
| Archives | Browse saved web captures |
| Interact As | Browse/chat as a selected persona |
| Settings | Application configuration |

## Creating Your First Persona

1. Click **Personas** in the navigation
2. Click **Create New Persona**
3. Fill in the four attribute categories:
   - **Demographic**: Location, language, age, occupation
   - **Psychographic**: Interests, values, personality
   - **Behavioral**: Browsing habits, device preferences
   - **Contextual**: Time of day, connection type
4. Click **Save**

For detailed instructions, see [Create Personas](../how-to/create-personas.md).

## Starting Your First Journey

1. Click **Interact As** in the navigation
2. Select a persona from the dropdown
3. Choose an interaction mode:
   - **Browse**: Navigate websites as the persona
   - **Chat**: Converse with Claude AI as the persona
4. Your interactions will be recorded as waypoints in a journey

For detailed instructions, see [Manage Journeys](../how-to/manage-journeys.md).

## Next Steps

- [Persona Model](../concepts/persona-model.md) - Understand the 4-dimensional persona framework
- [Create Personas](../how-to/create-personas.md) - Detailed persona creation guide
- [Manage Journeys](../how-to/manage-journeys.md) - Working with interaction records
