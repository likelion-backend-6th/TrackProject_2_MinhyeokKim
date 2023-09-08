from rest_framework import serializers
from PostListAPI.models import Post, Follow


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
