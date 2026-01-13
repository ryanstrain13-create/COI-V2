
import pandas as pd
import numpy as np
import os

# --- Configuration ---
# File Paths (Relative to Archetype Analysis folder or Absolute)
BASE_DIR = '/Users/ryanstrain/Desktop/COI V2'
FILE_NEEDS = os.path.join(BASE_DIR, 'Archetype Analysis', 'lineup_recommendations.csv')
FILE_CAP = os.path.join(BASE_DIR, 'Salary Cap Analysis', 'Salary Cap Tracker - Sheet1.csv')
FILE_APRON = os.path.join(BASE_DIR, 'Salary Cap Analysis', 'Apron 2024-2025 - Sheet1.csv')
FILE_FA = os.path.join(BASE_DIR, 'Contract Training', '2025 NBA Free Agents (1).csv')
FILE_OFF_CLUSTERS = os.path.join(BASE_DIR, 'Archetype Analysis', 'nba_player_clusters_offensive.csv')
FILE_DEF_CLUSTERS = os.path.join(BASE_DIR, 'Archetype Analysis', 'nba_defensive_clusters.csv')

OUTPUT_FILE = os.path.join(BASE_DIR, 'Archetype Analysis', 'final_free_agent_targets.csv')

def load_data():
    print("Loading datasets...")
    
    # 1. Needs
    needs_df = pd.read_csv(FILE_NEEDS)
    
    # 2. Cap Space
    # Rank,Team,Record,...,Cap SpaceAll
    cap_df = pd.read_csv(FILE_CAP)
    # Clean Cap Space: "-$1,220,220" -> -1220220
    def clean_money(x):
        if not isinstance(x, str): return 0
        clean = x.replace('$', '').replace(',', '')
        return float(clean)
        
    cap_df['Cap_Space_Clean'] = cap_df['Cap SpaceAll'].apply(clean_money)
    cap_map = cap_df.set_index('Team')['Cap_Space_Clean'].to_dict()
    
    # 3. Apron
    # Rank,Team,...,1st ApronSpace
    apron_df = pd.read_csv(FILE_APRON)
    # We really just need to know if they are deeply negative/hard capped?
    # Simple logic: Just check availability.
    # We will trust the Cap Space number for now, but use Apron text to flag constraints?
    # Actually, simpler: Use Cap Space. If negative, only Exceptions available (MLE/Min).
    
    # 4. Free Agents (Messy header)
    # Skip row 1?? No, row 0 is the messy one.
    fa_df = pd.read_csv(FILE_FA)
    # Rename cols: 
    # Col 0: From, Col 1: Player, Col 5: AAV
    fa_df.columns = ['From', 'Player', 'Pos', 'Yrs', 'Value', 'AAV', 'Status']
    fa_df['AAV_Clean'] = fa_df['AAV'].apply(clean_money)
    
    # 5. Archetype Maps
    off_clus = pd.read_csv(FILE_OFF_CLUSTERS)
    def_clus = pd.read_csv(FILE_DEF_CLUSTERS)
    
    # Map Player Name -> Archetype (Assuming unique names roughly)
    # Using Name to map beacause FA list doesn't have ID.
    off_map = off_clus.set_index('PLAYER_NAME')['Archetype_Name'].to_dict()
    def_map = def_clus.set_index('PLAYER_NAME')['Archetype_Name'].to_dict()
    
    # Add Archetypes to FA DF
    fa_df['OFF_Arch'] = fa_df['Player'].map(off_map).fillna('Unknown')
    fa_df['DEF_Arch'] = fa_df['Player'].map(def_map).fillna('Unknown')
    
    return needs_df, cap_map, fa_df

def determine_contract_type(aav):
    if aav > 35000000: return "Max"
    if aav > 12000000: return "High Value"
    if aav > 5000000: return "Mid-Level"
    return "Minimum/Low"

def recommend_signings(needs_df, cap_map, fa_df):
    print("Generating Recommendations...")
    
    targets = []
    
    # Group needs by Team to avoid duplicates if multiple lineups match
    # Or iterate uniquely?
    # Let's iterate unique (Team, Rec_Add_OFF, Rec_Add_DEF) tuples
    unique_needs = needs_df[['Team', 'Rec_Add_OFF', 'Rec_Add_DEF']].drop_duplicates()
    
    for _, row in unique_needs.iterrows():
        team = row['Team']
        needed_off = row['Rec_Add_OFF']
        needed_def = row['Rec_Add_DEF']
        
        # Budget Check
        space = cap_map.get(team, 0)
        
        # Max affordable offer
        # If space < 0, can only offer Taxpayer MLE (~5.2M) or Min
        if space < 0:
            max_offer = 5200000 
            budget_status = "Over Cap (MLE/Min only)"
        else:
            max_offer = space
            budget_status = f"Cap Space (${space:,.0f})"
            
        # Filter FAs
        # Logic: Must match OFF archetype OR DEF archetype (OR both is bonus)
        # Note: 'needed_off' might be a comma separated string if multiples were recommended?
        # The previous script joined lists with ", ".
        # We need to check if ANY needed archetype matches the FA.
        
        target_off_types = [x.strip() for x in needed_off.split(',')]
        target_def_types = [x.strip() for x in needed_def.split(',')]
        
        candidates = fa_df[
            (fa_df['OFF_Arch'].isin(target_off_types)) | 
            (fa_df['DEF_Arch'].isin(target_def_types))
        ].copy()
        
        # Further Filter by Budget
        # FA AAV must be <= max_offer (approx)
        # Allow some wiggle room? No, let's be strict or users get confused.
        # Exception: Re-signing own players often allows going over cap (Bird Rights).
        
        valid_targets = []
        
        for _, fa in candidates.iterrows():
            is_resign = (fa['From'] == team)
            
            # Bird Rights logic: If re-signing, ignore cap space constraint
            if is_resign:
                allowed = True
                action = "Re-sign (Bird Rights)"
            elif fa['AAV_Clean'] <= max_offer:
                allowed = True
                action = "Sign (Cap Space/MLE)"
            else:
                allowed = False
                
            if allowed:
                # Score/Rank?
                # Points for matching Offense + Points for matching Defense
                score = 0
                match_desc = []
                if fa['OFF_Arch'] in target_off_types: 
                    score += 1
                    match_desc.append("Offensive Fit")
                if fa['DEF_Arch'] in target_def_types: 
                    score += 1
                    match_desc.append("Defensive Fit")
                
                # Bonus for being good (AAV proxy for quality)
                # But irrelevant if they fit the role.
                
                valid_targets.append({
                    'Team': team,
                    'Budget_Status': budget_status,
                    'Player': fa['Player'],
                    'Action': action,
                    'Contract_Value': f"${fa['AAV_Clean']:,.0f}",
                    'Contract_Type': determine_contract_type(fa['AAV_Clean']),
                    'Fit_Reason': ", ".join(match_desc),
                    'Archetypes': f"{fa['OFF_Arch']} / {fa['DEF_Arch']}",
                    'Score': score
                })
        
        # Sort targets for this need
        # Priority: Score (Dual fit) -> Re-signs -> AAV (High quality first)
        targets_df = pd.DataFrame(valid_targets)
        if not targets_df.empty:
            targets_df = targets_df.sort_values(
                by=['Score', 'Action', 'Contract_Type'], 
                ascending=[False, True, False] # Re-sign is alphabetically 'Re' vs 'Si'.. wait. 'Re' < 'Si'. So True puts Re-sign first.
            )
            # Take top 3 recommendations per need to avoid spam
            top_rec = targets_df.head(3)
            targets.extend(top_rec.to_dict('records'))
            
    return pd.DataFrame(targets)

def main():
    needs, caps, fas = load_data()
    results = recommend_signings(needs, caps, fas)
    
    print(f"Saving {len(results)} targets to {OUTPUT_FILE}...")
    results.drop_duplicates(subset=['Team', 'Player']).to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
