from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["full_name", "phone_number", "cv", "cover_note"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name for this application"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "cv": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "cover_note": forms.Textarea(attrs={
                "rows": 4, "class": "form-control",
                "placeholder": "Tell the employer why you're a good fit for this specific role...",
            }),
        }


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]
        widgets = {"status": forms.Select(attrs={"class": "form-select form-select-sm"})}
