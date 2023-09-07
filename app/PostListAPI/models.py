from django.db import models
from django.contrib.auth.models import User


# User can create Posts
# Posts can be seen by everyone if it is public
# Posts can only be seen by the user and the people they follow if it is private
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# User can follow other users
# Followers can see the posts of the people they follow
# User information has followers and following
class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    def __str__(self):
        return str(self.follower) + "follows" + str(self.following)
