
from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd

try:
    print("Fetching 1996-97 Advanced Stats...")
    # MeasureType='Advanced' is the key parameter
    df = leaguedashplayerstats.LeagueDashPlayerStats(
        season='1996-97',
        measure_type_detailed_defense='Advanced' 
    ).get_data_frames()[0]
    
    print("\nColumns found:")
    print(df.columns.tolist())
    
    print("\nFirst row sample:")
    print(df.head(1).T)
    
except Exception as e:
    print(f"Error: {e}")
