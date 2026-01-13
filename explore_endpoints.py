
import nba_api.stats.endpoints as ep

# List all attributes in endpoints to find Synergy or Playtype related classes
print([x for x in dir(ep) if 'Synergy' in x or 'PlayType' in x or 'Year' in x])
