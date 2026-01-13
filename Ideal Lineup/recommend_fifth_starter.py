
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashlineups
from collections import Counter

# --- Configuration ---
SEASON = '2024-25'
OUTPUT_FILE = 'lineup_recommendations.csv'

# Input Files
FILE_PLAYER_OFF = 'nba_player_clusters_offensive.csv'
FILE_PLAYER_DEF = 'nba_defensive_clusters.csv' 
FILE_TEAM = 'nba_team_clusters.csv'
FILE_IDEAL = 'ideal_lineup_compositions.csv'

def load_reference_data():
    print("Loading reference data...")
    try:
        off_df = pd.read_csv(FILE_PLAYER_OFF)
        def_df = pd.read_csv(FILE_PLAYER_DEF)
        team_df = pd.read_csv(FILE_TEAM)
        ideal_df = pd.read_csv(FILE_IDEAL)
        
        # Mappings
        off_map = off_df.set_index('PLAYER_ID')['Archetype_Name'].to_dict()
        def_map = def_df.set_index('PLAYER_ID')['Archetype_Name'].to_dict()
        team_map = team_df.set_index('TEAM_ID')['Playstyle_Name'].to_dict()
        
        # Parse Ideal Compositions into easier structure
        # Dict: Playstyle -> {'OFF': [list of 5], 'DEF': [list of 5]}
        ideal_map = {}
        for _, row in ideal_df.iterrows():
            style = row['Playstyle']
            off_list = [row[f'OFF_Slot_{i+1}'] for i in range(5)]
            def_list = [row[f'DEF_Slot_{i+1}'] for i in range(5)]
            ideal_map[style] = {'OFF': off_list, 'DEF': def_list}
            
        return off_map, def_map, team_map, ideal_map
        
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None, None

def fetch_4man_lineups():
    print(f"Fetching 4-Man Lineups ({SEASON})...")
    try:
        lineups = leaguedashlineups.LeagueDashLineups(
            season=SEASON,
            group_quantity=4,
            measure_type_detailed_defense='Base',
            timeout=100
        ).get_data_frames()[0]
        
        # Filter for basic relevance (e.g. > 50 mins? or just sort by impact?)
        # Let's verify sample size isn't tiny.
        lineups = lineups[lineups['MIN'] > 50].copy()
        
        return lineups
    except Exception as e:
        print(f"Error fetching lineups: {e}")
        return pd.DataFrame()

def get_recommendations(current_list, ideal_list):
    """
    Returns a list of archetypes that are in Ideal but missing from Current.
    """
    ideal_counts = Counter(ideal_list)
    current_counts = Counter(current_list)
    
    missing = []
    # Subtract current from ideal
    diff = ideal_counts - current_counts
    
    for archetype, count in diff.items():
        missing.extend([archetype] * count)
        
    if not missing:
        return ["None / Fit is Perfect"]
        
    return list(set(missing)) # Return unique missing options to keep it clean

def generate_analysis(lineups_df, off_map, def_map, team_map, ideal_map):
    print("Generating Recommendations...")
    
    results = []
    
    # Process per Team
    teams = lineups_df['TEAM_ID'].unique()
    
    for team_id in teams:
        team_lineups = lineups_df[lineups_df['TEAM_ID'] == team_id].copy()
        
        # Rank by Plus_Minus (Total Impact)
        team_lineups = team_lineups.sort_values('PLUS_MINUS', ascending=False)
        
        # Take Top 5
        top_5 = team_lineups.head(5)
        
        playstyle = team_map.get(team_id, "Unknown")
        ideal_comp = ideal_map.get(playstyle)
        
        if not ideal_comp: continue
        
        for _, row in top_5.iterrows():
            # Parse Players
            raw_ids = row['GROUP_ID'].strip('-').split('-')
            pids = [int(p) for p in raw_ids if p]
            
            curr_off = [off_map.get(p, "Unknown") for p in pids]
            curr_def = [def_map.get(p, "Unknown") for p in pids]
            
            # Get Recommendations
            rec_off = get_recommendations(curr_off, ideal_comp['OFF'])
            rec_def = get_recommendations(curr_def, ideal_comp['DEF'])
            
            results.append({
                'Team': row['TEAM_ABBREVIATION'],
                'Team_Playstyle': playstyle,
                'Lineup_Name': row['GROUP_NAME'],
                'Minutes': row['MIN'],
                'Plus_Minus': row['PLUS_MINUS'],
                'Current_OFF_Archetypes': ", ".join(curr_off),
                'Current_DEF_Archetypes': ", ".join(curr_def),
                'Rec_Add_OFF': ", ".join(rec_off),
                'Rec_Add_DEF': ", ".join(rec_def)
            })
            
    return pd.DataFrame(results)

def main():
    # 1. Load Reference
    off_map, def_map, team_map, ideal_map = load_reference_data()
    if not off_map: return
    
    # 2. Fetch Lineups
    lineups_df = fetch_4man_lineups()
    if lineups_df.empty: return
    
    # 3. Analyze
    rec_df = generate_analysis(lineups_df, off_map, def_map, team_map, ideal_map)
    
    # 4. Save
    print(f"Saving {len(rec_df)} recommendations to {OUTPUT_FILE}...")
    rec_df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
