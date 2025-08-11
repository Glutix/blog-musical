from django.shortcuts import render, redirect
from .forms import CreateUserForm, CustomLoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    title = "Bievenidos a seccion de Usuario"
    return render(request, "index.html", {"title": title})


def register(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            print(form.errors)

    else:
        form = CreateUserForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            print(user)
            login(request, user)
            return redirect("index")
    else:
        form = CustomLoginForm()

    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
