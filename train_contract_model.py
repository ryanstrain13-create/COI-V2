import pandas as pd
import time
import joblib
from nba_api.stats.endpoints import leaguedashplayerstats
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

# Configuration
CAPS = {2023: 136021000, 2024: 140588000, 2025: 155100000}
SEASON_MAP = {2023: '2022-23', 2024: '2023-24', 2025: '2024-25'}
FEATURES = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 'TS_PCT', 'USG_PCT', 'PIE']

def clean_currency(val):
    if pd.isna(val) or val == '': return 0
    return float(str(val).replace('$', '').replace(',', '').strip())

def train():
    all_training_data = []
    for year, season in SEASON_MAP.items():
        print(f"Fetching training data for {season}...")
        trad = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed='Totals').get_data_frames()[0]
        adv = leaguedashplayerstats.LeagueDashPlayerStats(season=season, measure_type_detailed_defense='Advanced').get_data_frames()[0]
        stats = pd.merge(trad, adv[['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'PIE']], on='PLAYER_ID')

        fname = f'{year} NBA Free Agents.csv' if year != 2025 else '2025 NBA Free Agents (1).csv'
        fa_df = pd.read_csv(fname)
        p_col = [c for c in fa_df.columns if 'Player' in c][0]
        a_col = [c for c in fa_df.columns if 'AAV' in c][0]
        
        fa_df = fa_df[[p_col, a_col]].rename(columns={p_col: 'Player', a_col: 'Actual_AAV'})
        fa_df['Actual_AAV'] = fa_df['Actual_AAV'].apply(clean_currency)

        merged = pd.merge(stats, fa_df, left_on='PLAYER_NAME', right_on='Player')
        merged['Cap_Pct'] = merged['Actual_AAV'] / CAPS[year]
        all_training_data.append(merged)
        time.sleep(1.5)

    df_train = pd.concat(all_training_data).dropna()
    X, y = df_train[FEATURES], df_train['Cap_Pct']
    
    scaler = StandardScaler().fit(X)
    model = LassoCV(cv=5, random_state=42).fit(scaler.transform(X), y)
    
    # Save artifacts for Antigravity use
    joblib.dump(model, 'contract_model.joblib')
    joblib.dump(scaler, 'data_scaler.joblib')
    print("✅ Model trained and saved.")

if __name__ == "__main__":
    train()