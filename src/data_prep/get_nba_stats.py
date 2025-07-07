import pandas as pd
import numpy as np

def filter_data_by_years(data, start_year=None, end_year=None):
    if start_year is None and end_year is None:
        return data

    if 'season' not in data.columns:
        return data

    data['szn_numeric'] = pd.to_numeric(data['season'], errors='coerce')
    
    if start_year is not None:
        data = data[data['szn_numeric'] >= start_year]
    if end_year is not None:
        data = data[data['szn_numeric'] <= end_year]
        
    return data

def load_data(file_path, start_year=None, end_year=None):
    try:
        data = pd.read_csv(file_path)
        
        unique_cols = ['player', 'season', 'team_id'] 
        
        data.drop_duplicates(subset=unique_cols, keep='first', inplace=True)

        filtered_data = filter_data_by_years(data, start_year=start_year, end_year=end_year)
        if filtered_data is None or len(filtered_data) == 0:
            return None
        return filtered_data
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

def check_required_stats(data):
    # Core stats needed for PIE calculation (per-game versions)
    needed_per_g_stats = [
        "pts_per_g", 'fg_per_g', 'fga_per_g', 'ft_per_g', 'fta_per_g', 
        'ast_per_g', 'stl_per_g', 'blk_per_g', 'tov_per_g', 'pf_per_g', 'g'
    ]
    
    missing_core_stats = []
    for stat_code in needed_per_g_stats:
        if stat_code not in data.columns:
            missing_core_stats.append(stat_code)
            
    rebound_found = False
    if 'orb_per_g' in data.columns and 'drb_per_g' in data.columns:
        rebound_found = True
    elif 'trb_per_g' in data.columns:
        rebound_found = True
    
    if not rebound_found:
        missing_core_stats.append('rebounds (orb_per_g/drb_per_g or trb_per_g)')
        
    if missing_core_stats:
        print(f"Error: Missing the following *core* required statistics in the data: {', '.join(missing_core_stats)}")
        return False
        
    return True

def calculate_pie_scores(data):
    data = data.copy()
    
    per_g_stats = {
        'pts_per_g': 'pts', 'fg_per_g': 'fg', 'fga_per_g': 'fga',
        'ft_per_g': 'ft', 'fta_per_g': 'fta', 'ast_per_g': 'ast',
        'stl_per_g': 'stl', 'blk_per_g': 'blk', 'tov_per_g': 'tov',
        'pf_per_g': 'pf'
    }

    # Convert per-game stats to total stats for PIE calculation
    for pg_col, total_col in per_g_stats.items():
        if pg_col in data.columns and 'g' in data.columns:
            data[total_col] = pd.to_numeric(data[pg_col], errors='coerce').fillna(0) * pd.to_numeric(data['g'], errors='coerce').fillna(0)
        else:
            data[total_col] = 0 # Default to 0 if per-game stat or games played is missing

    # Handle rebounds, converting per-game to total
    if 'orb_per_g' in data.columns and 'drb_per_g' in data.columns and 'g' in data.columns:
        data['oreb'] = pd.to_numeric(data['orb_per_g'], errors='coerce').fillna(0) * pd.to_numeric(data['g'], errors='coerce').fillna(0)
        data['dreb'] = pd.to_numeric(data['drb_per_g'], errors='coerce').fillna(0) * pd.to_numeric(data['g'], errors='coerce').fillna(0)
    elif 'trb_per_g' in data.columns and 'g' in data.columns:
        total_trb = pd.to_numeric(data['trb_per_g'], errors='coerce').fillna(0) * pd.to_numeric(data['g'], errors='coerce').fillna(0)
        data['oreb'] = total_trb * 0.25
        data['dreb'] = total_trb * 0.75
    else:
        data['oreb'] = 0
        data['dreb'] = 0
    
    results_list = []
    
    if 'team_id' not in data.columns or 'season' not in data.columns or 'player' not in data.columns:
        return None

    for (team, season), team_data in data.groupby(['team_id', 'season']):
        if len(team_data) == 0:
            continue
            
        team_pts = team_data['pts'].sum()
        team_fgm = team_data['fg'].sum()
        team_fga = team_data['fga'].sum()
        team_ftm = team_data['ft'].sum()
        team_fta = team_data['fta'].sum()
        team_dreb = team_data['dreb'].sum()
        team_oreb = team_data['oreb'].sum()
        team_ast = team_data['ast'].sum()
        team_stl = team_data['stl'].sum()
        team_blk = team_data['blk'].sum()
        team_pf = team_data['pf'].sum()
        team_tov = team_data['tov'].sum()
        
        team_pie_total_denominator = (team_pts + team_fgm + team_ftm - team_fga - team_fta +
                                      team_dreb + (team_oreb * 0.5) + team_ast + team_stl +
                                      (team_blk * 0.5) - team_pf - team_tov)
        
        if team_pie_total_denominator <= 0:
            for _, player in team_data.iterrows():
                player_result = player.copy()
                player_result['PIE_Score'] = np.nan
                player_result['Player_Events_Numerator'] = np.nan
                player_result['Team_Total_Events_Denominator'] = np.nan
                if 'ws' in player: player_result['ws'] = player['ws']
                if 'bpm' in player: player_result['bpm'] = player['bpm']
                results_list.append(player_result)
            continue
            
        for _, player in team_data.iterrows():
            player_pie_numerator = (player['pts'] + player['fg'] + player['ft'] -
                                    player['fga'] - player['fta'] + player['dreb'] +
                                    (player['oreb'] * 0.5) + player['ast'] + player['stl'] +
                                    (player['blk'] * 0.5) - player['pf'] - player['tov'])
            
            pie_score = (player_pie_numerator / team_pie_total_denominator) * 100
            
            player_result = player.copy()
            player_result['PIE_Score'] = pie_score
            player_result['Player_Events_Numerator'] = player_pie_numerator
            player_result['Team_Total_Events_Denominator'] = team_pie_total_denominator
            
            if 'ws' in player:
                player_result['ws'] = player['ws']
            if 'bpm' in player:
                player_result['bpm'] = player['bpm']

            results_list.append(player_result)
    
    results = pd.DataFrame(results_list)
    if len(results) == 0:
        return None
    
    return results

def calculate_career_pie_scores(player_season_pies):
    if player_season_pies is None or player_season_pies.empty:
        return pd.DataFrame()

    agg_dict = {
        'career_player_events_numerator': ('Player_Events_Numerator', 'sum'),
        'career_team_total_events_denominator': ('Team_Total_Events_Denominator', 'sum'),
        'total_games': ('g', 'sum')
    }
    
    if 'ws' in player_season_pies.columns:
        agg_dict['highest_ws'] = ('ws', 'max')
    if 'bpm' in player_season_pies.columns:
        agg_dict['highest_bpm'] = ('bpm', 'max')

    career_data = player_season_pies.groupby('player').agg(**agg_dict).reset_index()

    career_data['All_Time_PIE_Score'] = np.where(
        career_data['career_team_total_events_denominator'] > 0,
        (career_data['career_player_events_numerator'] / career_data['career_team_total_events_denominator']) * 100,
        np.nan
    )

    player_season_min_max = player_season_pies.groupby('player')['season'].agg(['min', 'max']).reset_index()
    career_data = pd.merge(career_data, player_season_min_max, on='player', how='left')
    career_data.rename(columns={'min': 'First_Season', 'max': 'Last_Season'}, inplace=True)

    return career_data

def get_nba_player_impact_data(file_path, start_year=None, end_year=None):
    nba_data = load_data(file_path, start_year, end_year)
    if nba_data is None:
        return pd.DataFrame()
    
    if not check_required_stats(nba_data):
        return pd.DataFrame()
    
    results = calculate_pie_scores(nba_data)
    if results is None:
        return pd.DataFrame()

    all_time_pie_scores = calculate_career_pie_scores(results)
    
    if all_time_pie_scores.empty:
        return pd.DataFrame()

    # --- START OF FIX ---
    # Sort the DataFrame by the numeric PIE score FIRST
    all_time_pie_scores_sorted = all_time_pie_scores.sort_values(
        'All_Time_PIE_Score', ascending=False
    ).reset_index(drop=True)

    # Create the formatted 'Overall PIE' column from the sorted data
    all_time_pie_scores_sorted['Overall PIE'] = all_time_pie_scores_sorted['All_Time_PIE_Score'].round(4).apply(
        lambda x: f"{x:.4f}" if pd.notna(x) else 'N/A'
    )

    # Define the columns for the final display DataFrame
    final_df_columns = ['player']
    if 'highest_ws' in all_time_pie_scores_sorted.columns: # Check on the sorted df
        final_df_columns.append('highest_ws')
    if 'highest_bpm' in all_time_pie_scores_sorted.columns: # Check on the sorted df
        final_df_columns.append('highest_bpm')
    final_df_columns.append('Overall PIE') # This is the formatted string column
    
    # Select the desired columns from the already sorted DataFrame
    final_df = all_time_pie_scores_sorted[final_df_columns]

    # Rename columns for presentation
    display_column_names = {
        'player': 'PLAYER',
        'highest_ws': 'Highest_WS',
        'highest_bpm': 'Highest_BPM',
    }
    final_df = final_df.rename(columns=display_column_names)
    # --- END OF FIX ---

    return final_df
