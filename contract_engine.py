import time
import random
from nba_api.stats.endpoints import leaguedashplayerstats
from requests.exceptions import ReadTimeout, ConnectionError

# 1. DEFINE ROBUST HEADERS
# This mimics a standard browser to avoid being flagged by NBA security
CUSTOM_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'Connection': 'keep-alive',
}

def fetch_nba_data_with_retry(max_retries=5):
    """
    Fetches data with manual retries and custom headers.
    """
    for i in range(max_retries):
        try:
            # Add a small random delay to avoid rate limiting
            time.sleep(random.uniform(2.0, 4.0))
            
            # Call the endpoint with a long timeout (60s) and custom headers
            # Note: we pass headers directly into the endpoint initialization
            stats_call = leaguedashplayerstats.LeagueDashPlayerStats(
                season='2025-26', 
                per_mode_detailed='Totals',
                headers=CUSTOM_HEADERS,
                timeout=60
            )
            
            return stats_call.get_data_frames()[0]
            
        except (ReadTimeout, ConnectionError, Exception) as e:
            wait_time = (2 ** i) + random.random()
            print(f"Attempt {i+1} failed: {e}. Retrying in {wait_time:.2f} seconds...")
            if i == max_retries - 1:
                raise e
            time.sleep(wait_time)

def run_snapshot(lasso_model, data_scaler):
    print("Fetching live NBA player stats...")
    
    try:
        live_trad = fetch_nba_data_with_retry()
        print(f"Successfully fetched {len(live_trad)} player rows.")
        
        # ... your processing logic here ...
        
    except Exception as e:
        print(f"Failed to fetch data after retries: {e}")
        raise

if __name__ == "__main__":
    # Assuming model/scaler are loaded; if not, wrap in try/except
    run_snapshot(None, None)
