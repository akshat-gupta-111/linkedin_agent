# LinkedIn Telemetry Scraper (LinkGent)

An autonomous, multi-agent web scraping pipeline designed to extract highly structured professional telemetry from LinkedIn profiles. This system bypasses standard anti-bot protections using browser fingerprinting, session cookie injection, and intelligent lazy-load scrolling.

---

## 🚀 1. Quick Start & Setup

### Prerequisites
* Python 3.8 or higher.
* Google Chrome or Microsoft Edge installed on your machine.

### Installation Commands
Run these commands in your terminal to set up the environment and install the necessary stealth browsers.

1. **Clone/Navigate to the repository:**
   ```bash
   cd path/to/linkgent

```

2. **Create and activate a virtual environment (Recommended):**
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

```


3. **Install Python dependencies:**
```bash
pip install -r requirements.txt

```


4. **Install Playwright Chromium binaries (CRITICAL):**
```bash
playwright install chromium

```



---

## 🔑 2. Authentication Bypass (The Cookie Setup)

LinkedIn aggressively blocks automated logins. We bypass this by injecting a live session cookie from a real browser. **Do not use your primary LinkedIn account for scraping.** Use a secondary/burner account.

### Step 1: Install the Cookie Extractor

1. Install the **EditThisCookie** extension from the Chrome Web Store.
2. Right-click the extension icon -> **Options**.
3. Ensure the **"Choose the preferred export format"** is set to **JSON**.

### Step 2: Export the Session

1. Open your normal browser and log into your burner LinkedIn account.
2. Go to the main LinkedIn feed.
3. Click the **EditThisCookie** extension icon in your toolbar.
4. Click the **Export** button (a rectangle with an arrow pointing out). Your cookies are now copied to your clipboard.
5. **DO NOT click "Sign Out" on LinkedIn.** Just close the tab. If you sign out, the cookie dies.

### Step 3: Save the Cookie File

1. In the root directory of this project, create a new file named exactly: `linkedin_cookies.json`
2. Paste your clipboard contents into this file and save it.

### Step 4: Prevent "Stolen Cookie" Logouts

LinkedIn checks if the browser running the script matches the browser that created the cookie.

1. Search Google for "What is my user agent" on your normal browser.
2. Copy the resulting string.
3. Open `browser_manager.py` and replace the `self.user_agent` string in the `__init__` function with your exact User-Agent.

---

## 🏃 3. Running the Scraper

To execute the pipeline, simply run the orchestrator.

```bash
python orchestrator.py

```

* **Note on Speed:** The script is intentionally throttled. It injects hard 10-second waits and uses a "stubborn scroll" to force LinkedIn's servers to return all historical data before extracting. A full profile scrape takes roughly 1.5 to 2.5 minutes.
* **Output:** Upon completion, the data will be saved as a highly structured JSON file named `raw_extracted_payload.json` in your root directory.

---

---

## 🧠 4. Architecture & Component Explanation

This project avoids massive, brittle scraping scripts by using a routing architecture. The codebase is split into three highly specialized files.

### `browser_manager.py` (The Stealth Engine)

Responsible for network survival and anti-bot evasion.

* **`init_browser()`:** Launches a headless Chromium instance stripped of the `navigator.webdriver` flag so LinkedIn views it as a human browser.
* **`inject_cookies()`:** Reads `linkedin_cookies.json`, sanitizes the `sameSite` and Chrome-specific metadata to prevent Playwright crashes, and injects the session into the browser context.
* **`smart_scroll()`:** A stubborn lazy-loading function. It scrolls the page, waits for network requests to resolve, and verifies height changes to ensure all dynamic chunks (like old posts or long certification lists) are loaded before giving up.

### `extractors.py` (The Precision Parsers)

Contains isolated functions that parse specific DOM elements. It intentionally avoids standard CSS classes (which LinkedIn changes weekly) in favor of structural anchors.

* **Omnivorous Text Regex:** Methods like `extract_network_metrics()` grab the text of the entire `<body>` and use regular expressions to hunt down follower counts, avoiding broken `div` chains.
* **Component Key Targeting:** Methods like `extract_skills()` target LinkedIn's immutable backend identifiers (e.g., `com.linkedin.sdui.profile.skill`) to perfectly isolate skills without accidentally scraping sidebars or footers.
* **Double-Failsafe Counters:** Methods like `extract_certifications_count()` count both the physical UI blocks and the regex date matches, returning the highest number to prevent false negatives.

### `orchestrator.py` (The Supervisor)

The brain of the operation. It acts as a routing agent.

* **State Management:** Keeps the Playwright context alive across multiple URL navigations so the injected cookies persist.
* **Targeted Routing:** Instead of clicking UI buttons (which triggers blocking modals), it directly appends paths like `/details/skills/` or `/recent-activity/all/` to the target's base URL.
* **JSON Compilation:** Triggers the respective methods in `extractors.py` and compiles the raw data into the final nested JSON payload required by the mathematical scoring engine.

```