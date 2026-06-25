import asyncio
import json
from playwright.async_api import async_playwright
from browser_manager import LinkedInBrowserManager
from extractors import LinkedInExtractors

class LinkedInScraperSupervisor:
    """
    The orchestrator that manages the browser lifecycle, routes to specific 
    profile sub-directories, triggers extractors, and compiles the final payload.
    """
    def __init__(self, target_username: str, headless: bool = True):
        self.target_username = target_username.strip("/")
        self.base_url = f"https://www.linkedin.com/in/{self.target_username}"
        self.manager = LinkedInBrowserManager(headless=headless)
        self.extractors = LinkedInExtractors()

    async def execute_pipeline(self) -> dict:
        print(f"[*] Initializing pipeline for target: {self.target_username}")
        
        final_payload = {
            "profile": {"username": self.target_username},
            "network": {},
            "optimization": {},
            "recent_posts": [],
            "skills": {},
            "experience_count": 0,
            "certifications_count": 0,
            "recommendations": {"received": 0, "given": 0}
        }

        async with async_playwright() as p:
            context = await self.manager.init_browser(p)
            
            success = await self.manager.inject_cookies(context)
            if not success:
                print("[-] Aborting pipeline due to missing cookies.")
                return final_payload

            page = await context.new_page()

            try:
                # 1. Main Profile
                print(f"[*] Extracting Main Profile: {self.base_url}")
                await page.goto(self.base_url, wait_until="domcontentloaded")
                print("[*] Waiting 10 seconds for profile to render...")
                await page.wait_for_timeout(10000) # Hard 10 second wait
                
                final_payload["network"] = await self.extractors.extract_network_metrics(page)
                final_payload["optimization"] = await self.extractors.extract_optimization_flags(page)

                # 2. Activity Feed
                activity_url = f"{self.base_url}/recent-activity/all/"
                print(f"[*] Extracting Feed: {activity_url}")
                await page.goto(activity_url, wait_until="domcontentloaded")
                print("[*] Waiting 10 seconds for feed to render...")
                await page.wait_for_timeout(10000) 
                
                await self.manager.smart_scroll(page, max_scrolls=20, wait_time=4.0) 
                final_payload["recent_posts"] = await self.extractors.extract_recent_posts(page, max_posts=100)

                # ... (inside execute_pipeline) ...

                # 3. Skills Page
                skills_url = f"{self.base_url}/details/skills/"
                print(f"[*] Extracting Skills: {skills_url}")
                await page.goto(skills_url, wait_until="domcontentloaded")
                if "details/skills" in page.url:
                    print("[*] Waiting 10 seconds for skills to render...")
                    await page.wait_for_timeout(10000)
                    # MASSIVE WAIT TIME APPLIED HERE
                    await self.manager.smart_scroll(page, max_scrolls=15, wait_time=6.0)
                    final_payload["skills"] = await self.extractors.extract_skills(page)

                # 4. Experience Page
                exp_url = f"{self.base_url}/details/experience/"
                print(f"[*] Extracting Experience: {exp_url}")
                await page.goto(exp_url, wait_until="domcontentloaded")
                if "details/experience" in page.url:
                    print("[*] Waiting 10 seconds for experience to render...")
                    await page.wait_for_timeout(10000)
                    await self.manager.smart_scroll(page, max_scrolls=5, wait_time=4.0)
                    final_payload["experience_count"] = await self.extractors.extract_experience_count(page)

                # 5. Certifications Page
                cert_url = f"{self.base_url}/details/certifications/"
                print(f"[*] Extracting Certifications: {cert_url}")
                await page.goto(cert_url, wait_until="domcontentloaded")
                if "details/certifications" in page.url:
                    print("[*] Waiting 10 seconds for certifications to render...")
                    await page.wait_for_timeout(10000)
                    # MASSIVE WAIT TIME APPLIED HERE
                    await self.manager.smart_scroll(page, max_scrolls=15, wait_time=6.0)
                    final_payload["certifications_count"] = await self.extractors.extract_certifications_count(page)

                # ... (rest of the code) ...
                # 6. Recommendations Page
                rec_url = f"{self.base_url}/details/recommendations/"
                print(f"[*] Extracting Recommendations: {rec_url}")
                await page.goto(rec_url, wait_until="domcontentloaded")
                if "details/recommendations" in page.url:
                    print("[*] Waiting 10 seconds for recommendations to render...")
                    await page.wait_for_timeout(10000)
                    final_payload["recommendations"] = await self.extractors.extract_recommendations(page)

            except Exception as e:
                print(f"[-] Critical pipeline failure: {e}")


            finally:
                await context.close()
                print("[+] Pipeline execution complete. Browser context closed.")

        return final_payload

if __name__ == "__main__":
    TARGET = "akshat-gupta-88b129325" 
    supervisor = LinkedInScraperSupervisor(target_username=TARGET, headless=False)
    result_data = asyncio.run(supervisor.execute_pipeline())
    
    with open("raw_extracted_payload.json", "w") as f:
        json.dump(result_data, f, indent=4)
        
    print("[+] Payload saved to raw_extracted_payload.json")