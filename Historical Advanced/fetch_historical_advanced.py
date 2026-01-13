
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashplayerstats

# --- Configuration ---
START_YEAR = 1996
END_YEAR = 2024 # Starts 2024-25 season
OUTPUT_FILE = 'nba_historical_advanced_stats_1997_2025.csv'

# Column Mapping (API -> Output)
COL_MAP = {
    'PLAYER_ID': 'PLAYER_ID',
    'PLAYER_NAME': 'PLAYER_NAME',
    'TEAM_ABBREVIATION': 'TEAM',
    'GP': 'GP',
    'W': 'W',
    'L': 'L',
    'MIN': 'MIN',
    'OFF_RATING': 'OFFRTG',
    'DEF_RATING': 'DEFRTG',
    'NET_RATING': 'NETRTG',
    'AST_PCT': 'AST%',
    'AST_TO': 'AST/TO',
    'AST_RATIO': 'AST RATIO',
    'OREB_PCT': 'OREB%',
    'DREB_PCT': 'DREB%',
    'REB_PCT': 'REB%',
    'TM_TOV_PCT': 'TO RATIO',
    'EFG_PCT': 'EFG%',
    'TS_PCT': 'TS%',
    'USG_PCT': 'USG%',
    'PACE': 'PACE',
    'PIE': 'PIE',
    'POSS': 'POSS'
}

def get_season_string(start_year):
    # e.g. 1996 -> "1996-97"
    # e.g. 1999 -> "1999-00"
    end_part = (start_year + 1) % 100
    return f"{start_year}-{end_part:02d}"

def fetch_all_seasons():
    all_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        season_str = get_season_string(year)
        print(f"Fetching {season_str}...")
        
        try:
            df = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season_str,
                measure_type_detailed_defense='Advanced',
                timeout=120
            ).get_data_frames()[0]
            
            df['SEASON'] = season_str
            all_data.append(df)
            
            # Respect rate limits
            time.sleep(0.6)
            
        except Exception as e:
            print(f"  Error fetching {season_str}: {e}")
            
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def process_and_save(df):
    print("Processing Data...")
    
    # Select and Rename columns
    # Ensure all source cols exist
    available_cols = [c for c in COL_MAP.keys() if c in df.columns]
    
    # We might want to keep SEASON as well
    final_df = df[available_cols + ['SEASON']].copy()
    final_df = final_df.rename(columns=COL_MAP)
    
    # Reorder to match request + Context
    # Request: GP W L MIN OFFRTG DEFRTG NETRTG AST% AST/TO AST RATIO OREB% DREB% REB% TO RATIO EFG% TS% USG% PACE PIE POSS
    req_order = [
        'PLAYER_NAME', 'TEAM', 'SEASON', # Context
        'GP', 'W', 'L', 'MIN', 
        'OFFRTG', 'DEFRTG', 'NETRTG', 
        'AST%', 'AST/TO', 'AST RATIO', 
        'OREB%', 'DREB%', 'REB%', 'TO RATIO', 
        'EFG%', 'TS%', 'USG%', 
        'PACE', 'PIE', 'POSS'
    ]
    
    # Ensure they exist (e.g. POSS might be missing in old data?)
    # Validated: POSS exists in 1996-97 check
    
    # Handle missing cols gracefully
    for col in req_order:
        if col not in final_df.columns:
            final_df[col] = 'n/a'
            
    final_df = final_df[req_order]
    
    # Handle missing values (NaN -> n/a)
    final_df = final_df.fillna('n/a')
    
    print(f"Saving {len(final_df)} rows to {OUTPUT_FILE}...")
    final_df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

def main():
    df = fetch_all_seasons()
    if not df.empty:
        process_and_save(df)
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
