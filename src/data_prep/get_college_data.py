import pandas as pd

def _get_best_year(college_df):
    
    college_df = college_df.sort_values(by=["bpm"], ascending=False)
    college_df = college_df.drop_duplicates(subset=["player_name"])
    return college_df

def get_college_data(college_fp, draft_fp, start_year, end_year, college_metrics_features=[]):

    drafted_df = pd.read_excel(draft_fp)
    college_df = pd.read_csv(college_fp)

    #Filter by start and end year
    drafted_df = drafted_df[(drafted_df["YEAR"] >= start_year) & (drafted_df["YEAR"] <= end_year)]
    college_df = college_df[(college_df["year"] >= start_year) & (college_df["year"] <= end_year)]

    #for duplicates player names, keep the best performing year
    college_df = _get_best_year(college_df)

    #Rename player_name col and select desired features
    college_df = college_df.rename(columns={"player_name": "PLAYER"})
    if college_metrics_features:

        college_df = college_df[college_metrics_features]

    merged_df = pd.merge(college_df, drafted_df, on="PLAYER", how="inner")

    return merged_df.dropna().drop_duplicates(subset=["PLAYER"])

