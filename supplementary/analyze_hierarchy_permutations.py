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
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import os

# Constants
# Update path to reference parent directory's outputs folder
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
HIERARCHY_FILE = OUTPUT_DIR / "uscode_hierarchy.json"
DEPTH_ANALYSIS_DIR = OUTPUT_DIR / "depth_analysis"
RESULTS_FILE = DEPTH_ANALYSIS_DIR / "hierarchy_permutations.txt"
BAR_CHART_FILE = DEPTH_ANALYSIS_DIR / "hierarchy_depth_distribution.png"
SMOOTH_CHART_FILE = DEPTH_ANALYSIS_DIR / "hierarchy_depth_smooth.png"

# Create depth_analysis directory if it doesn't exist
os.makedirs(DEPTH_ANALYSIS_DIR, exist_ok=True)

# Anthropic orange color
ANTHROPIC_ORANGE = '#f9734a'

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

def visualize_depth_distribution(depth_counts):
    """
    Create visualizations showing the distribution of sections by hierarchy depth
    
    Args:
        depth_counts: Dictionary mapping depth to count of sections
    """
    # Sort depths for consistent display
    depths = sorted(depth_counts.keys())
    counts = [depth_counts[d] for d in depths]
    
    # Calculate percentages for labels
    total = sum(counts)
    percentages = [(count / total) * 100 for count in counts]
    
    # 1. Bar Chart with Anthropic Orange
    plt.figure(figsize=(12, 7))
    bars = plt.bar(depths, counts, color=ANTHROPIC_ORANGE, alpha=0.9)
    plt.xlabel('Hierarchy Depth', fontsize=12)
    plt.ylabel('Number of Sections', fontsize=12)
    plt.title('Distribution of US Code Sections by Hierarchy Depth', fontsize=14)
    plt.xticks(depths, fontsize=10)
    plt.yticks(fontsize=10)
    
    # Add count and percentage labels on top of bars
    for i, (bar, count, pct) in enumerate(zip(bars, counts, percentages)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{count:,}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=9)
    
    # Add grid lines for readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(BAR_CHART_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Smooth Distribution Curve
    plt.figure(figsize=(12, 7))
    
    # Create x values for smooth curve (more points than just the depths)
    x_smooth = np.linspace(min(depths), max(depths), 300)
    
    # Create the spline function
    if len(depths) > 3:  # Need at least 4 points for cubic spline
        spl = make_interp_spline(depths, counts, k=3)
        y_smooth = spl(x_smooth)
    else:
        # Fall back to linear interpolation if not enough points
        from scipy.interpolate import interp1d
        f = interp1d(depths, counts, kind='linear')
        y_smooth = f(x_smooth)
    
    # Plot the smooth curve
    plt.plot(x_smooth, y_smooth, color=ANTHROPIC_ORANGE, linewidth=3)
    
    # Add points at the actual data points
    plt.scatter(depths, counts, color=ANTHROPIC_ORANGE, s=100, zorder=5)
    
    # Add labels for the actual data points
    for i, (x, y, pct) in enumerate(zip(depths, counts, percentages)):
        plt.annotate(f'{y:,} ({pct:.1f}%)', 
                    (x, y), 
                    textcoords="offset points",
                    xytext=(0, 10), 
                    ha='center',
                    fontsize=9)
    
    # Fill the area under the curve
    plt.fill_between(x_smooth, y_smooth, color=ANTHROPIC_ORANGE, alpha=0.3)
    
    # Set labels and title
    plt.xlabel('Hierarchy Depth', fontsize=12)
    plt.ylabel('Number of Sections', fontsize=12)
    plt.title('Distribution of US Code Sections by Hierarchy Depth', fontsize=14)
    
    # Set x-ticks to only show the actual depth values
    plt.xticks(depths, fontsize=10)
    plt.yticks(fontsize=10)
    
    # Add grid for readability
    plt.grid(linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(SMOOTH_CHART_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualizations saved to {BAR_CHART_FILE} and {SMOOTH_CHART_FILE}")

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
    
    # Track counts by depth
    depth_counts = Counter()
    for structure, count in permutations.items():
        depth = len(structure)
        depth_counts[depth] += count
    
    # Create visualizations
    visualize_depth_distribution(depth_counts)
    
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
        f.write(f"Section instances with depth ≥ 5: {deep_section_count:,} out of {total_section_count:,} ({deep_weighted_percentage:.2f}%)\n")
        f.write(f"Section instances with depth ≥ 6: {deeper_section_count:,} out of {total_section_count:,} ({deeper_weighted_percentage:.2f}%)\n\n")
        
        # Add depth distribution table
        f.write("DEPTH DISTRIBUTION:\n")
        f.write("------------------\n")
        for depth in sorted(depth_counts.keys()):
            count = depth_counts[depth]
            percentage = (count / total_section_count) * 100
            f.write(f"Depth {depth}: {count:,} sections ({percentage:.2f}%)\n")
        f.write("\n")
        
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