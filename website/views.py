from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .forms import SignUpForm, PostForm
from .models import User, UserFollow, Message, Post, Comment
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, OuterRef, Subquery, Exists
from django.urls import reverse


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
        posts = Post.objects.all()
        return render(request, "home.html", {"posts": posts})


def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("home")
    else:
        form = PostForm()
    return render(request, "create_post.html", {"form": form})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, "post_detail.html", {"post": post, "comments": comments})


def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
        post.likes.add(request.user)
    return redirect(f"{reverse('home')}#post-{post_id}")


def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    else:
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        post.dislikes.add(request.user)
    return redirect(f"{reverse('home')}#post-{post_id}")


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
            | Q(bio__icontains=search_query)
            | Q(location__icontains=search_query)
        )

    if request.user.is_authenticated:
        users = users.annotate(
            is_followed=Exists(
                UserFollow.objects.filter(
                    follower=request.user, followed=OuterRef("pk")
                )
            )
        )

    return render(
        request, "all_users.html", {"users": users, "search_query": search_query}
    )


def user(request, pk):
    user = User.objects.get(id=pk)
    followers = UserFollow.objects.filter(followed=user).select_related("follower")
    followeds = UserFollow.objects.filter(follower=user).select_related("follower")
    is_following = UserFollow.objects.filter(
        follower=request.user, followed=user
    ).exists()

    followers_num = followers.count()
    followeds_num = followeds.count()

    if request.method == "POST":
        if is_following:
            UserFollow.objects.filter(follower=request.user, followed=user).delete()
            messages.success(request, f"You have unfollowed {user.username}!")
        else:
            UserFollow.objects.create(follower=request.user, followed=user)
            messages.success(request, f"You have followed {user.username}!")
        return redirect("user", pk=user.id)

    if request.user.is_authenticated:
        return render(
            request,
            "user.html",
            {
                "user": user,
                "is_following": is_following,
                "followers": followers,
                "followeds": followeds,
                "followers_num": followers_num,
                "followeds_num": followeds_num,
            },
        )
    else:
        messages.error(request, "You must be logged in to view this page!")
        redirect("home")


def profile(request):
    if request.user.is_authenticated:
        user = request.user
        followers = UserFollow.objects.filter(followed=user).select_related("follower")
        followeds = UserFollow.objects.filter(follower=user).select_related("follower")
        is_following = UserFollow.objects.filter(
            follower=request.user, followed=user
        ).exists()
        followers_num = followers.count()
        followeds_num = followeds.count()
        return render(
            request,
            "profile.html",
            {
                "user": user,
                "is_following": is_following,
                "followers": followers,
                "followeds": followeds,
                "followers_num": followers_num,
                "followeds_num": followeds_num,
            },
        )


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


def chat(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    if UserFollow.objects.filter(followed=receiver, follower=request.user).exists():
        if UserFollow.objects.filter(followed=request.user, follower=receiver).exists():
            messages1 = Message.objects.filter(
                sender=request.user, receiver=receiver
            ).order_by("timestamp")
            messages2 = Message.objects.filter(
                sender=receiver, receiver=request.user
            ).order_by("timestamp")
            msgs = messages1 | messages2

            if request.method == "POST":
                message_content = request.POST.get("message")
                if message_content:
                    Message.objects.create(
                        receiver=receiver,
                        sender=request.user,
                        message=message_content,
                    )
                    return redirect("chat", receiver_id=receiver.id)
            return render(
                request,
                "chat.html",
                {"receiver": receiver, "msg": msgs},
            )
        else:
            messages.error(request, f"{receiver.username} is not following you!")
            return redirect("home")
    else:
        messages.error(request, "You are not following this user!")
        return redirect("home")


def friends_list(request):
    search_query = request.GET.get("search", "")

    current_user = request.user
    following = UserFollow.objects.filter(follower=current_user).values_list(
        "followed", flat=True
    )
    friends = UserFollow.objects.filter(
        follower__in=following, followed=current_user
    ).values_list("follower", flat=True)

    friends_users = User.objects.filter(id__in=friends)

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(bio__icontains=search_query)
            | Q(location__icontains=search_query)
        )

    return render(request, "friends.html", {"users": friends_users})
