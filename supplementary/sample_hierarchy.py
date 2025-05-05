#!/usr/bin/env python3
"""
Generate one merged sample hierarchy tree and save it as Markdown under outputs/taxonomy.
Rooted at “US Code”, then Title, then deeper cluster levels.
"""

import pandas as pd
import random
from pathlib import Path

# --- Configuration ---
BASE_DIR       = Path(__file__).parent.parent
DATASET_PATH   = BASE_DIR / "outputs" / "cluster_level_dataset_no_links.tsv"
TAXONOMY_DIR   = BASE_DIR / "outputs" / "taxonomy"
TAXONOMY_FILE  = TAXONOMY_DIR / "taxonomy.md"

# Load dataset, treat empty strings as missing
df = (
    pd.read_csv(DATASET_PATH, sep="\t", dtype=str)
      .fillna("")
)

# Cluster columns and compute depth
cluster_cols = [f"cluster_{i}_name" for i in range(8)]
df["depth"] = df[cluster_cols].apply(lambda row: sum(bool(cell) for cell in row), axis=1)

def sample_path(min_depth, max_depth=None):
    """Return one random row with depth >= min_depth (and < max_depth if given)."""
    if max_depth is not None:
        candidates = df[(df.depth >= min_depth) & (df.depth < max_depth)]
    else:
        candidates = df[df.depth >= min_depth]
    return candidates.sample(1, random_state=42).iloc[0]

# Pick sample rows
random.seed(42)
samples = [
    sample_path(4, 5),
    sample_path(5, 6),
    sample_path(6)
]

# Build nested dict under "US Code"
tree: dict = {"US Code": {}}
for row in samples:
    path = [row[col] for col in cluster_cols if row[col]]
    subtree = tree["US Code"]
    for node in path:
        subtree = subtree.setdefault(node, {})

# Collect lines, wrapping in a Markdown code fence
output_lines: list[str] = ["# Sample US Code Taxonomy", "", "```", "US Code"]

def collect_subtree_lines(node_dict: dict, prefix: str = ""):
    """
    Recursively collect ASCII-tree lines into output_lines.
    """
    keys = list(node_dict.keys())
    for i, key in enumerate(keys):
        is_last = (i == len(keys) - 1)
        connector = "└── " if is_last else "├── "
        output_lines.append(f"{prefix}{connector}{key}")
        next_prefix = prefix + ("    " if is_last else "│   ")
        collect_subtree_lines(node_dict[key], next_prefix)

# Build the tree lines
collect_subtree_lines(tree["US Code"])
output_lines.append("```")  # close code fence

# Ensure output folder exists
TAXONOMY_DIR.mkdir(parents=True, exist_ok=True)

# Write Markdown file
TAXONOMY_FILE.write_text("\n".join(output_lines), encoding="utf-8")

# Also print to console
print("\n".join(output_lines))
print(f"\nSaved taxonomy Markdown to {TAXONOMY_FILE}")
