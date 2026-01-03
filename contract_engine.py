import time
import random
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.library.http import NBAStatsHTTP
from requests.exceptions import ReadTimeout, ConnectionError

# 1. SET GLOBAL CONFIGURATION
# Increase timeout to 60 seconds (default is 30)
NBAStatsHTTP.nba_response_timeout = 60

# 2. DEFINE ROBUST HEADERS
# This mimics a standard browser to avoid being flagged by Akamai/NBA security
CUSTOM_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'Connection': 'keep-alive',
}

def fetch_nba_data_with_retry(endpoint_call, max_retries=5):
    """
    Wrapper to handle timeouts and rate limits with exponential backoff.
    """
    for i in range(max_retries):
        try:
            # Add a small random delay before the request to avoid spamming
            time.sleep(random.uniform(1.5, 3.5))
            
            # Execute the endpoint call
            data = endpoint_call.get_data_frames()[0]
            return data
            
        except (ReadTimeout, ConnectionError) as e:
            wait_time = (2 ** i) + random.random() # Exponential backoff: 2s, 4s, 8s...
            print(f"Attempt {i+1} failed: {e}. Retrying in {wait_time:.2f} seconds...")
            if i == max_retries - 1:
                raise e
            time.sleep(wait_time)

# 3. UPDATED RUN SNAPSHOT FUNCTION
def run_snapshot(lasso_model, data_scaler):
    print("Fetching live NBA player stats...")
    
    # Define the endpoint object
    # Use headers=CUSTOM_HEADERS to ensure the request is accepted
    stats_call = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2025-26', 
        per_mode_detailed='Totals',
        headers=CUSTOM_HEADERS
    )
    
    # Use our new retry wrapper to get the data
    live_trad = fetch_nba_data_with_retry(stats_call)
    
    # ... rest of your processing logic (lasso_model, scaler
