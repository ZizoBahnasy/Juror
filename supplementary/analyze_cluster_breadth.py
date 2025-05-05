import pandas as pd
import os
from pathlib import Path

# Update path to reference parent directory's outputs folder
dataset_path = Path(__file__).parent.parent / "outputs" / "cluster_level_dataset_no_links.tsv"

# Ensure file exists
if not dataset_path.exists():
    raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")

# Load DataFrame, treat empty strings as missing values
df = pd.read_csv(dataset_path, sep='\t', dtype=str)
df = df.replace({'': pd.NA})

# Simple token counting: split on whitespace
def count_tokens(name_list):
    return sum(len(name.split()) for name in name_list if isinstance(name, str))

# Function to count unique breadth and token usage at each cluster level
def count_cluster_breadth(df):
    # Level 0: overall titles (cluster_0)
    lvl0_names = df['cluster_0_name'].dropna().unique().tolist()
    breadth0 = len(lvl0_names)
    tokens0 = count_tokens(lvl0_names)
    print(f"Cluster 0 max breadth: {breadth0} (top-level titles), tokens if listed: {tokens0}")

    # Level 1: per cluster_0_name
    lvl1 = df.dropna(subset=['cluster_1_name']).groupby('cluster_0_name')['cluster_1_name'].nunique()
    max1 = lvl1.max(); parent1 = lvl1.idxmax()
    children1 = df[df['cluster_0_name'] == parent1]['cluster_1_name'].dropna().unique().tolist()
    tokens1 = count_tokens(children1)
    print(f"Cluster 1 max breadth: {max1} under cluster_0 '{parent1}', tokens if listed: {tokens1}")

    # Level 2: per (cluster_0, cluster_1)
    lvl2 = df.dropna(subset=['cluster_2_name']).groupby(
        ['cluster_0_name','cluster_1_name']
    )['cluster_2_name'].nunique()
    max2 = lvl2.max(); parent2 = lvl2.idxmax()
    children2 = df[(df['cluster_0_name'] == parent2[0]) & (df['cluster_1_name'] == parent2[1])]['cluster_2_name'].dropna().unique().tolist()
    tokens2 = count_tokens(children2)
    print(f"Cluster 2 max breadth: {max2} under cluster_1 '{parent2[1]}' (in title '{parent2[0]}'), tokens if listed: {tokens2}")

    # Level 3: per (cluster_0, cluster_1, cluster_2)
    lvl3 = df.dropna(subset=['cluster_3_name']).groupby(
        ['cluster_0_name','cluster_1_name','cluster_2_name']
    )['cluster_3_name'].nunique()
    max3 = lvl3.max(); parent3 = lvl3.idxmax()
    children3 = df[(df['cluster_0_name']==parent3[0]) &
                   (df['cluster_1_name']==parent3[1]) &
                   (df['cluster_2_name']==parent3[2])]['cluster_3_name'].dropna().unique().tolist()
    tokens3 = count_tokens(children3)
    print(f"Cluster 3 max breadth: {max3} under cluster_2 '{parent3[2]}' (path {parent3[:2]}), tokens if listed: {tokens3}")

    # Level 4: per (cluster_0..cluster_3)
    lvl4 = df.dropna(subset=['cluster_4_name']).groupby(
        ['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name']
    )['cluster_4_name'].nunique()
    max4 = lvl4.max(); parent4 = lvl4.idxmax()
    children4 = df[(df['cluster_0_name']==parent4[0]) &
                   (df['cluster_1_name']==parent4[1]) &
                   (df['cluster_2_name']==parent4[2]) &
                   (df['cluster_3_name']==parent4[3])]['cluster_4_name'].dropna().unique().tolist()
    tokens4 = count_tokens(children4)
    print(f"Cluster 4 max breadth: {max4} under cluster_3 '{parent4[3]}' (path {parent4[:3]}), tokens if listed: {tokens4}")

    # Level 5: per (cluster_0..cluster_4)
    lvl5 = df.dropna(subset=['cluster_5_name']).groupby(
        ['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name','cluster_4_name']
    )['cluster_5_name'].nunique()
    max5 = lvl5.max(); parent5 = lvl5.idxmax()
    children5 = df[(df['cluster_0_name']==parent5[0]) &
                   (df['cluster_1_name']==parent5[1]) &
                   (df['cluster_2_name']==parent5[2]) &
                   (df['cluster_3_name']==parent5[3]) &
                   (df['cluster_4_name']==parent5[4])]['cluster_5_name'].dropna().unique().tolist()
    tokens5 = count_tokens(children5)
    print(f"Cluster 5 max breadth: {max5} under cluster_4 '{parent5[4]}' (path {parent5[:4]}), tokens if listed: {tokens5}")

    # Level 6: per (cluster_0..cluster_5)
    lvl6 = df.dropna(subset=['cluster_6_name']).groupby(
        ['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name','cluster_4_name','cluster_5_name']
    )['cluster_6_name'].nunique()
    max6 = lvl6.max(); parent6 = lvl6.idxmax()
    children6 = df[(df['cluster_0_name']==parent6[0]) &
                   (df['cluster_1_name']==parent6[1]) &
                   (df['cluster_2_name']==parent6[2]) &
                   (df['cluster_3_name']==parent6[3]) &
                   (df['cluster_4_name']==parent6[4]) &
                   (df['cluster_5_name']==parent6[5])]['cluster_6_name'].dropna().unique().tolist()
    tokens6 = count_tokens(children6)
    print(f"Cluster 6 max breadth: {max6} under cluster_5 '{parent6[5]}' (path {parent6[:5]}), tokens if listed: {tokens6}")

    # Level 7: per (cluster_0..cluster_6)
    lvl7 = df.dropna(subset=['cluster_7_name']).groupby(
        ['cluster_0_name','cluster_1_name','cluster_2_name','cluster_3_name','cluster_4_name','cluster_5_name','cluster_6_name']
    )['cluster_7_name'].nunique()
    max7 = lvl7.max(); parent7 = lvl7.idxmax()
    children7 = df[(df['cluster_0_name']==parent7[0]) &
                   (df['cluster_1_name']==parent7[1]) &
                   (df['cluster_2_name']==parent7[2]) &
                   (df['cluster_3_name']==parent7[3]) &
                   (df['cluster_4_name']==parent7[4]) &
                   (df['cluster_5_name']==parent7[5]) &
                   (df['cluster_6_name']==parent7[6])]['cluster_7_name'].dropna().unique().tolist()
    tokens7 = count_tokens(children7)
    print(f"Cluster 7 max breadth: {max7} under cluster_6 '{parent7[6]}' (path {parent7[:6]}), tokens if listed: {tokens7}")

if __name__ == "__main__":
    count_cluster_breadth(df)
