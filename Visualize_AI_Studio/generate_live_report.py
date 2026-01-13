
import os
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- Configuration ---
# You must set this env var or replace with your key
API_KEY = os.environ.get("GOOGLE_API_KEY") 
MODEL_NAME = 'gemini-1.5-pro' # or 'gemini-1.5-flash' for speed

# Paths to your live CSVs
BASE_DIR = '..'
DATA_FILES = {
    'Player_Archetypes': 'Archetype Analysis/nba_player_clusters_offensive.csv',
    'Team_Styles': 'Archetype Analysis/nba_team_clusters.csv',
    'Lineup_Needs': 'Archetype Analysis/lineup_recommendations.csv',
    'FA_Targets': 'Archetype Analysis/final_free_agent_targets.csv',
    'Ideal_Destinations': 'Ideal Destination/ideal_destinations.csv'
}

OUTPUT_DIR = 'Weekly_Reports'

def setup_gemini():
    if not API_KEY:
        print("Error: GOOGLE_API_KEY not found. Please export it or set it in the script.")
        return None
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(MODEL_NAME)

def load_data_context():
    context = ""
    for name, relative_path in DATA_FILES.items():
        path = os.path.join(BASE_DIR, relative_path)
        try:
            # Load CSV
            df = pd.read_csv(path)
            # For context, we might not need the WHOLE file if it's huge, 
            # but Gemini 1.5 Pro has 1M-2M token context, so we likely can.
            # Convert to CSV string
            csv_str = df.to_csv(index=False)
            context += f"\n\n--- FILE: {name} ({relative_path}) ---\n{csv_str}"
        except Exception as e:
            print(f"Warning: Could not load {name}: {e}")
    return context

def generate_report(model, data_context):
    print("Generating Analysis from Live Data...")
    
    # The Prompt Logic (Mirrors the Markdown Guide)
    prompt = f"""
    You are an expert NBA Analyst and General Manager Assistant.
    Attached below is the latest LIVE data from our internal tracking systems.
    
    DATA CONTEXT:
    {data_context}
    
    SYSTEM INSTRUCTIONS:
    Analyze this data to produce a "Weekly Strategic Report".
    Markdown format. Use bolding, lists, and clear headers.
    
    REPORT SECTIONS:
    
    1. **League Meta-Game Update:**
       - Analyze `Team_Styles`. What are the dominant playstyles right now? 
       - Which style generally has the best Defense (based on the data)?
       
    2. **Roster Gaps (The "Needs"):**
       - Analyze `Lineup_Needs`. Identify the top 3 most common "missing archetypes" across the league.
       - Highlight one specific team with a critical hole in their best lineup.
       
    3. **Market Opportunities (The "Supply"):**
       - Analyze `Ideal_Destinations` and `FA_Targets`.
       - Identify 3 "match-made-in-heaven" signings (High Fit Score).
       - Highlight a controversial recommendation (e.g. a Star changing teams).
       
    4. **Action Items:**
       - Summarize the top recommendation for the user's favorite team (Default: "Boston Celtics" if mostly 3-Point Heavy, or pick a random contender).
    
    Produce the report now.
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    # 1. Setup
    model = setup_gemini()
    if not model: return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # 2. Load Data
    data_context = load_data_context()
    
    # 3. Generate
    report_content = generate_report(model, data_context)
    
    # 4. Save
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{OUTPUT_DIR}/analysis_report_{date_str}.md"
    
    with open(filename, "w") as f:
        f.write(report_content)
        
    print(f"Report Generated: {filename}")
    print("You can verify this report in AI Studio by copying the prompt + data if debugging is needed.")

if __name__ == "__main__":
    main()
