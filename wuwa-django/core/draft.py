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

    actions = MatchDraftAction.objects.select_related("resonator").filter(match=match).order_by("step_index")

    banPhaseDone = match.left_bans_confirmed and match.right_bans_confirmed
    pickPhaseDone = match.left_picks_confirmed and match.right_picks_confirmed

    currentBanSlot = _getCurrentBanSlot(match)

    # Nur locked Bans anzeigen (erst wenn beide confirmed haben)
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

    picksLeft = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.LEFT,
            target_side=MatchSide.LEFT,
        )
        .order_by("step_index")
    )

    picksRight = (
        MatchDraftAction.objects.select_related("resonator")
        .filter(
            match=match,
            action_type=DraftActionType.PICK,
            acting_side=MatchSide.RIGHT,
            target_side=MatchSide.RIGHT,
        )
        .order_by("step_index")
    )

    banForm = None
    pickForm = None

    banPending = None
    if isPlayerInMatch and not banPhaseDone and currentBanSlot <= BAN_COUNT:
        banPending = MatchDraftAction.objects.select_related("resonator").filter(
            match=match,
            action_type=DraftActionType.BAN,
            acting_side=userSide,
            slot_index=currentBanSlot,
            is_locked=False,
        ).first()

        # wenn schon pending ausgewählt, dann zeigen wir Form optional trotzdem (re-choose)
        banForm = BanConfirmForm(available=Resonator.objects.filter(is_enabled=True))

    return {
        "match": match,
        "isHost": isHost,
        "userSide": userSide,
        "isPlayerInMatch": isPlayerInMatch,
        "actions": actions,
        "banPhaseDone": banPhaseDone,
        "pickPhaseDone": pickPhaseDone,
        "currentBanSlot": currentBanSlot,
        "banCount": BAN_COUNT,
        "banPending": banPending,
        "banForm": banForm,
        "pickForm": pickForm,
        "bansLeftToRight": bansLeftToRight,
        "bansRightToLeft": bansRightToLeft,
        "picksLeft": picksLeft,
        "picksRight": picksRight,
    }
