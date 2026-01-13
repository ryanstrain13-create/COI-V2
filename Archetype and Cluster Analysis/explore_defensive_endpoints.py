
import nba_api.stats.endpoints as ep

# List all attributes in endpoints to find Hustle, Defense, Matchup related classes
keywords = ['Hustle', 'Defense', 'Matchup', 'Defend']
matches = [x for x in dir(ep) if any(k in x for k in keywords)]
print(matches)
