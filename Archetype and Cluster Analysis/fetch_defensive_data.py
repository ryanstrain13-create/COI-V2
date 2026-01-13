
import pandas as pd
import numpy as np
import time
from nba_api.stats.endpoints import leaguedashplayerstats, leaguehustlestatsplayer, leagueseasonmatchups, leaguedashplayerbiostats
from nba_api.stats.static import teams

# --- Configuration ---
SEASON = '2024-25'
OUTPUT_FILE = 'nba_defensive_archetypes_2025.csv'

def get_player_stats_and_positions():
    print("Fetching Player Bio/Stats (for positions and USG)...")
    base = leaguedashplayerstats.LeagueDashPlayerStats(season=SEASON).get_data_frames()[0]
    adv = leaguedashplayerstats.LeagueDashPlayerStats(
        season=SEASON, measure_type_detailed_defense='Advanced'
    ).get_data_frames()[0]
    
    cols_base = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'GP', 'MIN', 'STL', 'BLK'] 
    
    df = pd.merge(
        base[cols_base],
        adv[['PLAYER_ID', 'DREB_PCT', 'DEF_RATING', 'USG_PCT']],
        on='PLAYER_ID'
    )
    
    usg_map = df.set_index('PLAYER_ID')['USG_PCT'].to_dict()
    
    return df, usg_map

def get_hustle_stats():
    print("Fetching Hustle Stats...")
    hustle = leaguehustlestatsplayer.LeagueHustleStatsPlayer(season=SEASON, per_mode_time='PerGame').get_data_frames()[0]
    return hustle[['PLAYER_ID', 'DEFLECTIONS', 'CONTESTED_SHOTS', 'MIN']]

def get_matchup_data(usg_map):
    print("Fetching Matchup Data (Iterating Teams)...")
    all_matchups = []
    nba_teams = teams.get_teams()
    
    for i, t in enumerate(nba_teams):
        tid = t['id']
        print(f"  Fetching vs {t['abbreviation']} ({i+1}/{30})...")
        try:
            matchups = leagueseasonmatchups.LeagueSeasonMatchups(
                season=SEASON,
                off_team_id_nullable=tid
            )
            df = matchups.get_data_frames()[0]
            # Only keep columns we need to save memory
            df = df[['OFF_PLAYER_ID', 'DEF_PLAYER_ID', 'MATCHUP_TIME_SEC', 'PLAYER_PTS', 'PARTIAL_POSS']]
            all_matchups.append(df)
            time.sleep(0.6)
        except Exception as e:
            print(f"  Error fetching {t['abbreviation']}: {e}")
            
    if not all_matchups:
        return pd.DataFrame(), pd.DataFrame()
        
    full_matchups = pd.concat(all_matchups, ignore_index=True)
    
    # Difficulty
    full_matchups['OPP_USG'] = full_matchups['OFF_PLAYER_ID'].map(usg_map)
    full_matchups['USG_TIME'] = full_matchups['OPP_USG'] * full_matchups['MATCHUP_TIME_SEC']
    
    grouped = full_matchups.groupby('DEF_PLAYER_ID').agg({
        'MATCHUP_TIME_SEC': 'sum',
        'USG_TIME': 'sum'
    }).reset_index()
    
    grouped['MATCHUP_DIFFICULTY'] = grouped['USG_TIME'] / grouped['MATCHUP_TIME_SEC']
    
    return grouped, full_matchups

def get_positions_via_bio():
    print("Fetching Player Bio Stats...")
    # Corrected Endpoint Import
    bio = leaguedashplayerbiostats.LeagueDashPlayerBioStats(season=SEASON).get_data_frames()[0]
    
    def parse_height(h_str):
        try:
            if isinstance(h_str, str) and '-' in h_str:
                ft, inch = map(int, h_str.split('-'))
                return ft * 12 + inch
            return 0
        except:
            return 0
            
    bio['Height_Inches'] = bio['PLAYER_HEIGHT'].apply(parse_height)
    
    def estimate_pos(row):
        h = row['Height_Inches']
        if h == 0: return 'Unknown'
        if h < 76: return 'PG'
        if h < 78: return 'SG'
        if h < 80: return 'SF'
        if h < 82: return 'PF'
        return 'C'
        
    bio['EST_POS'] = bio.apply(estimate_pos, axis=1)
    return bio.set_index('PLAYER_ID')['EST_POS'].to_dict()

def main():
    df_stats, usg_map = get_player_stats_and_positions()
    df_hustle = get_hustle_stats()
    df_hustle = df_hustle.rename(columns={'MIN': 'MIN_HUSTLE'})
    
    df_matchup_grouped, full_matchups_df = get_matchup_data(usg_map)
    
    # Positional
    if not full_matchups_df.empty:
        pos_map = get_positions_via_bio()
        print("Calculating Positional Distribution...")
        full_matchups_df['OPP_POS'] = full_matchups_df['OFF_PLAYER_ID'].map(pos_map).fillna('Unknown')
        
        pos_dist = full_matchups_df.pivot_table(
            index='DEF_PLAYER_ID', columns='OPP_POS', values='MATCHUP_TIME_SEC', aggfunc='sum', fill_value=0
        )
        total_time = pos_dist.sum(axis=1)
        
        pct_cols = []
        for pos in ['PG', 'SG', 'SF', 'PF', 'C']:
            col_name = f'd{pos}_PCT'
            pct_cols.append(col_name)
            if pos in pos_dist.columns:
                pos_dist[col_name] = pos_dist[pos] / total_time
            else:
                pos_dist[col_name] = 0.0
                
        def calc_entropy(row):
            vals = row[pct_cols].values
            vals = vals[vals > 0]
            if len(vals) == 0: return 0
            return -np.sum(vals * np.log(vals))
            
        pos_dist['VERSATILITY_RATING'] = pos_dist.apply(calc_entropy, axis=1)
    else:
        pos_dist = pd.DataFrame()
        pct_cols = []

    print("Merging...")
    final_df = pd.merge(df_stats, df_hustle, on='PLAYER_ID', how='left')
    
    if not df_matchup_grouped.empty:
        final_df = pd.merge(final_df, df_matchup_grouped[['DEF_PLAYER_ID', 'MATCHUP_DIFFICULTY']], left_on='PLAYER_ID', right_on='DEF_PLAYER_ID', how='left')
        
    if not pos_dist.empty:
        final_df = pd.merge(final_df, pos_dist[pct_cols + ['VERSATILITY_RATING']], left_on='PLAYER_ID', right_index=True, how='left')
    
    # Calc Deflections/75 (Approx)
    final_df['MIN_HUSTLE'] = final_df['MIN_HUSTLE'].replace(0, np.nan)
    final_df['DEFLECTIONS_PER_75'] = (final_df['DEFLECTIONS'] / final_df['MIN_HUSTLE']) * 36
    
    final_df = final_df.fillna(0)
    
    print(f"Saving to {OUTPUT_FILE}...")
    final_df.to_csv(OUTPUT_FILE, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
