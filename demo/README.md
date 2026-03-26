# A-Proxy Demonstration Script

Automated Playwright scripts that demonstrate key features of A-Proxy, capturing screenshots and video.

## Features Demonstrated

1. Login and dashboard
2. Persona list and selection
3. Journey creation and management
4. Waypoint navigation

## Prerequisites

- Python 3.10+ with A-Proxy dependencies installed (`pip install -r requirements.txt`)
- Playwright Chromium browser (`python -m playwright install chromium`)
- A-Proxy running at http://localhost:5002

## Quick Start

```bash
cd demo
./run-demo.sh
```

The script will:

1. Check if A-Proxy is running
2. Run the demo (opens a visible browser window)
3. Save screenshots to `./screenshots/`
4. Save video to `./videos/`
5. Optionally generate a PDF report

## Manual Usage

### Run the demo

```bash
python demo_script.py
```

### Generate PDF report from screenshots

```bash
python create_pdf_report.py
```

## Output

| Output | Location |
|--------|----------|
| Screenshots | `./screenshots/*.png` |
| Video | `./videos/` |
| PDF report | `./A-Proxy-Demo-Report.pdf` |

## Configuration

Edit the `CONFIG` dict at the top of `demo_script.py`:

- `base_url` — where A-Proxy is running (default: `http://localhost:5002`)
- `viewport` — browser window dimensions
- `record_video` — enable/disable video recording
- `slow_mo` — delay between actions in milliseconds
- `wait_time` — pause after page loads in milliseconds
