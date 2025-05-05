#!/usr/bin/env python3
"""
Analyze cluster breadth and token usage (using real LLM tokenization), then save a report.
"""

import pandas as pd
from pathlib import Path
import os
import matplotlib.pyplot as plt
import numpy as np

# Use tiktoken for GPT-style BPE counting
import tiktoken

# Paths
BASE_DIR             = Path(__file__).parent.parent
OUTPUTS_DIR          = BASE_DIR / "outputs"
BREADTH_ANALYSIS_DIR = OUTPUTS_DIR / "breadth_analysis"
DATASET_PATH         = OUTPUTS_DIR / "cluster_level_dataset_no_links.tsv"
REPORT_PATH          = BREADTH_ANALYSIS_DIR / "cluster_breadth_report.txt"
VERTICAL_CHART_FILE  = BREADTH_ANALYSIS_DIR / "cluster_breadth_vertical.png"
TOKEN_VERTICAL_CHART_FILE = BREADTH_ANALYSIS_DIR / "cluster_tokens_vertical.png"

# Anthropic orange color
ANTHROPIC_ORANGE = '#f9734a'

os.makedirs(BREADTH_ANALYSIS_DIR, exist_ok=True)

# Load dataset
if not DATASET_PATH.exists():
    raise FileNotFoundError(f"Dataset file not found at: {DATASET_PATH}")
df = pd.read_csv(DATASET_PATH, sep='\t', dtype=str).replace({'': pd.NA})

# Initialize a GPT-style tokenizer (for gpt-3.5-turbo / cl100k_base)
try:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
except KeyError:
    encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(name_list: list[str]) -> int:
    """
    Count tokens using BPE as the LLM does.
    """
    total = 0
    for name in name_list:
        if isinstance(name, str):
            total += len(encoding.encode(name))
    return total

def visualize_vertical_breadth(breadths, parents, cluster_levels):
    """
    Create a vertical top-down visualization of cluster breadth centered at 0
    
    Args:
        breadths: List of max breadth values for each cluster level
        parents: List of parent names for each cluster level
        cluster_levels: List of cluster level names
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Create horizontal bars centered at 0
    y_pos = np.arange(len(breadths))
    
    # Create bars that extend from -breadth/2 to +breadth/2
    half_breadths = [b/2 for b in breadths]
    
    # Plot horizontal bars centered at 0
    bars = ax.barh(y_pos, half_breadths, align='center', color=ANTHROPIC_ORANGE, alpha=0.7)
    bars = ax.barh(y_pos, [-b for b in half_breadths], align='center', color=ANTHROPIC_ORANGE, alpha=0.7)
    
    # Set y-axis labels (cluster levels)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cluster_levels)
    
    # Set x-axis label
    ax.set_xlabel('Breadth (Number of Children)', fontsize=12)
    
    # Set title
    ax.set_title('Cluster Breadth Distribution (Centered)', fontsize=14)
    
    # Add breadth values as annotations
    for i, breadth in enumerate(breadths):
        # Add breadth value at the end of the right bar
        ax.text(half_breadths[i] + 1, i, f'{breadth}', 
                va='center', ha='left', fontsize=10, fontweight='bold')
        
        # # Add parent name on the left side
        # if i > 0:  # Skip level 0 which has no parent
        #     parent_text = f"Under: '{parents[i]}'" if len(parents[i]) < 20 else f"Under: '{parents[i][:17]}...'"
        #     ax.text(-half_breadths[i] - 1, i, parent_text, 
        #             va='center', ha='right', fontsize=8)
    
    # Add a vertical line at x=0
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    
    # Add grid lines
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Remove top and right spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Invert y-axis to have top-down ordering
    ax.invert_yaxis()
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(VERTICAL_CHART_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Vertical visualization saved to {VERTICAL_CHART_FILE}")

def visualize_vertical_tokens(tokens, parents, cluster_levels):
    """
    Create a vertical top-down visualization of token counts centered at 0
    
    Args:
        tokens: List of token counts for each cluster level
        parents: List of parent names for each cluster level
        cluster_levels: List of cluster level names
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Create horizontal bars centered at 0
    y_pos = np.arange(len(tokens))
    
    # Create bars that extend from -tokens/2 to +tokens/2
    half_tokens = [t/2 for t in tokens]
    
    # Plot horizontal bars centered at 0
    bars = ax.barh(y_pos, half_tokens, align='center', color=ANTHROPIC_ORANGE, alpha=0.7)
    bars = ax.barh(y_pos, [-t for t in half_tokens], align='center', color=ANTHROPIC_ORANGE, alpha=0.7)
    
    # Set y-axis labels (cluster levels)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cluster_levels)
    
    # Set x-axis label
    ax.set_xlabel('Token Count', fontsize=12)
    
    # Set title
    ax.set_title('Token Usage Distribution (Centered)', fontsize=14)
    
    # Add token values as annotations
    for i, token_count in enumerate(tokens):
        # Add token value at the end of the right bar
        ax.text(half_tokens[i] + 50, i, f'{token_count:,}', 
                va='center', ha='left', fontsize=10, fontweight='bold')
        
        # # Add parent name on the left side
        # if i > 0:  # Skip level 0 which has no parent
        #     parent_text = f"Under: '{parents[i]}'" if len(parents[i]) < 20 else f"Under: '{parents[i][:17]}...'"
        #     ax.text(-half_tokens[i] - 50, i, parent_text, 
        #             va='center', ha='right', fontsize=8)
    
    # Add a vertical line at x=0
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    
    # Add grid lines
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Remove top and right spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Invert y-axis to have top-down ordering
    ax.invert_yaxis()
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(TOKEN_VERTICAL_CHART_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Token vertical visualization saved to {TOKEN_VERTICAL_CHART_FILE}")

def count_cluster_breadth(df: pd.DataFrame):
    report_lines: list[str] = []
    
    # Lists to store data for visualization
    breadths = []
    tokens_list = []
    parent_names = ["None"]  # Level 0 has no parent
    cluster_levels = []

    # Level 0
    lvl0 = df['cluster_0_name'].dropna().unique().tolist()
    breadth0 = len(lvl0)
    tokens0 = count_tokens(lvl0)
    line0 = (f"Cluster 0 max breadth: {breadth0} (top-level titles), "
             f"tokens if listed: {tokens0}")
    print(line0); report_lines.append(line0)
    breadths.append(breadth0)
    tokens_list.append(tokens0)
    cluster_levels.append("Cluster 0 (Titles)")

    # Level 1
    lvl1 = df.dropna(subset=['cluster_1_name']) \
             .groupby('cluster_0_name')['cluster_1_name'].nunique()
    max1, parent1 = lvl1.max(), lvl1.idxmax()
    children1 = df[df['cluster_0_name']==parent1] \
                  ['cluster_1_name'].dropna().unique().tolist()
    tokens1 = count_tokens(children1)
    line1 = (f"Cluster 1 max breadth: {max1} under cluster_0 '{parent1}', "
             f"tokens if listed: {tokens1}")
    print(line1); report_lines.append(line1)
    breadths.append(max1)
    tokens_list.append(tokens1)
    parent_names.append(parent1)
    cluster_levels.append("Cluster 1")

    # Level 2
    lvl2 = df.dropna(subset=['cluster_2_name']) \
             .groupby(['cluster_0_name','cluster_1_name'])['cluster_2_name'] \
             .nunique()
    max2, parent2 = lvl2.max(), lvl2.idxmax()
    children2 = df[
        (df['cluster_0_name']==parent2[0]) &
        (df['cluster_1_name']==parent2[1])
    ]['cluster_2_name'].dropna().unique().tolist()
    tokens2 = count_tokens(children2)
    line2 = (f"Cluster 2 max breadth: {max2} under cluster_1 '{parent2[1]}' "
             f"(in title '{parent2[0]}'), tokens if listed: {tokens2}")
    print(line2); report_lines.append(line2)
    breadths.append(max2)
    tokens_list.append(tokens2)
    parent_names.append(parent2[1])
    cluster_levels.append("Cluster 2")

    # Level 3
    lvl3 = df.dropna(subset=['cluster_3_name']) \
             .groupby(['cluster_0_name','cluster_1_name','cluster_2_name']) \
             ['cluster_3_name'].nunique()
    max3, parent3 = lvl3.max(), lvl3.idxmax()
    children3 = df[
        (df['cluster_0_name']==parent3[0]) &
        (df['cluster_1_name']==parent3[1]) &
        (df['cluster_2_name']==parent3[2])
    ]['cluster_3_name'].dropna().unique().tolist()
    tokens3 = count_tokens(children3)
    line3 = (f"Cluster 3 max breadth: {max3} under cluster_2 '{parent3[2]}' "
             f"(path {parent3[:2]}), tokens if listed: {tokens3}")
    print(line3); report_lines.append(line3)
    breadths.append(max3)
    tokens_list.append(tokens3)
    parent_names.append(parent3[2])
    cluster_levels.append("Cluster 3")

    # Level 4
    lvl4 = df.dropna(subset=['cluster_4_name']) \
             .groupby(['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name']) \
             ['cluster_4_name'].nunique()
    max4, parent4 = lvl4.max(), lvl4.idxmax()
    children4 = df[
        (df['cluster_0_name']==parent4[0]) &
        (df['cluster_1_name']==parent4[1]) &
        (df['cluster_2_name']==parent4[2]) &
        (df['cluster_3_name']==parent4[3])
    ]['cluster_4_name'].dropna().unique().tolist()
    tokens4 = count_tokens(children4)
    line4 = (f"Cluster 4 max breadth: {max4} under cluster_3 '{parent4[3]}' "
             f"(path {parent4[:3]}), tokens if listed: {tokens4}")
    print(line4); report_lines.append(line4)
    breadths.append(max4)
    tokens_list.append(tokens4)
    parent_names.append(parent4[3])
    cluster_levels.append("Cluster 4")

    # Level 5
    lvl5 = df.dropna(subset=['cluster_5_name']) \
             .groupby(['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name','cluster_4_name']) \
             ['cluster_5_name'].nunique()
    max5, parent5 = lvl5.max(), lvl5.idxmax()
    children5 = df[
        (df['cluster_0_name']==parent5[0]) &
        (df['cluster_1_name']==parent5[1]) &
        (df['cluster_2_name']==parent5[2]) &
        (df['cluster_3_name']==parent5[3]) &
        (df['cluster_4_name']==parent5[4])
    ]['cluster_5_name'].dropna().unique().tolist()
    tokens5 = count_tokens(children5)
    line5 = (f"Cluster 5 max breadth: {max5} under cluster_4 '{parent5[4]}' "
             f"(path {parent5[:4]}), tokens if listed: {tokens5}")
    print(line5); report_lines.append(line5)
    breadths.append(max5)
    tokens_list.append(tokens5)
    parent_names.append(parent5[4])
    cluster_levels.append("Cluster 5")

    # Level 6
    lvl6 = df.dropna(subset=['cluster_6_name']) \
             .groupby(['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name','cluster_4_name','cluster_5_name']) \
             ['cluster_6_name'].nunique()
    max6, parent6 = lvl6.max(), lvl6.idxmax()
    children6 = df[
        (df['cluster_0_name']==parent6[0]) &
        (df['cluster_1_name']==parent6[1]) &
        (df['cluster_2_name']==parent6[2]) &
        (df['cluster_3_name']==parent6[3]) &
        (df['cluster_4_name']==parent6[4]) &
        (df['cluster_5_name']==parent6[5])
    ]['cluster_6_name'].dropna().unique().tolist()
    tokens6 = count_tokens(children6)
    line6 = (f"Cluster 6 max breadth: {max6} under cluster_5 '{parent6[5]}' "
             f"(path {parent6[:5]}), tokens if listed: {tokens6}")
    print(line6); report_lines.append(line6)
    breadths.append(max6)
    tokens_list.append(tokens6)
    parent_names.append(parent6[5])
    cluster_levels.append("Cluster 6")

    # Level 7
    lvl7 = df.dropna(subset=['cluster_7_name']) \
             .groupby(['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name','cluster_4_name','cluster_5_name','cluster_6_name']) \
             ['cluster_7_name'].nunique()
    max7, parent7 = lvl7.max(), lvl7.idxmax()
    children7 = df[
        (df['cluster_0_name']==parent7[0]) &
        (df['cluster_1_name']==parent7[1]) &
        (df['cluster_2_name']==parent7[2]) &
        (df['cluster_3_name']==parent7[3]) &
        (df['cluster_4_name']==parent7[4]) &
        (df['cluster_5_name']==parent7[5]) &
        (df['cluster_6_name']==parent7[6])
    ]['cluster_7_name'].dropna().unique().tolist()
    tokens7 = count_tokens(children7)
    line7 = (f"Cluster 7 max breadth: {max7} under cluster_6 '{parent7[6]}' "
             f"(path {parent7[:6]}), tokens if listed: {tokens7}")
    print(line7); report_lines.append(line7)
    breadths.append(max7)
    tokens_list.append(tokens7)
    parent_names.append(parent7[6])
    cluster_levels.append("Cluster 7")

    # Create visualizations
    visualize_vertical_breadth(breadths, parent_names, cluster_levels)
    visualize_vertical_tokens(tokens_list, parent_names, cluster_levels)

    # Write out report
    REPORT_PATH.write_text("\n".join(report_lines))
    print(f"\nReport saved to {REPORT_PATH}")

if __name__ == "__main__":
    count_cluster_breadth(df)
