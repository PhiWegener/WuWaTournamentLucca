from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    User, Player, Tournament, Boss, Resonator,
    Match, BossTime, MatchDraftAction
)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    autocomplete_fields = ["players"]

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ["name"]

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Beim Bearbeiten eines bestehenden Users
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("App Fields", {"fields": ("role", "player")}),
    )

    # Beim Anlegen eines neuen Users (DAS war der fehlende Teil)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("App Fields", {"fields": ("role", "player")}),
    )

    list_display = ("username", "email", "role", "player", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")


# admin.site.register(Player)
# admin.site.register(Tournament)
admin.site.register(Boss)
admin.site.register(Resonator)
admin.site.register(Match)
admin.site.register(MatchDraftAction)
admin.site.register(BossTime)
