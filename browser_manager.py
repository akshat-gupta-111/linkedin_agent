import json
import random
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, BrowserContext, Page, Playwright

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
        Intelligently scrolls, utilizing a 'Stubborn Retry' loop to wait out 
        slow network requests from LinkedIn's servers.
        """
        print(f"[*] Initiating smart scroll (waiting {wait_time}s between chunks)...")
        previous_height = await page.evaluate("document.body.scrollHeight")
        
        empty_scrolls = 0
        max_empty_scrolls = 3 # Will wait out 3 consecutive failures

        for i in range(max_scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(wait_time)
            
            new_height = await page.evaluate("document.body.scrollHeight")
            
            if new_height == previous_height:
                empty_scrolls += 1
                print(f"[*] Chunk delayed. Stubborn wait {empty_scrolls}/{max_empty_scrolls}...")
                
                # Jiggle the scroll to force event listeners
                await page.evaluate("window.scrollBy(0, -500)")
                await asyncio.sleep(1.0)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # Add an extra penalty wait for slow servers
                await asyncio.sleep(wait_time + 2.0) 
                
                if empty_scrolls >= max_empty_scrolls:
                    print(f"[*] Reached absolute bottom after {i+1} total scrolls.")
                    break
            else:
                empty_scrolls = 0 # Reset the counter if we got new data!
                previous_height = new_height

                
    async def inject_cookies(self, context: BrowserContext, cookie_filepath: str = "linkedin_cookies.json") -> bool:
        """
        Loads exported session cookies to bypass the login wall.
        Sanitizes the cookie dictionary to match Playwright's strict schema.
        """
        try:
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