import pandas as pd
import warnings
from get_allstar_apps import get_allstar_apps
from get_college_data import get_college_data
from get_nba_stats import get_nba_player_impact_data

# Suppress the DtypeWarning for cleaner output
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)

def get_abbreviated_names(player_name):
    parts = player_name.split(" ")
    if len(parts) == 2:
        return f"{parts[0][0]}. {parts[1]}"
    elif len(parts) > 2:
        return f"{parts[0][0]}. {'. '.join(parts[1:-1])} {parts[-1]}"
    return player_name

def assign_position_group(pos):
    guards = ["PG", "SG", "G"]
    forwards = ["SF", "PF", "F"]
    centers = ["C"]
    if pos in guards:
        return "Guard"
    elif pos in forwards:
        return "Forward"
    elif pos in centers:
        return "Center"
    else:
        return "Other"

def assign_position_by_height(height):
    """Assign position based on height (rough approximation)"""
    try:
        # Handle date-formatted heights (Excel conversion issue)
        if isinstance(height, str):
            if "Jun" in height:
                # Handle both "10-Jun" and "Jun-00" formats
                if height.startswith("Jun"):
                    # "Jun-00" means 6'0"
                    total_inches = 6 * 12
                else:
                    # "10-Jun" means 6'10", "5-Jun" means 6'5", etc.
                    inches_part = int(height.split("-")[0])
                    total_inches = 6 * 12 + inches_part
            elif "Jul" in height:
                # "Jul-00" means 7'0"
                total_inches = 7 * 12
            elif "May" in height:
                # Handle both "11-May" and "May-##" formats
                if height.startswith("May"):
                    # "May-##" would be 5'##"
                    inches_part = int(height.split("-")[1]) if "-" in height and height.split("-")[1].isdigit() else 0
                    total_inches = 5 * 12 + inches_part
                else:
                    # "11-May" means 5'11", "9-May" means 5'9", etc.
                    inches_part = int(height.split("-")[0])
                    total_inches = 5 * 12 + inches_part
            elif "Aug" in height:
                # "Aug-##" would be 8'##" (very tall)
                inches_part = int(height.split("-")[1]) if "-" in height else 0
                total_inches = 8 * 12 + inches_part
            elif "'" in height:
                # Standard feet-inches format like "6'5""
                feet, inches = height.split("'")
                feet = int(feet)
                inches = int(inches.replace('"', '').strip()) if inches.replace('"', '').strip() else 0
                total_inches = feet * 12 + inches
            else:
                total_inches = float(height)
        else:
            total_inches = float(height)
        
        # Position assignment based on height
        if total_inches <= 74:  # 6'2" and under
            return "Guard"
        elif total_inches <= 79:  # 6'3" to 6'7"
            return "Forward"
        else:  # 6'8" and above
            return "Center"
    except Exception as e:
        # Silently handle errors and return "Other"
        return "Other"

def get_df(allstar_fp, college_fp, nba_stats_fp, draft_fp, start_year, end_year, position_fp=None):
    # Get individual datasets
    allstar_apps = get_allstar_apps(allstar_fp, start_year, end_year)
    college_data = get_college_data(college_fp, draft_fp, start_year, end_year)
    nba_stats = get_nba_player_impact_data(nba_stats_fp, start_year, end_year)
    
    # Debug: Print column names
    print("college_data columns:", college_data.columns.tolist())
    print("nba_stats columns:", nba_stats.columns.tolist())
    print("allstar_apps columns:", allstar_apps.columns.tolist())
    
    # Merge allstar appearances with college data
    college_data = pd.merge(college_data, allstar_apps, on="PLAYER", how="left")
    college_data["allstar_apps"] = college_data["allstar_apps"].fillna(0)
    
    # Merge with NBA stats
    df = pd.merge(college_data, nba_stats, on="PLAYER", how="inner")
    
    # Optional 
    if position_fp:
        try:
            position_data = pd.read_csv(position_fp, low_memory=False)
            print("position_data columns:", position_data.columns.tolist())
            df = pd.merge(df, position_data, on="PLAYER", how="left")
            print("Merged with position data successfully!")
        except Exception as e:
            print(f"Could not load position data: {e}")
    
    print("Final merged columns:", df.columns.tolist())
    
    # Check position column variations
    pos_columns = [col for col in df.columns if 'pos' in col.lower()]
    print("Position-related columns found:", pos_columns)
    
    # assigning position group using column or height
    if "pos" in df.columns:
        df["pos_group"] = df["pos"].apply(assign_position_group)
        print("Position group distribution:")
        print(df["pos_group"].value_counts())
    elif "POS" in df.columns:
        df["pos_group"] = df["POS"].apply(assign_position_group)
        print("Position group distribution:")
        print(df["pos_group"].value_counts())
    elif "position" in df.columns:
        df["pos_group"] = df["position"].apply(assign_position_group)
        print("Position group distribution:")
        print(df["pos_group"].value_counts())
    elif "ht" in df.columns:
        print("No position column found. Using height to estimate positions...")
        df["pos_group"] = df["ht"].apply(assign_position_by_height)
        print("Position group distribution (based on height):")
        print(df["pos_group"].value_counts())
        print("Sample height-to-position assignments:")
        print(df[["PLAYER", "ht", "pos_group"]].head(10))
    else:
        print("No position column or height column found in data.")
        print("You may need to add a position column or check your data sources.")
    
    return df.drop_duplicates(subset=["PLAYER"])

def print_all_players():
    # Get the dataset
    df = get_df(
        allstar_fp="src/data_prep/All-Star Selections.csv",
        college_fp="src/data_prep/CollegeBasketballPlayers2009-2021 2.csv",
        nba_stats_fp="src/data_prep/NBA_Dataset 3.csv",
        draft_fp="src/data_prep/DraftedPlayers2009-2021.xlsx",
        start_year=2010,
        end_year=2019
    )
    
    print("="*100)
    print(f"ALL {len(df)} PLAYERS IN THE DATASET")
    print("="*100)
    print()
    
    # position group sort, then by NBA metrics
    df_sorted = df.sort_values(['pos_group', 'Highest_WS'], ascending=[True, False])
    
    # header
    print(f"{'#':<3} {'PLAYER':<25} {'POSITION':<8} {'HEIGHT':<8} {'COLLEGE':<20} {'DRAFT':<6} {'ALL-STAR':<9} {'WIN SHARES':<11} {'BPM':<8} {'PIE':<8}")
    print("-" * 100)
    
    for idx, row in df_sorted.iterrows():
        # Format
        rank = df_sorted.index.get_loc(idx) + 1
        player = row['PLAYER'][:24] if len(row['PLAYER']) > 24 else row['PLAYER']
        position = row['pos_group']
        height = str(row['ht'])
        college = str(row['team'])[:19] if pd.notna(row['team']) else 'N/A'
        draft_pick = str(int(row['pick'])) if pd.notna(row['pick']) else 'Undrafted'
        allstar = str(int(row['allstar_apps'])) if pd.notna(row['allstar_apps']) else '0'
        
        # Handle numeric formatting
        try:
            win_shares = f"{float(row['Highest_WS']):.1f}" if pd.notna(row['Highest_WS']) else 'N/A'
        except (ValueError, TypeError):
            win_shares = str(row['Highest_WS'])[:10] if pd.notna(row['Highest_WS']) else 'N/A'
            
        try:
            bpm = f"{float(row['Highest_BPM']):.1f}" if pd.notna(row['Highest_BPM']) else 'N/A'
        except (ValueError, TypeError):
            bpm = str(row['Highest_BPM'])[:7] if pd.notna(row['Highest_BPM']) else 'N/A'
            
        try:
            pie = f"{float(row['Overall PIE']):.3f}" if pd.notna(row['Overall PIE']) else 'N/A'
        except (ValueError, TypeError):
            pie = str(row['Overall PIE'])[:7] if pd.notna(row['Overall PIE']) else 'N/A'
        
        print(f"{rank:<3} {player:<25} {position:<8} {height:<8} {college:<20} {draft_pick:<6} {allstar:<9} {win_shares:<11} {bpm:<8} {pie:<8}")
    
    print("-" * 100)
    print()
    
    # Print summary stats
    print("SUMMARY STATISTICS:")
    print("-" * 50)
    print(f"Total Players: {len(df)}")
    print(f"Guards: {len(df[df['pos_group'] == 'Guard'])}")
    print(f"Forwards: {len(df[df['pos_group'] == 'Forward'])}")
    print(f"Centers: {len(df[df['pos_group'] == 'Center'])}")
    print(f"Other: {len(df[df['pos_group'] == 'Other'])}")
    print()
    print(f"All-Stars: {len(df[df['allstar_apps'] > 0])}")
    
    # Safe numeric calculations
    try:
        avg_ws = pd.to_numeric(df['Highest_WS'], errors='coerce').mean()
        print(f"Average Win Shares: {avg_ws:.2f}")
    except:
        print("Average Win Shares: Could not calculate")
        
    try:
        avg_bpm = pd.to_numeric(df['Highest_BPM'], errors='coerce').mean()
        print(f"Average BPM: {avg_bpm:.2f}")
    except:
        print("Average BPM: Could not calculate")
        
    try:
        avg_pie = pd.to_numeric(df['Overall PIE'], errors='coerce').mean()
        print(f"Average PIE: {avg_pie:.3f}")
    except:
        print("Average PIE: Could not calculate")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    print_all_players()