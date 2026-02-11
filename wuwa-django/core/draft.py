from __future__ import annotations

from .models import (
    DraftActionType,
    MatchDraftAction,
    MatchSide,
    Resonator,
    UserRole,
)
from .forms import BanConfirmForm, PickConfirmForm


BAN_COUNT = 3
PICK_COUNT = 3



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


# def _getBanAvailable(match, *, allowReselectAction: MatchDraftAction | None):
#     usedIds = set(
#         MatchDraftAction.objects.filter(match=match).values_list("resonator_id", flat=True)
#     )
#     if allowReselectAction is not None:
#         usedIds.discard(allowReselectAction.resonator_id)

#     return Resonator.objects.filter(is_enabled=True).exclude(id__in=usedIds)


def _getCurrentPickSlot(match) -> int:
    lockedSlots = (
        MatchDraftAction.objects
        .filter(match=match, action_type=DraftActionType.PICK, is_locked=True)
        .values_list("slot_index", flat=True)
        .distinct()
    )
    return len(set(lockedSlots)) + 1


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
        usedBanIds = set(
            MatchDraftAction.objects.filter(
                match=match,
                action_type=DraftActionType.BAN,
                acting_side=userSide,
            ).values_list("resonator_id", flat=True)
        )

        if allowReselectAction is not None:
            usedBanIds.discard(allowReselectAction.resonator_id)

        available = Resonator.objects.filter(is_enabled=True).exclude(id__in=usedBanIds)
        banForm = BanConfirmForm(available=available)
        banAvailableCount = available.count()

    # Locked picks (für Anzeige)
    picksLeft = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.LEFT,
            target_side=MatchSide.LEFT,
            is_locked=True,
        )
        .order_by("slot_index")
    )

    picksRight = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.RIGHT,
            target_side=MatchSide.RIGHT,
            is_locked=True,
        )
        .order_by("slot_index")
    )

    currentPickSlot = _getCurrentPickSlot(match)

    # Pending picks – nur Host
    picksLeftPending = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.LEFT,
            target_side=MatchSide.LEFT,
            is_locked=False,
        )
        .order_by("slot_index")
    )

    picksRightPending = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.RIGHT,
            target_side=MatchSide.RIGHT,
            is_locked=False,
        )
        .order_by("slot_index")
    )

    pickPending = None
    allowReselectPick = None
    if isPlayerInMatch and banPhaseDone and (not pickPhaseDone) and currentPickSlot <= PICK_COUNT:
        pickPending = (
            MatchDraftAction.objects.select_related("resonator")
            .filter(
                match=match,
                action_type=DraftActionType.PICK,
                acting_side=userSide,
                slot_index=currentPickSlot,
                is_locked=False,
            )
            .first()
        )
        allowReselectPick = pickPending

    pickForm = None
    pickAvailableCount = 0
    if isPlayerInMatch and banPhaseDone and (not pickPhaseDone) and currentPickSlot <= PICK_COUNT:
        usedPickIds = set(
            MatchDraftAction.objects.filter(
                match=match,
                action_type=DraftActionType.PICK,
                acting_side=userSide,
            ).values_list("resonator_id", flat=True)
        )

        if allowReselectPick is not None:
            usedPickIds.discard(allowReselectPick.resonator_id)

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

        pickForm = PickConfirmForm(available=available)
        pickAvailableCount = available.count()

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
        "currentPickSlot": currentPickSlot,
        "pickCount": PICK_COUNT,
        "pickPending": pickPending,
        "pickForm": pickForm,
        "pickAvailableCount": pickAvailableCount,
        "picksLeftPending": picksLeftPending if isHost else [],
        "picksRightPending": picksRightPending if isHost else [],
    }
