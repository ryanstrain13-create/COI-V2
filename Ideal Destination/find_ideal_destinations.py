
import pandas as pd
import numpy as np
import os

# --- Configuration ---
# Paths relative to the script location (inside 'Ideal Destination')
# We need to go up one level specificly
BASE_DIR = '..' 
FILE_NEEDS = os.path.join(BASE_DIR, 'Archetype Analysis/lineup_recommendations.csv')
FILE_CAP = os.path.join(BASE_DIR, 'Salary Cap Analysis/Salary Cap Tracker - Sheet1.csv')
FILE_FA = os.path.join(BASE_DIR, 'Contract Training/2025 NBA Free Agents (1).csv')
FILE_OFF_CLUSTERS = os.path.join(BASE_DIR, 'Archetype Analysis/nba_player_clusters_offensive.csv')
FILE_DEF_CLUSTERS = os.path.join(BASE_DIR, 'Archetype Analysis/nba_defensive_clusters.csv')

OUTPUT_FILE = 'ideal_destinations.csv'

def load_data():
    print("Loading datasets...")
    needs_df = pd.read_csv(FILE_NEEDS)
    
    cap_df = pd.read_csv(FILE_CAP)
    def clean_money(x):
        if not isinstance(x, str): return 0
        clean = x.replace('$', '').replace(',', '')
        try: return float(clean)
        except: return 0
    cap_df['Cap_Space_Clean'] = cap_df['Cap SpaceAll'].apply(clean_money)
    cap_map = cap_df.set_index('Team')['Cap_Space_Clean'].to_dict()
    
    fa_df = pd.read_csv(FILE_FA)
    # Cleaning Columns from previous experience
    # Header format assumed consistent with previous step
    fa_df.columns = ['From', 'Player', 'Pos', 'Yrs', 'Value', 'AAV', 'Status']
    fa_df['AAV_Clean'] = fa_df['AAV'].apply(clean_money)
    
    off_clus = pd.read_csv(FILE_OFF_CLUSTERS)
    def_clus = pd.read_csv(FILE_DEF_CLUSTERS)
    off_map = off_clus.set_index('PLAYER_NAME')['Archetype_Name'].to_dict()
    def_map = def_clus.set_index('PLAYER_NAME')['Archetype_Name'].to_dict()
    
    # Map Archetypes to FA
    fa_df['OFF_Arch'] = fa_df['Player'].map(off_map).fillna('Unknown')
    fa_df['DEF_Arch'] = fa_df['Player'].map(def_map).fillna('Unknown')
    
    return needs_df, cap_map, fa_df

def score_fit(player_row, needs_df, cap_map):
    """
    Evaluate all 30 teams for this player.
    """
    player_o = player_row['OFF_Arch']
    player_d = player_row['DEF_Arch']
    player_aav = player_row['AAV_Clean']
    current_team = player_row['From']
    
    # Needs Cache: Team -> Set of Needed Archetypes
    # Needs DF has 'Rec_Add_OFF' and 'Rec_Add_DEF' columns
    # We aggregate ALL recommendations for a team.
    
    scores = []
    
    all_teams = cap_map.keys()
    
    for team in all_teams:
        score = 0
        reasons = []
        
        # 1. Need Check
        # Filter needs for this team
        team_needs = needs_df[needs_df['Team'] == team]
        
        needed_o = []
        needed_d = []
        for _, r in team_needs.iterrows():
            needed_o.extend([x.strip() for x in str(r['Rec_Add_OFF']).split(',')])
            needed_d.extend([x.strip() for x in str(r['Rec_Add_DEF']).split(',')])
            
        fit_o = player_o in needed_o
        fit_d = player_d in needed_d
        
        if fit_o: 
            score += 3
            reasons.append("Offensive Need")
        if fit_d: 
            score += 3
            reasons.append("Defensive Need")
            
        # 2. Budget Check
        cap_space = cap_map.get(team, 0)
        is_incumbent = (team == current_team)
        
        if is_incumbent:
            # Bird Rights - Can always sign
            score += 1
            reasons.append("Incumbent")
            can_afford = True
        elif cap_space >= player_aav:
             # Can afford outright
            score += 2 # Cap space is valuable
            reasons.append("Cap Space Fit")
            can_afford = True
            
        elif player_aav <= 5200000: # Taxpayer MLE approx
            # Accessible to anyone
            can_afford = True
        else:
            can_afford = False
            
        if not can_afford:
            score = -99 # Disqualify high cost players from broke teams
            reasons = ["Cannot Afford"]
            
        # 3. Winning Match?
        # Maybe preference for better teams? 
        # Using Cap Space as proxy (Low cap often = good team lol, not always)
        # For this exercise, simple 'Fit + Money' is enough.
        
        scores.append({
            'Team': team,
            'Score': score,
            'Reason': ", ".join(reasons)
        })
        
    # Sort and return best
    scores.sort(key=lambda x: x['Score'], reverse=True)
    best = scores[0]
    
    # If score is garbage, return "Unsigned" logic or Current Team fallback
    if best['Score'] < 0:
        return current_team, 0, "Retention (No Market Fit)"
        
    return best['Team'], best['Score'], best['Reason']

def main():
    needs, caps, fas = load_data()
    
    results = []
    print("Finding Ideal Destinations...")
    
    for _, fa in fas.iterrows():
        # Skip if unknown archetype (minor leaguers etc)
        if fa['OFF_Arch'] == "Unknown": continue
        
        dest_team, score, reason = score_fit(fa, needs, caps)
        
        results.append({
            'Player': fa['Player'],
            'Free_Agent_Class_Rank': "N/A", # Could infer from AAV
            'Current_Team': fa['From'],
            'AAV': f"${fa['AAV_Clean']:,.0f}",
            'Ideal_Destination': dest_team,
            'Fit_Score': score,
            'Reasoning': reason,
            'Archetypes': f"{fa['OFF_Arch']} | {fa['DEF_Arch']}"
        })
        
    df = pd.DataFrame(results)
    
    # Sort by Player Value (AAV) desc
    # Need to convert string back to float for sorting or reuse clean
    # Sort by the input order (Rank) is probably best as input was ranked.
    
    print(f"Saving {len(df)} recommendations to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
