from rest_framework import serializers
from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

        extra_kwargs = {"password": {"write_only": True}}


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

        read_only_fields = (
            "id",
            "author",
            "created_at",
            "updated_at",
        )


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"

        read_only_fields = ("id",)
