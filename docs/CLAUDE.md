# A-Proxy Development Setup and Information

This file contains development information, progress, and important notes for the A-Proxy project.

## Application Startup Command

The command to run the application is `start.sh`, NOT `python app.py`. Always use `start.sh` to run the application.

## Organization of Documentation

- **CLAUDE.md**: Main project progress and implementation details
- **docs/COMMON_ERRORS.md**: Common errors and their solutions
- **docs/SETUP_DEV_ENVIRONMENT.md**: Detailed setup instructions
- **docs/WSL_SETUP.md**: WSL-specific setup instructions
- **docs/MULTIPLE_ENVIRONMENTS.md**: Managing multiple environments
- **docs/PERSONA_API.md**: API documentation
- **docs/DOCKER.md**: Docker setup and configuration
- **docs/IMPLEMENTATION_NOTES.md**: Implementation details
- **docs/ARCHITECTURE.md**: System architecture and components
- **docs/README-DEV.md**: Comprehensive developer guide

## Historical Note: 2025-04-08 Initial WSL Development Environment Setup

This content has been integrated into the current documentation. Please see the docs directory for up-to-date information.

## Home Page and Dashboard Updates (2025-04-18)

Updates completed:
1. Created a new dashboard page that:
   - Displays browser and device information (moved from the home page)
   - Shows integration status for Claude and Internet Archive
   - Includes the location map visualization
   - Displays the application version number from VERSION.txt
   - Has a clean, organized layout with information cards

2. Updated the home page:
   - Removed the URL entry/Preview/Archive form from the header
   - Updated the content to focus on the application's core features
   - Added specific information about capturing personalized web and chat experiences
   - Removed all VPN references and related UI elements
   - Created feature cards for main application functions

## Chat Feature and Journey Integration Improvements (2025-04-18)

Updates completed:
1. **Enhanced Chat Save and Journey Integration**:
   - Added a custom 'fromjson' Jinja2 filter to the Flask application to fix template rendering errors
   - Modified the Save Chat modal to now show "Save Chat as Waypoint" for better clarity
   - Improved journey context detection to automatically select the current journey when saving
   - Enhanced waypoint handling to support both "chat with" and "chat as" perspectives in a single waypoint
   - Added a tabbed interface in waypoint display to show both chat perspectives separately

2. **Journey View Improvements**:
   - Updated the Journey view page to offer two options for continuing a journey: Browse or Chat
   - Modified the empty journey prompt to give users a choice between browsing and chatting
   - Ensured Chat option correctly passes the journey_id parameter to maintain journey context
   - Improved UI consistency across journey interaction points

3. **Conversation Continuity**:
   - Implemented ability to continue conversations directly from waypoints with all chat history
   - Updated "Continue Conversation" buttons to pass waypoint_id to the chat interface
   - Modified the direct_chat route to load and display previous chat history
   - Added smart detection to determine which chat mode to start with based on available history
   - Ensured that both "chat with" and "chat as" histories are properly loaded and displayed

4. **Enhanced Context Management**:
   - Implemented a modular context provider system in services.py
   - Created structured providers for persona and journey context
   - Added ability to pass previous conversations to Claude as context
   - Implemented token counting and management to prevent context overflow
   - Added visual indicators in the UI to show what context is being used
   - Built a system that automatically manages context priorities

These changes ensure users can seamlessly save both perspectives of a chat to the same waypoint, making the journey experience more cohesive. The improved journey page clearly offers both browse and chat options as ways to continue or start a journey. Users can now pick up conversations exactly where they left off when returning to a journey, with Claude maintaining awareness of both persona details and journey context. The contextual depth indicators provide transparency about what information is being used.

## Known Issues (2025-04-18)

1. **User email not displaying in header**: 
   - Despite implementing `{{ current_user.email }}` in the header status bar, the user's email is not being displayed when logged in
   - The template file (_header_status.html) has been updated to show the email, but it's not appearing in the rendered page
   - Potential causes may include:
     - FlaskLogin user object not properly passing the email attribute
     - Template variables not being correctly populated
     - CSS styling issues hiding the email text
   - Next steps:
     - Create a test account with a known email for explicit testing
     - Add debugging output to verify user object properties
     - Check auth.py route handlers to ensure user properties are correctly set
