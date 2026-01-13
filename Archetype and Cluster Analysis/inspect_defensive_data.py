
from nba_api.stats.endpoints import leaguehustlestatsplayer, leagueseasonmatchups
import pandas as pd

# 1. Inspect Hustle Stats
print("Fetching Hustle Stats...")
try:
    hustle = leaguehustlestatsplayer.LeagueHustleStatsPlayer(
        season='2024-25',
        per_mode_time='PerGame'
    )
    df_hustle = hustle.get_data_frames()[0]
    print("Hustle Columns:", df_hustle.columns.tolist())
    print("First row:", df_hustle.head(1).to_dict())
except Exception as e:
    print("Hustle Error:", e)

# 2. Inspect Matchups
print("\nFetching League Season Matchups...")
try:
    # Note: Arguments might be tricky. Usually requires 'Season' and maybe 'OffDef'
    matchups = leagueseasonmatchups.LeagueSeasonMatchups(
        season='2024-25',
        offensive_defensive_nullable='Defensive' # We want who they guarded
    )
    df_matchups = matchups.get_data_frames()[0]
    print("Matchup Columns:", df_matchups.columns.tolist())
    print("First row:", df_matchups.head(1).to_dict())
except Exception as e:
    print("Matchup Error:", e)
