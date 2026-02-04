from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.db import transaction

from .models import Tournament, Match, BossTime, Boss, Player, UserRole, MatchSide, MatchDraftAction, Resonator, DraftActionType
from .forms import HostMatchCreateForm, HostMatchWinnerForm, PlayerTimeSubmitForm, DraftActionForm, MatchTimeSubmitForm, BanConfirmForm, PickConfirmForm
from .permissions import requireRole, requireLogin


def home(request):
    return render(request, "core/home.html")


def userLogin(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Routing nach Rolle:
            if user.role in (UserRole.ADMIN, UserRole.COMMENTATOR):
                return redirect("hostTournamentList")
            return redirect("playerDashboard")
        return render(request, "core/login.html", {"error": "Invalid credentials"})
    return render(request, "core/login.html")


def userLogout(request):
    logout(request)
    return redirect("login")


@requireRole(UserRole.PLAYER)
def playerDashboard(request):
    if request.user.player is None:
        return render(request, "core/player_dashboard.html", {"error": "No player assigned to your account."})

    player = request.user.player

    matches = (
        Match.objects
        .select_related("player_left", "player_right", "boss", "tournament", "winner_player")
        .filter(Q(player_left=player) | Q(player_right=player))
        .order_by("-id")
    )

    return render(request, "core/player_dashboard.html", {
        "player": player,
        "matches": matches,
    })



@requireRole(UserRole.PLAYER)
def playerSubmitTime(request):
    """
    Spieler trägt Zeit ein:
    - wenn besser als bestehend -> überschreiben
    """
    if request.user.player is None:
        return render(request, "core/player_dashboard.html", {"error": "No player assigned to your account."})

    if request.method != "POST":
        return redirect("playerDashboard")

    form = PlayerTimeSubmitForm(request.POST)
    if not form.is_valid():
        return redirect("playerDashboard")

    player = request.user.player
    boss = form.cleaned_data["boss"]
    timeSeconds = form.cleaned_data["timeSeconds"]

    bossTime, created = BossTime.objects.get_or_create(
        player=player,
        boss=boss,
        defaults={"best_time_seconds": timeSeconds},
    )

    if not created and timeSeconds < bossTime.best_time_seconds:
        bossTime.best_time_seconds = timeSeconds
        bossTime.save()

    return redirect("playerDashboard")

@requireRole(UserRole.ADMIN, UserRole.COMMENTATOR)
def hostTournamentList(request):
    """
    Turnierliste
    """
    tournaments = Tournament.objects.all().order_by("-id")
    return render(request, "core/host_tournament_list.html", {
        "tournaments": tournaments
    })


@requireRole(UserRole.ADMIN, UserRole.COMMENTATOR)
def hostTournamentDetail(request, tournamentId: int):
    """
    Host-Turnier-Übersicht:
    """
    tournament = get_object_or_404(Tournament, id=tournamentId)

    matches = (
        Match.objects
        .select_related("player_left", "player_right", "boss", "winner_player")
        .filter(tournament=tournament)
        .order_by("-id")
    )

    if request.method == "POST":
        form = HostMatchCreateForm(request.POST)
        if form.is_valid():
            playerLeft = form.cleaned_data["playerLeft"]
            playerRight = form.cleaned_data["playerRight"]
            boss = form.cleaned_data["boss"]
            firstPickSide = form.cleaned_data["firstPickSide"]

            if playerLeft.id == playerRight.id:
                return render(request, "core/host_tournament_detail.html",  {
                    "tournament": tournament,
                    "matches": matches,
                    "form": form,
                    "error": "Left and right Player must be different."
                })
            
            Match.objects.create(
                tournament = tournament,
                player_left = playerLeft,
                player_right = playerRight,
                boss = boss,
                first_pick_side = firstPickSide,
            )
            return redirect("hostTournamentDetail", tournamentId=tournament.id)
    else:
        form = HostMatchCreateForm()

    return render(request, "core/host_tournament_detail.html", {
        "tournament": tournament,
        "matches": matches,
        "form": form,
    })


# @requireRole(UserRole.ADMIN, UserRole.COMMENTATOR)
# def hostMatchDetail(request, matchId: int):
#     match = get_object_or_404(
#         Match.objects.select_related("player_left", "player_right", "boss", "winner_player", "tournament"),
#         id=matchId,
#     )
#     form = HostMatchWinnerForm(initial={
#         "winner": match.winner_player_id or None,
#         "leftTimeSeconds": match.left_time_seconds or "",
#         "rightTimeSeconds": match.right_time_seconds or "",
#     })
#     return render(request, "core/host_match_detail.html", {"match": match, "form": form})


@requireRole(UserRole.ADMIN, UserRole.COMMENTATOR)
def hostSetWinner(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)
    form = HostMatchWinnerForm(request.POST, match=match)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    winner = form.cleaned_data["winner"]
    match.winner_player = winner
    match.left_time_seconds = form.cleaned_data.get("leftTimeSeconds")
    match.right_time_seconds = form.cleaned_data.get("rightTimeSeconds")
    match.save()

    return redirect("matchDetail", matchId=matchId)

@requireRole(UserRole.ADMIN, UserRole.COMMENTATOR)
def hostMatchStart(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)

    if match.started_at is None:
        match.started_at = timezone.now()
        match.finished_at = None
        match.save()

    return redirect("matchDetail", matchId=matchId)

@requireRole(UserRole.ADMIN, UserRole.COMMENTATOR)
def hostMatchFinish(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)

    # nur beenden, wenn gestartet und nicht beendet
    if match.started_at is not None and match.finished_at is None:
        match.finished_at = timezone.now()
        match.save()

    return redirect("matchDetail", matchId=matchId)


@requireRole(UserRole.ADMIN, UserRole.COMMENTATOR)
def hostSetWinner(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)
    form = HostMatchWinnerForm(request.POST)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    winnerPlayerId = form.cleaned_data["winnerPlayerId"]
    leftTimeSeconds = form.cleaned_data.get("leftTimeSeconds")
    rightTimeSeconds = form.cleaned_data.get("rightTimeSeconds")

    if winnerPlayerId not in (match.player_left_id, match.player_right_id):
        return redirect("matchDetail", matchId=matchId)

    match.winner_player_id = winnerPlayerId
    match.left_time_seconds = leftTimeSeconds
    match.right_time_seconds = rightTimeSeconds
    match.save()

    return redirect("matchDetail", matchId=matchId)

def leaderboards(request):
    """
    Öffentliche Leaderboards (Top5 pro Boss).
    """
    bosses = Boss.objects.all().order_by("name")
    bossLeaderboards = []
    for boss in bosses:
        top5 = (
            BossTime.objects
            .select_related("player")
            .filter(boss=boss)
            .order_by("best_time_seconds")[:5]
        )
        bossLeaderboards.append((boss, top5))

    return render(request, "core/leaderboards.html", {
        "bossLeaderboards": bossLeaderboards,
    })

def _getUserMatchSide(user, match) -> str | None:
    if not user.is_authenticated or user.player is None:
        return None
    if user.player_id == match.player_left_id:
        return MatchSide.LEFT
    if user.player_id == match.player_right_id:
        return MatchSide.RIGHT
    return None

def matchDetail(request, matchId: int):
    match = get_object_or_404(
        Match.objects.select_related("player_left", "player_right", "boss", "tournament", "winner_player"),
        id=matchId,
    )

    isHost = request.user.is_authenticated and request.user.role in (UserRole.ADMIN, UserRole.COMMENTATOR)
    userSide = _getUserSide(request.user, match)
    isPlayerInMatch = userSide is not None

    if not (isHost or isPlayerInMatch):
        return HttpResponseForbidden("Forbidden")

    actions = MatchDraftAction.objects.select_related("resonator").filter(match=match).order_by("step_index")

    banPhaseDone = match.left_bans_confirmed and match.right_bans_confirmed
    pickPhaseDone = match.left_picks_confirmed and match.right_picks_confirmed

    banForm = None
    pickForm = None

    myPicks = MatchDraftAction.objects.filter(match=match, action_type=DraftActionType.PICK, acting_side=userSide).select_related("resonator")
    oppSide = MatchSide.RIGHT if userSide == MatchSide.LEFT else MatchSide.LEFT
    oppPicks = MatchDraftAction.objects.filter(match=match, action_type=DraftActionType.PICK, acting_side=oppSide).select_related("resonator")

    bansAgainstMe = MatchDraftAction.objects.filter(match=match, action_type=DraftActionType.BAN, target_side=userSide).select_related("resonator")
    bansAgainstOpp = MatchDraftAction.objects.filter(match=match, action_type=DraftActionType.BAN, target_side=oppSide).select_related("resonator")

    if isPlayerInMatch:
        if not banPhaseDone:
            # Spieler darf bannen, wenn er noch nicht confirmed hat
            alreadyConfirmed = match.left_bans_confirmed if userSide == MatchSide.LEFT else match.right_bans_confirmed
            if not alreadyConfirmed:
                banForm = BanConfirmForm(available=Resonator.objects.filter(is_enabled=True))
        else:
            alreadyConfirmed = match.left_picks_confirmed if userSide == MatchSide.LEFT else match.right_picks_confirmed
            if not alreadyConfirmed and not pickPhaseDone:
                pickForm = PickConfirmForm(available=getPickAvailableForSide(match, userSide))

    timeForm = MatchTimeSubmitForm()  # wie du es schon hast


    bansLeftToRight = (
        MatchDraftAction.objects
        .select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=MatchSide.LEFT,
            target_side=MatchSide.RIGHT,
        )
        .order_by("step_index")
    )

    bansRightToLeft = (
        MatchDraftAction.objects
        .select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=MatchSide.RIGHT,
            target_side=MatchSide.LEFT,
        )
        .order_by("step_index")
    )

    picksLeft = (
        MatchDraftAction.objects
        .select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.LEFT,
            target_side=MatchSide.LEFT,
        )
        .order_by("step_index")
    )

    picksRight = (
        MatchDraftAction.objects
        .select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.RIGHT,
            target_side=MatchSide.RIGHT,
        )
        .order_by("step_index")
    )

    return render(request, "core/match_detail.html", {
        "match": match,
        "isHost": isHost,
        "userSide": userSide,
        "actions": actions,
        "banPhaseDone": banPhaseDone,
        "pickPhaseDone": pickPhaseDone,
        "banForm": banForm,
        "pickForm": pickForm,
        "timeForm": timeForm,
        "bansLeftToRight": bansLeftToRight,
        "bansRightToLeft": bansRightToLeft,
        "picksLeft": picksLeft,
        "picksRight": picksRight,
    })


@requireLogin
def matchDraftAction(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)

    isHost = request.user.role in (UserRole.ADMIN, UserRole.COMMENTATOR)
    userSide = _getUserMatchSide(request.user, match)
    isPlayerInMatch = userSide is not None

    if not (isHost or isPlayerInMatch):
        return HttpResponseForbidden("Forbidden")

    actions = MatchDraftAction.objects.filter(match=match).order_by("step_index")
    usedResonators = set(a.resonator_id for a in actions)
    availableResonators = Resonator.objects.filter(is_enabled=True).exclude(id__in=usedResonators)

    form = DraftActionForm(request.POST, availableResonators=availableResonators)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    actionType = form.cleaned_data["actionType"]
    actingSide = form.cleaned_data["actingSide"]
    resonator = form.cleaned_data["resonator"]

    # Spieler dürfen nur für ihre Seite handeln
    if not isHost and actingSide != userSide:
        return HttpResponseForbidden("Forbidden")

    # Step Index automatisch fortlaufend
    nextStepIndex = actions.count() + 1

    MatchDraftAction.objects.create(
        match=match,
        step_index=nextStepIndex,
        action_type=actionType,
        acting_side=actingSide,
        resonator=resonator,
    )

    return redirect("matchDetail", matchId=matchId)

@requireRole(UserRole.PLAYER)
def matchSubmitTime(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)

    # Muss im Match sein
    userSide = _getUserMatchSide(request.user, match)
    if userSide is None:
        return HttpResponseForbidden("Forbidden")

    if match.boss is None:
        return redirect("matchDetail", matchId=matchId)

    form = MatchTimeSubmitForm(request.POST)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    timeSeconds = form.cleaned_data["timeSeconds"]
    player = request.user.player
    boss = match.boss

    bossTime, created = BossTime.objects.get_or_create(
        player=player,
        boss=boss,
        defaults={"best_time_seconds": timeSeconds},
    )

    if not created and timeSeconds < bossTime.best_time_seconds:
        bossTime.best_time_seconds = timeSeconds
        bossTime.save()

    # Optional: Match-spezifische Zeit setzen
    if userSide == MatchSide.LEFT:
        match.left_time_seconds = timeSeconds
    else:
        match.right_time_seconds = timeSeconds
    match.save()

    return redirect("matchDetail", matchId=matchId)

def getConfirmedBans(match, actingSide: str):
    return MatchDraftAction.objects.filter(
        match=match,
        action_type=DraftActionType.BAN,
        acting_side=actingSide,
    ).values_list("resonator_id", flat=True)

def getBansAgainstSide(match, targetSide: str):
    return MatchDraftAction.objects.filter(
        match=match,
        action_type=DraftActionType.BAN,
        target_side=targetSide,
    ).values_list("resonator_id", flat=True)

def getAllPicked(match):
    return MatchDraftAction.objects.filter(
        match=match,
        action_type=DraftActionType.PICK,
    ).values_list("resonator_id", flat=True)

def getPickAvailableForSide(match, side: str):
    bannedAgainstMe = set(getBansAgainstSide(match, side))

    return (
        Resonator.objects
        .filter(is_enabled=True)
        .exclude(id__in=bannedAgainstMe)
    )

def _getUserSide(user, match):
    if not user.is_authenticated or user.player is None:
        return None
    if user.player_id == match.player_left_id:
        return MatchSide.LEFT
    if user.player_id == match.player_right_id:
        return MatchSide.RIGHT
    return None


@transaction.atomic
def matchConfirmBans(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)
    userSide = _getUserSide(request.user, match)
    if userSide is None:
        return HttpResponseForbidden("Forbidden")

    # Nur in BAN-Phase erlauben
    if match.left_bans_confirmed and match.right_bans_confirmed:
        return redirect("matchDetail", matchId=matchId)

    # Schon bestätigt? Dann nicht nochmal.
    if (userSide == MatchSide.LEFT and match.left_bans_confirmed) or (userSide == MatchSide.RIGHT and match.right_bans_confirmed):
        return redirect("matchDetail", matchId=matchId)

    # Available: alle enabled Resonatoren (bannen darf man alles, auch was später selber gepickt werden könnte)
    available = Resonator.objects.filter(is_enabled=True)

    form = BanConfirmForm(request.POST, available=available)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    selected = form.cleaned_data["bans"]

    # Alte Bans dieser Side entfernen (falls neu submitten erlaubt sein soll)
    MatchDraftAction.objects.filter(match=match, action_type=DraftActionType.BAN, acting_side=userSide).delete()

    targetSide = MatchSide.RIGHT if userSide == MatchSide.LEFT else MatchSide.LEFT

    # Neue Bans schreiben
    for idx, res in enumerate(selected, start=1):
        MatchDraftAction.objects.create(
            match=match,
            step_index=1000 + idx if userSide == MatchSide.LEFT else 2000 + idx,  # nur zur stabilen Sortierung
            action_type=DraftActionType.BAN,
            acting_side=userSide,
            target_side=targetSide,
            resonator=res,
        )

    # Confirm-Flag setzen
    if userSide == MatchSide.LEFT:
        match.left_bans_confirmed = True
    else:
        match.right_bans_confirmed = True
    match.save()

    return redirect("matchDetail", matchId=matchId)


@transaction.atomic
def matchConfirmPicks(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)
    userSide = _getUserSide(request.user, match)
    if userSide is None:
        return HttpResponseForbidden("Forbidden")

    # Nur wenn beide Bans confirmed
    if not (match.left_bans_confirmed and match.right_bans_confirmed):
        return redirect("matchDetail", matchId=matchId)

    # Schon bestätigt?
    if (userSide == MatchSide.LEFT and match.left_picks_confirmed) or (userSide == MatchSide.RIGHT and match.right_picks_confirmed):
        return redirect("matchDetail", matchId=matchId)

    available = getPickAvailableForSide(match, userSide)

    form = PickConfirmForm(request.POST, available=available)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    selected = form.cleaned_data["picks"]

    # Alte Picks dieser Side löschen, falls re-submit erlaubt
    MatchDraftAction.objects.filter(match=match, action_type=DraftActionType.PICK, acting_side=userSide).delete()

    for idx, res in enumerate(selected, start=1):
        MatchDraftAction.objects.create(
            match=match,
            step_index=3000 + idx if userSide == MatchSide.LEFT else 4000 + idx,
            action_type=DraftActionType.PICK,
            acting_side=userSide,
            target_side=userSide,
            resonator=res,
        )

    if userSide == MatchSide.LEFT:
        match.left_picks_confirmed = True
    else:
        match.right_picks_confirmed = True
    match.save()

    return redirect("matchDetail", matchId=matchId)


@transaction.atomic
def matchDraftReset(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)

    # Nur Host darf resetten
    if not (request.user.is_authenticated and request.user.role in (UserRole.ADMIN, UserRole.COMMENTATOR)):
        return HttpResponseForbidden("Forbidden")

    MatchDraftAction.objects.filter(match=match).delete()

    match.left_bans_confirmed = False
    match.right_bans_confirmed = False
    match.left_picks_confirmed = False
    match.right_picks_confirmed = False
    match.save()

    return redirect("matchDetail", matchId=matchId)