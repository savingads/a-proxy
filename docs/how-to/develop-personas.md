# Develop Personas via Chat

A-Proxy allows personas to be developed through conversations with an LLM. When conversations are saved as waypoints, A-Proxy automatically extracts persona attributes across all four categories. Archivists can then review and refine the extracted data.

## Overview

The chat interface provides a space to explore persona characteristics through dialogue. The LLM responds in context, helping archivists think through persona attributes. When conversations are saved, attributes are automatically extracted and merged into the persona profile.

!!! note "Automatic + Manual Updates"
    When a conversation is saved as a waypoint, A-Proxy automatically extracts persona attributes across all four categories (demographic, psychographic, behavioral, contextual) using the configured LLM. Archivists can also manually update persona profiles to refine or correct extracted data.

## Starting a Persona Chat

### Method 1: Direct Chat

1. Navigate to **Personas**
2. Click on an existing persona
3. Click **Chat** or **Direct Chat**
4. Begin conversing as or about the persona

### Method 2: Interact As

1. Navigate to **Interact As**
2. Select a persona from the dropdown
3. Choose **Chat** mode
4. Start the conversation

## Chat Modes

### Chat AS the Persona

Claude adopts the persona's identity and responds from their perspective:

```
System: You are [Persona Name], a 34-year-old chef in Brooklyn...
User: How do you feel about online grocery shopping?
Claude (as persona): I'm pretty skeptical of it, honestly. For my
restaurant, I need to see and smell the ingredients...
```

This mode helps explore how a persona might think or behave.

### Chat ABOUT the Persona

Discuss and develop the persona in third person:

```
User: What would this persona's reaction be to a new food delivery app?
Claude: Given their values around local sourcing and quality, they would
likely be skeptical of food delivery apps...
```

This mode helps analyze persona characteristics objectively.

## Conversation Techniques

### Directive Statements

Establish persona facts through statements:

```
You: "You have a job as a chef at a restaurant on 36th Street in Brooklyn."

Claude: "That's right, I work at a small Italian place in Park Slope.
The morning prep is my favorite part of the day..."
```

When saved, A-Proxy automatically extracts:

- Occupation: Chef
- City: Brooklyn
- Interests: Italian cuisine, cooking

### Exploratory Questions

Ask questions to discover preferences:

```
You: "What websites do you usually visit when looking for recipe inspiration?"

Claude: "I spend a lot of time on Serious Eats - Kenji Lopez-Alt's
scientific approach to cooking really appeals to me..."
```

When saved, A-Proxy automatically extracts:

- Browsing habits: "recipe sites", "food blogs"
- Interests: "scientific cooking"

### Scenario Development

Place the persona in situations:

```
You: "You're planning a special dinner menu for next week. Walk me
through how you'd research and prepare."

Claude: "First, I'd check what's coming in fresh from our local farms
this week - I usually browse the Greenmarket site on my phone..."
```

When saved, A-Proxy automatically extracts:

- Device type: mobile
- Personal values: "local sourcing"

## Recording Conversations

Chat sessions are automatically saved as waypoints in journeys:

1. Each message exchange is recorded
2. Conversation context is preserved
3. Chat history can be reviewed later

This preserves the conversation for:

- Future reference when updating personas
- Research on LLM interaction patterns
- Documentation of persona development process

## Workflow: Chat, Extract, Refine

### Step 1: Have a Conversation

Chat with Claude to explore the persona. The conversation can reveal demographic, psychographic, behavioral, and contextual details.

### Step 2: Save the Conversation

Save the chat as a waypoint. A-Proxy automatically extracts persona attributes from the conversation using the configured LLM and merges them into the persona profile.

### Step 3: Review and Refine

1. Navigate to **Personas**
2. Click the persona name to review the updated attributes
3. Click **Edit** to correct or refine any extracted data
4. Click **Save**

## Building Personas Over Multiple Sessions

**Session 1**: Establish basic identity
```
"You're a chef in Brooklyn who values local ingredients."
```
Auto-extracted: occupation, location, values

**Session 2**: Develop behaviors
```
"Tell me about your typical morning routine before work."
```
Auto-extracted: time_of_day, lifestyle

**Session 3**: Refine preferences
```
"What brands of kitchen equipment do you trust?"
```
Auto-extracted: brand_interactions, purchase_history

**Session 4**: Add depth
```
"How has your approach to cooking evolved over the years?"
```
Auto-extracted: attitudes, personality

## Best Practices

### Keep Notes During Chat

Note specific attributes mentioned during conversation for later data entry.

### Maintain Consistency

- Review existing persona data before new sessions
- Refer back to established facts in conversation
- Resolve contradictions through follow-up questions

### Document Reasoning

Add notes to persona fields explaining why attributes were chosen:

```
Occupation: Chef
(Established in chat session 2024-12-09, discussed restaurant work)
```

## Automatic Attribute Extraction

When a conversation is saved as a waypoint, A-Proxy uses the configured LLM to automatically extract persona attributes across all four categories:

- **Demographic**: age, gender, location, language, education, income, occupation
- **Psychographic**: interests, values, attitudes, opinions, lifestyle, personality
- **Behavioral**: browsing habits, purchase history, brand interactions, device usage, social media activity, content consumption
- **Contextual**: time of day, day of week, season, device type, browser type, connection type

Extraction is **additive** — list-type fields (interests, browsing habits, etc.) accumulate across conversations, while scalar fields (age, occupation, etc.) are updated to the latest value. Existing data is preserved when the LLM cannot determine a field.

This works with any configured LLM provider (Ollama, vLLM on Picotte, Anthropic, OpenAI).

## Exporting Personas

### JSON Export

From the persona detail page, click **Export > Download JSON** to download the full persona profile. The JSON file includes all four attribute categories and can be used for:

- Backup and migration between A-Proxy instances
- Input to external tools and scripts
- Research data collection

### Chrome Browsing Profile (Planned)

A complementary approach to persona-driven archiving involves generating Chrome browsing profiles with actual search history, YouTube watch history, and browsing history that influence ad-targeting algorithms. This is a separate but complementary workflow:

1. **A-Proxy** defines the persona analytically (who the persona *is*)
2. **Browsing profile scripts** generate behavioral artifacts (what the browser *did* as that persona)
3. **Archiving tools** (Browsertrix, ArchiveWeb.page) use the Chrome profile to capture personalized content

The Chrome profile export is planned and requires coordination with the browsing profile automation scripts. The **Export > Export as Chrome Profile** button on the persona detail page is a placeholder for this integration.

## Related Guides

- [Create Personas](create-personas.md) - Manual persona creation
- [Manage Journeys](manage-journeys.md) - Working with conversation records
- [Persona Model](../concepts/persona-model.md) - Understanding attribute categories
