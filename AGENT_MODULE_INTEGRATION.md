# Agent Module Integration

This document describes how the `agent_module` submodule has been integrated into the A-Proxy application to provide AI assistant capabilities within the journey workflow.

## Summary of Changes

### 1. Submodule Addition
- Added `agent_module` from `https://github.com/cr625/agent_module` as a Git submodule

### 2. Database Schema Updates
- Added `type` column to the `waypoints` table to distinguish between regular waypoints (`url`) and agent waypoints (`agent`)
- Added `agent_data` column to store conversation data in JSON format

### 3. Agent Service Layer
- Created `utils/agent.py` service to handle interactions with the agent module
- Implemented methods to:
  - Create agent blueprint
  - Save agent conversations as waypoints
  - Retrieve agent conversation data

### 4. UI Components
- Created `templates/agent_waypoint.html` for the agent chat interface
- Created `templates/agent_waypoint_summary.html` for displaying agent waypoints in the journey view
- Updated journey pages to include "Ask Agent" buttons

### 5. Routes & Integration
- Added routes in `routes/agent.py` for:
  - Displaying the agent interface
  - Processing agent messages
  - Saving agent conversations as waypoints
- Registered the agent blueprint in the main application

## Usage

The agent functionality is now available in journey workflows:

1. **Accessing the Agent**:
   - From the Journey View page, click the "Ask Agent" button in the toolbar
   - From the Journey Browse page, click the "Ask Agent" button in the header

2. **Using the Agent**:
   - Type your questions or requests in the message input
   - The agent will respond based on the context of your journey
   - You can reset the conversation or save it as a waypoint

3. **Viewing Agent Conversations**:
   - Agent conversations saved as waypoints appear in the journey timeline
   - They are displayed with a distinctive style to differentiate them from regular URL waypoints

## Implementation Details

### Agent Waypoint Structure
Agent waypoints store the following data:
- Basic waypoint information (title, notes, timestamp)
- Conversation history (messages between user and agent)
- Metadata about the conversation

### Technical Integration
- The agent module is integrated as a submodule to keep it separate from the main codebase
- The module's functionality is wrapped in a service layer for better maintainability
- Communication with the agent happens through a simple API in the agent routes

## Future Improvements

Potential future enhancements:
- Deeper integration with journey context (providing more information to the agent about waypoints)
- Customizable agent personas based on journey type
- Enhanced visualization of agent conversations
- Ability to export agent conversations as reports
