import pandas as pd
import joblib
import time
import os
from datetime import datetime
from nba_api.stats.endpoints import leaguedashplayerstats

CAP_2026_PROJECTED = 155100000
FEATURES = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 'TS_PCT', 'USG_PCT', 'PIE']

def clean_currency(val):
    if pd.isna(val) or val == '': return 0
    return float(str(val).replace('$', '').replace(',', '').strip())

def update_projections(filename='nba_contract_tracker.csv'):
    today = datetime.today().strftime('%Y-%m-%d')
    new_col_name = f"Live_AAV_{today}"
    
    # 1. Load Model Assets
    try:
        # Try loading from parent directory if not in current
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, 'contract_model.joblib')
        scaler_path = os.path.join(base_path, 'data_scaler.joblib')
        
        if os.path.exists(model_path):
             model = joblib.load(model_path)
             scaler = joblib.load(scaler_path)
        else:
             model = joblib.load('contract_model.joblib')
             scaler = joblib.load('data_scaler.joblib')
    except FileNotFoundError:
        print("Model or Scaler files missing. Please check pathing.")
        return

    print(f"Pulling LIVE 2025-26 stats for snapshot: {today}")
    
    # 2. Fetch Stats
    try:
        trad = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26', per_mode_detailed='Totals').get_data_frames()[0]
        time.sleep(1) # Rate limit safety
        adv = leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26', measure_type_detailed_defense='Advanced').get_data_frames()[0]
        
        # 3. Merge and Prepare Features
        live_stats = pd.merge(trad, adv[['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'PIE']], on='PLAYER_ID')
        
        # 4. Generate Predictions
        X_current = scaler.transform(live_stats[FEATURES])
        live_stats[new_col_name] = model.predict(X_current) * CAP_2026_PROJECTED
        
        # Preparing the new data to merge
        # We match on 'calc_key' -> 'PLAYER_NAME' 
        # But to be safe against name changes, we ideally use ID, but the existing CSV likely uses Name as key.
        # We will assume Name for now as it's the common denominator in the CSV.
        new_data = live_stats[['PLAYER_NAME', new_col_name]].copy()
        new_data = new_data.rename(columns={'PLAYER_NAME': 'Player'})

        # 5. Load and Update CSV
        if os.path.exists(filename):
            print(f"Updating existing file: {filename}")
            # on_bad_lines='skip' helps ignore the malformed rows at the bottom if any exist
            try:
                current_df = pd.read_csv(filename, on_bad_lines='skip')
            except Exception as e:
                print(f"Warning: Could not read existing file normally ({e}). Starting fresh or using backup.")
                current_df = pd.DataFrame()

            # Clean up: If the file has 'Player' column, we use it.
            if 'Player' in current_df.columns:
                # Merge the new column
                # We use outer join to keep players who might not be in the new feed (rare) or new players
                updated_df = pd.merge(current_df, new_data, on='Player', how='outer')
            else:
                # If structure is totally wrong, we initialize with the new data
                print("Existing file seems valid but missing 'Player' column. Re-initializing.")
                updated_df = new_data
        else:
            print(f"Creating new file: {filename}")
            updated_df = new_data
            
        # 6. Save back to CSV
        updated_df.to_csv(filename, index=False)
        print(f"✅ Success. Added/Updated column '{new_col_name}'. Total records: {len(updated_df)}")

    except Exception as e:
        print(f"Error during update: {e}")
        raise

if __name__ == "__main__":
    update_projections()