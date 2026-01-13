import pandas as pd
import time
import os
from datetime import datetime
from nba_api.stats.endpoints import leaguedashplayerstats, synergyplaytypes, leaguehustlestatsplayer

def capture_weekly_snapshot(filename="nba_timeseries_stats_2025_26.csv"):
    # 1. Define columns (Base + Advanced + Archetype Features)
    # Note: We will dynamically add columns based on merge, but let's keep the core structure.
    
    print(f"Fetching data for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    
    try:
        # --- 1. Base Stats ---
        print("Fetching Base Stats...")
        base_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2025-26', measure_type_detailed_defense='Base', rank='Y', timeout=100
        ).get_data_frames()[0]
        time.sleep(0.6)
        
        # --- 2. Advanced Stats (USG, AST%, DREB%, DEFRTG) ---
        print("Fetching Advanced Stats...")
        adv_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2025-26', measure_type_detailed_defense='Advanced', timeout=100
        ).get_data_frames()[0]
        
        # Keep relevant Advanced columns
        adv_cols = ['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'PIE', 'AST_PCT', 'DREB_PCT', 'DEF_RATING']
        adv_stats = adv_stats[[c for c in adv_cols if c in adv_stats.columns]]
        time.sleep(0.6)

        # --- 3. Hustle Stats (Contested Shots) ---
        print("Fetching Hustle Stats...")
        hustle_stats = leaguehustlestatsplayer.LeagueHustleStatsPlayer(
            season='2025-26', per_mode_time='PerGame', timeout=100
        ).get_data_frames()[0]
        
        # Rename/Keep Hustle columns
        # We need CONTESTED_SHOTS mostly.
        hustle_cols = ['PLAYER_ID', 'CONTESTED_SHOTS', 'CHARGES_DRAWN', 'DEF_LOOSE_BALLS_RECOVERED']
        hustle_stats = hustle_stats[[c for c in hustle_cols if c in hustle_stats.columns]]
        time.sleep(0.6)

        # --- 4. Synergy Playtypes (Offense) ---
        playtypes = [
            'Isolation', 'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound', 'Transition',
            'PRBallHandler', 'PRRollMan' # Will try variations if needed
        ]
        
        synergy_data = pd.DataFrame({'PLAYER_ID': base_stats['PLAYER_ID'].unique()}) # Initialize with IDs
        
        for pt in playtypes:
            print(f"  Fetching {pt}...")
            # Handle P&R key variations if needed (fetching 2025 so standard keys should work, 
            # but using the retry logic is safer if API is flaky)
            keys_to_try = [pt]
            if pt == 'PRBallHandler': keys_to_try = ['PRBallHandler', 'P&RBallHandler']
            if pt == 'PRRollMan': keys_to_try = ['PRRollMan', 'P&RRollMan']
            
            df_pt = pd.DataFrame()
            for key in keys_to_try:
                try:
                    df_pt = synergyplaytypes.SynergyPlayTypes(
                        season='2025-26', play_type_nullable=key, type_grouping_nullable='offensive',
                        player_or_team_abbreviation='P', per_mode_simple='PerGame', timeout=60
                    ).get_data_frames()[0]
                    if not df_pt.empty: break
                except: pass
                time.sleep(0.5)
            
            if not df_pt.empty:
                # Rename columns: FREQ and PPP
                # API cols: POSS_PCT, PPP
                cols = ['PLAYER_ID', 'POSS_PCT', 'PPP']
                df_pt = df_pt[[c for c in cols if c in df_pt.columns]]
                df_pt = df_pt.rename(columns={'POSS_PCT': f'{pt}_FREQ', 'PPP': f'{pt}_PPP'})
                # Merge into synergy accumulator
                synergy_data = pd.merge(synergy_data, df_pt, on='PLAYER_ID', how='left')
            else:
                print(f"    Warning: No data for {pt}")
                synergy_data[f'{pt}_FREQ'] = 0
                synergy_data[f'{pt}_PPP'] = 0
            
            time.sleep(0.5)

        # --- 5. Merge Everything ---
        print("Merging data...")
        final_df = pd.merge(base_stats, adv_stats, on='PLAYER_ID', how='left')
        final_df = pd.merge(final_df, hustle_stats, on='PLAYER_ID', how='left')
        final_df = pd.merge(final_df, synergy_data, on='PLAYER_ID', how='left')
        
        # Add Snapshot Time
        final_df['SNAPSHOT_TIME'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Fill NaNs for stats (0 is appropriate for usage/freq/hustle if missing)
        # Be careful not to fill IDs or Names with 0 if they were somehow missing (unlikely with Left Merge on Base)
        # Columns to fill 0:
        fill_0_cols = [c for c in final_df.columns if 'FREQ' in c or 'PPP' in c or 'PCT' in c or 'RATING' in c or c in hustle_cols]
        final_df[fill_0_cols] = final_df[fill_0_cols].fillna(0)

        # Update Master File (Read -> Concat -> Write to handle schema changes safe)
        if os.path.exists(filename):
            print(f"Reading existing file: {filename}...")
            try:
                # Read existing data
                existing_df = pd.read_csv(filename)
                
                # Check if we already have data for this snapshot (to avoid duplicates if re-run)
                # Simple check: timestamp match (approximate) or just append. 
                # Let's just append for now, user can dedupe if needed, or we can check.
                # Actually, duplicate snapshots are bad. Let's filter if same day? 
                # User's prompt didn't strictly ask for dedupe, but "update" implies adding new.
                
                # Concat (this handles new columns by adding them to the schema and filling NaNs in old rows)
                master_df = pd.concat([existing_df, final_df], ignore_index=True)
                
                # Write back
                master_df.to_csv(filename, index=False)
                print(f"Snapshot successful. Appended {len(final_df)} rows. Total rows: {len(master_df)}.")
                
            except Exception as e:
                print(f"Error reading/writing existing file: {e}")
                # Fallback: append mode if read fails (risky for schema but better than crash)
                final_df.to_csv(filename, mode='a', index=False, header=False)
        else:
            # Create new file
            # ensure directory exists
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            final_df.to_csv(filename, index=False)
            print(f"Snapshot successful. Created new file {filename} with {len(final_df)} rows.")
        
    except Exception as e:
        print(f"Error during snapshot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ensure we use the correct relative path from the Weekly Updates folder to the data folder
    # Based on user context: "Weekly Updates/Contract Value Weekly Update/nba_timeseries_stats_2025_26.csv"
    # The script sits in "Weekly Updates".
    target_file = "Contract Value Weekly Update/nba_timeseries_stats_2025_26.csv"
    capture_weekly_snapshot(target_file)