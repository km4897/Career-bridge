from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[(User.Role.APPLICANT, "Applicant"), (User.Role.EMPLOYER, "Employer")],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]
