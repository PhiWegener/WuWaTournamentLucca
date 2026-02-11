import random
from django.db import transaction

from .models import Match, MatchSide, Player, Tournament


@transaction.atomic
def generateSingleElim8(tournament: Tournament, *, shuffleSeed: int | None = None, overwrite: bool = True) -> list[Match]:
    """
    Erzeugt 8er Single Elimination Bracket:
      Round 0: 4 Matches (match_index 1..4)
      Round 1: 2 Matches (match_index 1..2)
      Round 2: 1 Match  (match_index 1)

    Mapping:
      R0 M1 -> R1 M1 LEFT
      R0 M2 -> R1 M1 RIGHT
      R0 M3 -> R1 M2 LEFT
      R0 M4 -> R1 M2 RIGHT
      R1 M1 -> R2 M1 LEFT
      R1 M2 -> R2 M1 RIGHT
    """
    players = list(tournament.players.all().order_by("id"))

    if len(players) != 8:
        raise ValueError(f"Need exactly 8 players, got {len(players)}")

    rng = random.Random(shuffleSeed)
    rng.shuffle(players)

    if overwrite:
        Match.objects.filter(tournament=tournament).delete()

    # Finale
    finalMatch = Match.objects.create(
        tournament=tournament,
        player_left=None,
        player_right=None,
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=2,
        match_index=1,
        next_match=None,
        next_side=None,
    )

    # Runde 1 (Halbfinale)
    semi1 = Match.objects.create(
        tournament=tournament,
        player_left=None,
        player_right=None,
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=1,
        match_index=1,
        next_match=finalMatch,
        next_side=MatchSide.LEFT,
    )
    semi2 = Match.objects.create(
        tournament=tournament,
        player_left=None,
        player_right=None,
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=1,
        match_index=2,
        next_match=finalMatch,
        next_side=MatchSide.RIGHT,
    )

    # Runde 0 (Viertelfinale) – echte Losung
    q1 = Match.objects.create(
        tournament=tournament,
        player_left=players[0],
        player_right=players[1],
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=0,
        match_index=1,
        next_match=semi1,
        next_side=MatchSide.LEFT,
    )
    q2 = Match.objects.create(
        tournament=tournament,
        player_left=players[2],
        player_right=players[3],
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=0,
        match_index=2,
        next_match=semi1,
        next_side=MatchSide.RIGHT,
    )
    q3 = Match.objects.create(
        tournament=tournament,
        player_left=players[4],
        player_right=players[5],
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=0,
        match_index=3,
        next_match=semi2,
        next_side=MatchSide.LEFT,
    )
    q4 = Match.objects.create(
        tournament=tournament,
        player_left=players[6],
        player_right=players[7],
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=0,
        match_index=4,
        next_match=semi2,
        next_side=MatchSide.RIGHT,
    )

    return [q1, q2, q3, q4, semi1, semi2, finalMatch]
