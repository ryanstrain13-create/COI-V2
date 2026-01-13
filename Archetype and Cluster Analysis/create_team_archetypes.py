
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- Configuration ---
INPUT_FILE = 'nba_team_archetypes_2025.csv'
OUTPUT_FILE = 'nba_team_clusters.csv'
N_CLUSTERS = 6
RANDOM_STATE = 42

FEATURES = [
    'PACE',
    'AST_PCT',
    '3PAr',
    'OREB_PCT',
    'FB_PCT', 
    'PAINT_PCT',
    'DEF_RATING',
    'TM_TOV_PCT'
]

def generate_persona_name(center_series):
    """
    Generates a descriptive name for a TEAM playstyle based on feature z-scores.
    """
    # Create z-score series
    z_scores = center_series.copy()
    
    traits = []
    
    # Check defining characteristics
    # Note: High DEF_RATING is BAD defense. Low DEF_RATING is GOOD defense.
    # We must handle this inversion for naming.
    
    if z_scores['PACE'] > 0.8:
        traits.append("High Pace")
    elif z_scores['PACE'] < -0.8:
        traits.append("Slow Grit")
        
    if z_scores['3PAr'] > 0.8:
        traits.append("3-Point Heavy")
    elif z_scores['3PAr'] < -0.8:
        traits.append("Rim/Midrange Focus")
        
    if z_scores['AST_PCT'] > 0.8:
        traits.append("High Ball Movement")
    elif z_scores['AST_PCT'] < -0.8:
        traits.append("Iso/Heliocentric")
        
    if z_scores['DEF_RATING'] < -0.8: # Low rating = Good D
        traits.append("Elite Defense")
    elif z_scores['DEF_RATING'] > 0.8:
        traits.append("Poor Defense")
        
    if z_scores['OREB_PCT'] > 0.8:
        traits.append("Glass Crashers")
        
    if z_scores['FB_PCT'] > 0.8:
        traits.append("Transition Heavy")
        
    if not traits:
        return "Balanced / Average Style"
        
    return " + ".join(traits[:3])

def main():
    print(f"Loading {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print("File not found.")
        return

    # 1. Feature Prep
    X = df[FEATURES].fillna(0)
    
    # 2. Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=FEATURES, index=df.index)
    
    # 3. Clustering
    print(f"Clustering into {N_CLUSTERS} styles...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    clusters = kmeans.fit_predict(X_scaled_df)
    df['Cluster'] = clusters
    
    # 4. Analysis & Personas
    centers = pd.DataFrame(kmeans.cluster_centers_, columns=FEATURES)
    persona_map = {}
    
    print("\n--- Team Playstyles ---")
    for cid in range(N_CLUSTERS):
        center = centers.iloc[cid]
        name = generate_persona_name(center)
        persona_map[cid] = name
        
        teams_in_cluster = df[df['Cluster'] == cid]['TEAM_NAME'].tolist()
        print(f"Cluster {cid}: {name} (n={len(teams_in_cluster)})")
        print(f"  Teams: {', '.join(teams_in_cluster)}")
        
    df['Playstyle_Name'] = df['Cluster'].map(persona_map)
    
    # 5. Save
    output_cols = ['TEAM_ID', 'TEAM_NAME', 'Playstyle_Name', 'Cluster'] + FEATURES
    df[output_cols].to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
