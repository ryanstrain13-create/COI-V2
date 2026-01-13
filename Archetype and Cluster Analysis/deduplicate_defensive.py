
import pandas as pd

INPUT_FILE = 'nba_defensive_archetypes_2025.csv'

print(f"Reading {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

original_rows = len(df)
# Deduplicate based on PLAYER_ID (should be unique)
df_deduped = df.drop_duplicates(subset=['PLAYER_ID'])
new_rows = len(df_deduped)

print(f"Removed {original_rows - new_rows} duplicate rows.")
print(f"New count: {new_rows}")

# Optional: Inspect if any key columns have all zeros which might imply bad fetch
print("Checking for zero-filled rows in key columns...")
zero_cols = df_deduped[['DEFLECTIONS', 'MATCHUP_DIFFICULTY', 'VERSATILITY_RATING']].eq(0).sum()
print(zero_cols)

df_deduped.to_csv(INPUT_FILE, index=False)
print("Saved deduped file.")
