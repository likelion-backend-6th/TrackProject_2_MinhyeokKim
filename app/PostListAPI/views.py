from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.exceptions import NotFound

from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User
from PostListAPI.serializers import PostSerializer, FollowSerializer, UserSerializer


# User R
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        users = User.objects.exclude(id=request.user.id).order_by("id")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# Post CRUD
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def check_authentication(self, request):
        if request.user != self.get_object().user:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        if self.action == "list":
            return Post.objects.filter(user=self.request.user)
        return super().get_queryset()

    def update(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().destroy(request, *args, **kwargs)


# Follow CRUD
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=["GET"], url_name="follows", url_path="follows")
    def follows(self, request, pk=None):
        user = User.objects.get(pk=pk)

        followers = Follow.objects.filter(following=user)
        followings = Follow.objects.filter(follower=user)
        follower_serializer = FollowSerializer(followers, many=True)
        following_serializer = FollowSerializer(followings, many=True)

        return Response(
            {
                "current user": user.username,
                "follower": follower_serializer.data,
                "following": following_serializer.data,
            }
        )

    @action(
        detail=False, methods=["POST"], url_name="add_follow", url_path="add_follow"
    )
    def add_follow(self, request):
        follower = request.user
        following_id = request.data.get("following_id")
        following = User.objects.get(pk=following_id)

        if Follow.objects.filter(follower=follower, following=following).exists():
            return Response(
                status=status.HTTP_409_CONFLICT,
                data="Already following",
            )
        result = f"{follower} follows {following}"
        Follow.objects.create(follower=follower, following=following)
        return Response(
            status=status.HTTP_201_CREATED,
            data=result,
        )

    @action(
        detail=False,
        methods=["DELETE"],
        url_name="unfollow",
        url_path="unfollow/(?P<following_id>[^/.]+)",
    )
    def unfollow(self, request, pk=None, following_id=None):
        follower = request.user

        if following_id is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data="Missing following_id",
            )

        try:
            following = User.objects.get(pk=following_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if Follow.objects.filter(follower=follower, following=following).exists():
            result = f"{follower} unfollows {following}"
            Follow.objects.filter(follower=follower, following=following).delete()
            return Response(
                status=status.HTTP_200_OK,
                data=result,
            )

        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data="Follow not found",
        )
