from __future__ import annotations

from .models import (
    DraftActionType,
    MatchDraftAction,
    MatchSide,
    Resonator,
    UserRole,
)
from .forms import BanConfirmForm


BAN_COUNT = 3


def _getUserSide(user, match) -> str | None:
    if not getattr(user, "is_authenticated", False):
        return None
    player = getattr(user, "player", None)
    if player is None:
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


def _getBanAvailable(match, *, allowReselectAction: MatchDraftAction | None):
    usedIds = set(
        MatchDraftAction.objects.filter(match=match).values_list("resonator_id", flat=True)
    )
    if allowReselectAction is not None:
        usedIds.discard(allowReselectAction.resonator_id)

    return Resonator.objects.filter(is_enabled=True).exclude(id__in=usedIds)


def buildDraftContext(match, requestUser) -> dict:
    isHost = bool(
        getattr(requestUser, "is_authenticated", False)
        and getattr(requestUser, "role", None) in (UserRole.ADMIN, UserRole.COMMENTATOR)
    )
    userSide = _getUserSide(requestUser, match)
    isPlayerInMatch = userSide is not None

    banPhaseDone = bool(match.left_bans_confirmed and match.right_bans_confirmed)
    pickPhaseDone = bool(match.left_picks_confirmed and match.right_picks_confirmed)

    currentBanSlot = _getCurrentBanSlot(match)

    bansLeftToRight = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=MatchSide.LEFT,
            target_side=MatchSide.RIGHT,
            is_locked=True,
        )
        .order_by("slot_index")
    )
    bansRightToLeft = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=MatchSide.RIGHT,
            target_side=MatchSide.LEFT,
            is_locked=True,
        )
        .order_by("slot_index")
    )

    # Pending – nur Host
    bansLeftToRightPending = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=MatchSide.LEFT,
            target_side=MatchSide.RIGHT,
            is_locked=False,
        )
        .order_by("slot_index")
    )
    bansRightToLeftPending = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=MatchSide.RIGHT,
            target_side=MatchSide.LEFT,
            is_locked=False,
        )
        .order_by("slot_index")
    )

    banPending = None
    allowReselectAction = None
    if isPlayerInMatch and (not banPhaseDone) and currentBanSlot <= BAN_COUNT:
        banPending = (
            MatchDraftAction.objects.select_related("resonator")
            .filter(
                match=match,
                action_type=DraftActionType.BAN,
                acting_side=userSide,
                slot_index=currentBanSlot,
                is_locked=False,
            )
            .first()
        )
        allowReselectAction = banPending

    banForm = None
    banAvailableCount = 0
    if isPlayerInMatch and (not banPhaseDone) and currentBanSlot <= BAN_COUNT:
        available = _getBanAvailable(match, allowReselectAction=allowReselectAction)
        banForm = BanConfirmForm(available=available)
        banAvailableCount = available.count()

    # Picks bleiben erstmal wie gehabt (Template erwartet die Variablen)
    picksLeft = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(match=match, action_type=DraftActionType.PICK, acting_side=MatchSide.LEFT, target_side=MatchSide.LEFT)
        .order_by("step_index")
    )
    picksRight = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(match=match, action_type=DraftActionType.PICK, acting_side=MatchSide.RIGHT, target_side=MatchSide.RIGHT)
        .order_by("step_index")
    )

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
        "banForm": banForm,
        "banAvailableCount": banAvailableCount,

        "bansLeftToRight": bansLeftToRight,
        "bansRightToLeft": bansRightToLeft,

        "bansLeftToRightPending": bansLeftToRightPending if isHost else [],
        "bansRightToLeftPending": bansRightToLeftPending if isHost else [],

        "picksLeft": picksLeft,
        "picksRight": picksRight,
    }
