from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
import requests
from .parsers import GamesParser, StandingsParser, PlayersParser

# mostly debugging imports
import time
import json
from django.conf import settings
import os

debugging = False
cache_key_games = "liiga-games"
cache_key_standings = "liiga-standings"
cache_key_players = "liiga-players"

# Create your views here.
def main(request):
  return render(request, "index.html")

def fetchGames(request):
  teamName = request.GET.get("team", None)
  if debugging:
    before = time.time()
  # django recommends to pass json array as a dict
  data = {}
  if cache.get(cache_key_games):
    data["data"] = cache.get(cache_key_games)
    data["method"] = "cache"
  else:
    if debugging:
      response = open(os.path.join(settings.BASE_DIR, "json/games.json"), encoding="utf-8")
      data["data"] = json.load(response)
    else:
      url = "https://liiga.fi/api/v1/games?tournament=runkosarja&season=2024"
      response = requests.get(url)
      data["data"] = response.json()
    data["method"] = "new"
    cache.set(cache_key_games, data["data"], 600) # 10 minutes
  if debugging:
    after = time.time()
    print(f"Fetch took {after - before} seconds")
    print(f"Games fetched with method: {data['method']}")
  data = GamesParser(data, teamName)
  return JsonResponse(data)

def fetchStandings(request):
  # django recommends to pass json array as a dict
  data = {}
  if cache.get(cache_key_standings):
    data["data"] = cache.get(cache_key_standings)
    data["method"] = "cache"
  else:
    if debugging:
      response = open(os.path.join(settings.BASE_DIR, "json/standings.json"), encoding="utf-8")
      data["data"] = json.load(response)
    else:
      url = "https://liiga.fi/api/v1/teams/stats/2024/runkosarja/"
      response = requests.get(url)
      data["data"] = response.json()
    data["method"] = "new"
    cache.set(cache_key_standings, data["data"], 600) # 10 minutes
  if debugging:
    print(f"Standings fetched with method: {data['method']}")
  data = StandingsParser(data)
  return JsonResponse(data)

def fetchPlayers(request):
  sort_by = request.GET.get("sort", "points")
  teamName = request.GET.get("team", None)
  # django recommends to pass json array as a dict
  data = {}
  if cache.get(cache_key_players):
    data["data"] = cache.get(cache_key_players)
    data["method"] = "cache"
  else:
    if debugging:
      response = open(os.path.join(settings.BASE_DIR, "json/players.json"), encoding="utf-8")
      data["data"] = json.load(response)
    else:
      url = "https://liiga.fi/api/v1/players/stats/2023/runkosarja"
      response = requests.get(url)
      data["data"] = response.json()
    data["method"] = "new"
    cache.set(cache_key_players, data["data"], 600) # 10 minutes
  if debugging:
    print(f"Players fetched with method: {data['method']}")
  data = PlayersParser(data, sort_by, teamName)
  return JsonResponse(data)
