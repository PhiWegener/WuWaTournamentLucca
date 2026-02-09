from .models import (
    MatchDraftAction, Resonator,
    UserRole, MatchSide, DraftActionType
)
from .forms import BanConfirmForm, PickConfirmForm


BAN_COUNT = 3  # falls du das später pro Match konfigurierbar machen willst


def _getUserSide(user, match):
    if not user.is_authenticated or user.player is None:
        return None
    if user.player_id == match.player_left_id:
        return MatchSide.LEFT
    if user.player_id == match.player_right_id:
        return MatchSide.RIGHT
    return None


def _getCurrentBanSlot(match) -> int:
    lockedSlots = (
        MatchDraftAction.objects
        .filter(match=match, action_type=DraftActionType.BAN, is_locked=True)
        .values_list("slot_index", flat=True)
        .distinct()
    )
    return len(set(lockedSlots)) + 1


def buildDraftContext(match, requestUser):
    isHost = requestUser.is_authenticated and requestUser.role in (UserRole.ADMIN, UserRole.COMMENTATOR)
    userSide = _getUserSide(requestUser, match)
    isPlayerInMatch = userSide is not None

    banPhaseDone = match.left_bans_confirmed and match.right_bans_confirmed
    pickPhaseDone = match.left_picks_confirmed and match.right_picks_confirmed

    currentBanSlot = _getCurrentBanSlot(match)

    # FINAL (locked) – das sehen Spieler + Host
    bansLeftToRight = MatchDraftAction.objects.select_related("resonator").filter(
        match=match,
        action_type=DraftActionType.BAN,
        acting_side=MatchSide.LEFT,
        target_side=MatchSide.RIGHT,
        is_locked=True,
    ).order_by("slot_index")

    bansRightToLeft = MatchDraftAction.objects.select_related("resonator").filter(
        match=match,
        action_type=DraftActionType.BAN,
        acting_side=MatchSide.RIGHT,
        target_side=MatchSide.LEFT,
        is_locked=True,
    ).order_by("slot_index")

    # PENDING – nur Host/Observer soll das sehen
    bansLeftToRightPending = MatchDraftAction.objects.select_related("resonator").filter(
        match=match,
        action_type=DraftActionType.BAN,
        acting_side=MatchSide.LEFT,
        target_side=MatchSide.RIGHT,
        is_locked=False,
    ).order_by("slot_index")

    bansRightToLeftPending = MatchDraftAction.objects.select_related("resonator").filter(
        match=match,
        action_type=DraftActionType.BAN,
        acting_side=MatchSide.RIGHT,
        target_side=MatchSide.LEFT,
        is_locked=False,
    ).order_by("slot_index")

    # eigener pending Ban (für Spieler UI)
    banPending = None
    if isPlayerInMatch and not banPhaseDone and currentBanSlot <= BAN_COUNT:
        banPending = MatchDraftAction.objects.select_related("resonator").filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=userSide,
            slot_index=currentBanSlot,
            is_locked=False,
        ).first()

    banForm = None

    if isPlayerInMatch and not banPhaseDone and currentBanSlot <= BAN_COUNT:
    # used resonators (ban+pick) im match
        usedIds = set(
            MatchDraftAction.objects.filter(match=match).values_list("resonator_id", flat=True)
        )

    # allow re-choose own pending for this slot
    existing = MatchDraftAction.objects.filter(
        match=match,
        action_type=DraftActionType.BAN,
        acting_side=userSide,
        slot_index=currentBanSlot,
        is_locked=False,
    ).first()
    if existing is not None:
        usedIds.discard(existing.resonator_id)

    available = Resonator.objects.filter(is_enabled=True).exclude(id__in=usedIds)

    # WICHTIG: Form auch dann anzeigen, wenn available leer ist?
    # Ich empfehle: anzeigen, aber mit Hinweis (sonst "verschwindet" es)
    banForm = BanConfirmForm(available=available)
    banAvailableCount = available.count() if banForm else 0

    return {
        "match": match,
        "isHost": isHost,
        "userSide": userSide,
        "isPlayerInMatch": isPlayerInMatch,
        "banPhaseDone": banPhaseDone,
        "pickPhaseDone": pickPhaseDone,
        "currentBanSlot": currentBanSlot,
        "banCount": BAN_COUNT,
        "banPending": banPending,
        "banAvailableCount": banAvailableCount,
        "bansLeftToRight": bansLeftToRight,
        "bansRightToLeft": bansRightToLeft,
        "bansLeftToRightPending": bansLeftToRightPending if isHost else [],
        "bansRightToLeftPending": bansRightToLeftPending if isHost else [],
    }
