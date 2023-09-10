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
    permission_classes = [permissions.AllowAny]

    def check_authentication(self):
        if not self.request.user.is_authenticated:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data="You are not allowed to perform this action",
            )

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data="You are not allowed to create a post",
            )

    @action(detail=False, methods=["GET"], url_name="my_posts", url_path="my_posts")
    def my_posts(self, request):
        self.check_authentication()

        my_posts = Post.objects.filter(author=request.user)

        if not my_posts:
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                data="You have no posts",
            )

        serializer = PostSerializer(my_posts, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        url_name="following_posts",
        url_path="following_posts",
    )
    def following_posts(self, request):
        self.check_authentication()

        following_users = Follow.objects.filter(follower=request.user).values_list(
            "following", flat=True
        )

        if not following_users:
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                data="No following posts found",
            )

        following_posts = Post.objects.filter(author__in=following_users).order_by("id")
        serializer = PostSerializer(following_posts, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        try:
            instance = self.get_object()
        except NotFound:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data="Post not found",
            )

        if instance.author != self.request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data="You are not allowed to update this post",
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except NotFound:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data="Post not found",
            )

        if instance.author != self.request.user:
            return Response(
                data="You are not allowed to delete this post",
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT, data="Post deleted")


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
