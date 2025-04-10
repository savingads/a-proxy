/**
 * Script to compile screenshots into a PDF report
 * 
 * This utility takes all screenshots from the demo and 
 * creates a nicely formatted PDF report document.
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

// Configuration
const config = {
  screenshotsDir: './screenshots',
  outputFile: './A-Proxy-Demo-Report.pdf',
  pageOptions: {
    format: 'A4',
    margin: {
      top: '50px',
      right: '50px',
      bottom: '50px',
      left: '50px'
    }
  },
  title: 'A-Proxy Feature Demonstration',
  subtitle: 'Visual Guide to Key Features'
};

// Get step descriptions based on filename
function getStepDescription(filename) {
  // Extract the step number and name from the filename
  const match = filename.match(/(\d+)-(.+)\.png$/);
  if (!match) return { number: 0, name: filename };
  
  const number = parseInt(match[1]);
  const name = match[2].replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  
  // Specific descriptions for each step
  const descriptions = {
    'Home Page': 'The A-Proxy home page provides an overview of the application and current status.',
    'Dashboard': 'The dashboard allows selecting geolocation and language settings.',
    'Select Country': 'Users can select a country to simulate browsing from that location.',
    'Click Map': 'Users can click directly on the map to set a precise geolocation.',
    'Test Geolocation': 'Testing the geolocation shows how the browser reports its location.',
    'Personas List': 'The personas page shows all saved user personas with their settings.',
    'Selected Persona': 'A persona can be selected to use for browsing sessions.',
    'Journeys List': 'The journeys page shows all tracking sessions for browsing activities.',
    'Create Journey Form': 'New journeys can be created to track specific browsing sessions.',
    'Filled Journey Form': 'Journey details include name, description, type, and associated persona.',
    'Journey Created': 'After creation, the journey is ready to track browsing activities.',
    'Journey Started': 'Starting a journey initiates the tracking session.',
    'Waypoint Url Loaded': 'Visiting a website during a journey creates a potential waypoint.',
    'Waypoint Saved': 'Saving the waypoint adds it to the journey timeline.',
    'Back To Journeys': 'Returning to the journeys list shows all active journeys.',
    'View Journey Details': 'Journey details show all waypoints and related information.',
    'Demo Completed': 'The demonstration has covered all key features of A-Proxy.'
  };
  
  const descriptionKey = Object.keys(descriptions).find(key => 
    name.toLowerCase().includes(key.toLowerCase())
  );
  
  return { 
    number, 
    name, 
    description: descriptionKey ? descriptions[descriptionKey] : ''
  };
}

// Create PDF from screenshots
async function createReport() {
  try {
    // Check if screenshots directory exists
    if (!fs.existsSync(config.screenshotsDir)) {
      console.error(`Screenshots directory not found: ${config.screenshotsDir}`);
      process.exit(1);
    }
    
    // Get all screenshot files and sort them
    const files = fs.readdirSync(config.screenshotsDir)
      .filter(file => file.endsWith('.png'))
      .sort((a, b) => {
        const numA = parseInt(a.match(/^(\d+)/)?.[1] || '0');
        const numB = parseInt(b.match(/^(\d+)/)?.[1] || '0');
        return numA - numB;
      });
      
    if (files.length === 0) {
      console.error('No screenshots found. Please run the demo script first.');
      process.exit(1);
    }
    
    console.log(`Found ${files.length} screenshots. Creating PDF report...`);
    
    // Launch browser
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Create PDF document
    await page.setContent(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${config.title}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
          }
          .cover {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 20px;
            box-sizing: border-box;
          }
          .cover h1 {
            font-size: 36px;
            margin-bottom: 10px;
            color: #0d6efd;
          }
          .cover h2 {
            font-size: 24px;
            font-weight: normal;
            margin-top: 0;
            color: #6c757d;
          }
          .cover .date {
            margin-top: 50px;
            font-style: italic;
            color: #6c757d;
          }
          .screenshot-page {
            page-break-after: always;
            padding: 20px;
          }
          .step-number {
            font-size: 18px;
            color: #0d6efd;
            margin-bottom: 5px;
          }
          .step-title {
            font-size: 24px;
            margin-top: 0;
            margin-bottom: 15px;
          }
          .description {
            margin-bottom: 20px;
            font-size: 16px;
            line-height: 1.5;
          }
          .screenshot {
            max-width: 100%;
            border: 1px solid #dee2e6;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
          }
          .footer {
            text-align: center;
            margin-top: 20px;
            color: #6c757d;
            font-size: 12px;
          }
        </style>
      </head>
      <body>
        <!-- Cover Page -->
        <div class="cover">
          <h1>${config.title}</h1>
          <h2>${config.subtitle}</h2>
          <p class="date">Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}</p>
        </div>
        
        <!-- Screenshots Pages -->
        ${files.map(file => {
          const { number, name, description } = getStepDescription(file);
          return `
            <div class="screenshot-page">
              <p class="step-number">Step ${number}</p>
              <h2 class="step-title">${name}</h2>
              <p class="description">${description}</p>
              <img class="screenshot" src="file://${path.resolve(path.join(config.screenshotsDir, file))}" />
              <div class="footer">A-Proxy Demonstration - Page ${number} of ${files.length}</div>
            </div>
          `;
        }).join('')}
      </body>
      </html>
    `);
    
    // Generate PDF
    await page.pdf({
      path: config.outputFile,
      format: config.pageOptions.format,
      margin: config.pageOptions.margin,
      printBackground: true
    });
    
    await browser.close();
    
    console.log(`PDF report created successfully: ${config.outputFile}`);
  } catch (error) {
    console.error('Error creating PDF report:', error);
    process.exit(1);
  }
}

// Run the report generation
createReport();
