# Claude as a Juror

[US Code](https://uscode.house.gov/) dataset curation and prompting for a Claude.ai legal experiment using Clio.

Why US Code? This legal corpus is the federal government's most organized hierarchy of laws currently in effect.

The final "cluster" dataset for use in Clio is located in `outputs/cluster_level_dataset_no_links.tsv`.

`outputs/cluster_level_dataset.tsv` contains the same data but with paired columns for each level containing the URL pointing to the relevant section of the US Code.

Unlike the O*NET task clustering the Anthropic team had to do to create a hierarchy to narrow down the classification options, the US legal code is already segmented into multiple thematically distinct levels, although the depth of the hierarchy is not uniform. Some sections contain as few as three layers (Title, Chapter, Section), a plurality contain four (Title, Chapter, Subchapter, Subsection), and some contain up to eight (Title, Subtitle, Division, Appendix, Duplicate, Chapter, Subchapter, Section).

See more on the varying depths in `outputs/hierarchy_permutations.txt`.

The final dataset excludes any Sections that have been 'Repealed', 'Omitted', or 'Transferred', which make up 9,648 of the 60,636 total Sections, leaving us with 50,988 viable statutory Sections. This is ~2.5x the size of the full O*NET task dataset.

Unlike the O*NET task descriptions, the individual 'cluster names' here are notably shorter in length. `supplementary/analyze_cluster_breadth.py` calculates the maximum classification option count for each layer, with the highest being 143 options at any one point. This is a high number, but it's also only 1,166 tokens at its peak, so these lists should not be prohibitively expensive to use in the classification prompts. See more of the distribution in `outputs/cluster_breadth_report.txt`.

## Project Structure

```
.
├── .env # Contains GovInfo API key from https://api.govinfo.gov/docs/
├── .gitignore # Git ignore file
├── README.md
├── main.py # Orchestrator to run fetch, hierarchy, clusters
├── scripts/ # Core processing scripts
│   ├── fetch_titles.py # Script to find latest US Code titles
|   ├── generate_hierarchy.py # Script to build US Code hierarchy
|   └── generate_clusters.py # Script to generate cluster datasets
├── utilities/ # Helper and analysis scripts
│   ├── analyze_cluster_breadth.py # Analyze cluster breadth
│   ├── analyze_hierarchy_permutations.py # Analyze hierarchy permutations
│   └── check_granule_count.py # Check and sum granule counts
└── outputs/ # Directory for storing processed data
    ├── latest_titles.json
    ├── title_summaries.json
    ├── uscode_hierarchy.json
    ├── cluster_level_dataset.tsv # Primary output with links
    ├── cluster_level_dataset_no_links.tsv # Primary output without links
    ├── granule_counts.json
    └── hierarchy_permutations.txt
```

## Usage

Follow the workflow sequence below to process and analyze legal data:

### Main Processing Scripts

run everything in one go:
```bash
python3 main.py
```
or step by step:
```bash
# Generate title information
python3 fetch_titles.py  # Generates outputs/latest_titles.json and outputs/title_summaries.json

# Generate hierarchy information
python3 generate_hierarchy.py  # Generates outputs/uscode_hierarchy.json

# Generate cluster datasets
python3 generate_clusters.py  # Generates cluster_level_dataset.tsv and cluster_level_dataset_no_links.tsv
```

### Supplementary Analysis Scripts (in utilities directory)
These scripts are not required for the main processing but can be used to analyze the generated data.

```bash
# Analyze cluster breadth
python3 analyze_cluster_breadth.py

# Analyze hierarchy permutations
python3 analyze_hierarchy_permutations.py

# Check granule counts
python3 check_granule_count.py  # Generates outputs/granule_counts.json
```

## License

MIT
