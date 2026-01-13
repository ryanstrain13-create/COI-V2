import pandas as pd
import time
import os
from nba_api.stats.endpoints import synergyplaytypes

def fetch_pnr_data():
    seasons = [
        '2015-16', '2016-17', '2017-18', '2018-19', '2019-20',
        '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'
    ]
    
    # Potential keys to try
    handler_keys = ['PRBallHandler', 'PickAndRollBallHandler', 'P&RBallHandler']
    rollman_keys = ['PRRollMan', 'PickAndRollRollMan', 'P&RRollMan']
    
    all_data = []

    for season in seasons:
        print(f"Fetching P&R Data for {season}...")
        
        # --- Fetch Handler ---
        df_handler = pd.DataFrame()
        for key in handler_keys:
            try:
                print(f"  Trying Handler key: '{key}'...")
                df_handler = synergyplaytypes.SynergyPlayTypes(
                    season=season,
                    play_type_nullable=key,
                    type_grouping_nullable='offensive',
                    player_or_team_abbreviation='P',
                    per_mode_simple='PerGame',
                    timeout=60
                ).get_data_frames()[0]
                
                if not df_handler.empty:
                    print(f"    Success with '{key}'! ({len(df_handler)} rows)")
                    # Rename columns immediately
                    df_handler = df_handler.rename(columns={'POSS_PCT': 'PRBallHandler_FREQ', 'PPP': 'PRBallHandler_PPP'})
                    break
            except Exception:
                pass
            time.sleep(1)
            
        # --- Fetch Roll Man ---
        df_roll = pd.DataFrame()
        for key in rollman_keys:
            try:
                print(f"  Trying RollMan key: '{key}'...")
                df_roll = synergyplaytypes.SynergyPlayTypes(
                    season=season,
                    play_type_nullable=key,
                    type_grouping_nullable='offensive',
                    player_or_team_abbreviation='P',
                    per_mode_simple='PerGame',
                    timeout=60
                ).get_data_frames()[0]
                
                if not df_roll.empty:
                    print(f"    Success with '{key}'! ({len(df_roll)} rows)")
                    df_roll = df_roll.rename(columns={'POSS_PCT': 'PRRollMan_FREQ', 'PPP': 'PRRollMan_PPP'})
                    break
            except Exception:
                pass
            time.sleep(1)

        # Merge for the Season
        # We need a base DF. Use Handler as base, merge Roll. Or concat IDs.
        # Ideally, we want one row per PLAYER_ID per Season.
        
        # Build base from unique IDs in both
        ids_handler = df_handler['PLAYER_ID'].unique() if not df_handler.empty else []
        ids_roll = df_roll['PLAYER_ID'].unique() if not df_roll.empty else []
        all_ids = set(ids_handler) | set(ids_roll)
        
        if not all_ids:
            print(f"  No P&R data found for {season}.")
            continue
            
        season_df = pd.DataFrame({'PLAYER_ID': list(all_ids)})
        season_df['SEASON'] = season
        
        # Merge Handler
        if not df_handler.empty:
            cols = ['PLAYER_ID', 'PRBallHandler_FREQ', 'PRBallHandler_PPP']
            season_df = pd.merge(season_df, df_handler[cols], on='PLAYER_ID', how='left')
            
        # Merge Roll Man
        if not df_roll.empty:
            cols = ['PLAYER_ID', 'PRRollMan_FREQ', 'PRRollMan_PPP']
            season_df = pd.merge(season_df, df_roll[cols], on='PLAYER_ID', how='left')
            
        all_data.append(season_df)

    # Concat all seasons
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df = final_df.fillna(0) # Logic: if not found in playtype list, freq/ppp is 0
        
        output_dir = '/Users/ryanstrain/Desktop/COI V2/Archetype and Cluster Analysis/Historical Player Clusters/Offensive'
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/nba_historical_pnr_2015_2025.csv"
        final_df.to_csv(output_path, index=False)
        print(f"Saved P&R Data to {output_path}")
    else:
        print("No P&R data fetched for any season.")

if __name__ == "__main__":
    fetch_pnr_data()
