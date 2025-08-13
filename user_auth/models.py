# user_auth/models.py
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = CloudinaryField(
        "image", blank=True, null=True
    )  # Permitir que sea opcional
    bio = models.TextField(blank=True, null=True)
    web_site = models.URLField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    is_author = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def has_avatar(self):
        return bool(self.avatar and self.avatar.url)

    @property
    def get_avatar_url(self):
        """
        Devuelve la URL del avatar. Si no hay avatar, devuelve uno por defecto.
        """
        if self.has_avatar:
            return self.avatar.url
        else:
            # Opción 1: Avatar generado con iniciales del usuario
            return self.get_generated_avatar()

    def get_generated_avatar(self):
        """
        Genera un avatar por defecto basado en las iniciales del usuario.
        Puedes elegir entre diferentes servicios.
        """
        # Opción A: UI Avatars (gratuito, buena calidad)
        initials = self.get_user_initials()
        return f"https://ui-avatars.com/api/?name={initials}&background=f39c12&color=ffffff&size=200&bold=true"

        # Opción B: DiceBear (más variedad de estilos)
        # return f"https://api.dicebear.com/7.x/initials/svg?seed={self.user.username}&backgroundColor=f39c12"

        # Opción C: Gravatar con fallback
        # email_hash = hashlib.md5(self.user.email.lower().encode('utf-8')).hexdigest()
        # return f"https://www.gravatar.com/avatar/{email_hash}?s=200&d=identicon"

    def get_user_initials(self):
        """
        Obtiene las iniciales del usuario para el avatar generado.
        """
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}"
        elif self.user.first_name:
            return self.user.first_name[:2]
        else:
            return self.user.username[:2]

    @property
    def avatar_with_fallback(self):
        """
        Método alternativo que combina avatar personalizado con fallback.
        """
        if self.has_avatar:
            return self.avatar.url

        # Diferentes opciones de fallback
        username = self.user.username

        # Opción 1: UI Avatars con colores basados en el usuario
        colors = ["f39c12", "e74c3c", "3498db", "2ecc71", "9b59b6", "e67e22"]
        color_index = sum(ord(c) for c in username) % len(colors)
        background_color = colors[color_index]

        initials = self.get_user_initials()
        return f"https://ui-avatars.com/api/?name={initials}&background={background_color}&color=ffffff&size=200&bold=true"
