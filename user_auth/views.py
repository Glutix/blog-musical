from django.shortcuts import render, redirect
from .forms import CreateUserForm


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
