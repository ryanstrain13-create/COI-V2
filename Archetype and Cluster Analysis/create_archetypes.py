
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- Configuration ---
INPUT_FILE = 'nba_player_archetypes_2025.csv'
OUTPUT_FILE = 'nba_player_clusters.csv'
MIN_GP = 10
MIN_MPG = 10
N_CLUSTERS = 8
RANDOM_STATE = 42

# Define features for clustering
FEATURES = [
    'USG_PCT',
    'AST_PCT',
    'PICK__ROLL_BALL_HANDLER_FREQ',
    'PICK__ROLL_ROLL_MAN_FREQ',
    'SPOT_UP_FREQ',
    'POST_UP_FREQ',
    'OFF_SCREEN_FREQ',
    'CUT_FREQ',
    'ISOLATION_FREQ',
    'TRANSITION_FREQ'
]

def generate_persona_name(center_series):
    """
    Generates a descriptive name for a cluster based on its standardized feature center.
    Returns a string like 'High P&R Handler, High AST'.
    """
    # Sort features by their Z-score value in descending order
    sorted_features = center_series.sort_values(ascending=False)
    
    # Take the top 2-3 defining traits (e.g., Z-score > 0.5)
    traits = []
    for feature, z_score in sorted_features.items():
        if z_score < 0.2: # Stop if we get to average/below average traits
            break
            
        name_map = {
            'USG_PCT': 'Usage',
            'AST_PCT': 'Playmaking',
            'PICK__ROLL_BALL_HANDLER_FREQ': 'P&R Handler',
            'PICK__ROLL_ROLL_MAN_FREQ': 'Roll Man',
            'SPOT_UP_FREQ': 'Spot Up',
            'POST_UP_FREQ': 'Post Up',
            'OFF_SCREEN_FREQ': 'Off-Screen',
            'CUT_FREQ': 'Cutter',
            'ISOLATION_FREQ': 'Iso',
            'TRANSITION_FREQ': 'Transition'
        }
        
        readable_feature = name_map.get(feature, feature)
        
        if z_score > 1.5:
            traits.append(f"Elite {readable_feature}")
        elif z_score > 0.8:
            traits.append(f"High {readable_feature}")
        elif z_score > 0.2:
            traits.append(f"{readable_feature}")
            
        if len(traits) >= 3:
            break
            
    if not traits:
        return "Balanced / Low Usage Role"
        
    return ", ".join(traits)

def main():
    print(f"Loading data from {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Please ensure the data fetch script ran successfully.")
        return

    # 1. Filter Data
    original_count = len(df)
    df_filtered = df[(df['GP'] >= MIN_GP) & (df['MIN'] >= MIN_MPG)].copy()
    print(f"Filtered data: {len(df_filtered)} players (from {original_count})")

    # 2. Preprocessing
    # Fill NaNs with 0 for playtypes (assuming NaN = 0 frequency)
    # Check if columns exist first
    missing_cols = [col for col in FEATURES if col not in df_filtered.columns]
    if missing_cols:
        print(f"Error: Missing columns in CSV: {missing_cols}")
        return

    X = df_filtered[FEATURES].fillna(0)

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Convert back to DataFrame for easier handling with column names
    X_scaled_df = pd.DataFrame(X_scaled, columns=FEATURES, index=df_filtered.index)

    # 3. Clustering
    print(f"Running K-Means (k={N_CLUSTERS})...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    clusters = kmeans.fit_predict(X_scaled_df)
    
    df_filtered['Cluster'] = clusters

    # 4. Generate Personas
    cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=FEATURES)
    
    persona_map = {}
    print("\n--- Cluster Personas ---")
    for cluster_id in range(N_CLUSTERS):
        center = cluster_centers.iloc[cluster_id]
        persona_name = generate_persona_name(center)
        persona_map[cluster_id] = persona_name
        
        # Find sizing
        count = len(df_filtered[df_filtered['Cluster'] == cluster_id])
        
        print(f"Cluster {cluster_id}: {persona_name} (n={count})")
        # Print top players
        example_players = df_filtered[df_filtered['Cluster'] == cluster_id].sort_values('USG_PCT', ascending=False)['PLAYER_NAME'].head(5).tolist()
        print(f"  Examples: {', '.join(example_players)}")

    df_filtered['Archetype_Name'] = df_filtered['Cluster'].map(persona_map)

    # 5. Save
    print(f"\nSaving results to {OUTPUT_FILE}...")
    output_cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'Archetype_Name', 'Cluster'] + FEATURES
    df_filtered[output_cols].to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
