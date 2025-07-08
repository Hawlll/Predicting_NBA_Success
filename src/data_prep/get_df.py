import pandas as pd

from get_allstar_apps import get_allstar_apps
from get_college_data import get_college_data
from get_nba_stats import get_nba_player_impact_data

def get_abbriviated_names(player_name):

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

    #replace player names with abbreviated names

    # allstar_apps["PLAYER"] = allstar_apps["PLAYER"].apply(get_abbriviated_names)

    # college_data["PLAYER"] = college_data["PLAYER"].apply(get_abbriviated_names)

    # nba_stats["PLAYER"] = nba_stats["PLAYER"].apply(get_abbriviated_names)

    # Merge allstar appearances with college data
    college_data = pd.merge(college_data, allstar_apps, on="PLAYER", how="left")

    # Fill allstar_app NaN values with 0
    college_data["allstar_apps"] = college_data["allstar_apps"].fillna(0)

    # Merge college data with NBA stats
    df = pd.merge(college_data, nba_stats, on="PLAYER", how="inner")
    
    return df.drop_duplicates(subset=["PLAYER"])
