from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[(User.Role.APPLICANT, "Applicant"), (User.Role.EMPLOYER, "Employer")],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Django's defaults are verbose (bulleted validator list, "required"
        # hint text, etc.) — trim to short, single-line helper text instead.
        self.fields["username"].help_text = "Letters, digits and @/./+/-/_ only."
        self.fields["username"].widget.attrs.update({"placeholder": "e.g. jane_doe", "autofocus": True})
        self.fields["email"].widget.attrs.update({"placeholder": "you@example.com"})
        self.fields["password1"].help_text = "At least 8 characters. Avoid common passwords."
        self.fields["password1"].widget.attrs.update({"placeholder": "Create a password"})
        self.fields["password2"].help_text = ""
        self.fields["password2"].widget.attrs.update({"placeholder": "Re-enter your password"})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"placeholder": "Username", "autofocus": True})
        self.fields["password"].widget.attrs.update({"placeholder": "Password"})
        self.fields["username"].help_text = ""
        self.fields["password"].help_text = ""
