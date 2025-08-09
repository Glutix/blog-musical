from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


# funciones al crear un usuario
def create_profile(user):
    Profile.objects.create(user=user)


# TODO: Posible implentacion a futuro, se deberia cambiar el modelo user, para que el campo de email sea obligatorio
# TODO: Tambien hay que validar los correo y realizar las configuraciones necesarias en setting.py
# def send_welcome_email():
#    pass


ACTIONS_ON_USER_CREATED = [create_profile]


@receiver(post_save, sender=User)
def my_handler(sender, instance, created, **kwargs):
    if created:
        for action in ACTIONS_ON_USER_CREATED:
            action(instance)
