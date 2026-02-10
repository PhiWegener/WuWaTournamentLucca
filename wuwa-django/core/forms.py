from django import forms
from .models import Boss, Match, Player, BossTime, MatchSide, Resonator, DraftActionType
import re

class HostMatchCreateForm(forms.Form):
    playerLeft = forms.ModelChoiceField(queryset=Player.objects.all())
    playerRight = forms.ModelChoiceField(queryset=Player.objects.all())
    boss = forms.ModelChoiceField(queryset=Boss.objects.all(), required=False)
    firstPickSide = forms.ChoiceField(choices=MatchSide.choices)

class MatchTimeSubmitForm(forms.Form):
    timeInput = forms.CharField(
        label="Time (M:SS.mmm)",
        help_text="Examples: 1:23, 1:23.456, 12:05.120",
        max_length=32,
        required=True,
    )

    def clean(self) -> dict:
        cleaned = super().clean()
        raw = (cleaned.get("timeInput") or "").strip()
        if not raw:
            return cleaned

        timeMs = self._parseTimeToMs(raw)
        cleaned["timeMs"] = timeMs
        return cleaned

    @staticmethod
    def _parseTimeToMs(value: str) -> int:
        s = value.strip().replace(",", ".")

        # M:SS(.mmm)
        m = re.fullmatch(r"(?P<min>\d+):(?P<sec>\d{1,2})(?:\.(?P<ms>\d{1,3}))?", s)
        if m:
            minutes = int(m.group("min"))
            seconds = int(m.group("sec"))
            if seconds >= 60:
                raise forms.ValidationError("Seconds must be < 60 in M:SS format.")

            msStr = m.group("ms")
            if msStr is None:
                ms = 0
            else:
                ms = int(msStr.ljust(3, "0"))  # 1->100, 12->120, 123->123

            return (minutes * 60 + seconds) * 1000 + ms

        # Optional: SS(.mmm)
        m = re.fullmatch(r"(?P<sec>\d+)(?:\.(?P<ms>\d{1,3}))?", s)
        if m:
            seconds = int(m.group("sec"))
            msStr = m.group("ms")
            ms = 0 if msStr is None else int(msStr.ljust(3, "0"))
            return seconds * 1000 + ms

        raise forms.ValidationError("Invalid time format. Use M:SS.mmm (e.g. 1:23.456).")

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