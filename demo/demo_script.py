"""
A-Proxy Feature Demonstration Script (Playwright)

Demonstrates key features:
1. Dashboard and geolocation selection
2. Persona selection and usage
3. Journey creation and management
4. Adding waypoints to a journey
"""
import os
import sys
from playwright.sync_api import sync_playwright

# Configuration
CONFIG = {
    "base_url": "http://localhost:5002",
    "screenshots_dir": "./screenshots",
    "videos_dir": "./videos",
    "viewport": {"width": 1280, "height": 800},
    "record_video": True,
    "slow_mo": 100,
    "wait_time": 1000,
}


def ensure_dirs():
    os.makedirs(CONFIG["screenshots_dir"], exist_ok=True)
    os.makedirs(CONFIG["videos_dir"], exist_ok=True)


def screenshot(page, name):
    path = os.path.join(CONFIG["screenshots_dir"], f"{name}.png")
    page.screenshot(path=path, full_page=True)
    print(f"  Screenshot: {path}")


def demonstrate_a_proxy():
    ensure_dirs()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=CONFIG["slow_mo"])

        context_options = {"viewport": CONFIG["viewport"]}
        if CONFIG["record_video"]:
            context_options["record_video_dir"] = CONFIG["videos_dir"]
            context_options["record_video_size"] = CONFIG["viewport"]

        context = browser.new_context(**context_options)
        page = context.new_page()

        try:
            # 1. Home page
            print("1. Navigating to home page...")
            page.goto(f"{CONFIG['base_url']}/")
            page.wait_for_timeout(CONFIG["wait_time"])
            screenshot(page, "01-home-page")

            # 2. Login if needed
            print("2. Logging in...")
            if page.url.endswith("/login") or "/login" in page.url:
                page.fill('input[name="email"]', "admin@example.com")
                page.fill('input[name="password"]', "password")
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle")
                screenshot(page, "02-logged-in")

            # 3. Dashboard
            print("3. Navigating to persona dashboard...")
            page.goto(f"{CONFIG['base_url']}/persona/dashboard")
            page.wait_for_timeout(2000)
            screenshot(page, "03-dashboard")

            # 4. Personas page
            print("4. Navigating to personas page...")
            page.goto(f"{CONFIG['base_url']}/personas")
            page.wait_for_timeout(2000)
            screenshot(page, "04-personas-list")

            # 5. Select a persona (click first "Use" link)
            print("5. Selecting a persona...")
            use_buttons = page.locator('a.btn-outline-secondary, a[href*="use-persona"]')
            if use_buttons.count() > 0:
                use_buttons.first.click()
                page.wait_for_load_state("networkidle")
                screenshot(page, "05-selected-persona")

            # 6. Journeys page
            print("6. Navigating to journeys page...")
            page.goto(f"{CONFIG['base_url']}/journeys")
            page.wait_for_timeout(2000)
            screenshot(page, "06-journeys-list")

            # 7. Create a journey
            print("7. Creating a new journey...")
            page.goto(f"{CONFIG['base_url']}/journey/create")
            page.wait_for_timeout(1000)
            page.fill("#name", "Demo Journey")
            page.fill("#description", "A demonstration journey for the feature showcase")

            # Select journey type if dropdown exists
            journey_type = page.locator("#journey_type")
            if journey_type.count() > 0:
                journey_type.select_option("research")

            # Select a persona if dropdown exists
            persona_select = page.locator("#persona_id")
            if persona_select.count() > 0:
                options = persona_select.locator("option")
                if options.count() > 1:
                    value = options.nth(1).get_attribute("value")
                    persona_select.select_option(value)

            screenshot(page, "07-filled-journey-form")

            # 8. Submit
            print("8. Submitting journey form...")
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            screenshot(page, "08-journey-created")

            # 9. Back to journeys
            print("9. Viewing journeys list...")
            page.goto(f"{CONFIG['base_url']}/journeys")
            page.wait_for_timeout(2000)
            screenshot(page, "09-journeys-with-new")

            print("Demo completed successfully!")
            screenshot(page, "10-demo-completed")

        except Exception as e:
            print(f"Error during demo: {e}")
            screenshot(page, "error-state")
        finally:
            context.close()
            browser.close()

    print(f"Screenshots saved to: {CONFIG['screenshots_dir']}")
    if CONFIG["record_video"]:
        print(f"Video saved to: {CONFIG['videos_dir']}")


if __name__ == "__main__":
    demonstrate_a_proxy()
