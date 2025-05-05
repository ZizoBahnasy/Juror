#!/usr/bin/env python3
"""
Check if the GovInfo API provides the total number of granules in its response.
Also sums granules across all US Code titles.
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
# Update path to reference parent directory's outputs folder
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def get_package_granules(package_id, page_size=100, offset_mark="*"):
    """Get granules for a specific package with pagination"""
    url = f"{BASE_URL}/packages/{package_id}/granules"
    params = {
        "api_key": API_KEY,
        "pageSize": page_size,
        "offsetMark": offset_mark
    }
    
    print(f"Making API request to: {url}")
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()

def check_single_title():
    """Check granule count for a single title"""
    print("Checking if API provides granule count")
    print("=====================================")
    
    # Load the latest titles to get a package ID
    try:
        with open(OUTPUT_DIR / "latest_titles.json", "r") as f:
            latest_titles = json.load(f)
            # Get the first package ID
            package_id = 'USCODE-2023-title7'
            print(f"Using package ID: {package_id}")
    except (FileNotFoundError, StopIteration):
        print("Could not find latest_titles.json or it's empty.")
        package_id = input("Please enter a package ID (e.g., USCODE-2023-title1): ")
    
    # Get granules for this package
    try:
        granules_data = get_package_granules(package_id, page_size=10)
        
        # Save the full response to a file for inspection
        with open(OUTPUT_DIR / "granules_response.json", "w") as f:
            json.dump(granules_data, f, indent=2)
        
        print(f"\nFull response saved to {OUTPUT_DIR / 'granules_response.json'}")
        
        # Check if the response contains a count or total field
        print("\nChecking for count or total fields in the response:")
        for key in granules_data.keys():
            print(f"  - {key}: {type(granules_data[key])}")
        
        # Check if count exists
        if "count" in granules_data:
            print(f"\nFound 'count' field: {granules_data['count']}")
        
        # Check if total exists
        if "total" in granules_data:
            print(f"\nFound 'total' field: {granules_data['total']}")
        
        # Print the number of granules in this page
        granules = granules_data.get("granules", [])
        print(f"\nNumber of granules in this page: {len(granules)}")
        
        # Check if there's a next page
        next_page = granules_data.get("nextPage")
        if next_page:
            print(f"\nThere is a next page: {next_page}")
        else:
            print("\nNo next page found - this might be the only page")
        
    except Exception as e:
        print(f"Error getting granules: {e}")

def sum_all_granules():
    """Sum the total number of granules across all US Code titles"""
    print("\nSumming granules across all US Code titles")
    print("=========================================")
    
    # Load the latest titles
    try:
        with open(OUTPUT_DIR / "latest_titles.json", "r") as f:
            latest_titles = json.load(f)
    except FileNotFoundError:
        print("Could not find latest_titles.json. Please run title_finder.py first.")
        return
    
    # Initialize counters
    total_granules = 0
    title_counts = {}
    
    # Process each title
    for title_number, package_id in latest_titles.items():
        print(f"\nProcessing Title {title_number} (Package ID: {package_id})")
        
        try:
            # Get granules data for this package
            granules_data = get_package_granules(package_id, page_size=1)
            
            # Extract the count
            if "count" in granules_data:
                count = granules_data["count"]
                title_counts[title_number] = count
                total_granules += count
                print(f"  Title {title_number} has {count} granules")
            else:
                print(f"  No count field found for Title {title_number}")
                
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)
                
        except Exception as e:
            print(f"  Error processing Title {title_number}: {e}")
    
    # Save the results
    results = {
        "total_granules": total_granules,
        "title_counts": title_counts,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    with open(OUTPUT_DIR / "granule_counts.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print the summary
    print("\n=== Summary ===")
    print(f"Total granules across all titles: {total_granules}")
    print(f"Detailed counts saved to {OUTPUT_DIR / 'granule_counts.json'}")

def main():
    """Main function to check granule count in API response"""
    if not API_KEY:
        print("Error: API_KEY not found in .env file")
        return
    
    # Ask user what they want to do
    print("What would you like to do?")
    print("1. Check granule count for a single title (Title 7)")
    print("2. Sum granules across all titles")
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        check_single_title()
    elif choice == "2":
        sum_all_granules()
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()