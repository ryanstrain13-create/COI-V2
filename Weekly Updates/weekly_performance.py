import pandas as pd
import time
import os
from datetime import datetime
from nba_api.stats.endpoints import leaguedashplayerstats

def capture_weekly_snapshot(filename="nba_timeseries_stats_2025_26.csv"):
    # 1. Define the full list of columns you requested
    target_columns = [
        'SNAPSHOT_TIME', 'PLAYER_ID','PLAYER_NAME','NICKNAME','TEAM_ID','TEAM_ABBREVIATION','AGE','GP','W','L','W_PCT',
        'MIN','FGM','FGA','FG_PCT','FG3M','FG3A','FG3_PCT','FTM','FTA','FT_PCT','OREB','DREB','REB',
        'AST','TOV','STL','BLK','BLKA','PF','PFD','PTS','PLUS_MINUS','NBA_FANTASY_PTS','DD2','TD3',
        'WNBA_FANTASY_PTS','GP_RANK','W_RANK','L_RANK','W_PCT_RANK','MIN_RANK','FGM_RANK','FGA_RANK',
        'FG_PCT_RANK','FG3M_RANK','FG3A_RANK','FG3_PCT_RANK','FTM_RANK','FTA_RANK','FT_PCT_RANK',
        'OREB_RANK','DREB_RANK','REB_RANK','AST_RANK','TOV_RANK','STL_RANK','BLK_RANK','BLKA_RANK',
        'PF_RANK','PFD_RANK','PTS_RANK','PLUS_MINUS_RANK','NBA_FANTASY_PTS_RANK','DD2_RANK','TD3_RANK',
        'WNBA_FANTASY_PTS_RANK','TEAM_COUNT','TS_PCT','USG_PCT','PIE'
    ]

    print(f"Fetching data for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    
    try:
        # 2. Fetch Base and Advanced Stats
        base_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2025-26', measure_type_detailed_defense='Base', rank='Y'
        ).get_data_frames()[0]
        
        time.sleep(1) # API Rate limit protection
        
        adv_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2025-26', measure_type_detailed_defense='Advanced'
        ).get_data_frames()[0][['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'PIE']]

        # 3. Merge and add the Timestamp
        final_df = pd.merge(base_stats, adv_stats, on='PLAYER_ID', how='inner')
        final_df['SNAPSHOT_TIME'] = datetime.now().strftime('%Y-%m-%d %H:%M')

        # 4. Filter for only your requested columns
        final_df = final_df[[col for col in target_columns if col in final_df.columns]]

        # 5. Append to CSV (Write header only if file doesn't exist)
        file_exists = os.path.isfile(filename)
        final_df.to_csv(filename, mode='a', index=False, header=not file_exists)
        
        print(f"Snapshot successful. Total rows in master file: {len(pd.read_csv(filename))}")
        
    except Exception as e:
        print(f"Error during snapshot: {e}")

# Call the function
capture_weekly_snapshot()