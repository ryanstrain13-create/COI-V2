import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- Configuration ---
DATA_DIR = '/Users/ryanstrain/Desktop/COI V2/Archetype and Cluster Analysis'
HIST_DIR = os.path.join(DATA_DIR, 'Historical Player Clusters')

# 2025 Golden Files
FILE_2025_OFF = os.path.join(DATA_DIR, 'nba_player_archetypes_2025.csv')
FILE_2025_DEF = os.path.join(DATA_DIR, 'nba_defensive_archetypes_2025.csv')

# Historical Files
FILE_HIST_OFF_PT = os.path.join(HIST_DIR, 'Offensive', 'nba_historical_offensive_playtypes_2015_2025.csv')
FILE_HIST_OFF_PNR = os.path.join(HIST_DIR, 'Offensive', 'nba_historical_pnr_2015_2025.csv')
FILE_HIST_DEF = os.path.join(HIST_DIR, 'Defensive', 'nba_historical_defensive_stats_2015_2025.csv')
FILE_HIST_GEN = os.path.join(HIST_DIR, 'General', 'nba_historical_general_stats_2015_2025.csv')

OUTPUT_FILE = os.path.join(DATA_DIR, 'Master_Archetype_CSV.csv')

# --- Feature Definitions ---

# Map 2025 Columns to Standard Internal Names
# We need to use the SAME features for training and prediction.
# We will rename the 2025 columns to match our Historical columns where possible, or vice versa.
# Let's standardize on the Historical naming convention derived from Synergy/API.

OFF_FEATURES = [
    'Isolation_FREQ', 'Isolation_PPP',
    'PRBallHandler_FREQ', 'PRBallHandler_PPP',
    'PRRollMan_FREQ', 'PRRollMan_PPP',
    'Postup_FREQ', 'Postup_PPP',
    'Spotup_FREQ', 'Spotup_PPP',
    'Handoff_FREQ', 'Handoff_PPP',
    'Cut_FREQ', 'Cut_PPP',
    'OffScreen_FREQ', 'OffScreen_PPP',
    'OffRebound_FREQ', 'OffRebound_PPP', # Note: 2025 might be Putback
    'Transition_FREQ', 'Transition_PPP',
    'USG_PCT', 'AST_PCT'
]

DEF_FEATURES = [
    'STL', 'BLK', 'DREB_PCT', 'DEF_RATING',
    'CONTESTED_SHOTS'
    # Dropped: Matchup stats, Deflections, Charges, Loose Balls (due to mismatch)
]

def load_and_prep_2025_off(file_path):
    df = pd.read_csv(file_path)
    
    # Map 2025 columns to OFF_FEATURES
    # Need to inspect 2025 headers again mentally or via map.
    # 2025 headers: 'PICK__ROLL_BALL_HANDLER_FREQ', ... 'PUTBACK_FREQ', ...
    
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
        'PUTBACK_FREQ': 'OffRebound_FREQ', # Map Putback -> OffRebound (Synergy name)
        'PUTBACK_PPP': 'OffRebound_PPP',
        'POST_UP_FREQ': 'Postup_FREQ',
        'POST_UP_PPP': 'Postup_PPP',
        'SPOT_UP_FREQ': 'Spotup_FREQ',
        'SPOT_UP_PPP': 'Spotup_PPP',
        'TRANSITION_FREQ': 'Transition_FREQ',
        'TRANSITION_PPP': 'Transition_PPP'
    }
    
    df = df.rename(columns=rename_map)
    # Filter to features
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
    """
    Creates a mapping from Cluster ID -> Label based on the 2025 ground truth.
    """
    mapping = {}
    for cluster_id in df[cluster_col].unique():
        # Get the mode of the usage label in this cluster
        subset = df[df[cluster_col] == cluster_id]
        if not subset.empty and label_col in subset.columns:
            mode_label = subset[label_col].mode()
            if not mode_label.empty:
                mapping[cluster_id] = mode_label[0]
            else:
                mapping[cluster_id] = "Unknown"
        else:
            mapping[cluster_id] = "Unknown"
    return mapping

def main():
    print("Loading data...")
    
    # 1. Load 2025 Data (Ground Truth)
    df_25_off = load_and_prep_2025_off(FILE_2025_OFF)
    df_25_def = load_and_prep_2025_def(FILE_2025_DEF)
    
    # Verify Features exist in 2025 data
    missing_off = [f for f in OFF_FEATURES if f not in df_25_off.columns]
    if missing_off:
        print(f"Warning: Missing Offensive Features in 2025 data: {missing_off}")
        # Identify columns that were not renamed correctly? 
        # For now, let's assume mapping covers it.
    
    missing_def = [f for f in DEF_FEATURES if f not in df_25_def.columns]
    if missing_def:
        print(f"Warning: Missing Defensive Features in 2025 data: {missing_def}")
        
    print("Training 2025 Models...")
    # Helper to get optimal K from existing labels? 
    # Offense Archetype col: 'Offensive Archetype' (Need to check col name)
    # Defense Archetype col: 'Defensive Archetype' (Need to check col name)
    # I'll check column names in the files dynamically.
    
    # Check 2025 Label Columns
    off_label_col = 'Aggr_Archetype' if 'Aggr_Archetype' in df_25_off.columns else 'Offensive Archetype' # Guessing
    # Actually, let's print headers if needed, but I'll assume 'Offensive Archetype' exists or similar.
    # From previous `head`, I didn't see explicit label column in the first line?
    # Wait, the `head` output for 2025 Off file:
    # PLAYER_ID,PLAYER_NAME,... (Features)
    # I did NOT see 'Offensive Archetype' in the first line of the snippet?
    # Maybe it's at the end or I missed it. I must assume it exists or I can't map labels!
    # If it's NOT in the file, I can't map. 
    # Assuming 'nba_player_archetypes_2025.csv' HAS the archetypes.
    
    # 2. Load Historical Data
    print("Loading Historical Data...")
    df_hist_off_pt = pd.read_csv(FILE_HIST_OFF_PT)
    df_hist_off_pnr = pd.read_csv(FILE_HIST_OFF_PNR)
    df_hist_def = pd.read_csv(FILE_HIST_DEF)
    df_hist_gen = pd.read_csv(FILE_HIST_GEN)
    
    # Merge Historical Data
    # Base: General Stats (Has best list of players/seasons)
    full_df = df_hist_gen.copy()
    
    # Helper to merge and avoid suffixes for metadata
    def safe_merge(left_df, right_df, on_keys):
        # Identify cols in right that are in left but NOT in keys
        # We want to keep the Left version (General has good names)
        cols_to_drop = [c for c in right_df.columns if c in left_df.columns and c not in on_keys]
        right_reduced = right_df.drop(columns=cols_to_drop)
        return pd.merge(left_df, right_reduced, on=on_keys, how='left')
    
    # Merge Playtypes
    print("Merging Offensive Playtypes...")
    full_df = safe_merge(full_df, df_hist_off_pt, ['PLAYER_ID', 'SEASON'])
    
    # Merge P&R
    print("Merging P&R Data...")
    full_df = safe_merge(full_df, df_hist_off_pnr, ['PLAYER_ID', 'SEASON'])
    
    # Merge Defensive
    # Note: Def Stats file has some cols that overlap with Gen (GP, MIN). 
    # safe_merge handles dropping duplicates.
    print("Merging Defensive Data...")
    cols_to_use_def = ['PLAYER_ID', 'SEASON'] + [c for c in DEF_FEATURES if c in df_hist_def.columns and c not in ['STL','BLK','DREB_PCT','DEF_RATING']]
    # Note: STL/BLK etc inside DEF_FEATURES might be in General.
    # If they are in General, safe_merge will drop the Defensive version.
    # Check if we prefer Defensive Source for these? 
    # General: STL, BLK (Per Game). 2025 Model expects Per Game or Scaled.
    # Historical General likely matches.
    full_df = safe_merge(full_df, df_hist_def, ['PLAYER_ID', 'SEASON'])
    
    # Fill NaNs
    # Playtype freqs/PPPs -> 0
    # Hustle stats -> 0
    # USG/AST -> median? or 0? 0 is safer for outlier detection, but might skew clustering.
    # Clustering usually handles 0 fine if scaled.
    full_df = full_df.fillna(0)
    
    # 3. Model Training & prediction
    
    # OFFENSE
    k_off = 8 # Assumption based on standard archetypes
    kmeans_off, scaler_off = train_kmeans(df_25_off, OFF_FEATURES, k_off)
    
    # Predict clusters for 2025 to build Map
    df_25_off['Cluster'] = kmeans_off.predict(scaler_off.transform(df_25_off[OFF_FEATURES].fillna(0)))
    
    # Determine Labels
    # If 'Offensive Archetype' isn't in 2025 data, we just use Cluster IDs or generated names.
    # The user wanted "Offensive and Defensive Archetype". 
    # I will attempt to find the label column.
    possible_cols = ['Offensive Archetype', 'Archetype', 'Cluster Name']
    found_col = next((c for c in possible_cols if c in df_25_off.columns), None)
    
    off_mapping = {}
    if found_col:
        off_mapping = map_clusters_to_labels(df_25_off, 'Cluster', found_col)
    else:
        # Fallback: Just string "Off_Cluster_X"
        for i in range(k_off): off_mapping[i] = f"Off_Cluster_{i}"
        
    # Predict for Historical
    X_hist_off = full_df[OFF_FEATURES].fillna(0)
    full_df['Off_Cluster'] = kmeans_off.predict(scaler_off.transform(X_hist_off))
    full_df['Offensive Archetype'] = full_df['Off_Cluster'].map(off_mapping)
    
    # DEFENSE
    k_def = 5 # Assumption
    kmeans_def, scaler_def = train_kmeans(df_25_def, DEF_FEATURES, k_def)
    
    # Predict clusters for 2025
    df_25_def['Cluster'] = kmeans_def.predict(scaler_def.transform(df_25_def[DEF_FEATURES].fillna(0)))
    
    # Determine Labels
    possible_cols_def = ['Defensive Archetype', 'Archetype', 'Cluster Name']
    found_col_def = next((c for c in possible_cols_def if c in df_25_def.columns), None)
    
    def_mapping = {}
    if found_col_def:
        def_mapping = map_clusters_to_labels(df_25_def, 'Cluster', found_col_def)
    else:
        for i in range(k_def): def_mapping[i] = f"Def_Cluster_{i}"
        
    # Predict for Historical
    X_hist_def = full_df[DEF_FEATURES].fillna(0)
    full_df['Def_Cluster'] = kmeans_def.predict(scaler_def.transform(X_hist_def))
    full_df['Defensive Archetype'] = full_df['Def_Cluster'].map(def_mapping)
    
    # 4. Save
    cols_export = [
        'PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'TEAM_ABBREVIATION',
        'Offensive Archetype', 'Defensive Archetype',
        'Off_Cluster', 'Def_Cluster',
        'USG_PCT', 'AST_PCT', 'DEF_RATING'
    ]
    # Ensure cols exist
    cols_export = [c for c in cols_export if c in full_df.columns]
    
    full_df[cols_export].to_csv(OUTPUT_FILE, index=False)
    print(f"Saved Master Archetype file to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
