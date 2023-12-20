from django.urls import path
from . import views

urlpatterns = [
  path("", views.main, name="main"),
  path("fetchGames/", views.fetchGames, name="fetchGames"),
  path("fetchStandings/", views.fetchStandings, name="fetchStandings"),
  path("fetchPlayers/", views.fetchPlayers, name="fetchPlayers"),
]
