from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse
from django.db import transaction
from django.template.loader import render_to_string

from .models import Tournament, Match, BossTime, Boss, Player, UserRole, MatchSide, MatchDraftAction, Resonator, DraftActionType
from .forms import HostMatchCreateForm, HostMatchWinnerForm, PlayerTimeSubmitForm, DraftActionForm, MatchTimeSubmitForm, BanConfirmForm, PickConfirmForm
from .permissions import requireRole, requireLogin
from .ws import broadcastDraftUpdate
from .draft import _getCurrentBanSlot, _getCurrentPickSlot, BAN_COUNT, PICK_COUNT, buildDraftContext, _getUserSide

def home(request):
    return render(request, "core/home.html")


def matchDraftPartial(request, matchId: int):
    match = get_object_or_404(
        Match.objects.select_related("player_left", "player_right", "boss", "tournament", "winner_player"),
        id=matchId,
    )

    # gleiche Permission-Logik wie matchDetail
    isHost = request.user.is_authenticated and request.user.role in (UserRole.ADMIN, UserRole.COMMENTATOR)
    userSide = _getUserSide(request.user, match)
    isPlayerInMatch = userSide is not None
    if not (isHost or isPlayerInMatch):
        return HttpResponseForbidden("Forbidden")

    context = buildDraftContext(match, request.user)
    html = render_to_string("core/partials/match_draft.html", context, request=request)
    return HttpResponse(html)

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

def matchDetail(request, matchId: int):
    match = get_object_or_404(
        Match.objects.select_related("player_left", "player_right", "boss", "tournament", "winner_player"),
        id=matchId,
    )

    isHost = request.user.is_authenticated and request.user.role in (UserRole.ADMIN, UserRole.COMMENTATOR)
    userSide = None
    if request.user.is_authenticated and getattr(request.user, "player_id", None) is not None:
        if request.user.player_id == match.player_left_id:
            userSide = "LEFT"
        elif request.user.player_id == match.player_right_id:
            userSide = "RIGHT"

    isPlayerInMatch = userSide is not None

    if not (isHost or isPlayerInMatch):
        return HttpResponseForbidden("Forbidden")

    context = buildDraftContext(match, request.user)
    return render(request, "core/match_detail.html", context)

@requireLogin
def matchDraftAction(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)

    isHost = request.user.role in (UserRole.ADMIN, UserRole.COMMENTATOR)
    userSide = _getUserSide(request.user, match)
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
    broadcastDraftUpdate(match.id)
    return redirect("matchDetail", matchId=matchId)

@requireRole(UserRole.PLAYER)
def matchSubmitTime(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = get_object_or_404(Match, id=matchId)

    # Muss im Match sein
    userSide = _getUserSide(request.user, match)
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


@transaction.atomic
def matchConfirmBans(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = Match.objects.select_for_update().get(id=matchId)

    userSide = _getUserSide(request.user, match)
    if userSide is None:
        return HttpResponseForbidden("Forbidden")

    # Ban-Phase fertig?
    if match.left_bans_confirmed and match.right_bans_confirmed:
        return redirect("matchDetail", matchId=matchId)

    currentSlot = _getCurrentBanSlot(match)
    if currentSlot > BAN_COUNT:
        match.left_bans_confirmed = True
        match.right_bans_confirmed = True
        match.save()
        broadcastDraftUpdate(match.id)
        return redirect("matchDetail", matchId=matchId)

    usedIds = set(
	MatchDraftAction.objects.filter(
		match=match,
		action_type=DraftActionType.BAN,
		acting_side=userSide,
	).values_list("resonator_id", flat=True)
    )

    # Wenn ich im aktuellen Slot schon einen pending Ban habe, darf ich den "re-choosen":
    existing = MatchDraftAction.objects.filter(
        match=match,
        action_type=DraftActionType.BAN,
        acting_side=userSide,
        slot_index=currentSlot,
        is_locked=False,
    ).first()
    if existing is not None:
        usedIds.discard(existing.resonator_id)

    available = Resonator.objects.filter(is_enabled=True).exclude(id__in=usedIds)

    form = BanConfirmForm(request.POST, available=available)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    selectedRes = form.cleaned_data["ban"]

    targetSide = MatchSide.RIGHT if userSide == MatchSide.LEFT else MatchSide.LEFT

    # Upsert pro (match, BAN, slot, side)
    stepIndex = 1000 + (currentSlot * 10) + (1 if userSide == MatchSide.LEFT else 2)

    MatchDraftAction.objects.update_or_create(
        match=match,
        action_type=DraftActionType.BAN,
        slot_index=currentSlot,
        acting_side=userSide,
        defaults={
            "target_side": targetSide,
            "resonator": selectedRes,
            "step_index": stepIndex,
            "is_locked": False,
        },
    )

    # Wenn beide Seiten in diesem Slot einen Ban gesetzt haben -> lock beide
    slotActions = MatchDraftAction.objects.filter(
        match=match,
        action_type=DraftActionType.BAN,
        slot_index=currentSlot,
    )

    hasLeft = slotActions.filter(acting_side=MatchSide.LEFT).exists()
    hasRight = slotActions.filter(acting_side=MatchSide.RIGHT).exists()

    if hasLeft and hasRight:
        slotActions.update(is_locked=True)

        if currentSlot >= BAN_COUNT:
            match.left_bans_confirmed = True
            match.right_bans_confirmed = True
            match.save()

    broadcastDraftUpdate(match.id)
    return redirect("matchDetail", matchId=matchId)

@transaction.atomic
def matchConfirmPicks(request, matchId: int):
    if request.method != "POST":
        return redirect("matchDetail", matchId=matchId)

    match = Match.objects.select_for_update().get(id=matchId)

    userSide = _getUserSide(request.user, match)
    if userSide is None:
        return HttpResponseForbidden("Forbidden")

    # Pick-Phase erst nach Ban-Phase
    if not (match.left_bans_confirmed and match.right_bans_confirmed):
        return redirect("matchDetail", matchId=matchId)

    # Pick-Phase fertig?
    if match.left_picks_confirmed and match.right_picks_confirmed:
        return redirect("matchDetail", matchId=matchId)

    currentSlot = _getCurrentPickSlot(match)
    if currentSlot > PICK_COUNT:
        match.left_picks_confirmed = True
        match.right_picks_confirmed = True
        match.save()
        broadcastDraftUpdate(match.id)
        return redirect("matchDetail", matchId=matchId)

    usedPickIds=set(
		MatchDraftAction.objects.filter(
			match=match,
			action_type=DraftActionType.PICK,
			acting_side=userSide,
		).values_list("resonator_id", flat=True)
	)
	existing = MatchDraftAction.objects.filter(
		match=match,
		action_type=DraftActionType.PICK,
		acting_side=userSide,
		slot_index=currentSlot,
		is_locked=False,
	).first()
	if existing is not None:
		usedPickIds.discard(existing.resonator_id)

    bannedAgainstMe = set(
        MatchDraftAction.objects.filter(
            match=match,
            action_type=DraftActionType.BAN,
            target_side=userSide,
            is_locked=True,
        ).values_list("resonator_id", flat=True)
    )

    available = (
        Resonator.objects.filter(is_enabled=True)
        .exclude(id__in=usedPickIds)
        .exclude(id__in=bannedAgainstMe)
    )

    form = PickConfirmForm(request.POST, available=available)
    if not form.is_valid():
        return redirect("matchDetail", matchId=matchId)

    selectedRes = form.cleaned_data["pick"]

    stepIndex = 3000 + (currentSlot * 10) + (1 if userSide == MatchSide.LEFT else 2)

    MatchDraftAction.objects.update_or_create(
        match=match,
        action_type=DraftActionType.PICK,
        slot_index=currentSlot,
        acting_side=userSide,
        defaults={
            "target_side": userSide,
            "resonator": selectedRes,
            "step_index": stepIndex,
            "is_locked": False,
        },
    )

    slotActions = MatchDraftAction.objects.filter(
        match=match,
        action_type=DraftActionType.PICK,
        slot_index=currentSlot,
    )

    hasLeft = slotActions.filter(acting_side=MatchSide.LEFT).exists()
    hasRight = slotActions.filter(acting_side=MatchSide.RIGHT).exists()

    if hasLeft and hasRight:
        slotActions.update(is_locked=True)

        if currentSlot >= PICK_COUNT:
            match.left_picks_confirmed = True
            match.right_picks_confirmed = True
            match.save()

    broadcastDraftUpdate(match.id)
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
