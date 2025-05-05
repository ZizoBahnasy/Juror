#!/usr/bin/env python3
"""
US Code Cluster Dataset Creator (v3)
Emits only non-empty hierarchy levels.
"""

import json
import csv
from pathlib import Path

# now one level up from scripts/
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
HIERARCHY_FILE = OUTPUT_DIR / "uscode_hierarchy.json"
MAX_CLUSTERS = 8
CLUSTER_DATASET_FILE          = OUTPUT_DIR / "cluster_level_dataset.tsv"
CLUSTER_DATASET_NO_LINKS_FILE = OUTPUT_DIR / "cluster_level_dataset_no_links.tsv"

# -----------------------------
# Helper Functions
# -----------------------------

def parse_granule_id_prefixes(granule_id):
    """
    Split a granule ID into progressive prefixes:
      e.g. "USCODE-2023-title54-subtitleIII-divsnA-app-dup4-chap3061-subchapIII-sec306131"
    → ["USCODE-2023-title54", "USCODE-2023-title54-subtitleIII", ..., full ID]
    """
    parts = granule_id.split('-')
    return ['-'.join(parts[:i+1]) for i in range(2, len(parts))]


def should_skip_section(title):
    """Skip sections marked Repealed/Omitted/Transferred."""
    return any(term in title for term in ('Repealed', 'Omitted', 'Transferred'))


def generate_title_link(year, title_num):
    """Build govinfo summary URL for a US Code title."""
    return f"https://api.govinfo.gov/packages/USCODE-{year}-title{title_num}/summary"

# -----------------------------
# Main Function
# -----------------------------

def create_cluster_dataset():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load hierarchy JSON
    try:
        hierarchy = json.loads(HIERARCHY_FILE.read_text())
    except FileNotFoundError:
        print(f"Error: {HIERARCHY_FILE} not found")
        return

    year = hierarchy.get('year', '2023')

    # Pre-collect titles & links
    granule_titles = {}
    granule_links  = {}
    for title_entry in hierarchy.get('titles', []):
        tnum = title_entry.get('titleNumber', '')
        gid  = f"USCODE-{year}-title{tnum}"
        granule_titles[gid] = title_entry.get('title', '')
        granule_links[gid]  = generate_title_link(year, tnum)
        for node in title_entry.get('granules', []):
            nid = node.get('granuleId','')
            if node.get('granuleTitle'):
                granule_titles[nid] = node['granuleTitle']
            if node.get('granuleLink'):
                granule_links[nid] = node['granuleLink']

    # Open output TSVs
    with open(CLUSTER_DATASET_FILE, "w", newline="") as f_links, \
         open(CLUSTER_DATASET_NO_LINKS_FILE, "w", newline="") as f_nolinks:

        writer_links   = csv.writer(f_links,   delimiter="\t")
        writer_nolinks = csv.writer(f_nolinks, delimiter="\t")

        # Fixed header describing the meaning of successive clusters
        header_links = []
        header_nolinks = []
        for i in range(MAX_CLUSTERS):
            header_links += [f"cluster_{i}_name", f"cluster_{i}_link"]
            header_nolinks += [f"cluster_{i}_name"]
        writer_links.writerow(header_links)
        writer_nolinks.writerow(header_nolinks)

        section_count = skipped_count = 0

        # Process each LEAF (section)
        for title_entry in hierarchy.get('titles', []):
            for node in title_entry.get('granules', []):
                if node.get('granuleClass') != 'LEAF':
                    continue
                gid   = node.get('granuleId','')
                title = node.get('granuleTitle') or node.get('title','')
                if 'sec' not in gid or should_skip_section(title):
                    skipped_count += 1
                    continue

                # Build full list of prefixes for this granule
                prefixes = parse_granule_id_prefixes(gid)

                # Collect only non-empty (name, link) pairs in order
                clusters_links = []  # flat [name, link, name, link, ...]
                clusters_nolinks = []  # [name, name, ...]
                for prefix in prefixes:
                    if len(clusters_nolinks) >= MAX_CLUSTERS:
                        break
                    name = granule_titles.get(prefix, "")
                    link = granule_links.get(prefix, "")
                    if name:
                        clusters_nolinks.append(name)
                        clusters_links += [name, link]

                # Ensure the final section is included as the last cluster
                if clusters_nolinks and clusters_nolinks[-1] != title:
                    if len(clusters_nolinks) < MAX_CLUSTERS:
                        clusters_nolinks.append(title)
                        clusters_links += [title, granule_links.get(gid, "")]
                    else:
                        # replace last if already at max depth
                        clusters_nolinks[-1] = title
                        clusters_links[-2:] = [title, granule_links.get(gid, "")]

                # Pad out to fill MAX_CLUSTERS slots so columns align to header
                # (empty strings for any missing deeper clusters)
                while len(clusters_nolinks) < MAX_CLUSTERS:
                    clusters_nolinks.append("")
                    clusters_links += ["", ""]

                # Write the row
                writer_links.writerow(clusters_links)
                writer_nolinks.writerow(clusters_nolinks)
                section_count += 1

    # Summary
    print(f"With-links TSV: {CLUSTER_DATASET_FILE}")
    print(f"No-links TSV:   {CLUSTER_DATASET_NO_LINKS_FILE}")
    print(f"Sections:       {section_count}")
    print(f"Skipped:        {skipped_count}")

if __name__ == "__main__":
    create_cluster_dataset()
