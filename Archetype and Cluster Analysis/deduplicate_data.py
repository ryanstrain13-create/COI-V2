
import pandas as pd

INPUT_FILE = 'nba_player_archetypes_2025.csv'

print(f"Reading {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

original_rows = len(df)
df_deduped = df.drop_duplicates(subset=['PLAYER_ID', 'PLAYER_NAME'])
new_rows = len(df_deduped)

print(f"Removed {original_rows - new_rows} duplicate rows.")
print(f"New count: {new_rows}")

df_deduped.to_csv(INPUT_FILE, index=False)
print("Saved deduped file.")
