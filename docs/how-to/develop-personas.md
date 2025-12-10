# Develop Personas via Chat

A-Proxy allows personas to be developed through conversations with Claude AI. Archivists chat with or about personas, then manually update the persona profile based on insights from the conversation.

## Overview

The chat interface provides a space to explore persona characteristics through dialogue. Claude responds in context, helping archivists think through persona attributes. After conversations, archivists manually update persona profiles with relevant information.

!!! note "Manual Update Required"
    A-Proxy does not automatically extract attributes from conversations. After chatting, navigate to the persona edit page to add or update attributes based on the conversation.

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

After this conversation, you would manually update:

- Occupation field: Chef
- City field: Brooklyn
- Add to interests: Italian cuisine, cooking

### Exploratory Questions

Ask questions to discover preferences:

```
You: "What websites do you usually visit when looking for recipe inspiration?"

Claude: "I spend a lot of time on Serious Eats - Kenji Lopez-Alt's
scientific approach to cooking really appeals to me..."
```

After this conversation, you would manually update:

- Browsing habits: Add "recipe sites", "food blogs"
- Interests: Add "scientific cooking"

### Scenario Development

Place the persona in situations:

```
You: "You're planning a special dinner menu for next week. Walk me
through how you'd research and prepare."

Claude: "First, I'd check what's coming in fresh from our local farms
this week - I usually browse the Greenmarket site on my phone..."
```

After this conversation, you would manually update:

- Device usage: Mobile for quick browsing
- Personal values: Add "local sourcing"

## Recording Conversations

Chat sessions are automatically saved as waypoints in journeys:

1. Each message exchange is recorded
2. Conversation context is preserved
3. Chat history can be reviewed later

This preserves the conversation for:

- Future reference when updating personas
- Research on LLM interaction patterns
- Documentation of persona development process

## Workflow: Chat Then Update

### Step 1: Have a Conversation

Chat with Claude to explore the persona. Take notes on relevant details that emerge.

### Step 2: Review the Conversation

The conversation is saved as a waypoint. Review it to identify persona attributes.

### Step 3: Update the Persona

1. Navigate to **Personas**
2. Click the persona name
3. Click **Edit**
4. Update relevant fields based on conversation insights
5. Click **Save**

## Building Personas Over Multiple Sessions

**Session 1**: Establish basic identity
```
"You're a chef in Brooklyn who values local ingredients."
```
Then update: occupation, location, values

**Session 2**: Develop behaviors
```
"Tell me about your typical morning routine before work."
```
Then update: time_of_day, lifestyle

**Session 3**: Refine preferences
```
"What brands of kitchen equipment do you trust?"
```
Then update: brand_interactions, purchase_history

**Session 4**: Add depth
```
"How has your approach to cooking evolved over the years?"
```
Then update: attitudes, personality

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

## Related Guides

- [Create Personas](create-personas.md) - Manual persona creation
- [Manage Journeys](manage-journeys.md) - Working with conversation records
- [Persona Model](../concepts/persona-model.md) - Understanding attribute categories
