from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile/", blank=True, null=True, default="profile/default.png"
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    def __str__(self):
        return self.username
