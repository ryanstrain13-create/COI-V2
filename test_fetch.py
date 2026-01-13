
from nba_api.stats.endpoints import leaguedashplayerstats, synergyplaytypes
import pandas as pd
import time

# 1. Test SynergyPlayTypes (Isolation)
print("Testing SynergyPlayTypes (Isolation)...")
try:
    synergy = synergyplaytypes.SynergyPlayTypes(
        player_or_team_abbreviation='P',
        play_type_nullable='Isolation',
        type_grouping_nullable='Offensive',
        season_nullable='2024-25'
    )
    df_iso = synergy.get_data_frames()[0]
    print("Columns:", df_iso.columns.tolist())
    print("First row:", df_iso.head(1).to_dict())
except Exception as e:
    print("Synergy Error:", e)

# 2. Test Advanced Stats
print("\nTesting Advanced Stats...")
try:
    adv = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2024-25',
        measure_type_detailed_defense='Advanced'
    )
    df_adv = adv.get_data_frames()[0]
    print("Adv Columns:", df_adv.columns.tolist())
except Exception as e:
    print("Advanced Stats Error:", e)
