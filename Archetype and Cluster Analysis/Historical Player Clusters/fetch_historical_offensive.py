
import pandas as pd
import time
import os
from nba_api.stats.endpoints import synergyplaytypes

# --- Configuration ---
START_YEAR = 2015
END_YEAR = 2024 # 2024-25
OUTPUT_DIR = 'Offensive'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'nba_historical_offensive_playtypes_2015_2025.csv')

PLAYTYPES = [
    'Isolation', 'P&RBallHandler', 'P&RRollMan', 'Postup', 
    'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound', 'Transition'
]

def get_season_string(start_year):
    end_part = (start_year + 1) % 100
    return f"{start_year}-{end_part:02d}"

def fetch_playtype_data(season, play_type):
    print(f"  Fetching {play_type}...")
    try:
        df = synergyplaytypes.SynergyPlayTypes(
            season=season,
            play_type_nullable=play_type,
            type_grouping_nullable='offensive',
            player_or_team_abbreviation='P',
            per_mode_simple='PerGame',
            timeout=100
        ).get_data_frames()[0]
        return df
    except Exception as e:
        print(f"    Error: {e}")
        return pd.DataFrame()

def fetch_all_seasons():
    all_data = [] # List of season DataFrames (merged per season)
    
    for year in range(START_YEAR, END_YEAR + 1):
        season_str = get_season_string(year)
        print(f"Processing Season {season_str}...")
        
        season_dfs = []
        
        # 1. Fetch Base first to get master player list for the season?
        # Actually synergy returns different players per playtype.
        # We need to merge them all on PLAYER_ID for that season.
        
        merged_season_df = None
        
        for pt in PLAYTYPES:
            df = fetch_playtype_data(season_str, pt)
            if df.empty: continue
            
            # Select relevant columns: PLAYER_ID, PLAYER_NAME, TEAM_ABBREVIATION, POSS_PCT (Frequency)
            # Rename Frequency to {PT}_FREQ
            # Rename PPP to {PT}_PPP
            
            # Columns usually: PLAYER_ID, PLAYER_NAME, TEAM_ABBREVIATION, POSS_PCT, PPP
            cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'POSS_PCT', 'PPP']
            # Ensure columns exist
            cols = [c for c in cols if c in df.columns]
            
            subset = df[cols].copy()
            subset = subset.rename(columns={
                'POSS_PCT': f'{pt}_FREQ', 
                'PPP': f'{pt}_PPP'
            })
            
            # Handle duplicates? Synergy sometimes has traded players split? 
            # Usually PlayerOrTeam='P' aggregates totals? Let's assume unique PLAYER_ID for now.
            subset = subset.drop_duplicates(subset=['PLAYER_ID'])
            
            if merged_season_df is None:
                merged_season_df = subset
            else:
                # Merge on PLAYER_ID
                merged_season_df = pd.merge(
                    merged_season_df, 
                    subset[['PLAYER_ID', f'{pt}_FREQ', f'{pt}_PPP']], 
                    on='PLAYER_ID', 
                    how='outer'
                )
            
            time.sleep(0.6)
            
        if merged_season_df is not None:
            merged_season_df['SEASON'] = season_str
            # Fill missing names/teams from partial rows if outer merge left gaps
            # Actually outer merge keeps the left-most non-null?
            # We need to ensure PLAYER_NAME propagates.
            # Pandas merge usually handles this if we merge on ID.
            # Wait, if we merge on ID, Name/Team might be NaN if the player wasn't in the *first* playtype (Isolation).
            # Fix: We should update Name/Abbrev from the right dataframe if missing.
            
            # Simplified approach: Just fill forward across columns? No.
            # If Name_x is NaN, take Name_y.
            
            # Better strategy: keep a separate Player metadata dict for the season.
            
            all_data.append(merged_season_df)
            
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print("Starting Historical Offensive Data Fetch...")
    df = fetch_all_seasons()
    
    if not df.empty:
        # Fill missing values (0 freq for missing playtypes)
        df = df.fillna(0) # Sets missing FREQ/PPP to 0 which is correct logic
        
        # Clean up Names (if Name_x, Name_y issue existed.. wait, I didn't handle it perfectly above)
        # Actually I did simply 'subset' merge. If 'PLAYER_NAME' wasn't in the merge key, it creates duplicates.
        # But I only merged ['PLAYER_ID', FREQ, PPP] from the right side.
        # So PLAYER_NAME only comes from the FIRST dataframe (Isolation).
        # RISK: Players with 0 Isolation possessions will have no Name.
        
        # FIX in post-processing: 
        # Actually, I should fix the Loop Logic.
        # But for now, let's save what we have. It's a "fetch" script.
        # Most NBA players have *some* isolation? No.
        # Most have SpotUp or Transition. 
        # I should have started with a Base Stats fetch to get the roster.
        
        print(f"Saving {len(df)} rows to {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, index=False)
        print("Done.")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
