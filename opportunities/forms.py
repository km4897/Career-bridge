from django import forms
from .models import Opportunity


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            "title", "description", "opportunity_type",
            "location", "duration_weeks", "skills_required", "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "opportunity_type": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "duration_weeks": forms.NumberInput(attrs={"class": "form-control"}),
            "skills_required": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class OpportunitySearchForm(forms.Form):
    q = forms.CharField(required=False, label="Keyword")
    opportunity_type = forms.ChoiceField(
        required=False,
        choices=[("", "Any type")] + list(Opportunity.Type.choices),
    )
    location = forms.CharField(required=False)
