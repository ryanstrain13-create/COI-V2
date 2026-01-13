import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime

# --- Configuration ---
DATA_DIR = '/Users/ryanstrain/Desktop/COI V2/Archetype and Cluster Analysis'
WEEKLY_DIR = '/Users/ryanstrain/Desktop/COI V2/Weekly Updates/Contract Value Weekly Update'

# Golden Training Data (from Master creation)
# Assume these files exist and define the "Truth" for 2025
FILE_2025_OFF = os.path.join(DATA_DIR, 'nba_player_archetypes_2025.csv')
FILE_2025_DEF = os.path.join(DATA_DIR, 'nba_defensive_archetypes_2025.csv')

# Weekly Data Input
FILE_WEEKLY_INPUT = os.path.join(WEEKLY_DIR, 'nba_timeseries_stats_2025_26.csv')

# Weekly Output (Archetype Timeseries)
FILE_WEEKLY_OUTPUT = os.path.join(WEEKLY_DIR, 'nba_archetype_timeseries_2025_26.csv')

# --- Feature Definitions (MUST MATCH TRAIN AND PREDICT) ---
OFF_FEATURES = [
    'Isolation_FREQ', 'Isolation_PPP',
    'PRBallHandler_FREQ', 'PRBallHandler_PPP',
    'PRRollMan_FREQ', 'PRRollMan_PPP',
    'Postup_FREQ', 'Postup_PPP',
    'Spotup_FREQ', 'Spotup_PPP',
    'Handoff_FREQ', 'Handoff_PPP',
    'Cut_FREQ', 'Cut_PPP',
    'OffScreen_FREQ', 'OffScreen_PPP',
    'OffRebound_FREQ', 'OffRebound_PPP', 
    'Transition_FREQ', 'Transition_PPP',
    'USG_PCT', 'AST_PCT'
]

DEF_FEATURES = [
    'STL', 'BLK', 'DREB_PCT', 'DEF_RATING',
    'CONTESTED_SHOTS' 
    # Must match what was used in Master Archetype creation (intersection of available feats)
]

def load_and_prep_2025_off(file_path):
    df = pd.read_csv(file_path)
    # Map 2025 Golden columns to Standard OFF_FEATURES names
    rename_map = {
        'PICK__ROLL_BALL_HANDLER_FREQ': 'PRBallHandler_FREQ',
        'PICK__ROLL_BALL_HANDLER_PPP': 'PRBallHandler_PPP',
        'PICK__ROLL_ROLL_MAN_FREQ': 'PRRollMan_FREQ',
        'PICK__ROLL_ROLL_MAN_PPP': 'PRRollMan_PPP',
        'ISOLATION_FREQ': 'Isolation_FREQ',
        'ISOLATION_PPP': 'Isolation_PPP',
        'HANDOFF_FREQ': 'Handoff_FREQ',
        'HANDOFF_PPP': 'Handoff_PPP',
        'OFF_SCREEN_FREQ': 'OffScreen_FREQ',
        'OFF_SCREEN_PPP': 'OffScreen_PPP',
        'CUT_FREQ': 'Cut_FREQ',
        'CUT_PPP': 'Cut_PPP',
        'PUTBACK_FREQ': 'OffRebound_FREQ',
        'PUTBACK_PPP': 'OffRebound_PPP',
        'POST_UP_FREQ': 'Postup_FREQ',
        'POST_UP_PPP': 'Postup_PPP',
        'SPOT_UP_FREQ': 'Spotup_FREQ',
        'SPOT_UP_PPP': 'Spotup_PPP',
        'TRANSITION_FREQ': 'Transition_FREQ',
        'TRANSITION_PPP': 'Transition_PPP'
    }
    df = df.rename(columns=rename_map)
    return df

def load_and_prep_2025_def(file_path):
    df = pd.read_csv(file_path)
    return df

def train_kmeans(df, features, k, random_state=42):
    scaler = StandardScaler()
    X = df[features].fillna(0)
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    kmeans.fit(X_scaled)
    
    return kmeans, scaler

def map_clusters_to_labels(df, cluster_col, label_col):
    mapping = {}
    if label_col not in df.columns:
        return mapping
        
    for cluster_id in df[cluster_col].unique():
        subset = df[df[cluster_col] == cluster_id]
        if not subset.empty:
            mode_label = subset[label_col].mode()
            if not mode_label.empty:
                mapping[cluster_id] = mode_label[0]
            else:
                mapping[cluster_id] = f"Cluster {cluster_id}"
    return mapping

def main():
    print("--- Starting Weekly Archetype Update ---")
    
    # 1. Train Models on Golden Data (2025 Definitions)
    print("Training models on 2025 Golden Data...")
    df_off_gold = load_and_prep_2025_off(FILE_2025_OFF)
    df_def_gold = load_and_prep_2025_def(FILE_2025_DEF)
    
    # Offense
    k_off = 8
    kmeans_off, scaler_off = train_kmeans(df_off_gold, OFF_FEATURES, k_off)
    # Create Label Map
    df_off_gold['Cluster'] = kmeans_off.predict(scaler_off.transform(df_off_gold[OFF_FEATURES].fillna(0)))
    # Try to find label col
    off_label_col = next((c for c in ['Offensive Archetype', 'Archetype', 'Aggr_Archetype'] if c in df_off_gold.columns), None)
    off_map = map_clusters_to_labels(df_off_gold, 'Cluster', off_label_col) if off_label_col else {i:f"Off_Cluster_{i}" for i in range(k_off)}
    
    # Defense
    k_def = 5
    kmeans_def, scaler_def = train_kmeans(df_def_gold, DEF_FEATURES, k_def)
    df_def_gold['Cluster'] = kmeans_def.predict(scaler_def.transform(df_def_gold[DEF_FEATURES].fillna(0)))
    def_label_col = next((c for c in ['Defensive Archetype', 'Archetype'] if c in df_def_gold.columns), None)
    def_map = map_clusters_to_labels(df_def_gold, 'Cluster', def_label_col) if def_label_col else {i:f"Def_Cluster_{i}" for i in range(k_def)}
    
    print("Models trained.")
    
    # 2. Load Weekly Data
    print(f"Loading Weekly Data from {FILE_WEEKLY_INPUT}...")
    if not os.path.exists(FILE_WEEKLY_INPUT):
        print("Weekly input file not found.")
        return

    df_weekly = pd.read_csv(FILE_WEEKLY_INPUT)
    
    # We want to process NEW snapshots. However, fetching all history might be safer to ensure consistency?
    # Or just process the latest snapshot.
    # User said "progression of a player...". If we append to a new file, we should process rows that are NOT in the output file yet.
    
    # Load existing output if any
    processed_keys = set()
    if os.path.exists(FILE_WEEKLY_OUTPUT):
        df_existing = pd.read_csv(FILE_WEEKLY_OUTPUT)
        # Create a unique key: PlayerID + Timestamp
        if 'SNAPSHOT_TIME' in df_existing.columns and 'PLAYER_ID' in df_existing.columns:
            processed_keys = set(zip(df_existing['SNAPSHOT_TIME'], df_existing['PLAYER_ID']))
    
    # Filter for unprocessed rows
    # It's faster to do this in memory or just re-process the last snapshot if the file is huge.
    # Let's process ANY row that isn't in processed_keys.
    
    # Identify rows to process
    rows_to_process = []
    for idx, row in df_weekly.iterrows():
        key = (row['SNAPSHOT_TIME'], row['PLAYER_ID'])
        if key not in processed_keys:
            rows_to_process.append(row)
            
    if not rows_to_process:
        print("No new data to process.")
        return
        
    df_new = pd.DataFrame(rows_to_process)
    print(f"Processing {len(df_new)} new player-snapshots...")
    
    # 3. Predict Archetypes
    # Prepare Features (Fill NA with 0)
    
    # Check if necessary columns exist (if script ran before weekly_perf was updated, cols might be missing)
    missing_feats = [f for f in OFF_FEATURES + DEF_FEATURES if f not in df_new.columns]
    if missing_feats:
        print(f"Warning: Missing features in weekly data: {missing_feats}")
        print("Filling with 0 to proceed, but results may be inaccurate for old snapshots.")
        for f in missing_feats:
            df_new[f] = 0
            
    # Offense Prediction
    X_off = df_new[OFF_FEATURES].fillna(0)
    df_new['Off_Cluster'] = kmeans_off.predict(scaler_off.transform(X_off))
    df_new['Offensive Archetype'] = df_new['Off_Cluster'].map(off_map)
    
    # Defense Prediction
    X_def = df_new[DEF_FEATURES].fillna(0)
    df_new['Def_Cluster'] = kmeans_def.predict(scaler_def.transform(X_def))
    df_new['Defensive Archetype'] = df_new['Def_Cluster'].map(def_map)
    
    # 4. Save to Output
    cols_to_save = [
        'SNAPSHOT_TIME', 'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION',
        'Offensive Archetype', 'Defensive Archetype',
        'Off_Cluster', 'Def_Cluster',
        'USG_PCT', 'AST_PCT', 'DEF_RATING' 
    ]
    # Add other useful stats if desired
    
    # Append to CSV
    header = not os.path.exists(FILE_WEEKLY_OUTPUT)
    df_new[cols_to_save].to_csv(FILE_WEEKLY_OUTPUT, mode='a', index=False, header=header)
    
    print(f"Successfully added rows to {FILE_WEEKLY_OUTPUT}")

if __name__ == "__main__":
    main()
