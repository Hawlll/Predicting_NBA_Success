import pandas as pd
from get_allstar_apps import get_allstar_apps
from get_college_data import get_college_data
from get_nba_stats import get_nba_player_impact_data

def get_abbreviated_names(player_name):
    parts = player_name.split(" ")
    if len(parts) == 2:
        return f"{parts[0][0]}. {parts[1]}"
    elif len(parts) > 2:
        return f"{parts[0][0]}. {'. '.join(parts[1:-1])} {parts[-1]}"
    return player_name

def get_df(allstar_fp, college_fp, nba_stats_fp, draft_fp, start_year, end_year):
    allstar_apps = get_allstar_apps(allstar_fp, start_year, end_year)
    college_data = get_college_data(college_fp, draft_fp, start_year, end_year)
    nba_stats = get_nba_player_impact_data(nba_stats_fp, start_year, end_year+5)
    
    # Merge allstar appearances with college data
    college_data = pd.merge(college_data, allstar_apps, on="PLAYER", how="left")
    college_data["allstar_apps"] = college_data["allstar_apps"].fillna(0)
    
    # Merge college data with NBA stats
    df = pd.merge(college_data, nba_stats, on="PLAYER", how="inner")
    
    return df.drop_duplicates(subset=["PLAYER"])

# Load the data
chuzz = get_df("Predicting_NBA_Success/src/data_prep/All-Star Selections.csv",
               "Predicting_NBA_Success/src/data_prep/CollegeBasketballPlayers2009-2021 2.csv",
               "Predicting_NBA_Success/src/data_prep/NBA_Dataset 2.csv",
               "Predicting_NBA_Success/src/data_prep/DraftedPlayers2009-2021.xlsx",
               2010, 2019)

print(f"Original dataset: {chuzz.shape}")

# FILTER TOP AND BOTTOM 2% BY WIN SHARES
print("\nFiltering by NBA Win Shares...")

if 'Highest_WS' in chuzz.columns:
    # Convert to numeric
    chuzz['Highest_WS'] = pd.to_numeric(chuzz['Highest_WS'], errors='coerce')
    
    # Calculate percentiles
    ws_2nd = chuzz['Highest_WS'].quantile(0.02)
    ws_98th = chuzz['Highest_WS'].quantile(0.98)
    
    print(f"Win Shares range: {chuzz['Highest_WS'].min():.2f} to {chuzz['Highest_WS'].max():.2f}")
    print(f"2nd percentile: {ws_2nd:.2f}")
    print(f"98th percentile: {ws_98th:.2f}")
    
    # Apply filter
    chuzz_filtered = chuzz[(chuzz['Highest_WS'] > ws_2nd) & (chuzz['Highest_WS'] < ws_98th)].copy()
    
    print(f"Filtered dataset: {chuzz_filtered.shape}")
    print(f"Removed: {len(chuzz) - len(chuzz_filtered)} players")
    
    # Save filtered dataset
    chuzz_filtered.to_csv("filtered_nba_dataset.csv", index=False)
    print("Filtered dataset saved!")
    
else:
    print("No Win Shares column found - filtering by college BPM instead...")
    
    chuzz['bpm'] = pd.to_numeric(chuzz['bpm'], errors='coerce')
    
    bmp_2nd = chuzz['bpm'].quantile(0.02)
    bmp_98th = chuzz['bmp'].quantile(0.98)
    
    chuzz_filtered = chuzz[(chuzz['bmp'] > bmp_2nd) & (chuzz['bmp'] < bmp_98th)].copy()
    
    print(f"Filtered by college BPM: {chuzz_filtered.shape}")
    chuzz_filtered.to_csv("filtered_nba_dataset.csv", index=False)