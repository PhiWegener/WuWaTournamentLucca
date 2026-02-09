from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcastDraftUpdate(matchId: int):
    channelLayer = get_channel_layer()
    groupName = f"matchDraft_{matchId}"

    async_to_sync(channelLayer.group_send)(
        groupName,
        {"type": "draftUpdated", "payload": {"type": "refresh"}},
    )

