import pandas as pd
import time
import os
from nba_api.stats.endpoints import leaguedashplayerstats

def fetch_general_stats():
    # Define seasons
    seasons = [
        '2015-16', '2016-17', '2017-18', '2018-19', '2019-20',
        '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'
    ]

    all_stats = []

    for season in seasons:
        print(f"Fetching General Stats for {season}...")
        try:
            # Fetch League Dash Player Stats (General)
            # This gives USG%, AST%, STL, BLK, REB, DEFRTG etc.
            df = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                per_mode_detailed='PerGame',
                measure_type_detailed_defense='Base', # or 'Advanced' for USG/AST?
                # Actually, USG% and AST% are in 'Advanced' measure type, Default is 'Base'
                # STL, BLK are in check 'Base'.
                # We might need two calls: Base and Advanced.
                timeout=100
            ).get_data_frames()[0]
            
            # We need USG%, AST% (Advanced) and STL, BLK, DREB_PCT (Advanced), DEF_RATING (Advanced)
            # Standard Stats (Base) gives STL, BLK per game.
            # Advanced Stats gives USG%, AST%, DREB%, DEF_RATING.
            # So let's fetch 'Advanced'.
            
            time.sleep(1) # Be nice to API

            df_adv = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                per_mode_detailed='PerGame',
                measure_type_detailed_defense='Advanced',
                timeout=100
            ).get_data_frames()[0]
            
            # Also need Base for raw STL/BLK per game if not in Advanced?
            # Advanced usually has STL% and BLK% but maybe not raw counts per game?
            # Let's fetch Base too to be safe and merge.
            
            time.sleep(1)
            
            df_base = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                per_mode_detailed='PerGame',
                measure_type_detailed_defense='Base',
                timeout=100
            ).get_data_frames()[0]
            
            # Merge Base and Advanced
            # df_adv has USG_PCT, AST_PCT, DREB_PCT, DEF_RATING
            # df_base has STL, BLK (Per Game)
            
            # Standardize IDs? Usually reliable here.
            
            cols_adv = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'USG_PCT', 'AST_PCT', 'DREB_PCT', 'DEF_RATING', 'TS_PCT', 'PIE']
            cols_base = ['PLAYER_ID', 'STL', 'BLK', 'DREB'] # DREB is raw defensive rebounds
            
            # Select columns if they exist
            df_adv_sel = df_adv[[c for c in cols_adv if c in df_adv.columns]]
            df_base_sel = df_base[[c for c in cols_base if c in df_base.columns]]
            
            merged = pd.merge(df_adv_sel, df_base_sel, on='PLAYER_ID', how='left')
            merged['SEASON'] = season
            all_stats.append(merged)
            
            print(f"  Fetched {len(merged)} rows.")
            
        except Exception as e:
            print(f"  Error fetching {season}: {e}")
            
        time.sleep(1)

    if all_stats:
        final_df = pd.concat(all_stats, ignore_index=True)
        output_dir = '/Users/ryanstrain/Desktop/COI V2/Archetype and Cluster Analysis/Historical Player Clusters/General'
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/nba_historical_general_stats_2015_2025.csv"
        final_df.to_csv(output_path, index=False)
        print(f"Saved General Stats to {output_path}")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    fetch_general_stats()
