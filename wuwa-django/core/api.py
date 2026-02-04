from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from core.models import Tournament, Match
from core.serializer import MatchDashboardSerializer


class TournamentMatchesAPIView(generics.ListAPIView):
    serializer_class = MatchDashboardSerializer
    permission_classes = [AllowAny]  # fürs öffentliche Dashboard

    def get_queryset(self):
        tournamentId = self.kwargs["tournamentId"]
        get_object_or_404(Tournament, id=tournamentId)

        return (
            Match.objects.filter(tournament_id=tournamentId)
            .select_related("player_left", "player_right", "boss", "winner_player", "tournament")
            .prefetch_related("draft_actions__resonator")
            .order_by("id")
        )
