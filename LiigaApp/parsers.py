import datetime

dateformat: str = "%Y-%m-%dT%H:%M:%S%z"
# How many games to return at most
max_games: int = 50

def GetLowercaseTeamName(raw_name):
  if raw_name == "Ässät":
    return "assat"
  if raw_name == "Kärpät":
    return "karpat"
  return raw_name.lower()

def PlayersParser(raw_json, sort_by, teamName):
  parsed_json = {}
  parsed_json["method"] = raw_json["method"]
  
  parsed_players = []
  for raw_plr in raw_json["data"]:
    # Filter by team name
    if not teamName == None:
      gameTeam = GetLowercaseTeamName(raw_plr["team"])
        
      if not gameTeam == teamName:
        # Filtered team is not in this game => continue
        continue

    parsed_plr = {}
    parsed_plr["name"] = raw_plr["full_name"]
    parsed_plr["team"] = raw_plr["team"]
    parsed_plr["games_played"] = raw_plr["games"]
    parsed_plr["goals"] = raw_plr["goals"]
    parsed_plr["assists"] = raw_plr["assists"]
    parsed_plr["points"] = raw_plr["points"]
    if parsed_plr["games_played"] > 0:
      parsed_plr["ppg"] = parsed_plr["points"] / parsed_plr["games_played"]
      parsed_plr["ppg"] = "%.2f" % round(parsed_plr["ppg"], 2)
    else:
      parsed_plr["ppg"] = 0.0
    parsed_plr["penalty_minutes"] = raw_plr["penalty_minutes"]
    parsed_plr["plus_minus"] = raw_plr["plus_minus"]
    parsed_plr["position"] = raw_plr["current_position"]
    
    parsed_players.append(parsed_plr)
    
  if sort_by == "points":
    parsed_players.sort(key=lambda plr: (-int(plr["points"]), -int(plr["goals"])))
  elif sort_by == "assists":
    parsed_players.sort(key=lambda plr: (-int(plr["assists"]), -int(plr["points"])))
  elif sort_by == "goals":
    parsed_players.sort(key=lambda plr: (-int(plr["goals"]), -int(plr["points"])))
    
  parsed_players = parsed_players[:15]
  
  parsed_json["data"] = parsed_players
  return parsed_json

def StandingsParser(raw_json):
  parsed_json = {}
  parsed_json["method"] = raw_json["method"]
  
  parsed_teams = []
  for raw_team in raw_json["data"]:
    parsed_team = {}
    parsed_team["games"] = raw_team["games"]
    parsed_team["games_won"] = raw_team["games_won"]
    parsed_team["games_lost"] = raw_team["games_lost"]
    parsed_team["games_tied"] = raw_team["games_tied"]
    parsed_team["ot_ps_won"] = raw_team["ot_ps_won"]
    parsed_team["goals_against"] = raw_team["goals_against"]
    parsed_team["goals_for"] = raw_team["goals_for"]
    parsed_team["points"] = raw_team["points"]
    parsed_team["points_per_game"] = raw_team["points_per_game"]
    parsed_team["powerplay_percentage"] = raw_team["powerplay_percentage"]
    parsed_team["penaltykill_percentage"] = raw_team["penaltykill_percentage"]
    parsed_team["team"] = raw_team["slug"]
    
    parsed_teams.append(parsed_team)
    
  parsed_teams.sort(key=lambda team: (-int(team["points"]), -float(team["points_per_game"])))
    
  parsed_json["data"] = parsed_teams
  return parsed_json

def GamesParser(raw_json, teamName):
  parsed_json = {}
  parsed_json["method"] = raw_json["method"]
  
  now = datetime.datetime.now(datetime.timezone.utc)
  deltaDays = 28 if teamName == None else 56
  afterDay = now - datetime.timedelta(days=deltaDays)
  beforeDay = now + datetime.timedelta(days=deltaDays)
  
  parsed_games = []
  for raw_game in raw_json["data"]:
    formattedGameDate = datetime.datetime.strptime(raw_game["start"], dateformat)
    if not (formattedGameDate > afterDay and formattedGameDate < beforeDay):
      # Only get games 4 weeks older or newer from current date if no team is selected
      # If team is selected get 8 weeks older or newer
      continue
    
    # Filter by team name
    if not teamName == None:
      hasTeam = False
      for i in range(2):
        team_str = "homeTeam" if i == 0 else "awayTeam"
        gameTeam = GetLowercaseTeamName(raw_game[team_str]["teamName"])
        
        if gameTeam == teamName:
          hasTeam = True
          break
      if not hasTeam:
        # Filtered team is not in this game => continue
        continue

    parsed_game = {}
    parsed_game["id"] = raw_game["id"]
    parsed_game["start"] = raw_game["start"]
    parsed_game["end"] = raw_game.get("end", False)
    parsed_game["started"] = raw_game["started"]
    parsed_game["ended"] = raw_game["ended"]
    parsed_game["gameTime"] = raw_game.get("gameTime", 0)
    parsed_game["finishedType"] = raw_game["finishedType"]
    
    parsed_game["dayMonth"] = f"{formattedGameDate.day}.{formattedGameDate.month}"
    
    for i in range(2):
      team_str = "homeTeam" if i == 0 else "awayTeam"
      parsed_game[team_str] = {}
      parsed_game[team_str]["teamId"] = raw_game[team_str]["teamId"]
      parsed_game[team_str]["teamName"] = raw_game[team_str]["teamName"]
      parsed_game[team_str]["goals"] = raw_game[team_str]["goals"]
    
    parsed_games.append(parsed_game)
      
  if len(parsed_games) > max_games:
    while len(parsed_games) > max_games:
      # Remove all games from specific dates
      last_game = parsed_games[-1]
      parsed_games = [x for x in parsed_games if x["dayMonth"] != last_game["dayMonth"]]
      if len(parsed_games) <= max_games:
        break
      first_game = parsed_games[0]
      parsed_games = [x for x in parsed_games if x["dayMonth"] != first_game["dayMonth"]]
      
  
  parsed_json["data"] = parsed_games
  return parsed_json
