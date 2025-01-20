from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),
    path("all_users/", views.All_users, name="all-users"),
    path("user/<int:pk>/", views.user, name="user"),
    path("profile/", views.profile, name="profile"),
    path("profile/update/", views.profile_update, name="profile-update"),
    path("chat/<int:receiver_id>", views.chat, name="chat"),
    path("friends/", views.friends_list, name="friends"),
    path("create_post/", views.create_post, name="create-post"),
    path("post_detail/<int:post_id>", views.post_detail, name="post-detail"),
    path("like_post/<int:post_id>/", views.like_post, name="like-post"),
    path("dislike_post/<int:post_id>/", views.dislike_post, name="dislike-post"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
