#!/usr/bin/env python3
"""
Main orchestrator for the Legal Data Processing Project.
Runs the three core scripts in sequence:
 1. scripts/fetch_titles.py
 2. scripts/generate_hierarchy.py
 3. scripts/generate_clusters.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    'scripts/fetch_titles.py',
    'scripts/generate_hierarchy.py',
    'scripts/generate_clusters.py'
]

def run_script(script_rel_path):
    script_path = Path(__file__).parent / script_rel_path
    if not script_path.exists():
        print(f"Error: {script_rel_path} not found")
        sys.exit(1)

    print(f"\n=== Running {script_rel_path} ===")
    result = subprocess.run(['python3', str(script_path)])
    if result.returncode != 0:
        print(f"Error: {script_rel_path} exited with code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == '__main__':
    for script in SCRIPTS:
        run_script(script)
    print("\nAll scripts completed successfully.")
