
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashteamstats

# --- Configuration ---
SEASON = '2024-25'
OUTPUT_FILE = 'nba_team_archetypes_2025.csv'

def fetch_data():
    print(f"Fetching Team Stats for {SEASON}...")
    
    # 1. Advanced Stats
    print("  Fetching Advanced...")
    adv = leaguedashteamstats.LeagueDashTeamStats(
        season=SEASON, 
        measure_type_detailed_defense='Advanced'
    ).get_data_frames()[0]
    time.sleep(0.6)
    
    # 2. Base Stats (for 3PAr)
    print("  Fetching Base...")
    base = leaguedashteamstats.LeagueDashTeamStats(
        season=SEASON, 
        measure_type_detailed_defense='Base'
    ).get_data_frames()[0]
    time.sleep(0.6)
    
    # 3. Misc Stats (for Paint/FB points)
    print("  Fetching Misc...")
    misc = leaguedashteamstats.LeagueDashTeamStats(
        season=SEASON, 
        measure_type_detailed_defense='Misc'
    ).get_data_frames()[0]
    
    return adv, base, misc

def process_data(adv, base, misc):
    print("Processing Data...")
    
    # Select Columns
    cols_adv = ['TEAM_ID', 'TEAM_NAME', 'PACE', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 
                'AST_PCT', 'OREB_PCT', 'TM_TOV_PCT', 'TS_PCT']
    cols_base = ['TEAM_ID', 'FG3A', 'FGA', 'PTS']
    cols_misc = ['TEAM_ID', 'PTS_FB', 'PTS_PAINT']
    
    # Merge
    # Start with Advanced as base
    df = adv[cols_adv].copy()
    
    # Merge Base
    df = pd.merge(df, base[cols_base], on='TEAM_ID')
    
    # Merge Misc
    df = pd.merge(df, misc[cols_misc], on='TEAM_ID')
    
    # Calculations
    print("  Calculating Derived Metrics...")
    
    # 3-Point Attempt Rate
    df['3PAr'] = df['FG3A'] / df['FGA']
    
    # Fast Break % (Style: Transition vs Halfcourt)
    df['FB_PCT'] = df['PTS_FB'] / df['PTS']
    
    # Paint % (Style: Rim Pressure vs Perimeter)
    df['PAINT_PCT'] = df['PTS_PAINT'] / df['PTS']
    
    # Handle any potential division by zero (unlikely for FGA/PTS but good practice)
    df = df.fillna(0)
    
    return df

def main():
    try:
        adv, base, misc = fetch_data()
        final_df = process_data(adv, base, misc)
        
        print(f"Saving {len(final_df)} teams to {OUTPUT_FILE}...")
        final_df.to_csv(OUTPUT_FILE, index=False)
        print("Done.")
        
        # Print a sneak peek
        print("\nTop 5 Pace Teams:")
        print(final_df.sort_values('PACE', ascending=False)[['TEAM_NAME', 'PACE']].head(5))
        
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()
