import pandas as pd
import joblib
import time
from datetime import datetime
from nba_api.stats.endpoints import leaguedashplayerstats

CAP_2026_PROJECTED = 155100000
FEATURES = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 'TS_PCT', 'USG_PCT', 'PIE']

def update_projections():
    today = datetime.today().strftime('%Y-%m-%d')
    model = joblib.load('contract_model.joblib')
    scaler = joblib.load('data_scaler.joblib')
    
    print(f"Pulling LIVE 2025-26 stats for snapshot: {today}")
    trad = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26', per_mode_detailed='Totals').get_data_frames()[0]
    adv = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26', measure_type_detailed_defense='Advanced').get_data_frames()[0]
    live_stats = pd.merge(trad, adv[['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'PIE']], on='PLAYER_ID')

    tracker = pd.read_csv('nba_contract_tracker.csv')
    
    # Predict based on CURRENT season performance
    current_data = pd.merge(live_stats, tracker[['Player']], left_on='PLAYER_NAME', right_on='Player')
    X_current = scaler.transform(current_data[FEATURES])
    current_data[f'Live_AAV_{today}'] = model.predict(X_current) * CAP_2026_PROJECTED
    
    # Merge live prediction back into master tracker
    new_col = current_data[['Player', f'Live_AAV_{today}']]
    tracker = pd.merge(tracker, new_col, on='Player', how='left')
    
    tracker.to_csv('nba_contract_tracker.csv', index=False)
    print(f"✅ Success. Updated tracker with {today} data.")

if __name__ == "__main__":
    update_projections()