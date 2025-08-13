from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as text
from django.contrib.auth.models import User
from .models import Profile
from django import forms
from django.core.files.uploadedfile import UploadedFile


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "web_site", "birth_date"]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Cuéntanos sobre ti, tu experiencia musical, instrumentos que tocas, géneros favoritos...",
                }
            ),
            "web_site": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://tu-sitio-web.com",
                }
            ),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "avatar": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }

        help_texts = {
            "bio": "Máximo 500 caracteres",
            "web_site": "URL completa incluyendo http:// o https://",
            "birth_date": "Solo se mostrará el día y mes públicamente",
            "avatar": "Formatos permitidos: JPG, PNG, GIF. Tamaño máximo: 5MB",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hacer todos los campos opcionales
        for field in self.fields.values():
            field.required = False

        # Personalizar labels
        self.fields["avatar"].label = "Imagen de perfil"
        self.fields["bio"].label = "Biografía"
        self.fields["web_site"].label = "Sitio web"
        self.fields["birth_date"].label = "Fecha de nacimiento"

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")

        if avatar and isinstance(avatar, UploadedFile):
            # Validar tamaño del archivo (5MB máximo)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La imagen debe ser menor a 5MB.")

            # Validar tipo de archivo
            if not avatar.content_type.startswith("image/"):
                raise forms.ValidationError("Solo se permiten archivos de imagen.")

        return avatar

    def clean_bio(self):
        bio = self.cleaned_data.get("bio")

        if bio and len(bio) > 500:
            raise forms.ValidationError(
                "La biografía no puede exceder los 500 caracteres."
            )

        return bio

    def clean_web_site(self):
        web_site = self.cleaned_data.get("web_site")

        if web_site:
            # Agregar protocolo si no lo tiene
            if not web_site.startswith(("http://", "https://")):
                web_site = "https://" + web_site

        return web_site
