from rest_framework import serializers
from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
        )

        extra_kwargs = {"password": {"write_only": True}}


class PostSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "username",
            "content",
            "created_date",
            "updated_date",
        )


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("follower", "following")

        read_only_fields = ("follower",)

    def unfollow(self, follower, following):
        return Follow.objects.filter(follower=follower, following=following).delete()
