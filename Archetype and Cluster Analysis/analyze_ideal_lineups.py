
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashlineups
import numpy as np

# --- Configuration ---
SEASON = '2024-25'
MIN_MINUTES = 80
OUTPUT_FILE = 'ideal_lineup_compositions.csv'

# Input Files
FILE_PLAYER_OFF = 'nba_player_clusters_offensive.csv'
FILE_PLAYER_DEF = 'nba_defensive_clusters.csv'
FILE_TEAM = 'nba_team_clusters.csv'

def load_reference_data():
    print("Loading reference data...")
    try:
        off_df = pd.read_csv(FILE_PLAYER_OFF)
        def_df = pd.read_csv(FILE_PLAYER_DEF)
        team_df = pd.read_csv(FILE_TEAM)
        
        off_map = off_df.set_index('PLAYER_ID')['Archetype_Name'].to_dict()
        def_map = def_df.set_index('PLAYER_ID')['Archetype_Name'].to_dict()
        team_map = team_df.set_index('TEAM_ID')['Playstyle_Name'].to_dict()
        
        return off_map, def_map, team_map
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None

def fetch_successful_lineups():
    print(f"Fetching Lineups (> {MIN_MINUTES} mins, Postive Net Rating)...")
    try:
        # Using Base Plus_Minus as proxy for Net Rating > 0 check
        lineups = leaguedashlineups.LeagueDashLineups(
            season=SEASON,
            group_quantity=5,
            measure_type_detailed_defense='Base',
            timeout=100
        ).get_data_frames()[0]
        
        filtered = lineups[
            (lineups['MIN'] >= MIN_MINUTES) & 
            (lineups['PLUS_MINUS'] > 0)
        ].copy()
        
        print(f"Found {len(filtered)} successful lineups.")
        return filtered
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def get_ideal_composition_list(series_of_lists, n_slots=5):
    """
    Given a series of lists (one list of 5 archetypes per lineup),
    calculate the aggregate 'Ideal 5'.
    Method: Calculate mean frequency of each archetype, then fill 5 slots proportionally.
    """
    # Flatten to get raw counts across all lineups
    all_items = []
    for l in series_of_lists:
        all_items.extend(l)
        
    if not all_items: return ["N/A"] * 5
    
    # Calculate average count per lineup
    n_lineups = len(series_of_lists)
    counts = pd.Series(all_items).value_counts()
    avg_per_lineup = counts / n_lineups
    
    # We want to construct a list of 5 players that maximizes these averages
    # Strategy: Round the averages to nearest whole number, then adjust to sum to 5?
    # Or just iterate: Pick highest average, subtract 1, repeat 5 times?
    
    final_list = []
    remaining_avgs = avg_per_lineup.copy()
    
    for _ in range(5):
        if remaining_avgs.empty or remaining_avgs.max() <= 0:
            final_list.append("Any/Versatile")
            continue
            
        best = remaining_avgs.idxmax()
        final_list.append(best)
        remaining_avgs[best] -= 1 # "Use" one instance of this archetype
        
    return final_list

def analyze_ideal_lineups(lineups_df, off_map, def_map, team_map):
    print("Analyzing compositions...")
    
    # Storage
    # Playstyle -> List of [List of 5 OFF Archetypes]
    style_off_data = {}
    style_def_data = {}
    
    for _, row in lineups_df.iterrows():
        team_id = row['TEAM_ID']
        playstyle = team_map.get(team_id, "Unknown")
        if playstyle == "Unknown": continue
        
        # Parse IDs
        raw_ids = row['GROUP_ID'].strip('-').split('-')
        pids = [int(p) for p in raw_ids if p]
        
        if len(pids) != 5: continue
        
        # Get Archetypes for this lineup
        lineup_off = [off_map.get(p, "Replacement/Unknown") for p in pids]
        lineup_def = [def_map.get(p, "Replacement/Unknown") for p in pids]
        
        if playstyle not in style_off_data:
            style_off_data[playstyle] = []
            style_def_data[playstyle] = []
            
        style_off_data[playstyle].append(lineup_off)
        style_def_data[playstyle].append(lineup_def)
        
    # Build Result DataFrame
    results = []
    
    for style in style_off_data.keys():
        off_lineups = style_off_data[style]
        def_lineups = style_def_data[style]
        
        # Calc Ideal 5
        ideal_off = get_ideal_composition_list(off_lineups)
        ideal_def = get_ideal_composition_list(def_lineups)
        
        row = {'Playstyle': style, 'Lineups_Analyzed': len(off_lineups)}
        
        for i in range(5):
            row[f'OFF_Slot_{i+1}'] = ideal_off[i]
            row[f'DEF_Slot_{i+1}'] = ideal_def[i]
            
        results.append(row)
        
    return pd.DataFrame(results)

def main():
    off_map, def_map, team_map = load_reference_data()
    if not off_map: return
    
    lineups = fetch_successful_lineups()
    if lineups.empty: return
    
    df = analyze_ideal_lineups(lineups, off_map, def_map, team_map)
    
    # Sort columns
    cols = ['Playstyle', 'Lineups_Analyzed'] + \
           [f'OFF_Slot_{i+1}' for i in range(5)] + \
           [f'DEF_Slot_{i+1}' for i in range(5)]
    
    df = df[cols]
    
    print("-" * 30)
    print(df.head())
    print("-" * 30)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
