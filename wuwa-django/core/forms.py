from django import forms
from .models import Boss, Match, Player, BossTime, MatchSide, Resonator, DraftActionType

class PlayerTimeSubmitForm(forms.Form):
    timeSeconds = forms.IntegerField(min_value=1)

class HostMatchWinnerForm(forms.Form):
    winner = forms.ModelChoiceField(queryset=Player.objects.none(), required=False)
    leftTimeSeconds = forms.IntegerField(min_value=1, required=False)
    rightTimeSeconds = forms.IntegerField(min_value=1, required=False)
    
    def __init__(self, *args, **kwargs):
        match = kwargs.pop(match, None)
        super().__init__(*args, **kwargs)
        if match is not None:
            self.fields["winner"].queryset = Player.objects.filter(id__in=[match.player_left_id, match.player_right_id])

class HostMatchCreateForm(forms.Form):
    playerLeft = forms.ModelChoiceField(queryset=Player.objects.all())
    playerRight = forms.ModelChoiceField(queryset=Player.objects.all())
    boss = forms.ModelChoiceField(queryset=Boss.objects.all(), required=False)
    firstPickSide = forms.ChoiceField(choices=MatchSide.choices)

class MatchTimeSubmitForm(forms.Form):
    timeSeconds = forms.IntegerField(min_value=1)

class DraftActionForm(forms.Form):
    actionType = forms.ChoiceField(choices = DraftActionType.choices)
    actingSide = forms.ChoiceField(choices = MatchSide.choices)
    resonator = forms.ModelChoiceField(queryset=Resonator.objects.filter(is_enabled=True))

    def __init__(self, *args, **kwargs):
        availableResonators = kwargs.pop("availableResonators", None)
        super().__init__(*args, **kwargs)
        if availableResonators is not None:
            self.fields["resonator"].queryset = availableResonators

class BanConfirmForm(forms.Form):
    ban = forms.ModelChoiceField(
        queryset=Resonator.objects.none(),
        widget=forms.Select(),
        empty_label="-- bitte wählen --",
        label="Ban",
    )

    def __init__(self, *args, **kwargs):
        available = kwargs.pop("available", None)
        super().__init__(*args, **kwargs)
        if available is not None:
            self.fields["ban"].queryset = available
        
    def clean_ban(self):
        ban = self.cleaned_data["ban"]
        if ban is None:
            raise forms.ValidationError("Bitte einen Ban auswählen")
        return ban

class PickConfirmForm(forms.Form):
    pick = forms.ModelChoiceField(
        queryset=Resonator.objects.none(),
        widget=forms.Select(),
        empty_label="— bitte wählen —",
        label="Pick",
    )

    def __init__(self, *args, **kwargs):
        available = kwargs.pop("available", None)
        super().__init__(*args, **kwargs)
        if available is not None:
            self.fields["pick"].queryset = available

    def clean_pick(self):
        pick = self.cleaned_data["pick"]
        if pick is None:
            raise forms.ValidationError("Bitte einen Pick auswählen.")
        return pick