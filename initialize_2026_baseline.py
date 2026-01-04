import pandas as pd
import joblib
from nba_api.stats.endpoints import leaguedashplayerstats

CAP_2026_PROJECTED = 155100000
FEATURES = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 'TS_PCT', 'USG_PCT', 'PIE']

def init_baseline():
    # Load trained model and scaler
    model = joblib.load('contract_model.joblib')
    scaler = joblib.load('data_scaler.joblib')

    print("Fetching 2024-25 stats for 2026 baseline...")
    trad = leaguedashplayerstats.LeagueDashPlayerStats(season='2024-25', per_mode_detailed='Totals').get_data_frames()[0]
    adv = leaguedashplayerstats.LeagueDashPlayerStats(season='2024-25', measure_type_detailed_defense='Advanced').get_data_frames()[0]
    live_df = pd.merge(trad, adv[['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'PIE']], on='PLAYER_ID')

    # UPDATED: Correctly handle the header row and column names
    fa_2026 = pd.read_csv('NBA Free Agents 2026 - Sheet1.csv', skiprows=1)
    
    # Clean column names to remove any leading/trailing spaces
    fa_2026.columns = fa_2026.columns.str.strip()
    
    # Rename 'Player (248)' to 'Player' for consistent merging
    fa_2026 = fa_2026.rename(columns={'Player (248)': 'Player'})

    # Merge stats with the free agent list
    final = pd.merge(live_df, fa_2026, left_on='PLAYER_NAME', right_on='Player')
    
    # Predict contract values
    X_live = scaler.transform(final[FEATURES])
    final['Baseline_AAV'] = model.predict(X_live) * CAP_2026_PROJECTED
    
    # UPDATED: Use 'Type' instead of 'Status' based on your CSV content
    output_cols = ['Player', 'Baseline_AAV', 'Type', 'Prev Team']
    output = final[output_cols]
    
    output.to_csv('nba_contract_tracker.csv', index=False)
    print(f"✅ Baseline created successfully. Processed {len(output)} players.")

if __name__ == "__main__":
    init_baseline()