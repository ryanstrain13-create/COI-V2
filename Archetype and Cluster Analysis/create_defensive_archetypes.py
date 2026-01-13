
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- Configuration ---
INPUT_FILE = 'nba_defensive_archetypes_2025.csv'
OUTPUT_FILE = 'nba_defensive_clusters.csv'
MIN_GP = 10
MIN_MPG = 10
N_CLUSTERS = 8 # Target distinct defensive roles
RANDOM_STATE = 42

def generate_persona_name(center_series):
    """
    Generates a descriptive name for a defensive cluster.
    """
    sorted_features = center_series.sort_values(ascending=False)
    
    traits = []
    
    # Check for specific role definitions based on position guarded
    d_pos_cols = ['dPG_PCT', 'dSG_PCT', 'dSF_PCT', 'dPF_PCT', 'dC_PCT']
    # Find max guarded position
    max_pos = center_series[d_pos_cols].idxmax()
    max_pos_val = center_series[max_pos]
    
    primary_guarding = ""
    if max_pos_val > 0.5:
        primary_guarding = f"Guards {max_pos[1:-4]}"
        
    for feature, z_score in sorted_features.items():
        if z_score < 0.2: break
        
        if feature in d_pos_cols: continue # Handled above roughly
        
        name_map = {
            'DEFLECTIONS_PER_75': 'Disruptor',
            'STL_PER_75': 'Steals',
            'BLK_PER_75': 'Rim Protection',
            'DREB_PCT': 'Rebounding',
            'VERSATILITY_RATING': 'Versatile',
            'MATCHUP_DIFFICULTY': 'High Difficulty',
        }
        
        readable = name_map.get(feature, feature)
        
        if z_score > 1.5:
            traits.append(f"Elite {readable}")
        elif z_score > 0.8:
            traits.append(f"High {readable}")
        elif z_score > 0.4:
            traits.append(f"{readable}")
            
    # Combine
    name = ", ".join(traits[:3])
    if primary_guarding and "Versatile" not in name:
        name = f"{primary_guarding} ({name})"
    elif not name:
        name = "Low Activity / Hidden"
        
    return name

def main():
    print(f"Loading {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print("File not found.")
        return

    # 1. Filter
    original = len(df)
    df = df[(df['GP'] >= MIN_GP) & (df['MIN'] >= MIN_MPG)].copy()
    print(f"Filtered to {len(df)} players (from {original})")

    # 2. Feature Engineering
    # Calculate Per 75 Possessions (Approx using 36 mins)
    df['STL_PER_75'] = (df['STL'] / df['MIN_HUSTLE']) * 36
    df['BLK_PER_75'] = (df['BLK'] / df['MIN_HUSTLE']) * 36
    # Note: MIN_HUSTLE is per game.
    # Check for NaNs/Inf usually not an issue with filter > 10 MPG
    
    features = [
        'DEFLECTIONS_PER_75', 'STL_PER_75', 'BLK_PER_75',
        'DREB_PCT', 'VERSATILITY_RATING', 'MATCHUP_DIFFICULTY',
        'dPG_PCT', 'dSG_PCT', 'dSF_PCT', 'dPF_PCT', 'dC_PCT'
    ]
    
    # Fill Nans
    X = df[features].fillna(0)
    
    # 3. Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=features, index=df.index)
    
    # 4. Cluster
    print(f"Clustering (k={N_CLUSTERS})...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    clusters = kmeans.fit_predict(X_scaled_df)
    df['Cluster'] = clusters
    
    # 5. Personas
    centers = pd.DataFrame(kmeans.cluster_centers_, columns=features)
    persona_map = {}
    
    print("\n--- Defensive Archetypes ---")
    for cid in range(N_CLUSTERS):
        center = centers.iloc[cid]
        # Custom logic for naming to be more specific than generic generator
        # Check defining characteristics manually for better naming?
        # Or improve the generator. Let's try generator first.
        name = generate_persona_name(center)
        
        # Hardcoded overrides for clarity if patterns are obvious
        # (This is safer than random words if the generator is weak)
        # Check specific logical groups:
        # High BLK + High dC% -> Rim Protector
        # High Deflections + High Difficulty -> POA/Wing Stopper
        
        if center['dC_PCT'] > 1.0 and center['BLK_PER_75'] > 0.5:
            name = "Anchor Big / Rim Protector"
        elif center['dPG_PCT'] > 1.0 and center['MATCHUP_DIFFICULTY'] > 0.5:
            name = "Point of Attack Stopper"
            
        persona_map[cid] = name
        
        count = len(df[df['Cluster'] == cid])
        examples = df[df['Cluster'] == cid].sort_values('MATCHUP_DIFFICULTY', ascending=False).head(5)['PLAYER_NAME'].tolist()
        print(f"Cluster {cid}: {name} (n={count})")
        print(f"  Examples: {', '.join(examples)}")
        
    df['Archetype_Name'] = df['Cluster'].map(persona_map)
    
    # 6. Save
    cols = ['PLAYER_ID', 'PLAYER_NAME', 'Archetype_Name', 'Cluster'] + features
    df[cols].to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
