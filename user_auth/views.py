#! Utilidaes de Django
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


#! utildades
import requests
import cloudinary.uploader

#! Modelos y formularios
from .forms import CreateUserForm, CustomLoginForm, ProfileForm
from .models import Profile
from django.contrib.auth.models import User
from blog.models import Article


# Create your views here.
def index(request):
    title = "Bievenidos a seccion de Usuario"
    return render(request, "index.html", {"title": title})


#! Registro de usuario
def register(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("user_auth:login")
        else:
            print(form.errors)

    else:
        form = CreateUserForm()

    return render(request, "register.html", {"form": form})


#! Authenticacion de usuario
def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            print(user)
            login(request, user)
            return redirect("/")
    else:
        form = CustomLoginForm()

    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("/")


#! Perfil de usuario
@login_required
def profile_view(request):
    """
    Vista para mostrar el perfil del usuario (solo lectura).
    """
    # Obtener o crear el perfil del usuario
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Obtener los artículos del usuario, ordenados por fecha de creación
    user_articles = Article.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "profile": profile,
        "user": request.user,
        "articles": user_articles,
    }

    return render(request, "profile_view.html", context)


@login_required
def profile_edit(request):
    """
    Vista para editar el perfil del usuario.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            updated_profile = form.save(commit=False)
            selected_avatar = request.POST.get("selected_avatar", "").strip()

            # Lógica para ELIMINAR el avatar
            if selected_avatar == "DELETE_AVATAR":
                if updated_profile.avatar:
                    try:
                        cloudinary.uploader.destroy(updated_profile.avatar.public_id)
                        updated_profile.avatar = None
                        messages.success(
                            request, "Avatar personalizado eliminado exitosamente."
                        )
                    except Exception as e:
                        messages.warning(
                            request, "No se pudo eliminar el avatar anterior."
                        )

            # ✅ Lógica para USAR un avatar por defecto (ahora sin el check 'startswith("http")')
            elif selected_avatar:
                try:
                    # ✅ Construimos la URL completa con el color del formulario
                    initials = ""
                    if profile.user.first_name and profile.user.last_name:
                        initials = (
                            f"{profile.user.first_name[0]}{profile.user.last_name[0]}"
                        )
                    elif profile.user.first_name:
                        initials = profile.user.first_name[:2]
                    else:
                        initials = profile.user.username[:2]

                    avatar_url = f"https://ui-avatars.com/api/?name={initials}&background={selected_avatar}&color=ffffff&size=200&bold=true"

                    response = requests.get(avatar_url, timeout=10)
                    if response.status_code == 200:
                        # Opcional: Eliminar avatar anterior antes de subir el nuevo
                        if updated_profile.avatar:
                            try:
                                cloudinary.uploader.destroy(
                                    updated_profile.avatar.public_id
                                )
                            except:
                                pass

                        # Subimos el archivo directamente a Cloudinary
                        # con un public_id que incluye el color para evitar el caché del navegador
                        new_public_id = f"avatar_{request.user.username}_{profile.id}_{selected_avatar}"

                        upload_result = cloudinary.uploader.upload(
                            response.content, folder="avatars", public_id=new_public_id
                        )

                        updated_profile.avatar = upload_result["public_id"]
                        messages.success(request, "Avatar actualizado exitosamente.")
                except requests.RequestException:
                    messages.error(
                        request,
                        "Error al descargar el avatar seleccionado. Verifica tu conexión a internet.",
                    )
                    return render(
                        request,
                        "profile_edit.html",
                        {"form": form, "profile": profile, "user": request.user},
                    )

            # Guardar la instancia del modelo UNA SOLA VEZ
            updated_profile.save()

            if not messages.get_messages(request):
                messages.success(request, "Perfil actualizado exitosamente.")

            return redirect("user_auth:profile_view")

        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
            print("Errores del formulario:", form.errors)

    else:  # Método GET
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
        "user": request.user,
    }

    return render(request, "profile_edit.html", context)


def public_profile_view(request, username):
    """
    Vista para mostrar el perfil público de cualquier usuario.
    Accesible desde: /profile/nombre_usuario/
    """
    # Buscar el usuario por username, 404 si no existe
    user = get_object_or_404(User, username=username)

    # Obtener o crear el perfil del usuario
    profile, created = Profile.objects.get_or_create(user=user)

    # Verificar si es el perfil del usuario actual (opcional)
    is_own_profile = request.user.is_authenticated and request.user == user

    context = {
        "profile_user": user,
        "profile": profile,
        "is_own_profile": is_own_profile,
    }

    return render(request, "public_profile.html", context)
