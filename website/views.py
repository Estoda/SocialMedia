from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .forms import SignUpForm
from .models import User
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q


def home(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("home")
    else:
        return render(request, "home.html", {})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("home")


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Authenticate
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, "You have been registered!")
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "register.html", {"form": form})


def is_admin_or_superuser(user):
    return user.is_staff or user.is_superuser


def All_users(request):
    search_query = request.GET.get("search", "")

    if request.user.is_superuser or request.user.is_staff:
        users = User.objects.all()
    elif request.user.is_authenticated:
        users = User.objects.filter(is_superuser=False)

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )
    return render(
        request, "all_users.html", {"users": users, "search_query": search_query}
    )


def user(request, pk):
    if request.user.is_authenticated:
        user = User.objects.get(id=pk)
        return render(request, "user.html", {"user": user})
    else:
        messages.error(request, "You must be logged in to view this page!")
        redirect("home")


def profile(request):
    if request.user.is_authenticated:
        user = request.user
        return render(request, "profile.html", {"user": user})


def profile_update(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to update this profile!")
        return redirect("home")
    current_user = request.user
    form = SignUpForm(
        request.POST or None, request.FILES or None, instance=current_user
    )

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            if "password" in form.cleaned_data:
                update_session_auth_hash(request, user)
            messages.success(request, "Your profile has been updated!")
            return redirect("profile-update")
    return render(request, "profile_update.html", {"form": form})
