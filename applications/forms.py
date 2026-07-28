from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cover_note"]
        widgets = {
            "cover_note": forms.Textarea(attrs={
                "rows": 4, "class": "form-control",
                "placeholder": "Optional note to the employer...",
            }),
        }


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]
        widgets = {"status": forms.Select(attrs={"class": "form-select form-select-sm"})}
