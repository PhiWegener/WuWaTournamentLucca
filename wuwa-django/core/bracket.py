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
    players = list(Player.objects.all().order_by("id"))

    if len(players) != 8:
        raise ValueError(f"Need exactly 8 players, got {len(players)}")

    rng = random.Random(shuffleSeed)
    rng.shuffle(players)

    if overwrite:
        Match.objects.filter(tournament=tournament).delete()

    # Runde 2 (Finale) zuerst erstellen, damit FK next_match direkt gesetzt werden kann
    finalMatch = Match.objects.create(
        tournament=tournament,
        player_left=players[0],   # placeholder, wird überschrieben
        player_right=players[1],  # placeholder, wird überschrieben
        boss=None,
        first_pick_side=MatchSide.LEFT,
        winner_player=None,
        round_index=2,
        match_index=1,
        next_match=None,
        next_side=None,
    )
    # Platzhalter-Spieler entfernen: wir wollen null, aber dein Model hat player_left/right required.
    # Deshalb setzen wir später korrekt und lassen bis dahin Platzhalter drin.
    # (Alternative: player_left/right nullable machen – aktuell nicht.)
    # Wir überschreiben die beiden jetzt sofort mit echten Halbfinal-Winnern, sobald HF erstellt sind.

    # Runde 1 (Halbfinale)
    semi1 = Match.objects.create(
        tournament=tournament,
        player_left=players[0],   # placeholder
        player_right=players[1],  # placeholder
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
        player_left=players[2],   # placeholder
        player_right=players[3],  # placeholder
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

    # Halbfinal/Finale: player_left/right sollen sinnvoll initial sein.
    # Du hast player_left/right NOT NULL => wir lassen sie erstmal als Platzhalter,
    # aber setzen sie "leer" im UI, indem du z.B. im Template "TBD" renderst, sobald round_index>0.
    # Alternativ: player_left/right nullable machen (sauberer). Für jetzt: lassen wir placeholders.

    return [q1, q2, q3, q4, semi1, semi2, finalMatch]
