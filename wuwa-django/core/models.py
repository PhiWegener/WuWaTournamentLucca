from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    COMMENTATOR = "COMMENTATOR", "Commentator"
    PLAYER = "PLAYER", "Player"


class MatchSide(models.TextChoices):
    LEFT = "LEFT", "Left"
    RIGHT = "RIGHT", "Right"


class DraftActionType(models.TextChoices):
    PICK = "PICK", "Pick"
    BAN = "BAN", "Ban"


class Player(models.Model):
    name = models.CharField(max_length=120, db_index=True)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """
    App-User mit Login, optional einem Player zugeordnet.
    Django übernimmt Passwort-Hashing/Verifikation.
    """
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.PLAYER)
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")

    def __str__(self) -> str:
        return self.username


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    
    players = models.ManyToManyField(Player, blank=True, related_name="tournaments")

    def __str__(self) -> str:
        return self.name


class Boss(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Resonator(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    icon_url = models.URLField()
    is_enabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, null=True, blank=True, on_delete=models.SET_NULL, related_name="matches")

    player_left = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="matches_as_left")
    player_right = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="matches_as_right")

    boss = models.ForeignKey(Boss, null=True, blank=True, on_delete=models.SET_NULL, related_name="matches")

    first_pick_side = models.CharField(max_length=5, choices=MatchSide.choices)
    winner_player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="wins")

    left_time_ms = models.PositiveIntegerField(null=True, blank=True)
    right_time_ms = models.PositiveIntegerField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    left_bans_confirmed = models.BooleanField(default=False)
    right_bans_confirmed = models.BooleanField(default=False)
    left_picks_confirmed = models.BooleanField(default=False)
    right_picks_confirmed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.player_left} vs {self.player_right}"

    round_index = models.PositiveIntegerField(default=0, db_index=True)
    match_index = models.PositiveIntegerField(default=0, db_index=True)

    next_match = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_matches",
    )
    next_side = models.CharField(max_length=5, choices=MatchSide.choices, null=True, blank=True)

    class Meta:
        unique_together = [("tournament", "round_index", "match_index")]
        ordering = ["round_index", "match_index"]

# class MatchDraftAction(models.Model):
#     match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="draft_actions")
    
#     step_index = models.PositiveIntegerField(db_index=True)
#     action_type = models.CharField(max_length=10, choices=DraftActionType.choices)
#     acting_side = models.CharField(max_length=5, choices=MatchSide.choices)
#     target_side = models.CharField(max_length=5, choices=MatchSide.choices)
#     slot_index = models.PositiveIntegerField(default=1)
#     is_locked = models.BooleanField(default=False)

#     resonator = models.ForeignKey(Resonator, on_delete=models.CASCADE, related_name="draft_actions")

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["match", "step_index"],
#                 name="uniq_matchdraftaction_match_step",
#             ),
#             models.UniqueConstraint(
#                 fields=["match", "action_type", "slot_index", "acting_side"],
#                 name="uniq_matchdraftaction_slot_per_side",
#             ),
#         ]
#         ordering = ["step_index"]


    def __str__(self) -> str:
        return f"{self.match} {self.action_type} {self.resonator} ({self.acting_side})"


class BossTime(models.Model):
    """
    Pro Player + Boss nur eine Bestzeit.
    Updates überschreiben, wenn besser.
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="boss_times")
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE, related_name="boss_times")

    best_time_ms = models.PositiveIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("player", "boss")]
        ordering = ["best_time_ms"]
