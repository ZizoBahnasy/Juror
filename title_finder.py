#!/usr/bin/env python3
"""
US Code Title Finder
This script finds the most recent version of each US Code title.
"""

import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Constants
BASE_URL = "https://api.govinfo.gov"
COLLECTION_CODE = "USCODE"
RATE_LIMIT_DELAY = 0.1  # Delay between API calls in seconds
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def get_title_latest_version(title_number, start_year=2023, end_year=2018):
    """
    Find the most recent version of a US Code title by trying years in descending order.
    
    Args:
        title_number: The title number (1-54)
        start_year: The year to start searching from (default: 2023)
        end_year: The earliest year to try (default: 2018)
    
    Returns:
        The package ID of the most recent version, or None if not found
    """
    print(f"\nSearching for latest version of Title {title_number}...")
    
    for year in range(start_year, end_year - 1, -1):
        package_id = f"USCODE-{year}-title{title_number}"
        url = f"{BASE_URL}/packages/{package_id}/summary"
        params = {"api_key": API_KEY}
        
        print(f"  Trying {package_id}...")
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # If we get here, the package exists
            print(f"  Found: {package_id}")
            return package_id
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"  Not found: {package_id}")
            else:
                print(f"  Error checking {package_id}: {e}")
        
        time.sleep(RATE_LIMIT_DELAY)
    
    print(f"  No version found for Title {title_number} between {start_year} and {end_year}")
    return None

def get_package_summary(package_id):
    """Get summary for a specific package"""
    url = f"{BASE_URL}/packages/{package_id}/summary"
    params = {"api_key": API_KEY}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()

def main():
    """Main function to execute the program"""
    print("US Code Title Finder")
    print("===================")
    
    if not API_KEY:
        print("Error: API_KEY not found in .env file")
        return
    
    # Find the latest version of each title
    latest_titles = {}
    title_summaries = {}
    
    # US Code has titles 1-54
    for title_number in range(1, 55):
        package_id = get_title_latest_version(title_number)
        
        if package_id:
            latest_titles[title_number] = package_id
            
            # Get the package summary
            try:
                summary = get_package_summary(package_id)
                title_summaries[package_id] = summary
                print(f"Retrieved summary for {package_id}")
            except Exception as e:
                print(f"Error retrieving summary for {package_id}: {e}")
            
            time.sleep(RATE_LIMIT_DELAY)
    
    # Save results
    with open(OUTPUT_DIR / "latest_titles.json", "w") as f:
        json.dump(latest_titles, f, indent=2)
    
    with open(OUTPUT_DIR / "title_summaries.json", "w") as f:
        json.dump(title_summaries, f, indent=2)
    
    print(f"\nFound latest versions for {len(latest_titles)} titles")
    print(f"Results saved to {OUTPUT_DIR / 'latest_titles.json'} and {OUTPUT_DIR / 'title_summaries.json'}")

if __name__ == "__main__":
    main()