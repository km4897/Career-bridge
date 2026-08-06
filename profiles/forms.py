from django import forms
from .models import ApplicantProfile, EmployerProfile, Skill


class ApplicantProfileForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        help_text="Comma-separated, e.g. Python, Django, Communication",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Python, Django, Communication"}),
    )

    class Meta:
        model = ApplicantProfile
        fields = ["full_name", "bio", "education", "cv", "certificate", "id_document"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "education": forms.TextInput(attrs={"class": "form-control"}),
            "cv": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "certificate": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "id_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["skills"].initial = ", ".join(s.name for s in self.instance.skills.all())

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            self._save_skills(profile)
        return profile

    def _save_skills(self, profile):
        names = [s.strip() for s in self.cleaned_data.get("skills", "").split(",") if s.strip()]
        skills = []
        for name in names:
            skill, _ = Skill.objects.get_or_create(name__iexact=name, defaults={"name": name})
            skills.append(skill)
        profile.skills.set(skills)


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ["organisation_name", "sector", "description", "logo", "website"]
        widgets = {
            "organisation_name": forms.TextInput(attrs={"class": "form-control"}),
            "sector": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
        }
