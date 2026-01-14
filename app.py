import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
from io import StringIO

# --- 1. CONFIGURATION ---
# Fetches key from Streamlit's internal secrets manager
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API Key not found. Please add it to your Streamlit Secrets.")
    st.stop()

model = genai.GenerativeModel("gemini-1.5-pro")

def to_raw(url):
    """Improved version to handle various GitHub URL formats."""
    # Remove any web parameters like ?short_path
    url = url.split('?')[0]
    # Standardize the conversion
    if "github.com" in url and "/blob/" in url:
        return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return url
    
# --- 2. DATA SOURCE DEFINITIONS ---
HISTORICAL_SOURCES = {
    "Hist_Archetypes": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Archetype%20and%20Cluster%20Analysis/Historical%20Player%20Clusters/General/Master_Archetype_CSV.csv",
    "Hist_Stats": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Historical%20Advanced/nba_historical_advanced_stats_1997_2025.csv",
    "Ideal_Lineup": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Archetype%20and%20Cluster%20Analysis/ideal_lineup_compositions.csv",
    "Lineup_Recs": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Archetype%20and%20Cluster%20Analysis/lineup_recommendations.csv",
    "Team_Archetypes_25": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Archetype%20and%20Cluster%20Analysis/nba_team_archetypes_2025.csv",
    "Team_Clusters": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Archetype%20and%20Cluster%20Analysis/nba_team_clusters.csv",
    "Free_Agents_26": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Contract%20Training/NBA%20Free%20Agents%202026%20-%20Sheet1.csv",
    "Ideal_Destinations": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Ideal%20Destination/ideal_destinations.csv",
    "FA_Targets": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Ideal%20Lineup/final_free_agent_targets.csv"
}

LIVING_SOURCES = {
    "Live_Stats_25_26": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Weekly%20Updates/Contract%20Value%20Weekly%20Update/nba_timeseries_stats_2025_26.csv",
    "Live_Contract_Value": "https://github.com/ryanstrain13-create/COI-V2/blob/main/Weekly%20Updates/Contract%20Value%20Weekly%20Update/nba_contract_tracker.csv"
}

# --- 3. DATA LOADING ENGINE ---
@st.cache_data(show_spinner="Loading Historical Databases...")
def load_historical():
    return {name: pd.read_csv(to_raw(url)) for name, url in HISTORICAL_SOURCES.items()}

@st.cache_data(ttl=3600, show_spinner="Fetching Weekly Updates...")
def load_living():
    return {name: pd.read_csv(to_raw(url)) for name, url in LIVING_SOURCES.items()}

hist_dfs = load_historical()
live_dfs = load_living()

# Creation of a global map for Team Abbreviation -> Team ID
team_id_map = live_dfs['Live_Stats_25_26'][['TEAM_ABBREVIATION', 'TEAM_ID']].drop_duplicates().set_index('TEAM_ABBREVIATION')['TEAM_ID'].to_dict()

# --- 4. SIDEBAR FILTERING ---
st.sidebar.title("🔍 Scout Filtering")

all_players = sorted(pd.concat([hist_dfs['Hist_Stats']['PLAYER_NAME'], live_dfs['Live_Stats_25_26']['PLAYER_NAME']]).unique())
selected_player = st.sidebar.selectbox("Select Player to Focus Analysis", ["None"] + all_players)

all_teams = sorted(live_dfs['Live_Stats_25_26']['TEAM_ABBREVIATION'].unique())
selected_team = st.sidebar.selectbox("Select Team to Focus Analysis", ["None"] + all_teams)

if st.sidebar.button("🔄 Clear All Cache & Refresh"):
    st.cache_data.clear()
    st.rerun()

# --- 5. RAG (RETRIEVAL) LOGIC ---
def get_filtered_context(player, team):
    context = "RELEVANT DATA EXTRACTED:\n"
    if player != "None":
        p_live = live_dfs['Live_Stats_25_26'][live_dfs['Live_Stats_25_26']['PLAYER_NAME'] == player]
        p_arch = hist_dfs['Hist_Archetypes'][hist_dfs['Hist_Archetypes']['PLAYER_NAME'] == player]
        p_hist = hist_dfs['Hist_Stats'][hist_dfs['Hist_Stats']['PLAYER_NAME'] == player].tail(3)
        p_contract = live_dfs['Live_Contract_Value'][live_dfs['Live_Contract_Value']['Player'] == player]
        
        context += f"\n--- Player: {player} ---\nStats: {p_live.to_string()}\nContracts: {p_contract.to_string()}\nArchetype: {p_arch.to_string()}\nHistory: {p_hist.to_string()}\n"

    if team != "None":
        tid = team_id_map.get(team)
        t_needs = hist_dfs['Team_Archetypes_25'][hist_dfs['Team_Archetypes_25']['TEAM_ID'] == tid]
        t_lineup = hist_dfs['Lineup_Recs'][hist_dfs['Lineup_Recs']['Team'] == team]
        t_roster = live_dfs['Live_Stats_25_26'][live_dfs['Live_Stats_25_26']['TEAM_ABBREVIATION'] == team]
        
        context += f"\n--- Team: {team} ---\nArchetype Comp: {t_needs.to_string()}\nRecommendations: {t_lineup.to_string()}\nRoster: {t_roster.head(5).to_string()}\n"
    
    return context if player != "None" or team != "None" else "No filters applied."

# --- 6. CHAT INTERFACE ---
st.title("🏀 NBA Archetype & Contract Scout")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if user_input := st.chat_input("Ask a scouting question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    data_context = get_filtered_context(selected_player, selected_team)
    full_prompt = f"System: Use this data context:\n{data_context}\n\nQuery: {user_input}"
    
    with st.chat_message("assistant"):
        response = model.generate_content(full_prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})