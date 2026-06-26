import re

def bucket_posts_by_month(posts: list) -> dict:
    """
    Translates LinkedIn's relative timestamp strings (e.g., '3w', '1mo') 
    into a trailing 12-month numerical bucket system.
    """
    # Initialize a trailing 12-month timeline with 0 posts
    monthly_counts = {f"month_{i}": 0 for i in range(1, 13)}
    
    if not posts:
        return monthly_counts

    for post in posts:
        time_str = post.get("timestamp_text", "").lower()
        if not time_str:
            continue
            
        # Hours, Days, and Weeks all fall into the current month (Month 1)
        if any(indicator in time_str for indicator in ['h', 'd', 'w']):
            monthly_counts["month_1"] += 1
            
        # Months (e.g., "4mo", "11mo")
        elif 'mo' in time_str:
            match = re.search(r'(\d+)', time_str)
            if match:
                month_idx = int(match.group(1))
                if 1 <= month_idx <= 12:
                    monthly_counts[f"month_{month_idx}"] += 1
                    
        # Years (e.g., "1yr"). Anything 1 year or older gets dumped into the final bucket 
        # or discarded depending on how strict you want the trailing 12-month window to be.
        elif 'yr' in time_str:
             monthly_counts["month_12"] += 1
             
    return monthly_counts