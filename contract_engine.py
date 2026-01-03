import pandas as pd
import numpy as np
import time
from datetime import datetime
from nba_api.stats.endpoints import leaguedashplayerstats
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
from requests.exceptions import ReadTimeout, ConnectionError

# --- CONFIGURATION ---
pd.options.display.float_format = '{:,.2f}'.format
TRACKER_FILE = 'nba_contract_tracker.csv'
TRAINING_FILE = 'master_training_set.csv' # THE STATIC FILE YOU CREATED
CAP_2026_PROJECTED = 155100000 
FEATURES = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 'TS_PCT', 'USG_PCT', 'PIE']

# --- ROBUST FETCH HELPER (ONLY FOR 2025-26) ---
def fetch_nba_data(endpoint_call, max_retries=5):
    for i in range(max_retries):
        try:
            return endpoint_call.get_data_frames()[0]
        except (ReadTimeout, ConnectionError):
            wait_time = (i + 1) * 5
            print(f"Timeout. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    raise Exception("API Failed.")

def parse_fa_type(type_str):
    t = str(type_str).upper()
    status, rights, opt_val = "UFA", "Non-Bird", 0
    if "RFA" in t: status = "RFA"
    elif "PLAYER" in t: status = "Player Option"
    elif "CLUB" in t: status = "Club Option"
    if "BIRD" in t and "EARLY" not in t: rights = "Full Bird"
    elif "EARLY BIRD" in t: rights = "Early Bird"
    if "$" in t:
        try: opt_val = float(t.split('$')[1].replace('M', '')) * 1_000_000
        except: pass
    return status, rights, opt_val

# --- STEP 1: LOAD STATIC TRAINING DATA ---
def train_model():
    print("Loading static training data...")
    df_train = pd.read_csv(TRAINING_FILE)
    X, y = df_train[FEATURES], df_train['Cap_Pct']
    scaler = StandardScaler().fit(X)
    lasso = LassoCV(cv=5, random_state=42).fit(scaler.transform(X), y)
    return lasso, scaler

# --- STEP 2: RUN WEEKLY SNAPSHOT ---
def run_snapshot(model, scaler):
    today = datetime.today().strftime('%Y-%m-%d')
    print(f"📅 Snapshot for: {today}")
    
    # ONLY ONE API CALL NOW
    live_trad = fetch_nba_data(leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26', per_mode_detailed='Totals'))
    time.sleep(2)
    live_adv = fetch_nba_data(leaguedashplayerstats.LeagueDashPlayerStats(season='2025-26', measure_type_detailed_defense='Advanced'))
    live_df = pd.merge(live_trad, live_adv[['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'PIE']], on='PLAYER_ID')
    
    fa_2026 = pd.read_csv('NBA Free Agents 2026 - Sheet1.csv', skiprows=1)
    fa_2026[['Status', 'Rights', 'Option_Value']] = fa_2026['Type'].apply(lambda x: pd.Series(parse_fa_type(x)))
    
    final = pd.merge(live_df, fa_2026, left_on='PLAYER_NAME', right_on='Player (248)')
    final = final.rename(columns={'PLAYER_NAME': 'Player'})
    
    X_live = scaler.transform(final[FEATURES])
    final['Snapshot_Date'] = today
    final['Predicted_AAV'] = model.predict(X_live) * CAP_2026_PROJECTED
    
    # Save to Tracker
    new_data = final[['Player', 'Snapshot_Date', 'Predicted_AAV', 'PIE', 'Status']]
    try:
        master = pd.read_csv(TRACKER_FILE)
        master = pd.concat([master, new_data], ignore_index=True).drop_duplicates(subset=['Player', 'Snapshot_Date'])
    except:
        master = new_data
    
    master.to_csv(TRACKER_FILE, index=False)
    print("✅ Success.")

# --- RUN ---
lasso_model, data_scaler = train_model()
run_snapshot(lasso_model, data_scaler)
