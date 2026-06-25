import re
from typing import Dict, List, Any
from playwright.async_api import Page

class LinkedInExtractors:
    """
    Surgical extraction methods utilizing aria-labels, component keys, and 
    omnivorous regex to survive LinkedIn's heavily obfuscated DOM.
    """

    @staticmethod
    async def extract_network_metrics(page: Page) -> Dict[str, int]:
        metrics = {"followers": 0, "connections": 0}
        try:
            # Wait for the profile top card, or just default to the body
            await page.wait_for_selector("body", timeout=15000)
            
            # Grab all text on the entire page to ensure we don't miss the header
            body_text = await page.locator("body").inner_text()
            
            followers_match = re.search(r'([\d,]+)\s*followers', body_text, re.IGNORECASE)
            if followers_match:
                metrics["followers"] = int(followers_match.group(1).replace(',', ''))
                
            connections_match = re.search(r'([\d,]+)\+?\s*connections', body_text, re.IGNORECASE)
            if connections_match:
                metrics["connections"] = int(connections_match.group(1).replace(',', ''))
        except Exception as e:
            print(f"[-] Warning: Network metrics extraction failed. {e}")
            
        return metrics
    @staticmethod
    async def extract_optimization_flags(page: Page) -> Dict[str, bool]:
        flags = {
            "has_about_section": False,
            "has_banner_image": False,
            "has_featured_section": False,
            "has_custom_url": False,
            "has_education": False
        }
        
        try:
            # Weaponizing Screenshot 1: Target accessibility labels instead of CSS
            banner = await page.locator("img[alt='Cover photo'], svg[aria-label='Cover photo']").count()
            flags["has_banner_image"] = banner > 0

            flags["has_about_section"] = await page.locator("h2:has-text('About'), #about").count() > 0
            flags["has_featured_section"] = await page.locator("h2:has-text('Featured'), #featured").count() > 0
            flags["has_education"] = await page.locator("h2:has-text('Education'), #education").count() > 0

            current_url = page.url
            if not re.search(r'-[a-z0-9]{8,10}/?$', current_url):
                flags["has_custom_url"] = True

        except Exception as e:
            print(f"[-] Warning: Error checking optimization flags: {e}")
            
        return flags

    @staticmethod
    async def extract_recent_posts(page: Page, max_posts: int = 50) -> List[Dict[str, Any]]:
        posts_data = []
        try:
            await page.wait_for_selector("div[data-urn^='urn:li:activity:']", timeout=15000)
            post_elements = await page.locator("div[data-urn^='urn:li:activity:']").all()
            
            for post in post_elements[:max_posts]:
                post_info = {"timestamp_text": "", "likes": 0, "comments": 0, "reposts": 0}
                
                post_html = await post.inner_html()
                post_text = await post.inner_text()

                time_match = re.search(r'\b(\d+[hdwmy][o]?[r]?)\b', post_text, re.IGNORECASE)
                if time_match:
                    post_info["timestamp_text"] = time_match.group(1)

                likes_match = re.search(r'([\d,]+)\s*(?:reactions|likes)', post_html, re.IGNORECASE)
                if likes_match:
                    post_info["likes"] = int(likes_match.group(1).replace(',', ''))
                    
                comments_match = re.search(r'([\d,]+)\s*comment', post_html, re.IGNORECASE)
                if comments_match:
                    post_info["comments"] = int(comments_match.group(1).replace(',', ''))

                reposts_match = re.search(r'([\d,]+)\s*repost', post_html, re.IGNORECASE)
                if reposts_match:
                    post_info["reposts"] = int(reposts_match.group(1).replace(',', ''))

                posts_data.append(post_info)
        except Exception as e:
             print(f"[-] Warning: Feed extraction failed: {e}")
             
        return posts_data

    @staticmethod
    async def extract_skills(page: Page) -> Dict[str, int]:
        skills_dict = {}
        try:
            await page.wait_for_selector("main", timeout=10000)
            
            skill_blocks = await page.locator("div[componentkey^='com.linkedin.sdui.profile.skill']").all()
            
            if skill_blocks:
                for block in skill_blocks:
                    text = await block.inner_text()
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    if lines:
                        skill_name = lines[0] 
                        
                        # Weaponizing Screenshot: Look explicitly for the link containing "/endorsers/"
                        endorser_link = block.locator("a[href*='/endorsers/']")
                        
                        if await endorser_link.count() > 0:
                            endorse_text = await endorser_link.first.inner_text()
                            match = re.search(r'([\d,]+)', endorse_text)
                            count = int(match.group(1).replace(',', '')) if match else 0
                        else:
                            # Fallback just in case
                            endorse_match = re.search(r'([\d,]+)\s*endorsement', text, re.IGNORECASE)
                            count = int(endorse_match.group(1).replace(',', '')) if endorse_match else 0
                            
                        skills_dict[skill_name] = count
            else:
                print("[-] Warning: SDUI component keys not found on skills page.")

        except Exception as e:
            print(f"[-] Warning: Skill extraction failed. {e}")
            
        return skills_dict
    
    @staticmethod
    async def extract_experience_count(page: Page) -> int:
        try:
            await page.wait_for_selector("main", timeout=10000)
            main_text = await page.locator("main").first.inner_text()
            
            # Count 1: Regex Date Match
            date_range_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec\s+\d{4}|Present)'
            regex_count = len(re.findall(date_range_pattern, main_text, re.IGNORECASE))
            
            # Count 2: Physical DOM Elements
            # Looks for the top-level list items to avoid counting nested skills
            ui_count = await page.locator("main > section > div > div > ul > li.pvs-list__paged-list-item").count()
            
            # Return whichever is more accurate
            return max(regex_count, ui_count)
        except Exception:
            return 0
        
    @staticmethod
    async def extract_certifications_count(page: Page) -> int:
        try:
            await page.wait_for_selector("main", timeout=10000)
            main_text = await page.locator("main").first.inner_text()
            
            # Count 1: Regex "Issued" Match
            regex_count = len(re.findall(r'Issued\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}', main_text, re.IGNORECASE))
            
            # Count 2: Physical DOM Elements
            ui_count = await page.locator("main > section > div > div > ul > li.pvs-list__paged-list-item").count()
            
            return max(regex_count, ui_count)
        except Exception:
            return 0

    @staticmethod
    async def extract_recommendations(page: Page) -> Dict[str, int]:
        recs = {"received": 0, "given": 0}
        try:
            await page.wait_for_selector("main", timeout=10000)
            main_text = await page.locator("main").first.inner_text()
            
            received_match = re.search(r'Received\s*\(?([\d,]+)\)?', main_text, re.IGNORECASE)
            if received_match:
                recs["received"] = int(received_match.group(1).replace(',', ''))
                
            given_match = re.search(r'Given\s*\(?([\d,]+)\)?', main_text, re.IGNORECASE)
            if given_match:
                recs["given"] = int(given_match.group(1).replace(',', ''))
        except Exception as e:
            print(f"[-] Warning: Recommendations extraction failed: {e}")
            
        return recs