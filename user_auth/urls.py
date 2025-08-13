from django.urls import path
from . import views

app_name = "user_auth"


urlpatterns = [
    path("registrarse/", views.register, name="register"),
    path("iniciar-sesion/", views.login_view, name="login"),
    path("cerrar-sesion/", views.logout_view, name="logout"),
    # URLs de perfil
    path("perfil/", views.profile_view, name="profile_view"),  # Ver perfil propio
    path("perfil/editar/", views.profile_edit, name="profile_edit"),  # Editar perfil
    # URL adicional recomendada para perfiles públicos
    path("perfil/<str:username>/", views.public_profile_view, name="public_profile"),
]
