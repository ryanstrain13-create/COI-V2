
import pandas as pd
import time
import os
from nba_api.stats.endpoints import leaguedashptdefend, leaguehustlestatsplayer

# --- Configuration ---
START_YEAR = 2015
END_YEAR = 2024
OUTPUT_DIR = 'Defensive'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'nba_historical_defensive_stats_2015_2025.csv')

def get_season_string(start_year):
    end_part = (start_year + 1) % 100
    return f"{start_year}-{end_part:02d}"

def standardize_columns(df, preferred_id='PLAYER_ID'):
    """Ensures PLAYER_ID exists, renaming alternatives like CLOSE_DEF_PERSON_ID."""
    if df.empty: return df
    
    # Common variations in Defense Dashboard
    col_map = {
        'CLOSE_DEF_PERSON_ID': 'PLAYER_ID',
        'Player_ID': 'PLAYER_ID',
        'person_id': 'PLAYER_ID'
    }
    df = df.rename(columns=col_map)
    return df

def fetch_defense_dashboard(season):
    print(f"  Fetching Defense Dashboard (Overall) for {season}...")
    try:
        df = leaguedashptdefend.LeagueDashPtDefend(
            season=season,
            defense_category='Overall',
            per_mode_simple='PerGame',
            timeout=100
        ).get_data_frames()[0]
        
        df = standardize_columns(df)
        return df
    except Exception as e:
        print(f"    Error fetching Defense Dashboard: {e}")
        return pd.DataFrame()

def fetch_hustle_stats(season):
    start_year_int = int(season[:4])
    if start_year_int < 2016:
        # Hustle stats not reliably available before 2016-17
        return pd.DataFrame()
        
    print(f"  Fetching Hustle Stats for {season}...")
    try:
        df = leaguehustlestatsplayer.LeagueHustleStatsPlayer(
            season=season,
            per_mode_time='PerGame',
            timeout=100
        ).get_data_frames()[0]
        
        df = standardize_columns(df)
        # Select key columns if they exist
        cols_to_keep = ['PLAYER_ID', 'CONTESTED_SHOTS', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT', 'DEF_LOOSE_BALLS_RECOVERED', 'CHARGES_DRAWN']
        existing_cols = [c for c in cols_to_keep if c in df.columns]
        
        return df[existing_cols]
    except Exception as e:
        print(f"    Error fetching Hustle Stats: {e}")
        return pd.DataFrame()

def fetch_all_seasons():
    all_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        season_str = get_season_string(year)
        print(f"Processing Season {season_str}...")
        
        # 1. Dashboard
        dash_df = fetch_defense_dashboard(season_str)
        
        if dash_df.empty:
            print("    Skipping season due to missing Dashboard data.")
            continue
            
        if 'PLAYER_ID' not in dash_df.columns:
            print("    Critical: PLAYER_ID missing from Dashboard columns. Skipping.")
            print(f"    Cols: {dash_df.columns.tolist()}")
            continue

        # 2. Hustle
        hustle_df = fetch_hustle_stats(season_str)
        
        # Merge
        merged_df = dash_df
        if not hustle_df.empty and 'PLAYER_ID' in hustle_df.columns:
            merged_df = pd.merge(dash_df, hustle_df, on='PLAYER_ID', how='left')
        else:
            # Add dummy hustle cols
            hustle_cols = ['CONTESTED_SHOTS', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT', 'CHARGES_DRAWN']
            for c in hustle_cols:
                merged_df[c] = 0
        
        merged_df['SEASON'] = season_str
        all_data.append(merged_df)
        
        time.sleep(0.6)
            
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print("Starting Historical Defensive Data Fetch...")
    df = fetch_all_seasons()
    
    if not df.empty:
        df = df.fillna(0) 
        print(f"Saving {len(df)} rows to {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, index=False)
        print("Done.")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
