#!/usr/bin/env python3
"""
Generate one merged sample hierarchy tree with multiple leaves per shared prefix,
and save it as Markdown under outputs/taxonomy.
"""

import pandas as pd
import random
from pathlib import Path

# --- Configuration ---
BASE_DIR       = Path(__file__).parent.parent
DATASET_PATH   = BASE_DIR / "outputs" / "cluster_level_dataset_no_links.tsv"
TAXONOMY_DIR   = BASE_DIR / "outputs" / "taxonomy"
TAXONOMY_FILE  = TAXONOMY_DIR / "taxonomy.md"

# Load dataset, treating empty strings as missing
df = pd.read_csv(DATASET_PATH, sep="\t", dtype=str).fillna("")

# Identify cluster columns
cluster_cols = [f"cluster_{i}_name" for i in range(8)]
# Compute depth = number of non-empty levels
df["depth"] = df[cluster_cols].apply(lambda row: sum(bool(cell) for cell in row), axis=1)

def sample_two_leaves(min_depth, max_depth=None):
    """
    Find a prefix of length (min_depth-1) that has at least two distinct leaves
    at level min_depth, then return exactly two sample rows under that prefix.
    """
    # Filter rows by depth
    if max_depth:
        bucket = df[(df.depth >= min_depth) & (df.depth < max_depth)]
    else:
        bucket = df[df.depth >= min_depth]

    prefix_len = min_depth - 1
    prefix_cols = cluster_cols[:prefix_len]
    leaf_col    = cluster_cols[prefix_len]

    # Group by the shared prefix
    groups = bucket.groupby(prefix_cols, dropna=False)

    # Keep only prefixes where there are 2+ distinct leaf_col values
    valid_prefixes = [
        (prefix, grp)
        for prefix, grp in groups
        if grp[leaf_col].nunique() >= 2
    ]
    if not valid_prefixes:
        raise RuntimeError(f"No prefix with two leaves at depth {min_depth}")

    # Pick one prefix at random
    random.seed(42)
    prefix, grp = random.choice(valid_prefixes)

    # Sample two different leaves
    samples = grp.sample(n=2, random_state=42)
    return samples.to_dict(orient="records")

# Build a list of all sample rows (2 leaves each for depth 4, 5, and 6+)
samples = []
samples += sample_two_leaves(4, 5)   # exactly depth=4
samples += sample_two_leaves(5, 6)   # exactly depth=5
samples += sample_two_leaves(6, None)  # depth>=6

# Build nested dict under "US Code"
tree = {"US Code": {}}
for row in samples:
    # Extract the non-empty cluster names in order
    path = [row[c] for c in cluster_cols if row[c]]
    subtree = tree["US Code"]
    for node in path:
        subtree = subtree.setdefault(node, {})

# Prepare Markdown lines with code fence
lines = ["# Sample US Code Taxonomy", "", "```", "US Code"]

def collect(node_dict, prefix=""):
    keys = list(node_dict.keys())
    for i, key in enumerate(keys):
        is_last = (i == len(keys)-1)
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{key}")
        child_prefix = prefix + ("    " if is_last else "│   ")
        collect(node_dict[key], child_prefix)

collect(tree["US Code"])
lines.append("```")

# Write out
TAXONOMY_DIR.mkdir(parents=True, exist_ok=True)
TAXONOMY_FILE.write_text("\n".join(lines), encoding="utf-8")

# Echo
print("\n".join(lines))
print(f"\nSaved taxonomy Markdown to {TAXONOMY_FILE}")
