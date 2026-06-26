import sys
import json
from engine import tool

def main():
    # 1. Grab the username from the command line
    if len(sys.argv) < 2:
        print("Usage: python test_run.py <username>")
        sys.exit(1)

    target_username = sys.argv[1]
    filepath = "raw_extracted_payload.json"

    # 2. Load the scraped JSON payload
    try:
        with open(filepath, "r") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"[-] Error: Could not find '{filepath}'.")
        print("    Please run 'python orchestrator.py' to generate the data first.")
        sys.exit(1)

    # Quick check to ensure the payload matches the target
    scraped_user = raw_data.get("profile", {}).get("username", "")
    if scraped_user != target_username:
        print(f"[*] Warning: The scraped data in {filepath} belongs to '{scraped_user}', not '{target_username}'. Executing anyway...\n")

    # 3. Execute the Math Engine (using default constants)
    print(f"[*] Booting Math Engine for {target_username}...")
    final_payload = tool.compile_linkedin_payload(raw_data)

    # 4. Print the exact JSON structure the frontend will receive
    print("\n" + "="*50)
    print(" 🚀 FINAL SCORED PAYLOAD ")
    print("="*50)
    print(json.dumps(final_payload, indent=4))
    print("="*50 + "\n")
    
    print(f"[+] Engine execution complete. Final Score: {final_payload['hard_metrics']['final_score']}/100")

if __name__ == "__main__":
    main()