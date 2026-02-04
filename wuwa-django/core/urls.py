from django.urls import path
from . import views

from django.urls import path
from core.api import TournamentMatchesAPIView

urlpatterns = [
    path("", views.home, name="home"),

    # Auth
    path("login/", views.userLogin, name="login"),
    path("logout/", views.userLogout, name="logout"),

    # Player portal
    path("player/", views.playerDashboard, name="playerDashboard"),
    path("player/submit-time/", views.playerSubmitTime, name="playerSubmitTime"),

    path("host/", views.hostTournamentList, name="hostTournamentList"),
    path("host/tournament/<int:tournamentId>/", views.hostTournamentDetail, name="hostTournamentDetail"),

    # path("host/match/<int:matchId>/", views.hostMatchDetail, name="hostMatchDetail"),
    path("host/match/<int:matchId>/start/", views.hostMatchStart, name="hostMatchStart"),
    path("host/match/<int:matchId>/finish/", views.hostMatchFinish, name="hostMatchFinish"),
    path("host/match/<int:matchId>/set-winner/", views.hostSetWinner, name="hostSetWinner"),

    path("match/<int:matchId>/", views.matchDetail, name="matchDetail"),
    path("match/<int:matchId>/confirm-bans/", views.matchConfirmBans, name="matchConfirmBans"),
    path("match/<int:matchId>/confirm-picks/", views.matchConfirmPicks, name="matchConfirmPicks"),
    path("match/<int:matchId>/draft-reset/", views.matchDraftReset, name="matchDraftReset"),
    path("match/<int:matchId>/submit-time/", views.matchSubmitTime, name="matchSubmitTime"),



    # Leaderboards
    path("leaderboards/", views.leaderboards, name="leaderboards"),
]

urlpatterns += [
    path("api/tournaments/<int:tournamentId>/matches/", TournamentMatchesAPIView.as_view(), name="api_tournament_matches"),
]
