from django.db import models
from django.contrib.auth.models import User

# from django.db.models.signals import post_save

# from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    web_site = models.CharField(max_length=200, blank=True, null=True)
    birth_date = models.DateField()
    is_author = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


""" # Señal para crear o actualizar automáticamente el perfil cuando se crea un usuario
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
 """
