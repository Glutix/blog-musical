from django.urls import path
from . import views

app_name = "user_auth"


urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # URLs de perfil
    path("profile/", views.profile_view, name="profile_view"),  # Ver perfil propio
    path("profile/edit/", views.profile_edit, name="profile_edit"),  # Editar perfil
    # URL adicional recomendada para perfiles públicos
    path("profile/<str:username>/", views.public_profile_view, name="public_profile"),
]
