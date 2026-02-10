from rest_framework import serializers
from core.models import Match, MatchDraftAction, Player, Boss, Resonator


class PlayerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "name"]


class BossMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boss
        fields = ["id", "slug", "name"]


class ResonatorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resonator
        fields = ["id", "slug", "name", "icon_url", "is_enabled"]


class MatchDraftActionSerializer(serializers.ModelSerializer):
    resonator = ResonatorMiniSerializer(read_only=True)

    class Meta:
        model = MatchDraftAction
        fields = [
            "id",
            "step_index",
            "action_type",
            "acting_side",
            "target_side",
            "resonator",
            "created_at",
        ]


class MatchDashboardSerializer(serializers.ModelSerializer):
    playerLeft = PlayerMiniSerializer(source="player_left", read_only=True)
    playerRight = PlayerMiniSerializer(source="player_right", read_only=True)
    winnerPlayer = PlayerMiniSerializer(source="winner_player", read_only=True)
    boss = BossMiniSerializer(read_only=True)
    draftActions = MatchDraftActionSerializer(source="draft_actions", many=True, read_only=True)
    leftPicks = serializers.SerializerMethodField()
    rightPicks = serializers.SerializerMethodField()
    leftBans = serializers.SerializerMethodField()
    rightBans = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament_id",
            "playerLeft",
            "playerRight",
            "boss",
            "first_pick_side",
            "winnerPlayer",
            "left_time_ms",
            "right_time_ms",
            "started_at",
            "finished_at",
            "left_bans_confirmed",
            "right_bans_confirmed",
            "left_picks_confirmed",
            "right_picks_confirmed",
            "draftActions",
            "leftPicks",
            "rightPicks",
            "leftBans",
            "rightBans",
        ]
    


    def _by(self, obj, actionType, targetSide):
        return [
            a.resonator_id
            for a in obj.draft_actions.all()
            if a.action_type == actionType and a.target_side == targetSide
        ]

    def get_leftPicks(self, obj): return self._by(obj, "PICK", "LEFT")
    def get_rightPicks(self, obj): return self._by(obj, "PICK", "RIGHT")
    def get_leftBans(self, obj): return self._by(obj, "BAN", "LEFT")
    def get_rightBans(self, obj): return self._by(obj, "BAN", "RIGHT")
