
from nba_api.stats.endpoints import leaguedashteamstats
import pandas as pd

measure_types = ['Base', 'Advanced', 'Four Factors', 'Misc']

for mt in measure_types:
    print(f"--- {mt} ---")
    try:
        df = leaguedashteamstats.LeagueDashTeamStats(season='2024-25', measure_type_detailed_defense=mt).get_data_frames()[0]
        print(df.columns.tolist())
    except Exception as e:
        print(f"Error: {e}")
