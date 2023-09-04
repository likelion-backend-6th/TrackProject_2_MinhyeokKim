from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    created_date = models.DateTimeField()
    published_date = models.DateTimeField()

    def __str__(self):
        return self.title


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed_user"
    )

    def __str__(self):
        return str(self.user) + " " + str(self.followed_user)
