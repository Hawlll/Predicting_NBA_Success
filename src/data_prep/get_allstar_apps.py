import pandas as pd

def get_allstar_apps(allstar_fp, start_year, end_year):
    
    allstar_df = pd.read_csv(allstar_fp)
    
    # Filter by start and end year and NBA league players only
    allstar_df = allstar_df[(allstar_df["season"] >= start_year) & (allstar_df["season"] <= end_year) & (allstar_df["lg"] == "NBA")]
    
    # Group by player and count appearances
    allstar_apps = allstar_df.groupby("player").size().reset_index(name="allstar_apps")

    # Rename player column to PLAYER
    allstar_apps = allstar_apps.rename(columns={"player": "PLAYER"})
    
    return allstar_apps.drop_duplicates(subset=["PLAYER"])
