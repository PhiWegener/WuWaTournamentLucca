from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from .models import Match
from .views import buildDraftContext


def broadcastDraftUpdate(matchId: int):

    channelLayer = get_channel_layer()
    groupName = f"matchDraft_{matchId}"

    match = Match.objects.get(id=matchId)

    # Observer neutral render
    User = get_user_model()
    dummyUser = User.objects.filter(is_superuser=True).first()

    context = buildDraftContext(match, dummyUser)

    html = render_to_string(
        "core/partials/match_draft.html",
        context
    )

    async_to_sync(channelLayer.group_send)(
        groupName,
        {
            "type": "draftUpdated",
            "payload": {
                "type": "draftState",
                "html": html
            }
        }
    )
