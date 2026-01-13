
from nba_api.stats.endpoints import leagueseasonmatchups
import time

print("Testing LeagueSeasonMatchups fetch...")
start = time.time()
try:
    # Try fetching for one team first to check structure/speed
    matchups = leagueseasonmatchups.LeagueSeasonMatchups(
        season='2024-25',
        off_team_id_nullable=1610612738 # Celtics
    )
    df = matchups.get_data_frames()[0]
    print(f"Fetched {len(df)} rows in {time.time() - start:.2f}s")
    print(df.columns.tolist())
    print(df.head(1).to_dict())
    
    # Check if 'OFF_PLAYER_ID' and 'DEF_PLAYER_ID' exist
except Exception as e:
    print("Error:", e)
