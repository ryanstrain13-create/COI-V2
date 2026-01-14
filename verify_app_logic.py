import pandas as pd
import os

# Define Local Paths
BASE_DIR = "/Users/ryanstrain/Desktop/COI V2"
PATHS = {
    "Hist_Stats": os.path.join(BASE_DIR, "Historical Advanced/nba_historical_advanced_stats_1997_2025.csv"),
    "Live_Stats_25_26": os.path.join(BASE_DIR, "Weekly Updates/Contract Value Weekly Update/nba_timeseries_stats_2025_26.csv"),
    "Hist_Archetypes": os.path.join(BASE_DIR, "Archetype and Cluster Analysis/Historical Player Clusters/General/Master_Archetype_CSV.csv"),
    "Live_Contract_Value": os.path.join(BASE_DIR, "Weekly Updates/Contract Value Weekly Update/nba_contract_tracker.csv"),
    "Team_Archetypes_25": os.path.join(BASE_DIR, "Archetype and Cluster Analysis/nba_team_archetypes_2025.csv"),
    "Lineup_Recs": os.path.join(BASE_DIR, "Archetype and Cluster Analysis/lineup_recommendations.csv")
}

def load_data():
    dfs = {}
    print("Loading Data...")
    for key, path in PATHS.items():
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path)
            print(f"✅ Loaded {key}")
        else:
            print(f"❌ Missing {path}")
    return dfs

def test_logic():
    dfs = load_data()
    
    # Simulate app.py logic
    try:
        # 1. Team ID Map
        team_id_map = dfs['Live_Stats_25_26'][['TEAM_ABBREVIATION', 'TEAM_ID']].drop_duplicates().set_index('TEAM_ABBREVIATION')['TEAM_ID'].to_dict()
        print("✅ Team ID Map created")

        # 2. All Players (Line 59)
        all_players = sorted(pd.concat([dfs['Hist_Stats']['PLAYER_NAME'], dfs['Live_Stats_25_26']['PLAYER_NAME']]).unique())
        print(f"✅ Player list generated ({len(all_players)} players)")

        # 3. All Teams (Line 62)
        all_teams = sorted(dfs['Live_Stats_25_26']['TEAM_ABBREVIATION'].dropna().unique())
        print(f"✅ Team list generated ({len(all_teams)} teams)")

        # 4. Filter Context Logic
        player = all_players[0]
        team = all_teams[0] # e.g. 'ATL'
        
        print(f"Testing filter for Player: {player}, Team: {team}")

        # Player Ops
        p_live = dfs['Live_Stats_25_26'][dfs['Live_Stats_25_26']['PLAYER_NAME'] == player]
        p_arch = dfs['Hist_Archetypes'][dfs['Hist_Archetypes']['PLAYER_NAME'] == player] # Potential error here if header wrong
        p_hist = dfs['Hist_Stats'][dfs['Hist_Stats']['PLAYER_NAME'] == player]
        p_contract = dfs['Live_Contract_Value'][dfs['Live_Contract_Value']['Player'] == player] # 'Player' key check
        print("✅ Player filtering success")

        # Team Ops
        tid = team_id_map.get(team)
        t_needs = dfs['Team_Archetypes_25'][dfs['Team_Archetypes_25']['TEAM_ID'] == tid]
        t_lineup = dfs['Lineup_Recs'][dfs['Lineup_Recs']['Team'] == team]
        t_roster = dfs['Live_Stats_25_26'][dfs['Live_Stats_25_26']['TEAM_ABBREVIATION'] == team]
        print("✅ Team filtering success")

    except KeyError as e:
        print(f"❌ KEY ERROR: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_logic()
