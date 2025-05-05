# Legal Data Processing Project

A Python project for processing and analyzing legal data from APIs with secure API key management.

## Project Structure

```
.
├── .env # Environment variables (API keys, etc.)
├── .gitignore # Git ignore file
├── README.md # Project documentation
├── fetch_titles.py # Script to find latest US Code titles
├── generate_hierarchy.py # Script to build US Code hierarchy
├── generate_clusters.py # Script to generate cluster datasets
├── main.py # Orchestrator to run fetch, hierarchy, clusters
├── utilities/ # Helper and analysis scripts
│   ├── analyze_cluster_breadth.py # Analyze cluster breadth
│   ├── analyze_hierarchy_permutations.py # Analyze hierarchy permutations
│   └── check_granule_count.py # Check and sum granule counts
└── outputs/ # Directory for storing processed data
    ├── latest_titles.json
    ├── title_summaries.json
    ├── uscode_hierarchy.json
    ├── cluster_level_dataset.tsv
    ├── cluster_level_dataset_no_links.tsv
    ├── granule_counts.json
    └── hierarchy_permutations.txt
```

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your API keys

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
