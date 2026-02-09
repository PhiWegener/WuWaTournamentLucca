import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from .models import Match, UserRole, MatchSide
from .draft import buildDraftContext


class MatchDraftConsumer(AsyncWebsocketConsumer):

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

        await self.sendDraftState(user.id)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.groupName, self.channel_name)

    async def draftUpdated(self, event):
        await self.send(text_data=json.dumps({"type": "refresh"}))

    async def sendDraftState(self, userId):
        payload = await self._buildPayload(userId)
        await self.send(text_data=json.dumps(payload))

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

        html = render_to_string(
            "core/partials/match_draft.html",
            context
        )

        return {
            "type": "draftState",
            "html": html
        }
