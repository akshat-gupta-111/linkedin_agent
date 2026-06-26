import json
import random
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, BrowserContext, Page, Playwright
import re
class LinkedInBrowserManager:
    """
    Handles stealth browser initialization, cookie injection, and human-like navigation 
    to bypass LinkedIn's basic anti-bot detection.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        
        # REPLACE THIS STRING with your exact User-Agent from Google
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"

    async def init_browser(self, p: Playwright) -> BrowserContext:
        """Launches the browser with stealth configurations."""
        browser = await p.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"] 
        )
        
        context = await browser.new_context(
            user_agent=self.user_agent, # We now use the static, matching User-Agent
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        return context

    # async def init_browser(self, p: Playwright) -> BrowserContext:
    #     """Launches the browser with stealth configurations."""
    #     browser = await p.chromium.launch(
    #         headless=self.headless,
    #         args=["--disable-blink-features=AutomationControlled"] # Hides webdriver flag
    #     )
        
    #     context = await browser.new_context(
    #         user_agent=random.choice(self.user_agents),
    #         viewport={"width": 1920, "height": 1080},
    #         device_scale_factor=1,
    #         has_touch=False,
    #         is_mobile=False
    #     )
        
    #     # Inject standard human-like navigator properties
    #     await context.add_init_script("""
    #         Object.defineProperty(navigator, 'webdriver', {
    #             get: () => undefined
    #         });
    #     """)
        
    #     return context

    async def smart_scroll(self, page: Page, max_scrolls: int = 15, wait_time: float = 4.0):
        """
        Universal Element-Aware Scroll: Uses native keyboard interactions and 
        combines DOM element counting with Regex text-parsing to verify lazy-loading.
        """
        print(f"[*] Initiating Element-Aware Smart Scroll...")
        
        previous_item_count = 0
        empty_scrolls = 0
        max_empty_scrolls = 2 

        for i in range(max_scrolls):
            try:
                # Safely focus the page without accidentally clicking hyperlinks.
                await page.focus("body")
                await page.mouse.click(10, 300) # Safe click in the top-left margin
            except Exception:
                pass
            
            # Simulate a human aggressively hitting the 'End' key
            await page.keyboard.press("End")
            await asyncio.sleep(1.0)
            
            # Jiggle the scroll to trigger stubborn event listeners
            await page.keyboard.press("PageUp")
            await asyncio.sleep(0.5)
            await page.keyboard.press("End")

            # Wait for the LinkedIn servers to return the data chunk
            await asyncio.sleep(wait_time)

            # --- THE HYBRID COUNTER LOGIC ---
            
            # 1. Count standard UI elements (Works perfectly for Posts and Skills)
            ui_count = await page.locator(
                "main section ul > li, " # The brute-force catch-all for lists
                "div[data-urn^='urn:li:activity:'], " # Catches posts
                "div[componentkey^='com.linkedin.sdui.profile.skill']" # Catches skills
            ).count()

            # 2. Extract raw text for Regex parsing (Bypasses CSS obfuscation for Exp/Certs)
            main_text = ""
            try:
                main_text = await page.locator("main").first.inner_text()
            except Exception:
                pass
                
            # Regex for Experience dates (e.g., "Jan 2020 - Present")
            exp_matches = len(re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec\s+\d{4}|Present)', main_text, re.IGNORECASE))
            
            # Regex for Certifications (e.g., "Issued May 2026")
            cert_matches = len(re.findall(r'Issued\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}', main_text, re.IGNORECASE))

            # The current count is whichever metric found the most items on the screen
            current_item_count = max(ui_count, exp_matches, cert_matches)
            
            # --------------------------------
            
            if current_item_count == previous_item_count:
                empty_scrolls += 1
                print(f"[*] No new items detected. Stubborn wait {empty_scrolls}/{max_empty_scrolls}...")
                
                if empty_scrolls >= max_empty_scrolls:
                    print(f"[*] Reached absolute bottom. Total items loaded: {current_item_count}")
                    break
            else:
                empty_scrolls = 0
                previous_item_count = current_item_count
                print(f"[*] Chunk loaded successfully. Total items visible: {current_item_count}")

                
    async def inject_cookies(self, context: BrowserContext, cookie_filepath: str | None = None) -> bool:
        """
        Loads exported session cookies to bypass the login wall.
        Sanitizes the cookie dictionary to match Playwright's strict schema.
        """
        try:
            if cookie_filepath is None:
                cookie_filepath = str(Path(__file__).resolve().parents[1] / "linkedin_cookies.json")

            with open(cookie_filepath, 'r') as file:
                raw_cookies = json.load(file)
            
            cleaned_cookies = []
            for cookie in raw_cookies:
                # 1. Fix SameSite enum formatting
                if 'sameSite' in cookie:
                    val = cookie['sameSite'].lower()
                    if val in ['no_restriction', 'none']:
                        cookie['sameSite'] = 'None'
                    elif val == 'lax':
                        cookie['sameSite'] = 'Lax'
                    elif val == 'strict':
                        cookie['sameSite'] = 'Strict'
                    else:
                        # Playwright prefers the key completely missing over an invalid string like 'unspecified'
                        del cookie['sameSite']

                # 2. Remove Chrome-specific keys that Playwright rejects
                for invalid_key in ['hostOnly', 'session', 'storeId', 'id']:
                    cookie.pop(invalid_key, None)

                # 3. Map EditThisCookie's 'expirationDate' to Playwright's 'expires'
                if 'expirationDate' in cookie:
                    cookie['expires'] = cookie.pop('expirationDate')

                cleaned_cookies.append(cookie)

            await context.add_cookies(cleaned_cookies)
            print("[+] Session cookies injected and sanitized successfully.")
            return True
            
        except FileNotFoundError:
            print(f"[-] ERROR: Cookie file '{cookie_filepath}' not found.")
            print("    Please log into LinkedIn manually, export cookies to JSON, and place them in the root directory.")
            return False
        except Exception as e:
            print(f"[-] ERROR injecting cookies: {e}")
            return False
        

    async def human_delay(self, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """Randomized delay to simulate human reading/processing time."""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def scroll_to_bottom(self, page: Page, max_scrolls: int = 5):
        """Simulates human scrolling to trigger lazy-loaded elements (like old posts)."""
        print(f"[*] Scrolling page to trigger lazy-loading...")
        for i in range(max_scrolls):
            # Scroll down by a random viewport percentage
            scroll_amount = random.randint(600, 1000)
            await page.mouse.wheel(0, scroll_amount)
            await self.human_delay(1.5, 3.0)