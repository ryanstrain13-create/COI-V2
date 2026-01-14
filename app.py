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


def generate_with_retry(prompt):
    """Attempts generation with multiple models in case of availability issues."""
    # Priority: 2.0 Flash -> 2.0 Flash Exp -> 2.5 Flash -> Flash Latest (Generic)
    models_to_try = [
        "gemini-2.0-flash", 
        "gemini-2.0-flash-exp", 
        "gemini-2.5-flash", 
        "gemini-flash-latest"
    ]
    errors = []

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")
            continue

    # If all fail, raise the collected errors
    error_msg = "\n".join(errors)
    raise Exception(f"All available models failed.\nDetails:\n{error_msg}")

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

# --- ARCHETYPE DEFINITIONS ---
OFF_ARCHETYPE_LABELS = {
    "Off_Cluster_0": "Low Usage / Rotation Body (Low USG, End of Bench)",
    "Off_Cluster_1": "Low Usage Wing / Connector (Low USG, 3&D Potential)",
    "Off_Cluster_2": "Off-Ball Shooter / Spacer (High 3P%, Off-Screen Action)",
    "Off_Cluster_3": "Versatile Big / Post Scorer (High Post, Rebounding)",
    "Off_Cluster_4": "Combo Guard / Secondary Handler (PnR, Spot Up)",
    "Off_Cluster_5": "Rim Runner / Paint Big (Lob Threat, Screen Setter)",
    "Off_Cluster_6": "High Usage Forward / Star Wing (Isolation, Scoring)",
    "Off_Cluster_7": "Heliocentric Star / Lead Guard (High USG, Playmaking)"
}

DEF_ARCHETYPE_LABELS = {
    "Def_Cluster_0": "Point of Attack Stopper (High On-Ball Defense)",
    "Def_Cluster_1": "Mobile Big / Rebounder (Versatile Big)",
    "Def_Cluster_2": "Wing Defender (Guards SF/SG)",
    "Def_Cluster_3": "High Steals / Disruptor (Passing Lane Gambler)",
    "Def_Cluster_4": "Anchor Big / Rim Protector (High Block Rate)",
    "Def_Cluster_5": "Guard Disruptor (PG Defender)",
    "Def_Cluster_6": "Versatile Forward (Switchable)",
    "Def_Cluster_7": "High Difficulty / Versatile (Elite Wing Defense)"
}

# --- 4. SIDEBAR FILTERING ---
st.sidebar.title("🔍 Scout Filtering")

all_players = sorted(pd.concat([hist_dfs['Hist_Stats']['PLAYER_NAME'], live_dfs['Live_Stats_25_26']['PLAYER_NAME']]).unique())
selected_player = st.sidebar.selectbox("Select Player to Focus Analysis", ["None"] + all_players)

all_teams = sorted(live_dfs['Live_Stats_25_26']['TEAM_ABBREVIATION'].unique())
selected_team = st.sidebar.selectbox("Select Team to Focus Analysis", ["None"] + all_teams)

st.sidebar.markdown("---")
generate_report = st.sidebar.button("📄 Generate Scouting Report")

if st.sidebar.button("🔄 Clear All Cache & Refresh"):
    st.cache_data.clear()
    st.rerun()

# --- DEBUG: API CHECKER ---
with st.sidebar.expander("🛠️ API Debugger", expanded=False):
    st.write(f"Lib Version: {genai.__version__}")
    if st.button("List Available Models"):
        try:
            st.write("Fetching models...")
            models = list(genai.list_models())
            found_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            st.success(f"Found {len(found_models)} models")
            st.code("\n".join(found_models))
        except Exception as e:
            st.error(f"List Error: {e}")

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
        
        context += f"\n--- Team: {team} ---\nArchetype Needs: {t_needs.to_string()}\nRecommendations: {t_lineup.to_string()}\nRoster Preview: {t_roster.head(5).to_string()}\n"
    
    return context if player != "None" or team != "None" else "No filters applied."

# --- 6. MAIN CHAT INTERFACE ---
st.title("🏀 NBA Archetype & Contract Scout")

tab_chat, tab_defs = st.tabs(["💬 Chat & Analysis", "📖 Archetype Definitions"])

with tab_defs:
    st.header("Player Archetype Definitions")
    st.markdown("These definitions map the algorithmic clusters to basketball playstyles.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏀 Offensive Archetypes")
        for k, v in OFF_ARCHETYPE_LABELS.items():
            st.markdown(f"**{k}**: {v}")
            
    with col2:
        st.subheader("🛡️ Defensive Archetypes")
        for k, v in DEF_ARCHETYPE_LABELS.items():
            st.markdown(f"**{k}**: {v}")

with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # Handle Report Generation
    if generate_report:
        if selected_player == "None" and selected_team == "None":
            st.error("⚠️ Please select a Player or Team from the sidebar to generate a report.")
        else:
            data_context = get_filtered_context(selected_player, selected_team)
            
            # Inject Definitions into Context
            def_context = "\nARCHETYPE DEFINITIONS REFERENCE:\n"
            for k,v in OFF_ARCHETYPE_LABELS.items(): def_context += f"{k}: {v}\n"
            for k,v in DEF_ARCHETYPE_LABELS.items(): def_context += f"{k}: {v}\n"
            
            full_prompt = f"""
            You are an expert NBA Scout. Generate a detailed, professional scouting report based on the selected data.
            
            TASK:
            Create a structured report for the selected Player/Team.
            - If Player: Analyze Playstyle (Archetype), Advanced Stats, Contract Value, and Historic Progression.
            - If Team: Analyze Roster Construction, Needs, and Recommended Targets.
            
            Use these definitions to interpret the Archetype Clusters:
            {def_context}
            
            DATA CONTEXT:
            {data_context}
            
            Format nicely with Markdown headers, bullet points, and a final 'Verdict'.
            """
            
            st.session_state.messages.append({"role": "user", "content": "Generate Detailed Scouting Report"})
            with st.chat_message("user"): st.markdown("Generate Detailed Scouting Report")
            
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Compiling scouting report..."):
                        response = generate_with_retry(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Report Generation Failed: {e}")

    # Handle Chat Input
    if user_input := st.chat_input("Ask a scouting question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        data_context = get_filtered_context(selected_player, selected_team)
        
        # Inject brief definitions context
        def_context_short = "OFF: " + str(OFF_ARCHETYPE_LABELS) + "\nDEF: " + str(DEF_ARCHETYPE_LABELS)
        
        full_prompt = f"System: You are an NBA Analyst. Use this data:\n{data_context}\n\nDefinitions:\n{def_context_short}\n\nUser Query: {user_input}"
        
        with st.chat_message("assistant"):
            try:
                with st.spinner("Analyzing data..."):
                    response = generate_with_retry(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")