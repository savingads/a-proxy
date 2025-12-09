# Develop Personas via Chat

A-Proxy allows personas to be developed and refined through conversations with Claude AI. This approach creates more natural, organically developed personas.

## Overview

Instead of filling out forms, archivists can chat with Claude while adopting a persona perspective. The system extracts relevant attributes from these conversations to build out the persona profile.

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

## Chat Techniques

### Directive Statements

Provide explicit information about the persona:

```
You: "You have a job as a chef at a restaurant on 36th Street in Brooklyn."

Claude: "That's right, I work at a small Italian place in Park Slope.
The morning prep is my favorite part of the day - there's something
meditative about chopping vegetables before the lunch rush."
```

The system extracts:
- Occupation: Chef
- Location: Brooklyn, 36th Street
- Workplace type: Italian restaurant
- Work schedule: Morning shifts

### Exploratory Questions

Ask questions to develop personality and preferences:

```
You: "What websites do you usually visit when looking for recipe inspiration?"

Claude: "I spend a lot of time on Serious Eats - Kenji Lopez-Alt's
scientific approach to cooking really appeals to me. I also follow
several Italian food blogs and check supplier sites for seasonal
ingredients."
```

The system extracts:
- Browsing habits: Serious Eats, Italian food blogs, supplier sites
- Interests: Scientific cooking approach, seasonal ingredients
- Personality: Detail-oriented, methodical

### Scenario Development

Place the persona in situations to reveal behavior:

```
You: "You're planning a special dinner menu for next week. Walk me
through how you'd research and prepare."

Claude: "First, I'd check what's coming in fresh from our local farms
this week - I usually browse the Greenmarket site on my phone during
my commute. Then I'd spend some time on my laptop looking at classic
Italian preparations..."
```

The system extracts:
- Device usage: Mobile for quick browsing, laptop for research
- Values: Local sourcing, seasonal cooking
- Behavioral patterns: Research habits, planning approach

## Persona Modes

### Chat AS the Persona

Claude adopts the persona's identity and responds from their perspective:

```
System: You are [Persona Name], a 34-year-old chef in Brooklyn...
User: How do you feel about online grocery shopping?
Claude (as persona): I'm pretty skeptical of it, honestly. For my
restaurant, I need to see and smell the ingredients...
```

### Chat ABOUT the Persona

Discuss and develop the persona in third person:

```
User: What would this persona's reaction be to a new food delivery app?
Claude: Given their values around local sourcing and quality, they would
likely be skeptical of food delivery apps...
```

## Attribute Extraction

The system monitors conversations for extractable information:

| Mentioned Information | Extracted Attribute | Category |
|----------------------|---------------------|----------|
| "I work at a restaurant" | occupation: Chef | Demographic |
| "I usually browse on my phone" | device_type: mobile | Contextual |
| "Local sourcing matters to me" | personal_values: [local sourcing] | Psychographic |
| "I check recipe sites every morning" | time_of_day: morning | Contextual |

## Building Context Over Time

Each conversation builds on previous ones:

**Session 1**: Establish basic identity
```
"You're a chef in Brooklyn who values local ingredients."
```

**Session 2**: Develop behaviors
```
"Tell me about your typical morning routine before work."
```

**Session 3**: Refine preferences
```
"What brands of kitchen equipment do you trust?"
```

**Session 4**: Add depth
```
"How has your approach to cooking evolved over the years?"
```

## Recording Conversations

Chat sessions are automatically saved as waypoints in journeys:

1. Each message exchange is recorded
2. Conversation context is preserved
3. Extracted attributes are linked to the persona
4. Chat history can be reviewed later

## Best Practices

### Start Broad, Then Narrow

1. Begin with general characteristics
2. Progressively add specific details
3. Allow natural personality traits to emerge

### Maintain Consistency

- Review previous conversations before new sessions
- Refer back to established facts
- Flag contradictions for resolution

### Document Reasoning

Include notes about why certain attributes were chosen:

```
User: "You decided to focus on Italian cuisine after training in Rome."
```

This provides research context for the persona development.

## Reviewing Extracted Data

After chat sessions:

1. Navigate to the persona's profile
2. Review newly extracted attributes
3. Confirm or adjust automatically detected information
4. Add manual annotations if needed

## Related Guides

- [Create Personas](create-personas.md) - Manual persona creation
- [Manage Journeys](manage-journeys.md) - Working with conversation records
- [Persona Model](../concepts/persona-model.md) - Understanding attribute categories
