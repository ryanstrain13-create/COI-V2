
# Google AI Studio Visualization Guide

This guide provides instructions for visualizing the NBA Archetype Analysis. It covers two methods:
1.  **Manual Prototyping:** Using the AI Studio Web UI for interactive exploration.
2.  **Automated Recurrence:** Using the Python SDK (Gemini API) for live, scheduled reporting.

---

## Part 1: Manual Prototyping (Web UI)
Use this method for ad-hoc analysis and generating charts on the fly.

### 1. Setup
1.  **Access:** Go to [Google AI Studio](https://aistudio.google.com/).
2.  **New Prompt:** Select "Create new" -> "Chat Prompt".
3.  **Upload Data:** Upload the CSV files from `Archetype Analysis/` and `Ideal Destination/`.

### 2. Visualization Prompts
Copy and paste these prompts into the AI Studio chat to generate specific insights.

**Phase 1: Player Landscape**
> "Create a Scatter Plot using `USG_PCT` (x-axis) vs `TS_PCT` (y-axis). Color points by `Archetype_Name`. Which archetypes are the most efficient?"

**Phase 2: Team Styles**
> "Create a Box Plot showing the distribution of `DEF_RATING` for each `Playstyle_Name`. Create a correlation heatmap of the team features."

**Phase 3: GM Dashboard**
> "Filter `lineup_recommendations.csv` for the 'Boston Celtics'. Display a clean table of their top 4-man lineups and the specific 'Rec_Add_OFF' suggested."

**Phase 4: Free Agent Market**
> "Create a Scatter Plot of Free Agents from `ideal_destinations.csv`: X-Axis = `Fit_Score`, Y-Axis = `Value` (AAV). Highlight targets in the top-right quadrant."

---

## Part 2: Automated Recurrence (Live Updates)
Use this method to run the analysis automatically as new data comes in (e.g., daily/weekly).

### Why use the API?
The AI Studio Web UI does not automatically sync with local files. To achieve "Live Updates", we use the **Gemini API** to programmatically feed the latest CSVs to the model.

### 1. Prerequisites
1.  **Get an API Key:**
    -   Go to [Google AI Studio](https://aistudio.google.com/).
    -   Click "Get API Key" -> "Create API Key in new project".
    -   Copy the key string.

2.  **Install Python SDK:**
    ```bash
    pip install google-generativeai pandas
    ```

3.  **Set Environment Variable:**
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    ```

### 2. Running the Live Report
We have created a script that bundles your project's latest CSVs and sends them to Gemini for analysis.

**Script Location:** `Visualize_AI_Studio/generate_live_report.py`

**How to Run:**
```bash
cd "Visualize_AI_Studio"
python3 generate_live_report.py
```

**What it does:**
1.  Loads the latest CSVs from `Archetype Analysis/` and `Ideal Destination/`.
2.  Constructs a prompt context with all ~3,000+ rows of data (leveraging the 1M+ token context window).
3.  Asks Gemini to produce a **"Weekly Strategic Report"** identifying current meta-trends, specific team holes, and market opportunities.
4.  Saves the output to `Weekly_Reports/analysis_report_YYYY-MM-DD.md`.

### 3. Scheduling (Optional)
To run this completely hands-free:
-   **Local:** Add the python command to your `crontab`.
-   **GitHub Actions:** Create a workflow (`.github/workflows/daily_report.yml`) that:
    1.  Checks out the code.
    2.  Installs dependencies.
    3.  Runs `python generate_live_report.py`.
    4.  Commits the new report back to the repo.
