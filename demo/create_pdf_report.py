"""
Generate a PDF report from demo screenshots using Playwright.

Replaces the Puppeteer-based create-pdf-report.js.
"""
import os
import glob
from datetime import datetime
from playwright.sync_api import sync_playwright


def create_report(screenshots_dir="./screenshots", output_path="A-Proxy-Demo-Report.pdf"):
    """Generate a PDF report from screenshots in the given directory."""
    screenshots = sorted(glob.glob(os.path.join(screenshots_dir, "*.png")))

    if not screenshots:
        print("No screenshots found. Run demo_script.py first.")
        return

    # Build HTML report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    images_html = ""
    for i, path in enumerate(screenshots):
        name = os.path.splitext(os.path.basename(path))[0]
        label = name.replace("-", " ").replace("_", " ").title()
        abs_path = os.path.abspath(path).replace("\\", "/")
        images_html += f"""
        <div class="screenshot">
            <h2>{i + 1}. {label}</h2>
            <img src="file:///{abs_path}" />
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #1a1a2e; border-bottom: 2px solid #16213e; padding-bottom: 10px; }}
        .meta {{ color: #666; margin-bottom: 30px; }}
        .screenshot {{ page-break-inside: avoid; margin-bottom: 30px; }}
        .screenshot h2 {{ color: #16213e; font-size: 16px; margin-bottom: 10px; }}
        .screenshot img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>A-Proxy Feature Demonstration Report</h1>
    <p class="meta">Generated: {timestamp}</p>
    <p>This report documents the key features of A-Proxy as captured during an automated demonstration run.</p>
    {images_html}
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(path=output_path, format="A4", margin={"top": "20mm", "bottom": "20mm"})
        browser.close()

    print(f"PDF report saved to: {output_path}")


if __name__ == "__main__":
    create_report()
