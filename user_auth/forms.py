from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as text
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        # Agregué 'email' para que también puedas pedirlo si querés luego
        fields = ["username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        # Defino placeholders y clases Bootstrap para cada campo
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Nombre de usuario",
                "autofocus": True,
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Contraseña",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Confirmar contraseña",
            }
        )


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombre de usuario",
                "autofocus": True,
                "autocomplete": "username",
            }
        )
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
                "autocomplete": "current-password",
                "id": "id_password",  # para manejar el toggle password en JS
            }
        ),
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                text("Esta cuenta está inactiva."),
                code="inactive",
            )

    error_messages = {
        "invalid_login": text("El nombre de usuario o la contraseña no son correctos."),
        "inactive": text("Esta cuenta está inactiva."),
    }
