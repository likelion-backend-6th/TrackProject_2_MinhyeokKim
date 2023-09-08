from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions

from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User
from PostListAPI.serializers import PostSerializer, FollowSerializer


# Post CRUD
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def my_posts(self, request):
        my_posts = Post.objects.filter(author=request.user)
        serializer = PostSerializer(my_posts, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        print("self", vars(self))

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
        instance = self.get_object()
        if instance.author != self.request.user:
            return Response(
                data="You are not allowed to delete this post",
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# Follow CRUD
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=["GET"])
    def follows(self, request, pk=None):
        print("pk value: ", pk)
        user = User.objects.get(pk=pk)

        followers = Follow.objects.filter(following=user)
        followings = Follow.objects.filter(follower=user)
        follower_serializer = FollowSerializer(followers, many=True)
        following_serializer = FollowSerializer(followings, many=True)

        print("follower_serializer.data : ", follower_serializer.data)
        print("following_serializer.data : ", following_serializer.data)

        return Response(
            {
                "current user": user.username,
                "follower": follower_serializer.data,
                "following": following_serializer.data,
            }
        )
