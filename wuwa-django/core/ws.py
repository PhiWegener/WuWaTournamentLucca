from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcastDraftUpdate(matchId: int):
    channelLayer = get_channel_layer()
    groupName = f"matchDraft_{matchId}"

    async_to_sync(channelLayer.group_send)(
        groupName,
        {"type": "draft_refresh"},
    )


def broadcastPageRefresh(matchId: int):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"matchDraft_{matchId}",
        {"type": "page_refresh"},
    )
