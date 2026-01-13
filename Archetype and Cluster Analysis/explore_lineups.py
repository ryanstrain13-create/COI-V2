
from nba_api.stats.endpoints import leaguedashlineups
import pandas as pd
import time

def fetch(measure_type):
    print(f"Fetching Lineup columns ({measure_type})...")
    try:
        lineups = leaguedashlineups.LeagueDashLineups(
            season='2024-25',
            group_quantity=5,
            measure_type_detailed_defense=measure_type,
            timeout=100
        ).get_data_frames()[0]
        
        print(f"--- {measure_type} Columns ---")
        print(lineups.columns.tolist())
        if not lineups.empty:
            print("First row:", lineups.head(1).to_dict())
            # Important: Check how Player IDs are stored
            # Usually GROUP_KEY or similar string
            print("Group ID Example:", lineups['GROUP_ID'].iloc[0] if 'GROUP_ID' in lineups.columns else "N/A")
            
    except Exception as e:
        print(f"Error fetching {measure_type}: {e}")

fetch('Base')
time.sleep(2)
fetch('Advanced')
