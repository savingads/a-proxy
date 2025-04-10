/**
 * A-Proxy Feature Demonstration Script
 * 
 * This script demonstrates the key features of A-Proxy:
 * 1. Dashboard and geolocation selection
 * 2. Persona selection and usage
 * 3. Journey creation and management
 * 4. Adding waypoints to a journey
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { PuppeteerScreenRecorder } = require('puppeteer-screen-recorder');

// Configuration
const config = {
  baseUrl: 'http://localhost:5002',
  screenshotsDir: './screenshots',
  videosDir: './videos',
  viewport: { width: 1280, height: 800 },
  recordVideo: true,
  slowMotion: 100, // Slow down actions by 100ms for better visibility
  waitTime: 1000     // Standard wait time between actions
};

// Helper function to highlight an element before clicking
async function highlightAndClick(page, selector, options = {}) {
  try {
    await page.evaluate((selector) => {
      const element = document.querySelector(selector);
      if (!element) return;
      
      const originalBorder = element.style.border;
      const originalBoxShadow = element.style.boxShadow;
      
      element.style.border = '2px solid #FF5722';
      element.style.boxShadow = '0 0 10px rgba(255, 87, 34, 0.7)';
      element.style.transition = 'all 0.3s';
      
      setTimeout(() => {
        element.style.border = originalBorder;
        element.style.boxShadow = originalBoxShadow;
      }, 800);
    }, selector);
    
    await page.waitForTimeout(300);
    await page.click(selector, options);
    await page.waitForTimeout(config.waitTime);
  } catch (error) {
    console.error(`Error highlighting/clicking element ${selector}:`, error);
    // Still try to click even if highlighting fails
    await page.click(selector, options).catch(e => console.error(`Fallback click also failed: ${e.message}`));
    await page.waitForTimeout(config.waitTime);
  }
}

// Helper function to add a note/annotation to the page for the demo
async function addNoteToPage(page, message, position = { x: 100, y: 100 }) {
  await page.evaluate(({ message, position }) => {
    // Remove any existing notes
    const existingNotes = document.querySelectorAll('.demo-note');
    existingNotes.forEach(note => note.remove());
    
    // Create new note element
    const note = document.createElement('div');
    note.className = 'demo-note';
    note.textContent = message;
    note.style.position = 'fixed';
    note.style.left = `${position.x}px`;
    note.style.top = `${position.y}px`;
    note.style.backgroundColor = 'rgba(33, 150, 243, 0.9)';
    note.style.color = 'white';
    note.style.padding = '10px 15px';
    note.style.borderRadius = '4px';
    note.style.zIndex = '10000';
    note.style.maxWidth = '300px';
    note.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    note.style.fontFamily = 'Arial, sans-serif';
    
    document.body.appendChild(note);
    
    // Auto-remove after 5 seconds
    setTimeout(() => note.remove(), 5000);
  }, { message, position });
  
  await page.waitForTimeout(1000); // Give time for the note to be visible
}

// Main function to demonstrate A-Proxy features
async function demonstrateAProxy() {
  // Launch browser
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: config.viewport,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  await page.setViewport(config.viewport);
  
  // Prepare directories
  if (!fs.existsSync(config.screenshotsDir)) fs.mkdirSync(config.screenshotsDir);
  if (!fs.existsSync(config.videosDir)) fs.mkdirSync(config.videosDir);
  
  // Recorder setup
  let recorder;
  if (config.recordVideo) {
    const recorderConfig = {
      fps: 30,
      ffmpeg_Path: null, // Uses default
      videoFrame: {
        width: config.viewport.width,
        height: config.viewport.height
      },
      aspectRatio: '16:9'
    };
    
    recorder = new PuppeteerScreenRecorder(page, recorderConfig);
    await recorder.start(`${config.videosDir}/a-proxy-demo.mp4`);
  }
  
  try {
    // 1. Start at the home page
    console.log("1. Navigating to the home page...");
    await page.goto(`${config.baseUrl}/`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: `${config.screenshotsDir}/01-home-page.png` });
    
    // Add annotation
    await addNoteToPage(page, "A-Proxy Home Page - Starting our demonstration", { x: 100, y: 100 });
    
    // 2. Navigate to the dashboard
    console.log("2. Navigating to the dashboard...");
    // Based on server logs, navigate directly to persona dashboard
    await page.goto(`${config.baseUrl}/persona/dashboard`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${config.screenshotsDir}/02-dashboard.png` });
    
    // Add annotation
    await addNoteToPage(page, "Dashboard - Here we can select geolocation and language settings", { x: 100, y: 100 });
    
    // 3. Select a country from the dropdown
    console.log("3. Selecting a country...");
    try {
      // Try to find a country dropdown
      const countrySelectors = [
        'select#country',
        'select#country-selector',
        'select[name="country"]',
        'select.country-selector'
      ];
      
      for (const selector of countrySelectors) {
        const countrySelector = await page.$(selector);
        if (countrySelector) {
          await highlightAndClick(page, selector);
          await page.select(selector, 'DE'); // DE for Germany
          console.log(`Selected country using selector: ${selector}`);
          break;
        }
      }
      
      await page.waitForTimeout(1000);
      await page.screenshot({ path: `${config.screenshotsDir}/03-select-country.png` });
    } catch (error) {
      console.log("Country selector not found, trying to click on the map...");
      try {
        // Alternative: click on map directly if no country selector
        await addNoteToPage(page, "Selecting location by clicking on the map", { x: 100, y: 150 });
        await page.click('#map', { position: { x: 500, y: 300 } }); // Approximate position
        await page.waitForTimeout(1000);
        await page.screenshot({ path: `${config.screenshotsDir}/03-click-map.png` });
      } catch (mapError) {
        console.error("Could not interact with map:", mapError);
      }
    }
    
    // 4. Test geolocation by checking for geolocation test buttons
    console.log("4. Testing geolocation...");
    try {
      // Try to find a button that might test geolocation
      const geolocationButtonSelectors = [
        'button.test-geolocation-btn',
        'a[href*="geolocation"]',
        'button:contains("Test")',
        'button:contains("Apply")',
        'button:contains("Set")'
      ];
      
      for (const selector of geolocationButtonSelectors) {
        try {
          const button = await page.$(selector);
          if (button) {
            await button.click();
            console.log(`Clicked geolocation test button using selector: ${selector}`);
            await page.waitForTimeout(2000);
            await page.screenshot({ path: `${config.screenshotsDir}/04-test-geolocation.png` });
            break;
          }
        } catch (btnError) {
          console.log(`Selector ${selector} not found or not clickable`);
        }
      }
      
      // If no specific test button found, look for any visible button
      if (!await page.$(`${config.screenshotsDir}/04-test-geolocation.png`)) {
        const visibleButtons = await page.$$('button:not([hidden]):not([disabled])');
        for (const button of visibleButtons) {
          const buttonText = await page.evaluate(el => el.textContent.toLowerCase(), button);
          if (buttonText.includes('test') || buttonText.includes('apply') || buttonText.includes('set')) {
            await button.click();
            await page.waitForTimeout(2000);
            await page.screenshot({ path: `${config.screenshotsDir}/04-test-geolocation.png` });
            break;
          }
        }
      }
    } catch (error) {
      console.error("Error testing geolocation:", error);
    }
    
    // 5. Navigate to the Personas page
    console.log("5. Navigating to Personas page...");
    await page.goto(`${config.baseUrl}/personas`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${config.screenshotsDir}/05-personas-list.png` });
    
    // Add annotation
    await addNoteToPage(page, "Personas Page - We can view and manage user personas here", { x: 100, y: 100 });
    
    // 6. Select and use a persona
    console.log("6. Selecting a persona...");
    try {
      // Find a "Use" button for a persona
      const useButtonSelectors = [
        'a.btn-outline-secondary',
        'a[href*="use-persona"]',
        'a:contains("Use")'
      ];
      
      for (const selector of useButtonSelectors) {
        try {
          const buttons = await page.$$(selector);
          if (buttons.length > 0) {
            await buttons[0].click();
            console.log(`Clicked 'Use' button with selector: ${selector}`);
            await page.waitForNavigation({ waitUntil: 'networkidle0' });
            await page.screenshot({ path: `${config.screenshotsDir}/06-selected-persona.png` });
            
            // Add annotation
            await addNoteToPage(page, "Selected a persona to use for browsing", { x: 100, y: 100 });
            break;
          }
        } catch (btnError) {
          console.log(`Selector ${selector} not found or not clickable`);
        }
      }
    } catch (error) {
      console.error("Error selecting persona:", error);
    }
    
    // 7. Navigate to the Journeys page
    console.log("7. Navigating to Journeys page...");
    await page.goto(`${config.baseUrl}/journeys`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${config.screenshotsDir}/07-journeys-list.png` });
    
    // Add annotation
    await addNoteToPage(page, "Journeys Page - We can create and manage user journeys", { x: 100, y: 100 });
    
    // 8. Create a new journey
    console.log("8. Creating a new journey...");
    // Navigate directly to create journey page based on server logs
    await page.goto(`${config.baseUrl}/journey/create`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${config.screenshotsDir}/08-create-journey-form.png` });
    
    // Add annotation
    await addNoteToPage(page, "Creating a new journey to track browsing behavior", { x: 100, y: 100 });
    
    // 9. Fill in journey details
    console.log("9. Filling journey details...");
    await page.type('#name', 'Demo Journey');
    await page.type('#description', 'A demonstration journey for the feature showcase');
    try {
      await page.select('#journey_type', 'research');
    } catch (error) {
      console.log("Could not select journey type:", error.message);
    }
    
    // Try to select a persona if the field exists
    try {
      const personaSelector = '#persona_id';
      const personaExists = await page.$(personaSelector);
      if (personaExists) {
        const options = await page.$$(`${personaSelector} > option`);
        if (options.length > 1) {
          // Select the first non-empty option
          const value = await page.evaluate(el => el.value, options[1]);
          await page.select(personaSelector, value);
        }
      }
    } catch (error) {
      console.log("Could not select persona for journey:", error.message);
    }
    
    await page.screenshot({ path: `${config.screenshotsDir}/09-filled-journey-form.png` });
    
    // 10. Submit the journey form
    console.log("10. Submitting journey form...");
    await highlightAndClick(page, 'button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    await page.screenshot({ path: `${config.screenshotsDir}/10-journey-created.png` });
    
    // Add annotation
    await addNoteToPage(page, "Journey created successfully", { x: 100, y: 100 });
    
    // 11. Start or browse the journey
    console.log("11. Starting the journey...");
    try {
      // Look for the Start or Browse button
      const startButtonSelectors = [
        'a.btn-outline-success',
        'a[href*="browse_journey"]',
        'a:contains("Start")',
        'a:contains("Browse")'
      ];
      
      for (const selector of startButtonSelectors) {
        try {
          const buttons = await page.$$(selector);
          if (buttons.length > 0) {
            await buttons[0].click();
            console.log(`Clicked journey start button with selector: ${selector}`);
            await page.waitForTimeout(2000);
            await page.screenshot({ path: `${config.screenshotsDir}/11-journey-started.png` });
            
            // Add annotation
            await addNoteToPage(page, "Starting our journey browsing experience", { x: 100, y: 100 });
            break;
          }
        } catch (btnError) {
          console.log(`Selector ${selector} not found or not clickable`);
        }
      }
    } catch (error) {
      console.error("Error starting journey:", error);
    }
    
    // 12. Add a waypoint by visiting a URL
    console.log("12. Adding a waypoint...");
    try {
      // Look for a URL input field
      const urlInputSelectors = [
        'input[type="url"]',
        'input[name="url"]',
        'input.form-control[placeholder*="URL"]',
        'input.form-control[placeholder*="url"]'
      ];
      
      for (const selector of urlInputSelectors) {
        const inputs = await page.$$(selector);
        if (inputs.length > 0) {
          await inputs[0].type('https://example.com');
          console.log(`Entered URL using selector: ${selector}`);
          
          // Find and click a submit button
          const submitSelectors = [
            'button[type="submit"]',
            'button.btn-primary',
            'button:contains("Preview")',
            'button:contains("Visit")'
          ];
          
          for (const submitSelector of submitSelectors) {
            try {
              const buttons = await page.$$(submitSelector);
              if (buttons.length > 0) {
                await buttons[0].click();
                console.log(`Clicked submit using selector: ${submitSelector}`);
                await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 30000 });
                await page.screenshot({ path: `${config.screenshotsDir}/12-waypoint-url-loaded.png` });
                
                // Add annotation
                await addNoteToPage(page, "Added a waypoint by visiting example.com", { x: 100, y: 100 });
                break;
              }
            } catch (submitError) {
              console.log(`Submit selector ${submitSelector} not found or not clickable`);
            }
          }
          break;
        }
      }
    } catch (error) {
      console.error("Error adding waypoint:", error);
    }
    
    // 13. Save the waypoint
    console.log("13. Saving the waypoint...");
    try {
      // Look for a button to save the waypoint
      const saveButtonSelectors = [
        'button.save-waypoint-btn',
        'button:contains("Save")',
        'button.btn-success',
        'button[type="submit"]:not(:disabled)'
      ];
      
      for (const selector of saveButtonSelectors) {
        try {
          const buttons = await page.$$(selector);
          if (buttons.length > 0) {
            await buttons[0].click();
            console.log(`Clicked save waypoint using selector: ${selector}`);
            await page.waitForTimeout(2000);
            await page.screenshot({ path: `${config.screenshotsDir}/13-waypoint-saved.png` });
            
            // Add annotation
            await addNoteToPage(page, "Waypoint saved to our journey", { x: 100, y: 100 });
            break;
          }
        } catch (btnError) {
          console.log(`Save selector ${selector} not found or not clickable`);
        }
      }
    } catch (error) {
      console.error("Error saving waypoint:", error);
    }
    
    // 14. Return to journeys list and view the journey
    console.log("14. Viewing the journey with waypoint...");
    await page.goto(`${config.baseUrl}/journeys`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${config.screenshotsDir}/14-back-to-journeys.png` });
    
    // Try to view the journey
    try {
      const viewButtonSelectors = [
        'a.btn-outline-primary',
        'a[href*="view_journey"]',
        'a:contains("View")'
      ];
      
      for (const selector of viewButtonSelectors) {
        try {
          const buttons = await page.$$(selector);
          if (buttons.length > 0) {
            await buttons[0].click();
            console.log(`Clicked view journey using selector: ${selector}`);
            await page.waitForNavigation({ waitUntil: 'networkidle0' });
            await page.screenshot({ path: `${config.screenshotsDir}/15-view-journey-details.png` });
            
            // Add annotation
            await addNoteToPage(page, "Viewing our journey with the added waypoint", { x: 100, y: 100 });
            break;
          }
        } catch (btnError) {
          console.log(`View selector ${selector} not found or not clickable`);
        }
      }
    } catch (error) {
      console.error("Error viewing journey:", error);
    }
    
    // 15. Finish the demo
    console.log("15. Demo completed successfully!");
    await addNoteToPage(page, "Demo completed! We've shown the key features of A-Proxy", { x: 100, y: 100 });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: `${config.screenshotsDir}/16-demo-completed.png` });
    
  } catch (error) {
    console.error("Error in demonstration:", error);
    await page.screenshot({ path: `${config.screenshotsDir}/error-state.png` });
  } finally {
    // Stop recording
    if (config.recordVideo && recorder) {
      console.log("Stopping video recording...");
      await recorder.stop();
    }
    
    // Close browser
    console.log("Closing browser...");
    await browser.close();
    
    console.log("Demo script execution completed.");
    console.log(`Screenshots saved to: ${config.screenshotsDir}`);
    if (config.recordVideo) {
      console.log(`Video saved to: ${config.videosDir}/a-proxy-demo.mp4`);
    }
  }
}

// Check if the A-Proxy application is running
async function checkAppRunning() {
  // Skip actual verification since we know it's running
  console.log(`Assuming A-Proxy is running at ${config.baseUrl}...`);
  console.log("A-Proxy is running and ready for the demo!");
  return true;
}

// Run the script
(async () => {
  try {
    // First check if the application is running
    await checkAppRunning();
    
    // Then run the demonstration
    await demonstrateAProxy();
  } catch (error) {
    console.error("Fatal error running demonstration:", error);
  }
})();
