from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from .models import Match, UserRole
from .draft import buildDraftContext


class MatchDraftConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.matchId = int(self.scope["url_route"]["kwargs"]["matchId"])
        self.groupName = f"matchDraft_{self.matchId}"

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        allowed = await self._userAllowed(user.id)
        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(self.groupName, self.channel_name)
        await self.accept()

        payload = await self._buildPayload(user.id)
        await self.send_json(payload)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.groupName, self.channel_name)

    async def draft_refresh(self, event):
        await self.send_json({"type": "draft_refresh"})

    async def page_refresh(self, event):
        await self.send_json({"type": "page_refresh"})

    @database_sync_to_async
    def _userAllowed(self, userId):
        User = get_user_model()
        user = User.objects.select_related("player").get(id=userId)
        match = Match.objects.get(id=self.matchId)

        isHost = user.role in (UserRole.ADMIN, UserRole.COMMENTATOR)
        isPlayer = user.player_id in (match.player_left_id, match.player_right_id)
        return isHost or isPlayer

    @database_sync_to_async
    def _buildPayload(self, userId):
        User = get_user_model()
        user = User.objects.select_related("player").get(id=userId)
        match = Match.objects.get(id=self.matchId)

        context = buildDraftContext(match, user)
        html = render_to_string("core/partials/match_draft.html", context)

        return {"type": "draftState", "html": html}
