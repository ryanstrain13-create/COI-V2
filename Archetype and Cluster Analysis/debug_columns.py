
from nba_api.stats.endpoints import leaguedashplayerstats
adv = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2024-25', measure_type_detailed_defense='Advanced'
    ).get_data_frames()[0]
print(adv.columns.tolist())
