
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashplayerstats, synergyplaytypes

# --- CONFIGURATION ---
SEASON = '2024-25'
OUTPUT_FILE = 'nba_player_archetypes_2025.csv'

def get_synergy_stats(play_type):
    """Fetches Synergy stats for a specific play type."""
    print(f"Fetching Synergy: {play_type}...")
    try:
        # Note: 
        # play_type_nullable values: 'Transition', 'Isolation', 'PRBallHandler', 'PRRollMan', 'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound' (Putback)
        # type_grouping_nullable: 'Offensive'
        
        # Mappings for user friendly names to API names if needed
        api_play_type_map = {
            'Pick & Roll Ball Handler': 'PRBallHandler',
            'Pick & Roll Roll Man': 'PRRollMan',
            'Putback': 'OffRebound',
            'Post Up': 'Postup',
            'Spot Up': 'Spotup',
            'Off-Screen': 'OffScreen'
        }
        
        query_play_type = api_play_type_map.get(play_type, play_type)
        
        synergy = synergyplaytypes.SynergyPlayTypes(
            player_or_team_abbreviation='P',
            play_type_nullable=query_play_type,
            type_grouping_nullable='Offensive',
            season=SEASON
        )
        df = synergy.get_data_frames()[0]
        time.sleep(0.6) # Gentle rate limiting
        
        # Keep relevant columns and rename
        # Common cols: PLAYER_ID, PLAYER_NAME, TEAM_ABBREVIATION, GP, POSS_PCT, PPP, etc.
        # We want Frequency (POSS_PCT) and PPP.
        
        cols_to_keep = ['PLAYER_ID', 'POSS_PCT', 'PPP']
        df_subset = df[cols_to_keep].copy()
        
        # Rename to include playtype prefix
        prefix = play_type.replace(' ', '_').replace('&', '').replace('-', '_').upper()
        df_subset.rename(columns={
            'POSS_PCT': f'{prefix}_FREQ',
            'PPP': f'{prefix}_PPP'
        }, inplace=True)
        
        return df_subset
    except Exception as e:
        print(f"Error fetching {play_type}: {e}")
        return pd.DataFrame()

def main():
    # 1. Fetch Advanced Stats
    print("Fetching Advanced Stats...")
    adv = leaguedashplayerstats.LeagueDashPlayerStats(
        season=SEASON, measure_type_detailed_defense='Advanced'
    ).get_data_frames()[0]
    
    # Select cols: USG_PCT, AST_PCT, TS_PCT, OFF_RATING, DEF_RATING, PIE
    adv_cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'GP', 
                'USG_PCT', 'AST_PCT', 'TS_PCT', 'OFF_RATING', 'DEF_RATING', 'PIE']
    df_final = adv[adv_cols].copy()
    
    # 2. Fetch Base Stats for 3PAr
    print("Fetching Base Stats (for 3PAr)...")
    base = leaguedashplayerstats.LeagueDashPlayerStats(
        season=SEASON, measure_type_detailed_defense='Base'
    ).get_data_frames()[0]
    
    # Calculate 3PAr = FG3A / FGA
    # Avoid division by zero
    base['FGA'] = base['FGA'].replace(0, 1) 
    base['3P_Attempt_Rate'] = base['FG3A'] / base['FGA']
    
    # Merge 3PAr into final
    df_final = pd.merge(df_final, base[['PLAYER_ID', '3P_Attempt_Rate']], on='PLAYER_ID', how='left')
    
    # 3. Fetch Synergy Playtypes
    play_types = [
        'Pick & Roll Ball Handler', 'Isolation', 'Handoff', 'Off-Screen',
        'Cut', 'Putback', 'Post Up', 'Pick & Roll Roll Man', 
        'Spot Up', 'Transition'
    ]
    
    for pt in play_types:
        df_synergy = get_synergy_stats(pt)
        if not df_synergy.empty:
            df_final = pd.merge(df_final, df_synergy, on='PLAYER_ID', how='left')
    
    # 4. Fill NaNs
    # For Synergy stats, NaN usually means 0 frequency/possessions
    df_final = df_final.fillna(0)
    
    # 5. Save
    print(f"Saving to {OUTPUT_FILE}...")
    df_final.to_csv(OUTPUT_FILE, index=False)
    print("Done!")
    print(df_final.head())

if __name__ == "__main__":
    main()
