import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
from io import StringIO

# 1. Fetch data from your GitHub Raw URL
@st.cache_data(ttl=3600) # Caches data for 1 hour to save performance
def load_github_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error("Could not fetch latest data from GitHub.")
        return None

# URLs to your living CSVs
Historical_STATS_URL = "https://github.com/ryanstrain13-create/COI-V2/blob/main/Historical%20Advanced/nba_historical_advanced_stats_1997_2025.csv"
ARCHETYPE_URL = "https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/data/Player_Archetypes.csv"

# 2. Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro")

# 3. Streamlit UI
st.title("🏀 NBA Live Scout & Analytics")

stats_df = load_github_csv(STATS_URL)
archetype_df = load_github_csv(ARCHETYPE_URL)

# Display a preview of the living data
with st.expander("View Live Data Sources"):
    st.write("Latest Player Stats:", stats_df.head())

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about a player's latest scouting report..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Construct the context with the fresh CSV data
    context = f"Here is the latest data:\nStats: {stats_df.to_string()}\nArchetypes: {archetype_df.to_string()}"
    full_prompt = f"{context}\n\nUser Question: {prompt}\nAnalyze this in the style of a lead scout."
    
    response = model.generate_content(full_prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})