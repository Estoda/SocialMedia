from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile/", blank=True, null=True, default="profile/default.png"
    )
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f" {self.sender.username} to {self.receiver.username}: {self.message}"


class UserFollow(models.Model):
    follower = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        User, related_name="followers", on_delete=models.CASCADE
    )
    date_followed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "follower",
            "followed",
        )  # Ensure a user can't follow another user more than once

        def __str__(self):
            return f"{self.follower.username} follows {self.followed.username}"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    dislikes = models.ManyToManyField(User, related_name="dislikes", blank=True)
    file = models.FileField(upload_to="post_files/", blank=True, null=True)

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def total_comments(self):
        return Comment.objects.filter(post=self).count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)
    dislikes = models.ManyToManyField(
        User, related_name="disliked_comments", blank=True
    )
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    file = models.FileField(upload_to="post_files/", blank=True, null=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.user.username}'s post"

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()
