from rest_framework import serializers
from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    # define a new field
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "is_following",
        )

        extra_kwargs = {"password": {"write_only": True}}

    # get_<field_name>()
    def get_is_following(self, obj):
        request_user = self.context["request"].user
        return Follow.objects.filter(follower=request_user, following=obj).exists()


class PostSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "username",
            "content",
            "is_hidden",
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
