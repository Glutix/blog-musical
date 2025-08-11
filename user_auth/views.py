from django.shortcuts import render, redirect
from .forms import CreateUserForm, CustomLoginForm
from django.contrib.auth import login


# Create your views here.
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

    return render(request, "user_auth/register.html", {"form": form})


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

    return render(request, "user_auth/login.html", {"form": form})
