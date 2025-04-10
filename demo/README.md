# A-Proxy Demonstration Script

This project contains a Puppeteer script that automatically demonstrates the key features of the A-Proxy application, creating a guided tour with screenshots and video recording.

## Features Demonstrated

The script showcases the following A-Proxy features:

1. Dashboard and geolocation selection
2. Persona selection and usage
3. Journey creation and management 
4. Adding waypoints to a journey

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)
- A-Proxy application running on http://localhost:5002

## Quick Start

The easiest way to run the demonstration is using the provided shell script:

```bash
cd demo
./run-demo.sh
```

This script will:
1. Check if A-Proxy is running and offer to start it if not
2. Install dependencies if needed
3. Run the demo script
4. Offer to generate a PDF report from the screenshots
5. Provide an option to open the recorded video

## Manual Usage

### Installation

1. Navigate to the demo directory
2. Install dependencies:

```bash
cd demo
npm install
```

### Running the Demo

Make sure A-Proxy is running first, then run:

```bash
npm run demo
```

### Generating a PDF Report

After running the demo, you can create a PDF report from the screenshots:

```bash
npm run report
```

### Other Commands

```bash
# Clean up screenshots, videos, and PDFs
npm run clean

# Run a complete demo (clean, run demo, generate report)
npm run full-demo
```

## Output Files

The script produces the following outputs:

1. **Screenshots**: Saved in the `./screenshots` directory, showing each step of the demonstration
2. **Video**: A recording of the entire demonstration saved in `./videos/a-proxy-demo.mp4`
3. **PDF Report**: A formatted document with all screenshots and explanations

## Troubleshooting

- **Application not running**: Make sure A-Proxy is running before starting the script
- **Element not found errors**: The script includes fallback mechanisms for finding elements, but may need adjustments if the A-Proxy UI has changed
- **Browser closes immediately**: Check the console output for errors

## Customization

You can modify the following settings in the `config` object at the top of the demo-script.js file:

- `baseUrl`: The URL where A-Proxy is running
- `viewport`: Browser window dimensions
- `recordVideo`: Toggle video recording
- `slowMotion`: Delay between actions (in milliseconds)
- `waitTime`: Standard wait time between actions
