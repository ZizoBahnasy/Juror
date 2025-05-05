#!/usr/bin/env python3
"""
US Code Hierarchy Builder (v3)

Fetches all granules for each US Code title and builds a flat hierarchy JSON.
Completely structure-agnostic: does not enforce specific nesting beyond grouping by title.
Gracefully handles missing API key and HTTP errors per title.
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (expects API_KEY in .env or environment)
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("Error: API_KEY is not set. Please configure your GOVINFO API key in .env or environment.")
    exit(1)

# Constants
BASE_URL = "https://api.govinfo.gov"
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
TITLE_SUMMARIES_FILE = OUTPUT_DIR / "title_summaries.json"
HIERARCHY_FILE = OUTPUT_DIR / "uscode_hierarchy.json"
PAGE_SIZE = 1000       # Number of granules per API page
RATE_LIMIT_DELAY = 0.1 # Seconds between API calls to avoid throttling


def load_title_summaries():
    """
    Load the pre-fetched title summaries JSON.
    Expects a mapping of package_id to summary metadata.
    """
    if not TITLE_SUMMARIES_FILE.exists():
        print(f"Error: {TITLE_SUMMARIES_FILE} not found. Run title_finder.py first.")
        return {}
    return json.loads(TITLE_SUMMARIES_FILE.read_text())


def fetch_all_granules(package_id):
    """
    Fetch every granule for a given package_id via paginated API calls.
    Appends the API key to each request URL.
    Returns a list of granule dicts; on error, returns what was collected so far.
    Also prints the total fetched vs API-reported count.
    """
    url = f"{BASE_URL}/packages/{package_id}/granules?offsetMark=*&pageSize={PAGE_SIZE}"
    all_granules = []
    reported_count = None

    while url:
        sep = '&' if '?' in url else '?'
        request_url = f"{url}{sep}api_key={API_KEY}"

        try:
            resp = requests.get(request_url)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"Warning: HTTP error for {package_id}: {e}")
            break
        except Exception as e:
            print(f"Warning: unexpected error for {package_id}: {e}")
            break

        # Capture the API-reported total on the first page
        if reported_count is None:
            reported_count = data.get("count")

        # Extend list and prepare next page
        all_granules.extend(data.get("granules", []))
        url = data.get("nextPage")
        time.sleep(RATE_LIMIT_DELAY)

    # Report fetched vs API count
    print(f"Fetched {len(all_granules)} total granules for {package_id}, API reported {reported_count}")
    return all_granules


def build_hierarchy():
    """
    Constructs a fresh hierarchy JSON by iterating over all titles:
      1. Reads title_summaries.json
      2. For each title, fetches granules via API (fetch_all_granules)
      3. Assembles a list of titles, each containing its flat list of granules
      4. Writes the complete hierarchy to uscode_hierarchy.json
    """
    summaries = load_title_summaries()
    if not summaries:
        return

    hierarchy = {
        "collectionName": "United States Code",
        "collectionCode": "USCODE",
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "titles": []
    }

    for pkg_id, summary in summaries.items():
        tnum = summary.get("titleNumber")
        print(f"Processing Title {tnum} (package: {pkg_id})...")

        # Basic title metadata
        entry = {
            "packageId": pkg_id,
            "titleNumber": tnum,
            "title": summary.get("title"),
            "dateIssued": summary.get("dateIssued"),
            "totalPages": int(summary.get("pages", 0)),
        }

        # Fetch granules; safe even if there's an HTTP error
        granules = fetch_all_granules(pkg_id)
        
        if not granules:
            print(f"  Warning: no granules found or failed for {pkg_id}")

        # Rename 'title' -> 'granuleTitle' in each granule for clarity
        for g in granules:
            if "title" in g:
                g["granuleTitle"] = g.pop("title")

        entry["granules"] = granules
        hierarchy["titles"].append(entry)

    # Save final hierarchy to file
    HIERARCHY_FILE.write_text(json.dumps(hierarchy, indent=2))
    print(f"Hierarchy saved to {HIERARCHY_FILE}")


if __name__ == "__main__":
    build_hierarchy()
