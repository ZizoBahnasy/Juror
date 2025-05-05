#!/usr/bin/env python3
"""
US Code Hierarchy Permutation Analyzer
This script analyzes the US Code hierarchy JSON file to identify
all unique permutations of hierarchical components in granule IDs
that end with a section.
"""

import json
import re
from pathlib import Path
from collections import Counter

# Constants
# Update path to reference parent directory's outputs folder
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
HIERARCHY_FILE = OUTPUT_DIR / "uscode_hierarchy.json"
RESULTS_FILE = OUTPUT_DIR / "hierarchy_permutations.txt"

def parse_granule_id(granule_id):
    """Parse a granule ID to extract its components and structure in the correct order"""
    # Define regex patterns for each component
    patterns = [
        (r'title(\d+)', 'title'),
        (r'subtitle([IVXLCDM]+|[A-Z])', 'subtitle'),
        (r'divsn([A-Z])', 'division'),  # Added division pattern
        (r'app(-[a-zA-Z0-9-]+)?', 'app'),  # App pattern (with or without suffix)
        (r'dup(\d+)', 'duplicate'),  # Added duplicate marker pattern
        (r'part([IVXLCDM]+|\d+|[A-Z])', 'part'),
        (r'subpart([A-Z]|\d+)', 'subpart'),
        (r'chap(\d+)', 'chapter'),
        (r'subchap([IVXLCDM]+|\d+)', 'subchapter'),
        (r'sec(\d+[a-z]?(?:-\d+)?)', 'section')
    ]
    
    # Find all matches with their positions
    matches = []
    for pattern, component_type in patterns:
        for match in re.finditer(f'-{pattern}', granule_id):
            start_pos = match.start()
            matches.append((start_pos, component_type))
    
    # Sort matches by their position in the string to preserve order
    matches.sort()
    
    # Extract the component types in order
    components = [component_type for _, component_type in matches]
    
    return tuple(components)

def analyze_hierarchy_permutations():
    """Analyze the hierarchy file to find all unique permutations of components that end with section"""
    # Load the hierarchy file
    try:
        with open(HIERARCHY_FILE, "r") as f:
            hierarchy = json.load(f)
    except FileNotFoundError:
        print(f"Error: {HIERARCHY_FILE} not found.")
        return
    
    # Track permutations
    permutations = Counter()
    granule_examples = {}
    
    # Process all titles
    for title_entry in hierarchy.get("titles", []):
        for granule in title_entry.get("granules", []):
            granule_id = granule.get("granuleId", "")
            granule_class = granule.get("granuleClass", "")
            
            # Only process LEAF granules (sections)
            if granule_class == "LEAF":
                # Parse the granule ID to extract its structure
                structure = parse_granule_id(granule_id)
                
                # Only keep structures that end with 'section'
                if structure and structure[-1] == "section":
                    # Count this permutation
                    permutations[structure] += 1
                    
                    # Store an example for each permutation
                    if structure not in granule_examples:
                        granule_examples[structure] = granule_id
    
    # Find the deepest permutation
    deepest_permutation = max(permutations.keys(), key=len)
    deepest_depth = len(deepest_permutation)
    deepest_count = permutations[deepest_permutation]
    deepest_example = granule_examples[deepest_permutation]
    
    # Calculate statistics for permutations with depth >= 5 and 6
    deep_permutations = {p: count for p, count in permutations.items() if len(p) >= 5}
    deeper_permutations = {p: count for p, count in permutations.items() if len(p) >= 6}
    deep_permutation_count = len(deep_permutations)
    deeper_permutation_count = len(deeper_permutations)

    total_permutation_count = len(permutations)
    
    # Calculate weighted percentage based on actual counts
    deep_section_count = sum(deep_permutations.values())
    deeper_section_count = sum(deeper_permutations.values())
    total_section_count = sum(permutations.values())
    deep_weighted_percentage = (deep_section_count / total_section_count) * 100 if total_section_count > 0 else 0
    deeper_weighted_percentage = (deeper_section_count / total_section_count) * 100 if total_section_count > 0 else 0
    
    # Write results to file
    with open(RESULTS_FILE, "w") as f:
        f.write("US Code Hierarchy Permutations (Ending with Section)\n")
        f.write("===============================================\n\n")
        
        # First print the deepest permutation
        f.write("DEEPEST HIERARCHY PATH:\n")
        f.write(f"Structure: {' > '.join(deepest_permutation)} (Depth: {deepest_depth})\n")
        f.write(f"Count: {deepest_count}\n")
        f.write(f"Example: {deepest_example}\n\n")
        
        # Add statistics about deep permutations
        f.write("DEPTH STATISTICS:\n")
        # f.write(f"Permutation types with depth ≥ 5 and 6: {deep_permutation_count} out of {total_permutation_count} ({(deep_permutation_count / total_permutation_count) * 100:.2f}%)\n")
        f.write(f"Section instances with depth ≥ 5: {deep_section_count:,} out of {total_section_count:,} ({deep_weighted_percentage:.2f}%)\n")
        f.write(f"Section instances with depth ≥ 6: {deeper_section_count:,} out of {total_section_count:,} ({deeper_weighted_percentage:.2f}%)\n\n")
        
        f.write("ALL PERMUTATIONS (by frequency):\n")
        f.write("-------------------------------\n\n")
        
        # Sort permutations by frequency (most common first)
        for structure, count in permutations.most_common():
            depth = len(structure)
            f.write(f"Structure: {' > '.join(structure)} (Depth: {depth})\n")
            f.write(f"Count: {count}\n")
            f.write(f"Example: {granule_examples[structure]}\n\n")
        
        # Summary
        f.write(f"Total unique permutations ending with section: {total_permutation_count}\n")
        f.write(f"Percentage of permutation types with depth ≥ 5: {(deep_permutation_count / total_permutation_count) * 100:.2f}%\n")
        f.write(f"Percentage of section instances with depth ≥ 5: {deep_weighted_percentage:.2f}%\n")
    
    # Print summary to console with focus on the deepest path
    print("\n=== DEEPEST HIERARCHY PATH IN US CODE ===")
    print(f"Deepest structure: {' > '.join(deepest_permutation)}")
    print(f"Depth: {deepest_depth} levels")
    print(f"Count: {deepest_count} instances")
    print(f"Example: {deepest_example}")
    print("=========================================\n")
    
    print(f"Found {total_permutation_count} unique permutations of hierarchy components ending with section.")
    print(f"Permutation types with depth ≥ 5: {deep_permutation_count} ({(deep_permutation_count / total_permutation_count) * 100:.2f}%)")
    print(f"Section instances with depth ≥ 5: {deep_section_count:,} out of {total_section_count:,} ({deep_weighted_percentage:.2f}%)")
    print(f"Results written to {RESULTS_FILE}")
    
    # Also print the top 5 most common permutations
    print("\nTop 5 most common permutations:")
    for structure, count in permutations.most_common(5):
        depth = len(structure)
        print(f"- {' > '.join(structure)} (Depth: {depth}): {count} occurrences")
        print(f"  Example: {granule_examples[structure]}")

if __name__ == "__main__":
    analyze_hierarchy_permutations()