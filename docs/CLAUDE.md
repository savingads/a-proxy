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
